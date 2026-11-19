"""Which starts a run's routes make due, after the command that started it, each result, and each
command that the person types."""

from __future__ import annotations

from dataclasses import dataclass

from record import Run
from rules import Rules


@dataclass
class Due:
    """A start due: the role to start, and its text, empty until the plugin's adapter gives one."""

    role: str
    text: str = ""


def due(rules: Rules, run: Run) -> list[Due]:
    """The starts due in the run.

    Takes: the plugin's rules, and the run as its record stands.
    Gives: each start that the route of the latest result or typed command makes due and that no
    start of the run has made since; a typed command that a route goes after puts its starts in
    place of those before; none once the routes start no more, which ends the run.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("routes.due")
