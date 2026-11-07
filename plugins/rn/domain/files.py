"""A file rn reads, held to its form, a JSON Schema in forms/ beside this module, by Lane's
reading of a schema; or refused, with why, so a check that can't read a file says so and never
passes it."""

from __future__ import annotations

import functools
import json
import os
from typing import Any

import schema

FORMS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "forms")


class Unreadable(Exception):
    """A file no check can read: it's missing, holds no JSON, or is out of its form. The message
    says why."""


@functools.cache
def form(name: str) -> dict[str, Any]:
    """The form of the name, forms/<name>.schema.json, read once."""
    with open(os.path.join(FORMS, f"{name}.schema.json"), encoding="utf-8") as f:
        return json.load(f)


def read(path: str) -> Any:
    """The JSON at the path, held to no form. Refuses, by Unreadable, a file that's missing or
    holds no JSON."""
    if not os.path.isfile(path):
        raise Unreadable(f"there is no file {path}")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise Unreadable(
            f"{path} is not JSON: {e.msg} at line {e.lineno} column {e.colno}"
        ) from None
    return data


def load(path: str, name: str) -> Any:
    """The JSON at the path, held to the form of the name. Refuses, by Unreadable, a file that's
    missing, holds no JSON, or is out of the form."""
    data = read(path)
    out = schema.held(form(name), data)
    if out:
        raise Unreadable(f"{path} is out of its form: {out.told()}")
    return data


def save(path: str, data: Any) -> None:
    """Writes the data at the path as JSON a person reads, making its folder where it's not
    there."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")
