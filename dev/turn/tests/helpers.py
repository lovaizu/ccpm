"""What Turn's tests stand on beside what every plugin's tests do: Turn's code on sys.path, its
modules taken by each test from here, so they are found whichever test runs first; a small best
practice of the kind `note`, kept as the repository's own, for a test to change; and a test whose
folder is the top of a repository, with that best practice laid and a Call written."""

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

import files
import phases
import plan
import practices
import rounds
import runs
import testing
import throwaway

__all__ = ["files", "phases", "plan", "practices", "rounds", "runs", "testing", "throwaway"]

# A best practice of the kind `note`: two parts, three questions, the last of the whole.
PRACTICE: dict[str, Any] = {
    "goal": "The reader acts on the note.",
    "parts": [
        {"id": "summary", "what": "One sentence."},
        {"id": "steps", "what": "The steps."},
    ],
    "benefits": [
        {"id": "Q1", "about": "summary", "what": "Can the reader say what it asks?"},
        {"id": "Q2", "about": "steps", "what": "Can the reader take each step?"},
        {"id": "Q3", "about": "the whole", "what": "Does each answer come when needed?"},
    ],
    "practices": [
        {"benefit": f"Q{n}", "thinking": "Think.", "steps": [], "grounds": []} for n in (1, 2, 3)
    ],
}
# Where a run's folder lies, and the repository's best practice of `note`.
RUN = os.path.join(".turn", "20261103-tidy-note")
NOTE = os.path.join(".turn", "best-practices", "note.json")
VERIFICATION = os.path.join(RUN, "verification")
# A Call of the kind `note`, as the planner writes it.
CALL: dict[str, Any] = {
    "request": "a note on tidy",
    "kind": "note",
    "reading": "refactor-doc",
    "goal": "Someone new to tidy sorts their folder with it.",
}
# A decision the calling AI settled, as Calling Turn gives it.
SETTLED: dict[str, Any] = {
    "id": "D1",
    "what": "Which run the steps show",
    "contributes_to": [],
    "builds_on": [],
    "decided": "tidy --dry-run, then tidy",
    "settled_by": "maker",
    "grounds": ["the person, 2026-11-03"],
}


def practice() -> dict[str, Any]:
    """A copy of the best practice of `note`, for a test to change."""
    return copy.deepcopy(PRACTICE)


def call(**given: Any) -> dict[str, Any]:
    """A copy of the Call, each field given put in its place."""
    return {**copy.deepcopy(CALL), **given}


class RepositoryTest(testing.FolderTest):
    """Each test stands at the top of a repository, `base`, which holds the best practice of
    `note`, and may write a Call into the run's folder."""

    def setUp(self) -> None:
        super().setUp()
        self.write_json(NOTE, PRACTICE)

    def calls(self, data: dict[str, Any] | None = None) -> None:
        """Writes the Call, `data` or the one of `note`, into the run's folder."""
        self.write_json(os.path.join(RUN, runs.CALL), CALL if data is None else data)

    def run_data(self) -> dict[str, Any]:
        """The Run on disk."""
        return self.read_json(os.path.join(RUN, runs.RUN))

    def started(self, data: dict[str, Any] | None = None) -> str:
        """A run begun from the Call, `data` or the one of `note`: its Request."""
        self.calls(data)
        return runs.start(RUN)

    def lay_run(self, works: list[dict[str, Any]]) -> None:
        """Writes the Run of the works, the Call of `note` beside it."""
        self.calls()
        self.write_json(os.path.join(RUN, runs.RUN), {"works": works})


def work(**given: Any) -> dict[str, Any]:
    """A work of `note`, in its rounds, lying at NOTES.md, each field given put in its place."""
    made = {
        "kind": "note",
        "practice": NOTE,
        "reading": "refactor-doc",
        "folder": RUN,
        "paths": ["NOTES.md"],
        "commands": [],
        "files": [],
        "at": "rounds",
    }
    made.update(given)
    return made


def line(data: dict[str, Any]) -> str:
    """The data as one JSON line, as Turn's scripts print run values."""
    return json.dumps(data, ensure_ascii=False)


# A best practice of how a note reads, of one question about the whole.
READING = {
    "goal": "The reader takes in what it says.",
    "benefits": [{"id": "Q1", "about": "the whole", "what": "Is each fact said once?"}],
}
# The design of the note: D1 serves note/Q1 and note/Q3, D2 serves note/Q2, D3 serves D2.
TREE = {
    "goal": {"what": "A newcomer sorts their folder.", "grounds": ["the person"]},
    "questions": [{"id": f"note/Q{n}", "what": f"Q{n}?"} for n in (1, 2, 3)],
    "decisions": [
        {"id": "D1", "contributes_to": ["note/Q1", "note/Q3"], "builds_on": []},
        {"id": "D2", "contributes_to": ["note/Q2"], "builds_on": []},
        {"id": "D3", "contributes_to": ["D2"], "builds_on": ["D2"]},
    ],
}
NOTES = "# tidy\n\ntidy sorts a folder.\n\n## Steps\n\nRun tidy --dry-run.\n"


def met(*questions, line="NOTES.md:1"):
    """Answers that meet each question, by the line given."""
    return {"met": [{"question": q, "lines": [line]} for q in questions], "not_met": []}


def short(*questions):
    """Answers that meet none of the questions."""
    return {"met": [], "not_met": [{"question": q, "lacks": f"{q} lacks"} for q in questions]}


class RoundsTest(RepositoryTest):
    """A run of one work of `note`, in its rounds, its design, its Standards and the note laid."""

    def setUp(self) -> None:
        super().setUp()
        self.lay_run([work()])
        self.write_json(os.path.join(RUN, "design-tree.json"), TREE)
        self.write_json(os.path.join(RUN, "standard.json"), practices.standard(PRACTICE))
        self.write_json(os.path.join(RUN, "reading-standard.json"), READING)
        self.write("NOTES.md", NOTES)

    def answers(self, name, data):
        """Writes the Answers of the name into the round's folder."""
        self.write_json(os.path.join(VERIFICATION, name), data)

    def round(self):
        """The Round on disk."""
        return self.read_json(os.path.join(VERIFICATION, "round.json"))

    def content_round(self, *groups):
        """A content round settled, each group's Answers given in order, the generator's meeting
        every question."""
        phases.settle(RUN)
        self.answers("generator.json", met("note/Q1", "note/Q2", "note/Q3"))
        for n, data in enumerate(groups, 1):
            self.answers(f"G{n}.json", data)

    def finished(self):
        """A content round and then a reading round, each meeting every question."""
        self.content_round(met("note/Q1"), met("note/Q2"), met("note/Q3"))
        phases.settle(RUN)
        self.answers("G1.json", met("refactor-doc/Q1"))
