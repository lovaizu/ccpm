#!/usr/bin/env python3
"""UserPromptExpansion hook for rn: remembers that the user typed /rn:ty, /rn:gm or /rn:dn, which
check 7 spends on the commit that records it."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import record  # noqa: E402
from checks import typed_command  # noqa: E402


def main():
    data = json.load(sys.stdin)
    typed_command.note(record.store(), data.get("session_id", ""), data.get("command_name"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
