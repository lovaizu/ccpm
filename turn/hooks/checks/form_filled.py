"""An agent of a run hands back only once every place of its form is filled, so the orchestrator
decides from answers to every item."""

import os

import up
from checks.open_run import open_run


def check(data):
    role = data.get("agent_type", "").partition("turn:")[2]
    run = open_run(data) if data.get("hook_event_name") == "SubagentStop" and role in up.ROLES else None
    if run is None:
        return []
    here = os.getcwd()
    os.chdir(data["cwd"])
    try:
        found = up.check(run["work"], run["round"], role)
    except up.Stop as stop:
        found = [str(stop)]
    finally:
        os.chdir(here)
    if found:
        return [f"fill your form before handing back ({run['work']}/{run['round']}/{role}.json):"] + found
    return []
