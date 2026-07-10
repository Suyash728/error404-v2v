"""Turns a fired RiskFlag into a warm, plain-English explanation via the LLM
(services/llm_client.py — the only module allowed to call one). Output is
validated against a flag_type-derived allowlist before being trusted; on
repeated violation, falls back to a static per-flag template so a risk flag
is never persisted without a safe explanation.
"""

from services import llm_client
from services.llm_client import LLMUnavailable

EXPLANATION_TEMPERATURE = 0.3
EXPLANATION_MAX_WORDS = 120
EXPLANATION_MAX_TOKENS = 350
EXPLANATION_MAX_ATTEMPTS = 2  # 1 try + 1 retry, per "on violation retry once"
STATIC_TEMPLATE_PROVIDER = "static_template"

SYSTEM_PROMPT = (
    "You explain a pattern alert from a deterministic rule engine to a user, "
    "in warm, simple 8th-grade English. You may ONLY reference the provided "
    "fired_rules — never invent numbers, symptoms, or details beyond them. "
    "NEVER name a medical condition other than the one this pattern is about. "
    "NEVER diagnose: this is a pattern worth discussing with a doctor, not a "
    "diagnosis, and you must say so clearly. End with 2-3 questions the user "
    "could ask a gynecologist about this pattern. Keep the entire response to "
    "120 words or fewer."
)

# Terms that name a specific diagnosis, keyed by the one flag_type allowed to
# reference them. Only used to build the "must not mention any OTHER
# condition's terms" allowlist below — not a fact-checker, just guards
# against the model wandering into a diagnosis it wasn't asked to explain.
CONDITION_NAME_TERMS: dict[str, list[str]] = {
    "PCOS_PATTERN": ["pcos", "polycystic"],
    "ANEMIA_PATTERN": ["anemia", "anaemia", "iron deficiency", "iron-deficiency"],
    "PMDD_PATTERN": ["pmdd", "premenstrual dysphoric"],
}

DOCTOR_MENTION_TERMS = ("doctor", "gynecologist", "gynaecologist", "ob-gyn", "obgyn", "physician")

# Small, deliberately narrow blocklist for "NEVER diagnose" — catches the
# most direct diagnostic phrasing without trying to be exhaustive.
DIAGNOSTIC_PHRASES = (
    "you have ",
    "you've been diagnosed",
    "you are diagnosed",
    "your diagnosis is",
    "you suffer from",
    "you definitely have",
    "this confirms",
)

STATIC_TEMPLATES: dict[str, str] = {
    "IRREGULARITY": (
        "Your recent cycles have varied more than usual in length. This is a pattern worth "
        "mentioning at your next visit — it's common and often not serious, but a doctor can "
        "help figure out what's behind it. Questions to ask a gynecologist: What could cause "
        "cycles to vary this much? Should I track anything else to help you understand it? Is "
        "there a simple test that could offer more insight?"
    ),
    "PCOS_PATTERN": (
        "Your logs show a pattern sometimes linked to PCOS, including irregular cycles "
        "alongside other symptoms. This is worth discussing with a doctor — it's not a "
        "diagnosis, just something worth asking about. Questions to ask a gynecologist: Could "
        "my symptoms be related to PCOS? What tests might help figure out what's going on? "
        "What lifestyle or treatment options could help if this is the cause?"
    ),
    "ANEMIA_PATTERN": (
        "Your logs show a pattern of heavy flow along with symptoms like fatigue. This "
        "combination is worth discussing with a doctor — it's not a diagnosis, but heavy "
        "periods can sometimes affect iron levels. Questions to ask a gynecologist: Could this "
        "be related to low iron? Would a blood test help check for anemia? Are there ways to "
        "manage heavy flow in the meantime?"
    ),
    "PMDD_PATTERN": (
        "Your logs show your mood tends to dip in the days before your period compared to "
        "mid-cycle. This pattern is worth discussing with a doctor — it's not a diagnosis, "
        "just something worth exploring together. Questions to ask a gynecologist: Could this "
        "be related to PMDD? What treatment options are available? Would tracking mood "
        "alongside my cycle help figure out what's going on?"
    ),
}


def _build_user_prompt(flag_type: str, fired_rules: list[str]) -> str:
    rules_block = "\n".join(f"- {rule}" for rule in fired_rules)
    return (
        f"Pattern detected: {flag_type}\n\n"
        "The rule engine found these specific things in the user's data — this is the ONLY "
        f"information you may reference:\n{rules_block}\n\n"
        "Write the explanation now."
    )


def is_valid_explanation(text: str, flag_type: str) -> bool:
    word_count = len(text.split())
    if word_count == 0 or word_count > EXPLANATION_MAX_WORDS:
        return False

    lowered = text.lower()

    for other_flag_type, terms in CONDITION_NAME_TERMS.items():
        if other_flag_type == flag_type:
            continue
        if any(term in lowered for term in terms):
            return False

    if not any(term in lowered for term in DOCTOR_MENTION_TERMS):
        return False

    if any(phrase in lowered for phrase in DIAGNOSTIC_PHRASES):
        return False

    return True


def generate_explanation(flag_type: str, fired_rules: list[str]) -> tuple[str, str]:
    """Returns (explanation, llm_provider). Tries the LLM up to
    EXPLANATION_MAX_ATTEMPTS times; falls back to a static per-flag template
    (provider="static_template") if every attempt is either unavailable or
    fails validation.
    """
    user_prompt = _build_user_prompt(flag_type, fired_rules)

    for _ in range(EXPLANATION_MAX_ATTEMPTS):
        try:
            result = llm_client.complete(
                system=SYSTEM_PROMPT,
                user=user_prompt,
                temperature=EXPLANATION_TEMPERATURE,
                max_tokens=EXPLANATION_MAX_TOKENS,
            )
        except LLMUnavailable:
            break

        if is_valid_explanation(result.text, flag_type):
            return result.text.strip(), result.provider

    return STATIC_TEMPLATES[flag_type], STATIC_TEMPLATE_PROVIDER
