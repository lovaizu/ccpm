#!/usr/bin/env python3
"""Check a pith result file against its form (../result-form.md).

Usage, from the repository root: check_result.py <result-file> <essentials-file>...
Prints each problem on its own line; exits 1 if any, 0 if none.
"""

import os
import sys

if sys.version_info < (3, 9):
    sys.stderr.write("writ: Python 3.9 or later is needed; install it and run again.\n")
    sys.exit(1)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from checks import evidence_found, every_question_answered, locations_exist  # noqa: E402
from parse import parse_result  # noqa: E402

CHECKS = (every_question_answered, locations_exist, evidence_found)


def main(argv):
    if len(argv) < 2:
        sys.stderr.write("usage: check_result.py <result-file> <essentials-file>...\n")
        return 2
    result_path, essentials_paths = argv[0], argv[1:]
    for path in argv:
        if not os.path.isfile(path):
            print("{}: no such file".format(path))
            return 1
    result = parse_result(result_path)
    problems = [problem for check in CHECKS for problem in check.check(result, essentials_paths)]
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
