"""Google Calendar sync. The only module allowed to call the Google
Calendar API, mirroring how services/llm_client.py is the only module
allowed to call an LLM.

Handles: the OAuth auth-code flow (building the consent URL, exchanging the
code, storing the refresh token encrypted), finding/creating a secondary
"Arohi" calendar, and syncing predicted-period/fertile-window events plus
reminder events into it. Access-token refresh is handled transparently by
google-auth's Credentials object on every API call; a revoked/expired
refresh token surfaces as GoogleCalendarAccessRevoked so the router can ask
the user to reconnect instead of crashing.
"""

import logging
import os
from datetime import date, datetime, time, timedelta
from typing import Optional
from urllib.parse import urlencode

import requests
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from core.crypto import InvalidToken, decrypt, encrypt
from core.errors import ApiError
from core.supabase import get_supabase
from models.schemas import Reminder
from services import cycles as cycles_service
from services import profiles as profiles_service
from services import prediction as prediction_service

logger = logging.getLogger("arohi.gcal")

OAUTH_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]
OAUTH_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"
CALENDAR_NAME = "Arohi"
CALENDAR_TIMEZONE = "Asia/Kolkata"

PERIOD_POPUP_MINUTES_BEFORE = 2 * 24 * 60  # "2-day popup", per CC-13
REMINDER_POPUP_MINUTES_BEFORE = 30
DISCREET_REMINDER_TITLE = "Arohi reminder"

FREQUENCY_RRULES = {
    "daily": "RRULE:FREQ=DAILY",
    "weekly": "RRULE:FREQ=WEEKLY",
    "monthly": "RRULE:FREQ=MONTHLY",
}


class GoogleCalendarNotConnected(Exception):
    """This user hasn't connected Google Calendar yet."""


class GoogleCalendarAccessRevoked(Exception):
    """The stored refresh token no longer works — access was revoked (or
    expired beyond refresh) on Google's side. The caller should prompt the
    user to reconnect; the stored token has already been cleared."""


# --- OAuth ---------------------------------------------------------------------


def build_auth_url(user_id: str) -> str:
    state = encrypt(user_id)
    params = {
        "client_id": os.environ["GOOGLE_CLIENT_ID"],
        "redirect_uri": os.environ["GOOGLE_REDIRECT_URI"],
        "response_type": "code",
        "scope": " ".join(OAUTH_SCOPES),
        "access_type": "offline",
        "prompt": "consent",  # forces a refresh_token on every connect, not just the first ever
        "state": state,
    }
    return f"{OAUTH_AUTH_URL}?{urlencode(params)}"


def handle_oauth_callback(code: str, state: str) -> str:
    """Exchanges the auth code for tokens, stores them, and runs an initial
    sync. Returns the user_id the connection belongs to."""
    try:
        user_id = decrypt(state)
    except InvalidToken as exc:
        raise ApiError(
            400, "invalid_oauth_state", "This connection link has expired or is invalid. Please try again."
        ) from exc

    token_response = requests.post(
        OAUTH_TOKEN_URL,
        data={
            "client_id": os.environ["GOOGLE_CLIENT_ID"],
            "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": os.environ["GOOGLE_REDIRECT_URI"],
        },
        timeout=10,
    )
    token_response.raise_for_status()
    tokens = token_response.json()

    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        # build_auth_url always sends prompt=consent, which should force a
        # fresh refresh_token every time — if it's still missing, something
        # upstream is misconfigured, not a case to silently paper over.
        raise ApiError(502, "gcal_no_refresh_token", "Google didn't return a refresh token.")

    _save_refresh_token(user_id, refresh_token)
    sync_all(user_id)
    return user_id


def _save_refresh_token(user_id: str, refresh_token: str) -> None:
    supabase = get_supabase()
    supabase.table("gcal_tokens").upsert(
        {"user_id": user_id, "refresh_token_encrypted": encrypt(refresh_token)},
        on_conflict="user_id",
    ).execute()
    supabase.table("profiles").update({"gcal_connected": True}).eq("id", user_id).execute()


def _handle_revocation(user_id: str) -> None:
    supabase = get_supabase()
    supabase.table("profiles").update({"gcal_connected": False}).eq("id", user_id).execute()
    supabase.table("gcal_tokens").delete().eq("user_id", user_id).execute()


def _get_credentials(user_id: str) -> Credentials:
    response = (
        get_supabase()
        .table("gcal_tokens")
        .select("refresh_token_encrypted")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if not response.data:
        raise GoogleCalendarNotConnected(user_id)

    refresh_token = decrypt(response.data[0]["refresh_token_encrypted"])
    return Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=OAUTH_TOKEN_URL,
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        scopes=OAUTH_SCOPES,
    )


def _calendar_service(user_id: str):
    return build("calendar", "v3", credentials=_get_credentials(user_id), cache_discovery=False)


# --- Calendar setup --------------------------------------------------------------


def ensure_calendar(user_id: str) -> str:
    """Finds or creates the secondary "Arohi" calendar, caching its id on
    gcal_tokens so repeat calls don't re-list/re-create it."""
    supabase = get_supabase()
    existing = (
        supabase.table("gcal_tokens").select("calendar_id").eq("user_id", user_id).limit(1).execute()
    )
    if existing.data and existing.data[0]["calendar_id"]:
        return existing.data[0]["calendar_id"]

    service = _calendar_service(user_id)
    calendar_list = service.calendarList().list().execute()
    calendar_id = next(
        (entry["id"] for entry in calendar_list.get("items", []) if entry.get("summary") == CALENDAR_NAME),
        None,
    )
    if calendar_id is None:
        created = service.calendars().insert(
            body={"summary": CALENDAR_NAME, "timeZone": CALENDAR_TIMEZONE}
        ).execute()
        calendar_id = created["id"]

    supabase.table("gcal_tokens").update({"calendar_id": calendar_id}).eq("user_id", user_id).execute()
    return calendar_id


# --- Prediction sync ---------------------------------------------------------------


def _upsert_synced_event(
    service,
    supabase,
    user_id: str,
    calendar_id: str,
    *,
    event_key: str,
    body: dict,
) -> None:
    existing = (
        supabase.table("gcal_synced_events")
        .select("gcal_event_id")
        .eq("user_id", user_id)
        .eq("event_key", event_key)
        .limit(1)
        .execute()
    )

    if existing.data:
        service.events().update(
            calendarId=calendar_id, eventId=existing.data[0]["gcal_event_id"], body=body
        ).execute()
        return

    created = service.events().insert(calendarId=calendar_id, body=body).execute()
    supabase.table("gcal_synced_events").upsert(
        {"user_id": user_id, "event_key": event_key, "gcal_event_id": created["id"]},
        on_conflict="user_id,event_key",
    ).execute()


def sync_predictions(user_id: str) -> None:
    supabase = get_supabase()
    calendar_id = ensure_calendar(user_id)
    service = _calendar_service(user_id)

    cycles = cycles_service.list_cycles(user_id)
    profile = profiles_service.get_profile(user_id)
    prediction = prediction_service.predict(cycles, profile)

    period_end = prediction.next_period_start + timedelta(days=profile.avg_period_len)
    _upsert_synced_event(
        service,
        supabase,
        user_id,
        calendar_id,
        event_key="predicted_period",
        body={
            "summary": "Predicted period",
            "start": {"date": prediction.next_period_start.isoformat()},
            "end": {"date": period_end.isoformat()},
            "reminders": {
                "useDefault": False,
                "overrides": [{"method": "popup", "minutes": PERIOD_POPUP_MINUTES_BEFORE}],
            },
        },
    )

    # Google's all-day "end.date" is exclusive, so +1 day to actually cover
    # fertile_window.end (an inclusive date from services/prediction.py).
    fertile_end_exclusive = prediction.fertile_window.end + timedelta(days=1)
    _upsert_synced_event(
        service,
        supabase,
        user_id,
        calendar_id,
        event_key="fertile_window",
        body={
            "summary": "Fertile window",
            "start": {"date": prediction.fertile_window.start.isoformat()},
            "end": {"date": fertile_end_exclusive.isoformat()},
            "reminders": {"useDefault": False, "overrides": []},
        },
    )


# --- Reminder sync -----------------------------------------------------------------


def _rrule_for(frequency: Optional[str]) -> Optional[list[str]]:
    """Best-effort mapping from reminders.frequency's free-text field to a
    recurrence rule — covers the common cases (daily/weekly/monthly
    anywhere in the text, case-insensitive); anything else is treated as a
    one-off event rather than guessing at a schedule."""
    if not frequency:
        return None
    lowered = frequency.strip().lower()
    for keyword, rrule in FREQUENCY_RRULES.items():
        if keyword in lowered:
            return [rrule]
    return None


def _title_for(reminder: Reminder) -> str:
    """Discreet reminders never show their real title in the calendar —
    which may be visible on a shared device or synced elsewhere — so they
    get a neutral placeholder instead."""
    return DISCREET_REMINDER_TITLE if reminder.discreet else reminder.title


def sync_reminders(user_id: str) -> None:
    supabase = get_supabase()
    calendar_id = ensure_calendar(user_id)
    service = _calendar_service(user_id)

    response = supabase.table("reminders").select("*").eq("user_id", user_id).execute()

    for row in response.data:
        reminder = Reminder(**row)
        start_time = reminder.time_of_day or time(9, 0)
        start_dt = datetime.combine(date.today(), start_time)
        end_dt = start_dt + timedelta(minutes=30)

        body = {
            "summary": _title_for(reminder),
            "start": {"dateTime": start_dt.isoformat(), "timeZone": CALENDAR_TIMEZONE},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": CALENDAR_TIMEZONE},
            "reminders": {
                "useDefault": False,
                "overrides": [{"method": "popup", "minutes": REMINDER_POPUP_MINUTES_BEFORE}],
            },
        }
        recurrence = _rrule_for(reminder.frequency)
        if recurrence:
            body["recurrence"] = recurrence

        if reminder.gcal_event_id:
            service.events().update(
                calendarId=calendar_id, eventId=reminder.gcal_event_id, body=body
            ).execute()
        else:
            created = service.events().insert(calendarId=calendar_id, body=body).execute()
            supabase.table("reminders").update({"gcal_event_id": created["id"]}).eq(
                "id", str(reminder.id)
            ).execute()


# --- Orchestration -----------------------------------------------------------------


def sync_all(user_id: str) -> None:
    try:
        ensure_calendar(user_id)
        sync_predictions(user_id)
        sync_reminders(user_id)
    except RefreshError as exc:
        logger.warning("gcal refresh token revoked for user %s: %s", user_id, exc)
        _handle_revocation(user_id)
        raise GoogleCalendarAccessRevoked(user_id) from exc
    except HttpError as exc:
        if exc.resp.status in (401, 403):
            logger.warning("gcal access revoked for user %s: %s", user_id, exc)
            _handle_revocation(user_id)
            raise GoogleCalendarAccessRevoked(user_id) from exc
        raise
