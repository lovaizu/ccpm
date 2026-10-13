"""Runs turn as its user does, on a fresh clone of this repository, with the turn of this working
tree in place of the installed one, answering each question turn asks with the next answer given,
and prints the conversation as it goes.

    python3 dev/turn/trials/run.py <new folder> <CCS file> <out name> [<answer> ...]

The CCS's paths are from the top of the repository. The clone holds this working tree's committed
state, so commit what the trial must see first. A question asked when no answer is left is answered
"Leave it; go on without it."
"""

import json
import os
import shutil
import subprocess
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
place, ccs, out, *answers = sys.argv[1:]
subprocess.run(["git", "clone", "-q", ROOT, place], check=True)
os.makedirs(os.path.join(place, ".tasks"), exist_ok=True)
shutil.copyfile(ccs, os.path.join(place, ".tasks", "in.json"))
claude = subprocess.Popen(
    ["claude", "-p", "--input-format", "stream-json", "--output-format", "stream-json", "--verbose",
     "--model", "opus", "--plugin-dir", os.path.join(ROOT, "turn"),
     "--settings", '{"enabledPlugins": {"turn@ccpm": false}}', "--permission-mode", "bypassPermissions"],
    cwd=place, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
limit = threading.Timer(3600, claude.kill)
limit.daemon = True
limit.start()


def say(text):
    print(f"> {text}", flush=True)
    claude.stdin.write(json.dumps({"type": "user", "message": {"role": "user", "content": text}}) + "\n")
    claude.stdin.flush()


say(f"/turn:up in: .tasks/in.json\nout: .tasks/{out}")
last = ""
for line in claude.stdout:
    event = json.loads(line)
    if event.get("type") == "assistant":
        for part in event["message"]["content"]:
            if part["type"] == "text":
                last = part["text"]
                print(last, flush=True)
    elif event.get("type") == "result":
        if "❓" in last:
            say(answers.pop(0) if answers else "Leave it; go on without it.")
            last = ""
        elif not os.path.exists(os.path.join(place, ".turn", "run.json")):
            break
claude.stdin.close()
claude.wait()
print("session:", event.get("session_id"), "cost:", event.get("total_cost_usd"))
