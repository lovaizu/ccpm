"""The user is shown each line of the console as the run reaches it, and what the run's end or stop
says, by the hook itself, since what the orchestrator writes between its tool calls does not reach
the user on every run."""

import os
import re

import up
from checks.open_run import open_run

CLOSING = re.compile(r'up\.py"?\s+(end|stop)\b')


def check(data):
    """Returns what to tell the orchestrator, and the lines to show the user."""
    if data.get("tool_name") != "Bash":
        return [], []
    run = open_run(data)
    if run is None:
        closing = CLOSING.search(data["tool_input"].get("command", ""))
        said = data["tool_response"].get("stdout", "") if closing else ""
        return [], said.splitlines()
    here = os.getcwd()
    os.chdir(data["cwd"])
    try:
        return [], up.console(run["work"])
    except up.Stop as stop:
        return [str(stop)], []
    finally:
        os.chdir(here)
