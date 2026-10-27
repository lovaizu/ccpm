"""Tries the generator and the first user settling the work between themselves, the two together, as
what is tried is each sending the other what it needs by message: the real roles and their lanes,
on the orchestrator trial's task, started by a stand-in for the orchestrator as turn:up starts them.
The generator's work is replaced by a set README with no license, so the first user, given demo.sh
as what the receiver has, finds no Good for B-1 and sends the generator what the receiver would
need; the generator mends the work for it and replies, and the first user reads the mended work
again. Prints the stand-in's session, from whose JSONL and its agents' the trial is judged, the
minutes, each tool every agent used, each hook stop, and what the stand-in replied last.

    python3 dev/turn/trials/roles/kept.py

Each run makes a folder of its own, `turn/<yyyymmdd>-kept-<random>/` in the system's temporary
folder, and prints its path. It holds the repository, the copy of turn and the set README, and is
removed when the run ends, however it ends; the records stay in Claude Code's own folder of the
session.
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
import shared

CALL = shared.call("has")

if sys.argv[1:2] == ["swap"]:
    # Run by the stand-in from the repository once the generator has ended: the set README takes
    # the place of its work.
    shutil.copyfile(sys.argv[2], "README.md")
    sys.exit()

if len(sys.argv) != 1:
    sys.exit("usage: kept.py")
run = shared.Run.made("kept")
place = run.repo
plugin = shared.turn(run)
# The set README stands in the run's folder beside the repository, where no role reads it.
unlicensed = os.path.join(run.top, "unlicensed.md")
swap = f'python3 "{os.path.abspath(__file__)}" swap "{unlicensed}"'
STEPS = """Take these steps, each command in a Bash call of its own, exactly as written.

1. Start the `turn:generator` agent with the Agent tool, not in the background, with the JSON
   {generator} as its whole prompt, and wait for it to end. Keep the agent ID it gave back.
2. Run `{swap}`.
3. Start the `turn:first-user` agent with the Agent tool, not in the background, with the JSON
   {{"result": "{result}", "generator": "<the agent ID the generator's start gave back>"}} as its
   whole prompt, and wait for it to end.
4. Reply with the first user's reply, and end."""

with shared.removed(run.top):
    shared.task(place, CALL)
    with open(unlicensed, "w", encoding="utf-8") as f:
        f.write(shared.UNLICENSED)
    result = shared.begun(plugin, place, CALL)
    generator = json.dumps({"result": result})
    start = time.time()
    end = shared.claude(
        STEPS.format(generator=generator, swap=swap, result=result), [plugin], cwd=place
    )
    session = end["session_id"]
    print("session:", session, "minutes:", round((time.time() - start) / 60, 1))
    print("cost:", end.get("total_cost_usd"))
    print("last:", end.get("result"))
    main = glob.glob(shared.record.conversation(session))
    for path in main + sorted(shared.agents(session)):
        shared.show(path)
