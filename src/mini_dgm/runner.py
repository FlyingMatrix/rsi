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


