"""How the guard reads each hook event as Lane's data and places it on its Runs, its Start, and its
role: by the event's session_id, by a missing agent_id for the main conversation, and by the
agent_id that the PostToolUse of a Start's Agent call ties to it, as claude-code-states.md lists
each state of Claude Code."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal, Union

from events import Event
from form import LanesFile
from runs import Conversation, Run, Start


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
    resumes, and the call."""

    role: str
    ours: bool
    text: str
    resume: bool
    tool_use_id: str


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


def place(event: Event, conversation: Conversation, lanes: LanesFile) -> Placed:
    """The event as Lane's data, on its Runs and its Start.

    Takes: the event, the Conversation as it stands, and the plugin's lanes.json.
    Gives: what the event is, with no `what` for an event that Lane hooks only for another state;
    for the main conversation's event, each Run of the conversation that isn't aside; for a
    subagent's event, the Run of the Start tied to its agent_id; for a call of lay.py write, the Run
    of up that showed its ID; no Run for an event of a subagent that no Start ties, or of the main
    conversation while every Run stands aside.
    Changes: nothing.
    Refuses: nothing.
    Carries: the placing of each `CC->>G` arrow of S1 to S7 on its Run, Start, and role.
    """
    raise NotImplementedError
