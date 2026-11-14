"""Decides what a command or a path that a Lane takes stands for: each name in braces, such as
`{commit}`, stands for its run value where the Start gives one, and for any one value where it
gives none, and every other word stands for itself, word for word."""

from __future__ import annotations

from collections.abc import Mapping


def names(pattern: str) -> tuple[str, ...]:
    """Each name in braces of the pattern, in order, once each; none for a pattern without one."""
    raise NotImplementedError("pattern.names")


def matches(pattern: str, given: str, values: Mapping[str, str]) -> bool:
    """Whether the command or path given is the pattern word for word, each name that `values`
    gives standing for its value alone and each other name for any one word of a command, or any
    one part of a path between slashes, never empty."""
    raise NotImplementedError("pattern.matches")


def fill(pattern: str, values: Mapping[str, str]) -> str | None:
    """The pattern with each name in braces replaced by its value, or None where `values` gives
    no value for one of its names."""
    raise NotImplementedError("pattern.fill")
