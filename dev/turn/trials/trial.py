"""Tries turn as its user does: a stand-in for the calling AI, in a clone of lovaizu/playground on a
branch of its own, pushing nothing, calls turn on a task of this folder with the step text the
README shows, answers each question it is sent with its recommended answer, checks what comes back
and fixes the work where it falls short. With `stopped`, it stops turn once it is told the first
user will read, and calls it again with the same call. Prints the stand-in's session, from whose
JSONL and its agents' the trial is judged, and the minutes from the call to the work coming back,
read from turn's records.

    python3 dev/turn/trials/trial.py <task folder, such as dev/turn/trials/readme> <new folder> [stopped]

The clone, its branch and the copy of turn are removed when the run ends; the records stay in
Claude Code's own folder of the session. The turn of this working tree is used as it is when the run
starts.
"""

import json
import os
import shutil
import sys
import time

import shared

CALL = shared.call("source")
START = f"Start the `turn:up` agent in the background with\n{json.dumps(CALL)}\n"
STEP = """turn sends you a line before each move; nothing need answer them.

The user is away: if it returns with questions, take each question's recommended answer as theirs,
write each into notes/readme.decisions.md, in place of what it changes there or as a line of its
own, so the decisions say one thing, and send the answers to the same agent with SendMessage,
loaded with ToolSearch, to the agent ID its start gave back. When it returns saying the result is
written, check each Good of the result against its lines in the work. Then fix in the work whatever
falls short of an item of the checklists, and end with a list of every item of the checklists,
saying of each whether the work met it when it came back, and of each you fixed, what and why."""
STOP = """Once a line says `turn:first-user will`, the first time alone, stop the agent with TaskStop,
loaded with ToolSearch, then start the `turn:up` agent in the background again with the same call.
"""

task, place = (os.path.abspath(p) for p in sys.argv[1:3])
stopped = sys.argv[3:] == ["stopped"]
shared.playground(task, place, "trial")
os.makedirs(os.path.join(place, ".tasks"))
shutil.copyfile(os.path.join(task, "ccs.json"), os.path.join(place, CALL["ccs"]))
plugin = shared.turn(place)
start = time.time()
end = shared.claude(START + (STOP if stopped else "") + STEP, [plugin], cwd=place, wait=120)
print(end.get("result"))
print("session:", end.get("session_id"), "cost:", end.get("total_cost_usd"))
print("minutes:", round((time.time() - start) / 60, 1))
# From the call to the work coming back: the first orchestrator's first entry to the last one's
# last, as a call again starts another.
times = []
for record in shared.agents(end["session_id"]):
    with open(record.replace(".jsonl", ".meta.json"), encoding="utf-8") as f:
        if json.load(f).get("agentType") != "turn:up":
            continue
    with open(record, encoding="utf-8") as f:
        times += [json.loads(line).get("timestamp") for line in f]
times = sorted(t for t in times if t)
if times:
    print("call to return:", times[0], times[-1])
for name in ("README.md", CALL["result"]):
    path = os.path.join(place, name)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            print(f"--- {name}\n{f.read()}")
shutil.rmtree(place)
shutil.rmtree(plugin)
