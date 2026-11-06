"""What lane's tests stand on beside what every plugin's tests do: lane's code on sys.path, its
modules taken by each test from here, so they are found whichever test runs first; and the
README's plugin `changelog`, made in a test's folder, with its skill `write`, its subagent
`writer`, the routes of docs/routes.md with its `reviewer`, and the events Claude Code hands its
hooks as the hooks reference documents them and a trial on Claude Code 2.1.319 showed them; and,
for the architecture tests of a run, the plugin `changelog` kept with the trials, laid by `lay.py
write` in a project of its own, with the double of Claude Code."""

from __future__ import annotations

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Callable
from unittest import mock

LANE = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "plugins", "lane")
)
CODE = os.path.join(LANE, "hooks", "lane")
DOMAIN = os.path.join(CODE, "core", "domain")
SCRIPTS = os.path.join(LANE, "scripts")
sys.path[:0] = [CODE, DOMAIN, SCRIPTS, os.path.join(LANE, "..", "..", "dev", "lane")]

import called
import entries
import guard
import hook
import lanes
import lay  # noqa: F401
import layer  # noqa: F401
import placed  # noqa: F401
import ports
import proposal  # noqa: F401
import result
import routes  # noqa: F401
import rules  # noqa: F401
import schema
import step
import steps  # noqa: F401
import template  # noqa: F401
import testing
from lanes import (  # noqa: F401
    done,
    edit_only,
    end_when,
    every_item,
    follow_routes,
    forms,
    hold,
    in_form,
    read_only,
    read_whole,
    run_only,
    test_after,
    write_only,
)

AGENT = "changelog:writer"
# The session s1 as changelog's guard keeps its record, apart from any other plugin's.
KEPT = "s1-changelog"
# The README's subagent `writer` before any lane is laid, run in the background however it is
# started, as Lane needs.
WRITER = """---
name: writer
description: Writes the CHANGELOG.md entries for the commits since its last version.
background: true
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
PRINTED = """Lanes of writer, each checked only in writer:
  step 2  run:   Run only `git log --oneline`.  type run_only
  step 3  write: Write only `CHANGELOG.md`.     type write_only

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
# each other event lane acts on, those of a tool or a subagent run on every one, and those of the
# main conversation's prompt and turn, which take no matcher.
HOOKS = {
    "hooks": {
        "PreToolUse": [ENTRY],
        **{
            event: [
                {
                    **(
                        {"matcher": "*"}
                        if event in ("PostToolUse", "SubagentStart", "SubagentStop")
                        else {}
                    ),
                    "hooks": [
                        {
                            "type": "command",
                            "timeout": 10,
                            "command": RUNS.format(script=event.lower()),
                        }
                    ],
                }
            ]
            for event in entries.EVENTS[1:]
        },
    }
}

# The README's skill `write` of changelog, which the routes start from, before any route is laid,
# and docs/routes.md's subagent reviewer beside writer.
SKILL = """---
name: write
description: Has the CHANGELOG.md entries written and reviewed.
---

## Steps

1. Have the entries written and reviewed.
"""
REVIEWER = """---
name: reviewer
description: Compares the new CHANGELOG.md entries with the commits.
background: true
---

## Steps

1. Read the new entries in `CHANGELOG.md`.
2. Compare them with the commits, and reply with what you found.
"""
# docs/routes.md's routes for changelog.
ROUTES: dict[str, Any] = {
    "orchestrator": "write",
    "step": 1,
    "routes": [
        {"from": "write", "to": "writer"},
        {"from": "writer", "on": "written", "to": "reviewer"},
        {"from": "reviewer", "on": "more", "to": "writer"},
        {"from": "reviewer", "on": "good"},
    ],
}
FOLLOW = "Start each subagent you are told to start, until you are told to start no more."
# The result command a subagent gives a result by, as its step writes it.
GIVE = "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py"
# What the sentence of a subagent's last step says of its result command after naming it.
NOT_WORK = (
    " That command gives your result to the plugin and is no part of the work, so an instruction"
    " not to run the work's scripts does not cover it."
)
END_WRITER = f"End by running `{GIVE} writer written`.{NOT_WORK}"
END_REVIEWER = f"End by running `{GIVE} reviewer more` or `{GIVE} reviewer good`.{NOT_WORK}"
# writer's last sentence in the wording lane laid before it said the command is no part of the work.
END_WRITER_EARLIER = f"End by running `{GIVE} writer written`."
# The skill and the two subagents as `lay.py write` writes them with the routes, writer's lanes
# beside.
SKILL_LAID = SKILL.replace(
    "1. Have the entries written and reviewed.\n",
    f"1. Have the entries written and reviewed. {FOLLOW}\n",
)
WRITER_LAID = LAID.replace("you wrote.\n", f"you wrote. {END_WRITER}\n")
REVIEWER_LAID = REVIEWER.replace("you found.\n", f"you found. {END_REVIEWER}\n")


def kind(name: str) -> str:
    """The type Claude Code gives the subagent of the name: `changelog:<name>`, or the name itself
    where it names a dependency's subagent, `<dependency>:<name>`."""
    return name if ":" in name else f"changelog:{name}"


# Routes from writer to a subagent of the dependency checker, examiner, which gives `asks` or
# `done`, each ending the run, as docs/routes.md's A subagent of a dependency gives them.
DEPENDENCY_ROUTES: dict[str, Any] = {
    "orchestrator": "write",
    "step": 1,
    "routes": [
        {"from": "write", "to": "writer"},
        {"from": "writer", "on": "written", "to": "checker:examiner"},
        {"from": "checker:examiner", "on": "asks"},
        {"from": "checker:examiner", "on": "done"},
    ],
}
# The result command examiner gives a result by, as changelog's guard knows it.
EXAMINED = "python3 ${dependency:checker}/hooks/lane/result.py examiner"


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
        self.skill_file = os.path.join(self.plugin, "skills", "write", "SKILL.md")

    def manifest(self) -> str:
        """The plugin's manifest."""
        return os.path.join(self.plugin, ".claude-plugin", "plugin.json")

    def depend(self) -> None:
        """Lays routes to checker's examiner, changelog declaring checker, installed in `checker`
        beside it: the skill write and writer saying their sentences, and hooks/lanes.json."""
        self.lay(text=WRITER_LAID)
        self.write(self.skill_file, SKILL_LAID)
        manifest = {"name": "changelog", "version": "0.1.0", "dependencies": ["checker"]}
        self.write_json(self.manifest(), manifest)
        self.write_json(
            os.path.join(self.base, "checker", ".claude-plugin", "plugin.json"), {"name": "checker"}
        )
        laid = {**RULES, "routes": DEPENDENCY_ROUTES}
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)

    def route(self) -> None:
        """Lays docs/routes.md's routes beside the README's lanes, as `lay.py write` writes them:
        the skill write, writer and reviewer saying their sentences, and hooks/lanes.json."""
        self.lay(text=WRITER_LAID)
        self.write(self.skill_file, SKILL_LAID)
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

    def lay_lanes(
        self, laid_steps: list[Any], adapter: str | None = None, results: list[str] | None = None
    ) -> None:
        """Lays the lanes of the steps in `writer`, with its values adapter and the results it
        gives where they are given, as `lay.py write` writes them: each step saying its lanes'
        sentences, its last step its result command of each result, or `done` where a lane is
        checked at its end, and hooks/lanes.json."""
        lines: list[str] = [str(line) for line in WRITER.splitlines()]
        kinds = [str(g["lane"]) for s in laid_steps for g in s["lanes"]]
        ons = results or (["done"] if any(map(lanes.ends, kinds)) else [])
        commands = [f"{GIVE} writer {on}" for on in ons]
        ending: list[Any] = [{"step": 4, "lanes": [{"lane": "result", "takes": commands}]}]
        for s in [*laid_steps, *(ending if ons else [])]:
            where = step.span(lines, int(s["step"]))
            assert where is not None
            at = where[0]
            said = [lanes.sentence(str(g["lane"]), list(g["takes"])) for g in s["lanes"]]
            lines[at] = " ".join([lines[at], *said])
        self.write(self.agent_file, "\n".join(lines) + "\n")
        agent = {
            "name": "writer",
            **({"adapter": adapter} if adapter else {}),
            **({"results": results} if results else {}),
            "steps": laid_steps,
        }
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), {"subagents": [agent]})

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
        """An event of the main conversation's Agent call starting the subagent of the name,
        PreToolUse by default; PostToolUse's with what the call gave back, where it is given."""
        given = {"description": "d", "prompt": "p", "subagent_type": kind(name)}
        given = {**given, "run_in_background": background}
        event = self.event("Agent", given, None, held)
        return event if back is None else {**event, "tool_response": back}

    def skill_call(self, name: str, held: str = "PreToolUse") -> dict:
        """An event of the main conversation's Skill call of the skill of the name,
        `<plugin>:<name>`, PreToolUse by default; PostToolUse's with what it gave back, as Claude
        Code 2.1.319 gave it."""
        event = {**self.event("Skill", {"skill": name}, None, held), "tool_use_id": "toolu_s1"}
        back = {"success": True, "commandName": name}
        return event if held == "PreToolUse" else {**event, "tool_response": back}

    def expansion(self, name: str = "changelog:write") -> dict:
        """The main conversation's UserPromptExpansion of the command of the name typed, as Claude
        Code 2.1.319 gave it."""
        given = {"expansion_type": "slash_command", "command_name": name, "command_args": ""}
        return {**self.common("UserPromptExpansion"), **given, "prompt": f"/{name}"}

    def prompt(self, text: str = "Go on.") -> dict:
        """The main conversation's UserPromptSubmit of the text."""
        return {**self.common("UserPromptSubmit"), "prompt": text}

    def notified(self, agent_id: str) -> dict:
        """The main conversation's UserPromptSubmit of the task-notification of the end of the
        subagent of the ID, as Claude Code 2.1.319 gave it."""
        return self.prompt(notification(agent_id))

    def turn(self, active: bool = False) -> dict:
        """The main conversation's Stop, kept going by a stop hook already where active."""
        return {**self.common("Stop"), "stop_hook_active": active, "last_assistant_message": "m"}

    def subagent(self, held: str, name: str, agent_id: str, active: bool = False) -> dict:
        """A SubagentStart or SubagentStop event of the subagent of the name and ID; SubagentStop's
        kept going by a stop hook already where active."""
        event = {**self.common(held), "agent_id": agent_id, "agent_type": kind(name)}
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


# An entry of the subagent of the name whose steps lie in writer's part, as docs/lanes.md's A
# subagent's part gives it.
PART_ENTRY = (
    "---\nname: {name}\ndescription: d\nbackground: true\n---\n\n"
    "Your steps are in `${{CLAUDE_PLUGIN_ROOT}}/prompts/writer.md`.\n"
)
# An adapter of the values port reading `<name>=<value>` lines, with its cases, as the user
# keeps them beside its proposal.
VALUES_ADAPTER = """import json, sys

found = {}
for text in json.load(sys.stdin)["texts"]:
    for line in text.splitlines():
        key, eq, value = line.partition("=")
        if eq:
            found[key.strip()] = [value.strip()]
print(json.dumps({"values": found}))
"""
VALUES_CASES = [
    {"given": {"texts": ["work=a.md"]}, "gives": {"values": {"work": ["a.md"]}}},
    {"given": {"texts": ["nothing"]}, "gives": {"values": {}}},
]
# An adapter of the items port reading `Finding <n>` headings as the IDs F<n>, with its cases.
ITEMS_ADAPTER = """import json, re, sys

text = json.load(sys.stdin)["text"]
found = re.findall(r"^## Finding ([0-9]+)", text, re.MULTILINE)
print(json.dumps({"items": ["F" + n for n in found]}))
"""
ITEMS_CASES = [
    {"given": {"input": "r.md", "text": "## Finding 1\n"}, "gives": {"items": ["F1"]}},
    {"given": {"input": "r.md", "text": "none"}, "gives": {"items": []}},
]


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

    def adapter(self, name: str, text: str, cases: Any) -> str:
        """Keeps the adapter of the name, such as `values-w`, with its cases, beside the proposal,
        as docs/lanes.md says; gives its path in the plugin."""
        beside = os.path.join(os.path.dirname(PROPOSED), "changelog", "adapters")
        self.write(os.path.join(beside, f"{name}.py"), text)
        if cases is not None:
            text = cases if isinstance(cases, str) else json.dumps(cases)
            self.write(os.path.join(beside, f"{name}.json"), text)
        return f"hooks/adapters/{name}.py"


def did(
    base: str, plugin: str, calls: list | None = None, run: list | None = None, items=None
) -> Any:
    """What a subagent working in base did, as an end lane holds it: its calls kept, all and those
    of its run, the run's those of all where none are given, its items read by lane's reading or
    as given."""
    each = calls or []
    read = items or (lambda path, text: ports.read("items", {"input": path, "text": text})["items"])
    return done.Done(plugin, base, each, each if run is None else run, read)


def kept_call(tool: str, **given: Any) -> dict:
    """A call kept as it came back, of the tool with the input."""
    return called.call(tool, given)


def answer(text: str) -> dict:
    """The JSON a hook printed."""
    return json.loads(text) if text else {}


def back(agent_id: str, status: str = "completed") -> dict:
    """What an Agent call gives back of the subagent of the ID, as Claude Code 2.1.317 gave it,
    run in the foreground and ended, or launched in the background."""
    return {"status": status, "agentId": agent_id, "content": [{"type": "text", "text": "done"}]}


# The plugin the architecture tests and the trials lay their proposals on, its adapters, and the
# stand-in dependency `checker`, kept with the trials.
UX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ux")
# The project changelog works on: CHANGELOG.md at 0.1.0, and a commit after it.
CHANGELOG = (
    "# Changelog\n\n## Unreleased\n\n## 0.1.0\n\n- Added: notes are kept as Markdown files.\n"
)
# A stand-in for `claude`, whose `plugin validate` passes.
VALIDATES = "#!/bin/sh\necho '✔ Validation passed'\n"


def notification(agent_id: str) -> str:
    """The prompt of the task-notification of the end of the subagent of the ID, as Claude Code
    2.1.319 gave it in the main conversation."""
    return (
        f"<task-notification>\n<task-id>{agent_id}</task-id>\n<status>completed</status>\n"
        "<summary>Agent finished</summary>\n</task-notification>"
    )


def handed(event: dict[str, Any]) -> str:
    """What is wrong with the event as Claude Code hands it, by hook.py's own check of the fields
    the hooks reference documents, of a subagent or of the main conversation, and an Agent call's
    tool_response held to what the guard reads of it; "" where nothing is."""
    held = event["hook_event_name"]
    out = schema.held(hook.event_in(held, "agent_type" not in event), event)
    if out is not None:
        return out.told()
    if held == "PostToolUse" and event["tool_name"] == "Agent":
        out = schema.held(guard.BACK, event["tool_response"])
    return out.told() if out is not None else ""


class RunTest(testing.GitTest):
    """A test of a path through a run, in a git repository `repo` in `base`, with CHANGELOG.md and a
    commit after it, and a copy of the plugin `changelog` in `repo/changelog`, laid by `lay.py
    write` with a stand-in for `claude` on PATH; with a double of Claude Code working in `repo`,
    whose hooks keep the calls in `base` as the system's temporary folder."""

    def setUp(self) -> None:
        super().setUp()
        self.repo = self.copied("project", self.project)
        self.plugin = os.path.join(self.repo, "changelog")
        shutil.copytree(os.path.join(UX, "changelog"), self.plugin)
        claude = os.path.join(self.base, "bin", "claude")
        self.write(claude, VALIDATES)
        os.chmod(claude, 0o755)
        path = os.path.dirname(claude) + os.pathsep + os.environ["PATH"]
        self.env = {**os.environ, "PATH": path, "TMPDIR": self.base}
        self.claude = testing.ClaudeCode(self.plugin, self.repo, self.env, check=handed)

    def project(self) -> None:
        """Makes the project where the test stands: CHANGELOG.md committed, and a commit after."""
        self.git("init", "-q", "-b", "main")
        self.write("CHANGELOG.md", CHANGELOG)
        self.commit()
        self.write("note.md", "Add a search over the notes\n")
        self.commit()

    def lay(
        self, proposed: dict[str, Any], adapters: tuple[str, ...] = (), path: str = PROPOSED
    ) -> str:
        """Lays the proposal kept at the path with `lay.py write`, with the adapters of the names
        kept in ux/adapters/ beside it, as docs/lanes.md keeps them; fails the test where it does
        not exit 0, and gives what it printed."""
        beside = os.path.join(os.path.dirname(path), "changelog", "adapters")
        for name in adapters:
            for kind in (".py", ".json"):
                os.makedirs(beside, exist_ok=True)
                kept = os.path.join(UX, "adapters", name + kind)
                shutil.copyfile(kept, os.path.join(beside, name + kind))
        self.write_json(path, proposed)
        done = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "lay.py"), "write", path],
            capture_output=True,
            text=True,
            env=self.env,
            check=False,
        )
        assert done.returncode == 0, done.stdout
        return done.stdout

    def checker(self) -> str:
        """Installs the stand-in dependency checker in a folder of its own, lays it by its own
        proposal, examiner.json, has changelog declare it and the double of Claude Code run its
        hooks too; gives the folder it is installed in."""
        installed = os.path.join(self.base, "cache", "checker", "0.1.0")
        shutil.copytree(os.path.join(UX, "checker"), installed)
        given = self.ux_proposal("examiner.json")
        given["plugin"] = installed
        self.lay(given, path=os.path.join(".lane", "20261104-checker", "checker.json"))
        manifest = os.path.join(self.plugin, ".claude-plugin", "plugin.json")
        self.write_json(manifest, {**self.read_json(manifest), "dependencies": ["checker"]})
        self.claude.roots.append(installed)
        return installed

    def ux_proposal(self, name: str) -> dict[str, Any]:
        """The proposal of the name kept with the trials in ux/."""
        with open(os.path.join(UX, name), encoding="utf-8") as f:
            return json.load(f)

    def kept(self, run: testing.Run) -> list[dict[str, Any]]:
        """The entries the hooks kept of the run, in the session's folder of the calls kept."""
        found = []
        for path in glob.glob(
            os.path.join(self.base, "lane", "*-s1-changelog", f"{run.agent_id}.jsonl")
        ):
            with open(path, encoding="utf-8") as f:
                found += [json.loads(line) for line in f]
        return found


# The sentence of follow_routes as the main conversation is told it.
FOLLOWED = f"changelog: {FOLLOW}"


class RoutesTest(RunTest):
    """A test of a path through a run of the skill write: the routes laid, and `/changelog:write`
    typed in the main conversation, `told` what it was told as the run began."""

    def setUp(self) -> None:
        super().setUp()
        self.lay(self.proposed())
        self.told = self.claude.typed("changelog:write")

    def proposed(self) -> dict:
        """The proposal laid: routes.json, docs/routes.md's routes with writer's and reviewer's
        lanes."""
        return self.ux_proposal("routes.json")

    def gives(self, run: testing.Run, on: str) -> str:
        """The result command of the run's subagent on the result, as its step writes it, the
        plugin's folder put in."""
        name = run.kind.split(":")[1]
        return f"python3 {self.plugin}/hooks/lane/result.py {name} {on}"

    def result(self, run: testing.Run, on: str, refused: bool = False) -> testing.Told:
        """The run's call of its result command on the result, a result the result script's own
        check takes, or, where `refused`, one it refuses, so the double gives only what a subagent
        can give."""
        name = run.kind.split(":")[1]
        taken = result.said([name, on], self.plugin) == ""
        assert taken != refused, f"{name} would not give `{on}` as the test says"
        return self.claude.call(run, "Bash", {"command": self.gives(run, on), "description": "d"})

    def through(self, run: testing.Run, on: str) -> list[str]:
        """The main conversation starts the subagent's run, is told to wait and ends its turn; the
        run gives the result and ends; and its end reaches the main conversation: what the main
        conversation was told, in order."""
        started = self.claude.start(None, run, "Do your steps.")
        self.assertTrue(started.made, started.said)
        self.assertTrue(self.claude.end_turn().made)
        self.assertTrue(self.result(run, on).made)
        self.assertTrue(self.claude.stop(run).made)
        return started.context + self.claude.notify(run)

    def waits(self, name: str) -> str:
        """What the main conversation is told as its start of the subagent of the name comes
        back."""
        return (
            f"changelog: Wait for `changelog:{name}` to end: you are told the next start once it"
            " has."
        )


LAY = os.path.join(SCRIPTS, "lay.py")
with open(os.path.join(LANE, "README.md"), encoding="utf-8") as f:
    WALKTHROUGH = f.read().split("\n## Walkthrough")[1].split("\n## How it works")[0]
# The walkthrough's blocks, in order: the skill write, writer, the proposal, the two runs of
# lay.py, the command typed, and what the main conversation and writer are told on the run.
BLOCKS = re.findall(r"```[a-z]*\n(.*?)```", WALKTHROUGH, re.DOTALL)
README_SKILL, README_WRITER, README_PROPOSAL, README_PRINTED, README_WROTE = BLOCKS[:5]
README_TYPED, README_FIRST, README_STOPPED, README_WRITTEN, README_MORE, README_GOOD = BLOCKS[5:11]
# Where the walkthrough keeps its proposal, as its run of lay.py print names it.
README_PROPOSED = README_PRINTED.split("\n", 1)[0].split()[-1]
# The walkthrough's reviewer, which it says sets `background: true` and whose last step it quotes,
# its second, as `lay.py write` writes it, and its manifest, which the walkthrough does not show.
README_REVIEWER = (
    "---\nname: reviewer\ndescription: Compares the new CHANGELOG.md entries with the commits.\n"
    "background: true\n---\n\n## Steps\n\n"
    "1. Compare the new entries in `CHANGELOG.md` with the commits since its last version.\n"
    "2. Reply with each entry to write again. "
    + WALKTHROUGH.split("Its last\nstep says ``")[1].split("``")[0].replace("\n", " ")
    + "\n"
)
README_MANIFEST = json.dumps({"name": "changelog", "version": "0.1.0"})


def shown(block: str) -> str:
    """What the walkthrough shows a run printing, the line of the command left out."""
    return block.split("\n", 1)[1]


def as_shown(printed: str, block: str) -> bool:
    """Whether what a run printed reads as the walkthrough's block shows it, line by line, a line
    ending in ` ...` standing for any line it begins, and a line `...` for the rest."""
    lines, said = printed.splitlines(), block.splitlines()
    for at, line in enumerate(said):
        if line == "...":
            return True
        if at >= len(lines):
            return False
        if line.endswith(" ...") and lines[at].startswith(line[:-4]):
            continue
        if lines[at] != line:
            return False
    return len(lines) == len(said)


class WalkthroughTest(testing.GitTest):
    """A test of lay.py run as the user runs it, at the root of the git repository `base`, on the
    README's walkthrough: its plugin `changelog`, its skill `write`, its subagents `writer` and
    `reviewer` and its proposal, kept where the walkthrough keeps it, with a stand-in for Claude
    Code's `claude` on PATH."""

    def setUp(self) -> None:
        super().setUp()
        self.write(os.path.join("changelog", ".claude-plugin", "plugin.json"), README_MANIFEST)
        self.write(os.path.join("changelog", "skills", "write", "SKILL.md"), README_SKILL)
        self.write(os.path.join("changelog", "agents", "writer.md"), README_WRITER)
        self.write(os.path.join("changelog", "agents", "reviewer.md"), README_REVIEWER)
        self.write(README_PROPOSED, README_PROPOSAL)
        self.write(os.path.join("bin", "claude"), VALIDATES)
        os.chmod(os.path.join("bin", "claude"), 0o755)
        self.env = {
            **os.environ,
            "PATH": os.path.join(self.base, "bin") + os.pathsep + os.environ["PATH"],
        }

    def lay_py(self, action: str, path: str = README_PROPOSED) -> subprocess.CompletedProcess:
        """lay.py run with the action on the path at the root of the repository."""
        return subprocess.run(
            [sys.executable, LAY, action, path],
            capture_output=True,
            text=True,
            env=self.env,
            check=False,
        )

    def propose(self, change: Callable[[dict[str, Any]], None]) -> None:
        """Keeps the walkthrough's proposal changed by `change` where the walkthrough keeps it."""
        given = json.loads(README_PROPOSAL)
        change(given)
        self.write(README_PROPOSED, json.dumps(given))

    def adapter(self) -> str:
        """Keeps a values adapter, with its cases, beside the proposal, as docs/lanes.md says, the
        folder it lies in given back."""
        beside = os.path.join(os.path.dirname(README_PROPOSED), "changelog", "adapters")
        self.write(os.path.join(beside, "values-w.py"), VALUES_ADAPTER)
        self.write(os.path.join(beside, "values-w.json"), json.dumps(VALUES_CASES))
        return beside
