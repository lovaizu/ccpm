"""SubagentStop entry of turn's hooks: runs each check as an agent stops, and keeps it at work with
what they say."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

from checks import form_filled


def main():
    data = json.loads(sys.stdin.read())
    said = form_filled.check(data)
    if said:
        sys.stderr.write("turn: " + "\n".join(said) + "\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
