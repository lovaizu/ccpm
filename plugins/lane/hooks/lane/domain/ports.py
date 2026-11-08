"""Decides how a text of the plugin becomes the form in which a check takes it, at the values,
items, and steps ports, as plugins/lane/docs/lanes.md gives the ports.

Lane reads its own form at the values and items ports. Where the plugin names an adapter, Lane runs
it instead: a Python 3 script that takes the port's JSON on standard input and prints the port's
JSON. An adapter lies in the plugin at `hooks/adapters/<port>-<name>.py`, its cases beside it at
`<port>-<name>.json`.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from typing import Any

import schema
from lanes import every_item

# The most seconds an adapter runs, within the hook's time.
TIMEOUT = 5.0
# The values of a start, by name: a list of texts, or null.
VALUES = {
    "type": "object",
    "additionalProperties": {"type": ["array", "null"], "items": {"type": "string"}},
}
# A lane of the trace kind on a step that the steps port gives.
TRACE = {
    "type": "object",
    "required": ["lane", "takes"],
    "additionalProperties": False,
    "properties": {
        "lane": {"enum": ["read_whole", "run_step", "write_step"]},
        "takes": {"type": "array", "minItems": 1, "items": {"type": "string"}},
    },
}
# A step that the steps port gives: what it says, and the lanes of its trace.
STEP = {
    "type": "object",
    "required": ["says", "lanes"],
    "additionalProperties": False,
    "properties": {"says": {"type": "string"}, "lanes": {"type": "array", "items": TRACE}},
}
# A step list that the steps port gives.
LIST = {
    "type": "object",
    "required": ["list", "steps"],
    "additionalProperties": False,
    "properties": {"list": {"type": "string"}, "steps": {"type": "array", "items": STEP}},
}
# Each port's JSON in and out, as plugins/lane/docs/lanes.md gives them.
PORTS: dict[str, dict[str, Any]] = {
    "values": {
        "in": {
            "type": "object",
            "required": ["texts"],
            "additionalProperties": False,
            "properties": {"texts": {"type": "array", "items": {"type": "string"}}},
        },
        "out": {
            "type": "object",
            "required": ["values"],
            "additionalProperties": False,
            "properties": {"values": VALUES},
        },
    },
    "items": {
        "in": {
            "type": "object",
            "required": ["input", "text", "values"],
            "additionalProperties": False,
            "properties": {
                "input": {"type": "string"},
                "text": {"type": "string"},
                "values": VALUES,
            },
        },
        "out": {
            "type": "object",
            "required": ["items"],
            "additionalProperties": False,
            "properties": {"items": {"type": "array", "items": {"type": "string"}}},
        },
    },
    "steps": {
        "in": {
            "type": "object",
            "required": ["values"],
            "additionalProperties": False,
            "properties": {"values": VALUES},
        },
        "out": {
            "type": "object",
            "required": ["lists"],
            "additionalProperties": False,
            "properties": {"lists": {"type": "array", "items": LIST}},
        },
    },
}
# What gives nothing at each port, which a set of cases holds once.
NOTHING = {"values": {"values": {}}, "items": {"items": []}, "steps": {"lists": []}}
# An adapter's path in the plugin, with its port.
ADAPTER = re.compile(r"hooks/adapters/(values|items|steps)-[^/]+\.py")


class Unported(ValueError):
    """A port that Lane can't read, with what's wrong."""


def values(texts: list[str], root: str = "", adapter: str | None = None) -> dict[str, Any]:
    """The values of a start, from the texts that the start holds, its prompt first.

    Lane's own form reads each JSON object that a text is, or that a line of a text is, the later
    over the earlier: a list of texts for itself, a text as a list of it, and null for itself. It
    raises Unported where the adapter fails.
    """
    if adapter is not None:
        return run(root, adapter, "values", {"texts": texts})["values"]
    found: dict[str, Any] = {}
    for text in texts:
        for chunk in [text, *text.splitlines()]:
            try:
                data = json.loads(chunk)
            except ValueError:
                continue
            if isinstance(data, dict):
                found.update({k: v for k, v in map(_value, data.items()) if k is not None})
    return found


def _value(item: tuple[str, Any]) -> tuple[str | None, Any]:
    """The value in Lane's form, or a None name where the value is of no type that Lane reads."""
    name, given = item
    if given is None:
        return name, None
    if isinstance(given, str):
        return name, [given]
    if isinstance(given, list) and all(isinstance(t, str) for t in given):
        return name, given
    return None, None


def items(
    path: str, text: str, given: dict[str, Any], root: str = "", adapter: str | None = None
) -> list[str]:
    """The items of the input at the path, from its text. It raises Unported where the adapter
    fails."""
    if adapter is None:
        return every_item.items(text)
    return run(root, adapter, "items", {"input": path, "text": text, "values": given})["items"]


def steps(given: dict[str, Any], root: str, adapter: str) -> list[dict[str, Any]]:
    """The step lists that the steps adapter gives for the start's values. It raises Unported where
    the adapter fails."""
    return run(root, adapter, "steps", {"values": given})["lists"]


def run(
    root: str,
    adapter: str,
    port: str,
    given: Any,
    timeout: float = TIMEOUT,
    script: str | None = None,
) -> Any:
    """What the adapter at its path in the plugin prints for the port's JSON given, held to the
    port's JSON out. script names the file to run where it lies elsewhere than in the plugin.

    It raises Unported where the adapter isn't there, fails, gives no answer in time, or answers
    out of the port.
    """
    path = script or os.path.join(root, adapter)
    if not os.path.isfile(path):
        raise Unported(f"{adapter} isn't there")
    env = {**os.environ, "CLAUDE_PLUGIN_ROOT": root}
    try:
        done = subprocess.run(
            [sys.executable, path],
            input=json.dumps(given),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            check=False,
        )
    except subprocess.TimeoutExpired:
        raise Unported(f"{adapter} gave no answer within {timeout} seconds") from None
    if done.returncode != 0:
        raise Unported(f"{adapter} exited with {done.returncode}: {done.stderr.strip()}")
    try:
        out = json.loads(done.stdout)
    except ValueError as why:
        raise Unported(f"{adapter} gave no JSON: {why}") from None
    point = schema.held(PORTS[port]["out"], out)
    if point:
        raise Unported(f"{adapter} answered out of the {port} port: {point.told()}")
    return out


def tried(
    root: str, adapter: str, folder: str | None = None
) -> tuple[list[tuple[Any, Any]], list[str]]:
    """What the adapter gives for each of its cases, and each fault of the cases: a case it gives
    otherwise, no case that gives nothing, or cases that aren't there or are out of their form.
    folder names where the adapter and its cases lie, where it's elsewhere than the plugin's
    `hooks/adapters/`."""
    found = ADAPTER.fullmatch(adapter)
    if found is None:
        return [], [
            (
                f"{adapter} isn't named hooks/adapters/<port>-<name>.py for the values, items or"
                " steps port"
            )
        ]
    port = found[1]
    where = folder or os.path.join(root, "hooks", "adapters")
    script = os.path.join(where, os.path.basename(adapter))
    named = adapter[: -len(".py")] + ".json"
    try:
        with open(os.path.join(where, os.path.basename(named)), encoding="utf-8") as f:
            cases = json.load(f)
    except (OSError, ValueError):
        return [], [f"{named} isn't there, which holds the adapter's cases"]
    case = {
        "type": "object",
        "required": ["given", "gives"],
        "additionalProperties": False,
        "properties": {"given": PORTS[port]["in"], "gives": PORTS[port]["out"]},
    }
    form = {"type": "array", "minItems": 1, "items": case}
    point = schema.held(form, cases)
    if point:
        return [], [f"{named} is out of its form: {point.told()}"]
    shown, faults = [], []
    for number, case in enumerate(cases, 1):
        try:
            gave = run(root, adapter, port, case["given"], script=script)
        except Unported as why:
            faults.append(str(why))
            continue
        shown.append((case["given"], gave))
        if gave != case["gives"]:
            faults.append(
                f"{adapter} gives {json.dumps(gave)} for case {number}, where its cases say"
                f" {json.dumps(case['gives'])}"
            )
    if not any(c["gives"] == NOTHING[port] for c in cases):
        faults.append(f"{named} holds no case that gives nothing")
    return shown, faults
