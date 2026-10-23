"""Tries turn as its user does: a stand-in for the calling AI, in a clone of lovaizu/playground on a
branch of its own, pushing nothing, calls turn on a task of this folder with the step text the
README shows, answers each question it is sent with its recommended answer, checks what comes back
and fixes the work where it falls short. With `stopped`, it stops turn during the first user's
reading, once the first user has started and before it replies, and calls it again with the same
call. Prints the stand-in's session, from whose JSONL and its agents' the trial is judged, and the
minutes from the call to the work coming back, read from turn's records.

    python3 dev/turn/trials/trial.py <task folder, such as dev/turn/trials/readme> <new folder> [stopped]

The clone, its branch and the copy of turn are removed when the run ends; the records stay in
Claude Code's own folder of the session. The turn of this working tree is used as it is when the run
starts.
"""

import json
import os
import re
import shutil
import sys
import time

import shared

CALL = shared.call("source")
START = f"Start the `turn:up` agent in the background with\n{json.dumps(CALL)}\n"
STEP = """turn sends you a line before each move and after each outcome; nothing need answer them.

The user is away: take each question's recommended answer as theirs, and write each into
notes/readme.decisions.md, in place of what it changes there or as a line of its own, so the
decisions say one thing. Where the agent replies with questions before any work is made, send the
answers to the same agent with SendMessage, loaded with ToolSearch, to the agent ID its start gave
back. Where it returns saying the result is written and the result holds questions, start the
`turn:up` agent in the background again with the same call, once the answers are in the decisions.
When the last call returns saying the result is written, check each Good of the result against its
lines in the work. Then fix in the work whatever falls short of an item of the checklists, and end
with a list of every item of the checklists, saying of each whether the work met it when it came
back, and of each you fixed, what and why."""
# Claude Code keeps a session's records in a folder named for the folder it runs in, each character
# but a letter or a digit made `-`, and an agent's meta file names its type once it has started.
RECORDS = os.path.expanduser("~/.claude/projects/{}/*/subagents/*.meta.json")
STOP = """Once a line says `turn:first-user will`, the first time alone, wait until the first user has
started, with `until grep -qs '"agentType":"turn:first-user"' {}; do sleep 2; done` in a command of
its own, then stop the agent with TaskStop, loaded with ToolSearch, and start the `turn:up` agent in
the background again with the same call.
"""

task, place = (os.path.abspath(p) for p in sys.argv[1:3])
stopped = sys.argv[3:] == ["stopped"]
shared.playground(task, place, "trial")
os.makedirs(os.path.join(place, ".tasks"))
shutil.copyfile(os.path.join(task, "ccs.json"), os.path.join(place, CALL["ccs"]))
plugin = shared.turn(place)
start = time.time()
stop = STOP.format(RECORDS.format(re.sub("[^A-Za-z0-9]", "-", place)))
end = shared.claude(START + (stop if stopped else "") + STEP, [plugin], cwd=place, wait=120)
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
