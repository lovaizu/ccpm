"""Tries the orchestrator's flow: the real orchestrator, scripts and hooks, with the four roles stood
in for by agents of this folder that give replies set in replies.json, so the run takes every way a
run goes: the first user stopping at an item sent back to the generator by message three times, the
fourth stop going on to the evaluator, and at a part of another item given its Good at the next
reading; the evaluator differing from the first user; the learner after each round, with a lesson
taken once and none the second time; the second round, whose first user gives every item a Good at
its first reading, one at lines that do not give it, so the item is left without Good; or, with
`unanswered`, the same task with its decision taken out, so the run returns the question alone
before any work is made. A stand-in for the calling AI calls turn on a task of two items, one
answered at its part and one in each part, in a repository made for the run. Prints the session,
from whose JSONL and its agents' the trial is judged, the order the agents were started in, the
minutes and the result.

    python3 dev/turn/trials/flow/flow.py <new folder> [unanswered]

The repository and the copy of turn are removed when the run ends; the records stay in Claude
Code's own folder of the session.
"""

import glob
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import shared

CALL = shared.call("has")
STEP = f"""Start the `turn:up` agent in the background with
{json.dumps(CALL)}
When it returns, reply with the line it returned."""

place = os.path.abspath(sys.argv[1])
shared.task(place, CALL, "" if sys.argv[2:] == ["unanswered"] else None)
plugin = shared.turn(place)
for agent in glob.glob(os.path.join(HERE, "roles", "*.md")):
    shutil.copyfile(agent, os.path.join(plugin, "agents", os.path.basename(agent)))
os.makedirs(os.path.join(plugin, "stand"))
for name in ("stand.py", "replies.json"):
    shutil.copyfile(os.path.join(HERE, name), os.path.join(plugin, "stand", name))
start = time.time()
end = shared.claude(STEP, [plugin], cwd=place, wait=60)
session = end["session_id"]
print(end.get("result"))
print("session:", session, "cost:", end.get("total_cost_usd"))
print("minutes:", round((time.time() - start) / 60, 1))
for record in sorted(
    shared.agents(session), key=lambda r: os.path.getmtime(r.replace(".jsonl", ".meta.json"))
):
    with open(record, encoding="utf-8") as f:
        first = json.loads(f.readline()).get("timestamp", "")
    with open(record.replace(".jsonl", ".meta.json"), encoding="utf-8") as f:
        print(first[11:19], json.load(f).get("agentType"))
path = os.path.join(place, CALL["result"])
if os.path.exists(path):
    with open(path, encoding="utf-8") as f:
        print(f"--- {CALL['result']}\n{f.read()}")
shutil.rmtree(place)
shutil.rmtree(plugin)
