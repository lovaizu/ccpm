"""Decides where each round of a deliverable keeps its files in the run's `rounds/`: its Try
record, the generator's Made, each evaluator's Answers, each More kept, and the Place of each start,
and which round is a deliverable's latest. A round lies in `rounds/<deliverable>/<number>/`, the
deliverable's path quoted as one name, and a start of a round names its round as `<deliverable>.r
<number>`, with `.g<group>` for an evaluator's group, which its record's name keeps."""

from __future__ import annotations

import json
import os
import re
from collections.abc import Sequence
from dataclasses import dataclass
from urllib.parse import quote, unquote

from fault import Wrong
from repository import git

from tree import records
from tree.design import DesignTree
from tree.more import More
from tree.results import Answers, Made, read_answers, read_made
from tree.runs import Run

# A start of a round, as a record's name keeps it.
_START = re.compile(r"^([^.]+)\.r(\d+)(?:\.g(\d+))?$")
# An evaluator's Answers in a round, by its group.
_ANSWERS = re.compile(r"^answers-(\d+)\.json$")
# What a Place's name holds before the name of its start's record.
_PLACE = "place-"


@dataclass(frozen=True)
class Round:
    """One round of a deliverable: the deliverable by its path, the round's number from 1, what the
    generator made, or None before it wrote it, and each evaluator's Answers written so far."""

    deliverable: str
    number: int
    made: Made | None
    answers: tuple[Answers, ...]


@dataclass(frozen=True)
class Start:
    """Which start of a round a record keeps: the deliverable's path, the round's number, and the
    evaluator's group of necessary conditions from 0, or None for the generator's."""

    deliverable: str
    number: int
    group: int | None


def each(run: Run, deliverable: str) -> tuple[Round, ...]:
    """Each round of a deliverable, the latest last.

    Takes: the run, and the deliverable's path.
    Gives: each round, through `results.read_made` and `results.read_answers`.
    Changes: nothing.
    Refuses: fault.Wrong, where the deliverable has no round or a file of it leaves its form.
    Carries: S1 `O->>T: gets the round (Answers, Made)`, and `T-->>O: each evaluator's Answers, and
    what the generator made`; S6 `O->>O: finds each change to a best practice and each general
    lesson in what the run's evaluators put in more`, which reads every round.
    """
    numbers = range(1, latest(run, deliverable) + 1)
    if not numbers:
        raise Wrong(f"{deliverable} has no round yet; its generator opens the first")
    return tuple(_round(run, deliverable, number) for number in numbers)


def latest(run: Run, deliverable: str) -> int:
    """The number of a deliverable's latest round.

    Takes: the run, and the deliverable's path.
    Gives: the number of the latest round that holds a file, from 1, or 0 where it has none.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `A->>T: gets each deliverable doing, and the Cut of the first that no start that
    runs holds`, which finds whether its round is made, judged, or to make again.
    """
    folder = _folder(run, deliverable)
    held = os.listdir(folder) if os.path.isdir(folder) else []
    return max((int(name) for name in held if name.isdigit()), default=0)


def made_path(run: Run, deliverable: str, new: bool) -> str:
    """Where the generator writes its Made.

    Takes: the run, the deliverable's path, and whether the start opens a new round.
    Gives: the path from the worktree, in the latest round, or in a new one after it, which is round
    1 where the deliverable has none.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `A->>T: ... the Cut of the first that no start that runs holds`, whose run values
    name it; `G->>F: writes what it made`.
    """
    number = latest(run, deliverable)
    return _in(run, deliverable, number + 1 if new or not number else number, "made.json")


def answers_path(run: Run, deliverable: str, group: int) -> str:
    """Where an evaluator writes its Answers.

    Takes: the run, the deliverable's path, and its group of necessary conditions, from 0, counted
    across the deliverable's kind's best practice and then the refactor one.
    Gives: the path from the worktree, in the latest round.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `A->>T: ... the Cut`, whose run values name it; `E->>F: writes each necessary
    condition in good ... or in more (Answers)`.
    """
    return _in(run, deliverable, latest(run, deliverable), f"answers-{group}.json")


def try_path(run: Run, deliverable: str) -> str:
    """Where throwaway.py keeps each command tried in the latest round.

    Takes: the run, and the deliverable's path.
    Gives: the path of the round's Try record, from the worktree.
    Changes: nothing.
    Refuses: fault.Wrong, where the deliverable has no round.
    Carries: S1 `G->>W: tries it (Try record)`.
    """
    number = _held(run, deliverable, "in which a command it tries is kept")
    return _in(run, deliverable, number, "try.jsonl")


def place_path(run: Run, record: str) -> str:
    """Where the Place of one start lies.

    Takes: the run, and the start's record.
    Gives: the full path, in the round of the start, or in the run's rounds/ for a start of no
    round.
    Changes: nothing.
    Refuses: fault.Wrong, where the record names no start of the run.
    Carries: S1 `G->>T: commits its work at the end of each step (Place)`; S5 `O->>G: starts each
    that stood in a step, at that step (Cut, Place)`.
    """
    name = f"{_PLACE}{os.path.basename(record)}"
    start = records.start_of(record)
    if not start:
        return os.path.join(run.folder, "rounds", name)
    of = start_of(start)
    return os.path.join(_folder(run, of.deliverable), str(of.number), name)


def stood_place(run: Run, start: str) -> str | None:
    """Where the Place of the latest start that stood in a start of a round lies.

    Takes: the run, and the start of the round, as `start_name` gives it.
    Gives: the full path of the Place of the latest start, in the order of the starts, whose record
    keeps that start of the round, or None where no start of it kept a Place.
    Changes: nothing.
    Refuses: fault.Wrong, where it names no start of a round.
    Carries: S5 `O->>G: starts each that stood in a step, at that step (Cut, Place)`, and the same
    of each evaluator, as each start anew of a round that one stood in takes its Place.
    """
    of = start_of(start)
    folder = os.path.join(_folder(run, of.deliverable), str(of.number))
    held = sorted(os.listdir(folder)) if os.path.isdir(folder) else []
    stood = [
        name
        for name in held
        if name.startswith(_PLACE)
        and records.start_of(os.path.join("records", name[len(_PLACE) :])) == start
    ]
    return os.path.join(folder, stood[-1]) if stood else None


def start_name(deliverable: str, number: int, group: int | None = None) -> str:
    """Which start of a round a start is, as `records.new_record` takes it.

    Takes: the deliverable's path, the round's number, and the evaluator's group, or None for the
    generator.
    Gives: the start, as `start_of` reads it back.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `A->>T: ... with the path of a new Record for the start`, whose name keeps it.
    """
    named = f"{_key(deliverable).replace('.', '%2E')}.r{number}"
    return named if group is None else f"{named}.g{group}"


def start_of(start: str) -> Start:
    """The start of a round that `start_name` gave.

    Takes: the start, as a record's name keeps it.
    Gives: its deliverable, round, and group.
    Changes: nothing.
    Refuses: fault.Wrong, where it names no start of a round.
    Carries: S1 `GD->>R: checks its record`, by the Cut of the start.
    """
    found = _START.match(start)
    if not found:
        raise Wrong(f"{start!r} names no start of a round")
    group = int(found[3]) if found[3] is not None else None
    return Start(unquote(found[1]), int(found[2]), group)


def keep_more(run: Run, more: Sequence[More]) -> tuple[str, ...]:
    """Keeps each More for the next round of its deliverable.

    Takes: the run, and each More, each checked by `more.keepable`.
    Gives: each path written, from the worktree.
    Changes: the More kept of each deliverable's latest round.
    Refuses: fault.Wrong, where a deliverable has no round.
    Carries: S1 `K->>T: writes the decision, and keeps the more (Design tree, More kept)`.
    """
    written = []
    for deliverable in dict.fromkeys(each.deliverable for each in more):
        number = _held(run, deliverable, "for whose next round a more is kept")
        kept = kept_more(run, deliverable, number)
        kept += tuple(m for m in more if m.deliverable == deliverable and m not in kept)
        path = _in(run, deliverable, number, "more.json")
        with open(os.path.join(run.worktree, path), "w", encoding="utf-8") as f:
            json.dump([{"condition": m.condition, "good_when": m.good_when} for m in kept], f)
        written.append(path)
    return tuple(written)


def kept_more(run: Run, deliverable: str, number: int | None = None) -> tuple[More, ...]:
    """Each More kept for a deliverable's next round.

    Takes: the run, the deliverable's path, and the round whose More kept it reads, its latest
    where None.
    Gives: each More kept in that round, none where it keeps none.
    Changes: nothing.
    Refuses: nothing; only `keep_more` writes the More kept, so a fault in it stops with its trace.
    Carries: S1 `O->>G: starts it, with that text (Cut, More kept)`, whose Cut holds them.
    """
    found = latest(run, deliverable) if number is None else number
    path = os.path.join(run.worktree, _in(run, deliverable, found, "more.json"))
    if not found or not os.path.exists(path):
        return ()
    with open(path, encoding="utf-8") as f:
        held = json.load(f)
        return tuple(More(deliverable, e["condition"], e["good_when"]) for e in held)


def at_cut(run: Run, deliverable: str) -> DesignTree:
    """The design tree as the deliverable's latest round took its cut.

    Takes: the run, and the deliverable's path.
    Gives: the tree as the commit that opened the round holds it, through
    `repository.git.file_at`.
    Changes: nothing.
    Refuses: fault.Wrong, where the deliverable has no round; fault.CantRun, where git fails. A
    round that no commit holds stops with its trace, as each step's end commits the round's files
    before an evaluator judges it.
    Carries: S1 `alt no decision that answers the more's necessary condition changed since the
    round's cut`.
    """
    number = _held(run, deliverable, "whose cut a more answers to")
    opened = git.history(run.worktree, os.path.join(_folder(run, deliverable), str(number)))
    tree = os.path.relpath(os.path.join(run.folder, "design-tree.json"), run.worktree)
    # design.write wrote the tree at that commit once design.apply held it to its form.
    return DesignTree(json.loads(git.file_at(run.worktree, opened[-1][0], tree)))


def _round(run: Run, deliverable: str, number: int) -> Round:
    """The round of the number, with the Made and each Answers written in it, by group."""
    folder = os.path.join(_folder(run, deliverable), str(number))
    made = os.path.join(folder, "made.json")
    groups = sorted(
        (int(found[1]), name)
        for name in (os.listdir(folder) if os.path.isdir(folder) else [])
        if (found := _ANSWERS.match(name))
    )
    return Round(
        deliverable,
        number,
        read_made(made) if os.path.exists(made) else None,
        tuple(read_answers(os.path.join(folder, name)) for _, name in groups),
    )


def _held(run: Run, deliverable: str, why: str) -> int:
    """The number of the deliverable's latest round; raises Wrong, saying why a round is needed,
    where it has none."""
    number = latest(run, deliverable)
    if not number:
        raise Wrong(f"{deliverable} has no round yet, {why}")
    return number


def _key(deliverable: str) -> str:
    """The deliverable's path as one name."""
    return quote(deliverable, safe="")


def _folder(run: Run, deliverable: str) -> str:
    return os.path.join(run.folder, "rounds", _key(deliverable))


def path_in(run: Run, deliverable: str, number: int, name: str) -> str:
    """The path of a file of a round.

    Takes: the run, the deliverable's path, the round's number, and the file's name, such as
    `made.json` or `answers-<group>.json`.
    Gives: the path from the worktree.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `A->>T: ... the Cut`, whose run values name the files of the start's round.
    """
    return _in(run, deliverable, number, name)


def _in(run: Run, deliverable: str, number: int, name: str) -> str:
    """The path from the worktree of a file of the deliverable's round."""
    return os.path.relpath(os.path.join(_folder(run, deliverable), str(number), name), run.worktree)
