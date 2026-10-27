"""How rn stops and checks what it is given: a stop says what went wrong and what to do, so whoever
runs rn goes on by doing it, and a value given is checked where it comes in, before anything is
read or written with it."""

from __future__ import annotations

import re

# A slug or a kind is a name that goes into a path, so it holds nothing that leads out of the folder
# it is meant for.
NAME = re.compile(r"[a-z0-9-]+")


class Stop(Exception):
    """What went wrong, and what to do about it."""


def named(value: str, what: str) -> str:
    """The value, when it is a name; stops otherwise."""
    if not NAME.fullmatch(value):
        raise Stop(
            f"rn: the {what} {value!r} is not lowercase letters, digits and hyphens alone;"
            f" give it as such, such as add-login"
        )
    return value


def given(value: str, what: str) -> str:
    """The value, when it holds some text; stops otherwise."""
    if not value.strip():
        raise Stop(f"rn: the {what} is empty; give it in words")
    return value


def joined(ids: list[str], last: str = "and") -> str:
    """The IDs in words, the last after the word given."""
    *rest, end = ids
    return f"{', '.join(rest)} {last} {end}" if rest else end
