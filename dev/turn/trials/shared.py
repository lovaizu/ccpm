"""What turn's trials share: the call, the flow trial's task made a repository, with its check and a
README that falls short, and the copy of turn a run uses; with Claude Code started on it as its
user starts it, and what a record shows of a role's work, which every plugin's trials share."""

import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# Starting Claude Code and reading its records are what every plugin's trials share, kept in lane's.
sys.path.insert(0, os.path.join(ROOT, "dev", "lane"))

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
    for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "task"]):
        subprocess.run(["git", "-C", place, *args], check=True)


def turn(place: str) -> str:
    """Copies the turn of this working tree beside place, so the run uses it as it is when the run
    starts, and gives the copy's folder."""
    plugin = place.rstrip("/") + "-turn"
    shutil.copytree(os.path.join(ROOT, "turn"), plugin)
    return plugin
