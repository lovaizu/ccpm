"""What rn's integration cases share: a bench for each case, with each Given kept once played;
rn's and Lane's code imported afresh by each script and hook that the double runs, as a new process
of Python would import the copy it runs; and the fixture `broken`, which takes out the part that
holds a rule, and each Lane that holds it beside, where TRACE_BROKEN is 1, as the plugin guide's A
principle's test seen to fail says."""

from __future__ import annotations

import json
import os
import shutil
from collections.abc import Iterator

import pytest

from dev.rn.tests import rn_walkthrough
from dev.tests import fresh_imports

# The modules of rn's code and of Lane's guard, by name, which a case's process holds no copy of
# while the case runs, so that each script and hook imports the code of the bench's copy.
MODULES = (
    "fault",
    "json_form",
    "throwaway",
    "tree",
    "record",
    "repository",
    "template",
    *fresh_imports.GUARD,
)


@pytest.fixture(autouse=True)
def fresh_modules() -> Iterator[None]:
    """Takes each module of rn's and Lane's code out of the process for the case, and puts back
    those it held before."""
    with fresh_imports.without(MODULES):
        yield


@pytest.fixture
def b(tmp_path_factory: pytest.TempPathFactory) -> rn_walkthrough.Bench:
    """The bench of the walkthrough: a copy of rn and of Lane, and invoicer with its remote, at the
    one folder of the test process that each case's bench takes in turn, so that each Given played
    there is kept and put back for each later case that takes it. Where TRACE_BROKEN is 1, each
    Given is played anew, as `broken` changes rn's code before it."""
    top = os.path.realpath(tmp_path_factory.getbasetemp())
    root = os.path.join(top, "bench")
    if os.path.isdir(root):
        shutil.rmtree(root)
    os.makedirs(root)
    givens = None if os.environ.get("TRACE_BROKEN") == "1" else os.path.join(top, "givens")
    return rn_walkthrough.bench(root, givens=givens)


# What takes out the part that holds each rule of Solution strategy, by the rule's heading: the file
# of rn's code, from domain/, and the stand-in that its end defines in place of the part, so that
# each script of the bench's copy runs it, in the case's process or in a new one.
WHOLE_TREE = '''
_held_next_start = next_start


def next_start(run, tree, role, running):
    """The Cut of the next start, with the whole design tree beside the role's part, and no commit
    at which its deliverable was done, so that a role reads each input whole."""
    cut = _held_next_start(run, tree, role, running)
    if cut is None:
        return None
    part = dict(cut.part, tree=dict(tree.data))
    if isinstance(part.get("cut"), dict):
        part["cut"] = {k: v for k, v in part["cut"].items() if k != "done_at"}
    return Cut(cut.role, cut.values, part)
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
# The Lanes that hold a rule beside its part of rn's code, by the rule, each by its role and lane
# type, as the guard holds a role's calls to its throwaway copy by the generator's run_only Lane.
LANES: dict[str, tuple[str, str]] = {
    "Tried in a throwaway copy": ("generator", "run_only"),
}
RULES: dict[str, tuple[str, str]] = {
    "Drawn out along the design tree": ("tree/cut.py", WHOLE_TREE),
    "Every step by best practice": ("record/order.py", NO_STEP_LACKS),
    "Every item handled": ("record/items.py", NO_ITEM_LACKS),
    "Judged by the people it's for": ("tree/cut.py", MAKERS_VIEW),
    "Signed off before it's built on": ("tree/turn.py", EVERY_TURN),
    "Back to the design tree on a problem": ("tree/more.py", EVERY_MORE),
    "The design tree reviewed each turn": ("tree/practices.py", RN_OWN),
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
        if rule in LANES:
            _lane_taken_out(b, *LANES[rule])


def _lane_taken_out(b: rn_walkthrough.Bench, role: str, kind: str) -> None:
    """The bench's copy of rn without the role's Lanes of the type, as Lane laid them."""
    path = os.path.join(b.rn, "hooks", "lanes.json")
    with open(path, encoding="utf-8") as f:
        laid = json.load(f)
    laid["lanes"] = [x for x in laid["lanes"] if (x["role"], x["type"]) != (role, kind)]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(laid, f)
