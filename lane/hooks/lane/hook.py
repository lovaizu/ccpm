"""What each entry of a plugin's hooks runs: every check of its event on the event Claude Code hands
it, a use stopped or an agent kept going with what they say; for a hook acting in one subagent
alone, such as a lane's, on that subagent's events alone."""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from typing import IO, Any

# Claude Code stops the tool's use, or keeps the agent going, on this exit, showing the AI what was
# written to stderr; on any other exit but 0 it goes on, showing stderr to the user.
STOPPED = 2
UNREAD = 1
# The fields each event of these hooks holds beside hook_event_name and cwd, and the type of each.
FIELDS = {"PreToolUse": {"tool_name": str, "tool_input": dict}}


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


def run(
    plugin: str, checks: Sequence[Any], stream: IO[str], err: IO[str], agent: str | None = None
) -> int:
    """Runs each check on the event in the stream, from the folder the event comes from; gives
    STOPPED with what they say on err, headed by the plugin's name, where any says something, 0
    where none does, and UNREAD where the stream holds no event as Claude Code hands it, which lets
    it through unchecked. Given the agent, such as `notes:changelog-writer`, it runs them only on
    an event whose agent_type is that agent, and gives 0 on any other, as a tool event's matcher
    tells tools apart, not agents."""
    event = event_read(stream)
    if event is None:
        err.write(
            f"{plugin}: the hook was handed no event as Claude Code hands it, a JSON object with"
            " hook_event_name and cwd, and for PreToolUse tool_name and tool_input, so it lets this"
            " through unchecked; update Claude Code with `claude update`, and where it goes on,"
            " report it at https://github.com/lovaizu/ccpm/issues\n"
        )
        return UNREAD
    if agent is not None and event.get("agent_type") != agent:
        return 0
    os.chdir(event["cwd"])
    said = [s for c in checks for s in c.check(event)]
    if said:
        err.write(f"{plugin}: " + "\n".join(said) + "\n")
        return STOPPED
    return 0
