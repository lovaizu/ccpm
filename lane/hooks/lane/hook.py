"""What each entry of a plugin's hooks runs: every check of its event on the event Claude Code hands
it, in one subagent alone, a use denied or the subagent kept going with what they say, answered in
Claude Code's JSON output."""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from typing import IO, Any, NamedTuple

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


class Said(NamedTuple):
    """What a check says: told the subagent, or, where it is for the user, told them alone, the use
    or the end let go on."""

    text: str
    user: bool = False


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


def answer(event: str, told: str, user: str) -> dict[str, Any]:
    """What a hook of the event answers Claude Code, as its JSON output on exit 0 has it: what the
    subagent is told, where there is anything, as the reason a tool's use is denied at PreToolUse,
    and at SubagentStop as the reason the subagent is kept going, which Claude Code gives it as its
    next instruction; and what the user is told, where there is anything, as the systemMessage
    Claude Code shows them, letting the use or the end go on. Nothing told answers nothing, which
    lets it go on."""
    found: dict[str, Any] = {"systemMessage": user} if user else {}
    if told and event == "PreToolUse":
        denied = {"hookEventName": event, "permissionDecision": "deny"}
        found["hookSpecificOutput"] = {**denied, "permissionDecisionReason": told}
    elif told:
        found.update(decision="block", reason=told)
    return found


def answered(out: IO[str], found: dict[str, Any]) -> None:
    """Writes the answer on the stream as the one JSON object Claude Code reads there, nothing
    where it is empty."""
    if found:
        out.write(json.dumps(found) + "\n")


def run(plugin: str, checks: Sequence[Any], stream: IO[str], out: IO[str], agent: str) -> None:
    """Runs each check on the event in the stream, from the folder the event comes from, where the
    event's agent_type is the agent, such as `notes:changelog-writer`, and answers on out what they
    say, each headed by the plugin's name; nothing where none says anything or the event is another
    agent's, as a tool event's matcher tells tools apart, not agents; where the stream holds no
    event as Claude Code hands it, tells the user so, letting it through unchecked."""
    event = event_read(stream)
    if event is None:
        each = ", ".join(f"for {e} {' and '.join(f)}" for e, f in FIELDS.items())
        unread = (
            f"{plugin}: the hook was handed no event as Claude Code hands it, a JSON object with"
            f" hook_event_name and cwd, and {each}, so it lets this through unchecked; update"
            " Claude Code with `claude update`, and where it goes on, report it at"
            " https://github.com/lovaizu/ccpm/issues"
        )
        answered(out, answer("", "", unread))
        return
    if event.get("agent_type") != agent:
        return
    os.chdir(event["cwd"])
    said = [s for c in checks for s in c.check(event)]
    told = "\n".join(f"{plugin}: {s.text}" for s in said if not s.user)
    users = "\n".join(f"{plugin}: {s.text}" for s in said if s.user)
    answered(out, answer(event["hook_event_name"], told, users))
