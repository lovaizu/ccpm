"""PreToolUse entry of rn's hooks: Claude Code runs it as a tool is about to be used, and it runs
each of rn's checks on that tool call, stopping the call with what they say.

    Claude Code --the event, JSON on stdin--> pretooluse.py --the event--> each check
    each check --what to say, or nothing--> pretooluse.py
    pretooluse.py --exit 2, `rn: ` and what was said on stderr--> Claude Code, which stops the call
                                                                  and shows it to the AI that made it

The checks are rn's guards: each stops a move of rn's conductor, the AI running rn's commands in the
user's conversation, that breaks one of rn's rules, saying what to do instead and why. hooks.json
runs this with rn's scripts on PYTHONPATH, as the checks find the session through rn.py.
"""

from __future__ import annotations

import json
import os
import sys
from typing import IO, Any

from checks import default_branch

CHECKS = (default_branch,)
# Claude Code stops the tool call on exit 2, showing stderr to the AI; on any other code other than
# 0 the call goes on, and stderr is shown to the user.
STOPPED = 2
UNREAD = 1


def event_read(stream: IO[str]) -> dict[str, Any] | None:
    """The PreToolUse event on the stream, when it is a JSON object holding the folder the call runs
    in, the tool's name and the tool's input, as Claude Code hands it; None otherwise."""
    try:
        event = json.load(stream)
    except ValueError:
        return None
    if not isinstance(event, dict):
        return None
    shaped = isinstance(event.get("tool_name"), str) and isinstance(event.get("tool_input"), dict)
    folder = event.get("cwd")
    return event if shaped and isinstance(folder, str) and os.path.isdir(folder) else None


def main(stream: IO[str], err: IO[str]) -> int:
    """Runs each check on the event on the stream from the folder the call runs in; 2 with what the
    checks say on err where any says something, 0 where none does, and 1 where the stream holds no
    event as Claude Code hands it, which lets the call go on unchecked."""
    event = event_read(stream)
    if event is None:
        err.write(
            "rn: the PreToolUse hook was handed no event as Claude Code hands it, a JSON object"
            " with cwd, tool_name and tool_input, so this tool call goes on unchecked; update"
            " Claude Code with `claude update`, and where it goes on, report it at"
            " https://github.com/lovaizu/ccpm/issues\n"
        )
        return UNREAD
    os.chdir(event["cwd"])
    said = [s for check in CHECKS for s in check.check(event)]
    if said:
        err.write("rn: " + "\n".join(said) + "\n")
        return STOPPED
    return 0


# Run as the hook, and not when the tests import it under the name pretooluse. It is written as
# membership rather than `==`, since an order comparison such as `<=` would also tell "__main__"
# from "pretooluse", and a mutant making it one would pass every test.
if __name__ in ("__main__",):
    sys.exit(main(sys.stdin, sys.stderr))
