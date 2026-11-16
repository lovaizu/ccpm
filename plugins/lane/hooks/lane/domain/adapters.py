"""How a start's text, a Step's Items, and the Kept results come from the user's plugin: the adapter
that lanes.json names, run in the hook event's cwd, what it's handed, and how its output is read,
with Lane's own text where the plugin names no adapter of a start's text."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any

# The text a start goes with where the plugin names no adapter of a start's text.
TEXT = "Carry out your steps"


class AdapterFailed(Exception):
    """An adapter that exited other than 0, printed what isn't in its form, or couldn't run, with
    why, so that the guard says who must fix it."""


@dataclass(frozen=True)
class StartText:
    """A start's text, and the run values that the role's Lanes hold it to."""

    text: str
    values: Mapping[str, str]


@dataclass(frozen=True)
class NoWork:
    """That no work waits for a start, such as while all of it waits for the person's approval, with
    why, as the adapter printed it in place of a text."""

    why: str


@dataclass(frozen=True)
class Running:
    """A Start of the Run that runs, as the adapter is handed it."""

    role: str
    text: str
    values: Mapping[str, str]


@dataclass(frozen=True)
class KeptResult:
    """One Result that the user's plugin keeps in its own records, by the role that gave it."""

    role: str
    result: str


def start_text(
    program: str | None, role: str, running: Sequence[Running], words: str, cwd: str
) -> StartText | NoWork:
    """The text and run values of one start due, or that no work waits for it.

    Takes: the adapter of a start's text that lanes.json names, or None; the role due; the text and
    values of each Start of the Run that runs; the words typed after the skill's command; and the
    hook event's cwd.
    Gives: what the adapter prints, `{"text": ..., "values": {<name>: <value>}}`, its values
    optional, given the role as its one argument and `{"running": [{"role": ..., "text": ...,
    "values": {...}}]}` on standard input; NoWork, with why, where the adapter prints
    `{"none": <why>}`, as no work waits for that start; or, with no adapter, Lane's text, `Carry
    out your steps`, and the words typed, with no values.
    Changes: nothing of Lane's; the adapter may read the plugin's files.
    Refuses: AdapterFailed, naming the adapter and why, where it can't run, exits other than 0
    (why being what it wrote to standard error), or prints other than a JSON object with a
    string `text` or `none` and, beside `text`, `values` that map strings to strings.
    Carries: S5 `G->>A: asks for the text of each start due, with each Start that runs`, and its
    `A-->>G` answers: `the text, and the run values` and, after `it gives none, as no work waits
    for that start`, and each way it fails, `why`.
    """
    if program is None:
        return StartText(f"{TEXT}: {words}" if words else TEXT, {})
    handed = {"running": [dict(asdict(each), values=dict(each.values)) for each in running]}
    printed = _run(program, [role], handed, cwd)
    if "none" in printed:
        return NoWork(_text(program, printed, "none"))
    values = printed.get("values", {})
    if not isinstance(values, dict) or not all(
        isinstance(v, str) for v in [*values, *values.values()]
    ):
        raise AdapterFailed(f"{program}: `values` must map each name to a string, not {values!r}")
    return StartText(_text(program, printed, "text"), values)


def _run(program: str, args: Sequence[str], handed: Mapping[str, Any], cwd: str) -> dict[str, Any]:
    """What the adapter printed, as a JSON object, given the arguments and, on standard input, what
    it's handed, run in the folder."""
    try:
        done = subprocess.run(
            [program, *args],
            input=json.dumps(handed),
            capture_output=True,
            text=True,
            cwd=cwd,
            check=False,
        )
    except OSError as e:
        raise AdapterFailed(f"{program} can't run: {e.strerror}") from e
    if done.returncode != 0:
        why = done.stderr.strip() or f"it exited {done.returncode}"
        raise AdapterFailed(f"{program} failed: {why}")
    try:
        printed = json.loads(done.stdout)
    except ValueError as e:
        raise AdapterFailed(f"{program} printed what isn't JSON: {done.stdout.strip()!r}") from e
    if not isinstance(printed, dict):
        raise AdapterFailed(f"{program} printed {printed!r}, not a JSON object")
    return printed


def _text(program: str, printed: Mapping[str, Any], key: str) -> str:
    """The string that the adapter printed under the key."""
    given = printed.get(key)
    if not isinstance(given, str):
        raise AdapterFailed(f'{program} printed no `"{key}"` that is a string: {dict(printed)!r}')
    return given


def step_items(
    program: str, role: str, step: int, values: Mapping[str, str], cwd: str
) -> tuple[str, ...]:
    """The IDs of the Items of a Step's checklist this run.

    Takes: the adapter of a step's items that lanes.json names; the role or skill; the Step's
    number, Step n of a run of step.py or the Step due of a run of item.py; the run values of the
    role's Start, none for the skill; and the hook event's cwd, to run it in.
    Gives: what the adapter prints, `{"items": [<id>, ...]}`, given the role and the Step's number
    as its two arguments and `{"values": {<name>: <value>}}` on standard input; none where the
    Step keeps no checklist this run.
    Changes: nothing of Lane's; the adapter may read the plugin's files.
    Refuses: AdapterFailed, naming the adapter and why, where it can't run, exits other than 0
    (why being what it wrote to standard error), or prints other than a JSON object whose `items`
    is a list of strings.
    Carries: S6 `G->>A: asks for the Step's Items, with the role, Step n, and the Start's run
    values`, `G->>A: asks for the Items of the Step due, with the role and the Start's run values`,
    each one's `A-->>G: each Item's ID`, and each one's `alt the adapter fails`.
    """
    printed = _run(program, [role, str(step)], {"values": dict(values)}, cwd)
    items = printed.get("items")
    if not isinstance(items, list) or not all(isinstance(each, str) for each in items):
        raise AdapterFailed(f"{program}: `items` must be a list of strings, not {items!r}")
    return tuple(items)


def kept_results(program: str, words: str, cwd: str) -> tuple[KeptResult, ...]:
    """The Results that the user's plugin keeps, in the order the run gave them.

    Takes: the adapter of the plugin's records that lanes.json names, the words typed after the
    skill's command, and the hook event's cwd.
    Gives: the Results of what the adapter prints, `{"results": [{"role": ..., "result": ...}]}`,
    given no argument and `{"words": <the words>}` on standard input, as words that begin with `-`
    would read as an option where they came as an argument; none where it gives none.
    Changes: nothing of Lane's.
    Refuses: AdapterFailed, naming the adapter and why, where it can't run, exits other than 0
    (why being what it wrote to standard error), or prints other than a JSON object whose
    `results` is a list of objects, each with a string `role` and a string `result`.
    Carries: S7 `G->>A: asks for the Kept results, with those words`, and its `A-->>G` answers.
    """
    printed = _run(program, [], {"words": words}, cwd)
    results = printed.get("results")
    if not isinstance(results, list) or not all(_kept(each) for each in results):
        raise AdapterFailed(
            f'{program}: `results` must be a list of {{"role": ..., "result": ...}}, each a'
            f" string, not {results!r}"
        )
    return tuple(KeptResult(each["role"], each["result"]) for each in results)


def _kept(given: Any) -> bool:
    """Whether one of the results that the adapter printed is a Kept result in its form."""
    return (
        isinstance(given, dict)
        and set(given) == {"role", "result"}
        and all(isinstance(v, str) for v in given.values())
    )
