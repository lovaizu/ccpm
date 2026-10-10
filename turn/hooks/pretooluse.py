#!/usr/bin/env python3
"""PreToolUse hook for turn: before the conductor calls one of turn's agents, the record handed in
has what is needed, and no use or learning was skipped. Other calls pass untouched."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "scripts")]

import transcript  # noqa: E402
from checks import handed, order  # noqa: E402


def main():
    data = json.load(sys.stdin)
    if data.get("agent_type") or not data.get("transcript_path"):
        return 0
    inp = data.get("tool_input") or {}
    message = data.get("tool_name") == "SendMessage"
    now = "made" if message else transcript.AGENTS.get(inp.get("subagent_type"))
    if not now:
        return 0
    items = transcript.entries(data["transcript_path"])
    start, args = transcript.last_turn(items)
    if start is None:
        return 0
    done = transcript.calls(items, start)
    if message and inp.get("to") not in {a for w, a in done if w == "maker"}:
        return 0
    cwd = data.get("cwd") or os.getcwd()
    problems = (handed.check(args, cwd) if now != "made" else []) or \
        order.check([w for w, a in done], now)
    if problems:
        print("turn check:\n- " + "\n- ".join(problems), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
