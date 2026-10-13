#!/usr/bin/env python3
"""Stop entry of turn's hooks: runs each check as Claude stops, and keeps it at work with what they
say."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

from checks import questions_said, run_ended  # noqa: E402


def main():
    data = json.loads(sys.stdin.read())
    said = questions_said.check(data) or run_ended.check(data)
    if said:
        sys.stderr.write("turn: " + "\n".join(said) + "\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
