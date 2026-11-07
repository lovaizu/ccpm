"""What each of lane's hook entries runs: reads the event Claude Code hands on stdin, holds it to
the fields Claude Code documents, and has the guard judge it where it is of a subagent of the
plugin, or of a dependency's subagent, by its agent_type, or of the main conversation, whose events
carry no agent_type; an event whose agent_type is empty, as Claude Code's prompt-suggestion fork
gives, is dropped. It answers in Claude Code's JSON output of the event: at PreToolUse a break
denied with its sentence, and a held command asked of the person with its; at SubagentStop and Stop
the end blocked with it, so the subagent or the main conversation goes on; at any other event what
the guard says added as context; and an error told the user too, as a break is the role's to put
right and an error the plugin's or Claude Code's, which letting the event go on unchecked would
hide. Of a call made by anyone in the session, it keeps what a start of a subagent of the plugin is
given, an Agent call's prompt or a SendMessage call's message, where the call goes on."""

from __future__ import annotations

import json
import os
import re
import sys
from typing import IO, Any

# No module before it on the path has the name of one of lane's.
sys.path.insert(
    0,  # pragma: no mutate
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "domain"),
)

import called
import guard
import rules
import schema

# Who must fix a hook's command that does not name the plugin.
LAY_AGAIN = (
    "the plugin's maker must lay its lanes again with `lay.py write`, to write its hooks anew"
)


# The fields of each event lane reads, beside those every event has, as the hooks reference
# documents them.
TOOL = {"tool_name": {"type": "string"}, "tool_input": {"type": "object"}}
STOP = {"stop_hook_active": {"type": "boolean"}}
FIELDS: dict[str, dict[str, Any]] = {
    "PreToolUse": TOOL,
    "PostToolUse": {**TOOL, "tool_response": {}},
    "SubagentStart": {},
    "SubagentStop": STOP,
    "UserPromptExpansion": {"command_name": {"type": "string"}},
    "UserPromptSubmit": {"prompt": {"type": "string"}},
    "Stop": STOP,
}
# The events of the main conversation the guard holds it by within a run.
MAIN = ("UserPromptExpansion", "UserPromptSubmit", "PreToolUse", "PostToolUse", "Stop")
# An ID Claude Code gives a session or a subagent's run, as it names the file of its calls kept.
ID = {"type": "string", "pattern": f"^{called.ID.pattern}$"}


def event_in(held: str, main: bool = False) -> dict[str, Any]:
    """The JSON Schema of the fields of the event of the name that lane reads, as the hooks
    reference documents them: the event's name, the folder it comes from, the session, the
    subagent's ID and type, but where the event is the main conversation's, and the event's own,
    such as the tool and its input."""
    agent = {} if main else {"agent_id": ID, "agent_type": {"type": "string"}}
    fields = {
        "hook_event_name": {"const": held},
        "cwd": {"type": "string"},
        "session_id": ID,
        **agent,
        **FIELDS.get(held, {}),
    }
    return {"type": "object", "required": list(fields), "properties": fields}


def event_wrong(event: dict[str, Any], held: str, main: bool = False) -> str:
    """Where the event is out of the fields of the event held, of the main conversation where
    `main`, as the hooks reference documents them; "" where it is not."""
    out = schema.held(event_in(held, main), event)
    if out is not None:
        return out.told()
    if not os.path.isdir(event["cwd"]):
        return f"$.cwd: expected a folder, found {schema.shown(event['cwd'])}"
    return ""


def answer(said: list[guard.Said], plugin: str, held: str) -> dict[str, Any]:
    """What the hook of the event held answers Claude Code of what was said, each line headed by the
    plugin's name, a part given as it is: at PreToolUse the call denied with it as the reason,
    which Claude Code shows the subagent, or, where all said is a held command's, asked of the
    person with it, which Claude Code's permission prompt shows them; at SubagentStop the end
    blocked with it as the reason, which the subagent is given to go on with, and at Stop the same
    for the main conversation; at any other event it added as context; and each error as the
    systemMessage too, which Claude Code shows the user. A note is told the user alone, and where
    all said is notes, the event goes on. Nothing where nothing was said, which lets the event go
    on."""
    if not said:
        return {}
    told = "\n".join(s.text if s.plain else f"{plugin}: {s.text}" for s in said)
    user = "\n".join(f"{plugin}: {s.text}" for s in said if s.error or s.note)
    found: dict[str, Any] = {"systemMessage": user} if user else {}
    if all(s.note for s in said):
        return found
    if held == "PreToolUse":
        decision = "ask" if all(s.ask for s in said) else "deny"
        denied = {"hookEventName": held, "permissionDecision": decision}
        return {**found, "hookSpecificOutput": {**denied, "permissionDecisionReason": told}}
    if held in ENDS:
        return {**found, "decision": "block", "reason": told}
    return {**found, "hookSpecificOutput": {"hookEventName": held, "additionalContext": told}}


# The events of an end, which a block keeps going.
ENDS = ("SubagentStop", "Stop")
# The guard's check of each event of a subagent.
CHECKS = {
    "PreToolUse": guard.check,
    "PostToolUse": guard.came_back,
    "SubagentStart": guard.started,
    "SubagentStop": guard.stopping,
}


def main(held: str, argv: list[str], stdin: IO[str], stdout: IO[str], root: str) -> None:
    """Answers on stdout the event of the hook's event held, read from stdin, for the plugin at
    root, the folder Claude Code gives as CLAUDE_PLUGIN_ROOT, whose name the hook's command gives
    as its one word. A command not in that form stops each subagent's call, and an event that is
    no JSON object every call, as no subagent can be told from them; the main conversation's calls
    go on, as no run of the plugin can be told."""
    plugin = " ".join(argv)
    text = stdin.read()
    try:
        event = json.loads(text)
    except ValueError:
        event = None
    head = plugin
    if not re.fullmatch(rules.NAME, plugin):
        if isinstance(event, dict) and "agent_type" not in event:
            return
        wrong = f"its command gives `{plugin}`, not the plugin's name, as `lay.py write` writes it"
        said, head = [guard.cannot("the lanes of this hook", wrong, LAY_AGAIN)], "lane"
    elif not isinstance(event, dict):
        wrong = "it was handed no JSON object"
        said = [guard.cannot("the lanes of this hook", wrong, guard.CLAUDE_CODE)]
    else:
        agent = event.get("agent_type")
        said = []
        if "agent_type" not in event and held in MAIN:
            said = guard.MAIN[held](root, plugin, event, event_wrong(event, held, True))
        elif isinstance(agent, str) and ":" in agent:
            # A subagent of the plugin by its own name, or of a dependency by its type, as the
            # routes name it.
            ours = agent.startswith(f"{plugin}:")
            name = agent[len(plugin) + 1 :] if ours else agent
            said = CHECKS[held](root, plugin, name, event, event_wrong(event, held))
        # A call stopped is not made, so gives its subagent nothing. Of the events of a call,
        # PreToolUse is the last in order, and the others hand none.
        later = held != "PreToolUse"  # pragma: no mutate
        if all(s.ask for s in said) or later:
            guard.handed(plugin, event, held)
    # An end that a stop hook kept going already is told no error again, so an error no one fixes
    # ends no turn in a loop.
    if held in ENDS and isinstance(event, dict) and event.get("stop_hook_active") is True:
        said = [s for s in said if not s.error]
    write(stdout, answer(said, head, held))


def write(stdout: IO[str], found: dict[str, Any]) -> None:
    """Writes the answer on stdout as the one JSON object Claude Code reads there, nothing where it
    is empty."""
    if found:
        stdout.write(json.dumps(found) + "\n")
