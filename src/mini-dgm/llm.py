from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from openai import OpenAI


@dataclass
class LLMConfig:
    """All knobs in one place — later this gets populated from config.yaml."""
    model: str = "qwen3:8b"
    base_url: str = "http://localhost:11434/v1"
    api_key: str = "ollama"            # dummy; Ollama ignores it
    temperature: float = 0.2           # low = more deterministic (good for code)
    max_tokens: int | None = None      # None: without upper limitation
    timeout: float = 600.0             # local models can be slow; be generous
    think: bool = True                 # default reasoning behaviour for this client, support chain-of-thought if available


@dataclass
class LLMResponse:
    """A backend-agnostic, normalized result. The rest of the system only sees this."""
    text: str                          # cleaned assistant answer
    reasoning: str | None              # chain-of-thought, if the backend exposed it
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    raw: Any = field(default=None, repr=False)   # full SDK object, for debugging


def _clean(text: str) -> str:
    """Strip the noise: leaked control tokens and inline think-blocks."""
    if not text:
        return ""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)  # older template style
    for tok in ("/think", "/no_think"):
        text = text.replace(tok, "")
    return text.strip()


class LLMClient:
    """Thin, provider-agnostic wrapper. Swap the backend by changing config, not callers."""

    def __init__(self, config: LLMConfig | None = None) -> None:
        self.config = config or LLMConfig()
        self._client = OpenAI(base_url=self.config.base_url, api_key=self.config.api_key)

    def chat(
        self,
        messages: list[dict],
        *,
        think: bool | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        cfg = self.config
        use_think = cfg.think if think is None else think

        msgs = [dict(m) for m in messages]          # copy so we never mutate the caller's list
        if not use_think:
            msgs = self._disable_thinking(msgs)

        resp = self._client.chat.completions.create(
            model=cfg.model,
            messages=msgs,
            temperature=cfg.temperature if temperature is None else temperature,
            max_tokens=cfg.max_tokens if max_tokens is None else max_tokens,
            timeout=cfg.timeout,
        )

        msg = resp.choices[0].message
        usage = resp.usage                          # tracks token consumption for that specific request (prompt_tokens, completion_tokens, etc.)

        return LLMResponse(
            text=_clean(msg.content or ""),
            reasoning=getattr(msg, "reasoning", None),   # non-standard field; may be absent
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            model=resp.model,
            raw=resp
        )

    @staticmethod
    def _disable_thinking(messages: list[dict]) -> list[dict]:
        """Qwen3 soft-switch: appending '/no_think' to the last user turn skips reasoning."""
        for m in reversed(messages):
            if m.get("role") == "user":
                m["content"] = (str(m["content"]).rstrip() + " /no_think").strip()
                return messages
        messages.append({"role": "user", "content": "/no_think"})
        return messages

