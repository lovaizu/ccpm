"""What turn's trials share: the call, the flow trial's task made a repository, with its check and a
README that falls short, the copy of turn a run uses, Claude Code started on it as its user starts
it, and what a record shows of a role's work."""

import glob
import json
import os
import shutil
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# The orchestrator's check of the flow trial's task: each item's Good found in the decisions.
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
# A README for the flow trial's task that names no license, so the first user stops at B-1.
UNLICENSED = "# demo\n\ndemo prints a greeting.\n\n## Use\n\nRun `sh demo.sh`.\n"


def call(has: str) -> dict:
    """The call turn is given, with the CCS key of what the work's receiver has."""
    return {
        "ccs": ".tasks/ccs.json",
        "result": ".tasks/result.json",
        "kind": {
            "work": "deliverable",
            "checklist": "checklist",
            "receiver": "audience",
            "use": "purpose",
            "has": has,
        },
    }


def task(place: str, given: dict, decisions: "str | None" = None) -> None:
    """Makes the flow trial's task a repository at place, its CCS where the call names it, and its
    decisions, when given, replaced with decisions."""
    shutil.copytree(os.path.join(os.path.dirname(__file__), "flow", "task"), place)
    if decisions is not None:
        with open(os.path.join(place, "notes", "decisions.md"), "w", encoding="utf-8") as f:
            f.write(decisions)
    os.makedirs(os.path.join(place, ".tasks"))
    shutil.move(os.path.join(place, "ccs.json"), os.path.join(place, given["ccs"]))
    for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "task"]):
        subprocess.run(["git", "-C", place, *args], check=True)


def turn(place: str) -> str:
    """Copies the turn of this working tree beside place, so the run uses it as it is when the run
    starts, and gives the copy's folder."""
    plugin = place.rstrip("/") + "-turn"
    shutil.copytree(os.path.join(ROOT, "turn"), plugin)
    return plugin


def claude(prompt: str, plugin: str, cwd: "str | None" = None, wait: int = 0) -> dict:
    """Runs Claude Code on prompt with the copy of turn in place of the installed one, as its user
    runs it, and gives what it printed last; wait is the minutes it waits for an agent started in
    the background, which it stops waiting for after 10 by default."""
    env = dict(os.environ)
    if wait:
        env["CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS"] = str(wait * 60 * 1000)
    done = subprocess.run(
        [
            "claude",
            "-p",
            prompt,
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
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )
    return json.loads(done.stdout)


def agents(session: str) -> list:
    """The records of each agent the session started."""
    return glob.glob(os.path.expanduser(f"~/.claude/projects/*/{session}/subagents/*.jsonl"))


def show(path: str) -> None:
    """Prints a record's path and, of what it holds, each message sent, each tool used and each
    hook stop."""
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
