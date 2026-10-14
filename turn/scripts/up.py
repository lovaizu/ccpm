"""What turn:up needs to come out the same on every run: the CCS checked, the list and the forms
laid out, each form checked, the first user's copy, the console, and the work and the CCS written
back, or a stopped run's CCS. Each command is in the file of what it is about."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brief import brief
from console import aim
from forms import check, coverage
from lifecycle import end, start, stop
from state import Stop

USAGE = """usage: up.py start <in> <out> <session>
       up.py brief <work folder> <generator|first-user|evaluator|learner>
       up.py coverage <work folder> <generator|evaluator>
       up.py check <work folder> <generator|hand-on|first-user|evaluator|orchestrator|learner>
       up.py aim <work folder> <what the work will let its receiver do>
       up.py console <work folder>
       up.py end <work folder>
       up.py stop <work folder>"""


COMMANDS = {
    "start": (start, 3),
    "brief": (brief, 2),
    "coverage": (coverage, 2),
    "end": (end, 1),
    "aim": (aim, 2),
    "stop": (stop, 1),
}


def main(argv):
    try:
        if argv[:1] == ["check"] and len(argv) == 3:
            found = check(*argv[1:])
            print("\n".join(found) or "filled")
            return 1 if found else 0
        command, count = COMMANDS.get(argv[0] if argv else "", (None, -1))
        if command is None or len(argv) - 1 != count:
            raise Stop(USAGE)
        command(*argv[1:])
        return 0
    except Stop as stop:
        print(stop)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
