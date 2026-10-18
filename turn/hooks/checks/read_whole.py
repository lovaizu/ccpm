"""Each role reads whole what its step has it read before it answers, and the work again after it
last changed, so that no item is judged on a part read and the rest guessed."""

from __future__ import annotations

import json
import os
import re
import shlex
from typing import Any

import agents
import run

# The learner reads records too long for one read, and takes what it needs from them by script.
READERS = ("generator", "first-user", "evaluator")
STATEMENT = re.compile(r"&&|\|\||;|\n")


def check(event: dict[str, Any]) -> list[str]:
    role = agents.role(event)
    answering = event["hook_event_name"] == "SubagentStop" and role in READERS
    if not (answering or recording(event, role)):
        return []
    kept = agents.running(event)
    if kept is None:
        return []
    checking = role == "up" and "check" in kept
    deciding = role == "up" and "decide" in kept
    if role == "up" and not (checking or deciding) and kept["next"]["agent"] != run.GENERATOR:
        return []
    cwd = os.path.realpath(event["cwd"])
    if role in ("first-user", "evaluator") or deciding:
        must = kept["work"] + ([] if deciding else kept["checklist"])
    else:
        # The check comes before the work is made, so it rests on what the work is made from.
        must = [
            p
            for p in kept["given"]
            if os.path.isfile(os.path.join(cwd, p)) and not (checking and p in kept["work"])
        ]
    read = whole(agents.transcript(event), cwd, kept["work"])
    missing = [p for p in must if os.path.realpath(os.path.join(cwd, p)) not in read]
    said = []
    # The items to decide are what turn.py printed last, seen whole only when not piped or sent to
    # a file.
    if deciding and not printed(agents.transcript(event)):
        said.append(
            "see the items to decide whole: run `turn.py next <the call's result>` again with no"
            " pipe or redirect, since an item decided without where the first user stopped is"
            " decided on a guess"
        )
    if missing:
        unread = ", ".join(missing)
        said.append(
            f"read whole, each with `cat -n` or with Read and no offset or limit: {unread}; what"
            " is left unread is judged on a guess, and the work is read again after it changed"
        )
    return said


def recording(event: dict[str, Any], role: str | None) -> bool:
    """Whether the orchestrator is recording its check, reading or decision with the script."""
    command = str(event.get("tool_input", {}).get("command", ""))
    return (
        role == "up"
        and event["hook_event_name"] == "PreToolUse"
        and event["tool_name"] == "Bash"
        and agents.runs(command, "next")
        and "<<" in command
    )


def whole(path: str, cwd: str, work: list[str]) -> set[str]:
    """Each file the agent's record shows read from top to end since it last changed: by this
    agent writing it, or, for the work, by the generator the agent started."""
    read: set[str] = set()
    seen: set[str] = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            shown = shown_whole(record.get("attachment"), cwd)
            if shown:
                read.add(shown)
            content = record.get("message", {}).get("content")
            for part in content if isinstance(content, list) else []:
                if part.get("type") != "tool_use" or part["id"] in seen:
                    continue
                seen.add(part["id"])
                name, given = part["name"], part["input"]
                if name == "Read" and "offset" not in given and "limit" not in given:
                    read.add(at(cwd, given.get("file_path", "")))
                elif name == "Bash":
                    read.update(at(cwd, p) for p in catted(str(given.get("command", ""))))
                elif name in ("Write", "Edit"):
                    read.discard(at(cwd, given.get("file_path", "")))
                elif name == "Agent" and given.get("subagent_type") == run.GENERATOR:
                    read.difference_update(at(cwd, w) for w in work)
    return read


def shown_whole(attachment: Any, cwd: str) -> str | None:
    """The file Claude Code put whole into the agent's context after another agent changed it, its
    lines numbered from the first to the last, or None."""
    if not isinstance(attachment, dict) or attachment.get("type") != "edited_text_file":
        return None
    path = at(cwd, str(attachment.get("filename", "")))
    try:
        with open(path, encoding="utf-8") as f:
            count = len(f.read().splitlines())
    except OSError:
        return None
    numbers = [n.partition("\t")[0] for n in str(attachment.get("snippet", "")).splitlines()]
    return path if numbers == [str(n) for n in range(1, count + 1)] else None


def printed(path: str) -> bool:
    """Whether the last `turn.py next` the agent ran without input showed its output whole."""
    shown = False
    with open(path, encoding="utf-8") as f:
        for line in f:
            content = json.loads(line).get("message", {}).get("content")
            for part in content if isinstance(content, list) else []:
                command = str(part.get("input", {}).get("command", ""))
                if (
                    part.get("type") == "tool_use"
                    and agents.runs(command, "next")
                    and "<<" not in command
                ):
                    shown = not {"|", ">"} & set(command)
    return shown


def catted(command: str) -> list[str]:
    """The files a command prints whole with cat, in a statement not piped or redirected."""
    files: list[str] = []
    for statement in STATEMENT.split(command):
        try:
            words = shlex.split(statement)
        except ValueError:
            continue
        if words[:1] == ["cat"] and not {"|", ">", ">>"} & set(words) and "|" not in statement:
            files += [w for w in words[1:] if not w.startswith("-")]
    return files


def at(cwd: str, path: str) -> str:
    return os.path.realpath(os.path.join(cwd, path))
