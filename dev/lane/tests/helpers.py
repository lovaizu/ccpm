"""What lane's tests stand on beside what every plugin's tests do: lane's folders on sys.path, and a
builder's plugin `notes` made in a test's folder, its subagent `changelog-writer` with the steps of
lane's README."""

from __future__ import annotations

import json
import os
import sys
from typing import Any

LANE = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "lane")
)
CODE = os.path.join(LANE, "hooks", "lane")
SCRIPTS = os.path.join(LANE, "scripts")
sys.path[:0] = [CODE, SCRIPTS, os.path.join(LANE, "..", "dev", "lane")]

# lane's modules, taken by each test from here, so they are found whichever test runs first.
import call  # noqa: F401
import forms  # noqa: F401
import hook  # noqa: F401
import lanes  # noqa: F401
import lay  # noqa: F401
import record  # noqa: F401
import schema  # noqa: F401
import shell  # noqa: F401
import step  # noqa: F401
import template  # noqa: F401
import testing
from lanes import hands_off, in_form, read_only, read_whole, start_with  # noqa: F401

AGENT = "notes:changelog-writer"
# The plugin's folder given to a lane that reads no file of the plugin.
NO_PLUGIN = ""
SENTENCE = "Do not run `git commit` or `git push`."
# The subagent's file before any lane is laid, its file named apart from its name, as Claude Code
# takes the name from the frontmatter.
STEPS = """---
name: changelog-writer
description: Writes the changelog of a project.
tools: Bash, Read, Write
---

## Role

You write the changelog.

## Steps

1. Read the commits since the last release.
2. Sort them into Added, Changed and Fixed.
3. Write the new entries into `CHANGELOG.md`.
   - Out: the entries, each one line.
4. Reply with what you wrote.
"""
# The subagent's file with hands_off laid on step 3, as lane:up writes it.
LAID = STEPS.replace("`CHANGELOG.md`.\n", f"`CHANGELOG.md`. {SENTENCE}\n")


class PluginTest(testing.FolderTest):
    """A test with the builder's plugin `notes` in `base/notes`, its subagent in
    `agents/writer.md`."""

    def setUp(self) -> None:
        super().setUp()
        self.plugin = os.path.join(self.base, "notes")
        self.write_json(
            os.path.join(self.plugin, ".claude-plugin", "plugin.json"), {"name": "notes"}
        )
        self.agent_file = os.path.join(self.plugin, "agents", "writer.md")
        self.write(self.agent_file, STEPS)

    def event(self, command: str, agent_type: str | None = AGENT, tool: str = "Bash") -> dict:
        """A PreToolUse event in Claude Code's shape for a call of the tool with the command, in
        the subagent of the type, or in the main conversation where it is None."""
        return self.called(tool, {"command": command}, agent_type)

    def called(self, tool: str, given: dict, agent_type: str | None = AGENT) -> dict:
        """A PreToolUse event in Claude Code's shape for a call of the tool with the input, in the
        session whose record is `session.jsonl`, in the subagent a1 of the type, or in the main
        conversation where it is None."""
        event = {
            "hook_event_name": "PreToolUse",
            "cwd": self.base,
            "tool_name": tool,
            "tool_input": given,
            "transcript_path": os.path.join(self.base, "session.jsonl"),
        }
        if agent_type:
            event.update(agent_id="a1", agent_type=agent_type)
        return event

    def record(self, calls: list) -> None:
        """Writes the record of the subagent a1 where Claude Code keeps it for the events above, of
        the calls, each a tool, its input and what it gave back, as `recorded` takes them."""
        place = os.path.join(self.base, "session", "subagents", "agent-a1.jsonl")
        self.write(place, recorded(self.base, calls))

    def stream(self, command: str, agent_type: str | None = AGENT) -> str:
        """The event as Claude Code hands it on stdin."""
        return json.dumps(self.event(command, agent_type))


def bash(command: str) -> tuple[str, dict[str, Any], str]:
    """A Bash call of the command, as `recorded` takes it, giving back nothing lane reads."""
    return ("Bash", {"command": command}, "")


def recorded(cwd: str, calls: list) -> str:
    """A subagent's record as Claude Code 2.1.306 writes it, cut to what lane reads and what lies
    beside it, for each call a tool, its input and what it gave back, None for a call not yet
    back: the prompt first, an attachment, and each call as an assistant's tool use and a user's
    tool result, each with the request as sent after it, here given text apart from them."""
    lines: list[dict[str, Any]] = [
        {"type": "user", "cwd": cwd, "message": {"role": "user", "content": "Do your steps."}},
        {"type": "attachment", "cwd": cwd, "attachment": {"type": "date", "date": "2026-10-22"}},
    ]
    for number, (tool, given, result) in enumerate(calls):
        use = {"type": "tool_use", "id": f"toolu_{number}", "name": tool, "input": given}
        lines.append(
            {"type": "assistant", "cwd": cwd, "message": {"role": "assistant", "content": [use]}}
        )
        sent = {**use, "input": {"command": "cd / && true"}}
        lines.append(
            {"type": "api-request-blob", "message": {"role": "assistant", "content": [sent]}}
        )
        if result is not None:
            back = {"tool_use_id": f"toolu_{number}", "type": "tool_result", "content": result}
            lines.append(
                {"type": "user", "cwd": cwd, "message": {"role": "user", "content": [back]}}
            )
            sent = {**back, "content": "as sent"}
            lines.append(
                {"type": "api-request-blob", "message": {"role": "user", "content": [sent]}}
            )
    return "".join(json.dumps(line) + "\n" for line in lines)
