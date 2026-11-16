"""Decides how rn holds a JSON value to one of its forms, each a JSON Schema beside the code: the
keywords of draft-07 that rn's schemas use, and the one place a value leaves its form, named by its
path from the top, such as `deliverables/0/status`, so that whoever wrote the value can mend it."""

from __future__ import annotations

import json
import os
import re
from collections.abc import Mapping
from typing import Any

from fault import Wrong

# The test of each JSON type, as Python reads JSON, and its name in a message.
_TYPES = {
    "object": (lambda v: isinstance(v, dict), "an object"),
    "array": (lambda v: isinstance(v, list), "an array"),
    "string": (lambda v: isinstance(v, str), "text"),
    "integer": (lambda v: isinstance(v, int) and not isinstance(v, bool), "a whole number"),
    "boolean": (lambda v: isinstance(v, bool), "true or false"),
    "null": (lambda v: v is None, "null"),
}
_DOMAIN = os.path.dirname(os.path.abspath(__file__))


def load(path: str) -> dict[str, Any]:
    """The JSON Schema in the file at the path, from rn's domain/ where it's relative. A form that
    rn ships is never the caller's to mend, so a fault in reading it stops with its trace."""
    with open(os.path.join(_DOMAIN, path), encoding="utf-8") as f:
        return json.load(f)


def hold(value: Any, schema: Mapping[str, Any], named: str) -> None:
    """Holds the value to the schema.

    Takes: the value as Python reads JSON, the schema, and the name of what holds the value, such
    as a file, which the message names first.
    Gives: nothing, where the value keeps its form.
    Raises Wrong, as `<named>: <place>: <what's wrong>`, at the place deepest in the value where it
    leaves its form, the top named as `the top`.
    """
    found = _faults(value, schema, schema, "")
    if found:
        place, what = max(found, key=lambda each: _depth(each[0]))
        raise Wrong(f"{named}: {place or 'the top'}: {what}")


def _faults(value: Any, node: Mapping[str, Any], root: Mapping[str, Any], place: str) -> list:
    """Each place where the value leaves the node of the schema, the deepest first."""
    if "$ref" in node:
        return _faults(value, _resolved(root, node["$ref"]), root, place)
    for branches in (node.get("anyOf"), node.get("oneOf")):
        if branches:
            return _best(value, branches, root, place)
    kind = node.get("type")
    if kind and not _TYPES[kind][0](value):
        return [(place, f"must be {_TYPES[kind][1]}, not {json.dumps(value)[:40]}")]
    return _of_value(value, node, place) or _within(value, node, root, place)


def _best(value: Any, branches: list, root: Mapping[str, Any], place: str) -> list:
    """The faults of the branch the value comes nearest to, the one whose faults lie deepest, or
    none where it keeps one."""
    tried = [_faults(value, each, root, place) for each in branches]
    if any(not each for each in tried):
        return []
    return max(tried, key=lambda each: (max(_depth(p) for p, _ in each), -len(each)))


def _of_value(value: Any, node: Mapping[str, Any], place: str) -> list:
    """The first fault of the value itself, against each keyword of _KEPT that the node holds."""
    for keyword, (keeps, says) in _KEPT.items():
        if keyword in node and not keeps(value, node[keyword]):
            return [(place, says(value, node[keyword]))]
    return []


# Each keyword that holds a value itself: whether the value keeps it, and what's wrong where not.
_KEPT = {
    "enum": (
        lambda v, given: v in given,
        lambda v, given: f"must be one of {', '.join(map(json.dumps, given))}",
    ),
    "const": (lambda v, given: v == given, lambda v, given: f"must be {json.dumps(given)}"),
    "minimum": (lambda v, given: v >= given, lambda v, given: f"must be {given} or more, not {v}"),
    "minLength": (
        lambda v, given: len(v) >= given,
        lambda v, given: f"must hold {given} character or more",
    ),
    "pattern": (
        lambda v, given: re.search(given, v) is not None,
        lambda v, given: f"must match {given}, not {json.dumps(v)}",
    ),
    "minItems": (
        lambda v, given: len(v) >= given,
        lambda v, given: f"must hold {given} item or more",
    ),
}


def _within(value: Any, node: Mapping[str, Any], root: Mapping[str, Any], place: str) -> list:
    """The faults of an object's fields, or of an array's items."""
    if isinstance(value, list) and "items" in node:
        return [
            fault
            for number, each in enumerate(value)
            for fault in _faults(each, node["items"], root, _join(place, str(number)))
        ]
    if not isinstance(value, dict):
        return []
    fields = node.get("properties", {})
    found = [
        (place, f"lacks the field {name}") for name in node.get("required", []) if name not in value
    ]
    closed = node.get("additionalProperties") is False
    found += [
        (place, f"{name} isn't a field it takes") for name in value if closed and name not in fields
    ]
    for name in (name for name in value if name in fields):
        found += _faults(value[name], fields[name], root, _join(place, name))
    return found


def _resolved(root: Mapping[str, Any], ref: str) -> Mapping[str, Any]:
    """The node that a `$ref` of the form `#/<section>/<name>` names."""
    node: Any = root
    for part in ref.lstrip("#/").split("/"):
        node = node[part]
    return node


def _depth(place: str) -> int:
    """How deep in the value a place lies, the top at 0."""
    return place.count("/") + 1 if place else 0


def _join(place: str, name: str) -> str:
    return f"{place}/{name}" if place else name
