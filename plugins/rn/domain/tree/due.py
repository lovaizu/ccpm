"""Decides what is due now in a run, from its design tree and each deliverable's Rounds and Fixes,
as `rounds.course` says what each deliverable waits on: the hearing while the goal is open; the
plan's sign-off; each result that asks the pruner's judgment; each open decision that waits on
the user; each role due for a deliverable whose inputs are done, once the plan is, or at work
already; each deliverable to put up, and each put up for a step that the user checks; and the final
check once every deliverable is done. Each comes in that order of kinds, the deliverables in the
tree's order, so that whoever runs the run starts each thing due at once and in the same way each
time."""

from __future__ import annotations

import os
from typing import NamedTuple

from repository.place import RunPlace
from rounds import course, files

from tree import signoff
from tree.form import OPEN, Deliverable, Tree

# The kinds of what is due, in the order they come.
KINDS = (
    "hearing",
    "sign-off-plan",
    "pruner",
    "answer",
    "start",
    "running",
    "put-up",
    "sign-off",
    "final-check",
)
# The roles that a deliverable's Rounds and Fixes start.
ROLES = ("generator", "evaluator", "fixer")


class Due(NamedTuple):
    """One thing due: its kind, one of KINDS, and its words, such as a role and a deliverable's
    path for `start`."""

    kind: str
    words: tuple[str, ...] = ()


def due(run: RunPlace, tree: Tree) -> list[Due]:
    """Each thing due now in the run.

    Takes: the run, and its design tree as it stands, in its form.
    Gives, where the goal is open, `hearing` alone, as nothing is settled yet to weigh. Else, in
    the order of KINDS, the deliverables in the tree's order:
    - `sign-off-plan`, where `tree.signoff.waiting` names the plan, open with each condition good;
    - `pruner` with the deliverable's path and the absolute path of the result to weigh, where
      `rounds.course.next_in` gives the pruner: the last Round's `generator.json` of the stage
      `point`, its `evaluator.json` of the stage `judged` and of no stage, to keep each finding
      left past the limit as an open decision, and the last Fix's `fixer.json` of the stage `fix`;
    - `answer` with the deliverable's path, the condition's id, and the decision's about, for each
      decision that `rounds.course.asked` gives where the deliverable waits on the answer, and for
      each open decision of the plan;
    - `start` with the role and the deliverable's path, where a role of ROLES is due and its Cut
      is to write, once the plan is done and each input that names a deliverable names a done
      one: a generator in a new Round, or resuming the last one whose result is a weighed point
      or which holds no Cut; an evaluator whose Cut isn't written; a fixer that hasn't started;
    - `running` with the role and the deliverable's path, where its Cut is written and it wrote
      no result yet;
    - `put-up` with the deliverable's path, where it waits on the sign-off, and its last Round or
      Fix holds no mark of the state that `rounds.course.held` gives it now;
    - `sign-off` with the deliverable's path, where it waits on the sign-off, open, put up with that
      state, at a step that `tree.signoff.checked` gives that the user checks;
    - `final-check`, where none of the above is due and every deliverable is done.
    A done deliverable is due only where its last folder is a Fix: its fixer, the pruner of the
    stage `fix`, or its put-up, as a Fix mends a done deliverable that stays done.
    Changes: nothing.
    Refuses: Wrong as `rounds.course.next_in` refuses.
    """
    if tree["goal"]["decided"] is None:
        return [Due("hearing")]
    found: list[Due] = []
    if signoff.waiting(tree, {}) is not None:
        found.append(Due("sign-off-plan"))
    paths = {each["path"]: each for each in tree["deliverables"]}
    plan_done = all(
        each["status"] == "done" for each in tree["deliverables"] if each["kind"] == "design-tree"
    )
    for node in tree["deliverables"]:
        if node["kind"] == "design-tree":
            found += _answers(node, course.held(node)["open"])
            continue
        inputs_done = all(
            paths[each]["status"] == "done" for each in node.get("inputs", []) if each in paths
        )
        found += _of(run, tree, node, plan_done and inputs_done)
    found.sort(key=lambda each: KINDS.index(each.kind))
    if not found and all(each["status"] == "done" for each in tree["deliverables"]):
        return [Due("final-check")]
    return found


def _of(run: RunPlace, tree: Tree, node: Deliverable, may_start: bool) -> list[Due]:
    """What is due of a deliverable but the plan, where its inputs and the plan are done or
    not."""
    path = node["path"]
    rounds, mends = course.so_far(run, path), course.mended(run, path)
    fixed_last = bool(mends) and (not rounds or mends[-1].fix.number > rounds[-1].round.number)
    opened = node["status"] in OPEN
    if not opened and not fixed_last:
        return []
    next_ = course.next_in(run, node)
    if next_.waits_on == "pruner":
        return [Due("pruner", (path, _weighed(next_, rounds, mends)))]
    if next_.waits_on in ROLES and (opened or next_.waits_on == "fixer"):
        return _role(next_, path, rounds, mends, may_start)
    if next_.waits_on == "answer" and opened:
        return _answers(node, course.asked(node, rounds, mends))
    if next_.waits_on != "sign-off":
        return []
    last = mends[-1].fix if fixed_last else rounds[-1].round
    return _signed(tree, node, files.marked(last) == course.held(node))


def _signed(tree: Tree, node: Deliverable, put_up: bool) -> list[Due]:
    """What is due of a deliverable that waits on the sign-off, put up already or not: its put-up,
    or the user's sign-off where it's open at a step that they check."""
    if not put_up:
        return [Due("put-up", (node["path"],))]
    if node["status"] in OPEN and signoff.checked(tree, node["path"]):
        return [Due("sign-off", (node["path"],))]
    return []


def _weighed(next_: course.Next, rounds: list[course.Done], mends: list[course.Mend]) -> str:
    """The absolute path of the result that the pruner weighs."""
    if next_.stage == course.FIX:
        return os.path.abspath(mends[-1].fix.result)
    role = "generator" if next_.stage == course.POINT else "evaluator"
    return os.path.abspath(rounds[-1].round.result(role))


def _answers(node: Deliverable, decisions: list[dict[str, str]]) -> list[Due]:
    """An `answer` for each open decision of the deliverable given."""
    return [Due("answer", (node["path"], each["condition"], each["about"])) for each in decisions]


def _role(
    next_: course.Next,
    path: str,
    rounds: list[course.Done],
    mends: list[course.Mend],
    may_start: bool,
) -> list[Due]:
    """The role due, at work where its Cut is written with no result, else to start where it
    may."""
    role = next_.waits_on
    if role == "fixer":
        working = next_.resumes
    elif role == "evaluator":
        working = os.path.isfile(rounds[-1].round.cut(role))
    else:
        last = rounds[-1] if next_.resumes else None
        working = (
            last is not None and last.generator is None and os.path.isfile(last.round.cut(role))
        )
    if working:
        return [Due("running", (role, path))]
    return [Due("start", (role, path))] if may_start else []
