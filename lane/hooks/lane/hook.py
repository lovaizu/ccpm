"""What each entry of a plugin's hooks runs: every check of its event on the event Claude Code hands
it, in one subagent alone, a use stopped or the subagent kept going with what they say."""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from typing import IO, Any

# Claude Code stops the tool's use, or keeps the agent going, on this exit, showing the AI what was
# written to stderr; on any other exit but 0 it goes on, showing stderr to the user.
STOPPED = 2
UNREAD = 1
# The fields each event of these hooks holds beside hook_event_name and cwd, and the types of each:
# at SubagentStop the agent's last reply, which Claude Code gives as null after the agent hands its
# reply back with SubagentHandback; as a call comes back, its ID, and of a failed one its error.
CALLED = {"tool_name": (str,), "tool_input": (dict,)}
FIELDS = {
    "PreToolUse": CALLED,
    "SubagentStop": {"last_assistant_message": (str, type(None))},
    "PostToolUse": {**CALLED, "tool_use_id": (str,)},
    "PostToolUseFailure": {**CALLED, "tool_use_id": (str,), "error": (str,)},
}


def event_read(stream: IO[str]) -> dict[str, Any] | None:
    """The event on the stream, when it is a JSON object holding the hook's event name, the folder
    it comes from and its event's fields, as Claude Code hands it; None otherwise."""
    try:
        event = json.load(stream)
    except ValueError:
        return None
    if not isinstance(event, dict) or not isinstance(event.get("hook_event_name"), str):
        return None
    fields = FIELDS.get(event["hook_event_name"], {})
    shaped = all(isinstance(event.get(k), kind) for k, kind in fields.items())
    folder = event.get("cwd")
    return event if shaped and isinstance(folder, str) and os.path.isdir(folder) else None


def run(plugin: str, checks: Sequence[Any], stream: IO[str], err: IO[str], agent: str) -> int:
    """Runs each check on the event in the stream, from the folder the event comes from, where the
    event's agent_type is the agent, such as `notes:changelog-writer`; gives STOPPED with what they
    say on err, headed by the plugin's name, where any says something, and 0 where none does or the
    event is another agent's, as a tool event's matcher tells tools apart, not agents; UNREAD where
    the stream holds no event as Claude Code hands it, which lets it through unchecked."""
    event = event_read(stream)
    if event is None:
        each = ", ".join(f"for {e} {' and '.join(f)}" for e, f in FIELDS.items())
        err.write(
            f"{plugin}: the hook was handed no event as Claude Code hands it, a JSON object with"
            f" hook_event_name and cwd, and {each}, so it lets this through unchecked; update"
            " Claude Code with `claude update`, and where it goes on, report it at"
            " https://github.com/lovaizu/ccpm/issues\n"
        )
        return UNREAD
    if event.get("agent_type") != agent:
        return 0
    os.chdir(event["cwd"])
    said = [s for c in checks for s in c.check(event)]
    if said:
        err.write("".join(f"{plugin}: {s}\n" for s in said))
        return STOPPED
    return 0
