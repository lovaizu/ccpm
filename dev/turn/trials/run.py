"""Runs turn as its user does, on a fresh clone of this repository, with the turn of this working
tree in place of the installed one, and prints how the run ended.

    python3 dev/turn/trials/run.py <new folder> <CCS file> <out name>

The CCS's paths are from the top of the repository. The clone holds this working tree's committed
state, so commit what the trial must see first.
"""

import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
place, ccs, out = sys.argv[1:4]
subprocess.run(["git", "clone", "-q", ROOT, place], check=True)
os.makedirs(os.path.join(place, ".tasks"), exist_ok=True)
shutil.copyfile(ccs, os.path.join(place, ".tasks", "in.json"))
ask = f"/turn:up in: .tasks/in.json\nout: .tasks/{out}"
done = subprocess.run(
    ["claude", "-p", ask, "--model", "opus", "--plugin-dir", os.path.join(ROOT, "turn"),
     "--settings", '{"enabledPlugins": {"turn@ccpm": false}}',
     "--permission-mode", "bypassPermissions", "--output-format", "json"],
    cwd=place, capture_output=True, text=True)
print(done.stdout[-3000:], done.stderr[-2000:])
