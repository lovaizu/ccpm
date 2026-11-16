"""How the guard reads each hook event as Lane's data and places it on its Runs, its Start, and its
role: by the event's session_id, by a missing agent_id for the main conversation, and by the
agent_id that the PostToolUse of a Start's Agent call ties to it, as claude-code-states.md lists
each state of Claude Code."""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal, Union

from events import Event
from form import LanesFile, Move
from manifest import plugin_name
from runs import Conversation, Run, Start
from script_calls import printed, result_args, write_call

# A subagent's end as it reaches the main conversation, by its agent_id.
NOTIFICATION = re.compile(r"<task-notification>\s*<task-id>([^<]+)</task-id>")


@dataclass(frozen=True)
class Call:
    """One tool call of a role or the main conversation, as the lane types check it: the tool, its
    input, the event's cwd, and the top of the worktree that the cwd lies in."""

    tool: str
    input: Mapping[str, Any]
    cwd: str
    top: str


@dataclass(frozen=True)
class SkillCall:
    """A call of a skill, typed by a person or called by the Skill tool, with the words typed after
    it: UserPromptExpansion's `command_args`, or the Skill tool's `tool_input.args`."""

    plugin: str
    skill: str
    by: Literal["person", "ai"]
    words: str


@dataclass(frozen=True)
class Prompt:
    """A prompt typed by a person, which the Data model's Run holds, such as a reply or a command
    of the plugin's that a Route waits for or goes after."""

    text: str


@dataclass(frozen=True)
class Notification:
    """A subagent's end as it reaches the main conversation, and whether TaskStop stopped it."""

    agent_id: str
    killed: bool


@dataclass(frozen=True)
class ToolCall:
    """A tool call other than a start: a Call."""

    call: Call


@dataclass(frozen=True)
class StartCall:
    """The main conversation's or a subagent's start or resume of a subagent, by its Agent or
    SendMessage call: the role by its name, whether it's a role of the plugin, its text, whether it
    resumes, the call, and the agent_id of the subagent it resumes."""

    role: str
    ours: bool
    text: str
    resume: bool
    tool_use_id: str
    agent_id: str | None = None


@dataclass(frozen=True)
class AgentPosted:
    """The PostToolUse of an Agent or SendMessage call, naming the subagent's agent_id."""

    tool_use_id: str
    agent_id: str


@dataclass(frozen=True)
class ResultPosted:
    """The PostToolUse of a run of result.py that gave 0, as `script_calls.result_args` reads its
    command."""

    role: str
    result: str


@dataclass(frozen=True)
class PrintPosted:
    """The PostToolUse of a run of lay.py print, with the Proposal's ID and what it showed, as
    `script_calls.printed` reads them."""

    proposal_id: str
    words: str


@dataclass(frozen=True)
class StepAsked:
    """A run of step.py, before it runs, as `script_calls.step_args` reads its command: the role
    and the Step it marks."""

    role: str
    step: int


@dataclass(frozen=True)
class ItemAsked:
    """A run of item.py, before it runs, as `script_calls.item_args` reads its command: the role
    and the Item it marks."""

    role: str
    item: str


@dataclass(frozen=True)
class StepPosted:
    """The PostToolUse of a run of step.py that gave 0: the role and the Step it marked."""

    role: str
    step: int


@dataclass(frozen=True)
class ItemPosted:
    """The PostToolUse of a run of item.py that gave 0: the role and the Item it marked."""

    role: str
    item: str


@dataclass(frozen=True)
class ReadPosted:
    """The PostToolUse of a Read: the Call, and the first and the last line it read."""

    call: Call
    first: int
    last: int


@dataclass(frozen=True)
class EndAsked:
    """The main conversation's end of its turn, or a subagent's end, with its last message."""

    last_message: str


What = Union[
    SkillCall,
    Prompt,
    Notification,
    ToolCall,
    StartCall,
    AgentPosted,
    ResultPosted,
    PrintPosted,
    StepAsked,
    ItemAsked,
    StepPosted,
    ItemPosted,
    ReadPosted,
    EndAsked,
]


@dataclass(frozen=True)
class Placed:
    """An event as Lane's data, placed: what it is; each Run whose Lanes hold it, none where it lies
    outside every Run; the Start it comes from, None for the main conversation; and the agent_id
    of a subagent's event."""

    what: What | None
    runs: tuple[Run, ...]
    start: Start | None
    agent_id: str | None


def place(event: Event, conversation: Conversation, lanes: LanesFile, root: str) -> Placed:
    """The event as Lane's data, on its Runs and its Start.

    Takes: the event, the Conversation as it stands, the plugin's lanes.json, and the plugin's
    folder, by which `script_calls.result_args`, `step_args`, and `item_args` read a run of its
    scripts.
    Gives: what the event is, with no `what` for an event that Lane hooks only for another state,
    a call by the Skill tool being a SkillCall by an AI, save one of another plugin's skill that a
    Run holds and no move due names, which is a ToolCall, a SendMessage to the subagent of a role's
    Start a StartCall that resumes that role, a run of step.py or item.py a StepAsked or an
    ItemAsked, its PostToolUse a StepPosted or an ItemPosted, and the PostToolUse of a Read a
    ReadPosted, with the lines it read; for the main conversation's event, each Run of the
    conversation that hasn't ended and isn't aside, and, for its end or a prompt, each Run that
    its skill's Result ended in the turn (`Run.closing`), and, for a start, each Run aside whose
    moves due start its role; for a subagent's event, the Run of the Start tied to its agent_id;
    for a call of lay.py write, the Run of up that showed its ID; for what lay.py print showed, the
    latest of the main conversation's Runs, whose call came last; no Run for an event of a subagent
    that no Start ties, or of the main conversation while every Run stands aside.
    Changes: nothing.
    Refuses: nothing.
    Carries: the placing of each `CC->>G` arrow of S1 to S7 on its Run, Start, and role.
    """
    what = _what(event, conversation, root)
    start, runs = _where(event, conversation, what)
    return Placed(what, runs, start, event.agent_id)


def _where(
    event: Event, conversation: Conversation, what: What | None
) -> tuple[Start | None, tuple[Run, ...]]:
    """The Start that the event comes from and the Runs that hold it: for a subagent's event, or
    the end of one that reaches the main conversation, its tied Start and that Start's Run; for the
    main conversation's, each Run that hasn't ended and doesn't stand aside, and, for its end or a
    prompt, each Run whose turn's end is still held after its skill's Result ended it. A subagent
    resumed lies on its latest Start. A call of lay.py write lies only on each of those Runs that
    showed its ID, and what lay.py print showed only on the latest of them, the Run whose call came
    last."""
    agent = event.agent_id or _notified(event)
    going = tuple(r for r in conversation.runs if not r.ended)
    if agent is None:
        runs = tuple(r for r in conversation.runs if _main(r, what))
        laid = _laid_id(what)
        if laid is not None:
            runs = tuple(r for r in runs if any(s.proposal_id == laid for s in r.shown))
        if isinstance(what, PrintPosted):
            runs = runs[-1:]
        return None, runs
    for run in going:
        for start in reversed(run.starts):
            if start.agent_id == agent:
                return start, (run,)
    return None, ()


def _main(run: Run, what: What | None) -> bool:
    """Whether the Run holds an event of the main conversation: a Run going and not aside; for a
    start, one aside whose moves due after the other plugin's run start that role, the move after
    that call; and, for its end or a prompt, one that its skill's Result ended in this turn."""
    if isinstance(what, StartCall) and run.aside:
        return Move("start", role=what.role) in run.due
    closing = isinstance(what, (EndAsked, Prompt))
    return (not run.ended and not run.aside) or (closing and run.closing)


def _what(event: Event, conversation: Conversation, root: str) -> What | None:
    """What the event is, by its kind and its tool, of the six that `events.hook_entries` hooks."""
    if event.name == "UserPromptExpansion":
        # A UserPromptExpansion names the command typed, as dev/lane/claude-code-states.md records.
        plugin, _, skill = (event.command_name or "").partition(":")
        return SkillCall(plugin, skill, "person", event.command_args or "")
    if event.name == "UserPromptSubmit":
        agent = _notified(event)
        killed = "<status>killed</status>" in (event.prompt or "")
        return Notification(agent, killed) if agent else Prompt(event.prompt or "")
    if event.name in ("Stop", "SubagentStop"):
        return EndAsked(event.last_message or "")
    tool_input = event.tool_input or {}
    if event.name == "PreToolUse":
        return _called(event, tool_input, conversation, root)
    return _posted(event, tool_input, root)


def _called(
    event: Event, tool_input: Mapping[str, Any], conversation: Conversation, root: str
) -> What:
    """What a tool call is: a start of a subagent, a resume of a role's subagent, a call of a
    skill by the Skill tool, or another Call."""
    if event.tool_name == "Agent":
        owner, _, role = str(tool_input.get("subagent_type", "")).rpartition(":")
        text = str(tool_input.get("prompt", ""))
        return StartCall(role, owner == plugin_name(root), text, False, str(event.tool_use_id))
    if event.tool_name == "Skill" and not _unnamed(tool_input, conversation, root):
        plugin, _, skill = str(tool_input.get("skill", "")).partition(":")
        return SkillCall(plugin, skill, "ai", str(tool_input.get("args", "")))
    resumed = _resumed(event, tool_input, conversation)
    if resumed is not None:
        return resumed
    return ToolCall(Call(str(event.tool_name), tool_input, event.cwd, _top(event.cwd)))


def _unnamed(tool_input: Mapping[str, Any], conversation: Conversation, root: str) -> bool:
    """Whether a Skill call is of another plugin's skill that a Run holds and no move due of it
    names, so that it is any other call."""
    name = str(tool_input.get("skill", ""))
    going = [r for r in conversation.runs if not r.ended and not r.aside]
    named = any(Move("call", skill=name) in r.due for r in going)
    return bool(going) and not named and not name.startswith(f"{plugin_name(root)}:")


def _resumed(
    event: Event, tool_input: Mapping[str, Any], conversation: Conversation
) -> StartCall | None:
    """A SendMessage to the subagent of a role's Start, as a resume of that role; None for any
    other call."""
    if event.tool_name != "SendMessage":
        return None
    tied = {s.agent_id: s for r in conversation.runs for s in r.starts if s.agent_id}
    start = tied.get(str(tool_input.get("to")))
    message = str(tool_input.get("message", ""))
    if start is None:
        return None
    return StartCall(start.role, True, message, True, str(event.tool_use_id), start.agent_id)


def _posted(event: Event, tool_input: Mapping[str, Any], root: str) -> What | None:
    """What the PostToolUse of a call tells: a subagent started, a Result given, or a Proposal
    shown."""
    response = event.tool_response if isinstance(event.tool_response, dict) else {}
    if event.tool_name == "Agent" and response.get("agentId"):
        return AgentPosted(str(event.tool_use_id), str(response["agentId"]))
    command = tool_input.get("command")
    if event.tool_name != "Bash" or not isinstance(command, str):
        return None
    given = result_args(command, root)
    if given:
        return ResultPosted(*given)
    shown = printed(command, str(response.get("stdout", "")))
    return PrintPosted(*shown) if shown else None


def _laid_id(what: What | None) -> str | None:
    """The Proposal's ID that a call of lay.py write lays; None for any other event."""
    if not isinstance(what, ToolCall):
        return None
    found = write_call(str(what.call.input.get("command", "")))
    return found[1] if found else None


def _notified(event: Event) -> str | None:
    """The agent_id whose end a task-notification tells the main conversation of."""
    if event.name != "UserPromptSubmit" or not event.prompt:
        return None
    found = NOTIFICATION.match(event.prompt)
    return found[1] if found else None


def _top(cwd: str) -> str:
    """The top of the worktree that the folder lies in, or the folder where no .git lies above."""
    folder = cwd
    while not os.path.exists(os.path.join(folder, ".git")):
        if os.path.dirname(folder) == folder:
            return cwd
        folder = os.path.dirname(folder)
    return folder
