"""What each role of a run reads: the inputs it is handed, turn's own files, and what Claude Code
keeps of its session's tool output, so the work is made from what the caller decided alone."""

import os

from brief import AGENTS
from ccs import entries
from state import read_json

TURN = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
# The places of a brief that name files; the rest is text, and `deliverable` is where the work
# goes, which no agent reads.
PATHS = (
    "work",
    "opens",
    "list",
    "form",
    "questions",
    "reading",
    "records",
    "content",
    "references",
)


def role(data):
    """The run's agent whose call this is, or the orchestrator, wherever it runs."""
    name = str(data.get("agent_type", "")).partition("turn:")[2]
    return name if data.get("agent_id") and name in AGENTS else "orchestrator"


def inputs(data, run):
    """The files and folders the role is handed, from the top of the repository."""
    cwd = data["cwd"]
    name = role(data)
    if name == "orchestrator":
        ccs = read_json(os.path.join(cwd, run["in"]), run["in"])
        found = [run["in"]] + [
            p
            for kind in ("checklist", "content", "reference")
            for p in entries(ccs, "retrieved_artifacts", kind)
        ]
        return found + [run["work"]]
    brief = os.path.join(run["work"], f"{name}-brief.json")
    if not os.path.isfile(os.path.join(cwd, brief)):
        return []
    given = read_json(os.path.join(cwd, brief), brief)
    return [shown(cwd, p) for k in PATHS if k in given for p in strings(given[k])] + [brief]


def strings(value):
    if isinstance(value, str):
        return [value]
    values = value.values() if isinstance(value, dict) else value
    return [s for v in values for s in strings(v)]


def shown(cwd, path):
    full = os.path.realpath(os.path.join(cwd, path))
    top = os.path.realpath(cwd)
    return os.path.relpath(full, top) if within(full, [top]) else path


def within(path, places):
    return any(path == p or path.startswith(p.rstrip(os.sep) + os.sep) for p in places)


def readable(data, run):
    """The full paths of the places the role may read in."""
    cwd = data["cwd"]
    places = [os.path.realpath(os.path.join(cwd, p)) for p in inputs(data, run)] + [TURN]
    if data.get("transcript_path"):
        folder = os.path.splitext(data["transcript_path"])[0]
        places.append(os.path.realpath(os.path.join(folder, "tool-results")))
    return places


def named(data, run):
    """What the role may read, as a stop says it."""
    found = inputs(data, run)
    return (", ".join(found) + " and " if found else "") + "turn's own files"
