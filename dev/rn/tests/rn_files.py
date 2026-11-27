"""How rn's cases make the files that rn reads, each in the form that its use reads it: a best
practice as its best-practice.json holds it.

Each helper writes or gives what the documents name, and nothing of how rn's code reads it, so
that a case calls rn's parts only through their interfaces."""

from __future__ import annotations

import functools
import json
import os
import subprocess
from typing import Any

from place import WorkPlace
from repo_files import git, write_files

TOP = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 3))
RN = os.path.join(TOP, "plugins", "rn")
PRACTICES = os.path.join(RN, "domain", "best-practices")
SCHEMAS = os.path.join(RN, "domain", "schemas")

# The outcome and the needs of the README's walkthrough, in English.
OUTCOME = (
    "An accountant who sends invoices at the month's end prints one from a statement file,"
    " without a developer's help."
)
# The user's words that the outcome rests on, as the walkthrough has them.
WORDS = (
    "the user on 2026-11-26:"
    " 経理チームが、Pythonを書かずに、明細から請求書を印刷できるコマンドがほしい"
)
PRINT = "I print one invoice from a statement file."
RULES = "It meets the invoice rules."
SETTLES = "the least that prints one invoice"
COMMAND = "invoice/__main__.py"
GUIDE = "docs/guide.md"


# The walkthrough's walking skeleton as the orchestrator's aim gives it: the command, then the
# guide.
WAY = {
    "for": "O1",
    "settles": SETTLES,
    "deliverables": [{"path": COMMAND, "kind": "code"}, {"path": GUIDE, "kind": "readme"}],
}


def schema(name: str = "steering") -> dict[str, Any]:
    """rn's schema of the name, read from domain/schemas/."""
    with open(os.path.join(SCHEMAS, f"{name}.schema.json"), encoding="utf-8") as f:
        return json.load(f)


def opportunity(id_: str, words: str) -> dict[str, Any]:
    """An opportunity of the steering, named by the user on the walkthrough's day, with no
    solution."""
    return {"id": id_, "opportunity": words, "by": "the user on 2026-11-26", "solution": None}


def ost(target: str | None = "O1", questions: list[str] | None = None) -> dict[str, Any]:
    """The walkthrough's opportunity solution tree: printing an invoice, and meeting the rules,
    with its solution where it's the target."""
    picked = opportunity("O1", PRINT)
    if target == "O1":
        picked["solution"] = {
            "solution": "A command that reads a statement file and prints one invoice.",
            "why": "It's the least that prints.",
        }
    return {
        "outcome": OUTCOME,
        "words": [WORDS],
        "opportunities": [picked, opportunity("O2", RULES)],
        "target": target,
        "decisions": [{"decision": "Talk in Japanese, and write in English.", "by": "user"}],
        "questions": questions or [],
    }


def step(status: str = "open", done: tuple[str, ...] = ()) -> dict[str, Any]:
    """The walkthrough's walking skeleton: the command, then its guide, each done where named."""
    return {
        "for": "O1",
        "settles": SETTLES,
        "deliverables": [
            {"path": path, "kind": kind, "status": "done" if path in done else "open"}
            for path, kind in ((COMMAND, "code"), (GUIDE, "readme"))
        ],
        "status": status,
    }


def steering(steps: list[dict[str, Any]] | None = None, **fields: Any) -> dict[str, Any]:
    """A steering in its schema's form: the walkthrough's tree, with its fields as given, and the
    steps as given, or its walking skeleton, open."""
    return {
        "ost": ost(**fields),
        "state": {
            "issues": {"closes": [38], "refs": []},
            "steps": [step()] if steps is None else steps,
        },
    }


@functools.cache
def _practice(kind: str) -> str:
    with open(os.path.join(PRACTICES, kind, "best-practice.json"), encoding="utf-8") as f:
        return f.read()


def practice(kind: str) -> dict[str, Any]:
    """rn's best practice of the kind, read from the JSON of its best-practice.json."""
    return json.loads(_practice(kind))


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


def write_json(path: str, value: Any) -> None:
    """Writes the value as JSON at the path, its folder made."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(value, f, indent=1)
        f.write("\n")


# The user's repository.


def repository(folder: str, branch: str = "main") -> str:
    """Makes a git repository in the folder with a README committed on the branch, and gives its
    real path."""
    os.makedirs(folder, exist_ok=True)
    git(folder, "init", "-q", "-b", branch)
    git(folder, "config", "user.email", "rn@example.com")
    git(folder, "config", "user.name", "rn")
    write_files(folder, {"README.md": "# Accounting\n"})
    git(folder, "add", "-A")
    git(folder, "commit", "-q", "-m", "accounting")
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


def worktree_of(repo: str, folder: str, branch: str) -> str:
    """Adds a worktree of the repository in the folder, on a new branch from its head, and gives
    its real path."""
    git(repo, "worktree", "add", "-q", "-b", branch, folder)
    return os.path.realpath(folder)


def work_with_origin(folder: str, name: str) -> WorkPlace:
    """Makes the user's repository `accounting` in the folder, with a bare `origin.git` beside it
    as its remote, and the work of the name in a worktree `invoices` beside it on the branch
    `invoices`, its folder empty, and gives the work."""
    repo = repository(os.path.join(folder, "accounting"))
    with_origin(repo, os.path.join(folder, "origin.git"))
    held = WorkPlace(worktree_of(repo, os.path.join(folder, "invoices"), "invoices"), name)
    os.makedirs(held.folder)
    return held


def committed_steering(
    worktree: str, name: str, value: Any, when: str = "2026-11-26T09:00:00"
) -> None:
    """Writes the work's steering in its worktree, and commits it as made at the time given, as each
    piece of work's branch is ordered by their last commit's time."""
    write_json(os.path.join(worktree, ".rn", name, "steering.json"), value)
    git(worktree, "add", "-A")
    env = {**os.environ, "GIT_COMMITTER_DATE": when, "GIT_AUTHOR_DATE": when}
    subprocess.run(
        ["git", "-C", worktree, "commit", "-q", "-m", f"steering of {name}"], env=env, check=True
    )
