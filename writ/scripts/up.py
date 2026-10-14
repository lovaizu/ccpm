"""What writ:up needs to come out the same on every job: the checklists listed, the form laid, the
CCS for turn written only from a settled form, and the job closed on what turn returned."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from job import ccs, end, form, start
from state import Stop

USAGE = """usage: up.py start <session>
       up.py form <job folder> <checklist> [<checklist> ...]
       up.py ccs <job folder>
       up.py end <job folder>"""

COMMANDS = {"start": (start, 1), "ccs": (ccs, 1), "end": (end, 1)}


def main(argv):
    try:
        if argv[:1] == ["form"] and len(argv) >= 3:
            form(*argv[1:])
            return 0
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
