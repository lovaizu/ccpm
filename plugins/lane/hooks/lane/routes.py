"""Lane's route adapter: which roles a plugin's fixed order makes due now, or whether its run ends,
from the routes of its lane/rules.json and the run as it stands."""

from __future__ import annotations

from collections import Counter

from order import OrderMove, OrderRun, StartDue, StartsDue
from rules import Route


def starts_due(routes: list[Route], run: OrderRun) -> StartsDue:
    """The starts due of the run by the routes, or its end.

    Takes: the plugin's routes, and the run as its order sees it.
    Gives: the `starts` of each role that the routes make due: the route after the run's latest
    command, and the route after each result since, once for each such result, so that two
    writers' `written` make a reviewer due twice; each as many times at once as the route names the
    role, less each start of it made since; the command that called the run, given again, leaves
    the starts due as they stand, as S10 draws after /compact; none where each start that the
    routes make due is made and one of them still runs, with no result yet; `ends` where no route
    goes after the latest command or a result since, or each start that they make due has its
    result, and no start of the run still runs.
    Changes: nothing.
    Refuses: nothing.
    """
    moves = run["moves"]
    # The command that called the run, given again, moves nothing.
    called = moves[0]
    since = [move for move in moves[1:] if move != called]
    commands = [i for i, move in enumerate(since) if move["kind"] == "command"]
    if commands:
        called, since = since[commands[-1]], since[commands[-1] + 1 :]
    due: Counter[str] = Counter()
    for move in [called, *since]:
        due.update(_route(routes, move))
    due.subtract(move["role"] for move in since if move["kind"] == "start")
    starts: list[StartDue] = [{"role": role, "count": n} for role, n in due.items() if n > 0]
    if starts:
        return {"starts": starts}
    kinds = Counter(move["kind"] for move in moves)
    return {"starts": []} if kinds["start"] > kinds["result"] else {"ends": True}


def _route(routes: list[Route], move: OrderMove) -> list[str]:
    """The roles that the route after the move starts, none where no route goes after it, as after
    a start."""
    if move["kind"] == "start":
        return []
    after = {key: move[key] for key in ("command", "role", "result") if key in move}
    return next((route["start"] for route in routes if route["after"] == after), [])
