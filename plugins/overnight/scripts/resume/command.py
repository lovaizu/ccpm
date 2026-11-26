"""Decides what resume takes and what it leaves behind, as Claude Code runs it when a turn ends at
the usage limit: from the StopFailure hook's input and the session's transcript, the session that
stopped, where it ran, and its permission mode; and from them, the waiter that resumes that very
session headless once the interval is over. Claude Code ignores what a StopFailure hook prints, so
each refusal is for whoever runs the hook by hand to try it."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping

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
    `cwd`, the mode being the last `permissionMode` that the transcript records at the top of a
    whole line. The interval is INTERVAL seconds, or the whole number of seconds that
    INTERVAL_VARIABLE holds.

    0 with nothing said, leaving nothing, where the input's `error` isn't `rate_limit`.

    1 with `resume: <what's wrong>`, leaving nothing, where the input isn't a JSON object with
    `session_id`, `transcript_path`, and `cwd` as strings, the transcript can't be read or records
    no permission mode that MODES holds, INTERVAL_VARIABLE holds no whole number from 1, or
    `claude` isn't found."""
    try:
        hook_input = _read(stdin)
        if hook_input.get("error") != RATE_LIMIT:
            return 0, ""
        session_id, transcript, cwd = (_text(hook_input, name) for name in FIELDS)
        mode = _mode(transcript)
        seconds = _interval(environ)
        if claude is None:
            raise Wrong("claude isn't on PATH, so no waiter can resume the session")
    except Wrong as wrong:
        return 1, f"resume: {wrong}\n"
    resumed = [claude, "-p", "--resume", session_id, "--permission-mode", mode, PROMPT]
    leave([*waiter, str(seconds), *resumed], cwd)
    return 0, ""


def _read(stdin: bytes) -> dict:
    """The hook's input as a JSON object."""
    try:
        hook_input = json.loads(stdin.decode("utf-8"))
    except ValueError as wrong:
        raise Wrong(f"the hook's input isn't JSON: {wrong}") from wrong
    if not isinstance(hook_input, dict):
        raise Wrong("the hook's input must be a JSON object, as Claude Code gives a StopFailure")
    return hook_input


def _text(hook_input: dict, name: str) -> str:
    """The input's field of the name, which must be a string."""
    field = hook_input.get(name)
    if not isinstance(field, str):
        raise Wrong(
            f"the hook's input must give {name} as a string, as Claude Code gives a StopFailure,"
            f" not {field!r}"
        )
    return field


def _mode(transcript: str) -> str:
    """The session's permission mode: the last `permissionMode` at the top of a record of the
    transcript. Claude Code writes the transcript as the session goes, so a line not yet whole is
    passed over, and so is a record that names `permissionMode` only within it, such as the output
    of a command that read another transcript."""
    mode = None
    try:
        with open(transcript, encoding="utf-8") as lines:
            for line in lines:
                try:
                    record = json.loads(line)
                except ValueError:
                    continue
                if "permissionMode" in record:
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
    # isdigit alone takes digits such as "²" that int refuses.
    if not (given.isascii() and given.isdigit()) or int(given) < 1:
        raise Wrong(f"{INTERVAL_VARIABLE} must be a whole number of seconds from 1, not {given!r}")
    return int(given)
