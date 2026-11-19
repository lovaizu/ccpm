"""How Lane asks what only the plugin knows: each adapter of the plugin a Python file of its
lane/adapters/, named by what it gives, run on its own in the conversation's folder with its input
as JSON on standard input and its output as JSON on standard output, each in the form of the schema
beside this module, and Lane's route adapter run inside the guard where the plugin gives routes."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Any, cast

import routes
from json_form import held
from order import StartsDue, order_run
from record import Run
from rules import Rules, Step


class AdapterFailed(Exception):
    """An adapter that failed or gave output out of its form, said with the adapter's file and what
    it gave, so that the plugin's author can mend it."""


def starts_due(plugin_root: str, cwd: str, run: Run, rules: Rules, turn_ended: bool) -> StartsDue:
    """The starts due of the run, or its end, from the plugin's order.

    Takes: the plugin's folder, the conversation's folder, the run as its record stands, the
    plugin's rules, and whether the main conversation's turn has just ended, its end let through.
    Gives: what the plugin's adapter of the starts due, lane/adapters/starts_due.py, gives for
    order.order_run of the run, in the forms of starts_due.in.schema.json and
    starts_due.out.schema.json, where the plugin gives one; else what routes.starts_due gives for
    it, where the rules give routes; else, for a plugin that gives no order, no start due, so that
    its run holds the main conversation to its skill's steps alone, and that the run ends where the
    turn has ended.
    Changes: nothing of Lane's; the plugin's adapter may read the conversation's folder.
    Refuses: AdapterFailed.
    """
    if os.path.isfile(_adapter(plugin_root, "starts_due.py")):
        given = {"run": order_run(run)}
        return cast(StartsDue, _ask(plugin_root, cwd, "starts_due", given))
    if "routes" in rules:
        return routes.starts_due(rules["routes"], order_run(run))
    return {"ends": True} if turn_ended else {"starts": []}


def given_steps(plugin_root: str, cwd: str, run: Run, role: str, prompt: str) -> list[Step]:
    """The steps and rules of a start, from the plugin's adapter of the rules,
    lane/adapters/rules.py.

    Takes: the plugin's folder, the conversation's folder, the run, the start's role, and the
    prompt that the main conversation gave it.
    Gives: the start's steps, each with its rules, in the forms of rules.in.schema.json and
    rules.out.schema.json.
    Changes: nothing of Lane's; the adapter may read the conversation's folder.
    Refuses: AdapterFailed, also where the plugin has no adapter of the rules, naming
    lane/adapters/rules.py and the role, for the plugin's author to add it.
    """
    if not os.path.isfile(_adapter(plugin_root, "rules.py")):
        raise AdapterFailed(
            f"Lane: {role} takes its steps from the plugin's adapter of the rules, which the"
            f" plugin doesn't give. The plugin's author adds lane/adapters/rules.py in"
            f" {plugin_root}, or the role's steps to lane/rules.json."
        )
    given = {"run": {"skill": run.skill, "words": run.words}, "role": role, "prompt": prompt}
    return _ask(plugin_root, cwd, "rules", given)["steps"]


def _adapter(plugin_root: str, name: str) -> str:
    """The path of the plugin's adapter of the name."""
    return os.path.join(plugin_root, "lane", "adapters", name)


def _ask(plugin_root: str, cwd: str, name: str, given: Any) -> Any:
    """What the plugin's adapter of the name gives for the input, held to its schema."""
    path = _adapter(plugin_root, f"{name}.py")
    done = subprocess.run(
        [sys.executable, path],
        input=json.dumps(given),
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    mend = "The plugin's author mends it."
    if done.returncode:
        raise AdapterFailed(f"Lane: {path} failed: {done.stderr.strip()}. {mend}")
    try:
        gave = json.loads(done.stdout)
    except ValueError:
        raise AdapterFailed(f"Lane: {path} gave no JSON: {done.stdout.strip()}. {mend}") from None
    left = held(gave, f"{name}.out.schema.json")
    if left is not None:
        raise AdapterFailed(f"Lane: {path} gave out of its form, at {left}. {mend}")
    return gave
