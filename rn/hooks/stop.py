#!/usr/bin/env python3
"""Stop hook for rn: when the conductor ends its turn, the record keeps its form and every commit is
pushed."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import form  # noqa: E402
import record  # noqa: E402
from checks import pushed  # noqa: E402


def main():
    found = record.find(json.load(sys.stdin), finished_too=True)
    if not found:
        return 0
    _, top, sdir = found
    problems = form.check(top, sdir) + pushed.check(top)
    if problems:
        print(json.dumps({"decision": "block", "reason": "rn check:\n- " + "\n- ".join(problems)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
