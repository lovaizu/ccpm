#!/usr/bin/env python3
"""PostToolUse hook for rn: the record's form right after a record file is written, and the
conductor's commit right after it is made, before it is pushed."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import form  # noqa: E402
import record  # noqa: E402
import shell  # noqa: E402
from checks import decision_line, settled_whole, typed_command  # noqa: E402


def main():
    data = json.load(sys.stdin)
    found = record.find(data, finished_too=True)
    if not found:
        return 0
    cwd, top, sdir = found
    if data.get("tool_name") in ("Write", "Edit"):
        path = os.path.realpath((data.get("tool_input") or {}).get("file_path", ""))
        if path.startswith(sdir + os.sep) or path.endswith("verification.md"):
            return record.report(form.check(top, sdir))
    if not data.get("agent_type") and shell.on_repo(shell.runs_of(data, cwd), ("commit",), top):
        msg = record.head_message(top)
        rel = os.path.relpath(sdir, top)
        return record.report(decision_line.check(msg) + settled_whole.check(top, rel, msg)
                             + typed_command.check(top, rel, msg, record.store(),
                                                   data.get("session_id", "")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
