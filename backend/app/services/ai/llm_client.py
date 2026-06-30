"""LLM client seam. Anthropic Claude when configured; otherwise None (callers
fall back to a deterministic, data-derived narration). Mockable in tests.

`anthropic` is an optional dependency (`pip install -e ".[ai]"`); it is imported
lazily so the app and tests run without it.
"""

from typing import Protocol

from app.core.config import settings


class LLMClient(Protocol):
    def complete(self, *, system: str, prompt: str) -> str: ...


class AnthropicLLMClient:
    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    def complete(self, *, system: str, prompt: str) -> str:
        import anthropic  # lazy import — optional dependency

        client = anthropic.Anthropic(api_key=self._api_key)
        message = client.messages.create(
            model=self._model,
            max_tokens=400,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        parts = [
            block.text
            for block in message.content
            if getattr(block, "type", None) == "text"
        ]
        return "".join(parts).strip()


def get_llm_client() -> LLMClient | None:
    if settings.anthropic_api_key:
        return AnthropicLLMClient(settings.anthropic_api_key, settings.ai_model)
    return None
