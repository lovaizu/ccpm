"""The form of a reporter's report: the words each reporter of bin/ takes, the line it prints, and
the report that the guard reads back from that line."""

from __future__ import annotations

from typing import TypedDict


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
    raise NotImplementedError("report.report")


def read_report(output: str) -> Report | None:
    """The report that a reporter's Bash call printed.

    Takes: the standard output of a Bash call.
    Gives: the report, where the output is one line that report printed; None for any other
    output.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("report.read_report")
