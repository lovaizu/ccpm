"""Decides what a command or a path that a Lane takes stands for: each name in braces, such as
`{commit}`, stands for its run value where the Start gives one, and for any one value where it
gives none, and every other word stands for itself, word for word."""

from __future__ import annotations

import re
from collections.abc import Mapping

_NAME = re.compile(r"\{(\w+)\}")


def names(pattern: str) -> tuple[str, ...]:
    """Each name in braces of the pattern, in order, once each; none for a pattern without one."""
    return tuple(dict.fromkeys(_NAME.findall(pattern)))


def matches(pattern: str, given: str, values: Mapping[str, str]) -> bool:
    """Whether the command or path given is the pattern word for word, each name that `values`
    gives standing for its value alone and each other name for any one word of a command, or any
    one part of a path between slashes, never empty."""
    words, against = pattern.split(), given.split()
    return len(words) == len(against) and all(
        _word(word, values).fullmatch(each) for word, each in zip(words, against)
    )


def _word(word: str, values: Mapping[str, str]) -> re.Pattern[str]:
    parts = _NAME.split(word)
    # The split gives the text between names at the even places and each name at the odd ones.
    held = [
        re.escape(part) if place % 2 == 0 else _stands_for(part, values)
        for place, part in enumerate(parts)
    ]
    return re.compile("".join(held))


def _stands_for(name: str, values: Mapping[str, str]) -> str:
    return re.escape(values[name]) if name in values else "[^/]+"


def fill(pattern: str, values: Mapping[str, str]) -> str | None:
    """The pattern with each name in braces replaced by its value, or None where `values` gives
    no value for one of its names."""
    if any(name not in values for name in names(pattern)):
        return None
    return _NAME.sub(lambda found: values[found[1]], pattern)
