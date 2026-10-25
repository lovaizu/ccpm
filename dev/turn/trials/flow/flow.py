"""Tries the orchestrator's flow: the real orchestrator, flow and lanes, with the three roles stood in
for by agents of this folder that write replies set in replies/<way>.json, so the run takes the way
named. A stand-in for the calling AI calls turn on a task of two items, B-1 answered at its part and
B-2 in each part, in a repository made for the run:

- `plain`: every item Good at the first reading, the learner with no lesson.
- `given`: the first user stopping at B-1 in a README that names no license, sent back to the
  generator by message, which adds it; the first user, sent the work made again, finds every Good.
- `sent`: the first user stopping at B-1 four times, sent back three times, the fourth stop ending
  the round with B-1 without Good; B-1 made again in the second round and given; the learner with a
  lesson.
- `left`: as `sent` in two rounds, so B-1 waits on a question the orchestrator words; the calling
  AI answers it, and a third round gives B-1; a lesson of the project's own.
- `generator`: the generator asking before making anything, and again while making; each answer
  sent to it, it makes the work, and the run goes on as `plain`.
- `asked`: the task with its decision taken out, so the check asks the calling AI; the run goes on
  as `plain`.
- `stopped`: as `plain`, the calling AI stopping the orchestrator once it is told, after the first
  user's reading, that the learner will learn, and calling turn again with the same call, which
  goes on from that move.

Where turn asks, the calling AI takes each question's recommended answer as the user's, keeps it in
the task's decisions and sends it.

    python3 dev/turn/trials/flow/flow.py <way> <new folder>

Prints the session, from whose records the trial is judged, the order the agents were started in,
the minutes, the cost and the result. The repository and the copy of turn are removed when the run
ends; what Claude Code printed is kept as `<new folder>.jsonl`, and the records stay in Claude
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
START = f"Start the `turn:up` agent in the background with\n{json.dumps(CALL)}\n"
ASKS = (
    START
    + "If it returns with questions, take each question's recommended answer as the user's, write"
    " it into notes/decisions.md as a line of its own, and send the answer to the same agent with"
    " SendMessage, to the agent ID its start gave back. When it returns with a line saying the"
    " result is written, reply with that line."
)
PLAIN = START + "When it returns, reply with the line it returned."
# Each way's steps for the calling AI, in the order the docstring lists them.
STEPS = {
    "plain": PLAIN,
    "given": PLAIN,
    "sent": PLAIN,
    "left": ASKS,
    "generator": ASKS,
    "asked": ASKS,
    "stopped": START
    + "turn sends you a line before each move. Once a line says `turn:learner will`, the first"
    " time alone, stop the agent with TaskStop at once, loaded with ToolSearch,"
    " then start the `turn:up` agent in the background again with the same call. When it returns,"
    " reply with the line it returned.",
}
# Each way's replies, by name; asked and stopped take plain's, as the calling AI's steps make them.
REPLIES = dict({w: w for w in STEPS}, asked="plain", stopped="plain")
ROLES = ("turn:generator", "turn:first-user", "turn:learner")

way, place = sys.argv[1], os.path.abspath(sys.argv[2])
if way not in STEPS:
    sys.exit(f"flow.py: {way} is not a way; give one of {', '.join(STEPS)}")
shared.task(place, CALL, "" if way == "asked" else None)
plugin = shared.turn(place)
for agent in glob.glob(os.path.join(HERE, "roles", "*.md")):
    shutil.copyfile(agent, os.path.join(plugin, "agents", os.path.basename(agent)))
# The stand-in roles keep no steps of the roles, so the roles' lanes are left out; the
# orchestrator's are the ones tried.
hooks_file = os.path.join(plugin, "hooks", "hooks.json")
with open(hooks_file, encoding="utf-8") as f:
    hooks = json.load(f)
for event, entries in hooks["hooks"].items():
    hooks["hooks"][event] = [
        e for e in entries if not any(f" {r} " in h["command"] for r in ROLES for h in e["hooks"])
    ]
with open(hooks_file, "w", encoding="utf-8") as f:
    json.dump(hooks, f, indent=2)
os.makedirs(os.path.join(plugin, "stand"))
shutil.copyfile(os.path.join(HERE, "stand.py"), os.path.join(plugin, "stand", "stand.py"))
shutil.copyfile(
    os.path.join(HERE, "replies", f"{REPLIES[way]}.json"),
    os.path.join(plugin, "stand", "replies.json"),
)
start = time.time()
end = shared.claude(STEPS[way], [plugin], cwd=place, wait=60, record=place + ".jsonl")
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
        print(first[11:19], json.load(f).get("agentType"), record)
path = os.path.join(place, CALL["result"])
if os.path.exists(path):
    with open(path, encoding="utf-8") as f:
        print(f"--- {CALL['result']}\n{f.read()}")
shutil.rmtree(place)
shutil.rmtree(plugin)
