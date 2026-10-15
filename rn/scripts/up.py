"""rn's one command, run by the conductor for each step that must come out the same every run."""

import argparse
import os
import sys

# Python run in isolated mode does not look in this file's folder for the commands beside it.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import checklists
import report
import task

USAGE = """usage:
  up.py checklists <kind>
  up.py decisions <session folder> <document>
  up.py task <session folder> --deliverable <path> [<path> ...] --receiver <who>
      [--use <what for>] --acceptance <what they can do> --checklist <path> [<path> ...]
      --decisions <path> [--reference <path> ...] [--opens <path> ...] [--language <language>]
  up.py report <CCS turn wrote back> <judgments>"""


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(USAGE)


def parse_task(argv):
    parser = _Parser(add_help=False)
    parser.add_argument("session")
    # A flag given twice adds to what it was given before: a skill writes one flag per path.
    parser.add_argument("--deliverable", nargs="+", action="extend", required=True)
    parser.add_argument("--receiver", required=True)
    parser.add_argument("--use")
    parser.add_argument("--acceptance", required=True)
    parser.add_argument("--checklist", nargs="+", action="extend", required=True)
    parser.add_argument("--decisions", required=True)
    parser.add_argument("--reference", nargs="*", action="extend", default=[])
    parser.add_argument("--opens", nargs="*", action="extend", default=[])
    parser.add_argument("--language")
    return parser.parse_args(argv)


def run(argv):
    command, args = (argv[0], argv[1:]) if argv else ("", [])
    if command == "checklists" and len(args) == 1:
        return checklists.find(args[0])
    if command == "decisions" and len(args) == 2:
        return task.decisions_file(args[0], args[1])
    if command == "task":
        return task.write(parse_task(args))
    if command == "report" and len(args) == 2:
        return report.make(args[0], args[1])
    raise ValueError(USAGE)


def main(argv):
    # Every stop is a ValueError whose text is the sentence for whoever runs rn.
    try:
        print(run(argv))
    except ValueError as stop:
        print(stop)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
