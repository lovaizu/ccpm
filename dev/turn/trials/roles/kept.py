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
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
CALL = {
    "ccs": ".tasks/ccs.json",
    "result": ".tasks/result.json",
    "kind": {
        "work": "deliverable",
        "checklist": "checklist",
        "receiver": "audience",
        "has": "code",
    },
}
CHECK = {
    "items": [
        {"checklist": "checklist.md", "item": "B-1", "can": "notes/decisions.md:2 names MIT."},
        {
            "checklist": "checklist.md",
            "item": "B-2",
            "can": "the decisions on demo and its license",
        },
    ],
    "questions": [],
}
# The set README the first user stops at, with no license.
UNLICENSED = "# demo\n\ndemo prints a greeting.\n\n## Use\n\nRun `sh demo.sh`.\n"

place = os.path.abspath(sys.argv[1])
shutil.copytree(os.path.join(os.path.dirname(HERE), "flow", "task"), place)
os.makedirs(os.path.join(place, ".tasks"))
shutil.move(os.path.join(place, "ccs.json"), os.path.join(place, CALL["ccs"]))
for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "task"]):
    subprocess.run(["git", "-C", place, *args], check=True)
plugin = place.rstrip("/") + "-turn"
shutil.copytree(os.path.join(ROOT, "turn"), plugin)
# The set README stands beside the repository, where no role reads it.
unlicensed = place.rstrip("/") + "-unlicensed.md"
with open(unlicensed, "w", encoding="utf-8") as f:
    f.write(UNLICENSED)
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
    input=json.dumps(CHECK),
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
done = subprocess.run(
    [
        "claude",
        "-p",
        STEPS,
        "--output-format",
        "json",
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
    check=True,
    capture_output=True,
    text=True,
)
end = json.loads(done.stdout)
session = end["session_id"]
print("session:", session, "minutes:", round((time.time() - start) / 60, 1))
print("last:", end.get("result"))
main = glob.glob(os.path.expanduser(f"~/.claude/projects/*/{session}.jsonl"))
agents = glob.glob(os.path.expanduser(f"~/.claude/projects/*/{session}/subagents/*.jsonl"))
for path in main + sorted(agents):
    print("record:", path)
    with open(path, encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            # Claude Code's copy of each request says again what the agent did.
            if entry.get("type") == "api-request-blob":
                continue
            if isinstance(entry.get("origin"), dict):
                print("  message:", entry["origin"].get("body"))
            content = entry.get("message", {}).get("content")
            if isinstance(content, str) and content.startswith("Stop hook feedback"):
                print("  stop:", content)
            for part in content if isinstance(content, list) else []:
                if part.get("type") == "tool_use":
                    print("  use:", part["name"], json.dumps(part["input"], ensure_ascii=False))
                elif part.get("type") == "tool_result" and part.get("is_error"):
                    print("  stop:", part.get("content"))
shutil.rmtree(place)
shutil.rmtree(plugin)
os.remove(unlicensed)
