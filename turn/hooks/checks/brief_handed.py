"""An agent of a run is handed only the brief the script wrote for it, so what it gets is the same on
every run and the steps before it are done."""

import os

import up
from checks.open_run import open_run


def check(data):
    given = data.get("tool_input", {})
    role = str(given.get("subagent_type", "")).partition("turn:")[2]
    run = open_run(data) if data.get("tool_name") == "Agent" and role in up.AGENTS else None
    if run is None:
        return []
    brief = os.path.join(run["work"], str(run["round"]), f"{role}-brief.json")
    if str(given.get("prompt", "")).strip() == brief and os.path.isfile(os.path.join(data["cwd"], brief)):
        return []
    return [f"step {up.AGENTS[role]}: run `python3 \"{up.SCRIPT}\" brief {run['work']} {run['round']} {role}` "
            f"and hand the agent only the path it prints"]
