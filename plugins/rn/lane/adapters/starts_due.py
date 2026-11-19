#!/usr/bin/env python3
"""Decides what rn's order gives Lane at each move: the starts due of the run, from its design tree
and its Rounds as course.due gives them, or the run's end."""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Sequence
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "domain"))

from fault import Wrong, end
from tree import course, design, rounds

# rn's folder, where the design tree's schema and the best practices lie.
PLUGIN = os.path.dirname(os.path.dirname(HERE))


def main(given: str, cwd: str) -> tuple[int, str, str]:
    """Gives Lane the starts due of the run, as Lane runs this adapter at each move.

    Takes: the run as Lane's order sees it, on standard input in the form of Lane's
    starts_due.in.schema.json, and the folder that the conversation works in: the repository's top,
    or rn's worktree of the run.
    Gives: 0 with, in the form of Lane's starts_due.out.schema.json:
    - `{"ends": true}` where the run's latest command is `rn:ty` and no run's folder that
      rounds.folder finds has work left, as that /rn:ty signs off the pull request;
    - else `{"starts": [...]}`, for each role, `rn:generator` or `rn:evaluator`, with its count,
      the starts that course.due gives for the design tree of the run's folder that rounds.folder
      finds and that folder's Rounds, beside the starts that run: those whose prompt, in the run's
      moves, names a Cut with no result beside it. These are one generator for each deliverable
      that can be made now, beside the others, or one evaluator for each group of conditions that
      its Round judges. A Cut with no result that no prompt of the moves names is a start that
      didn't end, stopped, failed, or lost with its conversation, and counts for nothing, so that
      a pick-up in a new conversation, whose moves hold no start, gives each start due again for
      a fresh Cut. None where the latest command is `rn:dn` with no `rn:up` after it, as the run
      waits paused, so that Lane lets the orchestrator's turn end; where the words ask for a new
      run and the moves hold no `rn:ty` yet, as the plan waits for the person's sign-off; or where
      no run's folder has work left.
    1 with what Wrong says, such as Lane's input out of its form, a design tree out of its schema,
    or a Round that isn't JSON. A design tree that isn't JSON never reaches it, as rounds.folder
    passes over it as one with no work left.
    Changes: nothing.
    Refuses: nothing beyond the exit codes above."""
    try:
        words, moves = _run(given)
        return 0, json.dumps(_due(words, moves, cwd)) + "\n", ""
    except Wrong as wrong:
        return 1, "", f"starts_due.py: {wrong}\n"


def _run(given: str) -> tuple[str, list[dict[str, str]]]:
    """The words and the moves of the run that Lane gives; Wrong where it leaves its form."""
    try:
        value: Any = json.loads(given)
    except ValueError as error:
        raise Wrong(f"Lane's input isn't JSON: {error}") from None
    run = value.get("run") if isinstance(value, dict) else None
    words = run.get("words") if isinstance(run, dict) else None
    moves = run.get("moves") if isinstance(run, dict) else None
    if not isinstance(words, str) or not isinstance(moves, list):
        raise Wrong(
            "Lane's input takes the form of starts_due.in.schema.json: run, with words and moves"
        )
    return words, moves


def _due(words: str, moves: Sequence[dict[str, str]], cwd: str) -> dict[str, Any]:
    """What the order gives for the run's words and moves, from the run's folder in `cwd`."""
    commands = [m["command"] for m in moves if m["kind"] == "command"]
    latest = commands[-1] if commands else ""
    if latest == "rn:dn" or (words and "rn:ty" not in commands):
        return {"starts": []}
    found = rounds.folder(cwd)
    if found is None:
        return {"ends": True} if latest == "rn:ty" else {"starts": []}
    run = os.path.join(cwd, found)
    starts = rounds.each(run)
    prompts = [m["prompt"] for m in moves if m["kind"] == "start"]
    due = course.due(design.read(run, PLUGIN), starts, _running(found, starts, prompts))
    roles = [f"rn:{d.role}" for d in due]
    return {"starts": [{"role": r, "count": roles.count(r)} for r in dict.fromkeys(roles)]}


def _running(
    found: str, starts: Sequence[rounds.Start], prompts: Sequence[str]
) -> list[course.Due]:
    """Each start with no result whose Cut a prompt names, by its path from the run's `.rn/`, as
    the orchestrator names it from rn's worktree of the run."""
    run = os.path.join(".rn", os.path.basename(found))
    return [
        course.Due(s.cut["deliverable"]["path"], s.role, s.group, s.cut["best_practice"], s.round)
        for s in starts
        if s.result is None and any(rounds.path(run, s) in p for p in prompts)
    ]


if __name__ == "__main__":
    end(main(sys.stdin.read(), os.getcwd()))
