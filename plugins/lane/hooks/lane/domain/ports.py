"""Each port lane reads a plugin's text at: the values a subagent is given and the items of an
input. Each is defined once, here, by the JSON it is given and the
JSON it gives back, a JSON Schema each, as docs/lanes.md shows them, and read by lane's one reading
of it; so each lane checks only what lanes.md defines it to take, and knows no plugin's form.

- `values`: given `{"texts": [<the prompt>, <each print of a start_with script and each message
  sent to the subagent after>]}`, in the order its record holds them, as started.py reads them,
  gives `{"values": {"<name>": ["<text>", ...] or null}}`: the value under each name in the JSON
  objects the texts hold, the later over the earlier, a list standing for each of its texts, a
  text for itself, null for null, the caller saying there is none; a value of another kind gives
  nothing.
- `items`: given `{"input": "<path>", "text": "<its text>", "values": {<the start's values>}}`,
  gives `{"items": ["<ID>", ...]}`: the ID each top-level item of a Markdown list in the text
  begins with. An adapter may read the items from elsewhere by the start's values, such as the
  nodes a change to a design tree touches; lane's reading reads the text alone.

A plugin whose text is in another form has an adapter of the port, a Python 3 script given the
port's JSON on stdin and giving its JSON on stdout, which `run` runs in place of lane's reading,
within the hook's time, holding what it gives to the port."""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
from typing import Any, Callable

import rules
import schema

# What reads a port for a lane, given the port's JSON, giving back the port's.
Port = Callable[[dict[str, Any]], dict[str, Any]]
# A text, and texts, as a port's JSON holds them.
TEXT = {"type": "string"}
TEXTS = {"type": "array", "items": TEXT}


def shape(**fields: dict[str, Any]) -> dict[str, Any]:
    """The schema of a JSON object holding each of the fields, of its schema, and no other."""
    return {
        "type": "object",
        "required": list(fields),
        "additionalProperties": False,
        "properties": fields,
    }


# A run's value, its texts or null, the caller saying there is none, as OpenAPI 3.1 writes a value
# that may be null.
VALUE = {**TEXTS, "type": ["array", "null"]}
# A start's values, by their names, as the values port gives them.
VALUES = {"type": "object", "additionalProperties": VALUE}
# Each port, by its name: the JSON it is given, "in", and the JSON it gives back, "out".
PORTS: dict[str, dict[str, dict[str, Any]]] = {
    "values": {"in": shape(texts=TEXTS), "out": shape(values=VALUES)},
    "items": {"in": shape(input=TEXT, text=TEXT, values=VALUES), "out": shape(items=TEXTS)},
}
# A top-level list item, its marker at the line's start, and the ID it begins with: capitals, a
# hyphen or not, a number, and numbers after a point, set in Markdown's bold, code or brackets or
# not, and followed by a colon, a point, a bracket, a blank or the line's end.
ITEM = re.compile(
    r"^(?:[-*+]|[0-9]+[.)])[ \t]+[*_`\[]*(?P<key>[A-Z][A-Za-z]*-?[0-9]+(?:\.[0-9]+)*)"
    r"[*_`\]]*(?=[:.)\s]|$)",
    re.MULTILINE,
)


def values(given: dict[str, Any]) -> dict[str, Any]:
    """lane's reading of the values port: the run's value of each name the JSON objects in the
    texts give, the later over the earlier, as the texts it stands for, or null for null."""
    merged: dict[str, Any] = {}
    for text in given["texts"]:
        for found in objects(text):
            merged.update(found)
    each = {name: texts_of(value) for name, value in merged.items()}
    return {"values": {n: v for n, v in each.items() if v is not None or merged[n] is None}}


def items(given: dict[str, Any]) -> dict[str, Any]:
    """lane's reading of the items port: the ID each top-level item of a Markdown list in the text
    begins with, in order."""
    return {"items": ITEM.findall(given["text"])}


def objects(text: str) -> list[dict[str, Any]]:
    """The JSON objects the text holds: the text itself where it is one JSON value, however many
    lines it is printed over; otherwise each line that is one, as a script may print lines of its
    own before it."""
    try:
        each = [json.loads(text)]
    except ValueError:
        each = [loaded(line) for line in text.splitlines()]
    return [o for o in each if isinstance(o, dict)]


def loaded(line: str) -> Any:
    """The JSON value the line is; None where it is none."""
    try:
        return json.loads(line)
    except ValueError:
        return None


def texts_of(value: Any) -> list[str] | None:
    """The texts a value stands for: a text itself, a list its texts; None for null, and for a value
    of another kind, which gives a lane nothing to hold to."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [v for v in value if isinstance(v, str)]
    return None


# lane's one reading of each port, by its name.
OWN: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "values": values,
    "items": items,
}


def read(port: str, given: dict[str, Any]) -> dict[str, Any]:
    """What the port gives back, given its JSON, by lane's reading of it."""
    return OWN[port](given)


# The seconds the hook leaves its adapters, of those Claude Code gives it, counted from when the
# guard began on the event, the rest for Python to start and the event to be read.
TIME = rules.TIMEOUT - 2.0


def left(start: float) -> float:
    """The seconds left of TIME for an event the guard began on at start, a time of
    time.monotonic; none once they are spent. Counted from the event, not from when lane's code was
    loaded, so it holds in a process that handles many events, as the tests do."""
    return max(TIME - (time.monotonic() - start), 0)


class Failed(Exception):
    """What an adapter did that is not as its port says."""


def run(path: str, port: str, given: dict[str, Any], root: str, seconds: float) -> dict[str, Any]:
    """What the port gives back, given its JSON, by the adapter at the path, run with python3 on the
    port's JSON within the seconds given, with
    CLAUDE_PLUGIN_ROOT the folder of the plugin at root, as Claude Code gives it a hook, so the
    adapter finds the plugin's files wherever it is, beside a proposal or in the plugin; stops with
    Failed saying what the adapter did where it exits other than 0, gives no answer in that time,
    prints no JSON, or answers out of the port."""
    try:
        done = subprocess.run(
            ["python3", path],
            input=json.dumps(given),
            env={**os.environ, "CLAUDE_PLUGIN_ROOT": root},
            capture_output=True,
            text=True,
            timeout=seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        raise Failed(f"gave no answer within the {TIME:g} seconds the hook leaves it") from None
    if done.returncode:
        last = (done.stderr.strip().splitlines() or [""])[-1]
        raise Failed(f"exited {done.returncode}: {last}")
    try:
        found = json.loads(done.stdout)
    except ValueError:
        raise Failed(f"printed no JSON: {schema.shown(done.stdout)}") from None
    out = schema.held(PORTS[port]["out"], found)
    if out is not None:
        raise Failed(f"answered out of the {port} port at {out.told()}")
    return found
