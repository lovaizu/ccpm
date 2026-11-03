"""The routes, as docs/routes.md gives them: the result command each subagent gives its result by;
and the next start, decided from the routes and the orchestrator's starts as they came back, with
the result each started subagent gave in its run, and told in its line of docs/routes.md's table.

A start counts once its subagent has ended: as its call comes back `completed`, or, come back
`async_launched`, once the subagent of the ID it gave has ended. Starts joined to the one before
them, as further runs of a subagent the routes fan out, or as a run started again for one that
ended with no result, count together, once every one has ended: their results give the one they
share, or the first of them in the order the routes give. The starts after the end are left out,
as the orchestrator is free once no start is left."""

from __future__ import annotations

from typing import Any, Callable, NamedTuple

# The result command, as a step writes it and Claude Code puts the plugin's folder in it.
COMMAND = "python3 ${{CLAUDE_PLUGIN_ROOT}}/hooks/lane/result.py {name} {on}"


# How a start is joined to the starts before it: as a further run of a subagent fanned out, or as
# a run started again where one of them ended with no result.
MORE = "more"
AGAIN = "again"


class Start(NamedTuple):
    """A start of the orchestrator's as its call came back: the subagent started, by its name, the
    status the call gave, the ID of the subagent's run, and how it is joined to the starts before
    it, MORE or AGAIN, or "" where it is not."""

    name: str
    status: str
    agent: str
    joined: str = ""


class Next(NamedTuple):
    """The next start: `start` with the subagent due, `wait` with the subagent run in the
    background, or `end` with none; the subagent and result it follows, where it follows one;
    whether it is the start of a subagent again, as a run of it ended with no result; how many runs
    gave the result it follows; and, waiting, whether more runs of the subagent may start, as the
    routes fan it out."""

    kind: str
    name: str
    gave: tuple[str, str] | None
    again: bool = False
    runs: int = 1
    more: bool = False


class Unordered(ValueError):
    """Where the runs of a subagent at once gave results the routes give no order to take one of
    them by: the subagent's name, and what is wrong."""

    def __init__(self, name: str, wrong: str) -> None:
        super().__init__(wrong)
        self.name = name


def command(name: str, on: str) -> str:
    """The command the subagent of the name gives the result by."""
    return COMMAND.format(name=name, on=on)


def ons(routes: dict[str, Any], name: str) -> list[str]:
    """The results the subagent of the name gives, as the routes from it are on them, in order."""
    return [r["on"] for r in routes["routes"] if r["from"] == name and "on" in r]


def named(routes: dict[str, Any]) -> list[str]:
    """Each subagent the routes name, the orchestrator first, then each as a route names it,
    once."""
    names = [routes["orchestrator"]]
    for r in routes["routes"]:
        names += [r[k] for k in ("from", "to") if k in r]
    return list(dict.fromkeys(names))


def giving(routes: dict[str, Any]) -> list[str]:
    """Each subagent that gives a result: those the routes are from, the orchestrator left out."""
    return [n for n in named(routes) if ons(routes, n)]


def listed(things: list[str]) -> str:
    """The things, listed with commas and `and` before the last."""
    return " and ".join(filter(None, [", ".join(things[:-1]), things[-1]]))


def fans_out(routes: dict[str, Any], name: str) -> bool:
    """Whether the orchestrator may start several runs of the subagent of the name at once."""
    return name in routes.get("fan_out", [])


def order(routes: dict[str, Any], name: str) -> list[str] | None:
    """The order the results of the subagent of the name are taken in, first to last: its own, or
    the one for every subagent; None where the routes give neither."""
    given = routes.get("precedence")
    return given.get(name) if isinstance(given, dict) else given


def combined(routes: dict[str, Any], name: str, given: list[str]) -> str:
    """The result of the runs of the subagent of the name, which gave the results: the one they
    share, or the first of them in its order. Stops with Unordered where they differ and the order
    does not hold each."""
    found = list(dict.fromkeys(given))
    if not found[1:]:
        # The results hold one here, so its first is its last.
        return found[0]  # pragma: no mutate
    taken = order(routes, name) or []
    if not all(on in taken for on in found):
        gave = listed([f"`{on}`" for on in found])
        wrong = f"the runs of {name} at once gave {gave}, and the routes order not each of them"
        raise Unordered(name, wrong + " in `precedence`")
    return min(found, key=taken.index)


def next_start(
    routes: dict[str, Any],
    starts: list[Start],
    result: Callable[[str], str | None],
    ended: Callable[[str], bool],
) -> Next:
    """The next start after the starts, as `result` gives the result of a subagent's run by its ID,
    and `ended` whether it has ended: the orchestrator's route at first; after each start, with
    those joined to it, the route of their subagent on their result once every run has ended, or
    the same subagent again where a run is left with no result; a wait while any runs in the
    background. Stops with Unordered where their results cannot be told one."""
    first = next(r["to"] for r in routes["routes"] if r["from"] == routes["orchestrator"])
    found = Next("start", first, None)
    name, runs = "", list[Start]()
    for s in starts:
        joins = bool(s.joined) and s.name == name
        # A next start is `end`, `start` or `wait`, `end` the first of them in order.
        over = found.kind == "end"  # pragma: no mutate
        # Once the runs have led to the end, a start joined to them may still come back.
        if over and not joins:
            break
        name, runs = s.name, [*runs, s] if joins else [s]
        found = taken(routes, name, runs, result, ended)
    return found


def running(s: Start, ended: Callable[[str], bool]) -> bool:
    """Whether the start's subagent still runs: launched in the background and not ended."""
    # The guard holds a status to `completed` and `async_launched` as the call comes back.
    background = s.status != "completed"  # pragma: no mutate
    return background and not ended(s.agent)


def taken(
    routes: dict[str, Any],
    name: str,
    runs: list[Start],
    result: Callable[[str], str | None],
    ended: Callable[[str], bool],
) -> Next:
    """The next start after the runs of the subagent of the name, joined, as `next_start` has
    it."""
    if any(running(s, ended) for s in runs):
        return Next("wait", name, None, more=fans_out(routes, name))
    given = [on for on in (result(s.agent) for s in runs) if on is not None]
    # Each run started again stands for one that ended with no result.
    owed = len(runs) - sum(s.joined == AGAIN for s in runs)
    if len(given) < owed:
        return Next("start", name, None, True)
    on = combined(routes, name, given)
    route = next((r for r in routes["routes"] if (r["from"], r.get("on")) == (name, on)), None)
    if route is None:
        return Next("start", name, None, True)
    kind = "start" if "to" in route else "end"
    return Next(kind, route.get("to", ""), (name, on), runs=len(given))


def line(found: Next, plugin: str) -> str:
    """What the orchestrator is told of the next start, as docs/routes.md's table has it, the
    plugin's name heading it left to whoever tells it."""
    # A next start is `end`, `start` or `wait`, `wait` the last of them in order.
    waiting = found.kind == "wait"  # pragma: no mutate
    if waiting and found.more:
        return (
            f"Wait for every run of `{plugin}:{found.name}` to end: you are told the next start"
            " once each has."
        )
    if waiting:
        return f"Wait for `{plugin}:{found.name}` to end: you are told the next start once it has."
    gave = f"{found.gave[0]} gave `{found.gave[1]}`. " if found.gave else ""
    # A run counts where it gave a result, so the runs are never fewer than 1.
    several = found.runs > 1  # pragma: no mutate
    if found.gave and several:
        gave = f"The {found.runs} runs of {found.gave[0]} gave `{found.gave[1]}`. "
    # A next start is `end`, `start` or `wait`, `end` the first of them in order.
    if found.kind == "end":  # pragma: no mutate
        return gave + "Start no more subagents."
    if found.again:
        return f"{found.name} ended with no result. Start `{plugin}:{found.name}` again."
    return gave + f"Start `{plugin}:{found.name}`."
