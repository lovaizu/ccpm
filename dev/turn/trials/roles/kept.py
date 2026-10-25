"""Tries the generator and the first user kept started within a round, the two together, as what is
tried is each sent the other's outcome by message: the real roles and their lanes, on the flow
trial's task, started and sent messages by a stand-in for the orchestrator making the moves turn's
flow prints. The generator's work is replaced by a set README with no license, so the first user,
given demo.sh as what the receiver has, stops at B-1; the generator, sent where the first user
stopped, what it did there and what it did not get, makes the work again, which the first user
reads again, with no reading between. Prints the stand-in's session, from whose JSONL and its
agents' the trial is judged, the minutes, each tool every agent used, each hook stop, and what the
script printed last.

    python3 dev/turn/trials/roles/kept.py

Each run makes a folder of its own, `turn/<yyyymmdd>-kept-<random>/` in the system's temporary
folder, and prints its path. It holds the repository, the copy of turn and the set README, and is
removed when the run ends, however it ends; the records stay in Claude Code's own folder of the
session.
"""

from __future__ import annotations

import glob
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import shared

CALL = shared.call("has")

if sys.argv[1:2] == ["swap"]:
    # Run by the stand-in from the repository once the generator's work is taken: the set README
    # takes its place, and the first user, due next, is given the parts of the set README.
    unlicensed, copy = sys.argv[2:4]
    shared.use(copy)
    import prompts
    import state

    shutil.copyfile(unlicensed, "README.md")
    kept = state.going(CALL["result"])
    for prompt in (kept["next"]["prompt"], kept["prompts"][prompts.FIRST_USER]):
        prompt["parts"] = prompts.parts(kept)
    state.save(kept)
    sys.exit()

if len(sys.argv) != 1:
    sys.exit("usage: kept.py")
run = shared.Run.made("kept")
place = run.repo
plugin = shared.turn(run)
# The set README stands in the run's folder beside the repository, where no role reads it.
unlicensed = os.path.join(run.top, "unlicensed.md")
script = f'python3 "{os.path.join(plugin, "scripts", "turn.py")}"'
swap = f'python3 "{os.path.abspath(__file__)}" swap "{unlicensed}" "{plugin}"'
result = CALL["result"]
STEPS = f"""Take these steps, each command in a Bash call of its own, exactly as written. Load
SendMessage with ToolSearch (`select:SendMessage`) first.

1. Run `{script} next {result}`. Its last line is a move, `{{"tool": ..., "input": {{...}}}}`.
   - A SendMessage whose `to` is `main`: send nothing, and do step 1 again.
   - An Agent call: make it, its input as printed, not in the background, and wait for its reply.
     Then run `{script} next {result} <<'EOF'` with `{{"agent_id": "<the agent ID it gave back>"}}`,
     ending with `EOF`. After the first Agent call alone, run `{swap}` next. Go to step 2.
   - Any other SendMessage: send it, its input as printed, then run `{script} next {result}` with
     nothing, again while it prints `{{"waiting": ...}}`, and go to step 2.
2. Where what turn.py printed last begins `turn: turn:first-user found` for the second time, reply
   with that line, and end. Otherwise do step 1 again."""

with shared.removed(run.top):
    shared.task(place, CALL)
    with open(unlicensed, "w", encoding="utf-8") as f:
        f.write(shared.UNLICENSED)
    shared.begun(plugin, place, CALL)
    start = time.time()
    end = shared.claude(STEPS, [plugin], cwd=place)
    session = end["session_id"]
    print("session:", session, "minutes:", round((time.time() - start) / 60, 1))
    print("cost:", end.get("total_cost_usd"))
    print("last:", end.get("result"))
    main = glob.glob(shared.record.conversation(session))
    for path in main + sorted(shared.agents(session)):
        shared.show(path)
