"""What turn's trials share: the call and the line starting turn with it, the flow trial's task made
a repository, with the roles trials' check of it and their README that falls short, the acceptance
trials' arguments, their repository and the copy kept of what a run gave back, and the copy of turn
a run uses, removed however the trial ends; with Claude Code started on it as its user starts it,
and what a record shows of a role's work, which every plugin's trials share."""

from __future__ import annotations

import contextlib
import glob
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Generator

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# Starting Claude Code and reading a plugin's hooks are what every plugin's trials and tests share,
# kept in lane's; how a CCS, a checklist and Claude Code's records are read is what turn's scripts
# read them by.
sys.path.insert(0, os.path.join(ROOT, "dev", "lane"))
sys.path.insert(0, os.path.join(ROOT, "dev", "lane", "trials"))
sys.path.insert(0, os.path.join(ROOT, "turn", "scripts"))

import record
from call import entries, items  # noqa: F401
from trying import agents, claude, show  # noqa: F401

# The orchestrator's check of the flow trial's task, as the roles trials set it: each item's Good
# found in the decisions.
CHECK = {
    "items": [
        {"checklist": "checklist.md", "item": "B-1", "can": "notes/decisions.md:2 names MIT."},
        {
            "checklist": "checklist.md",
            "item": "B-2",
            "can": "the decisions on demo and its license",
        },
    ],
    "questions": [],
}
# A README for the flow trial's task that names no license, which the roles trials set in place of
# the generator's work, so the first user stops at B-1.
UNLICENSED = "# demo\n\ndemo prints a greeting.\n\n## Use\n\nRun `sh demo.sh`.\n"


def call(has: str) -> dict:
    """The call turn is given, with the CCS key of what the work's receiver has."""
    return {
        "ccs": ".tasks/ccs.json",
        "result": ".tasks/result.json",
        "kind": {
            "work": "deliverable",
            "checklist": "checklist",
            "receiver": "audience",
            "use": "purpose",
            "has": has,
        },
    }


def start(given: dict) -> str:
    """The line a step's text starts turn with, as turn's README gives it, on the call."""
    return f"Start the `turn:up` agent in the background with\n{json.dumps(given)}\n"


def task(place: str, given: dict, decisions: str | None = None) -> None:
    """Makes the flow trial's task a repository at place, its CCS where the call names it, and its
    decisions, when given, replaced with decisions."""
    shutil.copytree(os.path.join(os.path.dirname(__file__), "flow", "task"), place)
    if decisions is not None:
        with open(os.path.join(place, "notes", "decisions.md"), "w", encoding="utf-8") as f:
            f.write(decisions)
    os.makedirs(os.path.join(place, ".tasks"))
    shutil.move(os.path.join(place, "ccs.json"), os.path.join(place, given["ccs"]))
    committed(place)


def committed(place: str) -> None:
    """Makes place a repository holding what is in it, committed."""
    # A machine with no git identity of its own still commits the task.
    who = ["-c", "user.name=trial", "-c", "user.email=trial@example.invalid"]
    for args in (["init", "-q"], ["add", "-A"], [*who, "commit", "-q", "-m", "task"]):
        subprocess.run(["git", "-C", place, *args], check=True)


def arguments(usage: str, more: tuple = ()) -> tuple:
    """The task folder and the new folder an acceptance trial is given, each absolute, and what
    follows them, one of more where more is given; stops with the usage on any other."""
    given = sys.argv[1:]
    if len(given) < 2 or given[2:] not in ([], *([m] for m in more)):
        sys.exit(f"usage: {usage}")
    task, place = (os.path.abspath(p) for p in given[:2])
    if not os.path.isfile(os.path.join(task, "ccs.json")):
        sys.exit(f"{task} holds no ccs.json; give a task folder, such as dev/turn/trials/readme")
    for taken in (place, kept(place)):
        if os.path.exists(taken):
            sys.exit(f"{taken} is there already; give a new folder")
    return task, place, given[2:]


def ccs(task: str) -> dict:
    """The task's CCS."""
    with open(os.path.join(task, "ccs.json"), encoding="utf-8") as f:
        return json.load(f)


def repository(task: str, place: str, given: dict) -> None:
    """Makes a repository at place with what the task folder holds but its CCS and the trial's
    results, the CCS where the call names it, and each checklist the CCS names that the folder does
    not hold taken from rn's, by its name, so the trial reads rn's as they now are; it holds no
    README, so the work is made from nothing."""
    os.makedirs(place)
    for name in os.listdir(task):
        if name in ("ccs.json", "results.json"):
            continue
        source = os.path.join(task, name)
        copy = shutil.copytree if os.path.isdir(source) else shutil.copyfile
        copy(source, os.path.join(place, name))
    for checklist in entries(ccs(task), "checklist"):
        if os.path.exists(os.path.join(place, checklist)):
            continue
        name = os.path.basename(checklist)
        found = glob.glob(os.path.join(ROOT, "rn", "checklists", "**", name), recursive=True)
        if len(found) != 1:
            sys.exit(
                f"{checklist}: put it in the task folder, as rn's checklists hold no one {name}"
            )
        os.makedirs(os.path.dirname(os.path.join(place, checklist)), exist_ok=True)
        shutil.copyfile(found[0], os.path.join(place, checklist))
    os.makedirs(os.path.join(place, os.path.dirname(given["ccs"])), exist_ok=True)
    shutil.copyfile(os.path.join(task, "ccs.json"), os.path.join(place, given["ccs"]))
    committed(place)


def folder(place: str) -> str:
    """The folder Claude Code keeps the records of a session run in place in; stops where place is
    so long a path that Claude Code names the folder with a hash, not made before the run."""
    found = record.folders(place)
    if not found:
        sys.exit(f"{place} is too long a path; give a shorter new folder")
    return found[0]


def kept(place: str) -> str:
    """Where what a run in place gave back is kept once place is removed."""
    return place.rstrip("/") + ".work"


def keep(task: str, place: str, result: str) -> None:
    """Keeps for the judge, beside place, what the run in it gave back: place as it ended but its
    git, which holds the task as the run left it, and the work, with the task's CCS at
    `.tasks/ccs.json`, where turn's call names it, whatever form of it the run was given; the result
    and what the run kept beside it are left out, as the judge reads the whole work alone."""
    name = os.path.basename(result)
    shutil.copytree(place, kept(place), ignore=shutil.ignore_patterns(".git", name, name + ".*"))
    os.makedirs(os.path.join(kept(place), ".tasks"), exist_ok=True)
    shutil.copyfile(os.path.join(task, "ccs.json"), os.path.join(kept(place), ".tasks", "ccs.json"))


def shown(task: str, place: str, result: str) -> None:
    """Prints the work the task's CCS names and the result, as they are in place."""
    for name in [*entries(ccs(task), "deliverable"), result]:
        path = os.path.join(place, name)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                print(f"--- {name}\n{f.read()}")


def use(plugin: str) -> None:
    """Puts the scripts of the copy of turn at plugin first on the path, in place of the working
    tree's this module took, so what a trial imports of turn from here on is the copy's, as the run
    uses it."""
    scripts = os.path.join(plugin, "scripts")
    sys.path.insert(0, scripts)
    for name in os.listdir(scripts):
        sys.modules.pop(os.path.splitext(name)[0], None)


@contextlib.contextmanager
def removed(*paths: str) -> Generator[None, None, None]:
    """Removes each path once the trial ends, however it ends, a failed run of Claude Code
    included."""
    try:
        yield
    finally:
        for path in paths:
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.exists(path):
                os.remove(path)


def begun(plugin: str, place: str, given: dict) -> None:
    """Starts a run of the copy of turn at plugin on the call in place, its check given as the roles
    trials set it, as the orchestrator would."""
    script = os.path.join(plugin, "scripts", "turn.py")
    check = json.dumps(CHECK)
    for args, text in ((["start", json.dumps(given)], ""), (["next", given["result"]], check)):
        subprocess.run(
            [sys.executable, script, *args],
            input=text,
            cwd=place,
            check=True,
            capture_output=True,
            text=True,
        )


def turn(place: str) -> str:
    """Copies the turn of this working tree beside place, so the run uses it as it is when the run
    starts, and gives the copy's folder."""
    plugin = place.rstrip("/") + "-turn"
    shutil.copytree(os.path.join(ROOT, "turn"), plugin)
    return plugin
