"""turn's agents neither commit nor push in the repository they work in, so the calling AI keeps the
work in git on its own judgment, after checking it; a repository an agent makes of its own outside
it, to run what the work gives, is theirs."""

import os
import re
from typing import Any

import agents
import shell

# The git commands that keep or send a commit, `commit-tree` among them.
KEEPS = re.compile(r"(commit|push)\b")


def check(event: dict[str, Any]) -> list[str]:
    if agents.role(event) is None or event["tool_name"] != "Bash":
        return []
    cwd = os.path.realpath(event["cwd"])
    command = str(event["tool_input"].get("command", ""))
    for folder, said in shell.git(command, cwd):
        if said and KEEPS.match(said[0]) and shell.inside(folder, cwd):
            return ["leave the work uncommitted; the caller checks it and keeps it in git"]
    return []
