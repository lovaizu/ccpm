"""Each port lane reads a plugin's text at: the values a subagent started from, the items of an
input and the move a script printed. Each is defined once, here, by the JSON it is given and the
JSON it gives back, a JSON Schema each, as docs/lanes.md shows them, and read by lane's one reading
of it; so each lane checks only what lanes.md defines it to take, and knows no plugin's form.

- `values`: given `{"texts": [<the prompt>, <each print of a start_with script>]}`, gives
  `{"values": {"<name>": ["<text>", ...]}}`: the value under each name in the JSON objects the texts
  hold, the later over the earlier, a list standing for each of its texts, a text for itself; a
  value of another kind gives nothing.
- `items`: given `{"input": "<path>", "text": "<its text>"}`, gives `{"items": ["<ID>", ...]}`: the
  ID each top-level item of a Markdown list in the text begins with.
- `move`: given `{"output": "<what the script printed>"}`, gives
  `{"move": {"tool": "...", "input": {...}}}` or `{"move": null}`: the last JSON object the output
  holds that names a tool and an input object, the tool call itself.

A plugin whose text is in another form has an adapter of the port, a Python 3 script given the
port's JSON on stdin and giving its JSON on stdout, which `run` runs in place of lane's reading,
within the hook's time, holding what it gives to the port."""

from __future__ import annotations

import json
import re
import subprocess
import time
from typing import Any, Callable

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


# A move, the tool call itself: a tool's name and its input.
MOVE = shape(tool=TEXT, input={"type": "object"})
# Each port, by its name: the JSON it is given, "in", and the JSON it gives back, "out".
PORTS: dict[str, dict[str, dict[str, Any]]] = {
    "values": {
        "in": shape(texts=TEXTS),
        "out": shape(values={"type": "object", "additionalProperties": TEXTS}),
    },
    "items": {"in": shape(input=TEXT, text=TEXT), "out": shape(items=TEXTS)},
    "move": {
        "in": shape(output=TEXT),
        "out": shape(move={"anyOf": [{"type": "null"}, MOVE]}),
    },
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
    texts give, the later over the earlier, as the texts it stands for."""
    merged: dict[str, Any] = {}
    for text in given["texts"]:
        for found in objects(text):
            merged.update(found)
    each = {name: texts_of(value) for name, value in merged.items()}
    return {"values": {name: value for name, value in each.items() if value is not None}}


def items(given: dict[str, Any]) -> dict[str, Any]:
    """lane's reading of the items port: the ID each top-level item of a Markdown list in the text
    begins with, in order."""
    return {"items": ITEM.findall(given["text"])}


def move(given: dict[str, Any]) -> dict[str, Any]:
    """lane's reading of the move port: the move the script printed, None where it printed none."""
    found = printed(given["output"])
    return {"move": None if found is None else {"tool": found[0], "input": found[1]}}


def printed(output: str) -> tuple[str, dict[str, Any]] | None:
    """The move in what the script printed: the last JSON object it printed, as `objects` finds
    them, that holds a tool's name and an input object; None where none does."""
    for found in reversed(objects(output)):
        tool, given = found.get("tool"), found.get("input")
        if isinstance(tool, str) and isinstance(given, dict):
            return tool, given
    return None


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
    """The texts a value stands for: a text itself, a list its texts; None for a value of another
    kind, which gives a lane nothing to hold to."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [v for v in value if isinstance(v, str)]
    return None


# lane's one reading of each port, by its name.
OWN: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "values": values,
    "items": items,
    "move": move,
}


def read(port: str, given: dict[str, Any]) -> dict[str, Any]:
    """What the port gives back, given its JSON, by lane's reading of it."""
    return OWN[port](given)


# The seconds the hook leaves its adapters, of the 10 Claude Code gives it, counted from when lane's
# code was loaded, the rest for Python to start and the subagent's record to be read.
TIME = 8.0
START = time.monotonic()


class Failed(Exception):
    """What an adapter did that is not as its port says."""


def run(path: str, port: str, given: dict[str, Any], left: float | None = None) -> dict[str, Any]:
    """What the port gives back, given its JSON, by the adapter at the path, run with python3 on the
    port's JSON within the seconds left, or what is left of TIME where none are given; stops with
    Failed saying what the adapter did where it exits other than 0, gives no answer in that time,
    prints no JSON, or answers out of the port."""
    if left is None:
        left = max(TIME - (time.monotonic() - START), 0)
    try:
        done = subprocess.run(
            ["python3", path],
            input=json.dumps(given),
            capture_output=True,
            text=True,
            timeout=left,
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
