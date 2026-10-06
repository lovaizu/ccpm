#!/usr/bin/env python3
"""UserPromptExpansion hook for rn: remembers that this conversation runs rn once the user types an
rn command in it, so rn's reminder after a summary reaches only that conversation."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import record  # noqa: E402


def main():
    data = json.load(sys.stdin)
    if record.rn_command(data.get("command_name")):
        record.mark(record.store(), data.get("session_id", ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
