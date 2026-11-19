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
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from claude_code import Agent, Answer, Conversation
from repo_files import environment, git, readme_block, write_files

TOP = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 3))
LANE = os.path.join(TOP, "plugins", "lane")
README = os.path.join(LANE, "README.md")
TEXT = "Carry out your steps"
RESULT = "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py"
# What coverage.py reads in a new process to measure it, and where it writes what it measured.


def plugin_file(name: str) -> str:
    """The file of the walkthrough's plugin at the path in changelog/, word for word as the README
    gives it."""
    with open(README, encoding="utf-8") as f:
        text = f.read()
    head = f"```markdown\n<!-- changelog/{name} -->\n"
    start = text.index(head) + len(head)
    return text[start : text.index("```", start)]


# The walkthrough's plugin, file by file.
WRITE = plugin_file("skills/write/SKILL.md")
WRITER = plugin_file("agents/writer.md")
REVIEWER = plugin_file("agents/reviewer.md")
FILES = {
    ".claude-plugin/plugin.json": json.dumps({"name": "changelog", "version": "0.1.0"}) + "\n",
    "skills/write/SKILL.md": WRITE,
    "agents/writer.md": WRITER,
    "agents/reviewer.md": REVIEWER,
}


# What Lane shows at each move of the walkthrough, as the README shows it.
SHOWN = readme_block(README, "You type:\n\n```text\n/lane:up changelog\n```\n\nLane shows:")
WROTE = readme_block(README, "```text\nyes\n```\n\nLane shows:")
ENDED_WITHOUT = readme_block(README, "tries to end without running its result script, Lane shows:")
README_ID = "6d9b4389"


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

    def step(self, role: str, step: int) -> str:
        """The command by which a role of changelog marks a Step done, as Lane lays it."""
        return f"python3 {self.changelog}/hooks/lane/step.py {role} {step}"

    def item(self, role: str, item: str) -> str:
        """The command by which a role of changelog marks an Item of its Step due done, as Lane
        lays it."""
        return f"python3 {self.changelog}/hooks/lane/item.py {role} {item}"

    def lay_py(self, *args: str) -> str:
        """The command that runs lay.py with the arguments."""
        return " ".join(["python3", os.path.join(self.lane, "scripts", "lay.py"), *args])


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
    write_files(
        repo,
        {"CHANGELOG.md": "# Changelog\n\n## 0.1.0\n\n- Counts lines.\n- Reads standard input.\n"},
    )
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
    env = environment(tmp)
    return Bench(lane, os.path.realpath(repo), os.path.realpath(changelog), temp, env)


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
    step 1, writer's Lanes on its steps 2, 3, and 4, and reviewer's on its steps 2 and 3."""
    return {
        "lanes": [
            lane("write", "skills/write/SKILL.md", 1, "routes"),
            lane("write", "skills/write/SKILL.md", 1, "ends_by_result"),
            lane("writer", "agents/writer.md", 2, "run_only", commands=["git log --oneline"]),
            lane("writer", "agents/writer.md", 3, "write_only", paths=["CHANGELOG.md"]),
            lane("writer", "agents/writer.md", 4, "ends_by_result"),
            lane("reviewer", "agents/reviewer.md", 2, "write_only", paths=["REVIEW.md"]),
            lane("reviewer", "agents/reviewer.md", 3, "ends_by_result"),
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
    AI's Skill call, as S1 draws, and gives what lay.py print gave, with the ID."""
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
    """The person lays the walkthrough's Proposal, as S1 and S2 draw: up proposes, the person
    replies yes, and lay.py write lays it."""
    c = converse(b)
    _, pid = propose(b, c, make=make)
    assert not c.type("yes").blocked
    written = c.bash(b.lay_py("write", "changelog", pid))
    assert written.exit_code == 0, written.output


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


# changelog with writer's Steps held as Lane's page of steps, routes, and adapters says: its step 1
# reads CHANGELOG.md whole, its step 2 never reads tally.py, its step 3 keeps the changelog's
# checklist, whose Items the adapter of a step's items gives, and its Steps are done in order.
MARKED_WRITER = (
    WRITER.replace(
        "1. Read `CHANGELOG.md` to learn its last version and its form, and `REVIEW.md`, where it"
        " exists, to learn what the entries lack.",
        "1. Read `CHANGELOG.md` whole, to learn its last version and its form.",
    )
    .replace(
        "2. Read the commits since then with `git log --oneline`.",
        "2. Read the commits since then with `git log --oneline`. Never read `tally.py`.",
    )
    .replace(
        "3. Write the new entries into `CHANGELOG.md`.",
        "3. Write the new entries into `CHANGELOG.md`, each item of the changelog's checklist"
        " kept.",
    )
)
ITEMS = "hooks/adapters/items.py"
# The adapter of a step's items: it gives writer's step 3 the Items `dated` and `linked`, and every
# other Step none, and adds what it was handed to items-handed.jsonl in the folder it runs in.
ITEMS_ADAPTER = """#!/usr/bin/env python3
import json, sys
handed = {"args": sys.argv[1:], "values": json.load(sys.stdin)["values"]}
with open("items-handed.jsonl", "a") as f:
    f.write(json.dumps(handed) + "\\n")
print(json.dumps({"items": ["dated", "linked"] if sys.argv[1:] == ["writer", "3"] else []}))
"""
FAILING_ITEMS = "#!/usr/bin/env python3\nimport sys\nsys.exit('CHECKLIST.md is not there')\n"


def marked_proposal() -> dict[str, Any]:
    """The walkthrough's Proposal, with writer's Lanes of reads_whole on its step 1, reads_none on
    its step 2, keeps_items on its step 3, and keeps_steps on its step 4, and the adapter of a
    step's items."""
    proposal = walkthrough_proposal()
    proposal["lanes"] += [
        lane("writer", "agents/writer.md", 1, "reads_whole", paths=["CHANGELOG.md"]),
        lane("writer", "agents/writer.md", 2, "reads_none", paths=["tally.py"]),
        lane("writer", "agents/writer.md", 3, "keeps_items"),
        lane("writer", "agents/writer.md", 4, "keeps_steps"),
    ]
    proposal["adapters"] = {"items": ITEMS}
    return proposal


def marked_bench(tmp: str, adapter: str = ITEMS_ADAPTER) -> Bench:
    """The bench, with writer's Steps of MARKED_WRITER and the adapter of a step's items."""
    files = dict(FILES, **{"agents/writer.md": MARKED_WRITER, ITEMS: adapter})
    b = bench(tmp, files)
    executable(os.path.join(b.changelog, ITEMS))
    return b


def marked_writer(b: Bench, make: Make = marked_proposal) -> tuple[Conversation, Agent]:
    """The marked Proposal laid, or the one `make` makes, and writer started by /changelog:write."""
    return writer_started(b, make=make)


def handed(b: Bench) -> list[dict[str, Any]]:
    """What the adapter of a step's items was handed, each time it ran, in the order it ran."""
    path = os.path.join(b.repo, "items-handed.jsonl")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]
