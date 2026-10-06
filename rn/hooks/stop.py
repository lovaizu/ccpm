#!/usr/bin/env python3
"""Stop hook for rn: checks 1 to 3, 8, 13 and 14 on every end of the conductor's turn, the second
end included, but for check 13: any end may speak to the user, and any may leave commits only on
this machine."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import form  # noqa: E402
import record  # noqa: E402
from checks import conversation_language, pushed, turn_end  # noqa: E402


def main():
    data = json.load(sys.stdin)
    found = record.find(data, finished_too=True)
    if not found:
        return 0
    _, top, sdir = found
    language = conversation_language.check(sdir, data.get("last_assistant_message") or "")
    problems = form.check(top, sdir) + pushed.check(top)
    if not problems:
        problems = turn_end.check(data, top, sdir)
    problems = language + problems
    if problems:
        print(json.dumps({"decision": "block", "reason": "rn check:\n- " + "\n- ".join(problems)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
