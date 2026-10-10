#!/usr/bin/env python3
"""Prints the JSONL paths a learner reads for the use just made: the conversation's, and those of
turn's agents called since the last learner."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import transcript  # noqa: E402


def main():
    path = transcript.session_path()
    if not path:
        print("turn: this conversation's JSONL was not found from CLAUDE_CODE_SESSION_ID",
              file=sys.stderr)
        return 2
    items = transcript.entries(path)
    start, _ = transcript.last_turn(items)
    calls = transcript.calls(items, start) if start is not None else []
    last = max([i for i, (w, a) in enumerate(calls) if w == "learner"], default=-1)
    print(f"conversation: {path}")
    shown = set()
    for what, aid in calls[last + 1:]:
        if aid and aid not in shown:
            shown.add(aid)
            print(f"{'maker' if what == 'made' else what}: {transcript.agent_path(path, aid)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
