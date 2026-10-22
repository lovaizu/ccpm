"""Tries turn as its user does: a stand-in for the calling AI, in a clone of lovaizu/playground on a
branch of its own, calls turn on a task of this folder with the step text the README shows, checks
what comes back and fixes the work where it falls short. Prints the stand-in's session, from whose
JSONL and its agents' the trial is judged, and the time from the call to the return.

    python3 dev/turn/trials/trial.py <task folder, such as dev/turn/trials/readme> <new folder>

The clone, its branch and the copy of turn are removed when the run ends; the records stay in
Claude Code's own folder of the session. The turn of this working tree is used as it is when the run
starts.
"""

import json
import os
import shutil
import subprocess
import sys
import time

import shared

CALL = shared.call("source")
STEP = f"""Start the `turn:up` agent in the background with
{json.dumps(CALL)}
When it returns, check each Good against its lines, and put each question to the user.

The user is away: take each question's recommended answer as theirs. If no work came back, write
each answer into notes/readme.decisions.md, in place of what it changes there or as a line of its
own, so the decisions say one thing, and call turn again as above; otherwise write it into the work yourself. Then fix in the work whatever falls short of an item of the checklists, and end with a
list of each item you fixed and why, or "none"."""

task, place = (os.path.abspath(p) for p in sys.argv[1:3])
subprocess.run(["gh", "repo", "clone", "lovaizu/playground", place, "--", "-q"], check=True)
subprocess.run(
    ["git", "-C", place, "switch", "-q", "-c", f"turn-trial-{int(time.time())}"], check=True
)
# The playground's own README goes, so the work is made from nothing.
os.remove(os.path.join(place, "README.md"))
for name in ("csvtidy.py", "notes"):
    source = os.path.join(task, name)
    copy = shutil.copytree if os.path.isdir(source) else shutil.copyfile
    copy(source, os.path.join(place, name))
os.makedirs(os.path.join(place, "checklists"))
for name in ("product/readme.md", "usability.md"):
    shutil.copyfile(
        os.path.join(shared.ROOT, "rn", "checklists", name),
        os.path.join(place, "checklists", os.path.basename(name)),
    )
os.makedirs(os.path.join(place, ".tasks"))
shutil.copyfile(os.path.join(task, "ccs.json"), os.path.join(place, CALL["ccs"]))
plugin = shared.turn(place)
start = time.time()
end = shared.claude(STEP, [plugin], cwd=place, wait=120)
print(end.get("result"))
print("session:", end.get("session_id"), "cost:", end.get("total_cost_usd"))
print("minutes:", round((time.time() - start) / 60, 1))
for name in ("README.md", CALL["result"]):
    path = os.path.join(place, name)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            print(f"--- {name}\n{f.read()}")
shutil.rmtree(place)
shutil.rmtree(plugin)
