"""writ stops during a job only to wait on the user's answer, or once the job has ended with the
document handed back; it is told once, so it is never held in a loop."""

import json
import os

from checks.open_job import open_job, turn_running


def check(data):
    job = open_job(data) if not data.get("stop_hook_active") else None
    # While turn's run is open, turn's own hook keeps it going.
    form = os.path.join(data.get("cwd", ""), job["folder"], "form.json") if job else ""
    # Before the form is laid, writ may wait on the user's choice of checklist.
    if job is None or turn_running(data) or not os.path.isfile(form):
        return []
    with open(form) as f:
        if json.load(f)["asking"]:
            return []
    return [
        (
            f"step 10: the job is open; go on with its steps, and end it with `up.py end "
            f"{job['folder']}`; to wait on the user's answer, write the question to `asking` in "
            "the form first"
        )
    ]
