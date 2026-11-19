"""Which starts a run's routes make due, and in which lane, after the command that started it, each
result, each command that the person types, and each chain that the plugin opens: a start that a
route after a command makes due, and the first start of a chain that the plugin opens, opens a lane
of its own, one that a route after a result makes due follows in that result's lane, and a lane
whose route started its role several times waits until each has its result."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from adapters import KeptResult, LaneStart, Opening
from record import Entry, Run
from rules import Rules

# The texts of a role due in a lane, one for each time it starts at once, by its agent type and the
# lane's starts so far: those that the plugin's start adapter gives, or one empty text where the
# plugin has none.
Texts = Callable[[str, list[LaneStart]], list[str]]


@dataclass
class Due:
    """A start due: the role to start, the name of the lane it lies in, the same at each reading of
    the run while the start stays due, and its text, empty where the plugin gives none."""

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


def due(rules: Rules, run: Run, texts: Texts) -> list[Due]:
    """The starts due in the run, each in its lane.

    Takes: the plugin's rules, the run as its record stands, and the texts of each role due.
    Gives: in each lane that an `opened` entry opened, its first start with the entry's text until
    the lane makes it; in each lane, a start for each text of the role that the route of its latest
    result, or of a `joined` entry of it, makes due, but those that the lane has started since; each
    start that a route after the command that called the run, or after a command typed, makes due,
    each role in a lane of its own; a start that a `stopped` entry ended with no result counts as
    not made, so its start is due again in its lane; a command of the plugin, typed or by the Skill
    tool, that a route goes after puts its starts in place of those due before in each lane, but the
    command that called the run, given again, leaves the starts as they stand, as S10 draws; none in
    a lane whose route started its role several times while one of them has no result, or while each
    has one and no `joined` entry follows; none once the routes start no more in any lane, which
    ends the run.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("routes.due")


def joins(rules: Rules, run: Run, texts: Texts) -> list[Join]:
    """The lanes that wait for one result from the results of several starts.

    Takes: the plugin's rules, the run as its record stands, and the texts of each role due.
    Gives: each lane whose latest route after a result started its role once for each of more than
    one text, where each of those starts has its result and no `joined` entry of the lane follows
    them; none where no lane waits so.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("routes.joins")


def picked_up(rules: Rules, run: Run, chains: list[list[KeptResult]]) -> list[Entry]:
    """The entries that pick a run up from the results that its plugin keeps.

    Takes: the plugin's rules, the run with no lane yet, and each chain of kept results in its
    order, as the plugin's kept adapter gives them.
    Gives: for each chain, a lane of its own, and a `result` entry in it for each of the chain's
    results that follows the routes from the command that called the run, up to the first that
    doesn't; none for a chain whose first result follows no route.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("routes.picked_up")


def lanes(run: Run) -> list[list[LaneStart]]:
    """Each lane of the run, with its starts so far, as the plugin's start adapter takes them.

    Takes: the run as its record stands.
    Gives: for each lane, in the order the lanes were opened, each start it has made, in their
    order, with its text and its result where it has one, and the first start of a chain that the
    plugin opened, with its text, while the lane hasn't made it.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("routes.lanes")


def opened(run: Run, openings: list[Opening]) -> list[Entry]:
    """The entries that open the chains that the plugin opens now.

    Takes: the run as its record stands, and the first start of each chain that the plugin's start
    adapter opens.
    Gives: an `opened` entry for each, with its role and its text, in a lane of its own; none where
    no chain opens.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("routes.opened")
