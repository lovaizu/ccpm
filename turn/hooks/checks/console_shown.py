"""The user is shown each line of the console as the run reaches it, and what the run's end or stop
says, by the hook itself, since what the orchestrator writes between its tool calls does not reach
the user on every run; an agent's commands run the hook in the same session, and show it nothing,
since what they would show reaches only the agent."""

import os
import re

import state
from console import console

from checks.open_run import open_run

CLOSING = re.compile(r'up\.py"?\s+(?:end|stop)\s+([^\s;&|]+)')


def check(data):
    """Returns what to tell the orchestrator, and the lines to show the user."""
    if data.get("tool_name") != "Bash" or data.get("agent_id"):
        return [], []
    run = open_run(data)
    if run is None:
        return [], closed(data)
    here = os.getcwd()
    os.chdir(data["cwd"])
    try:
        return [], console(run["work"])
    except state.Stop as stop:
        return [str(stop)], []
    finally:
        os.chdir(here)


def closed(data):
    """The last lines of a run the command just closed, taken once."""
    closing = CLOSING.search(data["tool_input"].get("command", ""))
    path = (
        os.path.join(data["cwd"], closing.group(1).strip("'\""), state.CLOSING) if closing else ""
    )
    if not os.path.isfile(path):
        return []
    with open(path) as f:
        lines = f.read().splitlines()
    os.remove(path)
    return lines
