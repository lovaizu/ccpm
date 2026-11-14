"""The guard's entry, which each of Lane's hook entries runs as
`python3 <plugin>/hooks/lane/hook.py` on each hook event of Claude Code: it alone holds the form of
Claude Code's hook events and answers, reads each event into the guard's form, and gives Claude Code
the guard's decision. A hook whose script fails stops the call, as its entry's `onFailure` is
`block`."""

from __future__ import annotations

import json
import os
import re
import sys
from collections.abc import Mapping
from dataclasses import replace
from typing import Any

from domain import said
from domain.event import (
    BEGUN,
    CALL,
    COMMAND,
    ELSE,
    ENDS,
    ENTER,
    OTHER,
    RAN,
    REACHED,
    READ,
    RESUME,
    SKILL,
    START,
    STOP_TASK,
    TURN_ENDS,
    TYPED,
    WRITE,
    Call,
    Event,
)
from domain.fault import Fault
from domain.guard import Decision, decide
from domain.laid_set import load
from domain.run_record import temp

# The folder of the plugin that holds this script, `<plugin>/hooks/lane/hook.py`.
_PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read(payload: str, environ: Mapping[str, str]) -> tuple[str, Event]:
    """The name of the hook event and the moment it tells, from the JSON payload that Claude Code
    gives on stdin and the hook's environment, whose `CLAUDE_PROJECT_DIR` is the root of the
    repository: a PreToolUse as CALL of its kind of Call; a PostToolUse as RAN, or, of a start or
    a resume, as BEGUN of the subagent that its response names; a PostToolUseFailure as RAN that
    failed; a person's prompt, or a command of a plugin's skill that expands, as TYPED; a prompt
    that tells a subagent's end as REACHED with its status and result; a SubagentStop as ENDS; a
    Stop as TURN_ENDS with each subagent that runs; and each other event as OTHER, in the form that
    the recorded runs of Claude Code show, the acting subagent by `agent_id` alone, never by
    `prompt_id`, which changes as the person types while a subagent runs. Raises
    Fault, naming what it lacks, with Lane to fix it, where the payload isn't such an event."""
    try:
        given: dict[str, Any] = json.loads(payload)
        name = given["hook_event_name"]
        base = Event(
            OTHER,
            session=given["session_id"],
            cwd=given["cwd"],
            root=environ.get("CLAUDE_PROJECT_DIR") or given["cwd"],
            agent=given.get("agent_id", ""),
            role=given.get("agent_type", ""),
        )
        return name, _MOMENTS.get(name, _other)(given, base)
    except (ValueError, KeyError, TypeError, AttributeError) as e:
        raise Fault(f"the hook event isn't one that Claude Code sends ({e!r})", "Lane") from None


def _other(payload: dict[str, Any], base: Event) -> Event:
    return base


# The kind of a call by its tool's name.
_KINDS = {
    "Bash": COMMAND,
    "Write": WRITE,
    "Edit": WRITE,
    "Read": READ,
    "Agent": START,
    "SendMessage": RESUME,
    "TaskStop": STOP_TASK,
    "Skill": SKILL,
    "EnterWorktree": ENTER,
    "ExitWorktree": ENTER,
}


def _call(payload: dict[str, Any]) -> Call:
    given = payload["tool_input"]
    kind = _KINDS.get(payload["tool_name"], ELSE)
    return Call(
        kind,
        command=given.get("command", "") if kind == COMMAND else "",
        path=given.get("file_path", ""),
        role=given.get("subagent_type", ""),
        agent=given.get("to", "") or given.get("task_id", ""),
        text=given.get("prompt", "") or given.get("message", ""),
        skill=given.get("skill", ""),
        args=given.get("args", ""),
    )


def _pre_tool_use(payload: dict[str, Any], base: Event) -> Event:
    return replace(base, moment=CALL, call=_call(payload))


def _post_tool_use(payload: dict[str, Any], base: Event) -> Event:
    call = _call(payload)
    response = payload.get("tool_response")
    if call.kind == START and isinstance(response, dict):
        return replace(base, moment=BEGUN, agent=response["agentId"], role=call.role)
    printed = response.get("stdout", "") if isinstance(response, dict) else ""
    return replace(base, moment=RAN, call=call, printed=printed)


def _failed(payload: dict[str, Any], base: Event) -> Event:
    return replace(base, moment=RAN, call=_call(payload), failed=True)


def _prompt(payload: dict[str, Any], base: Event) -> Event:
    prompt = payload["prompt"]
    if not prompt.startswith("<task-notification>"):
        return replace(base, moment=TYPED, prompt=prompt)
    told = {tag: _tag(prompt, tag) for tag in ("task-id", "status", "result")}
    return replace(
        base,
        moment=REACHED,
        agent=told["task-id"],
        message=told["result"],
        status=told["status"],
    )


def _tag(text: str, tag: str) -> str:
    found = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
    return found[1] if found else ""


def _expansion(payload: dict[str, Any], base: Event) -> Event:
    command, args = payload["command_name"], payload.get("command_args", "")
    return replace(base, moment=TYPED, prompt=payload["prompt"], command=command, args=args)


def _subagent_stop(payload: dict[str, Any], base: Event) -> Event:
    message = payload.get("last_assistant_message", "")
    return replace(base, moment=ENDS, message=message, again=bool(payload["stop_hook_active"]))


def _stop(payload: dict[str, Any], base: Event) -> Event:
    running = tuple(task["id"] for task in payload.get("background_tasks", []))
    message = payload.get("last_assistant_message", "")
    return replace(base, moment=TURN_ENDS, message=message, running=running)


_MOMENTS = {
    "PreToolUse": _pre_tool_use,
    "PostToolUse": _post_tool_use,
    "PostToolUseFailure": _failed,
    "UserPromptSubmit": _prompt,
    "UserPromptExpansion": _expansion,
    "SubagentStop": _subagent_stop,
    "Stop": _stop,
}


def answer(name: str, decision: Decision) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr that give Claude Code the decision on the hook event of the
    name, as its hooks reference says: a stop as the event takes one, a PreToolUse's denial with
    its reason, a Stop's or a SubagentStop's block with its reason, a prompt's block, and the
    context that the main conversation reads beside the event where the event takes one."""
    if decision.stop and name == "PreToolUse":
        denied = {"permissionDecision": "deny", "permissionDecisionReason": decision.said}
        return 0, json.dumps({"hookSpecificOutput": {"hookEventName": name, **denied}}), ""
    if decision.stop:
        return 0, json.dumps({"decision": "block", "reason": decision.said}), ""
    if decision.context:
        context = {"hookEventName": name, "additionalContext": decision.context}
        return 0, json.dumps({"hookSpecificOutput": context}), ""
    return 0, "", ""


def main(stdin: str, environ: Mapping[str, str]) -> tuple[int, str, str]:
    """The guard's answer to the event on stdin, from the laid set of the plugin that holds this
    script and the run records in the system's temporary folder; a stop with why and who must fix
    it where the event can't be read or the laid set can't be loaded."""
    try:
        name, event = read(stdin, environ)
    except Fault as fault:
        told = said.cant_check("lane", fault.why, fault.who)
        return 2, "", told + "\n"
    plugin = os.path.basename(_PLUGIN_ROOT)
    try:
        laid_set = load(_PLUGIN_ROOT)
    except Fault as fault:
        return answer(name, Decision(stop=True, said=said.cant_check(plugin, fault.why, fault.who)))
    if laid_set is None:
        why = f"{os.path.join(_PLUGIN_ROOT, 'hooks', 'lanes.json')} is missing"
        return answer(
            name, Decision(stop=True, said=said.cant_check(plugin, why, "the plugin's maker"))
        )
    return answer(name, decide(event, laid_set, _PLUGIN_ROOT, temp(environ)))


if __name__ == "__main__":
    import os

    code, out, err = main(sys.stdin.read(), os.environ)
    sys.stdout.write(out)
    sys.stderr.write(err)
    sys.exit(code)
