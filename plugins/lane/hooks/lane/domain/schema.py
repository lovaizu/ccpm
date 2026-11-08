"""Decides whether a JSON value holds to a JSON Schema, and which schemas Lane reads as a form.

A form is a schema that a step's output follows, such as in_form's. `checked` reads a form only in
the keywords that Anthropic's structured outputs accept, so that a model can write to any form that
Lane holds an output to. `held` reads those keywords and the few more that Lane's own schemas use:
`minimum`, `minLength`, `minItems` of any count, and `additionalProperties` given as a schema.

rn's scripts take this module through a link, so `checked`, `held`, `Out`, and `Unread` keep their
contract for them too.
"""

from __future__ import annotations

import json
import re
from typing import Any, Callable, NamedTuple

# Each basic type, with the test of a value as Python reads it from JSON, and its name in a message.
TYPES: dict[str, tuple[Callable[[Any], bool], str]] = {
    "object": (lambda v: isinstance(v, dict), "an object"),
    "array": (lambda v: isinstance(v, list), "an array"),
    "string": (lambda v: isinstance(v, str), "a string"),
    # JSON has no integer apart from a number with no fraction, so draft-07 takes 1.0 as one.
    "integer": (
        lambda v: (
            not isinstance(v, bool)
            and (isinstance(v, int) or isinstance(v, float) and v.is_integer())
        ),
        "an integer",
    ),
    "number": (lambda v: not isinstance(v, bool) and isinstance(v, (int, float)), "a number"),
    "boolean": (lambda v: isinstance(v, bool), "a boolean"),
    "null": (lambda v: v is None, "null"),
}
# The keywords that only describe a value, which a check passes over.
NOTES = {"title", "description", "default", "$schema"}
# The keywords of a form, besides the notes, as structured outputs accept them.
FORM_KEYWORDS = {
    "type",
    "properties",
    "required",
    "additionalProperties",
    "items",
    "enum",
    "const",
    "anyOf",
    "allOf",
    "$ref",
    "$defs",
    "definitions",
    "minItems",
    "pattern",
}
# A $ref that a form may hold: to the whole schema, or to a schema under $defs or definitions.
FORM_REF = re.compile(r"#(/(\$defs|definitions)/[^/]+)?")
# A key that a place shows as `.key`. Any other key shows as `["key"]`.
PLAIN_KEY = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")
# The most characters of a value that a message shows.
SHOWN = 40


class Unread(ValueError):
    """A schema that Lane doesn't read as a form, with the place in it and what's wrong there."""


class Out(NamedTuple):
    """The point at which a value is out of its schema."""

    # The keys and indexes from the top of the value to the point.
    path: tuple[Any, ...]
    # What the schema asks for there.
    expected: str
    # What the value holds there, as JSON, cut short.
    found: str

    def told(self) -> str:
        """The point in words, such as `$.lines[0]: expected a string, found 3`."""
        return f"{place(self.path)}: expected {self.expected}, found {self.found}"


def checked(form: Any) -> None:
    """Reads a schema as a form, whole, before Lane holds any value to it.

    It raises Unread where the schema uses a keyword that structured outputs don't accept, or one in
    a shape they don't accept, or a $ref that points outside the schema, to nothing, or back to
    itself.
    """
    _check_node(form, form, (), ())


def held(given: dict[str, Any], value: Any) -> Out | None:
    """The point at which the value is out of the schema, or None where the value holds.

    Where the value is out at several points, the point is the first one that a reader meets from
    the top of the value. In anyOf, it's the point of the branch that holds the value deepest.
    The schema is one that `checked` reads, or one of Lane's own.
    """
    return _out(given, given, value, ())


def place(path: tuple[Any, ...]) -> str:
    """The path as a place, `$` followed by `.key`, `["key"]`, or `[index]` for each step."""
    shown = "$"
    for step in path:
        if isinstance(step, int):
            shown += f"[{step}]"
        elif PLAIN_KEY.fullmatch(step):
            shown += f".{step}"
        else:
            shown += f"[{json.dumps(step)}]"
    return shown


def shown(value: Any) -> str:
    """The value as JSON, cut short after the most characters that a message shows."""
    text = json.dumps(value, ensure_ascii=False)
    return text if len(text) <= SHOWN else text[:SHOWN] + "..."


def _check_node(node: Any, root: Any, at: tuple[Any, ...], refs: tuple[str, ...]) -> None:
    """Reads the schema at the place, and follows each $ref in it. refs holds the $refs that the
    reading has followed so far."""
    if not isinstance(node, dict):
        raise Unread(f"{place(at)}: expected a schema object, found {shown(node)}")
    for key in node:
        if key not in FORM_KEYWORDS and key not in NOTES:
            raise Unread(f"{place(at)}: `{key}` is no keyword that Lane reads in a form")
    for key, value in node.items():
        if key in CHECKS:
            CHECKS[key](value, root, at + (key,), refs)


def _check_type(value: Any, root: Any, at: tuple[Any, ...], refs: tuple[str, ...]) -> None:
    names = value if isinstance(value, list) else [value]
    if not names or not all(isinstance(n, str) and n in TYPES for n in names):
        raise Unread(f"{place(at)}: expected a basic type or a list of them, found {shown(value)}")


def _check_schemas(value: Any, root: Any, at: tuple[Any, ...], refs: tuple[str, ...]) -> None:
    """Reads an object of schemas, as properties, $defs, and definitions hold."""
    if not isinstance(value, dict):
        raise Unread(f"{place(at)}: expected an object of schemas, found {shown(value)}")
    for key, node in value.items():
        _check_node(node, root, at + (key,), refs)


def _check_required(value: Any, root: Any, at: tuple[Any, ...], refs: tuple[str, ...]) -> None:
    if not isinstance(value, list) or not all(isinstance(k, str) for k in value):
        raise Unread(f"{place(at)}: expected a list of key names, found {shown(value)}")


def _check_additional(value: Any, root: Any, at: tuple[Any, ...], refs: tuple[str, ...]) -> None:
    if value is not False:
        raise Unread(f"{place(at)}: expected false, found {shown(value)}")


def _check_items(value: Any, root: Any, at: tuple[Any, ...], refs: tuple[str, ...]) -> None:
    _check_node(value, root, at, refs)


def _check_enum(value: Any, root: Any, at: tuple[Any, ...], refs: tuple[str, ...]) -> None:
    if not isinstance(value, list) or any(isinstance(v, (dict, list)) for v in value):
        raise Unread(
            f"{place(at)}: expected a list of strings, numbers, booleans or nulls, found"
            f" {shown(value)}"
        )


def _check_any_of(value: Any, root: Any, at: tuple[Any, ...], refs: tuple[str, ...]) -> None:
    if not isinstance(value, list):
        raise Unread(f"{place(at)}: expected a list of schemas, found {shown(value)}")
    for index, node in enumerate(value):
        _check_node(node, root, at + (index,), refs)


def _check_all_of(value: Any, root: Any, at: tuple[Any, ...], refs: tuple[str, ...]) -> None:
    if isinstance(value, list):
        for index, node in enumerate(value):
            if isinstance(node, dict) and "$ref" in node:
                raise Unread(
                    f"{place(at + (index,))}: expected a schema without $ref, as structured"
                    " outputs take none in allOf"
                )
    _check_any_of(value, root, at, refs)


def _check_ref(value: Any, root: Any, at: tuple[Any, ...], refs: tuple[str, ...]) -> None:
    if not isinstance(value, str) or not FORM_REF.fullmatch(value):
        raise Unread(
            f"{place(at)}: expected #, #/$defs/<name> or #/definitions/<name>, found {shown(value)}"
        )
    if value in refs:
        raise Unread(
            f"{place(at)}: {value} comes back to itself, and structured outputs take no recursive"
            " schema"
        )
    target = tuple(value.split("/")[1:])
    _check_node(_resolved(value, root, at), root, target, refs + (value,))


def _check_min_items(value: Any, root: Any, at: tuple[Any, ...], refs: tuple[str, ...]) -> None:
    if isinstance(value, bool) or value not in (0, 1):
        raise Unread(f"{place(at)}: expected 0 or 1, found {shown(value)}")


def _check_pattern(value: Any, root: Any, at: tuple[Any, ...], refs: tuple[str, ...]) -> None:
    try:
        re.compile(value)
    except (re.error, TypeError):
        raise Unread(f"{place(at)}: expected a regular expression, found {shown(value)}") from None


# How `checked` reads each keyword that holds more than a constant.
CHECKS: dict[str, Callable[[Any, Any, tuple[Any, ...], tuple[str, ...]], None]] = {
    "type": _check_type,
    "properties": _check_schemas,
    "$defs": _check_schemas,
    "definitions": _check_schemas,
    "required": _check_required,
    "additionalProperties": _check_additional,
    "items": _check_items,
    "enum": _check_enum,
    "anyOf": _check_any_of,
    "allOf": _check_all_of,
    "$ref": _check_ref,
    "minItems": _check_min_items,
    "pattern": _check_pattern,
}


def _resolved(ref: str, root: Any, at: tuple[Any, ...]) -> Any:
    """The schema that the $ref points to within the root.

    It raises Unread where the $ref points to nothing in the root.
    """
    if ref == "#":
        return root
    _, folder, name = ref.split("/")
    found = root.get(folder, {}) if isinstance(root, dict) else {}
    if not isinstance(found, dict) or name not in found:
        raise Unread(f"{place(at)}: {ref} points to nothing in the schema")
    return found[name]


def _same(a: Any, b: Any) -> bool:
    """Whether two JSON values are equal, true and 1 being two values, as JSON has them."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_same(a[k], b[k]) for k in a)
    return a == b


def _counted(count: int, noun: str) -> str:
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def _out(node: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]) -> Out | None:
    """The point at which the value at the path is out of the schema node."""
    for check in (_type_out, _value_out, _object_out, _array_out, _branches_out):
        found = check(node, root, value, path)
        if found:
            return found
    if "$ref" in node:
        return _out(_resolved(node["$ref"], root, path), root, value, path)
    return None


def _type_out(node: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]) -> Out | None:
    if "type" not in node:
        return None
    names = node["type"] if isinstance(node["type"], list) else [node["type"]]
    if any(TYPES[n][0](value) for n in names):
        return None
    return Out(path, " or ".join(TYPES[n][1] for n in names), shown(value))


def _value_out(node: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]) -> Out | None:
    """The point at which the value is out of enum, const, minimum, minLength, or pattern."""
    if "enum" in node and not any(_same(value, v) for v in node["enum"]):
        return Out(path, "one of " + ", ".join(shown(v) for v in node["enum"]), shown(value))
    if "const" in node and not _same(value, node["const"]):
        return Out(path, shown(node["const"]), shown(value))
    if "minimum" in node and TYPES["number"][0](value) and value < node["minimum"]:
        return Out(path, f"at least {node['minimum']}", shown(value))
    if isinstance(value, str):
        if "minLength" in node and len(value) < node["minLength"]:
            return Out(path, "at least " + _counted(node["minLength"], "character"), shown(value))
        if "pattern" in node and not re.search(node["pattern"], value):
            return Out(path, f"text matching {node['pattern']}", shown(value))
    return None


def _object_out(node: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]) -> Out | None:
    if not isinstance(value, dict):
        return None
    for key in node.get("required", []):
        if key not in value:
            return Out(path, f"the key {shown(key)}", "an object without it")
    properties = node.get("properties", {})
    extra = node.get("additionalProperties", True)
    for key, item in value.items():
        if key in properties:
            found = _out(properties[key], root, item, path + (key,))
        elif extra is False:
            found = Out(path + (key,), "no such key", shown(item))
        elif isinstance(extra, dict):
            found = _out(extra, root, item, path + (key,))
        else:
            found = None
        if found:
            return found
    return None


def _array_out(node: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]) -> Out | None:
    if not isinstance(value, list):
        return None
    if len(value) < node.get("minItems", 0):
        return Out(path, "at least " + _counted(node["minItems"], "item"), shown(value))
    if "items" in node:
        for index, item in enumerate(value):
            found = _out(node["items"], root, item, path + (index,))
            if found:
                return found
    return None


def _branches_out(node: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]) -> Out | None:
    for branch in node.get("allOf", []):
        found = _out(branch, root, value, path)
        if found:
            return found
    if "anyOf" not in node:
        return None
    outs = []
    for branch in node["anyOf"]:
        found = _out(branch, root, value, path)
        if not found:
            return None
        outs.append(found)
    return max(outs, key=lambda o: len(o.path))
