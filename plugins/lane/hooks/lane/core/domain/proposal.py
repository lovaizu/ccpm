"""The proposal the developer AI writes for lay.py, a JSON file at a path it gives: read and held to
its JSON Schema, PROPOSAL, which docs/lanes.md shows, then checked for what no schema can say: the
plugin and each subagent's file found, each name one a hook's command can carry, each subagent and
step given once, each step in its file, and each lane taking at least one thing, none empty; and
the routes held to their JSON Schema, which docs/routes.md shows, and checked as it says, against
the files of the subagents they name. What this version of lane does not lay yet, such as an
adapter or a lane other than run_only and write_only, is refused, so nothing is laid that no check
would hold."""

from __future__ import annotations

import json
import os
import re
from typing import Any

import lanes
import placed
import routes
import rules
import schema
import step
import template

# What the proposal is told to be, when it is not: in the shape docs/lanes.md gives, named by its
# whole path, as the developer AI may run lay.py from any folder.
LANES_MD = os.path.join(placed.LANE, "docs", "lanes.md")
AGAIN = f"write the proposal again in the shape {LANES_MD} gives"
ROUTES_MD = os.path.join(placed.LANE, "docs", "routes.md")
ROUTES_AGAIN = f"write the routes again as {ROUTES_MD} says"
# The proposal's JSON Schema, as docs/lanes.md gives it: each lane docs/lanes.md names, laid by
# this version or not, so a lane not laid yet is refused by name rather than out of shape.
NAMED = [
    "read_only",
    "read_whole",
    "write_only",
    "in_form",
    "run_only",
    "hold",
    "test_after",
    "end_when",
    "every_item",
]
TAKES = {"type": "array", "items": {"type": "string"}}
PROPOSAL = {
    **rules.shape(
        ["plugin"],
        {
            "plugin": {"type": "string", "description": "your plugin's folder"},
            "routes": {
                "type": "object",
                "description": "your subagents' routes, as docs/routes.md gives them",
            },
            "subagents": rules.subagents(NAMED, TAKES, 1, True),
        },
    ),
    "anyOf": [{"required": ["subagents"]}, {"required": ["routes"]}],
}
# A thing given for each run: a name in braces, the braces wrapping the whole take.
GIVEN = re.compile(r"\{[^{}]+\}")


class Stop(Exception):
    """What was wrong, and what to do, where lay.py cannot go on."""


def wrong(what: str, again: str = AGAIN) -> Stop:
    """The stop saying what is wrong with the proposal, and how to write it again."""
    return Stop(f"lay.py: the proposal {what}; {again}.")


def not_yet(what: str) -> Stop:
    """The stop saying the proposal gives what this version of lane does not lay yet."""
    return Stop(
        f"lay.py: the proposal gives {what}, which this version of lane does not lay yet; leave it"
        " out, and run again."
    )


def proposal(path: str) -> dict[str, Any]:
    """The proposal at the path, held to its schema and checked: the plugin's folder, its name, and
    each subagent with its file, its lines, and each step with where it is among them."""
    try:
        with open(path, encoding="utf-8") as f:
            given = json.load(f)
    except OSError:
        raise Stop(f"lay.py: there is no file {path}; {AGAIN}.") from None
    except ValueError:
        raise Stop(f"lay.py: {path} holds no JSON; {AGAIN}.") from None
    out = schema.held(PROPOSAL, given)
    if out is not None:
        raise wrong(f"is out of its shape at {out.told()}")
    root = given["plugin"]
    name = plugin_name(root)
    checked: list[dict[str, Any]] = []
    for each in given.get("subagents", []):
        agent = subagent(root, each)
        # A subagent given twice would be written twice, the second time from the second's lanes
        # alone, and the first's lost though the developer AI approved them.
        if agent["name"] in [a["name"] for a in checked]:
            raise wrong(f"gives {agent['name']} twice, where each subagent comes once")
        checked.append(agent)
    routed = routes_checked(root, given["routes"]) if "routes" in given else None
    return {"plugin": root, "name": name, "subagents": checked, "routes": routed}


def plugin_name(root: str) -> str:
    """The plugin's name, from its manifest, as a hook's command can carry it unquoted."""
    manifest = os.path.join(root, ".claude-plugin", "plugin.json")
    try:
        with open(manifest, encoding="utf-8") as f:
            given = json.load(f)
    except OSError:
        raise wrong(f"names {root} as the plugin, which has no {manifest}") from None
    except ValueError:
        raise Stop(f"lay.py: {manifest} holds no JSON; fix it and run again.") from None
    name = given.get("name") if isinstance(given, dict) else None
    if not isinstance(name, str) or not re.fullmatch(rules.NAME, name):
        raise Stop(
            f"lay.py: {manifest} names the plugin by no name of letters, digits and -._; fix it"
            " and run again."
        )
    return name


def agent_lines(root: str, name: str, again: str = AGAIN) -> tuple[str, list[str]]:
    """The file of the subagent of the name, and its lines; stops where the name is none a hook's
    command can carry, or no file in the plugin's agents/ gives it."""
    if not re.fullmatch(rules.NAME, name):
        raise wrong("gives a subagent no name", again)
    file = step.agent_file(root, name)
    if file is None:
        raise wrong(f"gives {name}, which no file in agents/ names", again)
    with open(file, encoding="utf-8") as f:
        return file, f.read().splitlines(keepends=True)


def routes_checked(root: str, given: dict[str, Any]) -> dict[str, Any]:
    """The routes, held to their schema and checked as docs/routes.md says: one first route, from
    the orchestrator, with a `to` and no `on`; each other from another subagent, on a result, one
    route a result; each `to` a subagent routed from, not the orchestrator, which gives no result;
    a route that ends; the orchestrator's step in its file, its tools, where named, with Agent; no
    subagent they name in the background; and each subagent giving a result with a last step."""
    out = schema.held(rules.ROUTES, given)
    if out is not None:
        raise wrong(f"is out of its shape at $.routes{out.told()[1:]}", ROUTES_AGAIN)
    lead, each = given["orchestrator"], given["routes"]
    first = [r for r in each if r["from"] == lead]
    if len(first) != 1 or "on" in first[0] or "to" not in first[0]:
        raise wrong(
            f"gives the routes no one route from {lead} with a `to` and no `on`, which starts the"
            " run",
            ROUTES_AGAIN,
        )
    seen: list[tuple[str, str]] = []
    for r in each:
        if r["from"] == lead:
            continue
        if "on" not in r:
            raise wrong(f"gives a route from {r['from']} with no `on`", ROUTES_AGAIN)
        if (r["from"], r["on"]) in seen:
            raise wrong(f"gives two routes from {r['from']} on `{r['on']}`", ROUTES_AGAIN)
        seen.append((r["from"], r["on"]))
    froms = [f for f, _ in seen]
    for r in each:
        to = r.get("to")
        if to == lead:
            raise wrong(
                f"gives a route to {lead}, the orchestrator, which gives no result", ROUTES_AGAIN
            )
        if to is not None and to not in froms:
            raise wrong(
                f"gives a route to {to}, which no route is from, so it would have no result to"
                " give",
                ROUTES_AGAIN,
            )
    if all("to" in r for r in each):
        raise wrong("gives no route without a `to`, so the run cannot end", ROUTES_AGAIN)
    for name in routes.named(given):
        _, lines = agent_lines(root, name, ROUTES_AGAIN)
        bare = [line.rstrip("\n") for line in lines]
        if name == lead and step.span(bare, given["step"]) is None:
            raise wrong(
                f"gives step {given['step']}, which the Steps of {lead} do not have", ROUTES_AGAIN
            )
        tools = template.value(bare, "tools")
        named = [t.strip() for t in tools.split(",")] if tools is not None else ["Agent"]
        if name == lead and not any(t == "Agent" or t.startswith("Agent(") for t in named):
            raise wrong(
                f"gives {lead} as the orchestrator, whose file names its tools without Agent,"
                " which it starts each subagent with",
                ROUTES_AGAIN,
            )
        if template.value(bare, "background") == "true":
            raise wrong(
                f"gives {name}, whose file sets `background: true`, so Claude Code would not tell"
                f" {lead} it ended",
                ROUTES_AGAIN,
            )
        if name in froms and step.last(bare) is None:
            raise wrong(f"gives {name}, whose file has no step to end by its result", ROUTES_AGAIN)
    return given


def subagent(root: str, given: dict[str, Any]) -> dict[str, Any]:
    """A subagent of the proposal, held to its schema, checked, with its file and its lines, and
    each step with where it is among them."""
    name = given["name"]
    if "adapter" in given:
        raise not_yet(f"an adapter for {name}")
    file, lines = agent_lines(root, name)
    numbers: list[int] = []
    for s in given["steps"]:
        number = s["step"]
        # A step given twice would be printed as two readings of it and written with the sentences
        # of one, so the step would say what no print showed.
        if number in numbers:
            raise wrong(f"gives step {number} of {name} twice, where each step comes once")
        numbers.append(number)
        where = step.span([line.rstrip("\n") for line in lines], number)
        if where is None:
            raise wrong(f"gives step {number}, which the Steps of {name} do not have")
        for lane in s["lanes"]:
            lane_check(lane, f"step {number} of {name}")
        s["span"] = where
    return {"name": name, "file": file, "lines": lines, "steps": given["steps"]}


def lane_check(lane: dict[str, Any], on: str) -> None:
    """Stops where the lane, held to its schema, on the step `on` names, is one this version does
    not lay, names an adapter, takes a thing given for each run, or takes nothing or an empty
    thing."""
    kind, takes = lane["lane"], lane["takes"]
    if kind not in lanes.LANES:
        raise not_yet(f"{kind} on {on}")
    if "adapter" in lane:
        raise not_yet(f"an adapter on {on}")
    given = [t for t in takes if GIVEN.fullmatch(t)]
    if given:
        raise not_yet(f"`{given[0]}`, given for each run, on {on}")
    if not takes:
        raise wrong(f"gives {kind} on {on} with no take")
    if not all(takes):
        raise wrong(f"gives {kind} on {on} with a take that is empty")
