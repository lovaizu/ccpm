#!/usr/bin/env python3
"""PreToolUse hook for writ: keeps the first user from reading how the work was made, and runs
writ's own agents in the foreground.

Written so that even an old Python can run it far enough to stop the first user or the start
of a writ agent and ask for Python 3.9 or later; every other call passes.
"""

import json
import os
import sys

FIRST_USER = "writ:first-user"
INSTALL = ("writ: stopped because its checks need Python 3.9 or later; "
           "install Python 3.9 or later and run again.")


def is_first_user(raw, data):
    if isinstance(data, dict):
        return data.get("agent_type") == FIRST_USER
    return '"agent_type":"' + FIRST_USER + '"' in raw.replace(" ", "")


def starts_writ_agent(raw):
    return '"subagent_type":"writ:' in raw.replace(" ", "")


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except ValueError:
        data = None

    if sys.version_info < (3, 9):
        if is_first_user(raw, data) or starts_writ_agent(raw):
            sys.stderr.write(INSTALL + "\n")
            return 2
        return 0

    if not isinstance(data, dict):
        if is_first_user(raw, data):
            sys.stderr.write("writ: could not read the hook input, so the first user is stopped.\n")
            return 2
        return 0

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from checks import first_user_history, foreground_agents

    for check in (first_user_history,):
        reason = check.check(data)
        if reason:
            sys.stderr.write(reason + "\n")
            return 2
    updated = foreground_agents.update(data)
    if updated is not None:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                                 "permissionDecision": "allow",
                                                 "updatedInput": updated}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
