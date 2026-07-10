from datetime import time
from urllib.parse import parse_qs, urlparse

from cryptography.fernet import Fernet

from core.crypto import decrypt
from models.schemas import Reminder
from services.gcal import DISCREET_REMINDER_TITLE, _rrule_for, _title_for, build_auth_url

USER_ID = "00000000-0000-0000-0000-000000000001"


def make_reminder(**kwargs) -> Reminder:
    defaults = dict(
        id=USER_ID,
        user_id=USER_ID,
        kind="appointment",
        title="Take contraception pill",
        time_of_day=time(9, 0),
        frequency=None,
        gcal_event_id=None,
        discreet=False,
    )
    defaults.update(kwargs)
    return Reminder(**defaults)


def set_gcal_env(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/calendar/oauth/callback")
    monkeypatch.setenv("GCAL_TOKEN_ENCRYPTION_KEY", Fernet.generate_key().decode())


# --- _rrule_for ----------------------------------------------------------------


def test_rrule_for_none_returns_none():
    assert _rrule_for(None) is None


def test_rrule_for_empty_string_returns_none():
    assert _rrule_for("") is None


def test_rrule_for_daily():
    assert _rrule_for("daily") == ["RRULE:FREQ=DAILY"]


def test_rrule_for_weekly_case_insensitive():
    assert _rrule_for("Weekly") == ["RRULE:FREQ=WEEKLY"]


def test_rrule_for_monthly_substring_match():
    assert _rrule_for("monthly on the 1st") == ["RRULE:FREQ=MONTHLY"]


def test_rrule_for_unrecognized_text_returns_none():
    assert _rrule_for("every other Tuesday") is None


# --- _title_for ------------------------------------------------------------------


def test_title_for_non_discreet_uses_real_title():
    reminder = make_reminder(title="Take contraception pill", discreet=False)
    assert _title_for(reminder) == "Take contraception pill"


def test_title_for_discreet_uses_placeholder():
    reminder = make_reminder(title="Take contraception pill", discreet=True)
    assert _title_for(reminder) == DISCREET_REMINDER_TITLE


def test_title_for_discreet_never_leaks_real_title():
    reminder = make_reminder(title="STI test follow-up", discreet=True)
    assert "STI" not in _title_for(reminder)


# --- build_auth_url --------------------------------------------------------------


def test_build_auth_url_contains_expected_params(monkeypatch):
    set_gcal_env(monkeypatch)

    url = build_auth_url(USER_ID)
    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    assert parsed.netloc == "accounts.google.com"
    assert params["client_id"] == ["test-client-id"]
    assert params["redirect_uri"] == ["http://localhost:8000/calendar/oauth/callback"]
    assert params["response_type"] == ["code"]
    assert params["access_type"] == ["offline"]
    assert "calendar" in params["scope"][0]
    assert "calendar.events" in params["scope"][0]


def test_build_auth_url_state_round_trips_to_user_id(monkeypatch):
    set_gcal_env(monkeypatch)

    url = build_auth_url(USER_ID)
    state = parse_qs(urlparse(url).query)["state"][0]
    assert decrypt(state) == USER_ID
