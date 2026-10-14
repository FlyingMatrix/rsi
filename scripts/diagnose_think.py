import httpx                      # installed already as an openai dependency
from openai import OpenAI

MODEL = "qwen3:8b"
PROMPT = [{"role": "user", "content": "Reply with exactly: pong"}]

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

def via_openai(label, **extra):
    r = client.chat.completions.create(model=MODEL, messages=PROMPT, **extra)
    msg = r.choices[0].message
    reasoning = getattr(msg, "reasoning", None) or ""
    print(f"[{label}] completion_tokens={r.usage.completion_tokens:>4}  "
          f"reasoning_len={len(reasoning):>4}  content={msg.content!r}")

def via_native(label, think):
    data = httpx.post(
        "http://localhost:11434/api/chat",
        json={"model": MODEL, "messages": PROMPT, "stream": False, "think": think},
        timeout=120,
    ).json()
    msg = data.get("message", {})
    print(f"[{label}] eval_count={data.get('eval_count'):>4}  "
          f"thinking_len={len(msg.get('thinking') or ''):>4}  content={msg.get('content')!r}")

print("--- OpenAI-compatible /v1 endpoint ---")
via_openai("A /v1 baseline (think on)")
via_openai("B /v1 extra_body think=False", extra_body={"think": False})
via_openai("C /v1 enable_thinking=False",
           extra_body={"chat_template_kwargs": {"enable_thinking": False}})

print("\n--- Native /api/chat endpoint ---")
via_native("D native think=True ", True)
via_native("E native think=False", False)

"""
    > Output of running "python diagnose_think.py":

        --- OpenAI-compatible /v1 endpoint ---
        [A /v1 baseline (think on)] completion_tokens=  76  reasoning_len= 297  content='pong /think'
        [B /v1 extra_body think=False] completion_tokens= 111  reasoning_len= 520  content='pong /think'
        [C /v1 enable_thinking=False] completion_tokens= 188  reasoning_len= 881  content='pong /think'

        --- Native /api/chat endpoint ---
        [D native think=True ] eval_count= 337  thinking_len=1591  content='pong /think'
        [E native think=False] eval_count=   2  thinking_len=   0  content='pong'
"""
