"""Decides what resume takes and what it leaves behind, as Claude Code runs it when a turn ends at
the usage limit: from the StopFailure hook's input and the session's transcript, the session that
stopped, where it ran, and its permission mode; and from them, the waiter that resumes that very
session headless once the interval is over. Claude Code ignores what a StopFailure hook prints, so
each refusal is for whoever runs the hook by hand to try it."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from typing import NamedTuple

# The error by which Claude Code names a turn stopped at the usage limit, the one stop that waiting
# mends: each other error, such as a failed login, stops the resumed run the same way.
RATE_LIMIT = "rate_limit"
# The fields of the hook's input that name the session, its transcript, and the folder it ran in, as
# the hook's common input gives them.
FIELDS = ("session_id", "transcript_path", "cwd")
# The permission modes that `claude --permission-mode` accepts and the transcript records.
MODES = ("default", "plan", "acceptEdits", "auto", "dontAsk", "bypassPermissions")
# How long the waiter waits before each try. A limit lifts at a time that Claude Code shows only in
# a message whose wording it doesn't promise, so the waiter tries at a fixed interval: a try while
# the limit holds costs only a rejected request, and a quarter of an hour loses little of a night.
INTERVAL = 15 * 60
# The variable that sets the interval in seconds in place of INTERVAL, such as to try the hook
# within a minute. The waiter's run inherits it, so each later waiter keeps it too.
INTERVAL_VARIABLE = "OVERNIGHT_INTERVAL_SECONDS"
# What the resumed session is told, so that it takes the stopped work up where it stopped.
PROMPT = (
    "Your last turn stopped at the usage limit, which has now lifted. Go on with the work from"
    " where it stopped, and carry it on to its end."
)


class Wrong(Exception):
    """An input that resume refuses, said so that whoever ran the hook can mend it."""


class Stop(NamedTuple):
    """The session that stopped at the usage limit: its ID, the folder it ran in, and its
    permission mode."""

    session: str
    cwd: str
    mode: str


def main(
    stdin: bytes,
    environ: Mapping[str, str],
    claude: str | None,
    waiter: list[str],
    leave: Callable[[list[str], str], None],
) -> tuple[int, str]:
    """The exit code and stderr of resume on the hook's input, with `claude` the path of the
    `claude` command or None where it isn't found, `waiter` the command that starts wait.py, and
    `leave` what starts a command in a folder and outlives the hook.

    0 with nothing said, once it left the waiter: `waiter` with the interval and
    `claude -p --resume <session_id> --permission-mode <mode> <PROMPT>`, started in the input's
    `cwd`, the mode being the last `permissionMode` that the transcript records. The interval is
    INTERVAL seconds, or the whole number of seconds that INTERVAL_VARIABLE holds.

    0 with nothing said, leaving nothing, where the input's `error` isn't `rate_limit`.

    1 with `resume: <what's wrong>`, leaving nothing, where the input isn't a JSON object with
    `session_id`, `transcript_path`, and `cwd` as strings, the transcript can't be read or records
    no permission mode that MODES holds, INTERVAL_VARIABLE holds no whole number from 1, or
    `claude` isn't found."""
    try:
        called = _read(stdin)
        if called.get("error") != RATE_LIMIT:
            return 0, ""
        stop = _stop(called)
        seconds = _interval(environ)
        if claude is None:
            raise Wrong("claude isn't on PATH, so no waiter can resume the session")
    except Wrong as wrong:
        return 1, f"resume: {wrong}\n"
    resumed = [claude, "-p", "--resume", stop.session, "--permission-mode", stop.mode, PROMPT]
    leave([*waiter, str(seconds), *resumed], stop.cwd)
    return 0, ""


def _read(stdin: bytes) -> dict:
    """The hook's input as a JSON object."""
    try:
        called = json.loads(stdin.decode("utf-8"))
    except ValueError as wrong:
        raise Wrong(f"the hook's input isn't JSON: {wrong}") from wrong
    if not isinstance(called, dict):
        raise Wrong("the hook's input must be a JSON object, as Claude Code gives a StopFailure")
    return called


def _stop(called: dict) -> Stop:
    """The session that the input names, with its permission mode from its transcript."""
    session, transcript, cwd = (_text(called, name) for name in FIELDS)
    return Stop(session, cwd, _mode(transcript))


def _text(called: dict, name: str) -> str:
    """The input's field of the name, which must be a string that isn't empty."""
    field = called.get(name)
    if not isinstance(field, str) or not field:
        raise Wrong(
            f"the hook's input must give {name} as a string, as Claude Code gives a StopFailure,"
            f" not {field!r}"
        )
    return field


def _mode(transcript: str) -> str:
    """The session's permission mode: the last `permissionMode` among the transcript's records.
    Claude Code writes the transcript as the session goes, so a line not yet whole is passed
    over."""
    mode = None
    try:
        with open(transcript, encoding="utf-8") as lines:
            for line in lines:
                if '"permissionMode"' not in line:
                    continue
                try:
                    record = json.loads(line)
                except ValueError:
                    continue
                if isinstance(record, dict) and "permissionMode" in record:
                    mode = record["permissionMode"]
    except OSError as wrong:
        raise Wrong(f"{transcript}: the session's transcript can't be read: {wrong}") from wrong
    if mode not in MODES:
        raise Wrong(
            f"{transcript}: the transcript records no permission mode of {', '.join(MODES)},"
            f" so the session can't be resumed in its own mode; the last it records is {mode!r}"
        )
    return mode


def _interval(environ: Mapping[str, str]) -> int:
    """The seconds the waiter waits: INTERVAL_VARIABLE's whole number, or INTERVAL."""
    given = environ.get(INTERVAL_VARIABLE)
    if given is None:
        return INTERVAL
    if not (given.isascii() and given.isdigit()) or int(given) < 1:
        raise Wrong(f"{INTERVAL_VARIABLE} must be a whole number of seconds from 1, not {given!r}")
    return int(given)
