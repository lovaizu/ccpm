"""How rn's cases make the files that rn reads, each in the form that its use reads it: a best
practice as its best-practice.json holds it, a design tree of design-tree.schema.json, a run's
folder at the place that the architecture's Directory structure names, a Round's folder with its
Cuts and results, and a git repository with a commit, as the user's repository is.

Each helper writes or gives what the documents name, and nothing of how rn's code reads it, so
that a case calls rn's parts only through their interfaces."""

from __future__ import annotations

import copy
import functools
import json
import os
import shutil
from collections.abc import Iterable, Mapping, Sequence
from typing import Any
from urllib.parse import quote

from repo_files import git, write_files

TOP = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 3))
RN = os.path.join(TOP, "plugins", "rn")
PRACTICES = os.path.join(RN, "domain", "best-practices")
SCHEMAS = os.path.join(RN, "domain", "schemas")
TREE_SCHEMA = os.path.join(PRACTICES, "design-tree", "design-tree.schema.json")
INVOICER = os.path.join(TOP, "dev", "rn", "tests", "invoicer")

# The walkthrough of rn's README: the user's words in reply to /rn:on, the goal as the orchestrator
# puts it with what its people do then, and the two deliverables of the plan, the command and its
# guide, the guide resting on the command.
WORDS = (
    "a command with which the accounting team prints an invoice from its lines, without writing"
    " Python"
)
GOAL = (
    "The accounting team prints each invoice themselves from the lines they keep in a"
    " spreadsheet, without asking a developer. A colleague from accounting prints an invoice from"
    " the guide alone."
)
# The run's name's goal part, as place.named gives it from WORDS: at most five of its words, lower
# case, joined by `-`.
NAMED = "a-command-with-which-the"
COMMAND = "invoicer/__main__.py"
COMMAND_NAME = "A command that prints an invoice from a file of its lines"
GUIDE = "docs/guide.md"
GUIDE_NAME = "A guide from which the accounting team prints an invoice on its own"
# The point that the walkthrough puts to the user, and their answer.
TAX_POINT = "Should the tax rate be given with each invoice, or set once?"
TAX_ABOUT = "the tax rate"
TAX_ANSWER = "with each invoice"


@functools.cache
def _practice(kind: str) -> str:
    with open(os.path.join(PRACTICES, kind, "best-practice.json"), encoding="utf-8") as f:
        return f.read()


def practice(kind: str) -> dict[str, Any]:
    """rn's best practice of the kind, read from the JSON of its best-practice.json."""
    return json.loads(_practice(kind))


def conditions(kind: str) -> list[str]:
    """The ID of each necessary condition of rn's best practice of the kind, in its order."""
    return [
        each["id"]
        for factor in practice(kind)["goal"]["critical_success_factors"]
        for each in factor["necessary_conditions"]
    ]


def items_at(kind: str, at: str) -> list[str]:
    """The ID of each item of rn's best practice of the kind that a maker takes at the stage, its
    condition's ID and its place among the condition's items from 1, such as `N1.2`, in the best
    practice's order, as practice.items' contract names them."""
    found = []
    for factor in practice(kind)["goal"]["critical_success_factors"]:
        for each in factor["necessary_conditions"]:
            for place, item in enumerate(each["items"], 1):
                if item["at"] == at:
                    found.append(f"{each['id']}.{place}")
    return found


def judged_by(kind: str) -> dict[str, Any]:
    """What an evaluator judges by, of rn's best practice of the kind, as practice.judged's
    contract names it: the goal's `what` and its factors, each condition with its id, about, and
    what alone."""
    goal = practice(kind)["goal"]
    return {
        "what": goal["what"],
        "critical_success_factors": [
            {
                "id": factor["id"],
                "what": factor["what"],
                "necessary_conditions": [
                    {"id": each["id"], "about": each["about"], "what": each["what"]}
                    for each in factor["necessary_conditions"]
                ],
            }
            for factor in goal["critical_success_factors"]
        ],
    }


def condition(
    id: str, good: bool = False, decisions: Sequence[Mapping[str, Any]] = ()
) -> dict[str, Any]:
    """A necessary condition of a deliverable, with whether it's good and its decisions."""
    return {"id": id, "good": good, "decisions": [dict(each) for each in decisions]}


def decision(about: str, decided: str | None, by: str | None = "maker") -> dict[str, Any]:
    """A decision: settled where `decided` is a string, by `by`, or open where it's None."""
    if decided is None:
        return {"about": about, "decided": None}
    return {"about": about, "decided": decided, "by": by}


def open_node(
    name: str,
    path: str,
    kind: str,
    inputs: Sequence[str] = (),
    good: bool | Iterable[str] = False,
) -> dict[str, Any]:
    """An open deliverable of the kind, with each necessary condition of its best practice in
    order, good where `good` is True or names it, each with no decision."""
    held = set(conditions(kind)) if good is True else set(good or ())
    return {
        "name": name,
        "path": path,
        "kind": kind,
        "inputs": list(inputs),
        "status": "open",
        "necessary_conditions": [condition(each, each in held) for each in conditions(kind)],
    }


def decided(
    node: Mapping[str, Any], decisions: Mapping[str, Sequence[Mapping[str, Any]]]
) -> dict[str, Any]:
    """A copy of the deliverable with each decision given added to its condition, by its ID."""
    given = copy.deepcopy(dict(node))
    for each in given["necessary_conditions"]:
        each["decisions"] += [dict(d) for d in decisions.get(each["id"], ())]
    return given


def done_node(name: str, path: str, kind: str) -> dict[str, Any]:
    """A deliverable that's done, in its one line."""
    return {"name": name, "path": path, "kind": kind, "status": "done"}


def work(do: str, path: str, condition_id: str | None = None, about: str | None = None) -> dict:
    """An item of the work."""
    item: dict[str, Any] = {"do": do, "path": path}
    if condition_id:
        item["condition"] = condition_id
    if about:
        item["about"] = about
    return item


def tree(
    deliverables: Sequence[Mapping[str, Any]],
    order: Sequence[Mapping[str, Any]] = (),
    goal: str = GOAL,
    by: str = "user",
) -> dict[str, Any]:
    """A design tree with the goal, the deliverables, and the work."""
    return {
        "goal": {"decided": goal, "by": by},
        "deliverables": [copy.deepcopy(dict(each)) for each in deliverables],
        "work": [dict(each) for each in order],
    }


def plan_path(name: str) -> str:
    """The plan's path from the run's worktree, the tree's own."""
    return f".rn/{name}/design-tree.json"


def plan(name: str, good: bool | Iterable[str] = True, goal: str = GOAL) -> dict[str, Any]:
    """The plan, the tree's own deliverable of the kind `design-tree`, named by the goal."""
    return open_node(goal, plan_path(name), "design-tree", good=good)


def walkthrough_tree(
    name: str,
    plan_done: bool = True,
    command_good: bool | Iterable[str] = False,
    guide_good: bool | Iterable[str] = False,
    command_decisions: Mapping[str, Sequence[Mapping[str, Any]]] | None = None,
) -> dict[str, Any]:
    """The design tree of the walkthrough's run: the plan, done or open with each condition good,
    the command, of the kind `light`, resting on invoicer's lines, and the guide, of the kind
    `readme`, resting on the command; the work makes the command, then the guide."""
    head = done_node(GOAL, plan_path(name), "design-tree") if plan_done else plan(name, good=True)
    return tree(
        [
            head,
            decided(
                open_node(COMMAND_NAME, COMMAND, "light", ["invoicer/lines.py"], command_good),
                command_decisions or {},
            ),
            open_node(GUIDE_NAME, GUIDE, "readme", [COMMAND], guide_good),
        ],
        [work("make", COMMAND), work("make", GUIDE)],
    )


# Where a run lies, as the architecture's Directory structure and repository.place's contract
# name each path.


def worktree_of(repository: str, name: str) -> str:
    """The run's worktree, `<repository>/.claude/worktrees/rn-<name>`."""
    return os.path.join(repository, ".claude", "worktrees", f"rn-{name}")


def folder_of(repository: str, name: str) -> str:
    """The run's folder, `<worktree>/.rn/<name>`."""
    return os.path.join(worktree_of(repository, name), ".rn", name)


def round_of(run_folder: str, deliverable: str, stage: str, number: int) -> str:
    """A Round's folder, `<run's folder>/rounds/<deliverable, percent-encoded whole>/<stage>-<n>`,
    as rounds.files names it."""
    return os.path.join(run_folder, "rounds", quote(deliverable, safe=""), f"{stage}-{number}")


def write_json(path: str, value: Any) -> None:
    """Writes the value as JSON at the path, its folder made."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(value, f, indent=1)
        f.write("\n")


def read_json(path: str) -> Any:
    """The JSON of the file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def run_folder(repository: str, name: str, design_tree: Mapping[str, Any]) -> str:
    """Writes the run's design tree in its folder, under its worktree, as files alone, with no git,
    and gives the run's folder."""
    folder = folder_of(repository, name)
    write_json(os.path.join(folder, "design-tree.json"), design_tree)
    return folder


def a_round(
    run: str, deliverable: str, stage: str, number: int, results: Mapping[str, Any] | None = None
) -> str:
    """Writes a Round's folder with each role's result given, by `generator` and `evaluator`, and
    gives the folder."""
    folder = round_of(run, deliverable, stage, number)
    os.makedirs(folder, exist_ok=True)
    for role, result in (results or {}).items():
        write_json(os.path.join(folder, f"{role}.json"), result)
    return folder


def made(good: Sequence[tuple[str, Sequence[str]]] = (), files: Sequence[str] = ()) -> dict:
    """A generator's result `made`, with the files it wrote and each condition it saw good."""
    return {
        "result": "made",
        "files": list(files),
        "good": [{"condition": c, "lines": list(lines)} for c, lines in good],
    }


def point(words: str = TAX_POINT) -> dict[str, Any]:
    """A generator's result `point`, with the point."""
    return {"result": "point", "point": words}


def judged(
    good: Sequence[tuple[str, Sequence[str]]] = (), more: Sequence[tuple[str, str]] = ()
) -> dict[str, Any]:
    """An evaluator's result `judged`, with each condition good and each with more."""
    return {
        "result": "judged",
        "good": [{"condition": c, "lines": list(lines)} for c, lines in good],
        "more": [{"condition": c, "good_when": when} for c, when in more],
    }


# The user's repository.


def repository(folder: str, files: Mapping[str, str] | None = None, branch: str = "main") -> str:
    """Makes a git repository in the folder with invoicer's files, or the files given, committed on
    the branch, and gives its real path."""
    os.makedirs(folder, exist_ok=True)
    git(folder, "init", "-q", "-b", branch)
    git(folder, "config", "user.email", "rn@example.com")
    git(folder, "config", "user.name", "rn")
    if files is None:
        shutil.copytree(INVOICER, folder, dirs_exist_ok=True)
    else:
        write_files(folder, files)
    git(folder, "add", "-A")
    git(folder, "commit", "-q", "-m", "invoicer")
    return os.path.realpath(folder)


def with_origin(repo: str, origin: str) -> str:
    """Gives the repository a bare repository as its remote `origin`, holding its branch, and gives
    the remote's path."""
    os.makedirs(origin)
    git(origin, "init", "-q", "--bare")
    git(repo, "remote", "add", "origin", origin)
    branch = git(repo, "branch", "--show-current").strip()
    git(repo, "push", "-q", "-u", "origin", branch)
    git(repo, "remote", "set-head", "origin", branch)
    return origin
