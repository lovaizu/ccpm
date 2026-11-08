"""Decides what passes between hook.py and the guard: a hook event as the guard reads it, and the
answer that the guard gives, with who fixes what the guard can't check."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any, NamedTuple

# Who fixes the lanes laid, as `lay.py write` lays them again from a proposal.
LAY_AGAIN = "the maker of {plugin} must lay its lanes again with Lane's lay.py write"
# Who fixes a hook input that Claude Code gave out of its documented form.
CLAUDE_CODE = "Anthropic must fix Claude Code, whose hook input isn't as its documentation gives it"


class Fault(Exception):
    """A check that the guard can't run, with what's wrong, who must fix it, and what it's about:
    a lane's sentence, a lane as text, or None where it's about every lane of the role or about the
    routes."""

    def __init__(self, what: str, who: str, about: Any = None) -> None:
        super().__init__(what)
        self.what = what
        self.who = who
        self.about = about


class Event(NamedTuple):
    """A hook event, as hook.py reads it from Claude Code's hook input."""

    # The event's name, such as PreToolUse.
    name: str
    # The session's ID.
    session: str
    # The folder that the session works in.
    cwd: str
    # The ID of the subagent that the event comes from, or None for the main conversation.
    agent_id: str | None = None
    # The type of that subagent, such as `changelog:writer`, or None.
    agent_type: str | None = None
    # The tool of a tool event, or None.
    tool: str | None = None
    # The tool's input of a tool event.
    tool_input: Mapping[str, Any] = MappingProxyType({})
    # What the tool gave back, in PostToolUse.
    tool_response: Any = None
    # The prompt of UserPromptSubmit.
    prompt: str | None = None
    # The command of UserPromptExpansion, such as `changelog:write`.
    command: str | None = None
    # Whether a stop hook kept the conversation or the role going before, in Stop and SubagentStop.
    stop_active: bool = False


class Answer(NamedTuple):
    """What the guard answers Claude Code. Each field left None says nothing."""

    # Why a tool call stops, which the role or the main conversation reads.
    deny: str | None = None
    # Why a tool call goes to the person to approve.
    ask: str | None = None
    # What Claude Code adds beside the event for the role or the main conversation.
    context: str | None = None
    # Why the role or the main conversation goes on, where it would end.
    block: str | None = None
    # What whoever runs the plugin reads.
    tell: str | None = None
