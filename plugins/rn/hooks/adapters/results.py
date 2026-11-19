#!/usr/bin/env python3
"""Lane's adapter of the results rn keeps: `results.py`, with the words typed after /rn:up on its
standard input. It prints each result of the run's Rounds in their order, so that a new
conversation goes on where the run stopped, and none for words that ask for a new run."""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "domain"))

from fault import Wrong, end
from tree import rounds


def main(given: str, cwd: str) -> tuple[int, str, str]:
    """Gives the results kept through rounds.each.

    Takes: what Lane gives on standard input, and the folder that the conversation works in.
    Gives: 0 with `{"results": [...]}`, empty where the words ask for a new run or no run's
    worktree is there; 1 with what Wrong says."""
    try:
        words = json.loads(given)["words"]
    except (ValueError, KeyError, TypeError):
        return 1, "", "results.py: Lane's input isn't {\"words\": ...}\n"
    run = rounds.folder(cwd)
    if words.strip() or run is None:
        return 0, json.dumps({"results": []}), ""
    try:
        starts = rounds.each(os.path.join(cwd, run))
    except Wrong as wrong:
        return 1, "", f"results.py: {wrong}\n"
    kept = [
        {"role": s.role, "result": s.result["result"] if s.role == "generator" else "judged"}
        for s in starts
        if s.result is not None
    ]
    return 0, json.dumps({"results": kept}), ""


if __name__ == "__main__":
    end(main(sys.stdin.read(), os.getcwd()))
