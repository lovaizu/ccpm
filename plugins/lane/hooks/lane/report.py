"""The form of a reporter's report: the words each reporter of bin/ takes, the line it prints, and
the report that the guard reads back from that line."""

from __future__ import annotations

import json
import sys
from typing import TypedDict, cast

# The words that each kind of reporter takes, by the fields of its report.
_FIELDS = {
    "step": ("step",),
    "item": ("step", "item"),
    "result": ("result",),
    "back": ("step",),
}


class Report(TypedDict, total=False):
    """What a reporter of bin/ prints for the guard: its `kind`, one of `step`, `item`, `result`,
    and `back`, and the step, the item, or the result it reports done, or the step it goes back
    to."""

    kind: str
    step: str
    item: str
    result: str


def report(kind: str, words: list[str]) -> int:
    """Prints the report of a step, an item, or a result done, or of a step gone back to.

    Takes: the reporter's kind, `step`, `item`, `result`, or `back`, and the words the AI gave it:
    the step; the step and the item; the result; or the step it goes back to.
    Gives: 0, once it prints the report as one line of JSON on standard output.
    Changes: nothing; the guard adds the report to the run at the Bash call's PostToolUse.
    Refuses: 2, with what the reporter takes on standard error, where the words don't fit its kind.
    """
    fields = _FIELDS[kind]
    if len(words) != len(fields):
        print(f"lane-{kind} takes {' '.join(f'<{f}>' for f in fields)}", file=sys.stderr)
        return 2
    print(json.dumps({"kind": kind, **dict(zip(fields, words))}))
    return 0


def read_report(output: str) -> Report | None:
    """The report that a reporter's Bash call printed.

    Takes: the standard output of a Bash call.
    Gives: the report, where the output is the JSON of a report, as report prints it, each value
    text; None for any other output.
    Changes: nothing.
    Refuses: nothing.
    """
    try:
        given = json.loads(output)
    except ValueError:
        return None
    # A reporter prints only text, its kind among it.
    if not isinstance(given, dict) or not all(isinstance(each, str) for each in given.values()):
        return None
    fields = _FIELDS.get(given.get("kind", ""))
    if fields is None or set(given) != {"kind", *fields}:
        return None
    return cast(Report, given)
