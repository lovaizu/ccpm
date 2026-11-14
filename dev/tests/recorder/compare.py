"""Decides whether a new version of Claude Code still gives what the double of Claude Code gives,
as the compatibility test of Lane's architecture says under Test strategy. It compares a record that
record.py and convert.py made again on the new version with the record of the same state in
dev/tests/recorded/, whose lines the double gives and whose form the double's own tests hold it to.
Run it as `python3 compare.py <recorded.jsonl> <new.jsonl>`. It exits 0 where the two agree, 1 where
they differ, printing each difference on a line, and 2 where it can't read either file, as a check
that can't read its input passes nothing.

It compares the lines that hold a payload. Each event is known by its form: its hook event, its
tool, and whether the main conversation or a subagent makes it, each subagent by the order in which
it first comes. Values, such as IDs, paths, prompts, and what a command printed, change on each run,
so they never differ; the events of different callers may interleave otherwise, as a subagent runs
beside the main conversation."""

from __future__ import annotations

import sys
from typing import Any


def form(payload: dict[str, Any], callers: dict[str, int]) -> tuple[str, str, int]:
    """The event's form: its hook event, its tool, "" where it has none, and its caller, 0 for the
    main conversation and n for the nth subagent of `callers`, which it adds the event's subagent
    to where it comes first."""
    raise NotImplementedError("compare.form")


def differences(recorded: list[dict[str, Any]], new: list[dict[str, Any]]) -> list[str]:
    """Each way in which the new record's lines differ from the recorded ones, in words that name
    the recorded event by its `event`: an event of a form that one record holds more times than the
    other; a field of an event, or of its `tool_input` or `tool_response`, that one holds and the
    other doesn't; and the events of one caller in another order. An empty list where they
    agree."""
    raise NotImplementedError("compare.differences")


def main(argv: list[str]) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of `compare.py <recorded.jsonl> <new.jsonl>`: 0 and nothing
    where the records agree; 1 and each difference, a line each, where they differ; 2 and why, with
    who must fix it, where a file can't be read or isn't JSON Lines."""
    raise NotImplementedError("compare.main")


if __name__ == "__main__":
    code, out, err = main(sys.argv[1:])
    sys.stdout.write(out)
    sys.stderr.write(err)
    sys.exit(code)
