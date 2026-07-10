from services import llm_client
from services.llm_client import LLMResult, LLMUnavailable
from services.risk_explanation import (
    STATIC_TEMPLATE_PROVIDER,
    STATIC_TEMPLATES,
    generate_explanation,
    is_valid_explanation,
)

FIRED_RULES = ["cycle length stddev 9.2d exceeds 8d (n=4 cycles)"]

VALID_IRREGULARITY_TEXT = (
    "Your cycles have varied more than usual lately. This is worth discussing with a doctor. "
    "Questions to ask a gynecologist: What could cause this? Should I track more? Is a test "
    "worth considering?"
)


# --- is_valid_explanation -----------------------------------------------------


def test_valid_explanation_passes():
    assert is_valid_explanation(VALID_IRREGULARITY_TEXT, "IRREGULARITY") is True


def test_explanation_over_word_limit_fails():
    text = "word " * 121 + "doctor gynecologist"
    assert is_valid_explanation(text, "IRREGULARITY") is False


def test_explanation_naming_another_condition_fails():
    text = (
        "This could be a sign of PCOS. Talk to your doctor. Questions to ask a gynecologist: "
        "What tests help? What else should I watch for? Any other advice?"
    )
    assert is_valid_explanation(text, "IRREGULARITY") is False


def test_explanation_naming_its_own_condition_is_allowed():
    text = (
        "Your logs show a pattern sometimes linked to PCOS. This is worth discussing with a "
        "doctor. Questions to ask a gynecologist: Could this be PCOS? What tests might help? "
        "What treatment options exist?"
    )
    assert is_valid_explanation(text, "PCOS_PATTERN") is True


def test_explanation_missing_doctor_mention_fails():
    text = "Your cycles have varied lately. Ask about this. What could cause this? Anything else?"
    assert is_valid_explanation(text, "IRREGULARITY") is False


def test_explanation_with_diagnostic_language_fails():
    text = (
        "You have anemia caused by heavy periods. See a doctor. Questions to ask a "
        "gynecologist: What treatment helps? Any tests needed? What else should I watch?"
    )
    assert is_valid_explanation(text, "ANEMIA_PATTERN") is False


# --- generate_explanation ------------------------------------------------------


def test_generate_explanation_returns_first_valid_attempt(monkeypatch):
    calls = []

    def fake_complete(**kwargs):
        calls.append(kwargs)
        return LLMResult(text=VALID_IRREGULARITY_TEXT, provider="gemini")

    monkeypatch.setattr(llm_client, "complete", fake_complete)

    explanation, provider = generate_explanation("IRREGULARITY", FIRED_RULES)

    assert explanation == VALID_IRREGULARITY_TEXT
    assert provider == "gemini"
    assert len(calls) == 1
    assert calls[0]["temperature"] == 0.3


def test_generate_explanation_retries_once_then_succeeds(monkeypatch):
    responses = [
        LLMResult(text="This mentions PCOS which is not allowed here.", provider="gemini"),
        LLMResult(text=VALID_IRREGULARITY_TEXT, provider="groq"),
    ]

    def fake_complete(**kwargs):
        return responses.pop(0)

    monkeypatch.setattr(llm_client, "complete", fake_complete)

    explanation, provider = generate_explanation("IRREGULARITY", FIRED_RULES)

    assert explanation == VALID_IRREGULARITY_TEXT
    assert provider == "groq"
    assert responses == []


def test_generate_explanation_falls_back_to_static_template_after_two_violations(monkeypatch):
    calls = []

    def fake_complete(**kwargs):
        calls.append(kwargs)
        return LLMResult(text="This mentions PCOS which is not allowed here.", provider="gemini")

    monkeypatch.setattr(llm_client, "complete", fake_complete)

    explanation, provider = generate_explanation("IRREGULARITY", FIRED_RULES)

    assert provider == STATIC_TEMPLATE_PROVIDER
    assert explanation == STATIC_TEMPLATES["IRREGULARITY"]
    assert len(calls) == 2  # one try + one retry


def test_generate_explanation_falls_back_immediately_when_llm_unavailable(monkeypatch):
    calls = []

    def fake_complete(**kwargs):
        calls.append(kwargs)
        raise LLMUnavailable("all providers failed")

    monkeypatch.setattr(llm_client, "complete", fake_complete)

    explanation, provider = generate_explanation("PMDD_PATTERN", FIRED_RULES)

    assert provider == STATIC_TEMPLATE_PROVIDER
    assert explanation == STATIC_TEMPLATES["PMDD_PATTERN"]
    assert len(calls) == 1  # no point retrying once every provider has already failed
