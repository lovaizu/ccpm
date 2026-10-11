"""Keep the generator from changing anything in the repository but the deliverable; the rest is the
user's work."""
import os

from checks.places import CHANGES, inside, target


def check(data, t):
    if data.get("agent_type") != "turn:generator" or data.get("tool_name") not in CHANGES:
        return []
    path = target(data)
    if inside(path, t["repo"]) and not inside(path, os.path.join(t["repo"], t["deliverable"])):
        return [f"{path} is in the repository; change only the deliverable, {t['deliverable']}, and make "
                "anything else you need to check it outside the repository"]
    return []
