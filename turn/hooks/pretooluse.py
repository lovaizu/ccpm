"""PreToolUse entry of turn's hooks: runs each check as a tool is called, and stops the call with what
they say."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

from checks import brief_handed, no_commit, write_in_run


def main():
    data = json.loads(sys.stdin.read())
    said = brief_handed.check(data) + write_in_run.check(data) + no_commit.check(data)
    if said:
        sys.stderr.write("turn: " + "\n".join(said) + "\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
