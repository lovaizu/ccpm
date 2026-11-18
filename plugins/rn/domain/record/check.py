"""Decides what rn's check holds an end to: a role's record against its prompt's steps and its best
practices, its result against the items of its Cut, and its deliverable against its kind's
template; the orchestrator's record at the end of a turn that puts work up."""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from typing import Any, cast

from fault import Wrong
from template import check as template_check
from tree import cut, records, results, rounds, runs, sign_offs
from tree.runs import Run

from record import form, items, order, practices, steps
from record.practices import Practice

# The commands whose steps the orchestrator takes, each in its own turn, `up` first.
_COMMANDS = ("up", "dn", "ty", "gm")
# The results by which a role ends before its last step, handing a point back.
_EARLY = ("asks", "lacks")


def check(
    plugin_root: str, cwd: str, role: str, result: str, record: str | None
) -> tuple[str, ...]:
    """What an end lacks.

    Takes: rn's folder; the folder the end came from; the role, or orchestrator; the result given,
    empty where none was; and the start's record from the worktree, or None for the orchestrator's
    of the run of the folder.
    Gives: each step, practice, or item lacking, from `order.lacks` and `items.lacks`, and each
    place where a Markdown deliverable leaves its kind's template, as `<deliverable>:<line>:
    <what>`, from template.check, with the Cut, Made, Answers, and best practice from tree.py's
    code; for a generator or an evaluator started again at a step, the steps from that step, by
    `rounds.started_at`; for asks or lacks, which end before the last step, none of the steps or
    practices; for the orchestrator, from what its record holds after the end of the turn
    before, the steps of each command recorded there, of up too in the run's first turn, and of
    its part, in their latest pass; none where it lacks nothing, or where the orchestrator's turn
    puts no work up, as no sign-off waits, or the folder lies in no run's worktree.
    Changes: keeps the result in the record through `form.keep` once it lacks nothing; for the
    orchestrator, marks the turn's end in its record through `form.mark_turn` once it lacks
    nothing, in a run's worktree.
    Refuses: fault.Wrong, where the record or a file it reads leaves its form; fault.CantRun, where
    one can't be read.
    Carries: S1 `GD->>R: checks its record, its result, and the deliverable (Record)`, and `R-->>GD:
    each step, practice, or item they lack, and each place where the deliverable leaves its kind's
    template, or none, keeping the result in the record`; S3 `R-->>GD: each step it lacks, or
    none, marking the turn's end in the record`.
    """
    run = runs.of_folder(cwd)
    if role == "orchestrator":
        return _orchestrator(plugin_root, run)
    if run is None or record is None:
        raise Wrong(f"the end of {role} names no record of a run's worktree, from {cwd}")
    path = os.path.join(run.worktree, record)
    held = form.read(path)
    taken = cut.of_record(run, record)
    lacking = items.lacks(taken, result, *_wrote(run, taken))
    if result not in _EARLY:
        kinds = _practices(taken, held)
        start = rounds.started_at(run, record) if role in ("generator", "evaluator") else None
        lacking = order.lacks(held, role, steps.numbers(plugin_root, role), kinds, start) + lacking
        lacking += _template(run, taken)
    if not lacking and result:
        form.keep(path, form.Kept(role, result))
    return lacking


def _orchestrator(plugin_root: str, run: Run | None) -> tuple[str, ...]:
    """What the orchestrator's record lacks at the end of a turn that puts work up, from what it
    recorded after the end of the turn before, marking the turn's end once it lacks nothing."""
    if run is None:
        return ()
    path = os.path.join(run.worktree, records.orchestrator_record(run))
    held = form.read(path)
    lacking: tuple[str, ...] = ()
    if any(s.state is sign_offs.State.WAITING for s in sign_offs.read(run).each):
        turn = form.Record(held.entries[held.turns[-1] if held.turns else 0 :], None)
        taken = {e.of for e in turn.entries if e.step is not None}
        first = not held.turns
        prompts = [c for c in _COMMANDS if (c == "up" and first) or c in taken] + ["orchestrator"]
        lacking = tuple(
            each
            for of in prompts
            for each in order.lacks(turn, of, steps.numbers(plugin_root, of), {})
        )
    if not lacking:
        form.mark_turn(path)
    return lacking


def _practices(taken: cut.Cut, held: form.Record) -> Mapping[str, Sequence[Practice]]:
    """Each practice of each best practice that the start works by, by its kind: a generator's of
    its kind and of the refactor one; the tree-keeper's of the design tree marked make, once it's
    resumed with a change, as its first pass only reads the tree, and the orchestrator decides
    each change that the tree-keeper writes."""
    part = cast(Any, taken.part)
    if taken.role == "generator":
        folders = (part["best_practice"], part["refactor"])
        return {os.path.basename(f.rstrip("/")): practices.practices(f) for f in folders}
    if taken.role == "tree-keeper" and len(order.passes(held, "tree-keeper", 1)) > 1:
        each = practices.practices(part["best_practice"])
        return {"design-tree": [p for p in each if p.phase is practices.Phase.MAKE]}
    return {}


def _wrote(run: Run, taken: cut.Cut) -> tuple[results.Made | None, results.Answers | None]:
    """The Made or the Answers that the start wrote, None where it wrote none."""
    part = cast(Any, taken.part)
    made, answers = (_written(run, part.get(field)) for field in ("made", "answers"))
    return (
        results.read_made(made) if made else None,
        results.read_answers(answers) if answers else None,
    )


def _written(run: Run, path: str | None) -> str | None:
    """The full path of a file that the start's Cut names, None where it names none or the start
    hasn't written it."""
    full = os.path.join(run.worktree, path) if path else None
    return full if full and os.path.exists(full) else None


def _template(run: Run, taken: cut.Cut) -> tuple[str, ...]:
    """Each place where a generator's deliverable, a Markdown file, leaves its kind's template."""
    part = cast(Any, taken.part)
    if taken.role != "generator" or not str(part["deliverable"]).endswith(".md"):
        return ()
    # Each kind whose deliverable is a Markdown file has a template, and a generator that ends done
    # has written its deliverable, so a fault in reading either stops with its trace.
    form_path = os.path.join(part["best_practice"], "template.md")
    document = os.path.join(run.worktree, part["deliverable"])
    with open(form_path, encoding="utf-8") as f:
        template = f.read()
    with open(document, encoding="utf-8") as f:
        text = f.read()
    return tuple(
        f"{part['deliverable']}:{fault.line}: {fault.what}"
        for fault in template_check.faults(template, text)
    )
