"""Tries each of turn's four roles on its own: the real role, scripts and hooks, started by a stand-in
for the orchestrator with the prompt turn.py prints, on the flow trial's task of two items, one
answered at its part and one in each part. Between the roles the run is set as a trial means: the
orchestrator's check finds each item's Good in the decisions, the generator's work is replaced by a
set README that names no license, the round has sent back as often as it may, so the
evaluator follows the first user whatever it finds, and the learner is given B-1 without Good and
the records of the three roles before it. Prints, for each role, its record, from which the trial
is judged, the minutes, each tool it used, each hook stop, and the reply kept.

    python3 dev/turn/trials/roles/roles.py <new folder>

The repository and the copy of turn are removed when the run ends; the records stay in Claude
Code's own folder of each session.
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
README = "# demo\n\ndemo prints a greeting.\n\n## Use\n\nRun `sh demo.sh`.\n"
UNMET = {
    "checklist": "checklist.md",
    "item": "B-1",
    "gets": "The reader learns under which license they may use demo.",
    "places": ["README.md:1-4", "README.md:5-7"],
}

place = os.path.abspath(sys.argv[1])
shutil.copytree(os.path.join(os.path.dirname(HERE), "flow", "task"), place)
os.makedirs(os.path.join(place, ".tasks"))
shutil.move(os.path.join(place, "ccs.json"), os.path.join(place, CALL["ccs"]))
for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "task"]):
    subprocess.run(["git", "-C", place, *args], check=True)
plugin = place.rstrip("/") + "-turn"
shutil.copytree(os.path.join(ROOT, "turn"), plugin)
sys.path.insert(0, os.path.join(plugin, "scripts"))
os.chdir(place)

# The copy of turn's scripts, on the path only once it is made.
import run


def turn(*args: str, given: str = "") -> dict:
    done = subprocess.run(
        ["python3", os.path.join(plugin, "scripts", "turn.py"), *args],
        input=given,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(done.stdout)


def role(step: dict) -> str:
    """Starts the role turn.py printed, as the orchestrator would, and gives its record."""
    ask = f"""Start the `{step["agent"]}` agent with the JSON on the line below as its whole prompt,
exactly as it is, and wait for its reply. Then reply with its reply as it is.
{step["prompt"]}"""
    start = time.time()
    done = subprocess.run(
        [
            "claude",
            "-p",
            ask,
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
        capture_output=True,
        text=True,
    )
    session = json.loads(done.stdout)["session_id"]
    record = glob.glob(os.path.expanduser(f"~/.claude/projects/*/{session}/subagents/*.jsonl"))
    print(f"=== {step['agent']}  minutes: {round((time.time() - start) / 60, 1)}")
    print("session:", session)
    for path in record:
        print("record:", path)
        with open(path, encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                # Claude Code's copy of each request says again what the role did.
                if entry.get("type") == "api-request-blob":
                    continue
                content = entry.get("message", {}).get("content")
                for part in content if isinstance(content, list) else []:
                    if part.get("type") == "tool_use":
                        print("  use:", part["name"], json.dumps(part["input"], ensure_ascii=False))
                    elif part.get("type") == "tool_result" and part.get("is_error"):
                        print("  stop:", part.get("content"))
    kept = run.running(CALL["result"])
    print("reply kept:", json.dumps(kept["next"].get("reply") if kept else None))
    return record[0] if record else ""


turn("start", json.dumps(CALL))
records = [role(turn("next", CALL["result"], given=json.dumps(CHECK)))]
with open("README.md", "w", encoding="utf-8") as f:
    f.write(README)
records.append(role(turn("next", CALL["result"])))
kept = run.running(CALL["result"])
if kept is None:
    sys.exit("the run ended before the evaluator")
kept["sent"] = run.SENDS
run.write(CALL["result"], {"running": kept})
records.append(role(turn("next", CALL["result"])))
kept = run.running(CALL["result"])
if kept is None:
    sys.exit("the run ended before the learner")
kept.update(settled={"items": [UNMET], "questions": []}, records=records)
role(run.ask(kept, run.LEARNER, {"findings": [UNMET], "records": records, "lessons": []}))
os.chdir(ROOT)
shutil.rmtree(place)
shutil.rmtree(plugin)
