"""The form of a reporter's report: the words each reporter of bin/ takes, the line it prints, and
the report that the guard reads back from that line."""

from __future__ import annotations

import json
import sys
from typing import TypedDict, cast

# The words that each kind of reporter takes, by the fields of its report.
_FIELDS = {"step": ("step",), "item": ("step", "item"), "result": ("result",)}


class Report(TypedDict, total=False):
    """What a reporter of bin/ prints for the guard: its `kind`, one of `step`, `item`, and
    `result`, and the step, the item, or the result it reports done."""

    kind: str
    step: str
    item: str
    result: str


def report(kind: str, words: list[str]) -> int:
    """Prints the report of a step, an item, or a result done.

    Takes: the reporter's kind, `step`, `item`, or `result`, and the words the AI gave it: the
    step; the step and the item; or the result.
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
    Gives: the report, where the output is one line that report printed; None for any other
    output.
    Changes: nothing.
    Refuses: nothing.
    """
    lines = output.splitlines()
    try:
        given = json.loads(lines[0]) if len(lines) == 1 else None
    except ValueError:
        return None
    if not isinstance(given, dict):
        return None
    fields = _FIELDS.get(given.get("kind", ""))
    if fields is None or set(given) != {"kind", *fields}:
        return None
    return cast(Report, given)
