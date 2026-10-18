"""PreToolUse entry of turn's hooks: runs each check as a tool is about to be used, and stops the
use with what they say."""

import json
import os
import sys
from typing import IO

# Not mutated: any place on the path finds the module.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # pragma: no mutate

import agents  # noqa: F401  (puts turn's scripts on the path the checks import from)
from checks import (
    call_given,
    no_commit,
    read_in_given,
    read_whole,
    role_given,
    start_as_called,
    write_work_alone,
)

CHECKS = (
    call_given,
    start_as_called,
    role_given,
    write_work_alone,
    no_commit,
    read_in_given,
    read_whole,
)


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
