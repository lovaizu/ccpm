"""What turn's trials share: the call, the flow trial's task made a repository, with its check and a
README that falls short, the acceptance trials' arguments, their clone of the playground and the
copy kept of what a run gave back, and the copy of turn a run uses; with Claude Code started on it
as its user starts it, and what a record shows of a role's work, which every plugin's trials
share."""

import glob
import json
import os
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# Starting Claude Code and reading its records are what every plugin's trials share, kept in lane's;
# how a CCS and a checklist are read is turn's own.
sys.path.insert(0, os.path.join(ROOT, "dev", "lane", "trials"))
sys.path.insert(0, os.path.join(ROOT, "turn", "scripts"))

import record
from call import entries, items  # noqa: F401
from trying import agents, claude, show  # noqa: F401

# The orchestrator's check of the flow trial's task: each item's Good found in the decisions.
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
# A README for the flow trial's task that names no license, so the first user stops at B-1.
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


def task(place: str, given: dict, decisions: "str | None" = None) -> None:
    """Makes the flow trial's task a repository at place, its CCS where the call names it, and its
    decisions, when given, replaced with decisions."""
    shutil.copytree(os.path.join(os.path.dirname(__file__), "flow", "task"), place)
    if decisions is not None:
        with open(os.path.join(place, "notes", "decisions.md"), "w", encoding="utf-8") as f:
            f.write(decisions)
    os.makedirs(os.path.join(place, ".tasks"))
    shutil.move(os.path.join(place, "ccs.json"), os.path.join(place, given["ccs"]))
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


def playground(task: str, place: str, trial: str) -> None:
    """Clones lovaizu/playground to place, on a branch of its own named for the trial and pushed
    nowhere, the playground's own README gone, so the work is made from nothing; with what the task
    folder holds but its CCS and the trial's results, and each checklist the CCS names that the
    folder does not hold taken from rn's, by its name, so the trial reads rn's as they now are."""
    subprocess.run(["gh", "repo", "clone", "lovaizu/playground", place, "--", "-q"], check=True)
    branch = f"turn-{trial}-{int(time.time())}"
    subprocess.run(["git", "-C", place, "switch", "-q", "-c", branch], check=True)
    os.remove(os.path.join(place, "README.md"))
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
    shutil.copytree(
        place, kept(place), ignore=shutil.ignore_patterns(".git", ".turn", name, name + ".*")
    )
    os.makedirs(os.path.join(kept(place), ".tasks"), exist_ok=True)
    shutil.copyfile(os.path.join(task, "ccs.json"), os.path.join(kept(place), ".tasks", "ccs.json"))


def shown(task: str, place: str, result: str) -> None:
    """Prints the work the task's CCS names and the result, as they are in place."""
    for name in [*entries(ccs(task), "deliverable"), result]:
        path = os.path.join(place, name)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                print(f"--- {name}\n{f.read()}")


def turn(place: str) -> str:
    """Copies the turn of this working tree beside place, so the run uses it as it is when the run
    starts, and gives the copy's folder."""
    plugin = place.rstrip("/") + "-turn"
    shutil.copytree(os.path.join(ROOT, "turn"), plugin)
    return plugin
