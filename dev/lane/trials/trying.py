"""What every plugin's trials stand on: the folder of its own each run of a trial writes in, Claude
Code started on copies of plugins as their user starts it, its record kept, and what the records of
the agents it started show."""

from __future__ import annotations

import glob
import importlib.util
import json
import os
import subprocess
import sys
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
# The folder a trial writes in is made as a test's is, by testing.py, kept in the folder above.
sys.path.insert(0, os.path.dirname(HERE))
import testing

# How Claude Code keeps its records is read by lane's record.py, loaded from its file, so a
# plugin's trials standing on this module meet their own modules of the names lane's code has, such
# as call.
RECORD = os.path.join(HERE, "../../../lane/hooks/lane/record.py")
FOUND = importlib.util.spec_from_file_location("record", os.path.normpath(RECORD))
assert FOUND and FOUND.loader
record = importlib.util.module_from_spec(FOUND)
FOUND.loader.exec_module(record)


def folder(plugin: str, name: str) -> str:
    """A new folder of the plugin's for a run of the trial of the name, in the system's temporary
    folder as dev/architecture.md's Where a plugin writes its files has it, outside any ccpm clone,
    so the conversations started in it load none of its instructions; its path is printed first,
    for whoever runs the trial to find what the run writes there. The path is given with every link
    in it followed, as Claude Code names the folder of a conversation's records by it, and macOS's
    temporary folder is reached through a link."""
    made = os.path.realpath(testing.temporary(plugin, name))
    print("folder:", made, flush=True)
    return made


def claude(
    prompt: str,
    plugins: list[str],
    cwd: str | None = None,
    wait: int = 0,
    record: str | None = None,
    env: dict[str, str] | None = None,
    resume: str | None = None,
) -> dict[str, Any]:
    """Runs Claude Code on prompt with the copies of plugins in place of the installed ones, as
    their user runs it, and gives the run's result, the last line it printed as stream-json, such
    as its session_id; wait is the minutes it waits for an agent started in the background, which
    Claude Code stops waiting for after 10 by default. Given record, it writes there each line
    Claude Code printed, kept before a failed run stops the trial; env is
    set over the environment Claude Code runs in. Given resume, a session ID, the prompt goes on
    that conversation, as the user types it where they read the reply before; without it, in a
    fresh one."""
    run_env = {**os.environ, **(env or {})}
    if wait:
        run_env["CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS"] = str(wait * 60 * 1000)
    names = []
    for plugin in plugins:
        with open(os.path.join(plugin, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
            names.append(json.load(f)["name"])
    command = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose"]
    if resume:
        command += ["--resume", resume]
    for plugin in plugins:
        command += ["--plugin-dir", plugin]
    # The copy stands in for the installed plugin, which would otherwise run beside it.
    installed = {f"{name}@ccpm": False for name in names}
    command += ["--model", "opus", "--settings", json.dumps({"enabledPlugins": installed})]
    command += ["--permission-mode", "bypassPermissions"]
    done = subprocess.run(
        command, cwd=cwd, env=run_env, capture_output=True, text=True, check=False
    )
    if record:
        with open(record, "w", encoding="utf-8") as f:
            f.write(done.stdout)
    if done.returncode:
        raise SystemExit(f"claude exited {done.returncode}: {done.stderr}")
    printed = done.stdout.strip().splitlines()
    if not printed:
        raise SystemExit(f"claude printed nothing: {done.stderr}")
    return json.loads(printed[-1])


def agents(session: str) -> list[str]:
    """The path of the record of each agent the session started."""
    return glob.glob(record.subagent(record.conversation(session), "*"))


def show(path: str) -> None:
    """Prints a record's path and, of what it holds, each message sent, each tool used and each
    hook stop."""
    print("record:", path)
    for entry in record.read(path) or []:
        # Claude Code's copy of each request says again what the agent did.
        if entry.get("type") == "api-request-blob":
            continue
        if isinstance(entry.get("origin"), dict):
            print("  message:", entry["origin"].get("body"))
        if record.told(entry):
            print("  stop:", record.text(entry))
        for part in record.blocks(entry):
            if part.get("type") == "tool_use":
                print("  use:", part["name"], json.dumps(part["input"], ensure_ascii=False))
            elif part.get("type") == "tool_result" and part.get("is_error"):
                print("  stop:", part.get("content"))
