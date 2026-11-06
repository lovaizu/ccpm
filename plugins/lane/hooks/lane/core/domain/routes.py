"""The routes, as docs/routes.md gives them: the results each subagent may give, and the result
command it gives each by; and the next start of a run of the skill the routes start from, decided
from the routes and the run's starts as they came back, with the result each started subagent
gave, and told in its line of docs/routes.md's table.

A start counts once its subagent has ended: as its call comes back `completed`, or, come back
`async_launched`, once the subagent of the ID it gave has ended. Starts joined to the one before
them, as further starts of a subagent the routes fan out, or as a start made again for one that
ended with no result, count together, once every one has ended: their results give the one they
share, or the first of them in the order the routes give. The starts after the end are left out,
as the run is over once no start is left."""

from __future__ import annotations

from typing import Any, Callable, NamedTuple

# The result command, as a step writes it and Claude Code puts the plugin's folder in it: the
# folder of the plugin the subagent is of, its own, or a dependency's as lanes/ names one.
COMMAND = "python3 {folder}/hooks/lane/result.py {name} {on}"
OWN = "${CLAUDE_PLUGIN_ROOT}"
DEPENDENCY = "${{dependency:{name}}}"


# How a start is joined to the starts before it: as a further run of a subagent fanned out, or as
# a run started again where one of them ended with no result.
MORE = "more"
AGAIN = "again"


class Start(NamedTuple):
    """A start of the run as its call came back: the subagent started, by its name, the
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
    """The command the subagent of the name gives the result by: by its own plugin's result script,
    in the plugin's folder, or in its dependency's where it is a dependency's,
    `<dependency>:<name>`, as its own plugin lays it."""
    dependency, colon, own = name.rpartition(":")
    folder = DEPENDENCY.format(name=dependency) if colon else OWN
    return COMMAND.format(folder=folder, name=own, on=on)


# The result a subagent with a lane checked at its end gives where no route is from it.
DONE = "done"


def gives(
    routes: dict[str, Any] | None, name: str, ends: bool, own: list[str] | None = None
) -> list[str]:
    """The results the subagent of the name may give, `ends` saying whether a lane of it is checked
    at its end: those the routes from it are on; where none is, its own results, or DONE where it
    names none and a lane of it is checked at its end."""
    found = ons(routes, name) if routes else []
    return found or own or ([DONE] if ends else [])


def kind(name: str, plugin: str) -> str:
    """The type Claude Code gives the subagent of the name, as the routes of the plugin name it:
    `<plugin>:<name>` for one of its own, or the name itself for a dependency's, which names its
    plugin already."""
    return name if ":" in name else f"{plugin}:{name}"


def ons(routes: dict[str, Any], name: str) -> list[str]:
    """The results the subagent of the name gives, as the routes from it are on them, in order."""
    return [r["on"] for r in routes["routes"] if r["from"] == name and "on" in r]


def named(routes: dict[str, Any]) -> list[str]:
    """Each name the routes give, the skill they start from first, then each as a route names it,
    once."""
    names = [routes["orchestrator"]]
    for r in routes["routes"]:
        names += [r[k] for k in ("from", "to") if k in r]
    return list(dict.fromkeys(names))


def giving(routes: dict[str, Any]) -> list[str]:
    """Each subagent that gives a result: those the routes are from, the skill left out."""
    return [n for n in named(routes) if ons(routes, n)]


def listed(things: list[str]) -> str:
    """The things, listed with commas and `and` before the last."""
    return " and ".join(filter(None, [", ".join(things[:-1]), things[-1]]))


def fans_out(routes: dict[str, Any], name: str) -> bool:
    """Whether the skill may start the subagent of the name several times at once."""
    return name in routes.get("fan_out", [])


def order(routes: dict[str, Any], name: str) -> list[str] | None:
    """The order the results of the subagent of the name are taken in, first to last: its own, or
    the one for every subagent; None where the routes give neither."""
    given = routes.get("precedence")
    return given.get(name) if isinstance(given, dict) else given


def unordered(routes: dict[str, Any]) -> str | None:
    """What is wrong where the routes fan out a subagent giving several results that its order
    does not hold each of, so the result of its runs at once could not be told: the first such,
    as `lay.py print` refuses it and the guard holds the routes laid to it; None where none is."""
    for name in routes.get("fan_out", []):
        ons_ = ons(routes, name)
        taken = order(routes, name) or []
        if ons_[1:] and not all(on in taken for on in ons_):
            results = listed([f"`{on}`" for on in ons_])
            return (
                f"gives {name} in `fan_out`, whose results {results} the routes do not order in"
                " `precedence`, so the result of its runs at once could not be told"
            )
    return None


def refused(routes: dict[str, Any]) -> str:
    """Why the routes, in their JSON Schema, cannot be followed, as `lay.py print` refuses them and
    the guard holds the routes laid to it, said as the proposal's error goes on; "" where they can:
    no one first route, from the skill, with a `to` and no `on`; another route with no
    `on`, or two from one subagent on one result; a route to the skill, which gives no
    result, or to a subagent no route is from; no route that ends; an order of results, or a
    subagent fanned out, as `ordered` checks them."""
    lead, each = routes["orchestrator"], routes["routes"]
    if ":" in lead:
        return (
            f"gives {lead} as the skill the routes start from, a skill of another plugin, whose"
            " steps the routes cannot be laid on"
        )
    first = [r for r in each if r["from"] == lead]
    # A first route alone is the start; with none or two, there is none, which has no `to`.
    start: dict[str, Any] = {}
    if len(first) == 1:
        start = first[0]  # pragma: no mutate
    if "on" in start or "to" not in start:
        return (
            f"gives the routes no one route from {lead} with a `to` and no `on`, which starts the"
            " run"
        )
    seen: list[tuple[str, str]] = []
    for r in each:
        if r["from"] == lead:
            continue
        if "on" not in r:
            return f"gives a route from {r['from']} with no `on`"
        if (r["from"], r["on"]) in seen:
            return f"gives two routes from {r['from']} on `{r['on']}`"
        seen.append((r["from"], r["on"]))
    froms = [f for f, _ in seen]
    for r in each:
        to = r.get("to")
        if to == lead:
            return (
                f"gives a route to {lead}, the skill the routes start from, which gives no result"
            )
        if to is not None and to not in froms:
            return (
                f"gives a route to {to}, which no route is from, so it would have no result to give"
            )
    if all("to" in r for r in each):
        return "gives no route without a `to`, so the run cannot end"
    return ordered(routes, froms)


def ordered(routes: dict[str, Any], froms: list[str]) -> str:
    """Why the routes' orders of results, or the subagents they fan out, cannot be followed, the
    subagents routes are from being `froms`; "" where they can: an order of the results of a
    subagent no route is from, naming a result twice or one no route from its subagent is on; a
    subagent fanned out that no route starts, or one giving several results its order does not
    hold each of, as `unordered` says."""
    precedence = routes.get("precedence")
    orders = precedence if isinstance(precedence, dict) else {"": precedence or []}
    for name, taken in orders.items():
        if name and name not in froms:
            return f"gives an order of the results of {name}, which no route is from"
        given = ons(routes, name) if name else [r["on"] for r in routes["routes"] if "on" in r]
        for at, on in enumerate(taken):
            if on in taken[:at]:
                return f"gives `{on}` twice in an order of results"
            if on not in given:
                which = f"no route from {name}" if name else "no route"
                return f"gives `{on}` in an order of results, which {which} is on"
    starts = [r["to"] for r in routes["routes"] if "to" in r]
    for name in routes.get("fan_out", []):
        if name not in starts:
            return f"gives {name} in `fan_out`, which no route starts"
    return unordered(routes) or ""


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
    left: Callable[[str], bool] = lambda agent: False,
) -> Next:
    """The next start after the starts, as `result` gives the result of a subagent's run by its ID,
    `ended` whether it has ended, and `left` whether a run of it ended with no result once: the
    skill's route at first; after each start, with those joined to it, the route of their
    subagent on their result once every run has ended, or the same subagent again where a run is
    left with no result; a wait while any runs in the background. Stops with Unordered where their
    results cannot be told one."""
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
        found = taken(routes, name, runs, result, ended, left)
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
    left: Callable[[str], bool],
) -> Next:
    """The next start after the runs of the subagent of the name, joined, as `next_start` has
    it."""
    if any(running(s, ended) for s in runs):
        return Next("wait", name, None, more=fans_out(routes, name))
    counted = in_place(runs, result, left)
    given = [on for on in (result(s.agent) for s in counted) if on is not None]
    if len(given) < len(counted):
        return Next("start", name, None, True)
    on = combined(routes, name, given)
    route = next((r for r in routes["routes"] if (r["from"], r.get("on")) == (name, on)), None)
    if route is None:
        return Next("start", name, None, True)
    kind = "start" if "to" in route else "end"
    return Next(kind, route.get("to", ""), (name, on), runs=len(given))


def in_place(
    runs: list[Start], result: Callable[[str], str | None], left: Callable[[str], bool]
) -> list[Start]:
    """The runs that count: each run started again takes the place of one that ended with no result,
    the first of them in order, so that run is out of the count even where it gives a result once
    resumed."""
    replaced = [s for s in runs if left(s.agent) or result(s.agent) is None]
    out = replaced[: sum(s.joined == AGAIN for s in runs)]
    return [s for s in runs if s not in out]


def line(found: Next, plugin: str) -> str:
    """What the main conversation is told of the next start, as docs/routes.md's table has it, the
    plugin's name heading it left to whoever tells it."""
    # A next start is `end`, `start` or `wait`, `wait` the last of them in order.
    waiting = found.kind == "wait"  # pragma: no mutate
    named = kind(found.name, plugin)
    if waiting and found.more:
        return f"Wait for every run of `{named}` to end: you are told the next start once each has."
    if waiting:
        return f"Wait for `{named}` to end: you are told the next start once it has."
    gave = f"{found.gave[0]} gave `{found.gave[1]}`. " if found.gave else ""
    # A run counts where it gave a result, so the runs are never fewer than 1.
    several = found.runs > 1  # pragma: no mutate
    if found.gave and several:
        gave = f"The {found.runs} runs of {found.gave[0]} gave `{found.gave[1]}`. "
    # A next start is `end`, `start` or `wait`, `end` the first of them in order.
    if found.kind == "end":  # pragma: no mutate
        return gave + "Start no more subagents."
    if found.again:
        return f"{found.name} ended with no result. Start `{named}` again."
    return gave + f"Start `{named}`."
