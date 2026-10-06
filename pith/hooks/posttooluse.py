#!/usr/bin/env python3
"""PostToolUse hook for pith: a result file written is checked against its form."""

import json
import os
import sys


def main():
    data = json.loads(sys.stdin.read())
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from checks import result_form

    reason = result_form.check(data)
    if reason:
        sys.stderr.write(reason + "\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
