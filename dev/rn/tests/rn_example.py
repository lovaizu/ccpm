"""The example of rn's cases, the walkthrough of rn's README, which is rn's specification: the
repository of `invoicer` in a folder of the test's own, with a bare repository as its remote on
GitHub and the double of gh first on the PATH, rn installed as a copy of its folder, as Claude Code
copies a plugin it installs, and the request, the goal, the plan, the point, and the decisions
that the walkthrough shows, each in its words. The cases play the user, the orchestrator, and
each role by the calls they make on the double of Claude Code."""

from __future__ import annotations

import json
import os
import pathlib
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any

from claude_code import Agent, Answer, Conversation

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
RN = os.path.join(TOP, "plugins", "rn")
GH = os.path.join(HERE, "gh")
COMMITS = os.path.join(HERE, "e2e", "invoicer-commits.json")

# The walkthrough's words.
REQUEST = "type hints for invoicer, so that the people who call it see what each function takes"
WORDS = "type hints for invoicer"
GOAL = (
    "The people who call invoicer learn from their editor and their type checker what each"
    " function takes and returns, before their code runs."
)
HINTS = "invoicer/"
TYPED = "invoicer/py.typed"
HINTS_NAME = "Type hints in each file of invoicer, checked by mypy --strict"
TYPED_NAME = "invoicer marked as typed, so that the callers' type checkers read its hints"
POINT = "Should the hints cover each file, or only the functions that callers import?"
ANSWER = "each file"
DECIMAL = "Typed amounts and rates as Decimal, as the code already computes with Decimal."
# The point behind DECIMAL, as the hints' generator settles it without asking.
SETTLED = {
    "point": "How are amounts and rates typed?",
    "decided": DECIMAL,
    "ground": "invoicer/totals.py already computes with Decimal.",
}
CAN_DO = "a caller's type checker names a wrong argument before the code runs."
LESSON = (
    "code: a library's type hints need py.typed\n\nThe plan of type hints for a library left"
    " out py.typed until the user's goal named its callers' type checkers."
)
# The groups of the necessary conditions of rn's code best practice, one evaluator for each.
CODE_GROUPS = ("C1", "C2", "C3")
ROLES = ("tree-keeper", "generator", "evaluator")


def condition(id: str, *decisions: dict[str, Any], good: bool = False) -> dict[str, Any]:
    """A necessary condition of a deliverable, in the form of design-tree.schema.json."""
    return {"id": id, "good": good, "decisions": list(decisions)}


def decided(about: str, what: str | None, by: str = "reasoning") -> dict[str, Any]:
    """A decision, open where `what` is None, in the form of design-tree.schema.json."""
    return (
        {"about": about, "decided": what}
        if what is None
        else {"about": about, "decided": what, "by": by}
    )


def code_deliverable(
    name: str, path: str, *conditions: dict[str, Any], **fields: Any
) -> dict[str, Any]:
    """A deliverable of the kind `code`, open, with each necessary condition of rn's code best
    practice that isn't given, each with no decision yet."""
    given = {each["id"]: each for each in conditions}
    ids = [f"N{n}" for n in range(1, 9)]
    item = {
        "name": name,
        "path": path,
        "kind": "code",
        "inputs": [],
        "preconditions": [],
        "status": "open",
        "necessary_conditions": [given.get(id, condition(id)) for id in ids],
    }
    item.update(fields)
    return item


def plan(*hints_conditions: dict[str, Any]) -> dict[str, Any]:
    """The design tree of the walkthrough's goal and plan, the hints with the conditions given."""
    return {
        "goal": {"decided": GOAL, "by": "user"},
        "deliverables": [
            code_deliverable(HINTS_NAME, HINTS, *hints_conditions),
            code_deliverable(TYPED_NAME, TYPED, inputs=[HINTS], preconditions=[HINTS]),
        ],
    }


# The plan as the tree-keeper first writes it, with the walkthrough's point open, and once the user
# answered it.
WITH_POINT = plan(condition("N3", decided(POINT, None)))
ANSWERED = plan(condition("N3", decided(POINT, ANSWER, "user")))
# invoicer's totals.py with its type hints, as the hints' generator would make it.
TYPED_TOTALS = """\
\"\"\"The totals of an invoice.\"\"\"
from decimal import Decimal

from invoicer.lines import Line
from invoicer.tax import with_tax


def subtotal(lines: list[Line]) -> Decimal:
    return sum((line.value() for line in lines), Decimal("0"))


def total(lines: list[Line], rate: Decimal) -> Decimal:
    return with_tax(subtotal(lines), rate)
"""
# The tree once both deliverables meet each necessary condition, each done keeping only its name,
# path, kind, and status.
ALL_DONE = {
    "goal": ANSWERED["goal"],
    "deliverables": [
        {"name": HINTS_NAME, "path": HINTS, "kind": "code", "status": "done"},
        {"name": TYPED_NAME, "path": TYPED, "kind": "code", "status": "done"},
    ],
}


@dataclass(frozen=True)
class Repo:
    """The test's repository of invoicer, its bare remote, the folder of rn as installed, the
    test's temporary folder, and the file in which the double of gh keeps what GitHub holds."""

    root: str
    remote: str
    plugin: str
    temp: str
    github: str


@dataclass(frozen=True)
class Run:
    """A run that `tree.py begin` made: its worktree, whole, and its folder from there."""

    worktree: str
    folder: str


def git(root: str, *args: str) -> str:
    """What git printed, run in the folder with none of the machine's own settings, nor its
    maintenance in the background."""
    quiet = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
    who = {
        f"GIT_{part}_{field}": value
        for part in ("AUTHOR", "COMMITTER")
        for field, value in (("NAME", "u"), ("EMAIL", "u@example.com"))
    }
    ran = subprocess.run(
        ["git", "-c", "gc.auto=0", "-c", "maintenance.auto=false", *args],
        cwd=root,
        env={**os.environ, **quiet, **who},
        capture_output=True,
        text=True,
        check=True,
    )
    return ran.stdout


def write(root: str, path: str, text: str) -> str:
    """Writes the text to the file at the path in the folder, making its folders, and gives the
    file's whole path."""
    whole = pathlib.Path(root, path)
    whole.parent.mkdir(parents=True, exist_ok=True)
    whole.write_text(text, encoding="utf-8")
    return str(whole)


def text_of(path: str) -> str:
    """The text of the file at the path."""
    return pathlib.Path(path).read_text(encoding="utf-8")


def invoicer() -> dict[str, str]:
    """Each file of invoicer by its path, as its last commit of the E2E test leaves it."""
    with open(COMMITS, encoding="utf-8") as f:
        return {path: text for each in json.load(f) for path, text in each["files"].items()}


def make_repo(base: str, logged_in: bool = True) -> Repo:
    """The repository of invoicer, its commits as the E2E test makes them, pushed to a bare
    repository as `origin`, with rn installed beside it and gh logged in or not."""
    root, remote = os.path.join(base, "invoicer"), os.path.join(base, "origin.git")
    temp = os.path.join(base, "tmp")
    os.makedirs(temp)
    git(base, "init", "-q", "--bare", "-b", "main", remote)
    git(base, "init", "-q", "-b", "main", root)
    with open(COMMITS, encoding="utf-8") as f:
        for each in json.load(f):
            for path, text in each["files"].items():
                write(root, path, text)
            git(root, "add", "-A")
            git(root, "commit", "-q", "-m", each["message"])
    git(root, "remote", "add", "origin", remote)
    git(root, "push", "-q", "-u", "origin", "main")
    plugin = os.path.join(base, "installed", "rn")
    shutil.copytree(RN, plugin, symlinks=True, ignore=shutil.ignore_patterns("__pycache__"))
    github = write(
        base, "github.json", json.dumps({"logged_in": logged_in, "pulls": {}, "issues": []})
    )
    return Repo(root, remote, plugin, temp, github)


def environment(repo: Repo) -> dict[str, str]:
    """The environment of the test's Claude Code: the double of gh first on the PATH, its state the
    test's own, git with none of the machine's settings, and the test's temporary folder, as
    TMPDIR moves it."""
    return dict(
        os.environ,
        PATH=GH + os.pathsep + os.environ.get("PATH", os.defpath),
        RN_GH_STATE=repo.github,
        TMPDIR=repo.temp,
        GIT_CONFIG_GLOBAL=os.devnull,
        GIT_CONFIG_NOSYSTEM="1",
    )


def conversation(repo: Repo) -> Conversation:
    """A conversation of the double of Claude Code at the root of invoicer with rn loaded."""
    return Conversation(repo.root, [repo.plugin], environment(repo), repo.temp)


def github(repo: Repo) -> dict[str, Any]:
    """What GitHub holds for the test, as the double of gh keeps it."""
    return json.loads(text_of(repo.github))


def comment_on(repo: Repo, body: str, at: str) -> None:
    """The user comments on the run's pull request at the time, as GitHub keeps it."""
    held = github(repo)
    for pull in held["pulls"].values():
        pull["comments"].append({"body": body, "createdAt": at})
    write(os.path.dirname(repo.github), os.path.basename(repo.github), json.dumps(held))


def tree(repo: Repo, *args: str) -> str:
    """The command line of the installed tree.py with the arguments."""
    return shlex.join(["python3", os.path.join(repo.plugin, "scripts", "tree.py"), *args])


def record(repo: Repo, *args: str) -> str:
    """The command line of the installed record.py with the arguments."""
    return shlex.join(["python3", os.path.join(repo.plugin, "scripts", "record.py"), *args])


def throwaway(repo: Repo, *args: str) -> str:
    """The command line of the installed throwaway.py with the arguments."""
    return shlex.join(["python3", os.path.join(repo.plugin, "scripts", "throwaway.py"), *args])


def result(repo: Repo, role: str, given: str) -> str:
    """The command line of the result script that Lane laid in rn, by which the role gives the
    result."""
    return shlex.join(
        ["python3", os.path.join(repo.plugin, "hooks", "lane", "result.py"), role, given]
    )


def begin(conv: Conversation, repo: Repo) -> Run:
    """The user types the walkthrough's request, and the orchestrator has tree.py make the run's
    worktree, and enters it."""
    conv.type(f"/rn:up {REQUEST}")
    made = conv.bash(tree(repo, "begin", WORDS))
    assert made.exit_code == 0, f"tree.py begin gave {made.exit_code}: {made.output}"
    worktree = made.output.strip()
    entered = conv.enter_worktree(path=worktree)
    assert not entered.blocked, f"EnterWorktree was stopped: {entered.said}"
    return Run(worktree, os.path.join(".rn", os.path.basename(worktree).removeprefix("rn-")))


def values(printed: str) -> dict[str, str]:
    """The run values that `tree.py cut` printed, as one JSON line."""
    return json.loads(printed.strip().splitlines()[-1])


def cut(conv: Conversation, repo: Repo, run: Run, role: str, *more: str) -> dict[str, str]:
    """The orchestrator has tree.py write the role's cut, and gives its run values."""
    printed = conv.bash(tree(repo, "cut", run.folder, role, *more))
    assert printed.exit_code == 0, f"tree.py cut gave {printed.exit_code}: {printed.output}"
    return values(printed.output)


def start(conv: Conversation, role: str, given: dict[str, str]) -> tuple[Answer, Agent | None]:
    """The main conversation starts rn's role with the text of its run values, one JSON line, as
    the guard gives it."""
    return conv.start(f"rn:{role}", json.dumps(given), role)


def started(
    conv: Conversation, repo: Repo, run: Run, role: str, *more: str
) -> tuple[dict[str, str], Agent]:
    """The role's cut written and the role started with it, which must start."""
    given = cut(conv, repo, run, role, *more)
    answer, agent = start(conv, role, given)
    assert agent, f"{role} didn't start: {answer.said}"
    return given, agent


def keeper_writes(
    agent: Agent, repo: Repo, run: Run, design: dict[str, Any], ground: str
) -> Answer:
    """The tree-keeper writes the design tree to a file and has tree.py write it with the ground."""
    path = os.path.join(repo.temp, "design-tree.json")
    if os.path.exists(path):
        os.remove(path)
    agent.write(path, json.dumps(design))
    return agent.bash(tree(repo, "write", run.folder, path, ground))


def steps_of(repo: Repo, role: str) -> list[int]:
    """The number of each step of the role's part, as the installed rn's `domain/<role>.md` lists
    them under `## Steps`."""
    text = text_of(os.path.join(repo.plugin, "domain", f"{role}.md"))
    listed = text.split("## Steps", 1)[-1].split("\n## ", 1)[0]
    return [int(item.split(".", 1)[0]) for item in listed.split("\n") if item[:1].isdigit()]


def practices_of(repo: Repo, kind: str) -> list[str]:
    """The ID of each practice of rn's best practice of the kind, such as `N6.2`."""
    found = json.loads(
        text_of(os.path.join(repo.plugin, "domain", "best-practices", kind, "best-practice.json"))
    )
    return [
        f"{need['id']}.{n}"
        for factor in found["goal"]["critical_success_factors"]
        for need in factor["necessary_conditions"]
        for n in range(1, len(need["items"]) + 1)
    ]


def records_all(agent: Agent, repo: Repo, given: dict[str, str], role: str, *kinds: str) -> None:
    """The role records each step of its part, and each practice of each best practice it works
    by, such as code and refactor-code, each with what it gave, as rn's check reads a record that
    holds every item."""
    for step in steps_of(repo, role):
        agent.bash(record(repo, "add", given["record"], role, str(step), f"step {step} held"))
    for kind in kinds:
        for practice in practices_of(repo, kind):
            agent.bash(
                record(repo, "add", given["record"], kind, practice, f"{practice} carried out")
            )


def gives(
    agent: Agent, repo: Repo, role: str, given: str, reply: str = ""
) -> tuple[Answer, Answer | None]:
    """The role gives the result by Lane's result script and ends with the reply; gives what
    stopped its end, or what the main conversation reads beside it."""
    agent.bash(result(repo, role, given))
    return agent.end(reply or f"Gave {given}.")


def keeper_done_and_paused(conv: Conversation, repo: Repo, run: Run) -> dict[str, str]:
    """The tree-keeper's `done` accepted by rn's check and kept in its record, and the run paused;
    gives the tree-keeper's run values."""
    given, keeper = started(conv, repo, run, "tree-keeper")
    keeper_writes(keeper, repo, run, ANSWERED, "The user answered each file.")
    records_all(keeper, repo, given, "tree-keeper", "design-tree")
    gives(keeper, repo, "tree-keeper", "done")
    conv.bash(tree(repo, "pause", run.folder))
    return given
