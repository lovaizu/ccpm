"""Which starts a run's routes make due, and in which lane, after the command that started it, each
result, and each command that the person types: a start that a route after a command makes due
opens a lane of its own, one that a route after a result makes due follows in that result's lane,
and a lane whose route started one role several times waits until each has its result."""

from __future__ import annotations

from dataclasses import dataclass

from record import Run
from rules import Rules


@dataclass
class Due:
    """A start due: the role to start, the name of the lane it lies in, the same at each reading of
    the run while the start stays due, and its text, empty until the plugin's adapter gives one."""

    role: str
    lane: str
    text: str = ""


@dataclass
class Join:
    """A lane that waits for one result: the role that its route started several times, and the
    result of each of those starts, in the order they were added."""

    lane: str
    role: str
    results: list[str]


def due(rules: Rules, run: Run) -> list[Due]:
    """The starts due in the run, each in its lane.

    Takes: the plugin's rules, and the run as its record stands.
    Gives: in each lane, each start that the route of its latest result, or of a `joined` entry of
    it, makes due and that no start of the lane has made since; each start that a route after the
    command that called the run, or after a command typed, makes due, each in a lane of its own; a
    start that a `stopped` entry ended with no result counts as not made, so its start is due again
    in its lane; a command of the plugin, typed or by the Skill tool, that a route goes after puts
    its starts in place of those due before in each lane, but the command that called the run,
    given again, leaves the starts as they stand, as S10 draws; none in a lane whose route started
    one role several times while one of them has no result, or while each has one and no `joined`
    entry follows; none once the routes start no more in any lane, which ends the run.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("routes.due")


def joins(rules: Rules, run: Run) -> list[Join]:
    """The lanes that wait for one result from the results of several starts.

    Takes: the plugin's rules, and the run as its record stands.
    Gives: each lane whose latest route after a result started one role several times, where each
    of those starts has its result and no `joined` entry of the lane follows them; none where no
    lane waits so.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("routes.joins")
