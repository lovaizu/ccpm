"""The orchestrator waits for the user only once it has said each question it waits on, so the user
sees what to answer."""

import os

import up
from checks.open_run import open_run
from checks.said import said


def check(data):
    run = open_run(data) if not data.get("stop_hook_active") else None
    if run is None:
        return []
    here = os.getcwd()
    os.chdir(data["cwd"])
    try:
        waiting = [up.asked(run["work"])[k - 1]["question"] for k in up.unanswered(run["work"])]
    finally:
        os.chdir(here)
    text = said(data)
    unseen = [q for q in waiting if f"❓ {q}" not in text]
    if not unseen:
        return []
    return ["step 5: say what `up.py console` printed, as printed; the user has not seen: " + "; ".join(unseen)]
