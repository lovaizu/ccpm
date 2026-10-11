#!/usr/bin/env python3
"""PreToolUse hook for turn: stops what an agent of turn must not do when it tries it, and keeps it
from handing back its report before its own record shows it did its job."""

import json
import os
import sys


def main():
    data = json.loads(sys.stdin.read())
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, here)
    import turn_state
    from checks import (deliverable_maker, first_user_place, generator_place, grounds, handed, no_commit,
                        read_first, read_whole)

    t = turn_state.of(data.get("session_id", ""))
    if t is None:
        return 0
    data["agent_transcript_path"] = os.path.join(
        os.path.dirname(data.get("transcript_path", "")), data["session_id"], "subagents",
        f"agent-{data.get('agent_id', '')}.jsonl")
    if data.get("tool_name") == "SubagentHandback":
        if not data.get("agent_type", "").startswith("turn:"):
            return 0
        # The report is delivered by this call, so the check made as the agent stops comes too late.
        reasons = read_whole.check(data, t) + grounds.check(data, t)
    else:
        reasons = [r for c in (first_user_place, generator_place, deliverable_maker, read_first, no_commit,
                               handed) for r in c.check(data, t)]
    if reasons:
        sys.stderr.write("turn: " + "\n".join(reasons) + "\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
