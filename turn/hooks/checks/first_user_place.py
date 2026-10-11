"""Keep the first user inside its copy, with the deliverable as it was handed.

Reading the repository would give it knowledge the receiver does not have, and its stumbles would not
show where the receiver's would.
"""
import os
import shlex

from checks.places import CHANGES, inside, spellings, target


def check(data, t):
    if data.get("agent_type") != "turn:first-user" or not t["copy"]:
        return []
    copy = t["copy"]
    path = target(data)
    if path is not None:
        report = os.path.realpath(os.path.join(t["work"], f"first-user-{t['round']}.md"))
        if data["tool_name"] in CHANGES and path == report:
            return []
        if not inside(path, copy):
            return [f"{path} is outside your copy; work only inside {copy}"]
        if data["tool_name"] in CHANGES and inside(path, os.path.join(os.path.realpath(copy), t["deliverable"])):
            return [f"{path} is the deliverable; use it as it is handed, do not change it"]
        return []
    if data.get("tool_name") != "Bash":
        return []
    command = (data.get("tool_input") or {}).get("command", "")
    if any(s in command for s in spellings(t["repo"])):
        return [f"the command reaches {t['repo']}, outside your copy; work only inside {copy}"]
    try:
        words = shlex.split(command)
    except ValueError:
        words = command.split()
    starts_in_copy = words[:1] == ["cd"] and len(words) > 1 and inside(os.path.realpath(words[1]), copy)
    if starts_in_copy or inside(os.path.realpath(data.get("cwd", "")), copy):
        return []
    return [f"cd into your copy first: start the command with cd {copy} &&"]
