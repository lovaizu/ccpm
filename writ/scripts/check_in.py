#!/usr/bin/env python3
"""PreToolUse on Skill: before one of the plugin's Returns starts, the CCS it is handed holds every
entry its IN requires and no open gap; otherwise the call is stopped with what is missing."""
import json
import os
import sys

import ccs


def missing(call, cwd):
    """What stops the call, or None to let it through."""
    called = ccs.returns().get(call.get("skill"))
    if not called:
        return None
    required = called[0]
    found = ccs.PATH.search(call.get("args") or "")
    if not found or not os.path.isfile(os.path.join(cwd, found.group(0))):
        return "Hand the path of its CCS, a .yaml file, as the skill's arguments."
    state = ccs.load(os.path.join(cwd, found.group(0)))
    with open(required) as f:
        entries = json.load(f)
    lacking = [f"{r['component']}: {r['type']} (from {r['from']})" for r in entries
               if not any(kind == r["type"] and value for kind, value in state.get(r["component"], []))]
    gaps = [value for kind, value in state["uncertainty_signal"] if kind == "gap"]
    if lacking or gaps:
        return (f"{found.group(0)} is not ready for {call['skill']}. Missing: {'; '.join(lacking) or 'none'}. "
                f"Open gaps: {'; '.join(gaps) or 'none'}.")
    return None


def main():
    hook = json.load(sys.stdin)
    reason = missing(hook.get("tool_input") or {}, hook.get("cwd") or os.getcwd())
    if reason:
        print(reason, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
