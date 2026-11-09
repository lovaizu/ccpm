"""Prints the text a start of the subagent given, `writer` or `reviewer`, begins with: its task,
the intents whose practices writer carries out, and the last review where `review.md` holds one."""

import json
import os
import sys

TASKS = {
    "writer": "Write the entries of the next release into `CHANGELOG.md`.\n"
    + json.dumps({"vital_few": ["Q1"]}),
    "reviewer": "Review the entries under `## Unreleased` of `CHANGELOG.md`.",
}
name = sys.argv[1] if len(sys.argv) > 1 else ""
if name not in TASKS:
    sys.exit(f"no subagent {name!r}; give `writer` or `reviewer`")
said = [TASKS[name]]
if os.path.isfile("review.md"):
    with open("review.md", encoding="utf-8") as f:
        said.append("The last review:\n" + f.read().strip())
print("\n\n".join(said))
