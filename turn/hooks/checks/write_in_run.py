"""During a run, a file is written only where the work goes and in the run's evidence, so the user
takes turn's change as one diff; and a file of the work is not written once the first user has been
handed it, so the version read is the version returned."""

import os

from ccs import deliverables
from state import read_json

from checks.open_run import open_run

TOOLS = {"Write": "file_path", "Edit": "file_path", "NotebookEdit": "notebook_path"}


def check(data):
    run = open_run(data) if data.get("tool_name") in TOOLS else None
    if run is None:
        return []
    cwd = data["cwd"]
    written = os.path.realpath(
        os.path.join(cwd, data["tool_input"].get(TOOLS[data["tool_name"]], ""))
    )
    goes = deliverables(read_json(os.path.join(cwd, run["in"]), run["in"]))
    folder = os.path.realpath(os.path.join(cwd, run["work"]))
    if written in [os.path.realpath(os.path.join(cwd, d)) for d in goes]:
        return []
    if not written.startswith(folder + os.sep):
        return [
            (
                f"steps 4 to 12: a run writes only {', '.join(goes)} and {run['work']}/, so the user "
                f"takes turn's change as one diff; {written} is left as it is"
            )
        ]
    if written.startswith(os.path.join(folder, "work") + os.sep) and os.path.isfile(
        os.path.join(cwd, run["work"], "first-user-brief.json")
    ):
        return [
            (
                "step 9: the work has been handed to the first user, and the version read is the "
                f"version returned, so a change to it goes into the second round or the next call; "
                f"{written} is left as it is"
            )
        ]
    return []
