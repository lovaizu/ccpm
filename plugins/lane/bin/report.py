"""The words each reporter of bin/ takes, and the report it prints for the guard to read from its
Bash call, in the form of place.Report of hooks/lane/."""

from __future__ import annotations


def report(kind: str, words: list[str]) -> int:
    """Prints the report of a step, an item, or a result done.

    Takes: the reporter's kind, `step`, `item`, or `result`, and the words the AI gave it: the
    step; the step and the item; or the result.
    Gives: 0, once it prints the report as one line of JSON on standard output.
    Changes: nothing; the guard adds the report to the run at the Bash call's PostToolUse.
    Refuses: 2, with what the reporter takes on standard error, where the words don't fit its kind.
    """
    raise NotImplementedError("report.report")
