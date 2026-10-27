"""Tries the orchestrator's flow: the real orchestrator, flow and lanes, with the two roles stood
in for by agents of this folder that write the replies replies.py sets for the way named, so the run
takes that way. A stand-in for the calling AI calls turn on a task of two items, B-1 answered at its
part and B-2 in each part, in a repository made for the run:

- `plain`: every item Good at the first reading.
- `given`: the first user stopping at B-1 in a README that names no license, sent back to the
  generator by message, which adds it; the first user, sent the work made again, finds every Good.
- `sent`: the first user stopping at B-1 four times, sent back three times, the fourth stop ending
  the round with B-1 without Good; B-1 made again in the second round and given.
- `left`: as `sent` in two rounds, so B-1 waits on a question the orchestrator words; the calling
  AI answers it, and a third round gives B-1.
- `generator`: the generator asking before making anything, and again while making; each answer
  sent to it, it makes the work, and the run goes on as `plain`.
- `stopped`: as `plain`, the calling AI stopping the orchestrator once it is told the first user
  starts, and calling turn again with the same call, which goes on from that move.

Where turn asks, the calling AI takes each question's recommended answer as the user's, keeps it in
the task's decisions and sends it.

    python3 dev/turn/trials/orchestrator/orchestrator.py <way>

The replies each way sets are in replies.py. Prints the session, from whose records the trial is
judged, the order the agents were started in, the minutes, the cost and the result. Each run makes a
folder of its own, `turn/<yyyymmdd>-orchestrator-<way>-<random>/` in the system's temporary folder,
and prints its path. The repository and the copy of turn in it are removed when the run ends,
however it ends; what Claude Code printed is kept in it as `<way>.jsonl`, and the records stay in
Claude Code's own folder of the session.
"""

from __future__ import annotations

import glob
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import replies
import shared
import testing

CALL = shared.call("has")
START = shared.start(CALL)
USAGE = "usage: orchestrator.py <way>"
ASKS = (
    START
    + "If it returns with questions, take each question's recommended answer as the user's, write"
    " it into notes/decisions.md as a line of its own, and send the answer to the same agent with"
    " SendMessage, to the agent ID its start gave back. When it returns with no questions, reply"
    " with the line it returned."
)
PLAIN = START + "When it returns, reply with the line it returned."
# Each way's steps for the calling AI, in the order the docstring lists them.
STEPS = {
    "plain": PLAIN,
    "given": PLAIN,
    "sent": PLAIN,
    "left": ASKS,
    "generator": ASKS,
    "stopped": START
    + "turn sends you a line as each of its agents starts. Once a line says `turn:first-user"
    " starts`, the first time alone, stop the agent with TaskStop at once, loaded with ToolSearch,"
    " then start the `turn:up` agent in the background again with the same call. When it returns,"
    " reply with the line it returned.",
}
# Each way's replies, by name; stopped takes plain's, as the calling AI's steps make it.
REPLIES = dict({w: w for w in STEPS}, stopped="plain")
ROLES = ("turn:generator", "turn:first-user")

if len(sys.argv) != 2 or sys.argv[1] not in STEPS:
    sys.exit(f"{USAGE}, the way one of {', '.join(STEPS)}")
way = sys.argv[1]
run = shared.Run.made(f"orchestrator-{way}")
place = run.repo
plugin = shared.turn(run)
with shared.removed(place, plugin):
    shared.task(place, CALL)
    for agent in glob.glob(os.path.join(HERE, "roles", "*.md")):
        shutil.copyfile(agent, os.path.join(plugin, "agents", os.path.basename(agent)))
    # The stand-in roles keep no steps of the roles, so the roles' lanes are left out, each entry
    # read as lane's layer reads it; the orchestrator's are the ones tried.
    (entries,) = testing.lane_code(plugin, "entries")
    hooks = entries.read(plugin)
    for event in entries.EVENTS:
        hooks["hooks"][event] = [
            e
            for e in hooks["hooks"][event]
            if not any(
                entries.words(h["command"], event)[:1] in [[role] for role in ROLES]
                for h in e["hooks"]
            )
        ]
    with open(os.path.join(plugin, "hooks", "hooks.json"), "w", encoding="utf-8") as f:
        json.dump(hooks, f, indent=2)
    os.makedirs(os.path.join(plugin, "stand"))
    shutil.copyfile(os.path.join(HERE, "stand.py"), os.path.join(plugin, "stand", "stand.py"))
    with open(os.path.join(plugin, "stand", "replies.json"), "w", encoding="utf-8") as f:
        json.dump(replies.WAYS[REPLIES[way]], f, indent=2, ensure_ascii=False)
    start = time.time()
    record = os.path.join(run.top, f"{way}.jsonl")
    end = shared.claude(STEPS[way], [plugin], cwd=place, wait=60, record=record)
    session = end["session_id"]
    print(end.get("result"))
    print("session:", session, "cost:", end.get("total_cost_usd"))
    print("minutes:", round((time.time() - start) / 60, 1))
    # Each agent's record by when it began, its first entry's time.
    for begun, path in sorted(
        (next((e["timestamp"] for e in shared.record.read(p) or [] if "timestamp" in e), ""), p)
        for p in shared.agents(session)
    ):
        print(begun[11:19], shared.record.agent_type(path), path)
    path = os.path.join(place, CALL["result"])
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            print(f"--- {CALL['result']}\n{f.read()}")
