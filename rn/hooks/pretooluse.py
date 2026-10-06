#!/usr/bin/env python3
"""PreToolUse hook for rn: stops an agent's commit or push on the session's repository before it
runs."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import record  # noqa: E402
import shell  # noqa: E402
from checks import conductor_only_git  # noqa: E402


def main():
    data = json.load(sys.stdin)
    found = record.find(data)
    if not found:
        return 0
    cwd, top, _ = found
    return record.report(conductor_only_git.check(data.get("agent_type") or "",
                                                  shell.runs_of(data, cwd), top))


if __name__ == "__main__":
    sys.exit(main())
