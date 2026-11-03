"""What lane's tests stand on beside what every plugin's tests do: lane's code on sys.path, its
modules taken by each test from here, so they are found whichever test runs first; and the
README's plugin `changelog`, made in a test's folder, with its subagent `writer`, and the events
Claude Code hands its hooks as the hooks reference documents them."""

from __future__ import annotations

import json
import os
import sys
from typing import Any

LANE = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "plugins", "lane")
)
CODE = os.path.join(LANE, "hooks", "lane")
DOMAIN = os.path.join(CODE, "core", "domain")
sys.path[:0] = [CODE, DOMAIN, os.path.join(LANE, "..", "..", "dev", "lane")]

import forms  # noqa: F401
import guard  # noqa: F401
import hook  # noqa: F401
import lanes  # noqa: F401
import ports  # noqa: F401
import rules  # noqa: F401
import schema  # noqa: F401
import step  # noqa: F401
import template  # noqa: F401
import testing
from lanes import run_only, write_only  # noqa: F401

AGENT = "changelog:writer"
# The README's subagent `writer` before any lane is laid.
WRITER = """---
name: writer
description: Writes the CHANGELOG.md entries for the commits since its last version.
---

## Steps

1. Read `CHANGELOG.md` to learn its last version and its form.
2. Read the commits since then with `git log --oneline`.
3. Write the new entries into `CHANGELOG.md`.
4. Reply with the entries you wrote.
"""
RUN = "Run only `git log --oneline`."
WRITE = "Write only `CHANGELOG.md`."
# `writer` with the README's two lanes laid on steps 2 and 3, as `lay.py write` writes it.
LAID = WRITER.replace("`git log --oneline`.\n", f"`git log --oneline`. {RUN}\n").replace(
    "into `CHANGELOG.md`.\n", f"into `CHANGELOG.md`. {WRITE}\n"
)
# The README's lanes, as hooks/lanes.json holds them.
STEPS = [
    {"step": 2, "lanes": [{"lane": "run_only", "takes": ["git log --oneline"]}]},
    {"step": 3, "lanes": [{"lane": "write_only", "takes": ["CHANGELOG.md"]}]},
]
RULES = {"subagents": [{"name": "writer", "steps": STEPS}]}


class PluginTest(testing.FolderTest):
    """A test with the README's plugin `changelog` in `base/changelog`, its subagent `writer` in
    `agents/writer.md`, the project it works on being `base`."""

    def setUp(self) -> None:
        super().setUp()
        self.plugin = os.path.join(self.base, "changelog")
        self.write_json(self.manifest(), {"name": "changelog", "version": "0.1.0"})
        self.agent_file = os.path.join(self.plugin, "agents", "writer.md")
        self.write(self.agent_file, WRITER)

    def manifest(self) -> str:
        """The plugin's manifest."""
        return os.path.join(self.plugin, ".claude-plugin", "plugin.json")

    def lay(self, steps: list[dict[str, Any]] | None = None, text: str = LAID) -> None:
        """Lays the README's lanes in `writer`, or the steps given, as `lay.py write` writes
        them: its file saying their sentences, and hooks/lanes.json."""
        self.write(self.agent_file, text)
        laid = {"subagents": [{"name": "writer", "steps": STEPS if steps is None else steps}]}
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)

    def event(self, tool: str, given: dict[str, Any], agent: str | None = AGENT) -> dict:
        """A PreToolUse event of a call of the tool with the input, in the fields the hooks
        reference documents, made in `base` by the subagent of the type, or by the main
        conversation where it is None."""
        event = {
            "session_id": "s1",
            "transcript_path": os.path.join(self.base, "s1.jsonl"),
            "cwd": self.base,
            "permission_mode": "bypassPermissions",
            "hook_event_name": "PreToolUse",
            "tool_name": tool,
            "tool_input": given,
            "tool_use_id": "toolu_1",
        }
        return event if agent is None else {**event, "agent_id": "a1", "agent_type": agent}

    def bash(self, command: str, agent: str | None = AGENT) -> dict:
        """A PreToolUse event of a Bash call of the command."""
        return self.event("Bash", {"command": command, "description": "d"}, agent)

    def written(self, path: str, tool: str = "Write") -> dict:
        """A PreToolUse event of a call of the tool writing the file at the path."""
        if tool == "NotebookEdit":
            return self.event(tool, {"notebook_path": path, "new_source": "x"})
        return self.event(tool, {"file_path": path, "content": "x"})


def answer(text: str) -> dict:
    """The JSON a hook printed."""
    return json.loads(text) if text else {}
