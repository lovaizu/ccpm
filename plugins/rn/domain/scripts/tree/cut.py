"""Decides what each role's Cut holds of the design tree and the Rounds, so that each role starts
with only what its work needs: the generator the language it writes in, its deliverable's
decisions, the user's answers and the pruner's remedies among them, and its own last good, but no
evaluator's findings, as it mends by its Cut's decisions alone; the evaluator only what the
deliverable's people have; and the fixer its deliverable's decisions and files, and the problem in
its own words, with nothing that would pull it past them. A Cut waits while the tree's goal is
open, as the generator's and the evaluator's hold it."""

from __future__ import annotations

import os
from typing import Any

from fault import Wrong
from practice import Found, judged, refactoring
from repository import trial
from repository.place import RunPlace
from rounds import files
from rounds.files import Fix, Result, Round
from template.check import TEMPLATE

from tree.form import Deliverable, Tree, deliverable, goal

# A role's Cut, in the form of domain/schemas/<role>-cut.schema.json.
Cut = dict[str, Any]


def generator(
    tree: Tree,
    run: RunPlace,
    round_: Round,
    kinds: dict[str, str],
    last: Result | None,
) -> Cut:
    """The generator's Cut for the Round.

    Takes: the tree, the run, the Round to make, a new one or the last one resumed, the folder of
    each kind's best practice, as `practice.kinds` gives them, and the deliverable's last
    generator's result, None before the first.
    Gives: the Cut of `generator-cut.schema.json`: the goal; the language of the deliverables, as
    the tree's context holds it; the deliverable's node, with each
    decision and the user's answers as its decisions; the run's worktree; the path of each
    deliverable its inputs name; the folder of the best practice it makes by, its kind's for
    content and the refactoring kind's, as `practice.refactoring` names it, for refactor; the
    `template.md` of its kind's best practice, whatever the stage, or None where the folder holds
    none; the Round's stage, number, and folder; the folder of the people's starting state as
    `repository.trial.folder` names it; and the last generator's `good`. It holds no evaluator's
    findings, as the pruner writes the remedy that it keeps of each into the node's decisions.
    Changes: nothing.
    Refuses: Wrong where the tree's goal is open, or the tree holds no open deliverable of the
    Round's path.
    """
    node = _open(tree, round_)
    kind = node["kind"]
    made_by = kind if round_.stage == "content" else str(refactoring(kind))
    template = os.path.join(kinds[kind], TEMPLATE)
    return {
        "goal": goal(tree),
        "language": tree["context"]["languages"]["deliverables"],
        "deliverable": node,
        "worktree": _from(run, run.worktree),
        "inputs": [_from(run, os.path.join(run.worktree, each)) for each in node["inputs"]],
        "best_practice": _from(run, kinds[made_by]),
        "template": _from(run, template) if os.path.isfile(template) else None,
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


def fixer(tree: Tree, run: RunPlace, fix: Fix) -> Cut:
    """The fixer's Cut for the Fix.

    Takes: the tree, the run, and the Fix to mend, its problem written.
    Gives: the Cut of `fixer-cut.schema.json`: the deliverable's node as the tree holds it, open
    or done, with its necessary conditions and their decisions; the run's worktree; the path of
    each file or folder of the deliverable in it, its path then each of its more paths; the Fix's
    problem; the run's folder; and the Fix's folder, where the fixer writes its result; each path
    from the folder that the conversation works in. It holds no goal, best practice, or Round,
    as the fixer mends within the decisions alone.
    Changes: nothing.
    Refuses: Wrong where the tree holds no deliverable of the Fix's path, or the Fix holds no
    problem.
    """
    node = deliverable(tree, fix.deliverable)
    problem = files.problem_of(fix)
    if problem is None:
        raise Wrong(f"{fix.folder}: holds no problem; write the Fix by tree fix")
    paths = [node["path"], *node.get("more_paths", [])]
    return {
        "deliverable": node,
        "worktree": _from(run, run.worktree),
        "paths": [_from(run, os.path.join(run.worktree, each)) for each in paths],
        "problem": problem,
        "run": _from(run, run.folder),
        "fix": _from(run, fix.folder),
    }


def _open(tree: Tree, round_: Round) -> Deliverable:
    """The open deliverable of the Round's path."""
    for each in tree["deliverables"]:
        if each["path"] == round_.deliverable and each["status"] == "open":
            return each
    raise Wrong(f"{round_.deliverable}: no open deliverable of the design tree has the path")


def _from(run: RunPlace, path: str) -> str:
    """The path from the folder that the conversation works in, the top of the repository."""
    return os.path.relpath(path, run.repository)
