"""turn's agents neither commit nor push, so the calling AI keeps the work in git on its own
judgment, after checking it."""

import re
from typing import Any

import agents

# git as the command of a statement, with its options, so text that speaks of a commit, such as a
# reading passed in a heredoc, is not taken for one.
GIT = re.compile(r"(?:^|[;&|(\n])\s*git(?:\s+-\S+(?:\s+[^-\s]\S*)?)*\s+(commit|push)\b")


def check(event: dict[str, Any]) -> list[str]:
    if agents.role(event) is None or event["tool_name"] != "Bash":
        return []
    if GIT.search(str(event["tool_input"].get("command", ""))):
        return ["leave the work uncommitted; the caller checks it and keeps it in git"]
    return []
