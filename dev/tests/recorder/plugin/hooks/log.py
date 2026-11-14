"""Append the hook payload read on stdin, with the time it came, as one JSON line to $REC_LOG."""

import json
import os
import sys
import time

payload = json.load(sys.stdin)
with open(os.environ["REC_LOG"], "a") as log:
    log.write(json.dumps({"time": time.time(), "payload": payload}) + "\n")
