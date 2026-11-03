"""The rules laid in a plugin, kept in its hooks/lanes.json in the shape of the proposal's
subagents and its routes: written by `lay.py write` and read by the guard and the result script, so
what runs is what was approved; and what every part of lane shares about a plugin's hooks, the
names a hook's command carries and the seconds Claude Code gives each hook."""

from __future__ import annotations

import json
import os
import re
from typing import Any, NamedTuple

import lanes
import routes
import schema

# A plugin's or a subagent's name, as a hook's command carries it unquoted.
NAME = r"[A-Za-z0-9._-]+"
# The seconds Claude Code gives each hook lane lays before it stops it, as lay.py writes it in the
# hook's entry.
TIMEOUT = 10
# Where the rules lie in a plugin.
FILE = os.path.join("hooks", "lanes.json")


def subagents(
    named: list[str], takes: dict[str, Any], least: int, adapters: bool
) -> dict[str, Any]:
    """The JSON Schema of the subagents a proposal gives and hooks/lanes.json holds, at least
    `least` of them: each by its name, each step its lanes are laid on, by its number, and each
    lane, one of those named, with what it takes, as `takes` holds it; where `adapters`, as a
    proposal gives them, the adapter a lane or a subagent may name."""

    def adapter(port: str) -> dict[str, Any]:
        return {"adapter": {"type": "string", "description": f"hooks/adapters/{port}-<name>.py"}}

    lane = {"lane": {"enum": named}, "takes": takes, **(adapter("<port>") if adapters else {})}
    step = {
        "step": {"type": "integer", "description": "its number in the subagent's Steps"},
        "lanes": {"type": "array", "minItems": 1, "items": shape(["lane", "takes"], lane)},
    }
    agent = {
        "name": {"type": "string", "description": "the subagent, as its file's name: field"},
        **(adapter("values") if adapters else {}),
        "steps": {"type": "array", "minItems": 1, "items": shape(["step", "lanes"], step)},
    }
    return {"type": "array", "minItems": least, "items": shape(["name", "steps"], agent)}


def shape(required: list[str], properties: dict[str, Any]) -> dict[str, Any]:
    """The JSON Schema of an object of the properties, those required among them, and no other."""
    return {
        "type": "object",
        "required": required,
        "additionalProperties": False,
        "properties": properties,
    }


# The routes' JSON Schema, as docs/routes.md gives it: the orchestrator, its step they are laid
# on, and each route from a subagent, on its result, to the subagent started next.
ROUTE = {
    "from": {
        "type": "string",
        "description": "the subagent that ends, or the orchestrator for the first start",
    },
    "on": {
        "type": "string",
        "pattern": "^[a-z][a-z0-9_-]*$",
        "description": "the result it ends with",
    },
    "to": {"type": "string", "description": "the subagent to start next; none where the run ends"},
}
ROUTES = shape(
    ["orchestrator", "step", "routes"],
    {
        "orchestrator": {
            "type": "string",
            "description": "the subagent that starts the others, as its file's name: field",
        },
        "step": {
            "type": "integer",
            "minimum": 1,
            "description": "the orchestrator's step the routes are laid on",
        },
        "routes": {"type": "array", "minItems": 2, "items": shape(["from"], ROUTE)},
    },
)
# hooks/lanes.json's JSON Schema: the subagents with lanes laid, none once every one is gone, each
# lane one lane lays, taking at least one thing, none of them empty, with the adapters approved; and
# the routes, where any are laid.
TAKEN = {"type": "array", "items": {"type": "string", "minLength": 1}, "minItems": 1}
# No list is shorter than none, nor than fewer.
NONE_LEFT = 0  # pragma: no mutate
SHAPE = shape(
    ["subagents"],
    {"subagents": subagents(list(lanes.LANES), TAKEN, NONE_LEFT, True), "routes": ROUTES},
)
# The result a subagent with a lane checked at its end gives where no route is from it.
DONE = "done"
# A thing given for each run: a name in braces, the braces wrapping the whole take.
GIVEN = re.compile(r"\{[^{}]+\}")


class Laid(NamedTuple):
    """A lane laid in a subagent: its step, the lane, what it takes, and the adapter it reads its
    port by, where it names one."""

    step: int
    lane: str
    takes: list[str]
    adapter: str | None = None


def read(root: str) -> dict[str, Any]:
    """The rules laid in the plugin at root, as its hooks/lanes.json holds them; stops with
    ValueError saying what is wrong where it is not there, holds no JSON, or is out of SHAPE."""
    try:
        with open(os.path.join(root, FILE), encoding="utf-8") as f:
            given = json.load(f)
    except OSError:
        raise ValueError(f"{FILE} is not there") from None
    except ValueError:
        raise ValueError(f"{FILE} holds no JSON") from None
    out = schema.held(SHAPE, given)
    if out is not None:
        raise ValueError(f"{FILE} is out of its shape at {out.told()}")
    return given


def of(laid: dict[str, Any], name: str) -> list[Laid] | None:
    """Each lane laid in the subagent of the name, of the rules `read` gives, in the order of its
    steps; None where none is laid in it."""
    found = next((a for a in laid["subagents"] if a["name"] == name), None)
    if found is None:
        return None
    return [
        Laid(s["step"], g["lane"], g["takes"], g.get("adapter"))
        for s in found["steps"]
        for g in s["lanes"]
    ]


def adapter_of(laid: dict[str, Any], name: str) -> str | None:
    """The values adapter of the subagent of the name, of the rules `read` gives; None where it
    names none."""
    found = next((a for a in laid["subagents"] if a["name"] == name), {})
    return found.get("adapter")


def gives(routed: dict[str, Any] | None, name: str, kinds: list[str]) -> list[str]:
    """The results the subagent of the name gives, its lanes being of the kinds: those the routes
    from it are on, or DONE where none is and one of its lanes is checked at its end."""
    ons = routes.ons(routed, name) if routed else []
    return ons or ([DONE] if any(map(lanes.ends, kinds)) else [])


def routes_of(laid: dict[str, Any]) -> dict[str, Any] | None:
    """The routes laid, of the rules `read` gives; None where none are."""
    return laid.get("routes")


def write(root: str, subagents: list[dict[str, Any]], routes: dict[str, Any] | None = None) -> None:
    """Writes the lanes of the subagents, each as a proposal gives it, its name and its steps, and
    the routes where any are given, into the plugin's hooks/lanes.json, indented by two for whoever
    reads it."""
    given = {"subagents": subagents, **({"routes": routes} if routes else {})}
    os.makedirs(os.path.join(root, "hooks"), exist_ok=True)
    with open(os.path.join(root, FILE), "w", encoding="utf-8") as f:
        f.write(json.dumps(given, indent=2, ensure_ascii=False) + "\n")
