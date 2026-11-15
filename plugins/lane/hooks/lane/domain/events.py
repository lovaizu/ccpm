"""Claude Code's hooks as the guard meets them: the form of the event that Claude Code hands a hook
on standard input, the form of the answer it takes back, and the entries of hooks.json that start
the guard on each event, as Claude Code's hooks reference gives them."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


class NotAnEvent(Exception):
    """Standard input that isn't a hook event in Claude Code's form, with what's wrong, so that the
    hook fails and its entry's onFailure stops the call."""


@dataclass(frozen=True)
class Event:
    """One hook event, with the fields of Claude Code's payload that the guard reads; a field that
    the event's kind doesn't carry is None."""

    name: str
    session_id: str
    cwd: str
    agent_id: str | None
    agent_type: str | None
    tool_name: str | None
    tool_input: Mapping[str, Any] | None
    tool_use_id: str | None
    tool_response: Any
    prompt: str | None
    command_name: str | None
    command_args: str | None
    last_message: str | None


@dataclass(frozen=True)
class Answer:
    """What the guard answers an event: whether it stops the call, the start, the end, or the
    prompt, and the words that reach the role or the person, empty where it says nothing."""

    stop: bool
    words: str


@dataclass(frozen=True)
class Output:
    """What the hook gives Claude Code: its exit code, its standard output, and its standard
    error."""

    code: int
    stdout: str
    stderr: str


def read_event(text: str) -> Event:
    """The hook event that Claude Code handed in.

    Takes: the hook's standard input.
    Gives: the Event.
    Changes: nothing.
    Refuses: NotAnEvent, where the text isn't JSON or lacks `hook_event_name` or `session_id`.
    Carries: each `CC->>G` arrow of S1 to S7, as it comes in.
    """
    raise NotImplementedError("events.read_event")


def write_answer(event: Event, answer: Answer) -> Output:
    """The guard's answer, in the form that Claude Code takes for the event's kind.

    Takes: the event, and the guard's answer to it.
    Gives: the exit code, the JSON or words on standard output, and the words on standard error,
    such as a PreToolUse's `permissionDecision` of `deny` with its reason, or a Stop's `decision` of
    `block`.
    Changes: nothing.
    Refuses: nothing.
    Carries: each `G-->>` arrow of S1 to S7 that reaches a role, the main conversation, or the
    person through Claude Code.
    """
    raise NotImplementedError("events.write_answer")


def hook_entries() -> dict[str, Any]:
    """Lane's entries of hooks.json, by which Claude Code runs hook.py on each event the guard
    needs.

    Takes: nothing.
    Gives: the `hooks` object of hooks.json for UserPromptSubmit, UserPromptExpansion, PreToolUse,
    PostToolUse, Stop, and SubagentStop, each an entry that runs
    `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/hook.py` with `onFailure` `block`.
    Changes: nothing.
    Refuses: nothing.
    Carries: S2 `L->>LS: replaces Lane's hook entries, as the guard's code names them`.
    """
    raise NotImplementedError("events.hook_entries")
