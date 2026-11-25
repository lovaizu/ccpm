"""Decides how a JSON value is held to one of rn's JSON Schemas, in the part of draft-07 that rn's
schemas and the design tree's use, with the standard library alone, and where rn's schemas lie."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Callable

from fault import CantRun

# The folder of rn's own schemas, domain/schemas/, two above this file's folder.
_DOMAIN = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_SCHEMAS = os.path.join(_DOMAIN, "schemas")

# Each type that rn's schemas name, by whether a value from JSON is of it; a bool is no integer.
_TYPES: dict[str, Callable[[Any], bool]] = {
    "object": lambda value: isinstance(value, dict),
    "array": lambda value: isinstance(value, list),
    "string": lambda value: isinstance(value, str),
    "integer": lambda value: isinstance(value, int) and not isinstance(value, bool),
    "boolean": lambda value: isinstance(value, bool),
    "null": lambda value: value is None,
}
# The keywords that only describe, and hold nothing of the value.
_NOTES = {"$schema", "title", "description", "$defs"}


def schema(name: str) -> str:
    """The path of rn's schema of the name, such as `generator-cut` for
    `domain/schemas/generator-cut.schema.json`."""
    return os.path.join(_SCHEMAS, f"{name}.schema.json")


def faults(value: Any, schema_path: str) -> list[str]:
    """Each place where the value leaves the schema.

    Takes: a value read from JSON, and the path of a JSON Schema.
    Gives: each place, by its JSON Pointer, with what the schema takes there, such as
    `/work/0/do: takes one of make, decide`; none where the value holds the schema.
    Changes: nothing.
    Refuses: CantRun where the schema can't be read or uses a keyword that this module doesn't
    check, naming it, so that no keyword passes unchecked.
    """
    try:
        with open(schema_path, encoding="utf-8") as file:
            schema = json.load(file)
    except (OSError, ValueError) as error:
        raise CantRun(f"{schema_path}: the schema can't be read: {error}") from None
    return _Holder(schema, schema_path).faults(value, schema, "")


class _Holder:
    """Holds values to the parts of one schema, whose `$ref`s point into it."""

    def __init__(self, root: dict[str, Any], path: str) -> None:
        self._root = root
        self._path = path
        self._keywords: dict[str, Callable[[Any, Any, str], list[str]]] = {
            "type": self._type,
            "enum": self._enum,
            "const": self._const,
            "required": self._required,
            "properties": self._properties,
            "items": self._items,
            "minItems": self._min_items,
            "minLength": self._min_length,
            "minimum": self._minimum,
            "pattern": self._pattern,
            "anyOf": self._any_of,
            "oneOf": self._one_of,
            "$ref": self._ref,
        }

    def faults(self, value: Any, schema: dict[str, Any], at: str) -> list[str]:
        """Each fault of the value at the pointer against the part of the schema."""
        found: list[str] = []
        for keyword, given in schema.items():
            if keyword in _NOTES:
                continue
            if keyword not in self._keywords and keyword != "additionalProperties":
                raise CantRun(
                    f"{self._path}: uses {keyword}, which rn's check of a form doesn't hold"
                )
            if keyword == "additionalProperties":
                found += self._additional(value, given, at, schema.get("properties", {}))
            else:
                found += self._keywords[keyword](value, given, at)
        return found

    def _type(self, value: Any, kind: str, at: str) -> list[str]:
        return [] if _TYPES[kind](value) else [f"{at}: takes a value of the type {kind}"]

    def _enum(self, value: Any, values: list[Any], at: str) -> list[str]:
        if value in values:
            return []
        return [f"{at}: takes one of {', '.join(str(each) for each in values)}"]

    def _const(self, value: Any, const: Any, at: str) -> list[str]:
        return [] if value == const else [f"{at}: takes {const}"]

    def _required(self, value: Any, names: list[str], at: str) -> list[str]:
        if not isinstance(value, dict):
            return []
        return [f"{_at(at, name)}: is required" for name in names if name not in value]

    def _properties(self, value: Any, schemas: dict[str, Any], at: str) -> list[str]:
        if not isinstance(value, dict):
            return []
        return [
            fault
            for name, schema in schemas.items()
            if name in value
            for fault in self.faults(value[name], schema, _at(at, name))
        ]

    def _additional(self, value: Any, schema: Any, at: str, named: dict[str, Any]) -> list[str]:
        if not isinstance(value, dict):
            return []
        found: list[str] = []
        for name, each in value.items():
            if name in named:
                continue
            if schema is False:
                found.append(f"{_at(at, name)}: isn't a property that the form takes")
            else:
                found += self.faults(each, schema, _at(at, name))
        return found

    def _items(self, value: Any, schema: dict[str, Any], at: str) -> list[str]:
        if not isinstance(value, list):
            return []
        return [
            fault
            for index, each in enumerate(value)
            for fault in self.faults(each, schema, _at(at, str(index)))
        ]

    def _min_items(self, value: Any, least: int, at: str) -> list[str]:
        if isinstance(value, list) and len(value) < least:
            return [f"{at}: takes {least} items at least"]
        return []

    def _min_length(self, value: Any, least: int, at: str) -> list[str]:
        if isinstance(value, str) and len(value) < least:
            return [f"{at}: takes {least} characters at least"]
        return []

    def _minimum(self, value: Any, least: int, at: str) -> list[str]:
        if _TYPES["integer"](value) and value < least:
            return [f"{at}: takes {least} at least"]
        return []

    def _pattern(self, value: Any, pattern: str, at: str) -> list[str]:
        if isinstance(value, str) and not re.search(pattern, value):
            return [f"{at}: takes a string that matches {pattern}"]
        return []

    def _branches(self, value: Any, schemas: list[dict[str, Any]], at: str) -> list[list[str]]:
        return [self.faults(value, schema, at) for schema in schemas]

    def _any_of(self, value: Any, schemas: list[dict[str, Any]], at: str) -> list[str]:
        return _fewest(self._branches(value, schemas, at))

    def _one_of(self, value: Any, schemas: list[dict[str, Any]], at: str) -> list[str]:
        found = self._branches(value, schemas, at)
        if found.count([]) > 1:
            return [f"{at}: holds more than one of the forms it takes one of"]
        return _fewest(found)

    def _ref(self, value: Any, ref: str, at: str) -> list[str]:
        schema: Any = self._root
        for name in ref.lstrip("#/").split("/"):
            schema = schema[name]
        return self.faults(value, schema, at)


def _fewest(found: list[list[str]]) -> list[str]:
    """None where a branch holds the value, else the faults of the branch with the fewest, as the
    form the value comes nearest to says best how to mend it."""
    return [] if [] in found else min(found, key=len)


def _at(at: str, name: str) -> str:
    """The JSON Pointer of the name under the pointer, `~` and `/` escaped."""
    return f"{at}/{name.replace('~', '~0').replace('/', '~1')}"
