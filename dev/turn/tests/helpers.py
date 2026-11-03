"""What Turn's tests stand on beside what every plugin's tests do: Turn's code on sys.path, its
modules taken by each test from here, so they are found whichever test runs first; and a run's
folder that holds, for each test to change one thing of."""

from __future__ import annotations

import copy
import json
import os
import sys
from typing import Any

TURN = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "plugins", "turn")
)
DOMAIN = os.path.join(TURN, "core", "domain")
SCRIPTS = os.path.join(TURN, "scripts")
sys.path[:0] = [DOMAIN, SCRIPTS, os.path.join(TURN, "..", "..", "dev", "lane")]

import answering
import answers
import designs
import files
import practices
import runs
import starts
import templates
import testing
import throwaway
import tree

# A work's command as designer writes it, inside Turn's throwaway.py.
THROWN = (
    f"python3 {os.path.join(SCRIPTS, 'throwaway.py')} --file Downloads/a.jpg"
    " -- 'python3 tidy.py --dry-run ~/Downloads'"
)
__all__ = [
    "answering",
    "answers",
    "designs",
    "files",
    "practices",
    "runs",
    "starts",
    "templates",
    "testing",
    "throwaway",
    "tree",
]

# A template of the kind `readme`: two parts, three questions, the last of the whole.
TEMPLATE: dict[str, Any] = {
    "goal": "The reader starts using the product only when it serves their work.",
    "parts": [
        {"id": "summary", "what": "One sentence."},
        {"id": "walkthrough", "what": "One run."},
    ],
    "benefits": [
        {"id": "Q1", "about": "summary", "what": "Can the reader say what it does?"},
        {"id": "Q2", "about": "walkthrough", "what": "Can the reader get the result?"},
        {"id": "Q3", "about": "the whole", "what": "Does each answer come when needed?"},
    ],
    "practices": [
        {"benefit": f"Q{n}", "thinking": "Think.", "steps": [], "grounds": []} for n in (1, 2, 3)
    ],
}
# The refactoring template, of one question about the whole.
REFACTORING: dict[str, Any] = {
    "goal": "The reader takes in what it says.",
    "benefits": [{"id": "Q1", "about": "the whole", "what": "Is each fact said once?"}],
    "practices": [{"benefit": "Q1", "thinking": "Think.", "steps": [], "grounds": []}],
}


def question(n: int, kind: str = "readme") -> str:
    """The ID a run gives question n of the kind's template."""
    return f"{kind}/Q{n}"


def decision(name: str, serves: list[str], on: list[str] | None = None) -> dict[str, Any]:
    """A decision of the ID name, decided, serving what it is given and building on `on`."""
    return {
        "id": name,
        "what": f"what {name} decides",
        "contributes_to": serves,
        "builds_on": on or [],
        "decided": f"{name} decided",
        "settled_by": "reasoning",
        "grounds": ["the goal"],
    }


# A run's folder that holds, its files by name: D1 serves Q1, D2 serves Q2, D3 serves D2 and builds
# on it; the work is README.md alone, of one part.
RUN: dict[str, Any] = {
    "run.json": {
        "kind": "readme",
        "template": "plugins/turn/core/domain/best-practices/readme.json",
        "refactoring": "refactor-doc",
        "groups": [
            {"id": "G1", "questions": ["readme/Q1"]},
            {"id": "G2", "questions": ["readme/Q2"]},
            {"id": "G3", "questions": ["readme/Q3"]},
        ],
        "refactoring_groups": [{"id": "G1", "questions": ["refactor-doc/Q1"]}],
    },
    "standard.json": templates.standard(TEMPLATE),
    "refactoring-standard.json": templates.standard(REFACTORING),
    "design-tree.json": {
        "goal": {"what": "A newcomer sorts their folder.", "grounds": ["the person"]},
        "questions": [
            {"id": question(n), "what": TEMPLATE["benefits"][n - 1]["what"]} for n in (1, 2, 3)
        ],
        "decisions": [
            decision("D1", [question(1), question(3)]),
            decision("D2", [question(2)]),
            decision("D3", ["D2"], ["D2"]),
        ],
    },
    "work.json": {
        "paths": ["README.md"],
        "commands": [THROWN],
        "parts": [{"id": "P1", "decisions": ["D1", "D2", "D3"], "paths": ["README.md"]}],
    },
}
WORK = "# tidy\n\ntidy sorts a folder.\n\n## Walkthrough\n\nRun tidy --dry-run.\n"


def run() -> dict[str, Any]:
    """A copy of the run's files, for a test to change."""
    return copy.deepcopy(RUN)


class RunTest(testing.FolderTest):
    """Each test has a run's folder, `run`, in its own folder, and the work beside it."""

    folder = ".turn/20261103-tidy-readme"

    def lay(self, made: dict[str, Any] | None = None, work: str = WORK) -> None:
        """Writes each file of the run, `made` or the one that holds, and the work."""
        for name, data in (RUN if made is None else made).items():
            self.write(os.path.join(self.folder, name), json.dumps(data))
        self.write("README.md", work)
