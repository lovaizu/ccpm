"""How a role's Marks stand on its Steps: each pass begun by a Mark of Step 1, the Step due in the
latest pass, the Reads and Marks since the Step due began, and the Items of that Step not yet
marked."""

from __future__ import annotations

from collections.abc import Sequence

from run_record import Marked, Report


def step_due(reports: Sequence[Report], last_step: int) -> int | None:
    """The Step due in the role's latest pass.

    Takes: the Marks and Reads of a Start, or of the skill's Run, in the order the record added
    them; and the number of the role's last Step.
    Gives: 1 where no Step has been marked; else the Step after the one marked last since the
    latest Mark of Step 1; None where that pass has marked the last Step.
    Changes: nothing.
    Refuses: nothing.
    Carries: S6 `alt Step n isn't due in the latest pass of its Start`, the Step due of `G->>A:
    asks for the Items of the Step due, with the role and the Start's run values`, and `else a
    Lane of keeps_steps finds a Step unmarked in the latest pass`.
    """
    steps = [r.step for r in reports if isinstance(r, Marked) and r.item is None]
    done = steps[-1] if steps else 0
    return done + 1 if done < last_step else None


def may_mark(reports: Sequence[Report], step: int, last_step: int) -> bool:
    """Whether the role may mark the Step now.

    Takes: the Marks and Reads, as `step_due` takes them; the Step that the run of step.py names;
    and the number of the role's last Step.
    Gives: True for Step 1, whose Mark begins a new pass, and for the Step that `step_due` gives;
    False for any other.
    Changes: nothing.
    Refuses: nothing.
    Carries: S6 `alt Step n isn't due in the latest pass of its Start` and its `else`.
    """
    return step == 1 or step == step_due(reports, last_step)


def since_step_began(reports: Sequence[Report]) -> tuple[Report, ...]:
    """The Reads and Marks since the Step due began.

    Takes: the Marks and Reads, as `step_due` takes them.
    Gives: each one after the latest Mark of a Step, or each one where no Step has been marked,
    as the Start began the first Step; Marks of Items among them.
    Changes: nothing.
    Refuses: nothing.
    Carries: S6 `G->>T: checks the Mark by each Lane on Step n, with the Reads and Marks since the
    Step began`.
    """
    ends = [i for i, r in enumerate(reports) if isinstance(r, Marked) and r.item is None]
    return tuple(reports[ends[-1] + 1 :] if ends else reports)


def items_left(reports: Sequence[Report], items: Sequence[str]) -> tuple[str, ...]:
    """The Items of the Step due that the role hasn't marked since the Step began.

    Takes: the Marks and Reads, as `step_due` takes them; and the Step's Items as the adapter
    gave them.
    Gives: each of the Items with no Mark since the Step began, in the adapter's order; none
    where each is marked.
    Changes: nothing.
    Refuses: nothing.
    Carries: S6 `else a path a Lane of reads_whole names wasn't read whole, or an Item isn't
    marked`, and `G-->>SA: stops it, with the Items left`.
    """
    marked = {r.item for r in since_step_began(reports) if isinstance(r, Marked)}
    return tuple(item for item in items if item not in marked)
