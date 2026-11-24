"""Decides what each role's Cut holds of the design tree and the Rounds, so that each role starts
with only what its work needs: the generator the language it writes in, its deliverable's
decisions, the user's answers and the pruner's remedies among them, and its own last good, but no
evaluator's findings, as it mends by its Cut's decisions alone; and the evaluator only what the
deliverable's people have. A Cut waits while the tree's goal is open, as each Cut holds it."""

from __future__ import annotations

import os
from typing import Any

from fault import Wrong
from practice import Found, judged
from repository import trial
from repository.place import RunPlace
from rounds.files import Result, Round

from tree.form import OPEN, Deliverable, Tree, goal

# A role's Cut, in the form of domain/schemas/<role>-cut.schema.json.
Cut = dict[str, Any]


def generator(
    tree: Tree,
    run: RunPlace,
    round_: Round,
    practice: Found,
    last: Result | None,
) -> Cut:
    """The generator's Cut for the Round.

    Takes: the tree, the run, the Round to make, a new one or the last one resumed, the best
    practice it makes by with its folder, its kind's for content and the refactoring kind's for
    refactor, and the deliverable's last generator's result, None before the first.
    Gives: the Cut of `generator-cut.schema.json`: the goal; the language of the deliverables, as
    the tree's context holds it; the deliverable's node, with each
    decision and the user's answers as its decisions; the run's worktree; the path of each
    deliverable its inputs name; the best practice's folder; the Round's stage, number, and folder;
    the folder of the people's starting state as `repository.trial.folder` names it; and the last
    generator's `good`. It holds no evaluator's findings, as the pruner writes the remedy that it
    keeps of each into the node's decisions.
    Changes: nothing.
    Refuses: Wrong where the tree's goal is open, or the tree holds no open deliverable of the
    Round's path.
    """
    node = _open(tree, round_)
    return {
        "goal": goal(tree),
        "language": tree["context"]["languages"]["deliverables"],
        "deliverable": node,
        "worktree": _from(run, run.worktree),
        "inputs": [_from(run, os.path.join(run.worktree, each)) for each in node["inputs"]],
        "best_practice": _from(run, practice.folder),
        "stage": round_.stage,
        "number": round_.number,
        "round": _from(run, round_.folder),
        "trial": trial.folder(run, round_),
        "last_good": None if last is None else last.get("good"),
    }


def evaluator(tree: Tree, run: RunPlace, round_: Round, practice: Found) -> Cut:
    """The evaluator's Cut for the Round.

    Takes: the tree, the run, the Round of content to judge, and the best practice of the
    deliverable's kind with its folder.
    Gives: the Cut of `evaluator-cut.schema.json`: the goal, the deliverable's name and paths, what
    it judges by as `practice.judged` gives it, the run's worktree, the folder of the people's
    starting state as `repository.trial.folder` names it, and the Round's folder; none of the
    deliverable's decisions or of what the generator wrote.
    Changes: nothing.
    Refuses: Wrong where the tree's goal is open, or the tree holds no open deliverable of the
    Round's path.
    """
    node = _open(tree, round_)
    return {
        "goal": goal(tree),
        "deliverable": {key: node[key] for key in ("name", "path", "more_paths") if key in node},
        "judges_by": judged(practice.practice),
        "worktree": _from(run, run.worktree),
        "trial": trial.folder(run, round_),
        "round": _from(run, round_.folder),
    }


def _open(tree: Tree, round_: Round) -> Deliverable:
    """The open deliverable of the Round's path."""
    for each in tree["deliverables"]:
        if each["path"] == round_.deliverable and each["status"] in OPEN:
            return each
    raise Wrong(f"{round_.deliverable}: no open deliverable of the design tree has the path")


def _from(run: RunPlace, path: str) -> str:
    """The path from the folder that the conversation works in, the top of the repository."""
    return os.path.relpath(path, run.repository)
