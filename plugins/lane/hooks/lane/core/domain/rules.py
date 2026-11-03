"""The rules laid in a plugin, kept in its hooks/lanes.json in the shape of the proposal's
subagents: written by `lay.py write` and read by the guard, so what runs is what was approved; and
what every part of lane shares about a plugin's hooks, the names a hook's command carries and the
seconds Claude Code gives each hook."""

from __future__ import annotations

import json
import os
from typing import Any, NamedTuple

import lanes
import schema

# A plugin's or a subagent's name, as a hook's command carries it unquoted.
NAME = r"[A-Za-z0-9._-]+"
# The seconds Claude Code gives each hook lane lays before it stops it, as lay.py writes it in the
# hook's entry.
TIMEOUT = 10
# Where the rules lie in a plugin.
FILE = os.path.join("hooks", "lanes.json")
# hooks/lanes.json's JSON Schema: each subagent by its name, each step its lanes are laid on, by its
# number, and each lane, one lane lays, with what it takes, none of it empty.
LANE = {
    "type": "object",
    "required": ["lane", "takes"],
    "additionalProperties": False,
    "properties": {
        "lane": {"enum": list(lanes.LANES)},
        "takes": {"type": "array", "items": {"type": "string", "minLength": 1}, "minItems": 1},
    },
}
STEP = {
    "type": "object",
    "required": ["step", "lanes"],
    "additionalProperties": False,
    "properties": {
        "step": {"type": "integer", "minimum": 1},
        "lanes": {"type": "array", "items": LANE, "minItems": 1},
    },
}
SUBAGENT = {
    "type": "object",
    "required": ["name", "steps"],
    "additionalProperties": False,
    "properties": {
        "name": {"type": "string"},
        "steps": {"type": "array", "items": STEP, "minItems": 1},
    },
}
SHAPE = {
    "type": "object",
    "required": ["subagents"],
    "additionalProperties": False,
    "properties": {"subagents": {"type": "array", "items": SUBAGENT}},
}


class Laid(NamedTuple):
    """A lane laid in a subagent: its step, the lane, and what it takes."""

    step: int
    lane: str
    takes: list[str]


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
    return [Laid(s["step"], g["lane"], g["takes"]) for s in found["steps"] for g in s["lanes"]]


def write(root: str, subagents: list[dict[str, Any]]) -> None:
    """Writes the lanes of the subagents, each as a proposal gives it, its name and its steps, into
    the plugin's hooks/lanes.json, indented by two for whoever reads it."""
    os.makedirs(os.path.join(root, "hooks"), exist_ok=True)
    with open(os.path.join(root, FILE), "w", encoding="utf-8") as f:
        f.write(json.dumps({"subagents": subagents}, indent=2, ensure_ascii=False) + "\n")
