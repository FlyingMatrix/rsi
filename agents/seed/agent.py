"""
    Generation-0 seed agent: the simplest thing that can solve a kata.

    This file is the scaffold the DGM will later copy and mutate. 
    Everything the agent knows how to do lives here as ordinary Python, so it can be rewritten. 
    Intentionally minimal — one shot, no self-repair — to leave obvious room for improvement.
"""

from __future__ import annotations
import re


SYSTEM_PROMPT = (
    "You are an expert Python programmer. "
    "Write correct, self-contained code using only the Python standard library. "
    "Respond with exactly one ```python code block and no prose."
)


def build_prompt(task: dict) -> str:
    return f"""Write a Python solution for the following task.

{task['spec']}

Requirements:
- Define a module-level function named `{task['entry_point']}`.
- Use only the Python standard library.

Example tests your solution must pass:
```python
{task['public_tests']}
```

Return ONLY the solution as a single ```python code block."""


def extract_code(text: str) -> str:
    """
        Pull code out of the model's reply. Prefer fenced blocks; fall back to raw text.
    """
    blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    if blocks:
        return blocks[-1].strip()      # last block is usually the final answer
    return text.strip()


def solve(task: dict, llm) -> str:
    """
        Given a kata agent-view, return solution source code (defines the entry_point).
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_prompt(task)},
    ]
    response = llm.chat(messages, think=True)   # thinking ON
    return extract_code(response.text)
