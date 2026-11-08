"""Decides whether a plugin can follow its routes, which results a role may give, and which start
is due from the starts of a run, as plugins/lane/docs/routes.md gives the routes.

A route names the role that the skill starts next after a role ends with a result. A role of the
plugin goes by its name, and a role or a skill of a dependency by `<dependency>:<name>`.
"""

from __future__ import annotations

from typing import Any, NamedTuple, Protocol

import called
import command
import lanes

# A result, as a role gives it by the result script.
RESULT = {"type": "string", "pattern": "^[a-z][a-z0-9_-]*$"}
# The form of the routes, as plugins/lane/docs/routes.md gives it.
SCHEMA = {
    "type": "object",
    "required": ["orchestrator", "routes"],
    "additionalProperties": False,
    "properties": {
        "orchestrator": {"type": "string"},
        "step": {"type": "integer", "minimum": 1},
        "command": {"type": "string", "minLength": 1},
        "routes": {
            "type": "array",
            "minItems": 2,
            "items": {
                "type": "object",
                "required": ["from"],
                "additionalProperties": False,
                "properties": {
                    "from": {"type": "string"},
                    "on": RESULT,
                    "to": {"type": "string"},
                    "waits": {"const": True},
                },
            },
        },
        "fan_out": {"type": "array", "items": {"type": "string"}},
        "precedence": {
            "anyOf": [
                {"type": "array", "items": RESULT},
                {"type": "object", "additionalProperties": {"type": "array", "items": RESULT}},
            ]
        },
    },
}
# The result of a role that gives one where no route and no `results` name any.
DONE = "done"


class Route(NamedTuple):
    """One route of the routes."""

    # The role that ends, or the skill for the first start.
    source: str
    # The result that the role ends with, or None for the first start.
    on: str | None
    # The role or the dependency's skill to start next, or None.
    to: str | None
    # Whether the run waits for the person's answer to the role's point.
    waits: bool


class Routes(NamedTuple):
    """The routes of a plugin, as `hooks/lanes.json` gives them."""

    # The skill that starts the roles, by its folder under skills/.
    orchestrator: str
    # The skill's step that the routes' sentence ends, or None where the skill holds no list.
    step: int | None
    # The command that prints the text of each start, or None.
    command: str | None
    # Each route, in the order the routes give them.
    routes: tuple[Route, ...]
    # Each role that the skill may start several times at once.
    fan_out: tuple[str, ...]
    # The order of results for every role, or one order for each role by its name, or None.
    precedence: list[str] | dict[str, list[str]] | None


class Due(NamedTuple):
    """Where a run stands: what the main conversation is to do next."""

    # `start`, `wait`, `again`, `waits`, `end`, or `unordered`.
    kind: str
    # The role to start, to wait for, to start again, whose point waits, or that ended the run.
    role: str
    # The result that led here, or None.
    result: str | None = None
    # The role that gave that result, or None.
    after: str | None = None
    # How many starts gave that result, or how many starts run.
    count: int = 0
    # The ID of the start whose point waits, or None.
    agent: str | None = None


def parsed(data: dict[str, Any]) -> Routes:
    """The routes in the JSON, which holds to SCHEMA."""
    found = tuple(
        Route(r["from"], r.get("on"), r.get("to"), r.get("waits") is True) for r in data["routes"]
    )
    return Routes(
        data["orchestrator"],
        data.get("step"),
        data.get("command"),
        found,
        tuple(data.get("fan_out", [])),
        data.get("precedence"),
    )


def faults(found: Routes) -> list[str]:
    """What keeps a plugin from following the routes, none where it can follow them."""
    shown = []
    first = [r for r in found.routes if r.source == found.orchestrator]
    if len(first) > 1:
        shown.append(f"the routes hold more than one route from {found.orchestrator}")
    elif not first or first[0].on is not None or first[0].to is None:
        shown.append(
            f"the routes hold no route from {found.orchestrator} with a `to` and no `on`, the"
            " first start"
        )
    seen = set()
    for route in found.routes:
        if route.source == found.orchestrator:
            continue
        if route.on is None:
            shown.append(f"the route from {route.source} to {route.to} has no `on`")
        elif (route.source, route.on) in seen:
            shown.append(f"two routes from {route.source} are on `{route.on}`")
        seen.add((route.source, route.on))
        if route.to and route.waits:
            shown.append(
                f"the route from {route.source} on `{route.on}` has both a `to` and `waits`"
            )
        if route.waits and route.source in found.fan_out:
            shown.append(
                f"{route.source} fans out, so Lane can't tell which of its starts to resume on"
                f" `{route.on}`"
            )
    sources = {r.source for r in found.routes}
    for to in dict.fromkeys(r.to for r in found.routes if r.to):
        if to not in sources:
            shown.append(f"{to} is started, and no route is from it, so it has no result to give")
    if not any(r.to is None and not r.waits for r in found.routes if r.on is not None):
        shown.append("no route has neither a `to` nor `waits`, so the run can't end")
    return shown + _fan_out_faults(found)


def _fan_out_faults(found: Routes) -> list[str]:
    """What keeps fan_out and precedence from telling the result of starts at once."""
    shown = []
    started = {r.to for r in found.routes}
    for role in found.fan_out:
        given = results(found, role) or []
        if role not in started:
            shown.append(f"fan_out names {role}, which no route starts")
        elif len(given) > 1 and not set(given) <= set(_order(found, role)):
            shown.append(
                f"{role} fans out and gives more than one result, so precedence orders each of them"
            )
    if isinstance(found.precedence, dict):
        orders = {
            f" for {role}": (o, results(found, role) or [], f"from {role} ")
            for role, o in found.precedence.items()
        }
    else:
        every = [r.on for r in found.routes if r.on]
        orders = {"": (found.precedence or [], every, "")}
    for where, (order, given, source) in orders.items():
        for result in dict.fromkeys(order):
            if order.count(result) > 1:
                shown.append(f"precedence names `{result}` twice{where}")
            if result not in given:
                shown.append(f"precedence names `{result}`, which no route {source}is on")
    return shown


def _order(found: Routes, role: str) -> list[str]:
    """The order of the role's results, first to last, or none where precedence gives none."""
    if isinstance(found.precedence, dict):
        return found.precedence.get(role, [])
    return found.precedence or []


def results(found: Routes, name: str) -> list[str] | None:
    """The results that the role of the name may give by the routes, or None where no route is
    from it. The skill gives the result of each route that ends the run."""
    if name == found.orchestrator:
        return [r.on for r in found.routes if r.on and r.to is None and not r.waits]
    ons = [r.on for r in found.routes if r.source == name and r.on]
    return ons or None


class _Laid(Protocol):
    """What allowed and result_commands read of the lanes laid, as the Laid of laid.py gives it."""

    @property
    def routes(self) -> Routes | None: ...

    def role(self, name: str) -> Any: ...


def allowed(found: _Laid, name: str) -> list[str]:
    """The results that the role of the name may give: those of the routes from it, else those its
    `results` name, else `done`."""
    if found.routes is not None:
        by_routes = results(found.routes, name)
        if by_routes is not None:
            return by_routes
    role = found.role(name)
    if role is not None and role.results is not None:
        return list(role.results)
    return [DONE]


def result_commands(found: _Laid, name: str) -> list[str]:
    """The commands by which the role or the skill of the name gives each result it may give, none
    where it gives no result.

    A role gives a result where the routes name it, where it names its results, or where it has a
    lane that the guard checks as the role gives its result.
    """
    by_routes = None if found.routes is None else results(found.routes, name)
    role = found.role(name)
    lanes_end = role is not None and any(
        lanes.ends(lane.lane) or lanes.traced(lane.lane) for lane in role.lanes
    )
    if by_routes is None and not lanes_end and (role is None or role.results is None):
        return []
    return [f"python3 {command.ROOT}/hooks/lane/result.py {name} {r}" for r in allowed(found, name)]


def named(found: Routes) -> list[str]:
    """Each role or dependency's skill that the routes name, once, the skill aside."""
    names = [n for r in found.routes for n in (r.source, r.to) if n]
    return [n for n in dict.fromkeys(names) if n != found.orchestrator]


def typed(plugin: str, name: str) -> str:
    """The name that Claude Code gives a role: `<plugin>:<name>` for the plugin's own role, and a
    dependency's role as the routes name it."""
    return name if ":" in name else f"{plugin}:{name}"


def combined(found: Routes, role: str, given: list[str]) -> str | None:
    """The result of starts of the role at once, or None where they gave different results that no
    order of precedence holds."""
    if len(set(given)) == 1:
        return given[0]
    order = _order(found, role)
    if not set(given) <= set(order):
        return None
    return next(r for r in order if r in given)


def due(found: Routes, groups: list[called.Group]) -> Due:
    """Where the run stands, from the groups of starts of the run, in their order."""
    first = next(r for r in found.routes if r.source == found.orchestrator)
    now = Due("start", first.to or "")
    for group in groups:
        if any(s.running for s in group.starts):
            return Due("wait", group.role, count=len(group.starts))
        if any(s.result is None for s in group.starts):
            return Due("again", group.role)
        result = combined(found, group.role, [s.result or "" for s in group.starts])
        route = next((r for r in found.routes if r.source == group.role and r.on == result), None)
        if route is None:
            return Due("unordered", group.role)
        count = len(group.starts)
        if route.to:
            now = Due("start", route.to, result, group.role, count)
        elif route.waits:
            now = Due("waits", group.role, result, group.role, count, group.starts[0].agent)
        else:
            return Due("end", group.role, result, group.role, count)
    return now
