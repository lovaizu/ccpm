"""During a run, a file is written only where the work goes and in the run's evidence, so the user
takes turn's change as one diff."""

import os

from ccs import entries
from state import read_json
from checks.open_run import open_run

TOOLS = {"Write": "file_path", "Edit": "file_path", "NotebookEdit": "notebook_path"}


def check(data):
    run = open_run(data) if data.get("tool_name") in TOOLS else None
    if run is None:
        return []
    written = os.path.realpath(os.path.join(data["cwd"], data["tool_input"].get(TOOLS[data["tool_name"]], "")))
    deliverable = entries(read_json(os.path.join(data["cwd"], run["in"]), run["in"]),
                             "focal_entities", "deliverable")[0]
    if written == os.path.realpath(os.path.join(data["cwd"], deliverable)) or \
            written.startswith(os.path.realpath(os.path.join(data["cwd"], run["work"])) + os.sep):
        return []
    return [f"a run writes only {deliverable} and {run['work']}/; {written} is left as it is"]
