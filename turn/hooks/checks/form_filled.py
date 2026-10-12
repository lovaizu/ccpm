"""An agent of a run hands back only once every place of its form is filled, so the orchestrator
decides from answers to every item."""

import json
import os

import up


def check(data):
    role = data.get("agent_type", "").partition("turn:")[2]
    run_file = os.path.join(data.get("cwd", ""), up.RUN)
    if data.get("tool_name") != "SubagentHandback" or role not in up.ROLES or not os.path.isfile(run_file):
        return []
    with open(run_file) as f:
        run = json.load(f)
    if run["session"] != data.get("session_id"):
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
