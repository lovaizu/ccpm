"""Stop the first user from reading how the work was made: git history and conversation records."""

import re
import shlex
from typing import List, Optional

FIRST_USER = "writ:first-user"
HISTORY_COMMANDS = {"log", "show", "blame", "reflog", "stash", "diff"}
# git options placed before the subcommand that take the next word as their value
OPTIONS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--super-prefix",
                      "--config-env", "--exec-path"}
CONVERSATION_RECORDS = re.compile(r"/\.claude/projects(?:/|$|[\s\"'`;|&)])")
SEPARATORS = re.compile(r"&&|\|\||[;|&\n()`]|\$\(")

REASON = ("writ: the first user does not read how the work was made "
          "(git history or Claude Code conversation records); use the work as it is.")


def _words(segment: str) -> List[str]:
    try:
        return shlex.split(segment)
    except ValueError:
        return segment.split()


def _runs_git_history(command: str) -> bool:
    for segment in SEPARATORS.split(command):
        words = _words(segment)
        for index, word in enumerate(words):
            if word != "git" and not word.endswith("/git"):
                continue
            rest = words[index + 1:]
            while rest and rest[0].startswith("-"):
                option = rest.pop(0)
                if option in OPTIONS_WITH_VALUE and rest:
                    rest.pop(0)
            if rest and rest[0] in HISTORY_COMMANDS:
                return True
    return False


def check(input_data: dict) -> Optional[str]:
    if input_data.get("agent_type") != FIRST_USER:
        return None
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input") or {}
    texts = [value for value in tool_input.values() if isinstance(value, str)]
    if any(CONVERSATION_RECORDS.search(text) for text in texts):
        return REASON
    if tool_name == "Bash" and _runs_git_history(str(tool_input.get("command", ""))):
        return REASON
    return None
