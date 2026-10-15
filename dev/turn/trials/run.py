"""Runs turn as its user does, on a fresh clone of this repository, with the turn of this working
tree in place of the installed one, answering each question turn asks with the next answer given,
and prints the conversation as it goes. Given a folder a trial already made, it calls turn again
there, as a caller does on the CCS a run returned.

    python3 dev/turn/trials/run.py <new folder> <CCS file> <out name> [--stop <words>] [<answer> ...]

The CCS's paths are from the top of the repository. The clone holds this working tree's committed
state, so commit what the trial must see first. Each question shown is answered in turn, once
Claude waits; one asked when no answer is left is answered as a user who does not know would. With
--stop, the run is stopped as by Esc the first time the console shows what it will make, and the
words are said in its place.
"""

import json
import os
import shutil
import subprocess
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
place, ccs, out, *answers = sys.argv[1:]
stop = answers[1] if answers[:1] == ["--stop"] else None
answers = answers[2:] if stop else answers
if not os.path.isdir(place):
    subprocess.run(["git", "clone", "-q", ROOT, place], check=True)
# The turn of this working tree as it is now, so that a change made while the trial runs does not
# reach it halfway.
plugin = place.rstrip("/") + "-turn"
if not os.path.isdir(plugin):
    shutil.copytree(os.path.join(ROOT, "turn"), plugin)
os.makedirs(os.path.join(place, ".tasks"), exist_ok=True)
given = f"in-{out}"
shutil.copyfile(ccs, os.path.join(place, ".tasks", given))
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
        '{"enabledPlugins": {"turn@ccpm": false}}',
        "--permission-mode",
        "bypassPermissions",
    ],
    cwd=place,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True,
)
assert claude.stdin and claude.stdout
limit = threading.Timer(2 * 3600, claude.kill)
limit.daemon = True
limit.start()


def say(text):
    print(f"> {text}", flush=True)
    claude.stdin.write(
        json.dumps({"type": "user", "message": {"role": "user", "content": text}}) + "\n"
    )
    claude.stdin.flush()


say(f"/turn:up in: .tasks/{given}\nout: .tasks/{out}")
asked, stopped = 0, None
for line in claude.stdout:
    event = json.loads(line)
    shown = (
        [p["text"] for p in event["message"]["content"] if p["type"] == "text"]
        if event.get("type") == "assistant"
        else [event["content"]]
        if event.get("type") == "system" and event.get("subtype") == "informational"
        else []
    )
    for text in shown:
        print(text, flush=True)
        asked += text.count("❓")
        if stop and "To make:" in text:
            print("[Esc]", flush=True)
            claude.stdin.write(
                json.dumps(
                    {
                        "type": "control_request",
                        "request_id": "esc",
                        "request": {"subtype": "interrupt"},
                    }
                )
                + "\n"
            )
            claude.stdin.flush()
            stopped, stop, asked = stop, None, 0
    if event.get("type") == "result" and stopped:
        say(stopped)
        stopped = None
    elif event.get("type") == "result":
        if not os.path.exists(os.path.join(place, ".turn", "run.json")):
            break
        if asked:
            say(answers.pop(0) if answers else "I don't know; leave it out of the work.")
            asked -= 1
claude.stdin.close()
claude.wait()
print("session:", event.get("session_id"), "cost:", event.get("total_cost_usd"))
