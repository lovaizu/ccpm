"""How Lane holds a JSON value to one of the JSON Schemas beside this module: the keywords that
those schemas use, and the first place where a value leaves its form, named by its path from the
top, such as `roles/log:writer/steps/0`, with what the form takes there."""

from __future__ import annotations

import json
import os
from typing import Any, Callable, Optional

HERE = os.path.dirname(os.path.abspath(__file__))

# A place in a value, by the keys and indexes from its top, and what the form takes there.
_At = tuple[Any, ...]
_Left = Optional[tuple[_At, str]]

# The Python types of a value of each type that a schema names, as json reads JSON; a bool is
# none of them, though Python counts it an int.
_KINDS: dict[str, tuple[type, ...]] = {
    "object": (dict,),
    "array": (list,),
    "string": (str,),
    "integer": (int,),
}


def held(value: Any, schema: str) -> str | None:
    """Where the value leaves the form of the schema.

    Takes: a value as json reads it, and the name of a schema beside this module, such as
    `rules.schema.json`.
    Gives: None where the value holds its form; else the first place where it leaves it, by its
    path from the top, or `the top`, and what the form takes there, such as
    `roles/log:writer/steps/0/rules/0: holds none of the forms it may take: {"type": "size"}`.
    Changes: nothing.
    Refuses: nothing; Lane's own schema that can't be read is Lane's fault, and stops with its
    trace.
    """
    with open(os.path.join(HERE, schema), encoding="utf-8") as f:
        root = json.load(f)
    left = _left(value, root, root, ())
    if left is None:
        return None
    at, what = left
    return f"{'/'.join(map(str, at)) or 'the top'}: {what}"


def _shown(value: Any) -> str:
    """The value as JSON, cut to what a message can show."""
    text = json.dumps(value)
    return text if len(text) <= 80 else text[:77] + "..."


def _left(value: Any, schema: dict[str, Any], root: dict[str, Any], at: _At) -> _Left:
    """The first place where the value leaves the schema, or None."""
    if "$ref" in schema:
        referred = root
        for key in schema["$ref"].partition("#/")[2].split("/"):
            referred = referred[key]
        return _left(value, referred, root, at)
    for check in _CHECKS:
        found = check(value, schema, root, at)
        if found is not None:
            return found
    return None


def _type(value: Any, schema: dict[str, Any], _root: Any, at: _At) -> _Left:
    """Where the value isn't of the schema's type."""
    kind = schema.get("type")
    if kind is None or (isinstance(value, _KINDS[kind]) and not isinstance(value, bool)):
        return None
    return at, f"takes {kind}, not {_shown(value)}"


def _const(value: Any, schema: dict[str, Any], _root: Any, at: _At) -> _Left:
    """Where the value isn't the one that the schema's const names."""
    if "const" not in schema or value == schema["const"]:
        return None
    return at, f"takes {_shown(schema['const'])}, not {_shown(value)}"


def _one_of(value: Any, schema: dict[str, Any], root: dict[str, Any], at: _At) -> _Left:
    """Where the value holds none of the forms of oneOf or anyOf; each schema of Lane's gives
    forms that no value holds two of, so the two keywords take the same check."""
    for keyword in ("oneOf", "anyOf"):
        forms = schema.get(keyword, [])
        if forms and all(_left(value, form, root, at) is not None for form in forms):
            return at, f"holds none of the forms it may take: {_shown(value)}"
    return None


def _required(value: Any, schema: dict[str, Any], _root: Any, at: _At) -> _Left:
    """Where an object lacks a field that the schema requires."""
    missing = next((name for name in schema.get("required", []) if name not in value), None)
    return None if missing is None else (at, f"lacks {missing}")


def _fields(value: Any, schema: dict[str, Any], root: dict[str, Any], at: _At) -> _Left:
    """The first field of an object that leaves its form: the form that properties names for it,
    else that of additionalProperties, where it's false naming no field at all."""
    if not isinstance(value, dict):
        return None
    named = schema.get("properties", {})
    other = schema.get("additionalProperties", True)
    for name, field in value.items():
        form = named.get(name, other)
        if form is False:
            return (*at, name), "is no field that its form names"
        if isinstance(form, dict):
            found = _left(field, form, root, (*at, name))
            if found is not None:
                return found
    return None


def _min_length(value: Any, schema: dict[str, Any], _root: Any, at: _At) -> _Left:
    """Where a string is shorter than minLength."""
    least = schema.get("minLength", 0)
    return None if len(value) >= least else (at, f"takes {least} characters at least")


def _min_items(value: Any, schema: dict[str, Any], _root: Any, at: _At) -> _Left:
    """Where an array holds fewer items than minItems."""
    least = schema.get("minItems", 0)
    return None if len(value) >= least else (at, f"takes {least} items at least")


def _items(value: Any, schema: dict[str, Any], root: dict[str, Any], at: _At) -> _Left:
    """The first item of an array that leaves its form."""
    if "items" not in schema:
        return None
    for index, item in enumerate(value):
        found = _left(item, schema["items"], root, (*at, index))
        if found is not None:
            return found
    return None


# Each keyword's check, in the order a value is held to them, its type first, so that each later
# check meets a value of the type that the schema names beside its keyword.
_CHECKS: tuple[Callable[[Any, dict[str, Any], dict[str, Any], _At], _Left], ...] = (
    _type,
    _const,
    _one_of,
    _required,
    _fields,
    _min_length,
    _min_items,
    _items,
)
