"""What Lane's tests stand on: where Lane's code lies, the changelog plugin of the README's
walkthrough, a double of Claude Code's command line, and a temporary repository for each test."""

from __future__ import annotations

import contextlib
import io
import json
import os
import runpy
import shlex
import shutil
import sys
import tempfile
import unittest
from dataclasses import dataclass
from typing import Any

TOP = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
LANE = os.path.join(TOP, "plugins", "lane")
CHANGELOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "changelog")

sys.path[:0] = [os.path.join(LANE, "hooks", "lane"), os.path.join(LANE, "scripts")]

# What `claude plugin validate` printed on Claude Code 2.1.319: first for a plugin it took, then
# for a plugin whose hooks.json held a number for its hooks.
PASSED = "✔ Validation passed"
FAILED = "✘ Found 1 error:\n  ❯ hooks: Invalid input: expected record, received number"


@dataclass
class Ran:
    """What a script gave as it ran: its exit code, and what it printed on stdout and stderr."""

    returncode: int
    stdout: str
    stderr: str


def run_script(argv: list[str], given: str, env: dict[str, str], cwd: str) -> Ran:
    """Runs the Python script that argv names in this process, as a new process of Python would
    run it: as `__main__`, with argv, the text on stdin, the environment, and the folder, each put
    back after it."""
    saved = (sys.argv, sys.stdin, dict(os.environ), os.getcwd(), list(sys.path))
    out, err = io.StringIO(), io.StringIO()
    code = 0
    try:
        sys.argv, sys.stdin = list(argv), io.StringIO(given)
        os.environ.clear()
        os.environ.update(env)
        os.chdir(cwd)
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                runpy.run_path(argv[0], run_name="__main__")
            except SystemExit as exit:
                code = exit.code if isinstance(exit.code, int) else (0 if exit.code is None else 1)
    finally:
        sys.argv, sys.stdin = saved[0], saved[1]
        os.environ.clear()
        os.environ.update(saved[2])
        os.chdir(saved[3])
        sys.path[:] = saved[4]
    return Ran(code, out.getvalue(), err.getvalue())


def run_entry(command: str, given: str, env: dict[str, str], plugin: str) -> Ran:
    """Runs a hook entry's command as the double of Claude Code: the plugin's folder put in for
    `${CLAUDE_PLUGIN_ROOT}`, and the Python script it names run in this process."""
    words = shlex.split(command.replace("${CLAUDE_PLUGIN_ROOT}", plugin))
    if words[0] != "python3":
        raise AssertionError(f"the hook entry runs {words[0]}, not python3: {command}")
    return run_script(words[1:], given, {**env, "CLAUDE_PLUGIN_ROOT": plugin}, plugin)


class RepositoryTest(unittest.TestCase):
    """Each test runs in a git repository of its own, `root`, that holds a copy of changelog and a
    double of `claude` first on PATH, removed after it."""

    def setUp(self) -> None:
        self.root = os.path.realpath(tempfile.mkdtemp(prefix="lane-tests-"))
        self.addCleanup(shutil.rmtree, self.root)
        os.mkdir(os.path.join(self.root, ".git"))
        shutil.copytree(CHANGELOG, os.path.join(self.root, "changelog"))
        self.bin = os.path.join(self.root, ".bin")
        os.mkdir(self.bin)
        self.claude(PASSED, 0)
        self.env = {**os.environ, "PATH": self.bin + os.pathsep + os.environ["PATH"]}

    def claude(self, printed: str, code: int) -> None:
        """Makes the double of `claude` print the text and exit with the code, as the real one did
        for `claude plugin validate`."""
        path = os.path.join(self.bin, "claude")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"#!/bin/sh\ncat <<'EOF'\n{printed}\nEOF\nexit {code}\n")
        os.chmod(path, 0o755)

    def path(self, *parts: str) -> str:
        """The path under the repository."""
        return os.path.join(self.root, *parts)

    def read(self, *parts: str) -> str:
        """The text of the file under the repository."""
        with open(self.path(*parts), encoding="utf-8") as f:
            return f.read()

    def write(self, text: str, *parts: str) -> None:
        """Writes the text at the path under the repository, making its folder."""
        path = self.path(*parts)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def propose(self, proposal: Any) -> str:
        """Keeps the proposal where the README says, and returns its path."""
        text = proposal if isinstance(proposal, str) else json.dumps(proposal)
        self.write(text, ".lane", "20261110-changelog", "changelog.json")
        return self.path(".lane", "20261110-changelog", "changelog.json")

    def lay(self, *args: str) -> Ran:
        """Runs lay.py as the user does, from the repository's root."""
        return run_script([os.path.join(LANE, "scripts", "lay.py"), *args], "", self.env, self.root)


WRITER_RUN_ONLY = {
    "plugin": "changelog",
    "subagents": [
        {
            "name": "writer",
            "steps": [{"step": 2, "lanes": [{"lane": "run_only", "takes": ["git log --oneline"]}]}],
        }
    ],
}


def bash(command: Any, agent: str | None = "changelog:writer") -> dict[str, Any]:
    """A PreToolUse event of a Bash call in the fields Claude Code 2.1.319 sent, of the subagent
    of the type `agent` names, or of the main conversation where it names none."""
    event: dict[str, Any] = {
        "session_id": "s1",
        "transcript_path": "/t/s1.jsonl",
        "cwd": "/repo",
        "permission_mode": "default",
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": command},
    }
    if agent is not None:
        event.update({"agent_id": "a1", "agent_type": agent})
    return event
