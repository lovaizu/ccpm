#!/usr/bin/env python3
"""SubagentStop hook for turn: keeps each of turn's agents running until its own record shows it did
its job."""

import json
import os
import sys


def main():
    data = json.loads(sys.stdin.read())
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path[:0] = [here, os.path.join(here, "..", "scripts")]
    import turn_state
    from checks import grounds, read_whole

    if not data.get("agent_type", "").startswith("turn:"):
        return 0
    t = turn_state.of(data.get("session_id", ""))
    if t is None:
        return 0
    reasons = read_whole.check(data, t) + grounds.check(data, t)
    if reasons:
        print(json.dumps({"decision": "block", "reason": "turn: " + "\n".join(reasons)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
