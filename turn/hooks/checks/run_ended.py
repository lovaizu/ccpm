"""The orchestrator stops only once the run has returned the work and the CCS, so a run is never
left half done; it is told once, so it is never held in a loop."""

import up
from checks.open_run import open_run


def check(data):
    run = open_run(data) if not data.get("stop_hook_active") else None
    if run is None:
        return []
    return [f"step 12: the run is open; run `python3 \"{up.SCRIPT}\" end {run['work']} {run['round']}` "
            f"and say what it printed"]
