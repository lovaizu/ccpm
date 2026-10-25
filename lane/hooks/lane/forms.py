"""The forms in_form holds an output to, each a file of the plugin: a `.json` file is a JSON Schema
of the keywords `schema` reads, held to by the output as JSON, or by each of its lines where the
output is named `.jsonl`; a `.md` file is a Markdown template, held to as `template` reads it. A
form is read whole before any output is held to it, and a file that is no form lane reads is
refused."""

from __future__ import annotations

import json
import os
from typing import Any, Union

import schema
import template

Form = Union[dict[str, Any], template.Template]


def read(path: str) -> Form:
    """The form the file at the path gives; stops with ValueError saying why where it gives none
    lane reads."""
    kind = os.path.splitext(path)[1]
    if kind not in (".json", ".md"):
        raise ValueError("is neither a .json schema nor a .md template")
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as error:
        raise ValueError(f"cannot be read: {error.strerror}") from None
    try:
        if kind == ".md":  # pragma: no mutate
            return template.read(text)
        given = json.loads(text)
        schema.checked(given)
    except ValueError as why:
        raise ValueError(f"is no form lane reads: {why}") from None
    return given


def held(form: Form, output: str, text: str) -> str:
    """The point the text written to the output is out of the form by; "" where it holds."""
    if isinstance(form, template.Template):
        return template.held(form, text)
    if not output.endswith(".jsonl"):
        return value_held(form, text, 0, "")
    for number, line in enumerate(text.splitlines()):
        told = value_held(form, line, number, f"line {number + 1}, ")
        if told:
            return told
    return ""


def value_held(form: dict[str, Any], text: str, before: int, where: str) -> str:
    """The point the JSON text, after so many lines before it, is out of the schema by, its place
    in the value headed by where; "" where it holds."""
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        rest = text[error.pos :].partition("\n")[0]
        found = schema.shown(rest) if rest else "the end of the line"
        at = f"line {before + error.lineno}, column {error.colno}"
        return f"{at}: expected JSON ({error.msg}), found {found}"
    out = schema.held(form, value)
    return f"{where}{out.told()}" if out else ""
