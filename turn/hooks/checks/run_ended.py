"""The orchestrator stops only once the run has returned the work and the CCS, since it waits for no
one while the run is open; it is told once, so it is never held in a loop."""

from brief import SCRIPT

from checks.open_run import open_run


def check(data):
    run = open_run(data) if not data.get("stop_hook_active") else None
    if run is None:
        return []
    return [f'step 13: the run is open; run `python3 "{SCRIPT}" end {run["work"]}`']
