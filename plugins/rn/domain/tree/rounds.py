"""Decides where each round of a deliverable keeps its files in the run's `rounds/`: its Try
record, the generator's Made, each evaluator's Answers, each More kept, and the Place of each start,
and which round is a deliverable's latest."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from tree.design import DesignTree
from tree.more import More
from tree.results import Answers, Made
from tree.runs import Run


@dataclass(frozen=True)
class Round:
    """One round of a deliverable: the deliverable by its path, the round's number from 1, what the
    generator made, or None before it wrote it, and each evaluator's Answers written so far."""

    deliverable: str
    number: int
    made: Made | None
    answers: tuple[Answers, ...]


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
    raise NotImplementedError("rounds.each")


def made_path(run: Run, deliverable: str, new: bool) -> str:
    """Where the generator writes its Made.

    Takes: the run, the deliverable's path, and whether the start opens a new round.
    Gives: the path, in the latest round or in a new one after it.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `A->>T: ... the Cut of the first that no start that runs holds`, whose run values
    name it; `G->>F: writes what it made`.
    """
    raise NotImplementedError("rounds.made_path")


def answers_path(run: Run, deliverable: str, group: int) -> str:
    """Where an evaluator writes its Answers.

    Takes: the run, the deliverable's path, and its group of necessary conditions, from 0.
    Gives: the path, in the latest round.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `A->>T: ... the Cut`, whose run values name it; `E->>F: writes each necessary
    condition in good ... or in more (Answers)`.
    """
    raise NotImplementedError("rounds.answers_path")


def try_path(run: Run, deliverable: str) -> str:
    """Where throwaway.py keeps each command tried in the latest round.

    Takes: the run, and the deliverable's path.
    Gives: the path of the round's Try record.
    Changes: nothing.
    Refuses: fault.Wrong, where the deliverable has no round.
    Carries: S1 `G->>W: tries it (Try record)`.
    """
    raise NotImplementedError("rounds.try_path")


def place_path(run: Run, record: str) -> str:
    """Where the Place of one start lies.

    Takes: the run, and the start's record.
    Gives: the path, in the round of the start.
    Changes: nothing.
    Refuses: fault.Wrong, where the record names no start of the run.
    Carries: S1 `G->>T: commits its work at the end of each step (Place)`; S5 `O->>G: starts each
    that stood in a step, at that step (Cut, Place)`.
    """
    raise NotImplementedError("rounds.place_path")


def keep_more(run: Run, more: Sequence[More]) -> tuple[str, ...]:
    """Keeps each More for the next round of its deliverable.

    Takes: the run, and each More, each checked by `more.keepable`.
    Gives: each path written, from the worktree.
    Changes: the More kept of each deliverable's latest round.
    Refuses: fault.Wrong, where a deliverable has no round.
    Carries: S1 `K->>T: writes the decision, and keeps the more (Design tree, More kept)`.
    """
    raise NotImplementedError("rounds.keep_more")


def kept_more(run: Run, deliverable: str) -> tuple[More, ...]:
    """Each More kept for a deliverable's next round.

    Takes: the run, and the deliverable's path.
    Gives: each More kept in its latest round.
    Changes: nothing.
    Refuses: fault.Wrong, where a file of the round leaves its form.
    Carries: S1 `O->>G: starts it, with that text (Cut, More kept)`, whose Cut holds them.
    """
    raise NotImplementedError("rounds.kept_more")


def at_cut(run: Run, deliverable: str) -> DesignTree:
    """The design tree as the deliverable's latest round took its cut.

    Takes: the run, and the deliverable's path.
    Gives: the tree as the commit that opened the round holds it, through
    `repository.git.file_at`.
    Changes: nothing.
    Refuses: fault.Wrong, where the deliverable has no round; fault.CantRun, where git fails.
    Carries: S1 `alt no decision that answers the more's necessary condition changed since the
    round's cut`.
    """
    raise NotImplementedError("rounds.at_cut")
