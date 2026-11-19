"""How Lane asks a plugin's adapters what only the plugin knows: each adapter a Python file of the
plugin's lane/adapters/, named by what it gives, run in the conversation's folder with its input as
JSON on standard input and its output as JSON on standard output, each in the form of the schema
beside this module."""

from __future__ import annotations

from typing import TypedDict

from record import Run


class KeptResult(TypedDict):
    """A result that the plugin keeps: the role that gave it, and the result."""

    role: str
    result: str


class AdapterFailed(Exception):
    """An adapter that failed or gave output out of its form, said with the adapter's file and what
    it gave, so that the plugin's author can mend it."""


def start_texts(plugin_root: str, cwd: str, run: Run, role: str) -> list[str] | None:
    """The texts of a role due, one for each time it starts at once, from the plugin's start
    adapter, lane/adapters/start.py.

    Takes: the plugin's folder, the conversation's folder, the run, and the role due, by its agent
    type.
    Gives: each text, in the form of start.out.schema.json, so that the role starts as many times
    as the texts given; None where the plugin has no start adapter, so that the role starts once.
    Changes: nothing of Lane's; the adapter may read the conversation's folder.
    Refuses: AdapterFailed.
    """
    raise NotImplementedError("adapters.start_texts")


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


def joined_result(plugin_root: str, cwd: str, run: Run, role: str, results: list[str]) -> str:
    """The one result of a lane whose route started its role several times, from the results of
    those starts, by the plugin's join adapter, lane/adapters/join.py.

    Takes: the plugin's folder, the conversation's folder, the run, the role, and each start's
    result, in the order the starts were added.
    Gives: the one result, in the form of join.out.schema.json, by which the lane moves on.
    Changes: nothing of Lane's; the adapter may read the conversation's folder.
    Refuses: AdapterFailed, also where the plugin has no join adapter.
    """
    raise NotImplementedError("adapters.joined_result")


def kept_results(
    plugin_root: str, cwd: str, skill: str, words: str
) -> list[list[KeptResult]] | None:
    """The results that the plugin keeps of a run, each chain's in its order, from its kept
    adapter, lane/adapters/kept.py.

    Takes: the plugin's folder, the conversation's folder, the skill, and the words typed after its
    command.
    Gives: each chain, with its kept results in their order, in the form of kept.out.schema.json;
    None where the plugin has no kept adapter.
    Changes: nothing of Lane's; the adapter may read the conversation's folder.
    Refuses: AdapterFailed.
    """
    raise NotImplementedError("adapters.kept_results")
