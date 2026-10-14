from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import httpx                           # we need to talk to Ollama's native API directly to toggle reasoning


@dataclass
class LLMConfig:
    """All knobs in one place — later this gets populated from config.yaml."""
    model: str = "qwen3:8b"
    host: str = "http://localhost:11434"
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
    """Provider-agnostic wrapper. Backed by Ollama's native /api/chat, because the OpenAI-compatible /v1 layer cannot toggle Qwen3's thinking."""

    def __init__(self, config: LLMConfig | None = None) -> None:
        self.config = config or LLMConfig()
        self._http = httpx.Client(base_url=self.config.host, timeout=self.config.timeout)

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

        # Native API puts sampling params under "options"; "think" is top-level.
        options: dict[str, Any] = {
            "temperature": cfg.temperature if temperature is None else temperature,
            "num_predict": cfg.max_tokens if max_tokens is None else max_tokens     # Ollama's name for max output tokens
        }

        payload = {
            "model": cfg.model,
            "messages": list(messages),
            "stream": False,
            "think": use_think,
            "options": options
        }

        resp = self._http.post("/api/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()

        msg = data.get("message", {})
        # These counts can be absent (e.g. when the prompt is fully cached) -> default 0.
        prompt_tokens = data.get("prompt_eval_count", 0)
        completion_tokens = data.get("eval_count", 0)

        return LLMResponse(
            text=_clean(msg.get("content", "")),
            reasoning=(msg.get("thinking") or None),   # native puts chain-of-thought in message.thinking
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            model=data.get("model", cfg.model),
            raw=data
        )

