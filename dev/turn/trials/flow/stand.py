"""Gives a stand-in role of a flow trial its next set reply, counting each role's calls in a file
beside this one, so every run of the trial takes the same way."""

import json
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
role = sys.argv[1]
count = os.path.join(here, f"{role}.count")
n = 0
if os.path.exists(count):
    with open(count) as f:
        n = int(f.read())
with open(count, "w") as f:
    f.write(str(n + 1))
with open(os.path.join(here, "replies.json")) as f:
    replies = json.load(f)[role]
given = replies[min(n, len(replies) - 1)]
# The generator writes the work as well; every other role only replies.
print(json.dumps(given if role == "generator" else given["reply"]))
