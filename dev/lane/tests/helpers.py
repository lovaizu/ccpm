"""What lane's tests stand on beside what every plugin's tests do: lane's code on sys.path, its
modules taken by each test from here, so they are found whichever test runs first; and the
README's plugin `changelog`, made in a test's folder, with its subagent `writer`, the routes of
docs/routes.md with its `lead` and `reviewer`, and the events Claude Code hands its hooks as the
hooks reference documents them."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from typing import Any
from unittest import mock

LANE = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "plugins", "lane")
)
CODE = os.path.join(LANE, "hooks", "lane")
DOMAIN = os.path.join(CODE, "core", "domain")
SCRIPTS = os.path.join(LANE, "scripts")
sys.path[:0] = [CODE, DOMAIN, SCRIPTS, os.path.join(LANE, "..", "..", "dev", "lane")]

import called  # noqa: F401
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
import result  # noqa: F401
import routes  # noqa: F401
import rules  # noqa: F401
import schema  # noqa: F401
import step  # noqa: F401
import steps  # noqa: F401
import template  # noqa: F401
import testing
from lanes import follow_routes, run_only, write_only  # noqa: F401

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
    ' exec python3 -B "${CLAUDE_PLUGIN_ROOT}/hooks/lane/pretooluse.py" changelog'
)
# Its entry of PreToolUse, run on every tool call, blocking the call where the hook fails.
ENTRY = {
    "matcher": "*",
    "hooks": [{"type": "command", "timeout": 10, "command": COMMAND, "onFailure": "block"}],
}
# The command of each other event's entry, which tells nothing where Python cannot run, as the
# PreToolUse entry stops each call then.
RUNS = (
    'python3 -c "import sys; sys.exit(sys.version_info < (3, 9))" 2>/dev/null || exit 0;'
    ' exec python3 -B "${{CLAUDE_PLUGIN_ROOT}}/hooks/lane/{script}.py" changelog'
)
# The entries lane lays for changelog with lanes laid in writer alone: PreToolUse's, and one for
# each other event lane acts on.
HOOKS = {
    "hooks": {
        "PreToolUse": [ENTRY],
        **{
            event: [
                {
                    "matcher": "*",
                    "hooks": [
                        {
                            "type": "command",
                            "timeout": 10,
                            "command": RUNS.format(script=event.lower()),
                        }
                    ],
                }
            ]
            for event in ("PostToolUse", "PostToolUseFailure", "SubagentStart", "SubagentStop")
        },
    }
}

# docs/routes.md's subagents of changelog beside writer: lead, the orchestrator, and reviewer,
# before any route is laid.
LEAD = """---
name: lead
description: Updates CHANGELOG.md for the next release, through writer and reviewer.
tools: Agent
---

## Steps

1. Have writer write the entries for the next release and reviewer review them.
2. Reply with the reviewed entries.
"""
REVIEWER = """---
name: reviewer
description: Compares the new CHANGELOG.md entries with the commits.
---

## Steps

1. Read the new entries in `CHANGELOG.md`.
2. Compare them with the commits, and reply with what you found.
"""
# docs/routes.md's routes for changelog.
ROUTES: dict[str, Any] = {
    "orchestrator": "lead",
    "step": 1,
    "routes": [
        {"from": "lead", "to": "writer"},
        {"from": "writer", "on": "written", "to": "reviewer"},
        {"from": "reviewer", "on": "more", "to": "writer"},
        {"from": "reviewer", "on": "good"},
    ],
}
FOLLOW = "Start each subagent you are told to start, until you are told to start no more."
# The result command a subagent gives a result by, as its step writes it.
GIVE = "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py"
END_WRITER = f"End by running `{GIVE} writer written`."
END_REVIEWER = f"End by running `{GIVE} reviewer more` or `{GIVE} reviewer good`."
# The three subagents as `lay.py write` writes them with the routes, writer's lanes beside.
LEAD_LAID = LEAD.replace("review them.\n", f"review them. {FOLLOW}\n")
WRITER_LAID = LAID.replace("you wrote.\n", f"you wrote. {END_WRITER}\n")
REVIEWER_LAID = REVIEWER.replace("you found.\n", f"you found. {END_REVIEWER}\n")


class PluginTest(testing.FolderTest):
    """A test with the README's plugin `changelog` in `base/changelog`, its subagent `writer` in
    `agents/writer.md`, the project it works on being `base`."""

    def setUp(self) -> None:
        super().setUp()
        # The calls kept go in the test's folder, as the system's temporary folder.
        patcher = mock.patch.object(tempfile, "tempdir", self.base)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.plugin = os.path.join(self.base, "changelog")
        self.write_json(self.manifest(), {"name": "changelog", "version": "0.1.0"})
        self.agent_file = os.path.join(self.plugin, "agents", "writer.md")
        self.write(self.agent_file, WRITER)

    def manifest(self) -> str:
        """The plugin's manifest."""
        return os.path.join(self.plugin, ".claude-plugin", "plugin.json")

    def route(self) -> None:
        """Lays docs/routes.md's routes beside the README's lanes, as `lay.py write` writes them:
        lead, writer and reviewer saying their sentences, and hooks/lanes.json."""
        self.lay(text=WRITER_LAID)
        self.write(os.path.join(self.plugin, "agents", "lead.md"), LEAD_LAID)
        self.write(os.path.join(self.plugin, "agents", "reviewer.md"), REVIEWER_LAID)
        laid = {**RULES, "routes": ROUTES}
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)

    def lay(self, laid_steps: list[dict[str, Any]] | None = None, text: str = LAID) -> None:
        """Lays the README's lanes in `writer`, or the steps given, as `lay.py write` writes
        them: its file saying their sentences, and hooks/lanes.json."""
        self.write(self.agent_file, text)
        given = STEPS if laid_steps is None else laid_steps
        laid = {"subagents": [{"name": "writer", "steps": given}]}
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)

    def event(
        self,
        tool: str,
        given: dict[str, Any],
        agent: str | None = AGENT,
        held: str = "PreToolUse",
        agent_id: str = "a1",
    ) -> dict:
        """An event of the name of a call of the tool with the input, PreToolUse by default, in
        the fields the hooks reference documents, made in `base` by the subagent of the type and
        ID, or by the main conversation where the type is None."""
        event = {
            **self.common(held),
            "tool_name": tool,
            "tool_input": given,
            "tool_use_id": "toolu_1",
        }
        return event if agent is None else {**event, "agent_id": agent_id, "agent_type": agent}

    def common(self, held: str) -> dict[str, Any]:
        """The fields every event of the name has, as the hooks reference documents them."""
        return {
            "session_id": "s1",
            "transcript_path": os.path.join(self.base, "s1.jsonl"),
            "cwd": self.base,
            "permission_mode": "bypassPermissions",
            "hook_event_name": held,
        }

    def bash(self, command: str, agent: str | None = AGENT, held: str = "PreToolUse") -> dict:
        """An event of a Bash call of the command, PreToolUse by default."""
        return self.event("Bash", {"command": command, "description": "d"}, agent, held)

    def came_back(self, command: str, agent: str = AGENT, agent_id: str = "a1") -> dict:
        """The PostToolUse event of a Bash call of the command that came back."""
        given = {"command": command, "description": "d"}
        back = {"stdout": "", "stderr": "", "interrupted": False}
        return {**self.event("Bash", given, agent, "PostToolUse", agent_id), "tool_response": back}

    def start(
        self, name: str, held: str = "PreToolUse", back: Any = None, background: bool = False
    ) -> dict:
        """An event of lead's Agent call starting the subagent of the name, PreToolUse by default;
        PostToolUse's with what the call gave back, where it is given."""
        given = {"description": "d", "prompt": "p", "subagent_type": f"changelog:{name}"}
        given = {**given, "run_in_background": background}
        event = self.event("Agent", given, "changelog:lead", held, "lead1")
        return event if back is None else {**event, "tool_response": back}

    def subagent(self, held: str, name: str, agent_id: str, active: bool = False) -> dict:
        """A SubagentStart or SubagentStop event of the subagent of the name and ID; SubagentStop's
        kept going by a stop hook already where active."""
        event = {**self.common(held), "agent_id": agent_id, "agent_type": f"changelog:{name}"}
        if held == "SubagentStop":
            transcript = os.path.join(self.base, "s1", "subagents", f"agent-{agent_id}.jsonl")
            stop = {"stop_hook_active": active, "agent_transcript_path": transcript}
            event = {**event, **stop, "last_assistant_message": "done"}
        return event

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


def back(agent_id: str, status: str = "completed") -> dict:
    """What an Agent call gives back of the subagent of the ID, as Claude Code 2.1.317 gave it,
    run in the foreground and ended, or launched in the background."""
    return {"status": status, "agentId": agent_id, "content": [{"type": "text", "text": "done"}]}
