"""What turn:up runs for what must come out the same on every run: the call checked and the run
started, and each reading recorded, sending items back to the generator or writing the result."""

import json
import os
import sys
from typing import IO

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import run
from call import Stop

USAGE = (
    "usage: turn.py start '<call JSON>'\n"
    "       turn.py read <result> < <the orchestrator's reading as JSON>"
)


def main(argv: list[str], stdin: IO[str]) -> int:
    """Prints what the orchestrator does next as JSON and gives 0, or prints what was wrong and
    gives 1."""
    try:
        if argv[:1] == ["start"] and len(argv) == 2:
            print(json.dumps({"prompt": run.start(argv[1])}))
        elif argv[:1] == ["read"] and len(argv) == 2:
            print(json.dumps(run.read(argv[1], stdin.read())))
        else:
            print(USAGE)
            return 1
    except Stop as stop:
        print(stop)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], sys.stdin))
