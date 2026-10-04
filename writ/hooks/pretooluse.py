#!/usr/bin/env python3
"""PreToolUse hook for writ: keeps the first user from reading how the work was made, and runs
writ's own agents in the foreground."""

import json
import os
import sys


def main():
    data = json.loads(sys.stdin.read())
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
