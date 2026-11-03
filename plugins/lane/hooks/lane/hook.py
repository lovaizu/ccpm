"""What each of lane's hook entries runs: reads the event Claude Code hands on stdin, holds it to
the fields Claude Code documents, has the guard judge it where it is of a subagent of the plugin,
and answers in Claude Code's JSON output of the event: at PreToolUse a break denied with its
sentence, and a held command asked of the person with its; at PostToolUse, PostToolUseFailure and
SubagentStart what the guard says added as context; at SubagentStop the end blocked with it, so the
subagent goes on; and an error told the user too, as a break is the subagent's to put right and an
error the plugin's or Claude Code's, which letting the event go on unchecked would hide. Of a call
made by anyone in the session, it keeps what a run of a subagent of the plugin is given, an Agent
call's prompt or a SendMessage call's message, where the call goes on."""

from __future__ import annotations

import json
import os
import re
import sys
from typing import IO, Any

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "core", "domain"))

import called
import guard
import rules
import schema

# Who must fix a hook's command that does not name the plugin.
LAY_AGAIN = (
    "the plugin's maker must lay its lanes again with `lay.py write`, to write its hooks anew"
)


# The fields of each event lane reads, beside those every event of a subagent has, as the hooks
# reference documents them.
TOOL = {"tool_name": {"type": "string"}, "tool_input": {"type": "object"}}
FIELDS: dict[str, dict[str, Any]] = {
    "PreToolUse": TOOL,
    "PostToolUse": {**TOOL, "tool_response": {}},
    "PostToolUseFailure": TOOL,
    "SubagentStart": {},
    "SubagentStop": {"stop_hook_active": {"type": "boolean"}},
}
# An ID Claude Code gives a session or a subagent's run, as it names the file of its calls kept.
ID = {"type": "string", "pattern": f"^{called.ID.pattern}$"}


def event_in(held: str) -> dict[str, Any]:
    """The JSON Schema of the fields of the event of the name that lane reads, as the hooks
    reference documents them: the event's name, the folder it comes from, the session, the
    subagent's run and type, and the event's own, such as the tool and its input."""
    fields = {
        "hook_event_name": {"const": held},
        "cwd": {"type": "string"},
        "session_id": ID,
        "agent_id": ID,
        "agent_type": {"type": "string"},
        **FIELDS[held],
    }
    return {"type": "object", "required": list(fields), "properties": fields}


def event_wrong(event: dict[str, Any], held: str) -> str:
    """Where the event is out of the fields of the event held, as the hooks reference documents
    them; "" where it is not."""
    out = schema.held(event_in(held), event)
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
    blocked with it as the reason, which the subagent is given to go on with; at any other event it
    added as context for the subagent; and each error as the systemMessage too, which Claude Code
    shows the user. Nothing where nothing was said, which lets the event go on."""
    if not said:
        return {}
    told = "\n".join(s.text if s.plain else f"{plugin}: {s.text}" for s in said)
    user = "\n".join(f"{plugin}: {s.text}" for s in said if s.error)
    found: dict[str, Any] = {"systemMessage": user} if user else {}
    if held == "PreToolUse":
        decision = "ask" if all(s.ask for s in said) else "deny"
        denied = {"hookEventName": held, "permissionDecision": decision}
        return {**found, "hookSpecificOutput": {**denied, "permissionDecisionReason": told}}
    if held == "SubagentStop":
        return {**found, "decision": "block", "reason": told}
    return {**found, "hookSpecificOutput": {"hookEventName": held, "additionalContext": told}}


# The guard's check of each event.
CHECKS = {
    "PreToolUse": guard.check,
    "PostToolUse": guard.came_back,
    "PostToolUseFailure": guard.failed,
    "SubagentStart": guard.started,
    "SubagentStop": guard.stopping,
}


def main(held: str, argv: list[str], stdin: IO[str], stdout: IO[str], root: str) -> None:
    """Answers on stdout the event of the hook's event held, read from stdin, for the plugin at
    root, the folder Claude Code gives as CLAUDE_PLUGIN_ROOT, whose name the hook's command gives
    as its one word. A command not in that form stops each subagent's call, and an event that is
    no JSON object every call, as no subagent can be told from them; the main conversation's calls
    go on, as lane checks subagents alone."""
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
        if isinstance(agent, str) and agent.startswith(f"{plugin}:"):
            name = agent[len(plugin) + 1 :]
            said = CHECKS[held](root, plugin, name, event, event_wrong(event, held))
        # A call stopped is not made, so gives its subagent nothing.
        if all(s.ask for s in said) or held != "PreToolUse":
            guard.handed(plugin, event, held)
    # An end that a stop hook kept going already is told no error again, so an error no one fixes
    # ends no run in a loop.
    if held == "SubagentStop" and isinstance(event, dict) and event.get("stop_hook_active") is True:
        said = [s for s in said if not s.error]
    write(stdout, answer(said, head, held))


def write(stdout: IO[str], found: dict[str, Any]) -> None:
    """Writes the answer on stdout as the one JSON object Claude Code reads there, nothing where it
    is empty."""
    if found:
        stdout.write(json.dumps(found) + "\n")
