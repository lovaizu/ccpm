"""During a run, each role reads and searches only in its inputs, turn's own files and its session's
tool output, so the work is made from what the caller decided, without bias from what was not
given; in the copy of the repository the work is made in, the orchestrator reads the work's files
alone."""

import os

from brief import AGENTS
from ccs import deliverables
from state import read_json

from checks.inputs import named, readable, role, within
from checks.open_run import open_run

TOOLS = {"Read": "file_path", "Grep": "path", "Glob": "path"}


def check(data):
    run = open_run(data) if data.get("tool_name") in TOOLS else None
    if run is None:
        return []
    # A search without a path searches the whole repository.
    path = data["tool_input"].get(TOOLS[data["tool_name"]]) or "."
    full = os.path.realpath(os.path.join(data["cwd"], path))
    if within(full, readable(data, run)) and not hidden(data, run, full):
        return []
    who = role(data)
    step = f"step {AGENTS[who]}" if who in AGENTS else "steps 2 to 12"
    return [
        (
            f"{step}: the {who.replace('-', ' ')} reads only its inputs, so the work is made without "
            f"bias from what was not given; {path} is not one of them. It may read {named(data, run)}"
        )
    ]


def hidden(data, run, full):
    """Whether the path is a file of the repository's copy the work is made in, other than one of the
    work's own, which the orchestrator does not read."""
    cwd = data["cwd"]
    copy = os.path.realpath(os.path.join(cwd, run["work"], "work"))
    if role(data) != "orchestrator" or not within(full, [copy]):
        return False
    goes = deliverables(read_json(os.path.join(cwd, run["in"]), run["in"]))
    return full not in [os.path.realpath(os.path.join(copy, d)) for d in goes]
