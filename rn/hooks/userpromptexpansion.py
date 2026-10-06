#!/usr/bin/env python3
"""UserPromptExpansion hook for rn: remembers that this conversation runs rn once the user types an
rn command in it, and that the user typed /rn:ty, /rn:gm or /rn:dn, which the commit recording it
spends."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import record  # noqa: E402
from checks import typed_command  # noqa: E402


def main():
    data = json.load(sys.stdin)
    if record.rn_command(data.get("command_name")):
        store = record.store()
        record.mark(store, data.get("session_id", ""))
        typed_command.note(store, data.get("session_id", ""), data.get("command_name"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
