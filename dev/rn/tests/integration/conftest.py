"""The fixtures of rn's integration cases: the test's repository of invoicer with rn installed, a
conversation of the double of Claude Code with rn loaded, a run begun, and the fixture `broken`,
which takes out the part that holds each principle where TRACE_BROKEN is 1, as the plugin guide's
A principle's test seen to fail says.

rn runs from the installed copy of its folder: the double runs tree.py and throwaway.py in the
test's own process, and Lane's guard runs the adapters and rn's check in processes of their own, so
`broken` takes a part out of the copy's files, where each of them reads it, and the cases import
none of rn's code."""

from __future__ import annotations

import json
import os
from typing import Any, Callable

import pytest
from claude_code import Conversation
from rn_example import Repo, Run, begin, conversation, make_repo

# What each take-out appends to a module of the installed copy: a definition of the same name, which
# holds in place of the one before it.
EVERY_DECISION = '''
_cut_alone = cut


def cut(run, role, deliverable="", group=""):
    """The Cut with every decision of the design tree, not only its deliverable's."""
    import dataclasses

    from tree import design

    whole = design.load(run)
    every = tuple(
        decision
        for each in whole.deliverables
        for need in each.conditions
        for decision in need.decisions
    )
    return dataclasses.replace(_cut_alone(run, role, deliverable, group), decisions=every)
'''
NO_LACKS = '''
_cut_with_lacks = cut


def cut(run, role, deliverable="", group=""):
    """The Cut without the lacks kept for its round."""
    import dataclasses

    return dataclasses.replace(_cut_with_lacks(run, role, deliverable, group), lacks=())
'''
NO_RECORD_FAULTS = '''
def record_faults(record, steps, best_practices):
    """No fault of any record."""
    return ()
'''
NO_RESULT_FAULTS = '''
def made_faults(cut, decisions, lacks):
    """No fault of anything a generator made."""
    return ()


def answers_faults(cut, answers):
    """No fault of any Answers."""
    return ()
'''
ALL_DUE = '''
def due(tree, sign_offs):
    """Each deliverable open, signed off or not."""
    return tuple(each.path for each in tree.deliverables if each.status == "open")
'''
RN_OWN_ONLY = '''
_find_made_on_a_run = find


def find(worktree, plugin_root, kind):
    """rn's own best practice of the kind, never one made on a run."""
    return _find_made_on_a_run("/nowhere", plugin_root, kind)
'''
IN_THE_WORKTREE = '''
def copy(worktree, run_name):
    """The worktree itself, with the home of the user."""
    import os

    return worktree, os.path.expanduser("~")
'''
NO_COMMIT = '''
def commit(worktree, message, environ):
    """Nothing committed."""
    return False
'''


def appended(path: str, code: str) -> Callable[[str], None]:
    """A take-out that appends the code to the module of the installed rn at the path."""

    def take_out(plugin: str) -> None:
        with open(os.path.join(plugin, path), "a", encoding="utf-8") as f:
            f.write("\n" + code)

    return take_out


def laid_lanes(plugin: str) -> tuple[str, dict[str, Any]]:
    """The path of the lanes that Lane laid in the installed rn, and what it holds. Fails the case
    where rn has none, as a take-out that took out nothing would let a case of the guard pass with
    its lane absent; `/lane:up rn` lays them once Lane is built."""
    path = os.path.join(plugin, "hooks", "lanes.json")
    if not os.path.exists(path):
        pytest.fail(
            f"{path} doesn't exist, so no lane can be taken out: lay rn's lanes by /lane:up rn"
        )
    with open(path, encoding="utf-8") as f:
        return path, json.load(f)


def without_lanes(kind: str, role: str = "") -> Callable[[str], None]:
    """A take-out that drops each lane of the type from the lanes that Lane laid in the installed
    rn, of the role only where one is given."""

    def take_out(plugin: str) -> None:
        path, laid = laid_lanes(plugin)
        laid["lanes"] = [
            each
            for each in laid["lanes"]
            if not (each["type"] == kind and (not role or each["role"] == role))
        ]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(laid, f)

    return take_out


def without_waits(plugin: str) -> None:
    """A take-out that has no route of the installed rn wait for a command the user types."""
    path, laid = laid_lanes(plugin)
    for route in laid["routes"]:
        for move in route["moves"]:
            move.pop("waits_for", None)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(laid, f)


# For each principle of rn's architecture, each part that holds it, taken out.
PARTS: dict[str, tuple[Callable[[str], None], ...]] = {
    "Drawn out along the design tree": (
        appended("domain/tree/cut.py", EVERY_DECISION),
        without_lanes("read_never", "generator"),
    ),
    "Every step by best practice": (appended("domain/record/check.py", NO_RECORD_FAULTS),),
    "Every item handled": (appended("domain/record/check.py", NO_RESULT_FAULTS),),
    "Judged by the people it's for": (without_lanes("read_never", "evaluator"),),
    "Signed off before it's built on": (appended("domain/tree/turn.py", ALL_DUE), without_waits),
    "Back to the design tree on a problem": (appended("domain/tree/cut.py", NO_LACKS),),
    "The design tree revised on each run": (appended("domain/tree/practices.py", RN_OWN_ONLY),),
    "Tried in a throwaway copy": (
        appended("domain/throwaway.py", IN_THE_WORKTREE),
        without_lanes("run_only", "generator"),
    ),
    "The repository holds the work": (
        appended("domain/repository/git.py", NO_COMMIT),
        without_lanes("write_only"),
    ),
}


@pytest.fixture
def repo(tmp_path: Any) -> Repo:
    """The test's repository of invoicer, pushed to its bare remote, with rn installed and gh
    logged in, as the walkthrough starts."""
    return make_repo(os.path.realpath(str(tmp_path)))


@pytest.fixture
def broken(request: pytest.FixtureRequest, repo: Repo) -> bool:
    """Where TRACE_BROKEN is 1, takes out of the installed rn each part that holds each principle
    that the case names, and gives True; else does nothing and gives False."""
    if os.environ.get("TRACE_BROKEN") != "1":
        return False
    for mark in request.node.iter_markers("supports"):
        for name in mark.args:
            for take_out in PARTS.get(name, ()):
                take_out(repo.plugin)
    return True


@pytest.fixture
def conv(repo: Repo, broken: bool) -> Conversation:
    """A conversation with rn loaded, at the root of invoicer, once `broken` took out what the case
    names."""
    return conversation(repo)


@pytest.fixture
def run(conv: Conversation, repo: Repo) -> Run:
    """The run of the walkthrough's request, its worktree made and entered."""
    return begin(conv, repo)
