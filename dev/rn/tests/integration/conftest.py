"""What rn's integration cases share: the top of the repository on the import path, from which the
cases take the double of Claude Code and the walkthrough's helpers by their paths, as the type
checker finds them there; a bench for each case; rn's and Lane's code imported afresh by each
script and hook that the double runs, as a new process of Python would import the copy it runs; and
the fixture `broken`, which takes out the part that holds a rule where TRACE_BROKEN is 1, as the
plugin guide's A principle's test seen to fail says."""

from __future__ import annotations

import os
import sys
from collections.abc import Iterator
from typing import Any

import pytest

TOP = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 4))
if TOP not in sys.path:
    sys.path.insert(0, TOP)

from dev.rn.tests import rn_walkthrough

# The modules of rn's code and of Lane's guard, by name, which a case's process holds no copy of
# while the case runs, so that each script and hook imports the code of the bench's copy.
MODULES = (
    "fault",
    "throwaway",
    "tree",
    "record",
    "repository",
    "template",
    "events",
    "guard",
    "place",
    "runs",
    "run_record",
    "form",
    "adapters",
    "answers",
    "script_calls",
    "lanes",
    "manifest",
)


def ours(name: str) -> bool:
    return name.split(".")[0] in MODULES


@pytest.fixture(autouse=True)
def fresh_modules() -> Iterator[None]:
    """Takes each module of rn's and Lane's code out of the process for the case, and puts back
    those it held before, as a case at another level may have imported them."""
    held = {name: module for name, module in sys.modules.items() if ours(name)}
    for name in held:
        del sys.modules[name]
    yield
    for name in [name for name in sys.modules if ours(name)]:
        del sys.modules[name]
    sys.modules.update(held)


@pytest.fixture
def b(tmp_path: Any) -> rn_walkthrough.Bench:
    """The bench of the walkthrough: a copy of rn and of Lane, and invoicer with its remote."""
    return rn_walkthrough.bench(str(tmp_path))


# What takes out the part that holds each rule of Solution strategy, by the rule's heading: the file
# of rn's code, from domain/, and the stand-in that its end defines in place of the part, so that
# each script of the bench's copy runs it, in the case's process or in a new one.
WHOLE_TREE = '''
_held_next_start = next_start


def next_start(run, tree, role, running):
    """The Cut of the next start, with the whole design tree beside the role's part."""
    cut = _held_next_start(run, tree, role, running)
    return None if cut is None else Cut(cut.role, cut.values, dict(cut.part, tree=dict(tree.data)))
'''
MAKERS_VIEW = '''
_held_next_start = next_start


def next_start(run, tree, role, running):
    """The Cut of the next start, with the goal and the decisions beside an evaluator's part."""
    cut = _held_next_start(run, tree, role, running)
    if cut is None or role != "evaluator":
        return cut
    goal = tree.data["goal"]
    each = tree.data["deliverables"]
    decisions = [d["necessary_conditions"] for d in each if "necessary_conditions" in d]
    return Cut(cut.role, cut.values, dict(cut.part, goal=goal, decisions=decisions))
'''
NO_STEP_LACKS = '''

def lacks(record, of, steps, practices):
    """Nothing lacking, whatever the record holds."""
    return ()
'''
NO_ITEM_LACKS = '''

def lacks(cut, result, made, answers):
    """Nothing lacking, whatever the result names."""
    return ()
'''
EVERY_TURN = '''

def mark_doing(tree, signed):
    """Each deliverable open marked doing, whatever it rests on."""
    import copy

    data = copy.deepcopy(dict(tree.data))
    marked = []
    for each in data["deliverables"]:
        if each.get("status") == "open":
            each["status"] = "doing"
            marked.append(each["path"])
    return DesignTree(data), tuple(marked)
'''
EVERY_MORE = '''

def keepable(at_cut, now, more):
    """Every more kept, whatever changed."""
    return None
'''
RN_OWN = '''

def folder(run, plugin_root, kind):
    """rn's own best practice of the kind, whatever the run made."""
    import os

    return os.path.join(plugin_root, "domain", "best-practices", kind)
'''
IN_PLACE = '''

def main(argv, cwd):
    """The command run in the worktree itself, with no Try record."""
    import subprocess

    done = subprocess.run(argv[1], shell=True, cwd=cwd, capture_output=True, text=True)
    return done.returncode, done.stdout, done.stderr
'''
NO_COMMIT = '''

def commit(run, paths, why):
    """No commit, whatever ended."""
    return ""


def push(run):
    """No push."""
    return None
'''
RULES: dict[str, tuple[str, str]] = {
    "Drawn out along the design tree": ("tree/cut.py", WHOLE_TREE),
    "Every step by best practice": ("record/order.py", NO_STEP_LACKS),
    "Every item handled": ("record/items.py", NO_ITEM_LACKS),
    "Judged by the people it's for": ("tree/cut.py", MAKERS_VIEW),
    "Signed off before it's built on": ("tree/turn.py", EVERY_TURN),
    "Back to the design tree on a problem": ("tree/more.py", EVERY_MORE),
    "The design tree revised on each run": ("tree/practices.py", RN_OWN),
    "Tried in a throwaway copy": ("throwaway.py", IN_PLACE),
    "The repository holds the work": ("tree/branch.py", NO_COMMIT),
}


@pytest.fixture
def broken(request: pytest.FixtureRequest, b: rn_walkthrough.Bench) -> None:
    """Where TRACE_BROKEN is 1, takes out of the bench's copy of rn the part that holds each rule
    the case names."""
    if os.environ.get("TRACE_BROKEN") != "1":
        return
    names = [name for mark in request.node.iter_markers("supports") for name in mark.args]
    rules = [name for name in names if name in RULES]
    assert rules, "the case names no rule"
    for rule in rules:
        file, stand_in = RULES[rule]
        with open(os.path.join(b.rn, "domain", file), "a", encoding="utf-8") as f:
            f.write(stand_in)
