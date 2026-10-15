"""During a run, each role reads and searches only in its inputs, turn's own files and its session's
tool output, so the work is made from what the caller decided, without bias from what was not
given."""

import os

from brief import AGENTS

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
    if within(full, readable(data, run)):
        return []
    who = role(data)
    step = f"step {AGENTS[who]}" if who in AGENTS else "steps 2 to 12"
    return [
        (
            f"{step}: the {who.replace('-', ' ')} reads only its inputs, so the work is made without "
            f"bias from what was not given; {path} is not one of them. It may read {named(data, run)}"
        )
    ]
