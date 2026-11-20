"""Decides rn's order, as Lane asks it at each move of a run: which of rn's roles start now, from
the run's design tree and its Rounds, each deliverable's Rounds beside the others', and when the
run ends."""

from __future__ import annotations

import os
import sys
from typing import Any

# rn's code lies in domain/, which comes on the import path before it's imported.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "domain"))

import json
from collections import Counter
from datetime import date

import practice
from fault import Wrong, end
from repository.place import RunPlace, named, of_folder
from repository.worktree import paused
from rounds import course, files
from tree import form

# rn's subagents, whose starts Lane counts.
_ROLES = {"rn:generator": "generator", "rn:evaluator": "evaluator"}

# The run as Lane gives it, in the form of Lane's starts_due.in.schema.json, and the starts due
# that rn gives back, in the form of its starts_due.out.schema.json.
Given = dict[str, Any]
Due = dict[str, Any]


def due(given: Given, cwd: str) -> Due:
    """The starts due of the run, or its end.

    Takes: the run as Lane gives it, and the folder that the conversation works in, the top of the
    user's repository.
    Gives: `{"ends": true}` where each deliverable of its design tree is done; `{"starts": []}`
    where the run's latest command is `rn:dn`, so that Lane holds the pause's turn to its steps and
    the run waits for `/rn:up`, where the run has no worktree yet, or where its plan, the
    deliverable of the kind `design-tree`, isn't done; else `{"starts": [...]}`, for `rn:generator`
    and `rn:evaluator`, the count of each: one for each deliverable that an item `make` of `work`
    names, whose inputs are each done, that rests through its inputs on no deliverable still being
    made, and that waits on the role, as `rounds.course.next_of` gives it, a deliverable with an
    open decision waiting on the answer and on no role, less each start of the role whose prompt
    names a Cut of the deliverable and that has no result yet in the moves. The run is the one whose
    folder the latest start's prompt names; else, for a run called with words, the newest run under
    `.claude/worktrees/` whose name ends with the part after the date that `place.named` gives for
    the words, done or not; else the first that `repository.worktree.paused` gives.
    Changes: nothing.
    Refuses: Wrong where the design tree or a Round can't be read, naming the file.
    """
    moves = given["run"]["moves"]
    commands = [each["command"] for each in moves if each["kind"] == "command"]
    if commands and commands[-1] == "rn:dn":
        return {"starts": []}
    starts = [each for each in moves if each["kind"] == "start" and each["role"] in _ROLES]
    run = _run(starts, given["run"]["words"], cwd)
    if run is None:
        return {"starts": []}
    tree = form.read(run.tree)
    deliverables = tree["deliverables"]
    if all(each["status"] == "done" for each in deliverables):
        return {"ends": True}
    done = {each["path"] for each in deliverables if each["status"] == "done"}
    if any(each["kind"] == "design-tree" and each["path"] not in done for each in deliverables):
        return {"starts": []}
    made = {each["path"] for each in tree["work"] if each["do"] == "make"}
    named = {each["path"] for each in deliverables}
    running = _running(run, moves, cwd)
    count: Counter[str] = Counter()
    for node in deliverables:
        inputs = {each for each in node.get("inputs", []) if each in named}
        if node["path"] not in made or node["path"] in done or not inputs <= done:
            continue
        role = _waits_on(run, node)
        if role in _ROLES.values() and (role, node["path"]) not in running:
            count[role] += 1
    return {"starts": [{"role": f"rn:{role}", "count": n} for role, n in count.items()]}


def _run(starts: list[Given], words: str, cwd: str) -> RunPlace | None:
    """The run that the latest start of rn's subagents names by its Cut; else the newest run of
    the words' name part, done or not; else the first that can be picked up; else None."""
    if starts:
        # A Cut lies at <run's folder>/rounds/<deliverable>/<stage>-<n>/<role>-cut.json.
        cut = os.path.join(cwd, starts[-1]["prompt"])
        return of_folder(cwd, os.path.normpath(os.path.join(cut, *[os.pardir] * 4)))
    if words:
        part = named(date.today(), words).split("-", 1)[1]
        found = sorted(
            (each for each in _runs(cwd) if each.name.split("-", 1)[1] == part),
            key=lambda each: each.name,
        )
        if found:
            return found[-1]
    found = paused(cwd)
    return found[0] if found else None


def _runs(cwd: str) -> list[RunPlace]:
    """Each run under the repository's `.claude/worktrees/` that holds its design tree."""
    worktrees = os.path.join(cwd, ".claude", "worktrees")
    if not os.path.isdir(worktrees):
        return []
    runs = [
        RunPlace(cwd, folder[3:]) for folder in os.listdir(worktrees) if folder.startswith("rn-")
    ]
    return [each for each in runs if os.path.isfile(each.tree)]


def _waits_on(run: RunPlace, node: Given) -> str:
    """What the deliverable waits on, as rounds.course gives it."""
    done = [
        (each, files.result(each, "generator"), files.result(each, "evaluator"))
        for each in files.of(run, node["path"])
    ]
    refactors = practice.refactoring(node["kind"]) is not None
    return course.next_of(node, done, refactors).waits_on


def _running(run: RunPlace, moves: list[Given], cwd: str) -> set[tuple[str, str]]:
    """Each start of rn's subagents with no result yet in the moves, by its role and the path of
    the deliverable whose Cut its prompt names; each result ends its role's earliest start."""
    pending: dict[str, list[str]] = {role: [] for role in _ROLES.values()}
    for each in moves:
        role = _ROLES.get(each.get("role", ""))
        if role is None:
            continue
        if each["kind"] == "start":
            folder = os.path.dirname(os.path.join(cwd, each["prompt"]))
            pending[role].append(files.at(run, folder).deliverable)
        else:
            del pending[role][:1]
    return {(role, path) for role, paths in pending.items() for path in paths}


def main(stdin: str, cwd: str) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of the adapter, as Lane runs it.

    Takes: what Lane writes on its standard input, and the folder it runs in.
    Gives: 0 with `due`'s output as one line of JSON; 1 with `starts_due.py: <what's wrong>`
    where the input isn't JSON or `due` refuses it as Wrong. Lane stops the move at hand on any
    but 0.
    Changes: nothing.
    Refuses: nothing; each fault is its exit code.
    """
    try:
        given = json.loads(stdin)
    except ValueError as error:
        return 1, "", f"starts_due.py: its input isn't JSON: {error}\n"
    try:
        if not isinstance(given, dict) or not isinstance(given.get("run"), dict):
            raise Wrong("its input isn't the run as Lane gives it, an object with its run")
        return 0, json.dumps(due(given, cwd)) + "\n", ""
    except Wrong as wrong:
        return 1, "", f"starts_due.py: {wrong}\n"


if __name__ == "__main__":
    end(main(sys.stdin.read(), os.getcwd()))
