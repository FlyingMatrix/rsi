from pathlib import Path

from mini_dgm.llm import LLMClient
from mini_dgm.tasks import load_katas
from mini_dgm.sandbox import run_tests
from mini_dgm.runner import load_agent

PROJECT = Path(__file__).resolve().parents[1]   # .resolve() ensures it's an absolute path
SEED = PROJECT / "agents" / "seed"

llm = LLMClient()
kata = {k.id: k for k in load_katas()}["rle_encode"]
agent = load_agent(SEED)

print(f"Seed agent solving '{kata.id}' (this may take a while on an 8B model)...")
solution = agent.solve(kata.agent_view(), llm)
print("\n--- generated solution ---")
print(solution)
print("--------------------------\n")

pub = run_tests(solution, kata.public_tests, timeout_s=kata.timeout_s)
print(f"PUBLIC: {pub.passed}/{pub.total} ({pub.score:.0%})  status={pub.status}")

hid = run_tests(solution, kata.hidden_tests, timeout_s=kata.timeout_s)
print(f"HIDDEN: {hid.passed}/{hid.total} ({hid.score:.0%})  status={hid.status}")

"""
    > Output of running "python scripts\test_seed_agent.py":

        ...
"""