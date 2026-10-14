"""An agent of a run is handed only the brief the script wrote for it, so what it gets is the same on
every run and the steps before it are done."""

import os

from brief import AGENTS, SCRIPT

from checks.open_run import open_run


def check(data):
    given = data.get("tool_input", {})
    role = str(given.get("subagent_type", "")).partition("turn:")[2]
    run = open_run(data) if data.get("tool_name") == "Agent" and role in AGENTS else None
    if run is None:
        return []
    brief = os.path.join(data["cwd"], run["work"], f"{role}-brief.json")
    handed = os.path.join(data["cwd"], str(given.get("prompt", "")).strip())
    if os.path.isfile(brief) and os.path.realpath(handed) == os.path.realpath(brief):
        return []
    return [
        (
            f'step {AGENTS[role]}: run `python3 "{SCRIPT}" brief {run["work"]} {role}` '
            f"and hand the agent only the path it prints"
        )
    ]
