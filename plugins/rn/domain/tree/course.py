"""Decides the course of a deliverable's rounds: rounds of content by its kind's best practice, then
rounds of structure by the refactor one, two of each at most since its latest sign-off, and which
groups of necessary conditions each round judges, as a later round judges again only what changed
and another round on the same decisions ends the same way."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from tree import design, practices, rounds, sign_offs
from tree.design import DesignTree
from tree.runs import Run

# The most rounds of content, and of structure, since a deliverable's latest sign-off.
_MOST = 2


@dataclass(frozen=True)
class Round:
    """A round's course: its number, whether it's of structure, and the number of each group it
    judges, as `practices.judged_by` numbers the groups of the kind's best practice and then of the
    refactor one."""

    number: int
    structure: bool
    groups: tuple[int, ...]


def rounds_of(run: Run, plugin_root: str, tree: DesignTree, deliverable: str) -> tuple[Round, ...]:
    """The course of each round of the deliverable since its latest sign-off.

    Takes: the run, rn's folder, the tree, and the deliverable's path.
    Gives: each round after the round that the deliverable's latest sign-off kept, the latest
    last: of structure once the round before is, once two rounds of content ran, or once the
    round before was of content and the next round's cut holds the same decisions under the
    deliverable as its own; each judging every group of its best practice where it's its kind's
    first, and else each group that holds a condition whose decisions changed since the round
    before, or, of structure, a condition of a More kept in the round before, every group where
    none does.
    Changes: nothing.
    Refuses: fault.Wrong, as `practices.judged_by` does.
    Carries: S1 `par one for each group of the best practice that the round judges by`.
    """
    groups = practices.judged_by(run, plugin_root, design.deliverable(tree, deliverable)["kind"])
    content = tuple(n for n, g in enumerate(groups) if not g.kind.startswith("refactor-"))
    structure = tuple(n for n in range(len(groups)) if n not in content)
    found: list[Round] = []
    for number in range(_since(run, deliverable) + 1, rounds.latest(run, deliverable) + 1):
        cut = _decisions(rounds.at_cut(run, deliverable, number), deliverable)
        before = found[-1] if found else None
        is_structure = before is not None and (
            before.structure
            or sum(not r.structure for r in found) >= _MOST
            or cut == _decisions(rounds.at_cut(run, deliverable, before.number), deliverable)
        )
        own = structure if is_structure else content
        if before is None or before.structure != is_structure:
            judged = own
        elif is_structure:
            named = {m.condition for m in rounds.kept_more(run, deliverable, number - 1)}
            judged = _holding(groups, own, named)
        else:
            was = _decisions(rounds.at_cut(run, deliverable, before.number), deliverable)
            judged = _holding(groups, own, {c for c in cut if cut[c] != was.get(c)})
        found.append(Round(number, is_structure, judged))
    return tuple(found)


def next_round(run: Run, plugin_root: str, tree: DesignTree, deliverable: str) -> Round | None:
    """The round that the deliverable's generator takes next.

    Takes: the run, rn's folder, the tree, and the deliverable's path.
    Gives: the latest round since the deliverable's latest sign-off where it holds no Made yet; a
    first round of content where none is; and, once each group that the latest round judges has
    its Answers, a round after it: of content where a decision under the deliverable changed since
    its cut and fewer than two rounds of content ran, and of structure where the latest was of
    content and two ran or no decision changed, or it was of structure, fewer than two of
    structure ran, and a decision changed; None where none of these holds, as the deliverable is
    then ready to put up.
    Changes: nothing.
    Refuses: fault.Wrong, as `practices.judged_by` does.
    Carries: S1 `A->>T: gets each deliverable doing, and the Cut of the first in the work's order
    that no start that runs holds`, for the generator.
    """
    each = rounds_of(run, plugin_root, tree, deliverable)
    if not each:
        return Round(_since(run, deliverable) + 1, False, ())
    latest = each[-1]
    if not _there(run, rounds.path_in(run, deliverable, latest.number, "made.json")):
        return latest
    answered = [
        _there(run, rounds.path_in(run, deliverable, latest.number, f"answers-{g}.json"))
        for g in latest.groups
    ]
    if not all(answered):
        return None
    changed = _decisions(rounds.at_cut(run, deliverable, latest.number), deliverable) != (
        _decisions(tree, deliverable)
    )
    made = sum(r.structure == latest.structure for r in each)
    if latest.structure:
        return Round(latest.number + 1, True, ()) if changed and made < _MOST else None
    return Round(latest.number + 1, not (changed and made < _MOST), ())


def of_structure(
    run: Run, plugin_root: str, tree: DesignTree, deliverable: str, number: int
) -> bool:
    """Whether a round of the deliverable is of structure.

    Takes: the run, rn's folder, the tree, the deliverable's path, and the round's number.
    Gives: True where `rounds_of` or, for a round not yet begun, `next_round` gives it as of
    structure.
    Changes: nothing.
    Refuses: fault.Wrong, as `practices.judged_by` does.
    Carries: S1 `O->>G: starts it, with that text (Cut, More kept)`, whose Cut names the best
    practice that the round works by.
    """
    each = [*rounds_of(run, plugin_root, tree, deliverable)]
    due = next_round(run, plugin_root, tree, deliverable)
    each += [due] if due else []
    return any(r.structure for r in each if r.number == number)


def _since(run: Run, deliverable: str) -> int:
    """The round that the deliverable's latest sign-off kept, 0 where none did."""
    kept = [
        s.round
        for s in sign_offs.read(run).each
        if s.kind is sign_offs.Kind.DELIVERABLE and s.what == deliverable and s.round is not None
    ]
    return kept[-1] if kept else 0


def _decisions(tree: DesignTree, deliverable: str) -> Mapping[str, Any]:
    """Each decision under the deliverable, by its necessary condition's ID."""
    node = design.deliverable(tree, deliverable)
    return {c["id"]: c["decisions"] for c in node.get("necessary_conditions", [])}


def _holding(
    groups: tuple[practices.Group, ...], own: tuple[int, ...], named: set[str]
) -> tuple[int, ...]:
    """Each of the groups that holds a condition named, or each of them where none does."""
    found = tuple(n for n in own if named & set(groups[n].conditions))
    return found or own


def _there(run: Run, path: str) -> bool:
    return os.path.exists(os.path.join(run.worktree, path))
