"""Tries the generator and the first user kept started within a round: the real roles, scripts and
hooks, on the flow trial's task, started and sent messages by a stand-in for the orchestrator. The
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

CALL = shared.call("code")

place = os.path.abspath(sys.argv[1])
shared.task(place, CALL)
plugin = shared.turn(place)
# The set README stands beside the repository, where no role reads it.
unlicensed = place.rstrip("/") + "-unlicensed.md"
with open(unlicensed, "w", encoding="utf-8") as f:
    f.write(shared.UNLICENSED)
script = f'python3 "{os.path.join(plugin, "scripts", "turn.py")}"'
result = CALL["result"]


subprocess.run(
    ["python3", os.path.join(plugin, "scripts", "turn.py"), "start", json.dumps(CALL)],
    cwd=place,
    check=True,
    capture_output=True,
)
done = subprocess.run(
    ["python3", os.path.join(plugin, "scripts", "turn.py"), "next", result],
    input=json.dumps(shared.CHECK),
    cwd=place,
    check=True,
    capture_output=True,
    text=True,
)
prompt = json.loads(done.stdout)["prompt"]
STEPS = f"""Take these steps in order, each command in a Bash call of its own, exactly as written.
Wherever a step says to send a message, load SendMessage with ToolSearch (`select:SendMessage`) the
first time, and send the `message` turn.py printed last to its `to`, both as printed; then run
`{script} next {result}` with nothing, and again while it prints `{{"waiting": ...}}`.

1. Start the `turn:generator` agent, not in the background, with the JSON on the line below as its
   whole prompt, exactly as it is, and wait for its reply.
   {prompt}
2. Run `cp {unlicensed} README.md`. Then run `{script} next {result}`.
3. Start the `turn:first-user` agent, not in the background, with the `prompt` turn.py printed last
   as its whole prompt, exactly as it is, and wait for its reply.
4. Run `{script} next {result}`, and send a message, as above.
5. Send a message, as above.
6. Reply with what turn.py printed last, as it is."""

start = time.time()
end = shared.claude(STEPS, [plugin], cwd=place)
session = end["session_id"]
print("session:", session, "minutes:", round((time.time() - start) / 60, 1))
print("last:", end.get("result"))
main = glob.glob(os.path.expanduser(f"~/.claude/projects/*/{session}.jsonl"))
for path in main + sorted(shared.agents(session)):
    shared.show(path)
shutil.rmtree(place)
shutil.rmtree(plugin)
os.remove(unlicensed)
