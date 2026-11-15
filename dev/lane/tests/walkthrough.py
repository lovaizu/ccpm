"""What Lane's integration cases share: the README's walkthrough as the cases play it on the double
of Claude Code. A bench holds a copy of Lane and the repository of `tally` with the plugin
`changelog` as the walkthrough gives its files, and each helper plays one move of the walkthrough
as the user, up, the main conversation, or a subagent makes it, through the double alone. What
Lane shows is taken word for word from the README, so that a case fails wherever Lane shows other
than its users read there."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from claude_code import Agent, Answer, Conversation

TOP = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 3))
LANE = os.path.join(TOP, "plugins", "lane")
README = os.path.join(LANE, "README.md")
TEXT = "Carry out your steps"
RESULT = "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py"

# The walkthrough's plugin, file by file, as the README gives it.
WRITE = """---
name: write
description: Has the CHANGELOG.md entries written and reviewed.
---

## Steps

1. Have the entries written and reviewed.
"""
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
REVIEWER = """---
name: reviewer
description: Reviews the CHANGELOG.md entries that writer wrote.
background: true
---

## Steps

1. Read the new entries in `CHANGELOG.md` against the commits they name.
2. Give `more` when an entry needs the writer again, and `good` when every entry is right.
"""
FILES = {
    ".claude-plugin/plugin.json": json.dumps({"name": "changelog", "version": "0.1.0"}) + "\n",
    "skills/write/SKILL.md": WRITE,
    "agents/writer.md": WRITER,
    "agents/reviewer.md": REVIEWER,
}


# The guard's form of an earlier Lane, as its copy in a plugin's hooks/lane/domain/ held it: its
# lanes.json keeps the Laid under `added`, and each sentence as [file, step, text], while the
# Laid it gives keeps the fields that every version keeps.
EARLIER_FORM = """from dataclasses import dataclass
import json


class OutOfForm(Exception):
    pass


@dataclass(frozen=True)
class LaidSentence:
    file: str
    step: int
    text: str


@dataclass(frozen=True)
class Laid:
    version: str
    sentences: tuple


@dataclass(frozen=True)
class LanesFile:
    laid: Laid


def read_lanes(path):
    with open(path, encoding="utf-8") as f:
        held = json.load(f)
    if "added" not in held:
        raise OutOfForm(["no added"])
    sentences = tuple(LaidSentence(*each) for each in held["added"]["sentences"])
    return LanesFile(Laid(held["added"]["version"], sentences))
"""


def readme_block(after: str) -> str:
    """The first `text` block of the README's walkthrough after the line that ends with `after`."""
    with open(README, encoding="utf-8") as f:
        text = f.read()
    start = text.index(after)
    found = re.search(r"```text\n(.*?)```", text[start:], re.DOTALL)
    assert found, f"the README holds no text block after {after!r}"
    return found[1].rstrip("\n")


# What Lane shows at each move of the walkthrough, as the README shows it.
SHOWN = readme_block("You type:\n\n```text\n/lane:up changelog\n```\n\nLane shows:")
WROTE = readme_block("```text\nyes\n```\n\nLane shows:")
README_ID = "b9fd8fd8"


def shown(proposal_id: str) -> str:
    """What lay.py print shows of the walkthrough's Proposal, with its ID."""
    return SHOWN.replace(f"ID: {README_ID}", f"ID: {proposal_id}")


@dataclass
class Bench:
    """The folders of one case: Lane's copy, the repository of tally with changelog in it, the
    double's own folder, and the environment that Claude Code runs with."""

    lane: str
    repo: str
    changelog: str
    temp: str
    env: dict[str, str]

    def result(self, role: str, result: str) -> str:
        """The command by which a role of changelog gives its Result, as Lane lays it."""
        return f"python3 {self.changelog}/hooks/lane/result.py {role} {result}"

    def up_result(self, result: str) -> str:
        """The command by which up gives its Result."""
        return f"python3 {self.lane}/hooks/lane/result.py up {result}"

    def lay_py(self, *args: str) -> str:
        """The command that runs lay.py with the arguments."""
        return " ".join(["python3", os.path.join(self.lane, "scripts", "lay.py"), *args])


def git(repo: str, *args: str) -> str:
    """Runs git in the repository, and gives what it printed."""
    done = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=True)
    return done.stdout


def bench(tmp: str, files: dict[str, str] | None = None) -> Bench:
    """A copy of Lane, and the repository of tally with changelog holding the files, the
    walkthrough's by default, committed after two commits of tally."""
    lane = os.path.join(tmp, "lane")
    shutil.copytree(LANE, lane)
    repo = os.path.join(tmp, "tally")
    os.makedirs(repo)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "tally@example.com")
    git(repo, "config", "user.name", "tally")
    write_files(repo, {"CHANGELOG.md": "# Changelog\n\n## 0.1.0\n\n- Counts lines.\n"})
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "Release 0.1.0")
    write_files(repo, {"tally.py": "print(sum(1 for _ in open(0)))\n"})
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "Count lines from standard input")
    changelog = os.path.join(repo, "changelog")
    write_files(changelog, FILES if files is None else files)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "Add the changelog plugin")
    temp = os.path.join(tmp, "claude")
    env = {
        "PATH": os.environ.get("PATH", os.defpath),
        "HOME": os.path.join(tmp, "home"),
        "TMPDIR": os.path.join(tmp, "system-temp"),
    }
    os.makedirs(env["TMPDIR"])
    return Bench(lane, os.path.realpath(repo), os.path.realpath(changelog), temp, env)


def write_files(folder: str, files: dict[str, str]) -> None:
    """Writes each file under the folder, by its path there."""
    for name, text in files.items():
        path = os.path.join(folder, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)


def executable(path: str) -> None:
    """Lets the file at the path run as a program."""
    os.chmod(path, 0o755)


def read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def converse(b: Bench, lane: bool = True) -> Conversation:
    """A new conversation in tally, run as `claude --plugin-dir changelog`, with Lane loaded where
    `lane` is true."""
    plugins = ([b.lane] if lane else []) + [b.changelog]
    return Conversation(b.repo, plugins, b.env, b.temp)


def types(b: Bench, c: Conversation) -> dict[str, Any]:
    """What lay.py types gives, as up runs it."""
    ran = c.bash(b.lay_py("types"))
    assert ran.exit_code == 0, ran.output
    return json.loads(ran.output)


def lane(role: str, file: str, step: int, kind: str, **args: Any) -> dict[str, Any]:
    """A Lane as up writes it, its values by the names that its type's `ARGS` gives."""
    return {"role": role, "file": file, "step": step, "type": kind, "args": args}


def walkthrough_proposal() -> dict[str, Any]:
    """The Proposal that the walkthrough's lay.py print shows: write's Routes and its end on its
    step 1, writer's Lanes on its steps 2, 3, and 4, and reviewer's end on its step 2."""
    return {
        "lanes": [
            lane("write", "skills/write/SKILL.md", 1, "routes"),
            lane("write", "skills/write/SKILL.md", 1, "ends_by_result"),
            lane("writer", "agents/writer.md", 2, "run_only", commands=["git log --oneline"]),
            lane("writer", "agents/writer.md", 3, "write_only", paths=["CHANGELOG.md"]),
            lane("writer", "agents/writer.md", 4, "ends_by_result"),
            lane("reviewer", "agents/reviewer.md", 2, "ends_by_result"),
        ],
        "routes": [
            {"skill": "write", "after": {"first": True}, "moves": [{"start": "writer"}]},
            {
                "skill": "write",
                "after": {"role": "writer", "result": "written"},
                "moves": [{"start": "reviewer"}],
            },
            {
                "skill": "write",
                "after": {"role": "reviewer", "result": "more"},
                "moves": [{"start": "writer"}],
            },
            {
                "skill": "write",
                "after": {"role": "reviewer", "result": "good"},
                "moves": [{"no_more": "good"}],
            },
        ],
        "adapters": {},
    }


def print_proposal(b: Bench, c: Conversation, proposal: dict[str, Any]) -> Answer:
    """up hands the Proposal to lay.py print on its standard input."""
    path = os.path.join(b.temp, "proposal.json")
    os.makedirs(b.temp, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(proposal, f)
    return c.bash(f"{b.lay_py('print', 'changelog')} < {path}")


def proposal_id(output: str) -> str:
    """The ID that lay.py print's output names."""
    found = re.search(r"^ID: (\S+)$", output, re.MULTILINE)
    assert found, f"lay.py print names no ID: {output!r}"
    return found[1]


Make = Callable[[], dict[str, Any]]


def propose(
    b: Bench, c: Conversation, by_ai: bool = False, make: Make | None = None
) -> tuple[Answer, str]:
    """up proposes the walkthrough's Proposal, called by the person's /lane:up changelog or by an
    AI's Skill call, as S1 and S3 draw, and gives what lay.py print gave, with the ID."""
    called = c.skill("lane:up", "changelog") if by_ai else c.type("/lane:up changelog")
    assert not called.blocked, called.said
    names = {each["name"] for each in types(b, c)["types"]}
    assert {"routes", "run_only", "write_only", "ends_by_result"} <= names, names
    steps = c.bash(b.lay_py("steps", "changelog"))
    assert steps.exit_code == 0, steps.output
    printed = print_proposal(b, c, (make or walkthrough_proposal)())
    assert printed.exit_code == 0, printed.output
    return printed, proposal_id(printed.output)


def lay(b: Bench, make: Make | None = None) -> None:
    """The person lays the walkthrough's Proposal, as S1 and S2 draw: up proposes, gives what
    lay.py print showed, the person replies yes, lay.py write lays it, up gives `laid`, and the
    person types /reload-plugins."""
    c = converse(b)
    printed, pid = propose(b, c, make=make)
    assert not c.stop(printed.output).blocked
    assert not c.type("yes").blocked
    written = c.bash(b.lay_py("write", "changelog", pid))
    assert written.exit_code == 0, written.output
    assert c.bash(b.up_result("laid")).exit_code == 0
    assert not c.stop(written.output).blocked


def laid(b: Bench, lane: bool = True, make: Make | None = None) -> Conversation:
    """A conversation in tally, after the person laid the walkthrough's Proposal, or the one that
    `make` makes, and typed /reload-plugins, with Lane loaded where `lane` is true."""
    lay(b, make)
    return converse(b, lane)


def start(c: Conversation, role: str) -> tuple[Answer, Agent | None]:
    """The main conversation starts the role of changelog with Lane's text, in the background."""
    return c.start(f"changelog:{role}", TEXT, role)


def give(b: Bench, agent: Agent, result: str) -> Answer:
    """The subagent gives its Result by result.py, and ends; gives what the main conversation reads
    as its end reaches it."""
    ran = agent.bash(b.result(agent.type.split(":")[-1], result))
    assert ran.exit_code == 0, ran.output
    ended, reached = agent.end(f"Gave {result}.")
    assert not ended.blocked, ended.said
    assert reached is not None
    return reached


def to_reviewer(b: Bench, c: Conversation) -> Agent:
    """The run of /changelog:write up to reviewer's start: writer started, gave `written`, and
    reviewer started, as the walkthrough's run goes."""
    assert not c.type("/changelog:write").blocked
    _, writer = start(c, "writer")
    assert writer
    give(b, writer, "written")
    _, reviewer = start(c, "reviewer")
    assert reviewer
    return reviewer


def writer_started(b: Bench, make: Make | None = None) -> tuple[Conversation, Agent]:
    """The walkthrough's Proposal laid, or the one `make` makes, and writer started by
    /changelog:write."""
    c = laid(b, make=make)
    assert not c.type("/changelog:write").blocked
    _, writer = start(c, "writer")
    assert writer
    return c, writer


def due(role: str) -> str:
    """The words by which Lane gives the start of the role due, as the README shows them."""
    return f"changelog: Start `changelog:{role}` with `{TEXT}`."


def in_temp(b: Bench, part: Callable[..., Any], *args: Any) -> Any:
    """What the part of Lane gives, run in this process with the system's temporary folder that
    the bench's conversations run with."""
    before = dict(os.environ)
    os.environ["TMPDIR"] = b.env["TMPDIR"]
    tempfile.tempdir = None
    try:
        return part(*args)
    finally:
        os.environ.clear()
        os.environ.update(before)
        tempfile.tempdir = None


def where(root: str, b: Bench, session_id: str) -> Any:
    """Where each Run of the conversation stands, as result.py reads it for the plugin of the
    folder."""
    from runs import where as stands

    return in_temp(b, stands, root, session_id)
