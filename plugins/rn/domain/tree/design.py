"""Decides what a design tree in form is: the run's `design-tree.json` read and held to the design
tree best practice's schema, then to each check of a condition that code can check, so that the
work always rests on a design tree in form."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from typing import Any

from fault import Wrong
from schemas import form

from tree import inputs, status, work

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
    path = os.path.join(run, "design-tree.json")
    try:
        with open(path, encoding="utf-8") as f:
            tree = json.load(f)
    except OSError:
        raise Wrong(f"{path}: no design-tree.json is there") from None
    except ValueError as error:
        raise Wrong(f"{path}: design-tree.json isn't JSON: {error}") from None
    practices = os.path.join(plugin, "domain", "best-practices")
    form.hold(
        tree, form.load(os.path.join(practices, "design-tree", "design-tree.schema.json")), path
    )
    top = os.path.dirname(os.path.dirname(os.path.abspath(run)))
    found = [*inputs.faults(tree, practices, top), *work.faults(tree), *status.faults(tree)]
    if found:
        raise Wrong(f"{path}: {found[0]}")
    return tree
