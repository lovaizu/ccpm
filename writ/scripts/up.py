"""What writ:up needs to come out the same on every call: the checklists for a kind, the content
file's place, the task turn is handed, and the report. Each command is in the file of what it is
about."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from checklists import Stop, checklists
from report import report
from task import content, task

USAGE = """usage: up.py checklists <kind>
       up.py content <document>
       up.py task --deliverable <path> [<path> ...] --receiver <who> [--use <what for>] --acceptance <what they can do> --checklist <path> [<path> ...] --content <path> [--reference <path> ...] [--opens <path> ...] [--language <language>]
       up.py report <CCS turn wrote back> <judgments>"""

COMMANDS = {"checklists": (checklists, 1), "content": (content, 1), "report": (report, 2)}


def main(argv):
    try:
        if argv[:1] == ["task"]:
            task(*argv[1:])
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
