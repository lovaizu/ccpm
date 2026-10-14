"""The job of the hook's session that is open in the repository, if there is one, and whether a run
of turn is open in that session."""

import json
import os

from state import JOB


def open_job(data):
    job = read(os.path.join(data.get("cwd", ""), JOB))
    return job if job and job["session"] == data.get("session_id") else None


def turn_running(data):
    run = read(os.path.join(data.get("cwd", ""), ".turn", "run.json"))
    return bool(run) and run.get("session") == data.get("session_id")


def read(path):
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        return json.load(f)
