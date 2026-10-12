"""The run of the hook's session that is open in the repository, if there is one."""

import json
import os

import up


def open_run(data):
    run_file = os.path.join(data.get("cwd", ""), up.RUN)
    if not os.path.isfile(run_file):
        return None
    with open(run_file) as f:
        run = json.load(f)
    return run if run["session"] == data.get("session_id") else None
