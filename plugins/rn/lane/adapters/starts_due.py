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

from fault import Answer, Wrong, end
from repository.place import RunPlace, of_folder, of_session
from rounds import course, files
from tree import form

# rn's subagents, whose starts Lane counts.
_ROLES = {"rn:generator": "generator", "rn:evaluator": "evaluator"}
# The orchestrator's roles, the skills of rn's commands, whose results move the run.
_ORCHESTRATOR = ("rn:on", "rn:up", "rn:dn", "rn:ty", "rn:gm")
# The orchestrator's results that leave the run: the user paused it or cancelled it.
_LEFT = ("paused", "cancelled")

# The run as Lane gives it, in the form of Lane's starts_due.in.schema.json, and the starts due
# that rn gives back, in the form of its starts_due.out.schema.json.
Given = dict[str, Any]
Due = dict[str, Any]


def due(given: Given, cwd: str) -> Due:
    """The starts due of the run, or its end.

    Takes: the run as Lane gives it, and the folder that the conversation works in, the top of the
    user's repository.
    Gives: `{"ends": true}` where the orchestrator reported `paused` or `cancelled`, as the user
    paused or cancelled the run, so that Lane holds no later turn of the conversation, and
    `/rn:up` picks a paused run up in a new run of Lane; where the run's worktree no longer lies
    here, as a role started on it, or the orchestrator reported `signed`, since the latest `rn:up`,
    since a run that isn't here has nothing to hold; and where each deliverable of its design tree
    is done; `{"starts": []}` where the run's latest command is `rn:dn` and the orchestrator
    reported no `paused`, so that Lane holds the pause's turn to its steps, where its only command
    is `rn:on` and the orchestrator reported no `signed`, as the run that the conversation makes
    waits on the user's goal and their sign-off of its plan, which their answer gives, where the
    run has no worktree here otherwise, as `repository.py find` makes it again at a pick-up, or
    where its plan, the deliverable of the kind `design-tree`, isn't done;
    else `{"starts": [...]}`, for `rn:generator` and `rn:evaluator`, the count of each: one for
    each deliverable that an item `make` of `work` names, whose inputs are each done, that rests
    through its inputs on no deliverable still being made, and that waits on the role, as
    `rounds.course.next_of` gives it, a deliverable with an open decision, such as a refusal that
    only the user can mend kept for them, waiting on the answer and on no role, so that the work
    it concerns stops and the rest goes on, less each start of the role whose prompt names a Cut
    of the deliverable and that has no result yet in the moves. The run is the one whose folder
    the latest start's prompt names; else the conversation's own, the one that
    `repository.place.of_session` gives for `run.session`, as rn's rules find it.
    Changes: nothing.
    Refuses: Wrong where the design tree or a Round can't be read, naming the file.
    """
    moves = given["run"]["moves"]
    if any(_reported(each, _LEFT) for each in moves):
        return {"ends": True}
    commands = [each["command"] for each in moves if each["kind"] == "command"]
    if commands and commands[-1] == "rn:dn":
        return {"starts": []}
    starts = [each for each in moves if each["kind"] == "start" and each["role"] in _ROLES]
    run = _run(commands, starts, given["run"], cwd)
    if run is None:
        return {"ends": True} if _lay_here(moves) else {"starts": []}
    tree = form.read(run.tree)
    deliverables = tree["deliverables"]
    if all(each["status"] == "done" for each in deliverables):
        return {"ends": True}
    done = {each["path"] for each in deliverables if each["status"] == "done"}
    if any(each["kind"] == "design-tree" and each["path"] not in done for each in deliverables):
        return {"starts": []}
    running = _running(run, moves, cwd)
    count = Counter(
        role
        for role, path in _waiting(run, tree, done)
        if role in _ROLES.values() and (role, path) not in running
    )
    return {"starts": [{"role": f"rn:{role}", "count": n} for role, n in count.items()]}


def _waiting(run: RunPlace, tree: form.Tree, done: set[str]) -> list[tuple[str, str]]:
    """What each deliverable that `work` makes waits on, by its path, where it isn't done and each
    of its inputs that is a deliverable is."""
    made = {each["path"] for each in tree["work"] if each["do"] == "make"}
    named = {each["path"] for each in tree["deliverables"]}
    found = []
    for node in tree["deliverables"]:
        inputs = {each for each in node.get("inputs", []) if each in named}
        if node["path"] in made and node["path"] not in done and inputs <= done:
            found.append((course.next_in(run, node).waits_on, node["path"]))
    return found


def _run(commands: list[str], starts: list[Given], given: Given, cwd: str) -> RunPlace | None:
    """The run whose starts are due: the one that the latest start of rn's subagents names by its
    Cut; else none where the run's only command is `rn:on` and the orchestrator reported no
    sign-off of the plan, as the conversation's own run waits on the user until its plan is signed
    off; else the conversation's own, whose design tree holds its session, as `new` and a pick-up
    write it, and as rn's rules find it, so that another conversation's run is never this one's;
    else None, as for a run named by its Cut whose folder no longer lies here."""
    moves = given["moves"]
    if starts:
        # A Cut lies at <run's folder>/rounds/<deliverable>/<stage>-<n>/<role>-cut.json, <n> the
        # Round's number among the deliverable's Rounds.
        cut = os.path.join(cwd, starts[-1]["prompt"])
        folder = os.path.normpath(os.path.join(cut, *[os.pardir] * 4))
        return of_folder(cwd, folder) if os.path.isdir(folder) else None
    if set(commands) == {"rn:on"} and not _signed(moves):
        return None
    return of_session(cwd, given["session"])


def _signed(moves: list[Given]) -> bool:
    """Whether the orchestrator reported, by `lane-result signed`, that the user's answer signed off
    the plan, as that answer is no command."""
    return any(
        each["kind"] == "result" and each["role"] == "rn:on" and each["result"] == "signed"
        for each in moves
    )


def _reported(move: Given, results: tuple[str, ...]) -> bool:
    """Whether the move is a result of the orchestrator's among the results, which no other role
    gives the run."""
    return move["kind"] == "result" and move["role"] in _ORCHESTRATOR and move["result"] in results


def _lay_here(moves: list[Given]) -> bool:
    """Whether the run's worktree lay here since the run was last picked up: a role started on it,
    or the orchestrator reported `signed`, after the latest command `rn:up`, which makes the
    worktree again where none lies."""
    picked = [i for i, each in enumerate(moves) if each.get("command") == "rn:up"]
    since = moves[picked[-1] + 1 :] if picked else moves
    return any(
        (each["kind"] == "start" and each["role"] in _ROLES) or _reported(each, ("signed",))
        for each in since
    )


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


def main(stdin: str, cwd: str) -> Answer:
    """The exit code, stdout, and stderr of the adapter, as Lane runs it.

    Takes: what Lane writes on its standard input, and the folder it runs in.
    Gives: 0 with `due`'s output as one line of JSON; 1 with `starts_due.py: <what's wrong>`
    where the input isn't JSON or `due` refuses it as Wrong. Lane reads any but 0 as starts due it
    couldn't check, and says so with what the adapter said.
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
    end(lambda: main(sys.stdin.read(), os.getcwd()))
