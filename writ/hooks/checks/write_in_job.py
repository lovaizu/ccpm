"""During a job, writ writes only its own job files, so the document and every checklist are written
by turn alone, which writes over a file only when git holds it."""

import os

from checks.open_job import open_job, turn_running

TOOLS = {"Write": "file_path", "Edit": "file_path", "NotebookEdit": "notebook_path"}


def check(data):
    job = open_job(data) if data.get("tool_name") in TOOLS else None
    # While turn's run is open, turn's own hooks keep the run to its files.
    if job is None or turn_running(data):
        return []
    written = os.path.realpath(
        os.path.join(data["cwd"], data["tool_input"].get(TOOLS[data["tool_name"]], ""))
    )
    if written.startswith(os.path.realpath(os.path.join(data["cwd"], job["folder"])) + os.sep):
        return []
    return [
        (
            f"a job writes only {job['folder']}/; the document and every checklist are written "
            f"by turn: settle in the form what the document should be, and make any other file "
            f"such as {os.path.basename(written)} as a job of its own"
        )
    ]
