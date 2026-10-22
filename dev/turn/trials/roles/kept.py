"""Tries the generator and the first user kept started within a round: the real roles and their
lanes, on the flow trial's task, started and sent messages by a stand-in for the orchestrator making
the moves turn's flow prints. The
generator's work is replaced by a set README with no license, so the first user, given demo.sh as
what the receiver has, stops at B-1; the generator, sent where the first user stopped, what it did
there and what it did not get, makes the work again, which the first user reads again, with no
reading between. Prints the stand-in's session, from whose JSONL and its agents' the trial is
judged, the minutes, each tool every agent used, each hook stop, and what the script printed last.

    python3 dev/turn/trials/roles/kept.py <new folder>

The repository and the copy of turn are removed when the run ends; the records stay in Claude
Code's own folder of the session.
"""

import glob
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import shared

CALL = shared.call("has")

place = os.path.abspath(sys.argv[1])
shared.task(place, CALL)
plugin = shared.turn(place)
# The set README stands beside the repository, where no role reads it.
unlicensed = place.rstrip("/") + "-unlicensed.md"
with open(unlicensed, "w", encoding="utf-8") as f:
    f.write(shared.UNLICENSED)
script = f'python3 "{os.path.join(plugin, "scripts", "turn.py")}"'
result = CALL["result"]
for args, given in (
    (["start", json.dumps(CALL)], ""),
    (["next", result], json.dumps(shared.CHECK)),
):
    subprocess.run(
        ["python3", os.path.join(plugin, "scripts", "turn.py"), *args],
        input=given,
        cwd=place,
        check=True,
        capture_output=True,
        text=True,
    )
STEPS = f"""Take these steps, each command in a Bash call of its own, exactly as written. Load
SendMessage with ToolSearch (`select:SendMessage`) first.

1. Run `{script} next {result}`. Its last line is a move, `{{"tool": ..., "input": {{...}}}}`.
   - A SendMessage whose `to` is `main`: send nothing, and do step 1 again.
   - An Agent call: make it, its input as printed, not in the background, and wait for its reply.
     Then run `{script} next {result} <<'EOF'` with `{{"agent_id": "<the agent ID it gave back>"}}`,
     ending with `EOF`, and go to step 2.
   - Any other SendMessage: send it, its input as printed, then run `{script} next {result}` with
     nothing, again while it prints `{{"waiting": ...}}`, and go to step 2.
2. After the first Agent call alone, run `cp {unlicensed} README.md`. Where what turn.py printed last
   begins `turn: turn:first-user found` for the second time, reply with that line, and end.
   Otherwise do step 1 again."""

start = time.time()
end = shared.claude(STEPS, [plugin], cwd=place)
session = end["session_id"]
print("session:", session, "minutes:", round((time.time() - start) / 60, 1))
print("cost:", end.get("total_cost_usd"))
print("last:", end.get("result"))
main = glob.glob(os.path.expanduser(f"~/.claude/projects/*/{session}.jsonl"))
for path in main + sorted(shared.agents(session)):
    shared.show(path)
shutil.rmtree(place)
shutil.rmtree(plugin)
os.remove(unlicensed)
