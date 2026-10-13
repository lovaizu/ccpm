"""The generator is called only once the user has been shown what the work will let its receiver do,
so they can stop a run whose aim they do not want before any work is written."""

import os

from checks.open_run import open_run
from checks.said import said


def check(data):
    given = data.get("tool_input", {})
    generator = data.get("tool_name") == "Agent" and given.get("subagent_type") == "turn:generator"
    run = open_run(data) if generator else None
    if run is None:
        return []
    with open(os.path.join(data["cwd"], run["work"], str(run["round"]), "aim.txt")) as f:
        if f"To make: {f.read().strip()}" in said(data):
            return []
    return ["step 4: say what `up.py aim` printed, as printed, before the generator is called"]
