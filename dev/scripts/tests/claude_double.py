#!/usr/bin/env python3
"""The double of Claude Code that the tests of dev/scripts/e2e.py put on the PATH as `claude`.

It plays the plan at $DOUBLE_PLAN, a JSON object, and adds each call to `calls.jsonl` beside
it. A call with `--json-schema` is the stand-in's: it prints, as `claude -p --output-format json`
does, a result whose `structured_output` is the plan's next item of `stand_in`, or that item as it
is where it's text. Any other call is a turn of the Claude Code under test, of the plan's next item
of `turns`. It runs each command of `SessionStart` and of `UserPromptSubmit` in
$CLAUDE_CONFIG_DIR/settings.json, as Claude Code runs a hook, on the conversation of the turn's
`session` where it names one, as /clear starts one, unless its `hooks` is false. It writes its
`transcript` lines into the session's transcript under $CLAUDE_CONFIG_DIR/projects/, its `subagents`
beside it, its `tmp` files under $TMPDIR, and its `files` into the working folder, commits each of
its `branches`, `{<name>: {<path>: <text>}}`, on a branch of that name in a worktree
`.claude/worktrees/<name>/` of the working folder, as a plugin may commit its work, prints its
`stream` lines, as `--output-format stream-json` does, sleeps its `sleep` seconds, and exits with
its `exit`. Each call notes what the working folder's `git log --oneline` gives, the text of each
file the turn's `show` names, and whether a push from it succeeded, so that a test checks the clone
that e2e.py removed."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time


def after(argv: list[str], flag: str) -> str | None:
    return argv[argv.index(flag) + 1] if flag in argv else None


def main(argv: list[str]) -> int:
    plan_path = os.environ["DOUBLE_PLAN"]
    with open(plan_path, encoding="utf-8") as f:
        plan = json.load(f)
    log = os.path.join(os.path.dirname(plan_path), "calls.jsonl")
    stand_in = "--json-schema" in argv
    n = sum(1 for each in _calls(log) if each["stand_in"] == stand_in)
    call = {
        "argv": argv,
        "cwd": os.getcwd(),
        "stand_in": stand_in,
        "env": {k: v for k, v in os.environ.items() if k.startswith("CLAUDE") or k == "TMPDIR"},
    }
    if stand_in:
        _note(log, call)
        reply = plan["stand_in"][n]
        print(reply if isinstance(reply, str) else json.dumps({"structured_output": reply}))
        return 0
    call.update(_clone())
    turn = plan["turns"][n]
    call["shown"] = _shown(turn)
    _note(log, call)
    return _play(turn, argv)


def _calls(log: str) -> list[dict]:
    """Each call that the log holds, or none where there's no log yet."""
    if not os.path.exists(log):
        return []
    with open(log, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def _note(log: str, call: dict) -> None:
    with open(log, "a", encoding="utf-8") as f:
        f.write(json.dumps(call) + "\n")


def _clone() -> dict:
    """What the working folder's `git log --oneline` gives, and whether a push from it succeeded."""
    log = subprocess.run(
        ["git", "log", "--oneline", "--format=%s"], capture_output=True, text=True, check=False
    ).stdout.splitlines()
    pushed = subprocess.run(
        ["git", "push", "-q", "origin", "HEAD:refs/heads/pushed"],
        capture_output=True,
        text=True,
        check=False,
    )
    return {"log": log, "pushed": pushed.returncode == 0}


def _shown(turn: dict) -> dict[str, str]:
    """The text of each file that the turn's `show` names, by its path."""
    shown = {}
    for path in turn.get("show", []):
        with open(path, encoding="utf-8") as f:
            shown[path] = f.read()
    return shown


def _play(turn: dict, argv: list[str]) -> int:
    """Plays the turn of the Claude Code under test, and gives its exit code."""
    config = os.environ["CLAUDE_CONFIG_DIR"]
    with open(os.path.join(config, "settings.json"), encoding="utf-8") as f:
        settings = json.load(f)
    # A turn that starts a new conversation, as /clear does, sends its SessionStart with the new ID.
    session = turn.get("session", after(argv, "--session-id") or after(argv, "--resume"))
    if turn.get("hooks", True):
        _run_hooks(settings, session, argv[-1])
    _write_transcripts(os.path.join(config, "projects", "-repo"), str(session), turn)
    _write_files(turn)
    _commit_branches(turn)
    for line in turn.get("stream", []):
        print(line if isinstance(line, str) else json.dumps(line))
    time.sleep(turn.get("sleep", 0))
    return turn.get("exit", 0)


def _run_hooks(settings: dict, session: str | None, prompt: str) -> None:
    """Runs each command of SessionStart and of UserPromptSubmit in the settings on its event."""
    events = [
        {"hook_event_name": "SessionStart", "session_id": session},
        {"hook_event_name": "UserPromptSubmit", "session_id": session, "prompt": prompt},
    ]
    for event in events:
        for entry in settings["hooks"][event["hook_event_name"]]:
            for hook in entry["hooks"]:
                subprocess.run(
                    hook["command"], shell=True, input=json.dumps(event), text=True, check=True
                )


def _write_transcripts(project: str, session: str, turn: dict) -> None:
    """Adds the turn's `transcript` lines to the session's transcript in the project's folder, and
    its `subagents` lines to each subagent's beside it."""
    os.makedirs(os.path.join(project, session, "subagents"), exist_ok=True)
    with open(os.path.join(project, f"{session}.jsonl"), "a", encoding="utf-8") as f:
        f.writelines(json.dumps(line) + "\n" for line in turn.get("transcript", []))
    for name, lines in turn.get("subagents", {}).items():
        with open(os.path.join(project, session, "subagents", name), "a") as f:
            f.writelines(json.dumps(line) + "\n" for line in lines)


def _write_files(turn: dict) -> None:
    """Writes the turn's `tmp` files under $TMPDIR and its `files` into the working folder."""
    for base, files in ((os.environ["TMPDIR"], "tmp"), (os.getcwd(), "files")):
        for path, text in turn.get(files, {}).items():
            full = os.path.join(base, path)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8") as f:
                f.write(text)


def _commit_branches(turn: dict) -> None:
    """Commits each of the turn's `branches` on a branch of its name, in a worktree of its own."""
    for name, files in turn.get("branches", {}).items():
        worktree = os.path.join(".claude", "worktrees", name)
        subprocess.run(["git", "worktree", "add", "-q", "-b", name, worktree], check=True)
        for path, text in files.items():
            with open(os.path.join(worktree, path), "w", encoding="utf-8") as f:
                f.write(text)
        for args in (["add", "-A"], ["commit", "-q", "-m", f"Work on {name}"]):
            subprocess.run(["git", *args], cwd=worktree, check=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
