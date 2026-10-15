#!/usr/bin/env python3
"""PreToolUse hook for rn: checks 9 and 12 before the tool call they judge, and the conductor's
commit and push kept apart. The first problem found stops the call."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import record
import shell
from checks import commit_then_push, conductor_only_git, foreground_agents


def main():
    data = json.load(sys.stdin)
    found = record.find(data)
    if not found:
        return 0
    cwd, top, _ = found
    agent = data.get("agent_type") or ""
    runs = shell.runs_of(data, cwd)
    return record.report(
        conductor_only_git.check(agent, runs, top)
        or commit_then_push.check(agent, runs, top)
        or foreground_agents.check(data)
    )


sys.exit(main())
