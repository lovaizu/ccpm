"""What rn's unit cases share: a repository with rn's worktree of a run, made by git alone so that
no case of one module rests on another's body, the walkthrough's design tree in the design tree best
practice's form, the double of gh on the PATH with what GitHub holds for it, and rn's adapters
as Lane runs them."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
from types import ModuleType
from typing import Any, cast

from tree.design import DesignTree
from tree.runs import Run

from dev.tests.repo_files import git

TOP = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 4))
RN = os.path.join(TOP, "plugins", "rn")
GH = os.path.join(TOP, "dev", "rn", "tests", "gh")
TODAY = "20261115"
NAME = f"{TODAY}-type-hints-for-invoicer"
GOAL = (
    "The people who call invoicer learn from their editor and their type checker what each"
    " function takes and returns, before their code runs."
)


def repository(tmp: str) -> str:
    """A repository of invoicer with one commit, holding CODE_INPUTS, its folder."""
    repo = os.path.join(tmp, "invoicer")
    os.makedirs(os.path.join(repo, "invoicer"))
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "invoicer@example.com")
    git(repo, "config", "user.name", "invoicer")
    with open(os.path.join(repo, "invoicer", "__init__.py"), "w", encoding="utf-8") as f:
        f.write('"""invoicer."""\n')
    os.makedirs(os.path.join(repo, "docs"))
    for each in CODE_INPUTS:
        with open(os.path.join(repo, each), "w", encoding="utf-8") as f:
            f.write(f"# invoicer's {os.path.basename(each)}\n")
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


# Files outside the tree, one for each kind that the code best practice takes, as the
# architecture, the software design, and the test design that a deliverable of code rests on.
CODE_INPUTS = ["docs/architecture.md", "docs/software-design.md", "docs/test-design.md"]


def open_deliverable(name: str, path: str, status: str = "open", **fields: Any) -> dict[str, Any]:
    """A deliverable of code not yet done, resting on CODE_INPUTS, with the fields given over its
    defaults."""
    each = {
        "name": name,
        "path": path,
        "kind": "code",
        "inputs": list(CODE_INPUTS),
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
    work = [{"do": "make", "path": "invoicer"}, {"do": "make", "path": "invoicer/py.typed"}]
    return {"goal": {"decided": GOAL, "by": "user"}, "deliverables": [hints, typed], "work": work}


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


def adapter(name: str) -> ModuleType:
    """rn's adapter of the name, from hooks/adapters/, as Lane runs it."""
    path = os.path.join(RN, "hooks", "adapters", f"{name}.py")
    spec = importlib.util.spec_from_file_location(f"rn_adapter_{name}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
