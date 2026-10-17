"""turn's agents neither commit nor push, so the calling AI keeps the work in git on its own
judgment, after checking it."""

import re
from typing import Any

import agents

GIT = re.compile(r"\bgit\s+(commit|push)\b")


def check(event: dict[str, Any]) -> list[str]:
    if agents.role(event) is None or event["tool_name"] != "Bash":
        return []
    if GIT.search(str(event["tool_input"].get("command", ""))):
        return ["leave the work uncommitted; the caller checks it and keeps it in git"]
    return []
