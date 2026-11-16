#!/usr/bin/env python3
"""Decides how the Cut of a start reaches Lane, as Lane's adapter of a start's text: the run of the
folder Lane runs it in, the Cut that tree.py's code gives there, set as one JSON line of the text,
and its run values, which the guard holds the role to, or why no work waits for the role."""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Sequence
from typing import TextIO

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "domain"))

from fault import CantRun, Missing, Wrong
from tree import cut, design, runs

USAGE = 'usage: text.py <role>, with {"running": [...]} on standard input\n'


def main(argv: Sequence[str], stdin: TextIO, cwd: str) -> tuple[int, str, str]:
    """Gives Lane the text of one start due.

    Takes: the role, as its one argument; `{"running": [{"role", "text", "values"}]}` on standard
    input, each start that runs; and the folder the conversation works in.
    Gives, as the exit code, standard output, and standard error: 0, with `{"text": <the Cut as one
    JSON line>, "values": <its run values>}`, from `runs.of_folder`, `design.read`, and
    `cut.next_start`; 0, with `{"none": <why no work waits for the role>}`, where
    `cut.next_start` gives None, such as while every deliverable doing waits for a sign-off, so
    that Lane leaves the start out of the moves due with why in its place; 1, with why, where the
    folder lies in no run's worktree, as before the orchestrator makes and enters it, or where
    standard input or a file of the run leaves its form; 2, with the usage.
    Changes: nothing.
    Refuses: by exit 1 or 2, as Gives says, which Lane reads as a failure with why.
    Carries: S1 `GD->>A: asks for the text of the tree-keeper's start`, `A-->>GD: fails, as the
    folder lies in no run's worktree yet`, `GD->>A: asks for the text of the generator's start,
    with each start that runs`, `A->>T: gets each deliverable doing, and the Cut`, and `A-->>GD:
    that start's text and run values in Lane's form, or none where no work waits`; S5 `GD->>A:
    asks for the text of the tree-keeper's start` and `A-->>GD: fails`.
    """
    if len(argv) != 1:
        return 2, "", USAGE
    try:
        running = _running(stdin.read())
        run = runs.of_folder(cwd)
        if run is None:
            raise Wrong(
                f"{cwd} lies in no run's worktree; the orchestrator makes and enters it first"
            )
        there = os.path.exists(os.path.join(run.folder, "design-tree.json"))
        tree = design.read(run) if there else design.DesignTree({})
        found = cut.next_start(run, tree, argv[0], running)
    except (Wrong, Missing, CantRun) as e:
        return 1, "", f"rn's adapter of a start's text: {e}\n"
    if found is None:
        why = f"no work waits for {argv[0]}: each deliverable doing is held, judged, or waits"
        return 0, json.dumps({"none": why}) + "\n", ""
    shown = {"text": json.dumps(found.part), "values": dict(found.values)}
    return 0, json.dumps(shown) + "\n", ""


def _running(text: str) -> list[dict[str, str]]:
    """The run values of each start that runs, from what Lane gives on standard input."""
    try:
        given = json.loads(text)
        return [dict(each.get("values", {})) for each in given["running"]]
    # Runs only on input out of form, which dev/scripts/quality.sh's property test gives,
    # test_any_input_of_the_adapter_of_a_starts_text_gives_a_text_none_or_why.
    except (ValueError, KeyError, TypeError, AttributeError):  # pragma: no cover
        raise Wrong('standard input must be {"running": [{"role", "text", "values"}]}') from None


if __name__ == "__main__":
    code, out, err = main(sys.argv[1:], sys.stdin, os.getcwd())
    sys.stdout.write(out)
    sys.stderr.write(err)
    raise SystemExit(code)
