"""Decides whether a JSON value holds to the form that one of rn's schemas gives, by the keywords
of JSON Schema that rn's schemas use: `type`, `required`, `properties`, `additionalProperties`,
`items`, `minItems`, `enum`, `const`, `minLength`, `pattern`, `oneOf`, and `$ref`, to a definition
in the same schema or to a part of another schema beside it. A schema that uses another keyword is
a fault of rn's own, so it refuses that schema rather than pass what it didn't check."""

from __future__ import annotations

import json
import os
import re
from typing import Any

from fault import Wrong

# Each JSON type by its name in a schema, and the Python types that `json.load` gives for it. A
# bool is an int in Python, so `integer` takes int alone, and a bool is held apart below.
_TYPES: dict[str, tuple[type, ...]] = {
    "object": (dict,),
    "array": (list,),
    "string": (str,),
    "integer": (int,),
    "boolean": (bool,),
    "null": (type(None),),
}
# The keywords that rn's schemas use, those that say what a value takes and those that only say
# what it is.
_CHECKED = {
    "type",
    "required",
    "properties",
    "additionalProperties",
    "items",
    "minItems",
    "enum",
    "const",
    "minLength",
    "pattern",
    "oneOf",
    "$ref",
}
_TOLD = {"$schema", "title", "description", "definitions"}


def held(path: str, schema_path: str, what: str) -> dict[str, Any]:
    """A file that one of rn's roles or scripts wrote, read and checked against its schema.

    Takes: the file's path, its schema's path, and what the file is, such as `the steering`, for
    the message.
    Gives: the file's JSON.
    Changes: nothing.
    Refuses: Wrong where no file lies there, it isn't JSON, or it leaves its schema, naming each
    place as `faults` does.
    """
    try:
        with open(path, encoding="utf-8") as f:
            value = json.load(f)
    except FileNotFoundError:
        raise Wrong(f"{path}: no {what} lies there") from None
    except json.JSONDecodeError as error:
        raise Wrong(f"{path}: {what} isn't JSON: {error}") from None
    found = faults(value, schema_path)
    if found:
        name = os.path.basename(schema_path)
        raise Wrong(f"{path}: {what} leaves its schema, {name}: " + "; ".join(found))
    return value


def read(path: str) -> dict[str, Any]:
    """The schema at the path, as JSON."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def faults(value: Any, schema_path: str) -> list[str]:
    """Where the value leaves the form of the schema.

    Takes: the value, as `json.load` gives it, and the path of the schema.
    Gives: each place that leaves the form, as `<JSON Pointer>: <what it takes>`, in the order
    found, `/` for the value whole; none where it holds to it.
    Changes: nothing.
    Refuses: ValueError where the schema uses a keyword that this module doesn't check, naming it.
    """
    root = read(schema_path)
    return _Check(os.path.dirname(schema_path), root).faults(value, root, "")


class _Check:
    """One check of a value, by a schema whose references within it lead to its root, and to
    another schema beside it in the folder."""

    def __init__(self, folder: str, root: dict[str, Any]) -> None:
        self.folder = folder
        self.root = root

    def faults(self, value: Any, schema: dict[str, Any], at: str) -> list[str]:
        unknown = set(schema) - _CHECKED - _TOLD
        if unknown:
            raise ValueError(f"the schema uses {sorted(unknown)}, which rn's form check doesn't")
        if "$ref" in schema:
            return self.referred(value, schema["$ref"], at)
        if "oneOf" in schema:
            return self.one_of(value, schema["oneOf"], at)
        if not _typed(value, schema.get("type")):
            return [f"{at or '/'}: takes {_said(schema['type'])}"]
        return self.within(value, schema, at)

    def referred(self, value: Any, ref: str, at: str) -> list[str]:
        file, _, pointer = ref.partition("#")
        check = _Check(self.folder, read(os.path.join(self.folder, file))) if file else self
        part: Any = check.root
        for key in pointer.strip("/").split("/"):
            part = part[key]
        return check.faults(value, part, at)

    def one_of(self, value: Any, options: list[dict[str, Any]], at: str) -> list[str]:
        held = [each for each in options if not self.faults(value, each, at)]
        if len(held) == 1:
            return []
        return [
            f"{at or '/'}: takes exactly one of its {len(options)} forms, and holds {len(held)}"
        ]

    def within(self, value: Any, schema: dict[str, Any], at: str) -> list[str]:
        found = _scalar_faults(value, schema, at)
        if isinstance(value, dict):
            found += self.object_faults(value, schema, at)
        if isinstance(value, list) and "items" in schema:
            for index, each in enumerate(value):
                found += self.faults(each, schema["items"], f"{at}/{index}")
        return found

    def object_faults(self, value: dict[str, Any], schema: dict[str, Any], at: str) -> list[str]:
        properties = schema.get("properties", {})
        found = [
            f"{at}/{key}: is required" for key in schema.get("required", []) if key not in value
        ]
        for key, each in value.items():
            if key in properties:
                found += self.faults(each, properties[key], f"{at}/{key}")
            elif schema.get("additionalProperties") is False:
                found.append(f"{at}/{key}: isn't a field of this form")
        return found


def _typed(value: Any, named: str | list[str] | None) -> bool:
    if named is None:
        return True
    names = [named] if isinstance(named, str) else named
    return any(_is(value, each) for each in names)


def _is(value: Any, name: str) -> bool:
    if isinstance(value, bool) and name != "boolean":
        return False
    return isinstance(value, _TYPES[name])


def _said(named: str | list[str]) -> str:
    return named if isinstance(named, str) else " or ".join(named)


def _scalar_faults(value: Any, schema: dict[str, Any], at: str) -> list[str]:
    found = []
    if "const" in schema and value != schema["const"]:
        found.append(f"{at}: takes {schema['const']}")
    if isinstance(value, list) and len(value) < schema.get("minItems", 0):
        found.append(f"{at}: takes at least {schema['minItems']} item")
    if "enum" in schema and value not in schema["enum"]:
        found.append(f"{at}: takes one of {', '.join(map(str, schema['enum']))}")
    if isinstance(value, str) and len(value) < schema.get("minLength", 0):
        found.append(f"{at}: takes at least {schema['minLength']} character")
    if isinstance(value, str) and "pattern" in schema and not re.search(schema["pattern"], value):
        found.append(f"{at}: takes the form {schema['pattern']}")
    return found
