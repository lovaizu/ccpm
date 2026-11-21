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

from fault import Wrong, end
from repository import host
from repository.place import RunPlace, of_folder
from repository.worktree import newest
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
    the run waits for `/rn:up`, where its only command is `rn:on`, as the run that the
    conversation makes waits on the user's goal and their sign-off of its plan, where the run has
    no worktree here, or where its plan, the deliverable of the kind `design-tree`, isn't done;
    else `{"starts": [...]}`, for `rn:generator` and `rn:evaluator`, the count of each: one for
    each deliverable that an item `make` of `work` names, whose inputs are each done, that rests
    through its inputs on no deliverable still being made, and that waits on the role, as
    `rounds.course.next_of` gives it, a deliverable with an open decision, such as a refusal that
    only the user can mend kept for them, waiting on the answer and on no role, so that the work
    it concerns stops and the rest goes on, less each start of the role whose prompt names a Cut
    of the deliverable and that has no result yet in the moves. The run is the one whose folder
    the latest start's prompt names; else the one that `repository.worktree.newest` gives.
    Changes: nothing.
    Refuses: Wrong where the design tree or a Round can't be read, naming the file.
    """
    moves = given["run"]["moves"]
    commands = [each["command"] for each in moves if each["kind"] == "command"]
    if commands and commands[-1] == "rn:dn":
        return {"starts": []}
    starts = [each for each in moves if each["kind"] == "start" and each["role"] in _ROLES]
    run = _run(commands, starts, cwd)
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
        role = course.next_in(run, node).waits_on
        if role in _ROLES.values() and (role, node["path"]) not in running:
            count[role] += 1
    return {"starts": [{"role": f"rn:{role}", "count": n} for role, n in count.items()]}


def _run(commands: list[str], starts: list[Given], cwd: str) -> RunPlace | None:
    """The run whose starts are due: the one that the latest start of rn's subagents names by its
    Cut; else none where the run's only command is `rn:on`, as the conversation's own run waits on
    the user until its plan is signed off; else the one that can be picked up, where its worktree
    lies here; else None."""
    if starts:
        # A Cut lies at <run's folder>/rounds/<deliverable>/<stage>-<n>/<role>-cut.json.
        cut = os.path.join(cwd, starts[-1]["prompt"])
        return of_folder(cwd, os.path.normpath(os.path.join(cut, *[os.pardir] * 4)))
    if set(commands) == {"rn:on"}:
        return None
    found = newest(cwd, host.run)
    return found if found and os.path.isfile(found.tree) else None


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
