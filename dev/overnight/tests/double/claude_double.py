"""The double of `claude` that overnight's unit cases run in its place. It gives each run from one
line of a record in recorded/: claude 2.1.332's runs of `claude -p --output-format json`, and, of
anthropics/claude-code#79500, a rate limit that exits 0, as the plugin guide's Each result of a
double from a record says.

It serves the cases as a program named `claude` on the PATH, which `put_on_path` makes in a folder,
for a case that runs the `overnight` command whole. It gives the runs the case names, one for each
call, in order, and keeps each call it was asked."""

# TODO: the double as a host that overnight's code calls in the test's own process, giving each
# event's run as the code's own type, once the code names how it runs `claude`.

from __future__ import annotations

import functools
import json
import os
import sys
from typing import Any, NamedTuple

HERE = os.path.dirname(os.path.abspath(__file__))
RECORDED = os.path.join(HERE, "recorded")
RECORDS = ("claude-2.1.332.jsonl", "claude-manual.jsonl")
DONE = "a run that is done"
RESUMED = "a resumed run that is done"
REFUSED = "a run that the API refuses"
NO_CONVERSATION = "a resume that finds no conversation"
RATE_LIMIT = "a run that the rate limit stops, exiting 0"
KILLED = "a run that is killed"
# The variable that names the folder of the program's runs and calls, for the program on the PATH.
FOLDER = "OVERNIGHT_CLAUDE_DOUBLE"
RUNS = "runs.json"
ASKED = "asked.jsonl"


class Gave(NamedTuple):
    """What a run of `claude` gave: its exit code, its stdout, and its stderr."""

    code: int
    out: str
    err: str


@functools.cache
def _lines() -> dict[str, dict[str, Any]]:
    lines: dict[str, dict[str, Any]] = {}
    for record in RECORDS:
        with open(os.path.join(RECORDED, record), encoding="utf-8") as f:
            for each in f:
                line = json.loads(each)
                lines[line["event"]] = line
    return lines


def given(event: str) -> Gave:
    """What the record of the event gave."""
    line = _lines()[event]
    return Gave(line["exit"], line["stdout"], line["stderr"])


def session_of(event: str) -> str:
    """The session_id in what the record of the event printed."""
    return json.loads(given(event).out)["session_id"]


def result_of(event: str) -> str:
    """The result in what the record of the event printed."""
    return json.loads(given(event).out)["result"]


def put_on_path(folder: str, *events: str) -> dict[str, str]:
    """Makes a program named `claude` in the folder that gives the events' runs in order, and
    gives the variables that put it first on the PATH and name the folder of its runs."""
    with open(os.path.join(folder, RUNS), "w", encoding="utf-8") as f:
        json.dump(list(events), f)
    program = os.path.join(folder, "claude")
    with open(program, "w", encoding="utf-8") as f:
        f.write(f'#!/bin/sh\nexec "{sys.executable}" "{os.path.abspath(__file__)}" "$@"\n')
    os.chmod(program, 0o755)
    return {"PATH": folder + os.pathsep + os.environ["PATH"], FOLDER: folder}


def asked(folder: str) -> list[dict[str, Any]]:
    """Each call that the program on the PATH was asked: its `argv`, `cwd`, `stdin`, and the `sid`
    of the session that it ran in."""
    path = os.path.join(folder, ASKED)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(each) for each in f]


def _program(argv: list[str]) -> int:
    folder = os.environ[FOLDER]
    with open(os.path.join(folder, RUNS), encoding="utf-8") as f:
        runs = json.load(f)
    call = {"argv": argv, "cwd": os.getcwd(), "stdin": sys.stdin.read(), "sid": os.getsid(0)}
    with open(os.path.join(folder, ASKED), "a", encoding="utf-8") as f:
        f.write(json.dumps(call) + "\n")
    ran = given(runs[len(asked(folder)) - 1])
    sys.stdout.write(ran.out)
    sys.stderr.write(ran.err)
    return ran.code


if __name__ == "__main__":
    raise SystemExit(_program(["claude", *sys.argv[1:]]))
