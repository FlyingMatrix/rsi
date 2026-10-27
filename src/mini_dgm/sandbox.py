from __future__ import annotations          # Enables postponed evaluation of type hints
                    
import shutil                               # Shell Utilities - high-level file operations
import subprocess                           # Spawns new processes
import tempfile                             # Generates temporary files and directories that automatically delete themselves when scripts finish
import time                                 # Provides time-related functions
import uuid                                 # Generates random, globally unique identifiers (UUIDs)
import xml.etree.ElementTree as ET          # Parses and creates XML data
from dataclasses import dataclass, field    # Provides a clean, lightweight way to create classes
from pathlib import Path                    # An object-oriented way to handle file paths

IMAGE = "minidgm-sandbox:latest"
STARTUP_OVERHEAD_S = 15.0                   # container start + pytest import, added to the kata's execution timeout budget


@dataclass
class TestFailure:
    name: str
    message: str


@dataclass
class SandboxResult:
    status: str                              # "completed" | "timeout" | "error"
    passed: int
    total: int
    failures: list[TestFailure] = field(default_factory=list)   # For new instances, list() will be called to generate a completely brand-new, independent empty list just for that specific instances
    stdout: str = ""
    stderr: str = ""
    duration_s: float = 0.0

    @property
    def score(self) -> float:
        return self.passed / self.total if self.total else 0.0

    @property
    def all_passed(self) -> bool:
        return self.total > 0 and self.passed == self.total


def run_tests(
    solution_code: str,
    test_code: str,
    *,
    timeout_s: float = 5.0,
    image: str = IMAGE,
    memory: str = "256m",                   # The memory (RAM) limit assigned to the Docker container
    cpus: str = "1.0"                       # The CPU resource limit assigned to the container (equivalent to 1 full CPU core)
) -> SandboxResult:
    """
        run_tests is a coordinator, not a tester. It arranges files on disk, launches Docker, and reads back a report. 
        The real test execution is pytest, running inside the cage.

        A data flow of run_tests():

            solution_code ─┐
                           ├─► written as two files ─► pytest (in Docker) runs test_suite.py
            test_code ─────┘                                │  which does `from solution import encode`
                                                            │  and calls encode(...) in each test
                                                            ▼
                                                        report.xml ─► _parse_junit ─► SandboxResult(passed/total)
    """
    
    work = Path(tempfile.mkdtemp(prefix="minidgm_"))
    (work / "solution.py").write_text(solution_code, encoding="utf-8")
    (work / "test_suite.py").write_text(test_code, encoding="utf-8")
    """
        work/
        ├── solution.py       # def encode(s): ...        (from solution_code)
        └── test_suite.py     # from solution import encode; def test_...  (from test_code)
    """

    name = f"minidgm-{uuid.uuid4().hex[:12]}"
    mount_src = work.as_posix()                     # forward slashes: converts to a forward-slash format to ensure that Docker and volume-mounting commands can read the path cleanly

    cmd = [
        "docker", "run", "--name", name,
        "--network", "none",                        # no network
        "--memory", memory, "--cpus", cpus,         # restricts memory and CPU resource usage
        "--pids-limit", "128",                      # caps the maximum number of processes/threads to protect against fork bombs
        "--cap-drop", "ALL",                        # removes all Linux kernel capabilities from the container, vastly reducing its privileges
        "--security-opt", "no-new-privileges",      # prevents processes within the container from gaining new privileges
        "-e", "PYTHONDONTWRITEBYTECODE=1",          # disables writing .pyc (bytecode cache) to the disk
        "-e", "PYTHONPATH=/work",                   # adds /work to Python's module search path
        "-v", f"{mount_src}:/work",                 # mounts a local directory (mount_src) into the container at /work so the test files can be accessed
        "-w", "/work",                              # sets the working directory inside the container
        image,                                      # the Docker image being used
        "python", "-m", "pytest", "-q",             # disables cache generation, writes a JUnit XML report to the mounted volume, and runs test_suite.py
        "-p", "no:cacheprovider",
        "--junitxml=/work/report.xml",
        "test_suite.py"
    ]

    start = time.monotonic()
    status, stdout, stderr = "completed", "", ""

    # Safely executes the Docker container with a time limit (timeout) and make sure the container is always cleaned up afterward
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=timeout_s + STARTUP_OVERHEAD_S
        )
        stdout, stderr = proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as e:
        status = "timeout"
        stdout = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        stderr = e.stderr.decode() if isinstance(e.stderr, bytes) else (e.stderr or "")
    finally:
        # Force-remove the container — this kills a runaway loop the client timeout left alive
        subprocess.run(["docker", "rm", "-f", name], capture_output=True, text=True)

    duration = time.monotonic() - start
    passed, total, failures = _parse_junit(work / "report.xml")

    # Completed but zero tests parsed => something broke (import/syntax error).
    if status == "completed" and total == 0:
        status = "error"

    # recursively deletes an entire folder, including all files and subfolders inside it
    shutil.rmtree(work, ignore_errors=True)

    return SandboxResult(
        status=status, passed=passed, total=total, failures=failures,
        stdout=stdout, stderr=stderr, duration_s=duration
    )


def _parse_junit(report_path: Path) -> tuple[int, int, list[TestFailure]]:
    if not report_path.exists():
        return 0, 0, []
    try:
        root = ET.parse(report_path).getroot()
    except ET.ParseError:
        return 0, 0, []

    passed = total = 0
    failures: list[TestFailure] = []
    for case in root.iter("testcase"):
        total += 1
        # NOTE: must use "is not None" — an Element is falsy when it has no children,
        # so `failure or error` would silently misclassify. Classic ElementTree trap.
        fail = case.find("failure")     # if the test failed an assertion, it returns the Element object, if the test passed, it returns None.
        err = case.find("error")        # if an unexpected exception or system error occurred during the test, it returns the Element. Otherwise, it returns None.
        bad = fail if fail is not None else err
        if bad is not None:
            msg = (bad.get("message") or (bad.text or "")).strip()
            failures.append(TestFailure(name=case.get("name", "?"), message=msg[:500]))
        elif case.find("skipped") is None:
            passed += 1

    return passed, total, failures
