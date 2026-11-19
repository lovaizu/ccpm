"""How Lane asks what only the plugin knows: each adapter of the plugin a Python file of its
lane/adapters/, named by what it gives, run on its own in the conversation's folder with its input
as JSON on standard input and its output as JSON on standard output, each in the form of the schema
beside this module, and Lane's route adapter run inside the guard where the plugin gives routes."""

from __future__ import annotations

from order import StartsDue
from record import Run
from rules import Rules


class AdapterFailed(Exception):
    """An adapter that failed or gave output out of its form, said with the adapter's file and what
    it gave, so that the plugin's author can mend it."""


def starts_due(plugin_root: str, cwd: str, run: Run, rules: Rules) -> StartsDue:
    """The starts due of the run, or its end, from the plugin's order.

    Takes: the plugin's folder, the conversation's folder, the run as its record stands, and the
    plugin's rules.
    Gives: what the plugin's adapter of the starts due, lane/adapters/starts_due.py, gives for
    order.order_run of the run, in the forms of starts_due.in.schema.json and
    starts_due.out.schema.json, where the plugin gives one; else what routes.starts_due gives for
    it from the routes of the rules, or from none where the rules give none.
    Changes: nothing of Lane's; the plugin's adapter may read the conversation's folder.
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
