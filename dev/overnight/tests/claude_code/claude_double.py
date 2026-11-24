"""The stand-in of Claude Code that overnight's cases run in its place, as overnight's Test strategy
says under Integration testing and Contract testing. It answers each run of `claude -p` that the
runner makes from one line of a record in recorded/: Claude Code 2.1.331's runs in its mode that
asks no one, `--permission-mode dontAsk`, with JSON output, of a run that ends with its last words,
one resumed in its conversation, one that refuses a call to a tool not allowed and ends, one that
ends by an error of its own, and one resumed in no conversation; and, of Claude Code's page of
errors, a run that the session limit, the weekly limit, or a usage limit with no reset time stops,
as the plugin guide's Each result of a double from a record says. No run spends the usage limit on
purpose, so the stops come from the page. A run that no record holds, such as one in another mode
or with text output, fails with exit 1, naming itself, so that a body that makes it shows the gap.

The case gives the stand-in its plays, each piece's runs in order, in a JSON file of the folder of
its state, keyed by the piece's number, which it reads from the folder it runs in,
`<repository>-overnight-<n>`, or by `*` for any other folder. A play names what the run gives, by
its kind, and may set the last words, the reset time that the stop gives, the time of the bench's
clock as the run ends, a file to commit as the piece's work, and a hold, under which the run waits
for the case to release it. Each run is kept in the folder's file of calls, as it starts."""

from __future__ import annotations

import copy
import functools
import json
import os
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime
from typing import Any

RECORDED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recorded")
RUN = "claude-2.1.331-print.jsonl"
MANUAL = "claude-manual.jsonl"
# The file of the plays in the folder of the stand-in's state, and the file of each run it made.
PLAYS = "claude-plays.json"
CALLS = "claude-calls.jsonl"
# The file whose being there releases every hold, as each case's end makes it.
RELEASE_ALL = "release-all"
# The tool call that the record of a refusal tried, and the rules that would allow it.
REFUSED_CALL = "Bash(touch made.txt)"
ALLOWING = ("Bash", "Bash(touch:*)", "Bash(touch made.txt)")
# The longest a hold waits for its release, so that a case that never releases it ends.
HOLD_LONGEST = 60.0
# The time that each stop of the page gives, which a play may set in its place.
SESSION_RESETS = "3:45pm"
WEEKLY_RESETS = "Mon 12:00am"
# A piece's folder, which names its number.
PIECE_FOLDER = re.compile(r".+-overnight-(\d+)")


@functools.cache
def _record(record: str) -> tuple[dict[str, Any], ...]:
    with open(os.path.join(RECORDED, record), encoding="utf-8") as f:
        return tuple(json.loads(each) for each in f)


def line(record: str, event: str) -> dict[str, Any]:
    """A copy of the line of the record in recorded/ that the event names."""
    return copy.deepcopy(next(each for each in _record(record) if each["event"] == event))


# What a run of each kind of play gives, first and resumed, each from one line of a record.
KINDS = {
    "ends": lambda: line(RUN, "a run ends with its last words"),
    "refuses": lambda: line(RUN, "a run refuses a call to a tool not allowed at once, and ends"),
    "errs": lambda: line(RUN, "a run ends by an error of its own"),
    "session limit": lambda: line(MANUAL, "the session limit stops a run, with the time it resets"),
    "weekly limit": lambda: line(
        MANUAL, "the weekly limit stops a run, with the day and time it resets"
    ),
    "limit with no time": lambda: line(MANUAL, "a usage limit stops a run, with no time it resets"),
}
RESUMED = {"ends": lambda: line(RUN, "a run resumed goes on in its conversation and ends")}


def no_conversation() -> dict[str, Any]:
    """What a run resumed in a conversation that isn't there gives."""
    return line(RUN, "a run resumed in no conversation fails")


def conversation(folder: str) -> str:
    """The ID of the conversation of the runs in the folder, one for each folder."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, os.path.realpath(folder)))


def plays(state: str, given: dict[str, list[dict[str, Any]]], clock: str | None = None) -> None:
    """Gives the stand-in its plays, by each piece's number or `*`, and the file of the bench's
    clock that a play's `at` sets, where there is one."""
    os.makedirs(state, exist_ok=True)
    with open(os.path.join(state, PLAYS), "w", encoding="utf-8") as f:
        json.dump({"plays": given, "clock": clock}, f)


def calls(state: str) -> list[dict[str, Any]]:
    """Each run that the stand-in made, in the order it started."""
    path = os.path.join(state, CALLS)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(each) for each in f if each.strip()]


def release(state: str, hold: str) -> None:
    """Releases the runs held by the name."""
    with open(os.path.join(state, f"release-{hold}"), "w", encoding="utf-8"):
        pass


def _split(rules: str) -> list[str]:
    """Each permission rule of the words, apart at each comma or space outside parentheses."""
    found, word, depth = [], "", 0
    for char in rules:
        depth += {"(": 1, ")": -1}.get(char, 0)
        if char in ", " and depth == 0:
            found, word = found + [word] if word else found, ""
        else:
            word += char
    return found + [word] if word else found


def options(argv: list[str]) -> dict[str, Any]:
    """What the run's arguments ask: print mode, the output's form, the permission mode, each tool
    allowed, and the conversation to resume, None where they don't name one."""
    asked: dict[str, Any] = {"print": False, "output": None, "mode": None, "tools": None}
    asked["resume"] = None
    at = 0
    while at < len(argv):
        each = argv[at]
        if each in ("-p", "--print"):
            asked["print"] = True
        elif each in ("--allowedTools", "--allowed-tools"):
            values = []
            while at + 1 < len(argv) and not argv[at + 1].startswith("-"):
                at += 1
                values += _split(argv[at])
            asked["tools"] = values
        elif each in ("--output-format", "--permission-mode", "--resume", "-r"):
            at += 1
            key = {"--output-format": "output", "--permission-mode": "mode"}.get(each, "resume")
            asked[key] = argv[at] if at < len(argv) else None
        at += 1
    return asked


def _plays_of(state: str, cwd: str) -> tuple[list[dict[str, Any]], str | None]:
    """The plays of the piece whose folder it is, and the file of the bench's clock."""
    with open(os.path.join(state, PLAYS), encoding="utf-8") as f:
        given = json.load(f)
    named = PIECE_FOLDER.fullmatch(os.path.basename(os.path.realpath(cwd)))
    key = named.group(1) if named and named.group(1) in given["plays"] else "*"
    return given["plays"].get(key, []), given["clock"]


def _keep(state: str, call: dict[str, Any]) -> None:
    """Adds the run to the file of calls, in one write, as several runners run at once."""
    text = json.dumps(call, ensure_ascii=False) + "\n"
    descriptor = os.open(os.path.join(state, CALLS), os.O_WRONLY | os.O_APPEND | os.O_CREAT)
    try:
        os.write(descriptor, text.encode("utf-8"))
    finally:
        os.close(descriptor)


def _hold(state: str, hold: str) -> None:
    """Waits until the case releases the hold, or every hold."""
    end = time.monotonic() + HOLD_LONGEST
    names = (f"release-{hold}", RELEASE_ALL)
    while not any(os.path.exists(os.path.join(state, name)) for name in names):
        if time.monotonic() > end:
            return
        time.sleep(0.05)


def _set_clock(clock: str | None, at: str | None) -> None:
    """Sets the bench's clock to the time, in the local zone, where the play gives one."""
    if not (clock and at):
        return
    kept = os.path.join(os.path.dirname(clock), f".{os.getpid()}.clock")
    with open(kept, "w", encoding="utf-8") as f:
        json.dump({"now": datetime.fromisoformat(at).astimezone().isoformat()}, f)
    os.replace(kept, clock)


def _commit(cwd: str, name: str) -> None:
    """Commits a file of the name in the folder, as the piece's work."""
    with open(os.path.join(cwd, name), "w", encoding="utf-8") as f:
        f.write("fixed\n")
    for args in (["add", name], ["commit", "-q", "-m", f"Fix by {name}"]):
        subprocess.run(["git", "-C", cwd, *args], check=True, capture_output=True)


def _unrecorded(why: str) -> tuple[int, str, str]:
    return 1, "", f"the stand-in of Claude Code holds no record of {why}\n"


def _given(play: dict[str, Any], asked: dict[str, Any], cwd: str) -> dict[str, Any]:
    """The line that the run gives, with the folder's conversation, the play's last words, and
    the play's reset time."""
    kind = play["kind"]
    if asked["resume"] is not None and asked["resume"] != conversation(cwd):
        given = no_conversation()
        given["stderr"] = given["stderr"].replace(
            "00000000-0000-0000-0000-000000000000", asked["resume"]
        )
        return given
    resumed = asked["resume"] is not None and kind in RESUMED
    given = (RESUMED if resumed else KINDS)[kind]()
    reply = json.loads(given["stdout"])
    reply["session_id"] = conversation(cwd)
    if "last_words" in play:
        reply["result"] = play["last_words"]
    if "resets" in play:
        stops = (SESSION_RESETS, WEEKLY_RESETS)
        for each in stops:
            reply["result"] = reply["result"].replace(each, play["resets"])
    given["stdout"] = json.dumps(reply, separators=(",", ":"), ensure_ascii=False) + "\n"
    return given


def answer(argv: list[str], stdin: str, cwd: str, state: str) -> tuple[int, str, str]:
    """What the stand-in gives for the run of Claude Code: its exit code, stdout, and stderr."""
    asked = options(argv)
    played, clock = _plays_of(state, cwd)
    made = [each for each in calls(state) if each["cwd"] == os.path.realpath(cwd)]
    call = {
        "argv": argv,
        "cwd": os.path.realpath(cwd),
        "stdin": stdin,
        "pid": os.getpid(),
        "ppid": os.getppid(),
        **asked,
    }
    _keep(state, call)
    if not (asked["print"] and asked["output"] == "json" and asked["mode"] == "dontAsk"):
        return _unrecorded(f"a run of {' '.join(argv)!r}: each record is of `-p` in dontAsk mode")
    if len(made) >= len(played):
        return _unrecorded(f"run {len(made) + 1} in {cwd}, as its case gives {len(played)} plays")
    play = played[len(made)]
    if "hold" in play:
        _hold(state, play["hold"])
    if play["kind"] == "refuses" and set(asked["tools"] or ()) & set(ALLOWING):
        return _unrecorded(f"{REFUSED_CALL} run with it allowed")
    if "commit" in play:
        _commit(cwd, play["commit"])
    given = _given(play, asked, cwd)
    _set_clock(clock, play.get("at"))
    return given["exit"], given["stdout"], given["stderr"]


def program(bin_folder: str, state: str) -> str:
    """Writes `claude` into the bin folder, a program that answers as `answer` does with its state
    in the state folder, and gives the bin folder."""
    os.makedirs(bin_folder, exist_ok=True)
    os.makedirs(state, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    script = os.path.join(bin_folder, "claude_stand_in.py")
    with open(script, "w", encoding="utf-8") as f:
        f.write(
            "import os\n"
            "import sys\n"
            f"sys.path.insert(0, {here!r})\n"
            "import claude_double\n"
            "stdin = sys.stdin.read()\n"
            f"given = claude_double.answer(sys.argv[1:], stdin, os.getcwd(), {state!r})\n"
            "code, out, err = given\n"
            "sys.stdout.write(out)\n"
            "sys.stderr.write(err)\n"
            "sys.exit(code)\n"
        )
    if os.name == "nt":
        with open(os.path.join(bin_folder, "claude.cmd"), "w", encoding="utf-8") as f:
            f.write(f'@"{sys.executable}" "{script}" %*\n')
    else:
        path = os.path.join(bin_folder, "claude")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f'#!/bin/sh\nexec "{sys.executable}" "{script}" "$@"\n')
        os.chmod(path, 0o755)
    return bin_folder
