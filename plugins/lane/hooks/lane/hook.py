"""The guard, as each hook entry that lay.py write lays runs it: `python3 hook.py <plugin>`, given
Claude Code's event on stdin. It prints a denial in the form Claude Code reads, or nothing where the
call goes on."""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # pragma: no mutate

from domain import guard, laid

NO_PLUGIN = (
    "lane: Lane can't check this call, as its hook entry doesn't end in hook.py and one plugin's"
    " name. The maker of the plugin must lay its proposal again with lay.py write."
)


def main(argv: list[str], given: str, folder: str) -> str:
    """What the hook prints for the event `given`, with the guard's code in `folder`, which lies
    in the plugin's hooks/ beside lanes.json."""
    if len(argv) != 2:
        told = NO_PLUGIN
    else:
        try:
            event = json.loads(given)
        except ValueError:
            event = None
        told = guard.decide(event, laid.read(os.path.dirname(folder)), argv[1])
    if told is None:
        return ""
    return json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": told,
            }
        }
    )


if __name__ == "__main__":  # pragma: no mutate
    printed = main(sys.argv, sys.stdin.read(), os.path.dirname(os.path.abspath(__file__)))
    if printed:
        print(printed)
