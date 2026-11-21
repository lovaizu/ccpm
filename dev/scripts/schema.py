"""A JSON Schema of the keywords, in the forms, that the schemas of dev/scripts use, in
draft-07's wording: type of one basic type, properties, required, additionalProperties false,
items, enum of strings, const of a string, anyOf, minItems, minLength, minimum, pattern, and $ref
alone to an entry of $defs that holds neither $ref nor anyOf at its top; with title, description,
and $schema, which say what a value is and check nothing. A schema is read whole before any value
is held to it, and one using any other keyword, or a keyword in another form, is refused, so no
value is let through by a keyword left unread, and holding a value to it ends. A value held to it
gives the one point it's out by: its place, what was expected, and what was found, as
check-jsonschema gives jsonschema's best match, the point highest in the value first."""

from __future__ import annotations

import json
import re
from typing import Any, Callable, NamedTuple

# Each basic type, with what tells a value of it as Python reads JSON, and its name in a message.
TYPES: dict[str, tuple[Callable[[Any], bool], str]] = {
    "object": (lambda v: isinstance(v, dict), "an object"),
    "array": (lambda v: isinstance(v, list), "an array"),
    "string": (lambda v: isinstance(v, str), "a string"),
    "integer": (lambda v: isinstance(v, int) and not isinstance(v, bool), "an integer"),
    "boolean": (lambda v: isinstance(v, bool), "a boolean"),
    "null": (lambda v: v is None, "null"),
}
# The keywords that check nothing, read and left.
NOTES = {"title", "description", "$schema"}
# Where a $ref points: an entry of the schema's $defs.
REF = re.compile(r"#/\$defs/([^/~]+)")
# How much of a value found a message shows.
SHOWN = 40


class Unread(ValueError):
    """A schema this check doesn't read whole: the place in it and what is wrong there."""


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
    """The place as check-jsonschema names it: `$`, then `.key` or `[index]`."""
    return "$" + "".join(f"[{step}]" if isinstance(step, int) else f".{step}" for step in path)


def shown(value: Any) -> str:
    """The value as JSON, words beyond ASCII as written, cut where it is long."""
    text = json.dumps(value, ensure_ascii=False)
    return text if len(text) <= SHOWN else text[: SHOWN - 3] + "..."


def checked(schema: Any) -> None:
    """Stops with Unread naming the place and what is wrong there, where the schema is not one it
    reads whole."""
    _node(schema, schema, "$")


def _node(schema: Any, root: Any, at: str) -> None:
    """Stops where the schema at the place, in the root it lies in, is not one it reads."""
    if not isinstance(schema, dict):
        raise Unread(f"{at}: expected a schema object, found {shown(schema)}")
    # Draft-07 leaves every keyword beside a $ref unread, so one there would check nothing.
    if "$ref" in schema and set(schema) - NOTES - {"$ref"}:
        raise Unread(f"{at}: expected $ref alone, as draft-07 reads no keyword beside it")
    for key, value in schema.items():
        if key in KEYWORDS:
            KEYWORDS[key][0](value, root, f"{at}.{key}")
        elif key not in NOTES:
            *each, last = KEYWORDS
            raise Unread(
                f"{at}: `{key}` is no keyword it reads; it reads {', '.join(each)} and {last}"
            )


def _type_read(value: Any, root: Any, at: str) -> None:
    if not isinstance(value, str) or value not in TYPES:
        raise Unread(f"{at}: expected one of {', '.join(TYPES)}")


def _schemas_read(value: Any, root: Any, at: str) -> None:
    if not isinstance(value, dict):
        raise Unread(f"{at}: expected an object of schemas")
    for key, each in value.items():
        _node(each, root, f"{at}.{key}")


def _list_read(value: Any, root: Any, at: str) -> None:
    if not isinstance(value, list) or not value:
        raise Unread(f"{at}: expected a list of schemas")
    for index, each in enumerate(value):
        _node(each, root, f"{at}[{index}]")


def _strings_read(value: Any, root: Any, at: str) -> None:
    if not isinstance(value, list) or not all(isinstance(k, str) for k in value):
        raise Unread(f"{at}: expected a list of strings")


def _additional_read(value: Any, root: Any, at: str) -> None:
    if value is not False:
        raise Unread(f"{at}: expected false")


def _const_read(value: Any, root: Any, at: str) -> None:
    if not isinstance(value, str):
        raise Unread(f"{at}: expected a string")


def _whole_read(value: Any, root: Any, at: str) -> None:
    if not TYPES["integer"][0](value):
        raise Unread(f"{at}: expected a whole number")


def _number_read(value: Any, root: Any, at: str) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise Unread(f"{at}: expected a number")


def _pattern_read(value: Any, root: Any, at: str) -> None:
    try:
        re.compile(value)
    except (TypeError, re.error):
        raise Unread(f"{at}: expected a regular expression") from None


def _ref_read(value: Any, root: Any, at: str) -> None:
    target = _resolved(value, root)
    if target is None:
        raise Unread(f"{at}: expected `#/$defs/<name>`, the name of an entry of $defs")
    # A $ref or an anyOf holds the value where it is, so an entry with one at its top could lead
    # back to itself, and holding a value would never end.
    if not isinstance(target, dict) or {"$ref", "anyOf"} & set(target):
        raise Unread(f"{at}: expected an entry of $defs with neither $ref nor anyOf at its top")


def _resolved(ref: Any, root: Any) -> Any:
    """The entry of the root's $defs that the $ref names, or None where it names none."""
    found = REF.fullmatch(ref) if isinstance(ref, str) else None
    return root.get("$defs", {}).get(found.group(1)) if found else None


def held(schema: dict[str, Any], value: Any) -> Out | None:
    """The point the value is out of the schema by, a schema `checked` has read whole; None where
    it holds to it."""
    return out(schema, schema, value, ())


def out(schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]) -> Out | None:
    """The point the value at the path is out of the schema by, the root's $refs followed."""
    for key, (_, held_to) in KEYWORDS.items():
        if key in schema:
            found = held_to(schema, root, value, path)
            if found:
                return found
    return None


def _ref_out(schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]) -> Out | None:
    return out(_resolved(schema["$ref"], root), root, value, path)


def _type_out(schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]) -> Out | None:
    holds, named = TYPES[schema["type"]]
    return None if holds(value) else Out(path, named, shown(value))


def _enum_out(schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]) -> Out | None:
    allowed = schema["enum"]
    if value in allowed:
        return None
    return Out(path, "one of " + ", ".join(map(shown, allowed)), shown(value))


def _const_out(schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]) -> Out | None:
    asked = schema["const"]
    return None if value == asked else Out(path, shown(asked), shown(value))


def _required_out(
    schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]
) -> Out | None:
    missing = [k for k in schema["required"] if isinstance(value, dict) and k not in value]
    if not missing:
        return None
    return Out(path, f"the key {shown(missing[0])}", "an object without it")


def _additional_out(
    schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]
) -> Out | None:
    known = schema.get("properties", {})
    extra = [k for k in value if k not in known] if isinstance(value, dict) else []
    if not extra:
        return None
    keys = ", ".join(map(shown, known)) or "none"
    return Out(path, f"only the keys {keys}", f"the key {shown(extra[0])}")


def _properties_out(
    schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]
) -> Out | None:
    if not isinstance(value, dict):
        return None
    for key, each in schema["properties"].items():
        found = out(each, root, value[key], (*path, key)) if key in value else None
        if found:
            return found
    return None


def _items_out(schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]) -> Out | None:
    for index, each in enumerate(value if isinstance(value, list) else []):
        found = out(schema["items"], root, each, (*path, index))
        if found:
            return found
    return None


def _min_items_out(
    schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]
) -> Out | None:
    least = schema["minItems"]
    if isinstance(value, list) and len(value) < least:
        return Out(path, f"{least} or more items", str(len(value)))
    return None


def _min_length_out(
    schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]
) -> Out | None:
    least = schema["minLength"]
    if isinstance(value, str) and len(value) < least:
        return Out(path, f"a string of length {least} or more", shown(value))
    return None


def _minimum_out(
    schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]
) -> Out | None:
    least = schema["minimum"]
    if isinstance(value, (int, float)) and not isinstance(value, bool) and value < least:
        return Out(path, f"a number of at least {shown(least)}", shown(value))
    return None


def _pattern_out(
    schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]
) -> Out | None:
    # A pattern is searched for anywhere in the string, as JSON Schema has it, its anchors
    # holding it to the whole.
    asked = schema["pattern"]
    if isinstance(value, str) and not re.search(asked, value):
        return Out(path, f"a string matching {asked}", shown(value))
    return None


def _any_of_out(schema: dict[str, Any], root: Any, value: Any, path: tuple[Any, ...]) -> Out | None:
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


# Each keyword it reads, in the order a value is held to them, so the point highest in the value
# is found first: how it is read in a schema, `_<keyword>_read(value, root, at)`, which stops with
# Unread naming the place where the keyword's value is not one it reads, and the point a value is
# out by under it, `_<keyword>_out(schema, root, value, path)`, None where it holds.
KEYWORDS: dict[str, tuple[Callable[..., None], Callable[..., Out | None]]] = {
    "$ref": (_ref_read, _ref_out),
    "type": (_type_read, _type_out),
    "enum": (_strings_read, _enum_out),
    "const": (_const_read, _const_out),
    "required": (_strings_read, _required_out),
    "additionalProperties": (_additional_read, _additional_out),
    "minItems": (_whole_read, _min_items_out),
    "minLength": (_whole_read, _min_length_out),
    "minimum": (_number_read, _minimum_out),
    "pattern": (_pattern_read, _pattern_out),
    "properties": (_schemas_read, _properties_out),
    "items": (_node, _items_out),
    "anyOf": (_list_read, _any_of_out),
    "$defs": (_schemas_read, lambda *_: None),
}
