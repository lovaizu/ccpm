"""Decides the form of the lanes and routes that the user approves: the proposal, and
`hooks/lanes.json`, which `lay.py write` writes from it and the guard reads. Lane holds both to
the proposal's JSON Schema, which plugins/lane/docs/lanes.md gives, and to the checks of lanes/
that tell whether each lane can stand.
"""

from __future__ import annotations

import json
import os
from typing import Any, NamedTuple

import lanes
import routes
import schema
import step

# The form of a role's lanes, as the proposal gives them.
SUBAGENT = {
    "type": "object",
    "required": ["name", "steps"],
    "additionalProperties": False,
    "properties": {
        "name": {"type": "string"},
        "adapter": {"type": "string"},
        "steps_adapter": {"type": "string"},
        "results": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "pattern": "^[a-z][a-z0-9_-]*$"},
        },
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["step", "lanes"],
                "additionalProperties": False,
                "properties": {
                    "step": {"type": "integer"},
                    "lanes": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "object",
                            "required": ["lane", "takes"],
                            "additionalProperties": False,
                            "properties": {
                                "lane": {"enum": list(lanes.PROPOSED)},
                                "takes": {"type": "array", "items": {"type": "string"}},
                                "adapter": {"type": "string"},
                            },
                        },
                    },
                },
            },
        },
    },
}
# The form of `hooks/lanes.json`: the proposal without the plugin's folder.
LAID = {
    "type": "object",
    "additionalProperties": False,
    "anyOf": [{"required": ["subagents"]}, {"required": ["routes"]}],
    "properties": {
        "routes": {"type": "object"},
        "subagents": {"type": "array", "minItems": 1, "items": SUBAGENT},
    },
}
# The form of a proposal.
PROPOSAL = {
    **LAID,
    "required": ["plugin"],
    "properties": {**LAID["properties"], "plugin": {"type": "string"}},
}
# The lanes that read a port given by an adapter that the lane names.
PORTED = ("every_item",)


class Unlaid(ValueError):
    """Lanes laid that the guard can't read, with what's wrong."""


class Lane(NamedTuple):
    """One lane on a step of a role."""

    # The number of the step it's on.
    step: int
    # The name of its type.
    lane: str
    # What it takes, as the proposal writes it.
    takes: tuple[str, ...]
    # The path in the plugin of the adapter of the port it reads, or None.
    adapter: str | None


class Role(NamedTuple):
    """A role's lanes, as the proposal gives them."""

    # The role's name.
    name: str
    # Each lane on each of its steps, in the order the proposal gives them.
    lanes: tuple[Lane, ...]
    # The path in the plugin of its values adapter, or None.
    adapter: str | None
    # The path in the plugin of its steps adapter, or None.
    steps_adapter: str | None
    # The results it gives where no route is from it, or None.
    results: tuple[str, ...] | None


class Said(NamedTuple):
    """A sentence that the lanes and routes lay in a role's or the skill's steps."""

    # The number of the step that the sentence ends, or None where no step says it.
    step: int | None
    # The type of lane that the sentence says, follow_routes for the routes' sentence, or end_by
    # for the result sentence.
    lane: str
    # What the sentence takes.
    takes: list[str]


class Laid(NamedTuple):
    """The lanes and routes, as the proposal or `hooks/lanes.json` gives them."""

    # Each role with lanes.
    roles: tuple[Role, ...]
    # The routes, or None where the JSON gives none.
    routes: routes.Routes | None
    # The JSON, as `lay.py write` writes it into `hooks/lanes.json`.
    data: dict[str, Any]

    def role(self, name: str) -> Role | None:
        """The role of the name, or None where no role has it."""
        return next((r for r in self.roles if r.name == name), None)


def unheld(data: Any, form: dict[str, Any]) -> str | None:
    """Where the JSON is out of the form of `hooks/lanes.json` or of a proposal, or its routes out
    of theirs, such as `its form: $.subagents: expected an array, found 1`, or None where it
    holds."""
    out = schema.held(form, data)
    if out:
        return f"its form: {out.told()}"
    out = schema.held(routes.SCHEMA, data["routes"]) if "routes" in data else None
    return f"the form of the routes: {out.told()}" if out else None


def parsed(data: dict[str, Any]) -> Laid:
    """The lanes and routes in the JSON, of which `unheld` finds nothing out of its form."""
    roles = []
    for given in data.get("subagents", []):
        found = tuple(
            Lane(s["step"], g["lane"], tuple(g["takes"]), g.get("adapter"))
            for s in given["steps"]
            for g in s["lanes"]
        )
        results = tuple(given["results"]) if "results" in given else None
        roles.append(
            Role(given["name"], found, given.get("adapter"), given.get("steps_adapter"), results)
        )
    laid = {k: v for k, v in data.items() if k != "plugin"}
    given = routes.parsed(data["routes"]) if "routes" in data else None
    return Laid(tuple(roles), given, laid)


def faults(found: Laid) -> list[str]:
    """What keeps the lanes and routes from standing, none where each can stand."""
    shown = []
    if found.routes is not None:
        shown += routes.faults(found.routes)
        for role in found.roles:
            if role.results is not None and routes.results(found.routes, role.name) is not None:
                shown.append(
                    f"{role.name} names its results, and the routes are from it, which give its"
                    " results"
                )
    names = [r.name for r in found.roles]
    for name in dict.fromkeys(n for n in names if names.count(n) > 1):
        shown.append(f"{name} is given twice")
    for role, given in zip(found.roles, found.data.get("subagents", [])):
        steps = [s["step"] for s in given["steps"]]
        for number in dict.fromkeys(s for s in steps if steps.count(s) > 1):
            shown.append(f"{role.name} gives step {number} twice")
        for lane in role.lanes:
            where = f"step {lane.step} of {role.name}"
            shown += [f"{where}: {f}" for f in lanes.stands(lane.lane, list(lane.takes))]
            if lane.adapter is not None and lane.lane not in PORTED:
                shown.append(f"{where}: {lane.lane} reads no port, so it takes no adapter")
    return shown


def sentences(found: Laid, name: str, steps: list[step.Step]) -> list[Said]:
    """Each sentence that the lanes and routes lay in the steps of the role or the skill of the
    name, whose part holds the steps given: the role's lanes' sentences, the routes' sentence on
    the skill's step, and the result sentence on the last step. A part with no numbered list says
    none of them."""
    role = found.role(name)
    said = [Said(lane.step, lane.lane, list(lane.takes)) for lane in role.lanes] if role else []
    if found.routes is not None and found.routes.orchestrator == name:
        said.append(Said(found.routes.step, "follow_routes", []))
    commands = routes.result_commands(found, name)
    if commands:
        said.append(Said(steps[-1].number if steps else None, "end_by", commands))
    if not steps:
        said = [Said(None, s.lane, s.takes) for s in said]
    return said


def read(root: str) -> Laid:
    """The lanes and routes laid in the plugin at the root, in `hooks/lanes.json`.

    It raises Unlaid where the file is missing, isn't JSON, is out of its form, or holds a lane that
    can't stand.
    """
    path = os.path.join(root, "hooks", "lanes.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise Unlaid(f"{root} holds no hooks/lanes.json") from None
    except json.JSONDecodeError as why:
        raise Unlaid(f"{path} is no JSON: {why}") from None
    out = unheld(data, LAID)
    if out:
        raise Unlaid(f"{path} is out of {out}")
    found = parsed(data)
    shown = faults(found)
    if shown:
        raise Unlaid(f"{path}: {'; '.join(shown)}")
    return found
