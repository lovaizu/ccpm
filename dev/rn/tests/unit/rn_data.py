"""What rn's unit cases share: a repository with rn's worktree of a run, made by git alone so that
no case of one module rests on another's body, the walkthrough's design tree in the design tree best
practice's form, and the double of gh on the PATH with what GitHub holds for it."""

from __future__ import annotations

import copy
import json
import os
import subprocess
from typing import Any, cast

from tree.design import DesignTree
from tree.runs import Run

TOP = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 4))
RN = os.path.join(TOP, "plugins", "rn")
GH = os.path.join(TOP, "dev", "rn", "tests", "gh")
TODAY = "20261115"
NAME = f"{TODAY}-type-hints-for-invoicer"
GOAL = (
    "The people who call invoicer learn from their editor and their type checker what each"
    " function takes and returns, before their code runs."
)


def git(folder: str, *args: str) -> str:
    """Runs git in the folder, and gives what it printed."""
    done = subprocess.run(["git", "-C", folder, *args], capture_output=True, text=True, check=True)
    return done.stdout


def repository(tmp: str) -> str:
    """A repository of invoicer with one commit, its folder."""
    repo = os.path.join(tmp, "invoicer")
    os.makedirs(os.path.join(repo, "invoicer"))
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "invoicer@example.com")
    git(repo, "config", "user.name", "invoicer")
    with open(os.path.join(repo, "invoicer", "__init__.py"), "w", encoding="utf-8") as f:
        f.write('"""invoicer."""\n')
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "invoicer 1.4.0")
    return os.path.realpath(repo)


def run_of(repo: str, name: str = NAME) -> Run:
    """rn's worktree of a run of the name in the repository, on its own branch, with the run's
    folder made in it, as runs.start would leave it."""
    worktree = os.path.join(repo, ".claude", "worktrees", f"rn-{name}")
    branch = f"rn-{name}"
    git(repo, "worktree", "add", "-q", "-b", branch, worktree)
    folder = os.path.join(worktree, ".rn", name)
    os.makedirs(os.path.join(folder, "records"))
    os.makedirs(os.path.join(folder, "rounds"))
    return Run(name, worktree, branch, folder)


def remote_for(repo: str, tmp: str) -> str:
    """A bare repository as the repository's remote origin, its folder."""
    origin = os.path.join(tmp, "origin.git")
    subprocess.run(["git", "init", "-q", "--bare", origin], check=True)
    git(repo, "remote", "add", "origin", origin)
    git(repo, "push", "-q", "origin", "main")
    return origin


def conditions(ids: int = 8) -> list[dict[str, Any]]:
    """Necessary conditions N1 to N<ids>, not yet good, with no decision."""
    return [{"id": f"N{n}", "good": False, "decisions": []} for n in range(1, ids + 1)]


def open_deliverable(name: str, path: str, status: str = "open", **fields: Any) -> dict[str, Any]:
    """A deliverable of code not yet done, with the fields given over its defaults."""
    each = {
        "name": name,
        "path": path,
        "kind": "code",
        "inputs": [],
        "preconditions": [],
        "status": status,
        "necessary_conditions": conditions(),
    }
    each.update(fields)
    return each


def walkthrough_tree() -> dict[str, Any]:
    """The walkthrough's design tree once the user answered their point: the goal by the user, and
    two deliverables of code, the first with the user's decision on which files under N1."""
    hints = open_deliverable("Type hints in each file of invoicer", "invoicer")
    hints["necessary_conditions"][0]["decisions"] = [
        {"about": "which files the hints cover", "decided": "each file", "by": "user"}
    ]
    typed = open_deliverable("invoicer marked as typed", "invoicer/py.typed")
    return {"goal": {"decided": GOAL, "by": "user"}, "deliverables": [hints, typed]}


def with_status(data: dict[str, Any], *statuses: str) -> dict[str, Any]:
    """A copy of the tree with each deliverable's status, in order."""
    changed = copy.deepcopy(data)
    for each, status in zip(changed["deliverables"], statuses):
        each["status"] = status
    return changed


def design(data: dict[str, Any] | None = None) -> DesignTree:
    """The design tree of the data, the walkthrough's by default."""
    return DesignTree(data if data is not None else walkthrough_tree())


def write_json(path: str, data: Any) -> str:
    """Writes the data as JSON at the path, its folder made, and gives the path."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return path


def read_json(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def tree_written(run: Run, data: dict[str, Any] | None = None) -> str:
    """The run's design-tree.json written with the data, the walkthrough's by default, and
    committed on the run's branch; gives its path."""
    path = write_json(os.path.join(run.folder, "design-tree.json"), data or walkthrough_tree())
    git(run.worktree, "add", "-A")
    git(run.worktree, "commit", "-q", "-m", "The design tree")
    return path


def github(tmp: str, logged_in: bool = True, pulls: dict[str, Any] | None = None) -> dict[str, str]:
    """The environment that puts the double of gh first on the PATH, with what GitHub holds for it
    in a file of its own: the login, each pull request by branch, and no issue."""
    path = write_json(
        os.path.join(tmp, "github.json"),
        {"logged_in": logged_in, "pulls": pulls or {}, "issues": []},
    )
    return {"PATH": os.pathsep.join([GH, os.environ.get("PATH", os.defpath)]), "RN_GH_STATE": path}


def answers(conditions_: list[str]) -> dict[str, Any]:
    """An evaluator's Answers with each condition good, on a line of the deliverable."""
    return {
        "good": [{"question": c, "lines": ["def total(lines, rate):"]} for c in conditions_],
        "more": [],
    }


def made() -> dict[str, Any]:
    """A generator's Made, carrying out the user's decision on which files, with a point settled."""
    return {
        "decisions": [
            {"path": "deliverables/0/necessary_conditions/0/decisions/0", "where": "invoicer"}
        ],
        "more": [],
        "settled": [
            {
                "point": "the type of amounts and rates",
                "decided": "Decimal",
                "ground": "the code already computes with Decimal",
            }
        ],
    }


def held(tree: DesignTree) -> Any:
    """The tree's data, as JSON that a case reads by its keys."""
    return cast(Any, tree.data)


def part(given: Any) -> Any:
    """A Cut's part, as JSON that a case reads by its keys."""
    return cast(Any, given.part)
