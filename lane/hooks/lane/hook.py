"""What each entry of a plugin's hooks runs: every check of its event on the event Claude Code hands
it, in one subagent alone, answered in Claude Code's JSON output. A drift is told the subagent,
its tool's use denied or it kept going; an error, where what a lane is given is not as its IN says,
is told the subagent and the user alike, the use denied or the subagent kept going once, as a
drift is the subagent's to put right and an error the plugin's, which a pass would hide."""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from typing import IO, Any, NamedTuple

import schema

# Who must fix an error lane meets in what Claude Code hands it, as the subagent replies it.
CLAUDE_CODE = (
    "Claude Code must be updated with `claude update`, and where this goes on, it must be reported"
    " at https://github.com/lovaizu/ccpm/issues"
)
# The fields each event of these hooks holds beside hook_event_name and cwd, and the types of each:
# at SubagentStop the agent's last reply, which Claude Code gives as null after the agent hands its
# reply back with SubagentHandback; as a call comes back, its ID, and of a failed one its error.
CALLED = {"tool_name": {"type": "string"}, "tool_input": {"type": "object"}}
FIELDS = {
    "PreToolUse": CALLED,
    "SubagentStop": {"last_assistant_message": {"type": ["string", "null"]}},
    "PostToolUse": {**CALLED, "tool_use_id": {"type": "string"}},
    "PostToolUseFailure": {
        **CALLED,
        "tool_use_id": {"type": "string"},
        "error": {"type": "string"},
    },
}


def event_in(name: str) -> dict[str, Any]:
    """The IN of an event of the name, as Claude Code hands it: a JSON object holding the hook's
    event name, the folder it comes from, and the event's fields FIELDS gives."""
    fields = {"hook_event_name": {"const": name}, "cwd": {"type": "string"}, **FIELDS[name]}
    return {"type": "object", "required": list(fields), "properties": fields}


class Said(NamedTuple):
    """What a check says: a drift, told the subagent; or an error, told the subagent and the user
    alike."""

    text: str
    error: bool = False


def event_read(text: str, held: str) -> tuple[dict[str, Any] | None, str]:
    """The event of the hook's event held in the text, and "" where it is as its IN says, the folder
    it comes from there; otherwise None, or the text read as JSON where it is an object, and what is
    wrong."""
    try:
        event = json.loads(text)
    except ValueError:
        return None, "it holds no JSON"
    out = schema.held(event_in(held), event)
    if out is not None:
        return (event if isinstance(event, dict) else None), out.told()
    if not os.path.isdir(event["cwd"]):
        return event, f"$.cwd: expected a folder, found {schema.shown(event['cwd'])}"
    return event, ""


def answer(event: str, told: str, user: str) -> dict[str, Any]:
    """What a hook of the event answers Claude Code, as its JSON output on exit 0 has it: what the
    subagent is told, where there is anything, as the reason a tool's use is denied at PreToolUse,
    and at SubagentStop as the reason the subagent is kept going, which Claude Code gives it as its
    next instruction, as a call that has come back cannot be stopped; and what the user is told,
    where there is anything, as the systemMessage Claude Code shows them. Nothing told answers
    nothing, which lets it go on."""
    found: dict[str, Any] = {"systemMessage": user} if user else {}
    if told and event == "PreToolUse":
        denied = {"hookEventName": event, "permissionDecision": "deny"}
        found["hookSpecificOutput"] = {**denied, "permissionDecisionReason": told}
    elif told and event == "SubagentStop":
        found.update(decision="block", reason=told)
    return found


def answered(out: IO[str], found: dict[str, Any]) -> None:
    """Writes the answer on the stream as the one JSON object Claude Code reads there, nothing
    where it is empty."""
    if found:
        out.write(json.dumps(found) + "\n")


def said_on(event: dict[str, Any] | None, held: str, said: list[Said]) -> dict[str, Any]:
    """The answer to the event of the hook's event held, None where it could not be read, of what
    was said: each drift and each error told the subagent, each error the user too; at the
    subagent's end, once a stop hook has kept it going, as the event says, an error told the user
    alone, letting it end, so an error is told it once and it is never held for good."""
    again = held == "SubagentStop" and bool((event or {}).get("stop_hook_active"))
    told = "\n".join(s.text for s in said if not (again and s.error))
    return answer(held, told, "\n".join(s.text for s in said if s.error))


def failed(held: str, text: str, stream: IO[str], out: IO[str]) -> None:
    """Answers, on the event of the hook's event held on the stream, the error the text says, where
    no subagent can be told from what the hook was given."""
    try:
        event = json.load(stream)
    except ValueError:
        event = None
    answered(out, said_on(event if isinstance(event, dict) else None, held, [Said(text, True)]))


def run(
    plugin: str, held: str, checks: Sequence[Any], stream: IO[str], out: IO[str], agent: str
) -> None:
    """Runs each check on the event of the hook's event held in the stream, from the folder the
    event comes from, where the event's agent_type is the agent, such as `notes:changelog-writer`,
    and answers on out what they say, each headed by the plugin's name; nothing where none says
    anything or the event is another agent's, as a tool event's matcher tells tools apart, not
    agents. Where the stream holds no event as its IN says, that is an error, as no lane can check
    the call."""
    event, wrong = event_read(stream.read(), held)
    if wrong or event is None:
        name = agent.split(":")[1]
        unread = (
            f"{plugin}: lane cannot check the lanes of {name}: the hook was handed no event as"
            f" Claude Code hands it, {wrong}. Stop here and reply that {CLAUDE_CODE}."
        )
        answered(out, said_on(event, held, [Said(unread, True)]))
        return
    if event.get("agent_type") != agent:
        return
    os.chdir(event["cwd"])
    said = [Said(f"{plugin}: {s.text}", s.error) for c in checks for s in c.check(event)]
    answered(out, said_on(event, held, said))
