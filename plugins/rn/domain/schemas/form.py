"""Decides how rn holds a JSON value to one of its JSON Schemas: the keywords of draft-07 that rn's
schemas use, and the one place where a value
leaves its form, named by its path from the top, such as `deliverables/0/status`, so that whoever
wrote the value can mend it."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from typing import Any

from fault import CantRun, Wrong

# A JSON value as Python reads it.
Json = Any

# Each type a schema names, with what tells a value of it as Python reads JSON.
_TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def load(path: str) -> Mapping[str, Json]:
    """The JSON Schema at `path`.

    Takes: the path of a schema, such as a file of `schemas/` or the design tree best practice's.
    Gives: the schema.
    Refuses: CantRun where the file can't be read or isn't JSON, as rn's own file is at fault."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as error:
        raise CantRun(f"rn's schema {path} can't be read: {error}") from None


def read(path: str, schema: str, name: str) -> Json:
    """The JSON file at `path`, held to the schema at `schema`.

    Takes: the file's path, the schema's path, and the name by which whoever wrote the file knows
    it, such as its path from the top of the worktree.
    Gives: the file's value, once it holds its form.
    Refuses: Wrong, naming `name`, where the file isn't there, isn't JSON, or leaves its form."""
    try:
        with open(path, encoding="utf-8") as f:
            value = json.load(f)
    except OSError:
        raise Wrong(f"{name}: no file is there") from None
    except ValueError as error:
        raise Wrong(f"{name}: isn't JSON: {error}") from None
    hold(value, load(schema), name)
    return value


def hold(value: Json, schema: Mapping[str, Json], name: str) -> None:
    """Holds `value` to `schema`.

    Takes: the value read from the file named `name`, and its schema.
    Gives: nothing, where the value holds its form.
    Refuses: Wrong, naming `name`, the path within the value of the first place that leaves the
    form, and what the schema takes there."""
    out = _out(value, schema, schema, ())
    if out is not None:
        place, what = out
        raise Wrong(f"{name}: {'/'.join(map(str, place)) or 'the top'}: {what}")


def _out(value: Json, schema: Mapping[str, Json], root: Mapping[str, Json], at: tuple) -> Any:
    """The first place where `value` leaves `schema`, with what the schema takes there, or None."""
    if "$ref" in schema:
        return _out(value, root["$defs"][schema["$ref"].rsplit("/", 1)[1]], root, at)
    for check in _KEYWORDS:
        out = check(value, schema, root, at)
        if out is not None:
            return out
    return None


def _type(value: Json, schema: Mapping[str, Json], _root: Any, at: tuple) -> Any:
    """Where the value isn't of the type the schema names."""
    types = schema.get("type", list(_TYPES))
    types = [types] if isinstance(types, str) else types
    if any(_TYPES[t](value) for t in types):
        return None
    return at, f"takes {' or '.join(types)}, not {json.dumps(value)[:40]}"


def _enum(value: Json, schema: Mapping[str, Json], _root: Any, at: tuple) -> Any:
    """Where the value is none of the values that enum or const names."""
    allowed = schema.get("enum", [schema["const"]] if "const" in schema else None)
    if allowed is None or value in allowed:
        return None
    return at, f"takes {' or '.join(map(json.dumps, allowed))}, not {json.dumps(value)[:40]}"


def _any_of(value: Json, schema: Mapping[str, Json], root: Any, at: tuple) -> Any:
    """Where the value holds no form of anyOf: the place of the form it went deepest in, the first
    of those, as jsonschema's best match takes, or the value's own where it went into none."""
    if "anyOf" not in schema:
        return None
    found = [_out(value, f, root, at) for f in schema["anyOf"]]
    if None in found:
        return None
    deepest = max(found, key=lambda out: len(out[0]))
    return deepest if len(deepest[0]) > len(at) else (at, "holds none of the forms it may take")


def _required(value: Json, schema: Mapping[str, Json], _root: Any, at: tuple) -> Any:
    """Where an object lacks a field that the schema requires."""
    lacked = [key for key in schema.get("required", []) if key not in value]
    return (at, f"lacks {lacked[0]}") if lacked else None


def _additional(value: Json, schema: Mapping[str, Json], _root: Any, at: tuple) -> Any:
    """Where an object holds a field that a schema of additionalProperties false doesn't name."""
    if schema.get("additionalProperties") is not False:
        return None
    other = [key for key in value if key not in schema.get("properties", {})]
    return ((*at, other[0]), "is no field that the form names") if other else None


def _properties(value: Json, schema: Mapping[str, Json], root: Any, at: tuple) -> Any:
    """The first field of an object that leaves its form."""
    fields = schema.get("properties", {})
    found = (_out(value[k], f, root, (*at, k)) for k, f in fields.items() if k in value)
    return next((out for out in found if out is not None), None)


def _pattern(value: Json, schema: Mapping[str, Json], _root: Any, at: tuple) -> Any:
    """Where a string holds no match of the schema's pattern, searched for anywhere in it, as
    draft-07 searches."""
    if "pattern" not in schema or re.search(schema["pattern"], value):
        return None
    return at, "holds what its form leaves to elsewhere, such as a date or a ground"


def _min_items(value: Json, schema: Mapping[str, Json], _root: Any, at: tuple) -> Any:
    """Where an array holds fewer items than minItems."""
    if "minItems" not in schema or len(value) >= schema["minItems"]:
        return None
    return at, f"takes at least {schema['minItems']} items"


def _items(value: Json, schema: Mapping[str, Json], root: Any, at: tuple) -> Any:
    """The first item of an array that leaves its form."""
    if "items" not in schema:
        return None
    found = (_out(item, schema["items"], root, (*at, i)) for i, item in enumerate(value))
    return next((out for out in found if out is not None), None)


# The check of each keyword, in the order a value is held to them, its type first, so that each
# later check meets a value of the type that the schema names beside its keyword.
_KEYWORDS = (
    _type,
    _enum,
    _any_of,
    _required,
    _additional,
    _properties,
    _pattern,
    _min_items,
    _items,
)
