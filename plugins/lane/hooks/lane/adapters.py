"""How Lane asks the adapters what only the plugin knows: each adapter a Python file, the plugin's
in its lane/adapters/ named by what it gives, or Lane's route adapter in Lane's adapters/routes.py,
run in the conversation's folder with its input as JSON on standard input and its output as JSON
on standard output, each in the form of the schema beside this module, the run that the plugin's
order is given among them."""

from __future__ import annotations

from typing import TypedDict

from record import Run
from rules import Rules


class OrderMove(TypedDict, total=False):
    """A move of the run as the plugin's order sees it: its `kind`, one of `command`, `start`, and
    `result`, and the `command` typed, or the `role` started, or the `role` and the `result` it
    gave."""

    kind: str
    command: str
    role: str
    result: str


class OrderRun(TypedDict):
    """The run as the plugin's order sees it: the skill that called it, the words typed after its
    command, and each of its moves in their order."""

    skill: str
    words: str
    moves: list[OrderMove]


class StartDue(TypedDict):
    """A role to start now, by its agent type, and how many times at once."""

    role: str
    count: int


class AdapterFailed(Exception):
    """An adapter that failed or gave output out of its form, said with the adapter's file and what
    it gave, so that the plugin's author can mend it."""


def order_run(run: Run) -> OrderRun:
    """The run as the plugin's order sees it.

    Takes: the run as its record stands.
    Gives: its skill and words, and each command that called or moved it, each start made, and each
    result, in their order; a start whose Agent call failed, or that ended with no result, such as
    one stopped by TaskStop, is left out, so that the order gives its role due again.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("adapters.order_run")


def starts_due(plugin_root: str, cwd: str, run: Run, rules: Rules) -> list[StartDue]:
    """The starts due of the run, from the plugin's order.

    Takes: the plugin's folder, the conversation's folder, the run as its record stands, and the
    plugin's rules.
    Gives: each role to start now and how many times, in the form of starts_due.out.schema.json,
    from the plugin's adapter of the starts due, lane/adapters/starts_due.py, where it gives one,
    or else from Lane's route adapter, where its rules give routes; each given the plugin's folder
    and order_run of the run, in the form of starts_due.in.schema.json; none where the plugin gives
    neither.
    Changes: nothing of Lane's; the adapter may read the conversation's folder.
    Refuses: AdapterFailed.
    """
    raise NotImplementedError("adapters.starts_due")


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
