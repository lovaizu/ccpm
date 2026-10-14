"""Runs writ as its user does, in a new repository holding a copy of a trial's files, with the writ
and turn of this working tree in place of the installed ones, and prints the conversation as it
goes. Each time Claude waits on the user while writ's job is open, another Claude answers as the
user, from what the user knows and nothing else.

    python3 dev/writ/trials/run.py [--writ <folder>] <new folder> <what the user knows>
        <first message> <files> ...

Each folder of files is copied over the ones before it. With --writ, that writ runs in place of this
working tree's, such as the version in use, to compare with; turn is left out, as that version does
not use it. The trial ends once writ's job is closed, or, for a writ that keeps no job, once the
user has nothing to answer; and after an hour.
"""

import json
import os
import shutil
import subprocess
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
args = sys.argv[1:]
writ = args[1] if args[:1] == ["--writ"] else ""
place, knows, first, *files = args[2:] if writ else args
for folder in files:
    shutil.copytree(folder, place, dirs_exist_ok=True)
for args in (
    ["init", "-q"],
    ["add", "."],
    ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "the trial's files"],
):
    subprocess.run(["git", "-C", place, *args], check=True)
with open(knows) as f:
    known = f.read()
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
        writ or os.path.join(ROOT, "writ"),
        *([] if writ else ["--plugin-dir", os.path.join(ROOT, "turn")]),
        "--settings",
        '{"enabledPlugins": {"writ@ccpm": false, "turn@ccpm": false}}',
        "--permission-mode",
        "bypassPermissions",
    ],
    cwd=place,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True,
)
assert claude.stdin and claude.stdout
limit = threading.Timer(3600, claude.kill)
limit.daemon = True
limit.start()


def say(text):
    print(f"> {text}", flush=True)
    claude.stdin.write(
        json.dumps({"type": "user", "message": {"role": "user", "content": text}}) + "\n"
    )
    claude.stdin.flush()


def answer(said):
    """What the user, knowing only what they know, says back to writ's last words."""
    done = subprocess.run(
        ["claude", "-p", "--model", "opus", "--tools", ""],
        input=f"{known}\nwrit has just said to you:\n\n{said}\n\nReply as this user would, "
        "in a sentence or two, and nothing else; if writ asks you nothing, reply DONE.",
        capture_output=True,
        text=True,
        check=True,
    )
    return done.stdout.strip()


say(first)
last, event, took, asked = "", {}, 0, 0
for line in claude.stdout:
    event = json.loads(line)
    if event.get("type") == "assistant":
        for part in event["message"]["content"]:
            if part["type"] == "text":
                print(part["text"], flush=True)
                last = part["text"]
    elif event.get("type") == "result":
        took += event.get("duration_ms", 0)
        if not writ and not os.path.exists(os.path.join(place, ".writ", "job.json")):
            break
        reply = answer(last)
        if reply == "DONE":
            break
        say(reply)
        asked += 1
claude.stdin.close()
claude.wait()
print(
    "session:",
    event.get("session_id"),
    "answers:",
    asked,
    "minutes:",
    round(took / 60000, 1),
    "cost:",
    event.get("total_cost_usd"),
)
