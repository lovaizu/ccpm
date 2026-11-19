#!/usr/bin/env python3
"""Lane's adapter of a start's text: `start.py <role>`, with the starts that run on its standard
input, as Lane's guide to adapters gives them. It prints the text of the start due, which points the
role to its Cut, with each path its steps name as a run value, or why no work waits for the role."""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "domain"))

from fault import Wrong, end
from tree import course, cut, design, rounds

# rn's folder, where the design tree's schema and the best practices lie.
PLUGIN = os.path.join(HERE, "..", "..")
USAGE = "usage: start.py <role>, with Lane's starts that run on standard input\n"


def main(argv: list[str], given: str, cwd: str) -> tuple[int, str, str]:
    """Gives the start due of the role through course.due and cut.write.

    Takes: the role as the one argument, what Lane gives on standard input, and the folder of the
    run's worktree.
    Gives: 0 with `{"text": ..., "values": {...}}`, the values as _values gives them, or with
    `{"none": ...}` where no start of the role is due; 1 with what Wrong says; 2 with the usage.
    Changes: the run's folder, by the Cut written."""
    if len(argv) != 1:
        return 2, "", USAGE
    try:
        given_starts = json.loads(given)["running"]
    except (ValueError, KeyError, TypeError):
        return 1, "", "start.py: Lane's input isn't {\"running\": [...]}\n"
    try:
        run = _run(cwd)
        tree = design.read(os.path.join(cwd, run), PLUGIN)
        running = [_due(cwd, s) for s in given_starts]
        due = [d for d in course.due(tree, rounds.each(os.path.join(cwd, run)), running)]
    except Wrong as wrong:
        return 1, "", f"start.py: {wrong}\n"
    mine = [d for d in due if d.role == argv[0]]
    if not mine:
        return 0, json.dumps({"none": f"no work waits for the {argv[0]}"}), ""
    cut_path = os.path.relpath(cut.write(os.path.join(cwd, run), tree, mine[0]), cwd)
    text = f"Carry out your steps, from your Cut at {cut_path}."
    return 0, json.dumps({"text": text, "values": _values(run, cut_path, mine[0])}), ""


def _values(run: str, cut_path: str, due: course.Due) -> dict[str, str]:
    """The run values of the start, each path that its steps name: its Cut, its deliverable, and its
    result beside its Cut; for an evaluator also the design tree and the generator's Cut and result
    of its Round, which its steps never read, as it tries the deliverable with only what its people
    have."""
    values = {
        "cut": cut_path,
        "deliverable": due.deliverable,
        "result": cut_path.removesuffix(".cut.json") + ".json",
    }
    if due.role == "evaluator":
        folder = os.path.dirname(cut_path)
        values["tree"] = os.path.join(run, "design-tree.json")
        values["generator_cut"] = os.path.join(folder, "generator.cut.json")
        values["generator_result"] = os.path.join(folder, "generator.json")
    return values


def _run(cwd: str) -> str:
    """The run's folder from the top of the worktree, as Lane runs the adapter only in a run's
    worktree."""
    found = rounds.folder(cwd)
    if found is None:
        raise Wrong(f"{cwd} holds no run's design tree in .rn/; start the run with /rn:up")
    return found


def _due(cwd: str, start: dict) -> course.Due:
    """The start that runs, as its Cut names it."""
    path = start["values"]["cut"]
    with open(os.path.join(cwd, path), encoding="utf-8") as f:
        held = json.load(f)
    return course.Due(
        held["deliverable"]["path"],
        held["role"],
        held.get("group", ""),
        held["best_practice"],
        int(path.split("/")[-2]),
    )


if __name__ == "__main__":
    end(main(sys.argv[1:], sys.stdin.read(), os.getcwd()))
