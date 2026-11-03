"""The routes, as docs/routes.md gives them: the result command each subagent gives its result by;
and the next start, decided from the routes and the orchestrator's starts as they came back, with
the result each started subagent gave in its run, and told in its line of docs/routes.md's table.

A start counts once its subagent has ended: as its call comes back `completed`, or, come back
`async_launched`, once the subagent of the ID it gave has ended. The starts after the end are left
out, as the orchestrator is free once no start is left."""

from __future__ import annotations

from typing import Any, Callable, NamedTuple

# The result command, as a step writes it and Claude Code puts the plugin's folder in it.
COMMAND = "python3 ${{CLAUDE_PLUGIN_ROOT}}/hooks/lane/result.py {name} {on}"


class Start(NamedTuple):
    """A start of the orchestrator's as its call came back: the subagent started, by its name, the
    status the call gave, and the ID of the subagent's run."""

    name: str
    status: str
    agent: str


class Next(NamedTuple):
    """The next start: `start` with the subagent due, `wait` with the subagent run in the
    background, or `end` with none; and the subagent and result it follows, where it follows one."""

    kind: str
    name: str
    gave: tuple[str, str] | None


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


def next_start(
    routes: dict[str, Any],
    starts: list[Start],
    result: Callable[[str], str | None],
    ended: Callable[[str], bool],
) -> Next:
    """The next start after the starts, as `result` gives the result of a subagent's run by its ID,
    and `ended` whether it has ended: the orchestrator's route at first; after each start counted,
    the route of its subagent on its result, or the same start again where it gave no result; a
    wait while the last runs in the background."""
    first = next(r["to"] for r in routes["routes"] if r["from"] == routes["orchestrator"])
    found = Next("start", first, None)
    for s in starts:
        # A next start is `end`, `start` or `wait`, `end` the first of them in order; once it is
        # `end` it stays so, so each turn left would break.
        if found.kind == "end":  # pragma: no mutate
            break  # pragma: no mutate
        # The guard holds a status to `completed` and `async_launched` as the call comes back.
        background = s.status != "completed"  # pragma: no mutate
        if background and not ended(s.agent):
            found = Next("wait", s.name, None)
            continue
        on = result(s.agent)
        route = next(
            (r for r in routes["routes"] if (r["from"], r.get("on")) == (s.name, on)), None
        )
        if route is None:
            found = Next("start", s.name, None)
        else:
            found = Next(
                "start" if "to" in route else "end", route.get("to", ""), (s.name, route["on"])
            )
    return found


def line(found: Next, plugin: str) -> str:
    """What the orchestrator is told of the next start, as docs/routes.md's table has it, the
    plugin's name heading it left to whoever tells it."""
    # A next start is `end`, `start` or `wait`, `wait` the last of them in order.
    if found.kind == "wait":  # pragma: no mutate
        return f"Wait for `{plugin}:{found.name}` to end: you are told the next start once it has."
    gave = f"{found.gave[0]} gave `{found.gave[1]}`. " if found.gave else ""
    # A next start is `end`, `start` or `wait`, `end` the first of them in order.
    if found.kind == "end":  # pragma: no mutate
        return gave + "Start no more subagents."
    return gave + f"Start `{plugin}:{found.name}`."
