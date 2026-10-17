"""PreToolUse entry of turn's hooks: runs each check as a tool is about to be used, and stops the
use with what they say."""

import json
import os
import sys
from typing import IO

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import agents  # noqa: F401  (puts turn's scripts on the path the checks import from)
from checks import (
    call_given,
    no_commit,
    read_in_given,
    role_given,
    start_as_called,
    write_work_alone,
)

CHECKS = (call_given, start_as_called, role_given, write_work_alone, no_commit, read_in_given)


def main(stream: IO[str]) -> int:
    event = json.load(stream)
    os.chdir(event["cwd"])
    said = [s for c in CHECKS for s in c.check(event)]
    if said:
        sys.stderr.write("turn: " + "\n".join(said) + "\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.stdin))
