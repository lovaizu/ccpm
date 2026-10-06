#!/usr/bin/env python3
"""PreToolUse hook for rn: checks 9 to 12 before the tool call they judge, the conductor's commit
and push kept apart, and checks 1 to 3 before the first user is called. The first problem found
stops the call."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import form  # noqa: E402
import record  # noqa: E402
import shell  # noqa: E402
from checks import (commit_then_push, conductor_only_git, first_user_reads,  # noqa: E402
                    first_user_writes, foreground_agents)


def first_user_called(data, top, sdir):
    inp = data.get("tool_input") or {}
    if not data.get("agent_type") and data.get("tool_name") == "Agent" and \
            inp.get("subagent_type") == first_user_writes.FIRST_USER:
        return form.check(top, sdir)
    return []


def main():
    data = json.load(sys.stdin)
    found = record.find(data)
    if not found:
        return 0
    cwd, top, sdir = found
    agent = data.get("agent_type") or ""
    runs = shell.runs_of(data, cwd)
    store = record.store()
    return record.report(conductor_only_git.check(agent, runs, top)
                         or commit_then_push.check(agent, runs, top)
                         or first_user_reads.check_history(data, runs, top)
                         or first_user_writes.check(data, top, sdir, store)
                         or first_user_reads.check_files(data, sdir, store)
                         or foreground_agents.check(data)
                         or first_user_called(data, top, sdir))


if __name__ == "__main__":
    sys.exit(main())
