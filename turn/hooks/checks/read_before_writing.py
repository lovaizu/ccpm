"""Keep each agent from writing what it returns before it has read whole what it decides from: the generator
before it changes the deliverable, the learner and the evaluator before they write their file. Checked only when it
finishes, a read made after the work could not be told from one that shaped it."""
import os

from checks import read_whole
from checks.places import CHANGES, inside, target


def returns(data, t):
    """Whether the call writes what the agent returns."""
    role = data.get("agent_type", "").split(":", 1)[-1]
    path = target(data)
    if role == "generator":
        return inside(path, os.path.join(t["repo"], t["deliverable"]))
    if role in ("learner", "evaluator"):
        return path == os.path.realpath(os.path.join(t["work"], f"{role}-{t['round']}.json"))
    return False


def check(data, t):
    if data.get("tool_name") not in CHANGES or not returns(data, t):
        return []
    return read_whole.check(data, t)
