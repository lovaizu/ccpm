"""Decides what a design tree in form is: the run's `design-tree.json` read and held to the design
tree best practice's schema, then to each check of a condition that code can check, so that the
work always rests on a design tree in form."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

# The design tree, as its schema gives it.
Tree = Mapping[str, Any]


def read(run: str, plugin: str) -> Tree:
    """The run's design tree, held to its form.

    Takes: the run's folder, `.rn/<yyyymmdd>-<goal>/`, and rn's folder, where the schema and the
    best practices lie.
    Gives: the design tree, once it holds the schema and the checks of inputs.py, work.py, and
    status.py.
    Refuses: Wrong, naming the first fault, where the file isn't there, isn't JSON, leaves the
    schema, or fails a check."""
    raise NotImplementedError("design.read")
