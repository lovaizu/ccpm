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
SCRIPTS = os.path.join(LANE, "scripts")
sys.path[:0] = [CODE, DOMAIN, SCRIPTS, os.path.join(LANE, "..", "..", "dev", "lane")]

import entries  # noqa: F401
import forms  # noqa: F401
import guard  # noqa: F401
import hook  # noqa: F401
import lanes  # noqa: F401
import lay  # noqa: F401
import layer  # noqa: F401
import placed  # noqa: F401
import ports  # noqa: F401
import proposal  # noqa: F401
import rules  # noqa: F401
import schema  # noqa: F401
import step  # noqa: F401
import steps  # noqa: F401
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
STEPS: list[dict[str, Any]] = [
    {"step": 2, "lanes": [{"lane": "run_only", "takes": ["git log --oneline"]}]},
    {"step": 3, "lanes": [{"lane": "write_only", "takes": ["CHANGELOG.md"]}]},
]
RULES = {"subagents": [{"name": "writer", "steps": STEPS}]}
# The README's proposal, laying them.
PROPOSAL = {"plugin": "changelog", "subagents": [{"name": "writer", "steps": STEPS}]}
# Where the README keeps it, from the root of the repository.
PROPOSED = os.path.join(".lane", "20261102-changelog", "changelog.json")
# What the README's `lay.py print` prints of it.
PRINTED = """Lanes of writer, each hook acting in writer alone:
  step 2  run:   Run only `git log --oneline`.  hook run_only
  step 3  write: Write only `CHANGELOG.md`.     hook write_only

2. Read the commits since then with `git log --oneline`. Run only `git log --oneline`.
3. Write the new entries into `CHANGELOG.md`. Write only `CHANGELOG.md`.
"""
# The hook's command `lay.py write` writes for changelog with lanes laid in writer alone.
COMMAND = (
    'python3 -c "import sys; sys.exit(sys.version_info < (3, 9))" 2>/dev/null'
    ' || { e=; while IFS= read -r l || [ -n "$l" ]; do e="$e$l"; l=; done; case "$e" in'
    """ *'"agent_type":"changelog:writer"'*|*'"agent_type": "changelog:writer"'*)"""
    """ echo '{"systemMessage": "changelog: install Python 3.9 or later, run as python3, for its"""
    """ hooks to run", "hookSpecificOutput": {"hookEventName": "PreToolUse","""
    """ "permissionDecision": "deny", "permissionDecisionReason": "changelog: install Python 3.9"""
    """ or later, run as python3, for its hooks to run"}}';; esac; exit 0; };"""
    ' exec python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lane/pretooluse.py" changelog'
)
# Its entry of PreToolUse, run on every tool call, blocking the call where the hook fails.
ENTRY = {
    "matcher": "*",
    "hooks": [{"type": "command", "timeout": 10, "command": COMMAND, "onFailure": "block"}],
}


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

    def lay(self, laid_steps: list[dict[str, Any]] | None = None, text: str = LAID) -> None:
        """Lays the README's lanes in `writer`, or the steps given, as `lay.py write` writes
        them: its file saying their sentences, and hooks/lanes.json."""
        self.write(self.agent_file, text)
        given = STEPS if laid_steps is None else laid_steps
        laid = {"subagents": [{"name": "writer", "steps": given}]}
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


class LayTest(PluginTest):
    """A test of `lay.py` at the root of the repository `base`, the README's proposal kept where
    the README keeps it."""

    def setUp(self) -> None:
        super().setUp()
        self.propose(PROPOSAL)

    def propose(self, given: Any) -> str:
        """Writes the proposal where the README keeps it, as JSON, or as the text given."""
        self.write(PROPOSED, given if isinstance(given, str) else json.dumps(given))
        return PROPOSED

    def proposal(self, **changed: Any) -> dict:
        """The README's proposal with writer's entry changed as given."""
        return {"plugin": "changelog", "subagents": [{"name": "writer", "steps": STEPS, **changed}]}


def answer(text: str) -> dict:
    """The JSON a hook printed."""
    return json.loads(text) if text else {}
