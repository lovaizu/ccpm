"""How Lane asks what only the plugin knows: each adapter of the plugin a Python file of its
lane/adapters/, named by what it gives, run on its own in the conversation's folder with its input
as JSON on standard input and its output as JSON on standard output, each in the form of the schema
beside this module, and Lane's route adapter run inside the guard where the plugin gives routes."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Any, TypedDict, cast

import routes
from json_form import held
from order import StartsDue, order_run
from record import Run
from rules import Rules, Step


class EarlierTurn(TypedDict):
    """An earlier turn of the main conversation in the run: its role, by the skill's name, the
    prompt that began it, empty for the run's first turn, and the latest command that it called,
    None for none."""

    role: str
    prompt: str
    command: str | None


class Asked(TypedDict):
    """What a start or a turn asks the plugin's adapter of the rules for: its role, the prompt it
    began with, the latest command that the turn called, None for none and for a start, and each
    earlier turn of the run, oldest first, none for a start."""

    role: str
    prompt: str
    command: str | None
    turns: list[EarlierTurn]


class AdapterFailed(Exception):
    """An adapter that couldn't give its answer, as it is missing, can't be run, fails, or gives
    output out of its form, said with what Lane couldn't check and why: the adapter's file and what
    it gave."""


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
        return cast(StartsDue, _ask(plugin_root, cwd, "starts_due", given, "which starts are due"))
    if "routes" in rules:
        return routes.starts_due(rules["routes"], order_run(run))
    return {"ends": True} if turn_ended else {"starts": []}


def given_steps(plugin_root: str, cwd: str, run: Run, asked: Asked) -> list[Step]:
    """The steps and rules of a start, or of a turn of the main conversation, from the plugin's
    adapter of the rules, lane/adapters/rules.py.

    Takes: the plugin's folder, the conversation's folder, the run, and what's asked: the start's
    role with the prompt that the main conversation gave it and no turn, or, for a turn, the main
    conversation's role, by the skill's name, with the prompt that began the turn as Claude Code
    gives it and each earlier turn of the run, oldest first.
    Gives: the steps of the start or the turn, each with its rules, in the forms of
    rules.in.schema.json and rules.out.schema.json.
    Changes: nothing of Lane's; the adapter may read the conversation's folder.
    Refuses: AdapterFailed, also where the plugin has no adapter of the rules, saying that Lane
    couldn't check the role's steps, as the plugin's folder holds no lane/adapters/rules.py.
    """
    what = f"the steps of {asked['role']}"
    if not os.path.isfile(_adapter(plugin_root, "rules.py")):
        raise AdapterFailed(
            f"Lane couldn't check {what}: they come from the plugin's adapter of the rules,"
            f" lane/adapters/rules.py, which {plugin_root} doesn't hold"
        )
    given = {"run": {"skill": run.skill, "words": run.words, "session": run.session_id}, **asked}
    return _ask(plugin_root, cwd, "rules", given, what)["steps"]


def _adapter(plugin_root: str, name: str) -> str:
    """The path of the plugin's adapter of the name."""
    return os.path.join(plugin_root, "lane", "adapters", name)


def _ask(plugin_root: str, cwd: str, name: str, given: Any, what: str) -> Any:
    """What the plugin's adapter of the name gives for the input, held to its schema; where it
    gives none, AdapterFailed saying that Lane couldn't check what the call names, and why."""
    path = _adapter(plugin_root, f"{name}.py")
    unchecked = f"Lane couldn't check {what}: {path}"
    try:
        done = subprocess.run(
            [sys.executable, path],
            input=json.dumps(given),
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as error:
        raise AdapterFailed(f"{unchecked} can't be run: {error}") from None
    if done.returncode:
        raise AdapterFailed(f"{unchecked} failed: {done.stderr.strip()}")
    try:
        gave = json.loads(done.stdout)
    except ValueError:
        raise AdapterFailed(f"{unchecked} gave no JSON: {done.stdout.strip()}") from None
    left = held(gave, f"{name}.out.schema.json")
    if left is not None:
        raise AdapterFailed(f"{unchecked} gave out of its form, at {left}")
    return gave
