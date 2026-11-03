"""What pin's tests stand on beside what every plugin's tests do: pin's code on sys.path, its
modules taken by each test from here, so they are found whichever test runs first; and a design
tree that holds, the README walkthrough's, for each test to change one thing of."""

from __future__ import annotations

import copy
import json
import os
import re
import sys
from typing import Any

PIN = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "plugins", "pin")
)
DOMAIN = os.path.join(PIN, "core", "domain")
SCRIPTS = os.path.join(PIN, "scripts")
sys.path[:0] = [DOMAIN, SCRIPTS, os.path.join(PIN, "..", "..", "dev", "lane")]

import check
import testing
import tree

__all__ = ["check", "testing", "tree"]

with open(os.path.join(PIN, "README.md"), encoding="utf-8") as f:
    README = f.read()
# The design tree the README's walkthrough keeps, which holds.
WALKTHROUGH: dict[str, Any] = json.loads(
    re.search(r"```json\n(.*?)```", README, re.DOTALL).group(1)  # type: ignore[union-attr]
)


def walkthrough() -> dict[str, Any]:
    """A copy of the walkthrough's design tree, for a test to change."""
    return copy.deepcopy(WALKTHROUGH)


def decision(name: str, **given: Any) -> dict[str, Any]:
    """A decision of the ID name, open, serving Q1 and building on none, with each field given
    in its place."""
    made: dict[str, Any] = {
        "id": name,
        "what": f"what {name} decides",
        "contributes_to": ["Q1"],
        "builds_on": [],
        "decided": None,
        "settled_by": None,
        "grounds": [],
    }
    made.update(given)
    return made


def settled(name: str, **given: Any) -> dict[str, Any]:
    """A decision of the ID name, decided by the person, as decision makes it otherwise."""
    return decision(
        name, decided=f"{name} decided", settled_by="user", grounds=["the person"], **given
    )


def made(*decisions: dict[str, Any], questions: tuple[str, ...] = ("Q1",)) -> dict[str, Any]:
    """A design tree of the decisions, under a confirmed goal and the questions of the ids."""
    return {
        "goal": {"what": "the goal", "grounds": ["the person"]},
        "questions": [{"id": q, "what": f"does {q} hold?"} for q in questions],
        "decisions": list(decisions),
    }
