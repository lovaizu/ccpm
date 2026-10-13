"""The orchestrator stops only once the run has returned the work and the CCS, or while it waits for
the user or the generator, so a run is never left half done; it is told once, so it is never held
in a loop."""

import os

import up
from checks.open_run import open_run


def check(data):
    run = open_run(data) if not data.get("stop_hook_active") else None
    if run is None:
        return []
    here = os.getcwd()
    os.chdir(data["cwd"])
    try:
        resting = up.at_rest(run)
    finally:
        os.chdir(here)
    if resting:
        return []
    return [f"step 14: the run is open; run `python3 \"{up.SCRIPT}\" end {run['work']} {run['round']}` "
            f"and say what it printed"]
