"""Tries the version of turn in use, 0.1.0, on the same task as trial.py, so the key results are
compared with it: in a clone of lovaizu/playground on a branch of its own, pushing nothing, the
calling AI runs 0.1.0's `turn:up` skill on the task's CCS written in 0.1.0's form, each question
it asks is answered as trial.py's stand-in answers, and once turn is done the calling AI checks
what came back and fixes the work where it falls short, as in trial.py. Prints what the calling AI
showed, its session, the minutes from the call to turn being done, and the work.

    python3 dev/turn/trials/baseline.py <task folder, such as dev/turn/trials/readme> <new folder>

0.1.0's turn runs in the main conversation and asks there, so the user's side is held by this
script over Claude Code's stream input, as 0.1.0's own trial held it. The clone, its branch and the
copy of turn are removed when the run ends; the records stay in Claude Code's own folder.
"""

import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import threading
import time

import shared

VERSION = "turn--v0.1.0"
ANSWER = "Take the answer you recommend."
# A run that ends its turns without being done, asking nothing more, is not answered for good.
ANSWERS = 8
CHECK = """turn is done. Check each item turn says the work meets against its lines in the work.
Then fix in the work whatever falls short of an item of the checklists, and end with a list of
every item of the checklists, saying of each whether the work met it when it came back, and of each
you fixed, what and why."""

task, place = (os.path.abspath(p) for p in sys.argv[1:3])
shared.playground(task, place, "baseline")
# The task's CCS in 0.1.0's form: its kinds named as 0.1.0 names them, and all nine parts.
with open(os.path.join(task, "ccs.json"), encoding="utf-8") as f:
    given = json.load(f)
kinds = {k: v for part in given.values() for entry in part for k, v in entry.items()}
ccs = {
    "focal_entities": [{"deliverable": kinds["deliverable"]}, {"receiver": kinds["audience"]}],
    "goal_orientation": [{"use": kinds["purpose"]}, {"acceptance": kinds["purpose"]}],
    "retrieved_artifacts": [
        *({"viewpoint": e["checklist"]} for e in given["retrieved_artifacts"] if "checklist" in e),
        *(
            {"source": v}
            for e in given["retrieved_artifacts"]
            for k, v in e.items()
            if k != "checklist"
        ),
    ],
    "constraints": [{"language": "English"}],
    **{p: [] for p in ("predictive_cue", "uncertainty_signal", "semantic_gist")},
    **{p: [] for p in ("relational_map", "episodic_trace")},
}
os.makedirs(os.path.join(place, ".tasks"))
with open(os.path.join(place, ".tasks", "in.json"), "w", encoding="utf-8") as f:
    json.dump(ccs, f, indent=1)
subprocess.run(["git", "-C", place, "add", "-A"], check=True)
who = ["-c", "user.name=trial", "-c", "user.email=trial@example.invalid"]
subprocess.run(["git", "-C", place, *who, "commit", "-q", "-m", "task"], check=True)
# 0.1.0's turn, taken from its tag.
plugin = place.rstrip("/") + "-turn"
archive = subprocess.run(
    ["git", "-C", shared.ROOT, "archive", VERSION, "turn"], capture_output=True, check=True
)
with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
    tar.extractall(plugin + "-tag")
shutil.move(os.path.join(plugin + "-tag", "turn"), plugin)
os.rmdir(plugin + "-tag")

claude = subprocess.Popen(
    [
        "claude",
        "-p",
        "--input-format",
        "stream-json",
        "--output-format",
        "stream-json",
        "--verbose",
        "--model",
        "opus",
        "--plugin-dir",
        plugin,
        "--settings",
        json.dumps({"enabledPlugins": {"turn@ccpm": False}}),
        "--permission-mode",
        "bypassPermissions",
    ],
    cwd=place,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True,
)
limit = threading.Timer(7200, claude.kill)
limit.daemon = True
limit.start()


def say(text: str) -> None:
    print(f"> {text}", flush=True)
    message = {"type": "user", "message": {"role": "user", "content": text}}
    assert claude.stdin
    claude.stdin.write(json.dumps(message) + "\n")
    claude.stdin.flush()


start = time.time()
say("/turn:up in: .tasks/in.json\nout: .tasks/out.json")
done, checked, event, answers = None, False, {}, 0
assert claude.stdout
for line in claude.stdout:
    event = json.loads(line)
    if event.get("type") == "assistant":
        for part in event["message"]["content"]:
            if part["type"] == "text":
                print(part["text"], flush=True)
    if event.get("type") != "result":
        continue
    if checked:
        break
    if os.path.exists(os.path.join(place, ".tasks", "out.json")):
        done = done or time.time()
        checked = True
        say(CHECK)
    elif answers < ANSWERS:
        answers += 1
        say(ANSWER)
    else:
        break
assert claude.stdin
claude.stdin.close()
claude.wait()
print("session:", event.get("session_id"), "cost:", event.get("total_cost_usd"))
if done:
    print("call to return minutes:", round((done - start) / 60, 1))
for name in ("README.md", ".tasks/out.json"):
    path = os.path.join(place, name)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            print(f"--- {name}\n{f.read()}")
shutil.rmtree(place)
shutil.rmtree(plugin)
