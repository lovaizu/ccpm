"""PostToolUse entry of turn's hooks: runs each check after a tool call, shows the user what they
show, and tells Claude what they say."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
)

from checks import console_shown


def main():
    data = json.loads(sys.stdin.read())
    said, shown = console_shown.check(data)
    if said:
        sys.stderr.write("turn: " + "\n".join(said) + "\n")
        return 2
    if shown:
        print(json.dumps({"systemMessage": "\n".join(shown)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
