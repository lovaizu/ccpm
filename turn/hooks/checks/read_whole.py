"""Each role reads whole every input of its step before it answers, and the work again after it
last changed, and the learner is shown every page of every record, so that no item is judged on a
part read and the rest guessed."""

from __future__ import annotations

import json
import os
import re
import shlex
from typing import Any

import agents
import records
import run

READERS = ("generator", "first-user", "evaluator", "learner")
STATEMENT = re.compile(r"&&|\|\||;|\n")
# How Claude Code records a message from another agent: from an agent, or from the conversation
# that started it.
MESSAGED = ("peer", "coordinator")
PAGE = re.compile(r"""turn\.py["']?\s+record\s+\S+\s+(\d+)\s+(\d+)""")


def check(event: dict[str, Any]) -> list[str]:
    role = agents.role(event)
    if not (answering(event, role) or recording(event, role)):
        return []
    kept = agents.running(event)
    if kept is None:
        return []
    return HOLDS[str(role)](event, kept)


def answering(event: dict[str, Any], role: str | None) -> bool:
    """Whether a role is ending with its reply."""
    return event["hook_event_name"] == "SubagentStop" and role in READERS


def orchestrator(event: dict[str, Any], kept: dict[str, Any]) -> list[str]:
    """The orchestrator's check rests on what the work is made from, its decision on the items to
    decide and the work, and its reading on what the run was given; going on after a role rests on
    nothing read."""
    if "check" in kept:
        # The check comes before the work is made, so it rests on what the work is made from.
        return unread(
            event, kept, [p for p in files(event, kept["given"]) if p not in kept["work"]]
        )
    if "decide" in kept:
        # The items to decide are what turn.py printed last, seen whole only when not piped or sent
        # to a file.
        said = []
        if not printed(agents.transcript(event)):
            said.append(
                "see the items to decide whole: run `turn.py next <the call's result>` again with"
                " no pipe or redirect, since an item decided without where the first user stopped"
                " is decided on a guess"
            )
        return said + unread(event, kept, kept["work"])
    if "hold" in kept:
        if printed(agents.transcript(event)):
            return []
        said = (
            "see the items to hold whole: run `turn.py next <the call's result>` again with no"
            " pipe or redirect, since an item held unseen is held on a guess"
        )
        return [said]
    if "take" in kept:
        if printed(agents.transcript(event)):
            return []
        said = (
            "see what the learner found whole: run `turn.py next <the call's result>` again with"
            " no pipe or redirect, since a lesson taken unseen is taken on a guess"
        )
        return [said]
    if kept["next"]["agent"] != run.GENERATOR:
        return []
    return unread(event, kept, files(event, kept["given"]))


def generator(event: dict[str, Any], kept: dict[str, Any]) -> list[str]:
    return unread(event, kept, files(event, kept["given"]))


def reader(event: dict[str, Any], kept: dict[str, Any]) -> list[str]:
    """The first user and the evaluator read the work and what the receiver has with it."""
    return unread(event, kept, kept["work"] + kept["checklist"] + kept["opens"])


def learner(event: dict[str, Any], kept: dict[str, Any]) -> list[str]:
    return unshown(agents.transcript(event), kept)


HOLDS = {
    "up": orchestrator,
    "generator": generator,
    "first-user": reader,
    "evaluator": reader,
    "learner": learner,
}


def files(event: dict[str, Any], paths: list[str]) -> list[str]:
    """The paths that are files, not folders."""
    return [p for p in paths if os.path.isfile(os.path.join(event["cwd"], p))]


def unread(event: dict[str, Any], kept: dict[str, Any], must: list[str]) -> list[str]:
    """What is to be read whole and was not."""
    cwd = os.path.realpath(event["cwd"])
    read = whole(agents.transcript(event), cwd, kept["work"])
    missing = [p for p in must if os.path.realpath(os.path.join(cwd, p)) not in read]
    if not missing:
        return []
    unread = ", ".join(missing)
    said = (
        f"read whole, each with `cat -n` or with Read and no offset or limit: {unread}; what"
        " is left unread is judged on a guess, and the work is read again after it changed"
    )
    return [said]


def unshown(path: str, kept: dict[str, Any]) -> list[str]:
    """Each page of each record the learner was not shown whole by turn's script."""
    seen: set[tuple[int, int]] = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            content = json.loads(line).get("message", {}).get("content")
            for part in content if isinstance(content, list) else []:
                command = str(part.get("input", {}).get("command", ""))
                if not {"|", ">"} & set(command):
                    seen.update((int(n), int(p)) for n, p in PAGE.findall(command))
    result = kept["call"]["result"]
    missing = [
        f"turn.py record {result} {n} {p}"
        for n, record in enumerate(run.learnt_from(kept), 1)
        for p in range(1, len(records.pages(record)) + 1)
        if (n, p) not in seen
    ]
    if not missing:
        return []
    return [
        "be shown every page of every record, each in a command of its own with no pipe or"
        " redirect: " + ", ".join(missing) + "; a record left unread is learnt from on a guess"
    ]


def recording(event: dict[str, Any], role: str | None) -> bool:
    """Whether the orchestrator is recording its check, reading or decision with the script."""
    command = str(event.get("tool_input", {}).get("command", ""))
    return (
        (role, event["hook_event_name"], event.get("tool_name")) == ("up", "PreToolUse", "Bash")
        and agents.runs(command, "next")
        and "<<" in command
    )


def whole(path: str, cwd: str, work: list[str]) -> set[str]:
    """Each file the agent's record shows read from top to end since it last changed: by this
    agent writing it, or, for the work, by the generator the agent started or sent a message, or
    by the generator before a message the agent was sent."""
    read: set[str] = set()
    seen: set[str] = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            origin = record.get("origin")
            if isinstance(origin, dict) and origin.get("kind") in MESSAGED:
                read.difference_update(at(cwd, w) for w in work)
            shown = shown_whole(record.get("attachment"), cwd)
            if shown:
                read.add(shown)
            content = record.get("message", {}).get("content")
            for part in content if isinstance(content, list) else []:
                # A tool used is kept twice under one ID; other parts have none.
                if "id" not in part or part["id"] in seen:
                    continue
                seen.add(part["id"])
                USES.get(part.get("name"), lambda *_: None)(read, part["input"], cwd, work)
    return read


def reads(read: set[str], given: dict[str, Any], cwd: str, work: list[str]) -> None:
    if "offset" not in given and "limit" not in given:
        read.add(at(cwd, given.get("file_path", "")))


def runs(read: set[str], given: dict[str, Any], cwd: str, work: list[str]) -> None:
    read.update(at(cwd, p) for p in catted(str(given.get("command", ""))))


def changes(read: set[str], given: dict[str, Any], cwd: str, work: list[str]) -> None:
    read.discard(at(cwd, given.get("file_path", "")))


def starts(read: set[str], given: dict[str, Any], cwd: str, work: list[str]) -> None:
    """The generator started may change the work."""
    if given.get("subagent_type") == run.GENERATOR:
        read.difference_update(at(cwd, w) for w in work)


def sends(read: set[str], given: dict[str, Any], cwd: str, work: list[str]) -> None:
    """A role sent a message may be the generator, which changes the work."""
    read.difference_update(at(cwd, w) for w in work)


USES = {
    "Read": reads,
    "Bash": runs,
    "Write": changes,
    "Edit": changes,
    "Agent": starts,
    "SendMessage": sends,
}


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
                if agents.runs(command, "next") and "<<" not in command:
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
        head, *rest = words or [""]
        if head == "cat" and not {"|", ">", ">>"} & set(rest) and "|" not in statement:
            files += [w for w in rest if not w.startswith("-")]
    return files


def at(cwd: str, path: str) -> str:
    return os.path.realpath(os.path.join(cwd, path))
