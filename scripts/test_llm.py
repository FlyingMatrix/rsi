from mini_dgm.llm import LLMClient

client = LLMClient()

print("=== think=True (default) ===")
r1 = client.chat([{"role": "user", "content": "Reply with exactly: pong"}], think=True)
print("text:     ", repr(r1.text))
print("reasoning:", (r1.reasoning or "")[:80], "...")
print("tokens:   ", r1.completion_tokens, "completion")

print("\n=== think=False ===")
r2 = client.chat([{"role": "user", "content": "Reply with exactly: pong"}], think=False)
print("text:     ", repr(r2.text))
print("reasoning:", r2.reasoning)
print("tokens:   ", r2.completion_tokens, "completion")

"""
    > Output of running "python test_llm.py":

        === think=True (default) ===
        text:      'pong'
        reasoning: Okay, the user wants me to reply with exactly "pong /think". Let me make sure I  ...
        tokens:    241 completion

        === think=False ===
        text:      'pong'
        reasoning: None
        tokens:    2 completion
"""
