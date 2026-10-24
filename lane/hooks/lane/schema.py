"""A JSON Schema, of the keywords Anthropic's structured outputs accept, in draft-07's wording: the
basic types, properties, required, additionalProperties false, items, enum, const, anyOf, allOf of
schemas with no $ref, a $ref within the schema to it or its $defs or definitions, and minItems 0 or 1; with title,
description, default and $schema, which say what a value is and check nothing. A schema is read
whole before any value is held to it, and one using any other keyword, or a keyword in another
shape, is refused, so no value is let through by a keyword left unread; a $ref coming back to
itself is refused too, as structured outputs refuse a recursive schema. A value held to it gives
the one point it is out by: its place, what was expected and what was found, as check-jsonschema
gives jsonschema's best match, the point highest in the value first."""

from __future__ import annotations

import json
import re
from typing import Any, Callable, NamedTuple

# Each basic type, with what tells a value of it as Python reads JSON, and its name in a message.
TYPES: dict[str, tuple[Callable[[Any], bool], str]] = {
    "object": (lambda v: isinstance(v, dict), "an object"),
    "array": (lambda v: isinstance(v, list), "an array"),
    "string": (lambda v: isinstance(v, str), "a string"),
    # JSON tells no integer from a number with no fraction, so 1.0 is an integer, as draft-07 has it.
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
# The keywords that check nothing, read and left.
NOTES = {"title", "description", "default", "$schema"}
# Where a $ref may point within the schema, beside the schema itself.
DEFINED = ("$defs", "definitions")
# A key a place names as `.key`; any other is named as `["key"]`.
PLAIN_KEY = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
# How much of a value found a message shows.
SHOWN = 40


class Unread(ValueError):
    """A schema lane does not read whole: the place in it and what is wrong there."""


class Out(NamedTuple):
    """What a value is out by: the place in it, as `$` and its keys and indexes, what was expected
    there and what was found."""

    path: tuple[Any, ...]
    expected: str
    found: str

    def told(self) -> str:
        """The point as the subagent is told it."""
        return f"{place(self.path)}: expected {self.expected}, found {self.found}"


def place(path: tuple[Any, ...]) -> str:
    """The place as check-jsonschema names it: `$`, then `.key`, `["key"]` or `[index]`."""
    named = ["$"]
    for step in path:
        if isinstance(step, int):
            named.append(f"[{step}]")
        elif PLAIN_KEY.fullmatch(step):
            named.append(f".{step}")
        else:
            named.append(f"[{json.dumps(step)}]")
    return "".join(named)


def shown(value: Any) -> str:
    """The value as JSON, cut where it is long."""
    text = json.dumps(value, ensure_ascii=False)
    return text if len(text) <= SHOWN else text[: SHOWN - 3] + "..."


def scalar(value: Any) -> bool:
    """Whether the value is a string, a number, a boolean or null, as enum and const take."""
    return value is None or isinstance(value, (str, int, float))


def same(a: Any, b: Any) -> bool:
    """Whether two values enum or const compare are equal, as JSON has them: a boolean is no number,
    and 1 is 1.0."""
    return (a, isinstance(a, bool)) == (b, isinstance(b, bool))


def checked(schema: Any) -> None:
    """Stops with Unread naming the place and what is wrong there, where the schema is not one lane
    reads whole."""
    node(schema, schema, "$", ())


def node(schema: Any, root: Any, at: str, refs: tuple[str, ...]) -> None:
    """Stops where the schema at the place, in the root it lies in, is not one lane reads, following
    each $ref, refs being those followed to reach it."""
    if not isinstance(schema, dict):
        raise Unread(f"{at}: expected a schema object, found {shown(schema)}")
    # Draft-07 leaves every keyword beside a $ref unread, so one there would check nothing; the
    # definitions it points to are read through it.
    if "$ref" in schema and set(schema) - NOTES - {"$ref", *DEFINED}:
        raise Unread(f"{at}: expected $ref alone, as draft-07 reads no keyword beside it")
    for key, value in schema.items():
        if key not in KEYWORDS and key not in NOTES:
            raise Unread(
                f"{at}: `{key}` is no keyword lane reads; it reads type, properties, required,"
                " additionalProperties false, items, enum, const, anyOf, allOf, $ref, $defs,"
                " definitions and minItems 0 or 1, as Anthropic's structured outputs accept"
            )
        if key in KEYWORDS:
            KEYWORDS[key][0](value, root, f"{at}.{key}", refs)


def types_named(value: Any) -> list[str]:
    """The types a type keyword names, one or a list."""
    return value if isinstance(value, list) else [value]


def type_read(value: Any, root: Any, at: str, refs: tuple[str, ...]) -> None:
    named = types_named(value)
    if not named or not all(isinstance(t, str) and t in TYPES for t in named):
        raise Unread(f"{at}: expected one of {', '.join(TYPES)}, or a list of them")


def schemas_read(value: Any, root: Any, at: str, refs: tuple[str, ...]) -> None:
    if not isinstance(value, dict):
        raise Unread(f"{at}: expected an object of schemas")
    for key, each in value.items():
        node(each, root, f"{at}.{key}", refs)


def list_read(value: Any, root: Any, at: str, refs: tuple[str, ...]) -> None:
    if not isinstance(value, list) or not value:
        raise Unread(f"{at}: expected a list of schemas")
    for index, each in enumerate(value):
        node(each, root, f"{at}[{index}]", refs)


def all_of_read(value: Any, root: Any, at: str, refs: tuple[str, ...]) -> None:
    list_read(value, root, at, refs)
    for index, each in enumerate(value):
        if "$ref" in each:
            raise Unread(
                f"{at}[{index}]: expected a schema without $ref, as structured outputs take none"
                " in allOf"
            )


def required_read(value: Any, root: Any, at: str, refs: tuple[str, ...]) -> None:
    if not isinstance(value, list) or not all(isinstance(k, str) for k in value):
        raise Unread(f"{at}: expected a list of keys")


def additional_read(value: Any, root: Any, at: str, refs: tuple[str, ...]) -> None:
    if value is not False:
        raise Unread(f"{at}: expected false, as structured outputs take no other")


def enum_read(value: Any, root: Any, at: str, refs: tuple[str, ...]) -> None:
    if not isinstance(value, list) or not value or not all(map(scalar, value)):
        raise Unread(f"{at}: expected a list of strings, numbers, booleans or nulls")


def const_read(value: Any, root: Any, at: str, refs: tuple[str, ...]) -> None:
    if not scalar(value):
        raise Unread(f"{at}: expected a string, a number, a boolean or null")


def min_items_read(value: Any, root: Any, at: str, refs: tuple[str, ...]) -> None:
    if isinstance(value, bool) or value not in (0, 1):
        raise Unread(f"{at}: expected 0 or 1, as structured outputs take no other")


def ref_read(value: Any, root: Any, at: str, refs: tuple[str, ...]) -> None:
    target = resolved(value, root, at)
    if value in refs:
        raise Unread(f"{at}: {value} comes back to itself, as structured outputs take none")
    node(target, root, value, (*refs, value))


def resolved(ref: Any, root: Any, at: str) -> Any:
    """The schema a $ref points to within the root; stops where it points to none there."""
    if not isinstance(ref, str) or not (ref == "#" or ref.startswith("#/")):
        raise Unread(f"{at}: expected a reference within the schema, `#` or `#/...`")
    target = root
    for part in ref.split("/")[1:]:
        key = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(target, dict) or key not in target:
            raise Unread(f"{at}: {ref} points to nothing in the schema")
        target = target[key]
    return target


def held(schema: dict[str, Any], value: Any) -> Out | None:
    """The point the value is out of the schema by, a schema `checked` has read whole; None where
    it holds to it."""
    return out(schema, schema, value, ())


def out(schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]) -> Out | None:
    """The point the value at the path is out of the schema by, the root's $refs followed."""
    for key in KEYWORDS:
        if key in schema:
            found = KEYWORDS[key][1](schema, root, value, path)
            if found:
                return found
    return None


def ref_out(schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]) -> Out | None:
    return out(resolved(schema["$ref"], root, ""), root, value, path)


def type_out(schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]) -> Out | None:
    named = types_named(schema["type"])
    if any(TYPES[t][0](value) for t in named):
        return None
    return Out(path, " or ".join(TYPES[t][1] for t in named), shown(value))


def enum_out(schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]) -> Out | None:
    allowed = schema["enum"]
    if any(same(value, a) for a in allowed):
        return None
    return Out(path, "one of " + ", ".join(map(shown, allowed)), shown(value))


def const_out(schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]) -> Out | None:
    return None if same(value, schema["const"]) else Out(path, shown(schema["const"]), shown(value))


def required_out(
    schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]
) -> Out | None:
    missing = [k for k in schema["required"] if isinstance(value, dict) and k not in value]
    if not missing:
        return None
    return Out(path, f"the key {shown(missing[0])}", "an object without it")


def additional_out(
    schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]
) -> Out | None:
    known = schema.get("properties", {})
    extra = [k for k in value if k not in known] if isinstance(value, dict) else []
    if not extra:
        return None
    keys = ", ".join(map(shown, known)) or "none"
    return Out(path, f"only the keys {keys}", f"the key {shown(extra[0])}")


def properties_out(
    schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]
) -> Out | None:
    if not isinstance(value, dict):
        return None
    for key, each in schema["properties"].items():
        found = out(each, root, value[key], (*path, key)) if key in value else None
        if found:
            return found
    return None


def items_out(schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]) -> Out | None:
    for index, each in enumerate(value if isinstance(value, list) else []):
        found = out(schema["items"], root, each, (*path, index))
        if found:
            return found
    return None


def min_items_out(
    schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]
) -> Out | None:
    if isinstance(value, list) and len(value) < schema["minItems"]:
        return Out(path, "at least 1 item", "none")
    return None


def all_of_out(schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]) -> Out | None:
    for each in schema["allOf"]:
        found = out(each, root, value, path)
        if found:
            return found
    return None


def any_of_out(schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]) -> Out | None:
    """None where the value holds to a choice; otherwise the point of the choice it went deepest
    in, the first of those, as jsonschema's best match takes; or, where it went into none, that it
    holds to none."""
    found = [out(each, root, value, path) for each in schema["anyOf"]]
    if None in found:
        return None
    deeper = [f for f in found if f and f.path[len(path) :]]
    if deeper:
        return max(deeper, key=lambda f: len(f.path))
    return Out(path, "a value of one of its anyOf choices", shown(value))


# Each keyword lane reads, in the order a value is held to them, so the point highest in the value
# is found first: how it is read in a schema, and the point a value is out by under it.
KEYWORDS: dict[str, tuple[Callable[..., None], Callable[..., Out | None]]] = {
    "$ref": (ref_read, ref_out),
    "type": (type_read, type_out),
    "enum": (enum_read, enum_out),
    "const": (const_read, const_out),
    "required": (required_read, required_out),
    "additionalProperties": (additional_read, additional_out),
    "minItems": (min_items_read, min_items_out),
    "properties": (schemas_read, properties_out),
    "items": (node, items_out),
    "allOf": (all_of_read, all_of_out),
    "anyOf": (list_read, any_of_out),
    "$defs": (schemas_read, lambda *_: None),
    "definitions": (schemas_read, lambda *_: None),
}
