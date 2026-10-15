"""A run never commits or pushes, so the user decides what to commit once it returns."""

import re

from checks.open_run import open_run

COMMIT = re.compile(r"\bgit(\s+-[cC]\s+\S+|\s+--?[\w-]+(=\S+)?)*\s+(commit|push)(?=\s|$|[;&|])")


def check(data):
    run = open_run(data) if data.get("tool_name") == "Bash" else None
    if run is None or not COMMIT.search(data["tool_input"].get("command", "")):
        return []
    return [
        (
            "steps 1 to 14: a run never commits or pushes, so the user decides what to commit once "
            "the run returns"
        )
    ]
