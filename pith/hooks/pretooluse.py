#!/usr/bin/env python3
"""PreToolUse hook for pith: keeps the first user from reading how the work was made."""

import json
import os
import sys


def main():
    data = json.loads(sys.stdin.read())
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from checks import first_user_history

    reason = first_user_history.check(data)
    if reason:
        sys.stderr.write(reason + "\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
