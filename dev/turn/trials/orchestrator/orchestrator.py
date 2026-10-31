"""Tries turn's orchestrator: the real orchestrator and its lanes, with the two roles stood in for
by agents of this folder that write the replies replies.py sets for the way named, so the run takes
that way. A stand-in for the calling AI calls turn on a task of two items, B-1 answered at its part
and B-2 in each part, in a repository made for the run:

- `plain`: every item Good at the first reading, the result holding both at their lines.
- `left`: the first user finding no Good for B-1 in a README that names no license, and ending
  without sending, the result holding B-1 in `left` with what the reader would need.
- `stopped`: as `plain`, the calling AI stopping the orchestrator once the first user has started,
  and calling turn again with the same call, which starts the generator again on what the run's
  folder holds.

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
PLAIN = START + "When it returns, reply with the line it returned."
# Each way's steps for the calling AI, in the order the docstring lists them.
STEPS = {
    "plain": PLAIN,
    "left": PLAIN,
    "stopped": START + "Wait until the first user has started, with `until grep -qs"
    ' \'"agentType":"turn:first-user"\' {records}/*.meta.json; do sleep 2; done` in a command of'
    " its own, then stop the agent with TaskStop at once, loaded with ToolSearch, and start the"
    " `turn:up` agent in the background again with the same call. When it returns, reply with the"
    " line it returned.",
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
    # The folder of each agent's record of the session, where an agent's meta file names its type
    # once it has started.
    records = os.path.dirname(
        shared.record.subagent(shared.record.conversation("*", shared.folder(place)), "*")
    )
    steps = STEPS[way].replace("{records}", records)
    end = shared.claude(steps, [plugin], cwd=place, wait=60, record=record)
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
