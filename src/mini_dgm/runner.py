"""
    Load an agent scaffold from a directory and run it.

    Agents are plain Python modules (agent.py) living in their own folders — the seed in agents/seed/, 
    and later each evolved variant in its own archive folder. 
    We import them dynamically by path so the orchestrator can run any of them.
"""

from __future__ import annotations

import importlib.util
import uuid
from pathlib import Path
from types import ModuleType


def load_agent(agent_dir: str | Path) -> ModuleType:
    agent_dir = Path(agent_dir)
    agent_file = agent_dir / "agent.py"
    if not agent_file.exists():
        raise FileNotFoundError(f"No agent.py in {agent_dir}")

    # Unique module name so loading many variants never collides in sys.modules.
    mod_name = f"minidgm_agent_{agent_dir.name}_{uuid.uuid4().hex[:8]}"
    spec = importlib.util.spec_from_file_location(mod_name, agent_file)
    module = importlib.util.module_from_spec(spec)      # <module 'mod_name' from 'agent_file'>
    spec.loader.exec_module(module)                     # execute code -> now you can use module.build_prompt(), module.extract_code() and module.solve()

    if not hasattr(module, "solve"):
        raise AttributeError(f"Agent in {agent_dir} has no solve(task, llm) function")
    return module
