#!/usr/bin/env python3
"""PreToolUse hook for turn: stops what an agent of turn must not do when it tries it."""

import json
import os
import sys


def main():
    data = json.loads(sys.stdin.read())
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path[:0] = [here, os.path.join(here, "..", "scripts")]
    import turn_state
    from checks import first_user_place, generator_place, handed, no_commit

    t = turn_state.of(data.get("session_id", ""))
    if t is None:
        return 0
    reasons = [r for c in (first_user_place, generator_place, no_commit, handed) for r in c.check(data, t)]
    if reasons:
        sys.stderr.write("turn: " + "\n".join(reasons) + "\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
