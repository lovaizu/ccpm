"""How Lane asks a plugin's adapters what only the plugin knows: each adapter a Python file of the
plugin's lane/adapters/, named by what it gives, run in the conversation's folder with its input as
JSON on standard input and its output as JSON on standard output, each in the form of the schema
beside this module."""

from __future__ import annotations

from typing import TypedDict

from record import Run
from routes import Due


class KeptResult(TypedDict):
    """A result that the plugin keeps: the role that gave it, and the result."""

    role: str
    result: str


class AdapterFailed(Exception):
    """An adapter that failed or gave output out of its form, said with the adapter's file and what
    it gave, so that the plugin's author can mend it."""


def start_text(plugin_root: str, cwd: str, run: Run, start: Due) -> str | None:
    """The text of a start due, from the plugin's start adapter, lane/adapters/start.py.

    Takes: the plugin's folder, the conversation's folder, the run, and the start due.
    Gives: the text, in the form of start.out.schema.json; None where the plugin has no start
    adapter.
    Changes: nothing of Lane's; the adapter may read the conversation's folder.
    Refuses: AdapterFailed.
    """
    raise NotImplementedError("adapters.start_text")


def checklist(plugin_root: str, cwd: str, run: Run, role: str, step: str) -> list[str]:
    """The items of a step's checklist, from the plugin's checklist adapter,
    lane/adapters/checklist.py.

    Takes: the plugin's folder, the conversation's folder, the run, the role, and the step.
    Gives: each item, in the form of checklist.out.schema.json.
    Changes: nothing of Lane's; the adapter may read the conversation's folder.
    Refuses: AdapterFailed, also where a rule of the step asks for a checklist and the plugin has
    no checklist adapter.
    """
    raise NotImplementedError("adapters.checklist")


def kept_results(plugin_root: str, cwd: str, skill: str, words: str) -> list[KeptResult] | None:
    """The results that the plugin keeps of a run, from its kept adapter, lane/adapters/kept.py.

    Takes: the plugin's folder, the conversation's folder, the skill, and the words typed after its
    command.
    Gives: each kept result, in its order, in the form of kept.out.schema.json; None where the
    plugin has no kept adapter.
    Changes: nothing of Lane's; the adapter may read the conversation's folder.
    Refuses: AdapterFailed.
    """
    raise NotImplementedError("adapters.kept_results")
