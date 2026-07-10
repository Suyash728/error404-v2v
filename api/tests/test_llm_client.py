import pytest

from services import llm_client
from services.llm_client import LLMResult, LLMUnavailable, complete


def test_falls_back_to_groq_when_gemini_fails(monkeypatch):
    monkeypatch.setenv("LLM_PRIMARY", "gemini")

    def failing_gemini(system, user, json_mode, max_tokens, temperature):
        raise RuntimeError("gemini is down")

    def working_groq(system, user, json_mode, max_tokens, temperature):
        return "groq response"

    monkeypatch.setattr(llm_client, "_call_gemini", failing_gemini)
    monkeypatch.setattr(llm_client, "_call_groq", working_groq)

    result = complete(system="sys", user="hello")

    assert result == LLMResult(text="groq response", provider="groq")


def test_raises_llm_unavailable_when_every_provider_fails(monkeypatch):
    monkeypatch.setenv("LLM_PRIMARY", "gemini")

    def always_fails(system, user, json_mode, max_tokens, temperature):
        raise RuntimeError("down")

    monkeypatch.setattr(llm_client, "_call_gemini", always_fails)
    monkeypatch.setattr(llm_client, "_call_groq", always_fails)

    with pytest.raises(LLMUnavailable):
        complete(system="sys", user="hello")
