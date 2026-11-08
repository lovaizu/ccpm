"""Holds what a role writes to its output to one of the forms it takes.

A form is a `.json` JSON Schema, which schema.py reads as a form, or a `.md` Markdown template. A
JSON output holds to the schema, and so does each line of a `.jsonl` one. A Markdown output holds
each heading of its template in the template's order, and each key of the template's frontmatter.
"""

from __future__ import annotations

import json
import os
import re

import command
import plugin
import schema

import lanes

WORDING = "Write `<output>` in the form of `<form>`."
# A heading of a Markdown text.
HEADING = re.compile(r"^#{1,6} .+$", re.MULTILINE)


def stands(found: dict[str, list[str]]) -> list[str]:
    """What keeps the forms from standing. A lane names each form by its path in the plugin, and
    each form is a `.json` JSON Schema or a `.md` template."""
    faults = []
    for form in found["form"]:
        if not form.startswith(command.ROOT + "/"):
            faults.append(
                f"in_form takes the form `{form}` by its path in the plugin, as"
                f" `{command.ROOT}/<path>`"
            )
        elif not form.endswith((".json", ".md")):
            faults.append(
                f"in_form takes a form that is a `.json` JSON Schema or a `.md` template, not"
                f" `{form}`"
            )
    return faults


def readable(form: str) -> str | None:
    """What keeps Lane from reading the form at the path, or None where it reads it."""
    try:
        if form.endswith(".md"):
            _read(form)
        else:
            _schema(form)
    except lanes.Unchecked as why:
        return str(why)
    return None


def check(call: lanes.Call, given: dict[str, list[str]], context: lanes.Context) -> str | None:
    """Where the text that the call writes to an output is out of every form, or None where the
    call goes on. The check holds an Edit with its change made to the file's text.

    It raises `lanes.Unchecked` where a form isn't there or isn't one that Lane reads.
    """
    if call.tool not in ("Write", "Edit"):
        return None
    path = lanes.called_path(call) or ""
    if not lanes.under(path, given["output"]):
        return None
    return _out(path, _written(call, path), given["form"], "The content")


def end(given: dict[str, list[str]], calls: list[lanes.Call], context: lanes.Context) -> str | None:
    """Where an output that's there is out of every form, or None, as a command may have written
    it.

    It raises `lanes.Unchecked` where a form isn't there or isn't one that Lane reads.
    """
    for path in given["output"]:
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                out = _out(path, f.read(), given["form"], f"`{path}`")
            if out is not None:
                return out
    return None


def _written(call: lanes.Call, path: str) -> str:
    """The text that the call leaves in the file: a Write's content, or an Edit's change made."""
    if call.tool == "Write":
        return str(call.input.get("content", ""))
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        text = ""
    old, new = str(call.input.get("old_string", "")), str(call.input.get("new_string", ""))
    return text.replace(old, new) if call.input.get("replace_all") else text.replace(old, new, 1)


def _out(path: str, text: str, forms: list[str], what: str) -> str | None:
    """Where the text is out of the first form, or None where it holds to any form. what names the
    text in the message."""
    found = []
    for form in forms:
        out = _held(path, text, form, what)
        if out is None:
            return None
        found.append(out)
    return found[0]


def _held(path: str, text: str, form: str, what: str) -> str | None:
    """Where the output's text is out of the form, or None where it holds."""
    if form.endswith(".md"):
        return _template_out(text, form, what)
    loaded = _schema(form)
    if path.endswith(".jsonl"):
        for number, line in enumerate(text.splitlines(), 1):
            if line.strip():
                out = _value_out(line, loaded, f"Line {number}", form)
                if out:
                    return out
        return None
    return _value_out(text, loaded, what, form)


def _value_out(text: str, loaded: dict, what: str, form: str) -> str | None:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as why:
        return f"{what} is no JSON at line {why.lineno}, column {why.colno}: {why.msg}"
    out = schema.held(loaded, value)
    return f"{what} is out of `{form}`: {out.told()}" if out else None


def _read(form: str) -> str:
    try:
        with open(form, encoding="utf-8") as f:
            return f.read()
    except OSError:
        raise lanes.Unchecked(f"the form {form} isn't there") from None


def _schema(form: str) -> dict:
    """The JSON Schema in the form's file, read whole as a form."""
    try:
        loaded = json.loads(_read(form))
        schema.checked(loaded)
    except (json.JSONDecodeError, schema.Unread) as why:
        raise lanes.Unchecked(f"the form {form} is no form that Lane reads: {why}") from None
    return loaded


def _template_out(text: str, form: str, what: str) -> str | None:
    """Where the Markdown text lacks a heading of the template, in its order, or a key of the
    template's frontmatter, or None where it holds them all."""
    template = _read(form)
    keys = plugin.frontmatter(template)
    have = plugin.frontmatter(text)
    for key in keys:
        if key not in have:
            return f"{what} is out of `{form}`: its frontmatter lacks the key `{key}`."
    headings = HEADING.findall(text)
    at = 0
    for heading in HEADING.findall(template):
        if heading in headings[at:]:
            at = headings.index(heading, at) + 1
        else:
            return f"{what} is out of `{form}`: it lacks the heading `{heading}`."
    return None
