#!/usr/bin/env python3
"""Check a pith result file against its form (../references/result-form.md).

Usage, from the repository root: check_result.py <result-file> [<essentials-file>...]
Without essentials files, the ones its `Essentials:` line names are used.
Prints each problem on its own line; exits 1 if any, 0 if none.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from checks import evidence_found, every_question_answered, locations_exist  # noqa: E402
from parse import parse_result  # noqa: E402

CHECKS = (every_question_answered, locations_exist, evidence_found)


def problems(result_path, essentials_paths):
    if not os.path.isfile(result_path):
        return ["{}: no such file".format(result_path)]
    result = parse_result(result_path)
    essentials_paths = essentials_paths or result.essentials
    if not essentials_paths:
        return ["{}: no `Essentials:` line naming the essentials files".format(result_path)]
    missing = [path for path in essentials_paths if not os.path.isfile(path)]
    if missing:
        return ["{}: no such file".format(path) for path in missing]
    return [problem for check in CHECKS for problem in check.check(result, essentials_paths)]


def main(argv):
    if not argv:
        sys.stderr.write("usage: check_result.py <result-file> [<essentials-file>...]\n")
        return 2
    found = problems(argv[0], argv[1:])
    for problem in found:
        print(problem)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
