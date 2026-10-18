"""Tries the orchestrator's flow: the real orchestrator, scripts and hooks, with the four roles stood
in for by agents of this folder that give replies set in replies.json, so the run takes every way a
run goes: an item sent back, the evaluator differing from the findings, the learner and the work
made again, and the second reading. A stand-in for the calling AI calls turn on a task of one item
in a repository made for the run. Prints the session, from whose JSONL and its agents' the trial is
judged, the order the agents were started in, the minutes and the result.

    python3 dev/turn/trials/flow/flow.py <new folder>

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
    "kind": {"work": "deliverable", "checklist": "checklist", "receiver": "audience"},
}
STEP = f"""Start the `turn:up` agent in the background with
{json.dumps(CALL)}
When it returns, reply with the line it returned."""

place = os.path.abspath(sys.argv[1])
shutil.copytree(os.path.join(HERE, "task"), place)
os.makedirs(os.path.join(place, ".tasks"))
shutil.move(os.path.join(place, "ccs.json"), os.path.join(place, CALL["ccs"]))
for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "task"]):
    subprocess.run(["git", "-C", place, *args], check=True)
plugin = place.rstrip("/") + "-turn"
shutil.copytree(os.path.join(ROOT, "turn"), plugin)
for agent in glob.glob(os.path.join(HERE, "roles", "*.md")):
    shutil.copyfile(agent, os.path.join(plugin, "agents", os.path.basename(agent)))
os.makedirs(os.path.join(plugin, "stand"))
for name in ("stand.py", "replies.json"):
    shutil.copyfile(os.path.join(HERE, name), os.path.join(plugin, "stand", name))
start = time.time()
done = subprocess.run(
    [
        "claude",
        "-p",
        STEP,
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
    check=True,
    cwd=place,
    # claude -p stops waiting for turn, which runs in the background, after 10 minutes by default.
    env={**os.environ, "CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS": str(60 * 60 * 1000)},
    capture_output=True,
    text=True,
)
end = json.loads(done.stdout)
session = end.get("session_id")
print(end.get("result"))
print("session:", session, "cost:", end.get("total_cost_usd"))
print("minutes:", round((time.time() - start) / 60, 1))
for meta in sorted(
    glob.glob(os.path.expanduser(f"~/.claude/projects/*/{session}/subagents/*.meta.json")),
    key=os.path.getmtime,
):
    with open(meta.replace(".meta.json", ".jsonl"), encoding="utf-8") as f:
        first = json.loads(f.readline()).get("timestamp", "")
    with open(meta, encoding="utf-8") as f:
        print(first[11:19], json.load(f).get("agentType"))
path = os.path.join(place, CALL["result"])
if os.path.exists(path):
    with open(path, encoding="utf-8") as f:
        print(f"--- {CALL['result']}\n{f.read()}")
shutil.rmtree(place)
shutil.rmtree(plugin)
