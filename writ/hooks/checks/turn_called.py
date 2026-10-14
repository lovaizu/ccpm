"""turn is called in a job only with the CCS the script wrote from a settled form, as it wrote it,
so nothing reaches turn unsettled."""

import os
import re

from job import digest

from checks.open_job import open_job


def check(data):
    given = data.get("tool_input", {})
    job = open_job(data) if data.get("tool_name") == "Skill" else None
    if job is None or given.get("skill") != "turn:up":
        return []
    named = re.search(r"^in:\s*(\S+)", str(given.get("args", "")), re.MULTILINE)
    path = os.path.join(data["cwd"], named.group(1)) if named else ""
    given_path, given_digest = job.get("given", ["", ""])
    if (
        os.path.realpath(path) == os.path.realpath(os.path.join(data["cwd"], given_path))
        and os.path.isfile(path)
        and digest(path) == given_digest
    ):
        return []
    return [
        (
            f"step 5: settle the form, and run `up.py ccs {job['folder']}`; call turn with the "
            "two lines it prints, as they are"
        )
    ]
