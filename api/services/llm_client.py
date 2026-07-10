"""The only module allowed to call an LLM. Everything else goes through complete()."""

import logging
import os
import time
from dataclasses import dataclass

import google.generativeai as genai
from groq import Groq

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 8
RETRIES_PER_PROVIDER = 1  # one retry, i.e. 2 attempts total, before moving on

GEMINI_MODEL = "gemini-2.5-flash"
GROQ_MODEL = "llama-3.3-70b-versatile"


class LLMUnavailable(Exception):
    """Raised when every provider in the chain has failed."""


@dataclass
class LLMResult:
    text: str
    provider: str


def _provider_chain() -> list[str]:
    primary = os.environ.get("LLM_PRIMARY", "gemini")
    fallbacks = [p for p in ("gemini", "groq") if p != primary]
    return [primary, *fallbacks]


def _call_gemini(system: str, user: str, json_mode: bool, max_tokens: int, temperature: float) -> str:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=system)

    generation_config = {"max_output_tokens": max_tokens, "temperature": temperature}
    if json_mode:
        generation_config["response_mime_type"] = "application/json"

    response = model.generate_content(
        user,
        generation_config=generation_config,
        request_options={"timeout": TIMEOUT_SECONDS},
    )
    return response.text


def _call_groq(system: str, user: str, json_mode: bool, max_tokens: int, temperature: float) -> str:
    client = Groq(api_key=os.environ["GROQ_API_KEY"], timeout=TIMEOUT_SECONDS)

    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        **kwargs,
    )
    return response.choices[0].message.content


def _call_provider(
    provider: str, system: str, user: str, json_mode: bool, max_tokens: int, temperature: float
) -> str:
    if provider == "gemini":
        return _call_gemini(system, user, json_mode, max_tokens, temperature)
    if provider == "groq":
        return _call_groq(system, user, json_mode, max_tokens, temperature)
    raise LLMUnavailable(f"unknown LLM provider: {provider}")


def complete(
    system: str,
    user: str,
    json_mode: bool = False,
    max_tokens: int = 400,
    temperature: float = 0.7,
) -> LLMResult:
    chain = _provider_chain()
    call_start = time.monotonic()

    for position, provider in enumerate(chain):
        for attempt in range(RETRIES_PER_PROVIDER + 1):
            try:
                text = _call_provider(provider, system, user, json_mode, max_tokens, temperature)
            except Exception:
                logger.warning(
                    "llm provider attempt failed",
                    extra={"provider": provider, "attempt": attempt},
                    exc_info=True,
                )
                continue

            fell_back = position > 0
            latency_ms = int((time.monotonic() - call_start) * 1000)
            logger.info(
                "llm call served",
                extra={"provider": provider, "latency_ms": latency_ms, "fell_back": fell_back},
            )
            return LLMResult(text=text, provider=provider)

    latency_ms = int((time.monotonic() - call_start) * 1000)
    logger.error(
        "llm call failed on every provider",
        extra={"provider": None, "latency_ms": latency_ms, "fell_back": True},
    )
    raise LLMUnavailable("all LLM providers failed")
