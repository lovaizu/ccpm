"""The rules laid in a plugin's hooks/lanes.json: the form lay.py write writes them in, and the
reading the guard takes them by."""

from __future__ import annotations

import json
import os
from typing import Any

from domain.lanes import TYPES

NAME = "hooks/lanes.json"


def _in_form(data: Any) -> bool:
    """Whether the data is the rules in the form `laid` gives: the plugin, and each role's steps,
    each with its number and its rules of a known type and their takes."""
    if not isinstance(data, dict) or not isinstance(data.get("plugin"), str):
        return False
    roles = data.get("subagents")
    if not isinstance(roles, dict):
        return False
    for role in roles.values():
        if not isinstance(role, dict) or not isinstance(role.get("steps"), list):
            return False
        for step in role["steps"]:
            if not isinstance(step, dict) or not isinstance(step.get("step"), int):
                return False
            lanes = step.get("lanes")
            if not isinstance(lanes, list) or not all(
                isinstance(lane, dict)
                and lane.get("lane") in TYPES
                and isinstance(lane.get("takes"), list)
                and all(isinstance(each, str) for each in lane["takes"])
                for lane in lanes
            ):
                return False
    return True


def laid(plugin: str, roles: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    """The rules to write into hooks/lanes.json: each role's steps as the proposal gives them."""
    return {
        "plugin": plugin,
        "subagents": {name: {"steps": steps} for name, steps in roles.items()},
    }


def read(hooks: str) -> dict[str, Any] | str:  # pragma: no mutate
    """The rules in the folder `hooks`, or a text that says why they can't serve."""
    path = os.path.join(hooks, "lanes.json")
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return f"{NAME} isn't there"
    except OSError as error:
        return f"{NAME} can't be opened ({error.strerror})"
    try:
        data = json.loads(text)
    except ValueError:
        return f"{NAME} isn't JSON"
    return data if _in_form(data) else f"{NAME} isn't in the form lay.py write writes"
