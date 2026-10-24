"""Prints the next move of a publishing run as the tool call itself, one JSON line: running
status.py beside this script."""

import json
import os

status = os.path.join(os.path.dirname(os.path.abspath(__file__)), "status.py")
print("The next move:")
print(json.dumps({"tool": "Bash", "input": {"command": f"python3 {status}"}}))
