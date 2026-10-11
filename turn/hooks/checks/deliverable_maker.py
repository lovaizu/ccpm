"""Keep the learner and the evaluator from changing the deliverable: only the generator changes it, so it is made
from one understanding of what it should be. The first user is kept off it by first_user_place."""
import os

from checks.places import CHANGES, inside, target


def check(data, t):
    if data.get("agent_type") not in ("turn:learner", "turn:evaluator") or data.get("tool_name") not in CHANGES:
        return []
    path = target(data)
    if inside(path, os.path.join(t["repo"], t["deliverable"])):
        return [f"{path} is the deliverable; only the generator changes the deliverable"]
    return []
