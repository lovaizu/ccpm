"""Lane's route adapter: which roles a plugin's fixed order makes due now, or whether its run ends,
from the routes of its lane/rules.json and the run as it stands."""

from __future__ import annotations

from order import OrderRun, StartsDue
from rules import Route


def starts_due(routes: list[Route], run: OrderRun) -> StartsDue:
    """The starts due of the run by the routes, or its end.

    Takes: the plugin's routes, and the run as its order sees it.
    Gives: the `starts` of each role that the route after the run's latest result or command makes
    due, as many times at once as the route names it, less each start of it made since; the command
    that called the run, given again, leaves the starts due as they stand, as S10 draws after
    /compact; none where each start that the route makes due is made and one of them still runs,
    with no result yet; `ends` where no route goes after the latest result or command, or each
    start that its route makes due has its result, and no start of the run still runs.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("routes.starts_due")
