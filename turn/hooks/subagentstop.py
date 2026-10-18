"""SubagentStop entry of turn's hooks: runs each check as one of turn's agents ends, and keeps it
going with what they say."""

import json
import os
import sys
from typing import IO

# Not mutated: any place on the path finds the module.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # pragma: no mutate

import agents  # noqa: F401  (puts turn's scripts on the path the checks import from)
from checks import read_whole, role_reply, run_returned

CHECKS = (read_whole, role_reply, run_returned)


def main(stream: IO[str]) -> int:
    event = json.load(stream)
    os.chdir(event["cwd"])
    said = [s for c in CHECKS for s in c.check(event)]
    if said:
        sys.stderr.write("turn: " + "\n".join(said) + "\n")
        return 2
    return 0


# Not mutated: __name__ is that very string, so `is` or `<=` mean the same.
if __name__ == "__main__":  # pragma: no mutate
    sys.exit(main(sys.stdin))
