"""What pin's tests stand on beside what every plugin's tests do: pin's code on sys.path, its
modules taken by each test from here, so they are found whichever test runs first; a design
tree that holds, the README walkthrough's, for each test to change one thing of; and, for an
architecture test, a double of the pinner that writes the tree of each step and runs check.py by
the command pin:down names."""

from __future__ import annotations

import copy
import json
import os
import re
import subprocess
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
# What the walkthrough decides each decision as.
WALKTHROUGH_DECIDED = {d["id"]: d["decided"] for d in WALKTHROUGH["decisions"]}


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
    """A decision of the ID name, decided by the person, as decision makes it otherwise, with
    each field given in its place."""
    return decision(
        name,
        **{"decided": f"{name} decided", "settled_by": "user", "grounds": ["the person"], **given},
    )


def made(*decisions: dict[str, Any], questions: tuple[str, ...] = ("Q1",)) -> dict[str, Any]:
    """A design tree of the decisions, under a confirmed goal and the questions of the ids."""
    return {
        "goal": {"what": "the goal", "grounds": ["the person"]},
        "questions": [{"id": q, "what": f"does {q} hold?"} for q in questions],
        "decisions": list(decisions),
    }


with open(os.path.join(PIN, "skills", "down", "SKILL.md"), encoding="utf-8") as f:
    SKILL = f.read()
# The check command as pin:down's text names it, with pin's folder in place of
# ${CLAUDE_PLUGIN_ROOT}, as Claude Code puts it there wherever the text is loaded.
CHECK_COMMAND = (
    re.search(r"The check below is `([^`]+)`", SKILL)  # type: ignore[union-attr]
    .group(1)
    .replace("${CLAUDE_PLUGIN_ROOT}", PIN)
)


class PinnerTest(testing.FolderTest):
    """For an architecture test, a double of the pinner on one path of pin's Sequences: in the
    folder it works in, the test's own, it writes at each step the tree the step calls for, in the
    form of the walkthrough's tree, and runs check.py by the command pin:down names."""

    # Where the tree lies: a person's tree, as pinner.md's "Where the tree lies" gives it.
    path = os.path.join(".pin", "20261103-notes-json", "design-tree.json")

    def setUp(self) -> None:
        super().setUp()
        # The tree the double holds, the walkthrough's, kept on disk by each step.
        self.tree = walkthrough()

    def writes(self) -> None:
        """Writes the tree the double holds at the tree's path, as the pinner does with Write."""
        self.write(self.path, json.dumps(self.tree, indent=1))

    def writes_new(self) -> None:
        """Writes the walkthrough's tree as the pinner writes it first: the goal not confirmed,
        every decision open."""
        self.tree["goal"]["grounds"] = []
        for d in self.tree["decisions"]:
            d.update(decided=None, settled_by=None, grounds=[])
        self.writes()

    def at(self, name: str) -> dict[str, Any]:
        """The decision of the ID name in the tree the double holds."""
        return next(d for d in self.tree["decisions"] if d["id"] == name)

    def confirms_goal(self) -> None:
        """Writes the goal confirmed, the person's words as its ground."""
        self.tree["goal"]["grounds"] = ["the person, 2026-11-03"]
        self.writes()

    def rests(self, name: str, *grounds: str) -> None:
        """Writes the grounds added to those the decision of the ID name holds, left open, as the
        pinner writes a fact confirmed or told before the decision's own turn."""
        self.at(name)["grounds"] += list(grounds)
        self.writes()

    def decides(self, name: str, by: str, *grounds: str, what: str = "") -> None:
        """Writes the decision of the ID name decided, as what or else as the walkthrough decides
        it, settled by `by`, its grounds added to those it holds."""
        d = self.at(name)
        d.update(decided=what or WALKTHROUGH_DECIDED[name], settled_by=by)
        d["grounds"] += list(grounds)
        self.writes()

    def opens(self, *names: str) -> None:
        """Writes each decision of the names open again, its grounds kept."""
        for name in names:
            self.at(name).update(decided=None, settled_by=None)
        self.writes()

    def checked(self) -> tuple[int, str, str]:
        """The exit code and what check.py prints to its output and its error output, run on the
        tree's path in sh by pin:down's command, from the folder the pinner works in."""
        command = CHECK_COMMAND.replace("<design tree>", self.path)
        done = subprocess.run(["sh", "-c", command], capture_output=True, text=True, check=False)
        return done.returncode, done.stdout, done.stderr

    def holds(self, *open_now: str) -> tuple[int, str, str]:
        """What check.py gives on the tree's path where it holds, with the decisions open now."""
        said = f"Open to decide now: {', '.join(open_now)}." if open_now else "No decision is open."
        return 0, f"check.py: {self.path} holds: {check.HOLDS}\n{said}\n", ""

    def does_not_hold(self, *found: str) -> tuple[int, str, str]:
        """What check.py gives on the tree's path where it names the problems found."""
        listed = "".join(f"- {problem}\n" for problem in found)
        return 1, f"check.py: {self.path} does not hold:\n{listed}", ""
