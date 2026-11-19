"""What Lane's cases share: a plugin `log` that depends on Lane, whose skill `/log:up <version>`
has a writer write the version's CHANGELOG.md entry and a reviewer judge it, as Lane's README's
walkthrough says, with its rules, which fix its order by routes, and its skills; the adapters that a
case gives `log` in place of its routes or of a role's steps; and a bench that holds copies of Lane
and of that plugin, a repository it works in, and the double of Claude Code to play the person, the
main conversation, and each subagent through.

Each helper plays one move as the architecture draws it, through the double, and says nothing of
how Lane's parts carry it."""

from __future__ import annotations

import copy
import json
import os
import shutil
from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import pytest
from claude_code import Agent, Answer, Conversation
from repo_files import environment, git, write_files

if TYPE_CHECKING:
    from rules import Rules

TOP = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 3))
LANE = os.path.join(TOP, "plugins", "lane")

# Why each integration case fails for now: Lane's parts have no bodies, and the double of Claude
# Code lacks what dev/lane/skeleton-gaps.md names, for a case that reaches the plugin's folder, and
# for one that runs a reporter by its name too.
UNBUILT = pytest.mark.xfail(
    strict=True,
    reason="Lane's parts have no bodies yet, and the double of Claude Code writes no transcript"
    " that holds the skill's base directory",
)
UNREPORTED = pytest.mark.xfail(
    strict=True,
    reason="Lane's parts have no bodies yet, and the double of Claude Code writes no transcript"
    " that holds the skill's base directory, nor puts each plugin's bin/ on the Bash path",
)

# The words the person types after the command, the version whose entry the run writes.
WORDS = "1.2.0"
ENTRY = "# Changelog\n\n## 1.2.0\n\n- Invoices print from the command line.\n"
# The notes the writer reads whole, of 5 lines, which Read counts as 6, the empty line after the
# last newline among them.
NOTES = "Invoices print.\nFrom the command line.\nWith the rate.\nIn euros.\nOn A4.\n"
# The output of the plugin's check where CHANGELOG.md holds no entry of the version.
CHECK_SAYS = "CHANGELOG.md holds no entry of 1.2.0"

# The rules of `log`: the main conversation's steps by the skill's name, each subagent's by its
# agent type, and the routes, which start the writer after the command, the reviewer after the
# writer's result, the writer again after the reviewer's `more`, two writers after its `split`, and
# none after its `good`; `/log:retry` starts the writer in place of what was due, and `/log:tag`,
# whose skill holds the main conversation to steps of its own, starts the tagger in place of what
# was due, whose `tagged` ends the run.
RULES: Rules = {
    "roles": {
        "log:up": {
            "steps": [
                {
                    "name": "lead",
                    "rules": [
                        {"type": "writes", "paths": [".log/up.md"]},
                        {"type": "commands", "commands": ["git status"]},
                    ],
                }
            ]
        },
        "log:tag": {
            "steps": [{"name": "lead", "rules": [{"type": "writes", "paths": [".log/tags.md"]}]}]
        },
        "log:writer": {
            "steps": [
                {
                    "name": "write",
                    "rules": [
                        {"type": "order"},
                        {"type": "writes", "paths": ["CHANGELOG.md", "docs/changes/"]},
                        {"type": "reads_none", "paths": ["secrets/", ".env"]},
                        {"type": "commands", "commands": ["git log"]},
                        {"type": "reads_whole", "paths": ["NOTES.md"]},
                        {"type": "checklist", "items": ["dated", "linked"]},
                    ],
                },
                {
                    "name": "report",
                    "rules": [
                        {"type": "order"},
                        {"type": "reads_whole", "paths": ["CHANGELOG.md"]},
                        {"type": "result", "results": ["written"]},
                        {
                            "type": "check",
                            "check": f"grep -q '## 1.2.0' CHANGELOG.md || {{ echo '{CHECK_SAYS}';"
                            " exit 1; }",
                        },
                    ],
                },
            ]
        },
        "log:reviewer": {
            "steps": [
                {
                    "name": "review",
                    "rules": [{"type": "result", "results": ["good", "more", "split"]}],
                }
            ]
        },
        "log:tagger": {
            "steps": [{"name": "tag", "rules": [{"type": "result", "results": ["tagged"]}]}]
        },
    },
    "routes": [
        {"after": {"command": "log:up"}, "start": ["log:writer"]},
        {"after": {"role": "log:writer", "result": "written"}, "start": ["log:reviewer"]},
        {"after": {"role": "log:reviewer", "result": "more"}, "start": ["log:writer"]},
        {
            "after": {"role": "log:reviewer", "result": "split"},
            "start": ["log:writer", "log:writer"],
        },
        {"after": {"role": "log:reviewer", "result": "good"}, "start": []},
        {"after": {"command": "log:retry"}, "start": ["log:writer"]},
        {"after": {"command": "log:tag"}, "start": ["log:tagger"]},
        {"after": {"role": "log:tagger", "result": "tagged"}, "start": []},
    ],
}

# `log` fixes each step's rules and gives routes, so it gives no adapter: Lane's route adapter gives
# its starts due.
ADAPTERS: dict[str, str] = {}
SKILLS = ("up", "retry", "tag")

# An adapter of the starts due that `log` gives in place of its routes, which finds where the run
# stands from the plugin's own file, CHANGELOG.md, and from the run that Lane gives it: the reviewer
# due where the entry of the words is there and no result after it asks for more, else the writer;
# none while a start runs; and the run's end after the reviewer's `good`.
ORDER = """\
import json, sys

run = json.load(sys.stdin)["run"]
starts = [m for m in run["moves"] if m["kind"] == "start"]
results = [m["result"] for m in run["moves"] if m["kind"] == "result"]
try:
    with open("CHANGELOG.md", encoding="utf-8") as f:
        written = "## " + run["words"] in f.read()
except OSError:
    written = False
if results[-1:] == ["good"]:
    print(json.dumps({"ends": True}))
elif len(starts) > len(results):
    print(json.dumps({"starts": []}))
elif written and results[-1:] != ["more"]:
    print(json.dumps({"starts": [{"role": "log:reviewer", "count": 1}]}))
else:
    print(json.dumps({"starts": [{"role": "log:writer", "count": 1}]}))
"""

# An adapter of the rules that `log` gives for a role that its rules name with no steps: one step
# `write`, which writes each Markdown file that the start's prompt names.
RULES_ADAPTER = """\
import json, re, sys

prompt = json.load(sys.stdin)["prompt"]
paths = re.findall(r"[\\w./-]+\\.md", prompt)
print(json.dumps({"steps": [{"name": "write", "rules": [{"type": "writes", "paths": paths}]}]}))
"""

# The rules of `log` naming its writer with no steps, for its adapter of the rules to give.
ADAPTED: Rules = copy.deepcopy(RULES)
ADAPTED["roles"]["log:writer"] = {}


def prompt(role: str, words: str = WORDS) -> str:
    """The prompt that the main conversation gives the role's start, as log's skill words it."""
    return f"You are {role}. Write the entry of {words}."


def plugin(
    folder: str,
    name: str,
    skills: tuple[str, ...],
    rules: Mapping[str, Any] | None,
    adapters: Mapping[str, str],
) -> str:
    """Writes a plugin of the name in the folder: its manifest, naming Lane among its dependencies,
    a SKILL.md for each skill, its lane/rules.json where rules are given, and each adapter; gives
    the folder."""
    manifest = {"name": name, "version": "0.1.0", "dependencies": [{"name": "lane"}]}
    files = {".claude-plugin/plugin.json": json.dumps(manifest)}
    for skill in skills:
        files[f"skills/{skill}/SKILL.md"] = (
            f"---\nname: {skill}\ndescription: The {skill} of {name}.\n---\n"
            "Start each subagent that Lane gives as due.\n"
        )
    if rules is not None:
        files["lane/rules.json"] = json.dumps(rules, indent=2)
    files.update({f"lane/adapters/{each}": code for each, code in adapters.items()})
    write_files(folder, files)
    return folder


def denier(folder: str) -> str:
    """Writes a plugin `deny` in the folder whose PreToolUse hook denies each Agent call, as another
    plugin may, and gives the folder."""
    plugin(folder, "deny", (), None, {})
    entry = {"type": "command", "command": "python3", "args": ["${CLAUDE_PLUGIN_ROOT}/deny.py"]}
    hooks = {"hooks": {"PreToolUse": [{"matcher": "Agent", "hooks": [entry]}]}}
    denied = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "another plugin denies it",
        }
    }
    write_files(
        folder,
        {
            "hooks/hooks.json": json.dumps(hooks),
            "deny.py": f"import json\n\nprint(json.dumps({denied!r}))\n",
        },
    )
    return folder


@dataclass(frozen=True)
class Bench:
    """Copies of Lane and of `log`, the repository the conversation works in, the double's own
    folder, and the environment of each command."""

    lane: str
    log: str
    repo: str
    temp: str
    env: dict[str, str]

    def converse(self, *more: str) -> Conversation:
        """A new conversation in the repository, with `log`, each plugin given, and Lane loaded."""
        return Conversation(self.repo, [self.log, *more, self.lane], self.env, self.temp)

    def at(self, path: str) -> str:
        """The path in the repository."""
        return os.path.join(self.repo, path)

    def rules(self, rules: Any) -> None:
        """Writes the rules of `log`, as its author changes them."""
        write_files(self.log, {"lane/rules.json": json.dumps(rules, indent=2)})

    def adapter(self, name: str, code: str | None) -> None:
        """Writes the adapter of `log` with the code, or removes it where the code is None."""
        path = os.path.join(self.log, "lane", "adapters", name)
        if code is None:
            os.remove(path)
        else:
            write_files(self.log, {f"lane/adapters/{name}": code})

    def other(self, name: str, rules: Mapping[str, Any] | None) -> str:
        """Writes another plugin of the name beside `log`, with its skill `up` and the rules, and
        gives its folder."""
        return plugin(os.path.join(os.path.dirname(self.log), name), name, ("up",), rules, {})


def ending(b: Bench, step: int, result: str) -> None:
    """Writes the rules of `log` with the writer's step at the index naming the result among those
    that end the start at that step, which no route goes after."""
    rules = copy.deepcopy(RULES)
    rules["roles"]["log:writer"]["steps"][step]["rules"].append(
        {"type": "result", "ends": [result]}
    )
    b.rules(rules)


def steps_from_adapter(b: Bench) -> None:
    """Writes the rules of `log` naming its writer with no steps, so that each start of it takes its
    steps from RULES_ADAPTER, the plugin's adapter of the rules."""
    b.rules(ADAPTED)
    b.adapter("rules.py", RULES_ADAPTER)


def bench(tmp: str) -> Bench:
    """Copies of Lane and of `log`, and a repository with its notes, a secret, and a README,
    committed."""
    lane = os.path.join(tmp, "plugins", "lane")
    shutil.copytree(LANE, lane, ignore=shutil.ignore_patterns("__pycache__"))
    log = plugin(os.path.join(tmp, "plugins", "log"), "log", SKILLS, RULES, ADAPTERS)
    repo = os.path.join(tmp, "repo")
    os.makedirs(repo)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "log@example.com")
    git(repo, "config", "user.name", "log")
    write_files(
        repo,
        {"NOTES.md": NOTES, "README.md": "# repo\n", "secrets/key.txt": "k\n", ".env": "K=k\n"},
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "The notes")
    return Bench(lane, log, os.path.realpath(repo), os.path.join(tmp, "claude"), environment(tmp))


# The moves of a run, as the person, the main conversation, and each subagent make them.


def opened(b: Bench, words: str = WORDS) -> Conversation:
    """A conversation in which the person typed `/log:up` with the words."""
    c = b.converse()
    c.type(f"/log:up {words}")
    return c


def started(
    c: Conversation, role: str = "log:writer", words: str = WORDS, given: str | None = None
) -> Agent:
    """The main conversation starts the role in the background with the prompt given, else the one
    that log's skill words, and gives the subagent; the start must go through."""
    answer, agent = c.start(role, given or prompt(role, words), f"Run {role}")
    assert agent is not None, answer.said
    return agent


def items(agent: Agent) -> None:
    """The writer reports each item of its step `write` done."""
    for item in ("dated", "linked"):
        agent.bash(f"lane-item write {item}")


def written(
    agent: Agent, result: str | None = "written", entry: str = ENTRY, report: bool = True
) -> None:
    """The writer keeps each step: it writes the entry, reads its notes whole, reports each item and
    the step `write` done, reads the entry whole, reports the result where one is given, and
    reports the step `report` done where `report` says so."""
    c = agent.conversation
    agent.write(os.path.join(c.cwd, "CHANGELOG.md"), entry)
    agent.read(os.path.join(c.cwd, "NOTES.md"))
    items(agent)
    agent.bash("lane-step write")
    agent.read(os.path.join(c.cwd, "CHANGELOG.md"))
    if result:
        agent.bash(f"lane-result {result}")
    if report:
        agent.bash("lane-step report")


def reached(agent: Agent, reply: str = "Done.") -> Answer:
    """The subagent ends with the reply, its end must go through, and gives what the main
    conversation reads as its end reaches it."""
    stopped, notified = agent.end(reply)
    assert not stopped.blocked and notified is not None, stopped.said
    return notified


def reviewed(c: Conversation, result: str) -> Answer:
    """The reviewer due starts, reports its result, and ends; gives what the main conversation
    reads as its end reaches it."""
    reviewer = started(c, "log:reviewer")
    reviewer.bash(f"lane-result {result}")
    return reached(reviewer)


def to_review(b: Bench) -> Conversation:
    """A conversation whose writer kept each step and ended, so that the reviewer is due."""
    c = opened(b)
    writer = started(c)
    written(writer)
    reached(writer)
    return c
