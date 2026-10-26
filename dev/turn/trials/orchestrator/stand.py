"""Gives a stand-in role of an orchestrator trial its next set reply, from the way of the run set
beside this file, counting each role's calls in a file beside this one, so every run of the trial
takes the same way."""

import json
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
role = sys.argv[1]
count = os.path.join(here, f"{role}.count")
try:
    with open(count, encoding="utf-8") as f:
        n = int(f.read())
except FileNotFoundError:
    # The role's first call.
    n = 0
with open(count, "w", encoding="utf-8") as f:
    f.write(str(n + 1))
with open(os.path.join(here, "replies.json"), encoding="utf-8") as f:
    replies = json.load(f)[role]
given = replies[min(n, len(replies) - 1)]
# The generator writes the work as well; every other role only replies.
print(json.dumps(given if role == "generator" else given["reply"]))
