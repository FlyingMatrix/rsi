# enable postponed evaluation of annotations
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

# src/minidgm/tasks.py -> parents[2] is the project root (rsi/)
TASKS_DIR = Path(__file__).resolve().parents[2] / "tasks"


@dataclass(frozen=True)
class Kata:
    id: str                                 # a unique identifier for the kata
    spec: str                               # the problem description, usually markdown text
    entry_point: str                        # the function or class name the user's code needs to implement
    public_tests: str                       # tests that are visible to the agent/user to help them debug
    hidden_tests: str = field(repr=False)   # evaluation tests kept secret from the user (field(repr=False))
    timeout_s: float = 5.0                  # metadata -> execution time limits
    difficulty: str = "unknown"             # metadata -> difficulty ratings
    tags: tuple[str, ...] = ()              # metadata -> category tags
    path: Path | None = None                # metadata -> the source folder path

    def agent_view(self) -> dict:
        """Exactly what the agent is allowed to see. Hidden tests are NOT here."""
        return {
            "id": self.id,
            "spec": self.spec,
            "entry_point": self.entry_point,
            "public_tests": self.public_tests
        }


def load_kata(folder: Path) -> Kata:
    meta = yaml.safe_load((folder / "meta.yaml").read_text(encoding="utf-8"))
    return Kata(
        id=meta["id"],
        spec=(folder / "spec.md").read_text(encoding="utf-8"),
        entry_point=meta["entry_point"],
        public_tests=(folder / "tests_public.py").read_text(encoding="utf-8"),
        hidden_tests=(folder / "tests_hidden.py").read_text(encoding="utf-8"),
        timeout_s=float(meta.get("timeout_s", 5)),
        difficulty=meta.get("difficulty", "unknown"),
        tags=tuple(meta.get("tags", [])),
        path=folder,
    )


def load_katas(tasks_dir: Path = TASKS_DIR) -> list[Kata]:
    folders = [p for p in sorted(tasks_dir.iterdir()) if (p / "meta.yaml").exists()]
    return [load_kata(p) for p in folders]

