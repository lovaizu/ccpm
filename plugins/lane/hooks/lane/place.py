"""Which run, start, role, and step each move of a conversation belongs to, and what kind of move it
is, by what Claude Code's hook events carry, as dev/lane/claude-code-states.md lists."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypedDict

from record import Run

# A hook event as Claude Code sends it on standard input.
Event = dict[str, Any]


class Report(TypedDict, total=False):
    """What a reporter of bin/ prints for the guard: its `kind`, one of `step`, `item`, and
    `result`, and the step, the item, or the result it reports done."""

    kind: str
    step: str
    item: str
    result: str


@dataclass
class SkillCall:
    """A call of a skill, typed by the person or made by the Skill tool, with the words given
    after it."""

    session_id: str
    transcript_path: str
    skill: str
    words: str


@dataclass
class Move:
    """One move placed on its run: its `kind`, one of `call`, `start`, `tie`, `drop`, `read`,
    `report`, `end`, `turn_end`, `typed`, and `result_reached`; the role, None for the main
    conversation; the subagent's `agent_id`; the step its start stands at; and the report where a
    reporter made the move."""

    kind: str
    event: Event
    run: Run
    role: str | None
    agent_id: str | None
    step: str | None
    report: Report | None


def skill_call(event: Event) -> SkillCall | None:
    """The skill that the event calls.

    Takes: a UserPromptExpansion, or a PreToolUse or PostToolUse of Skill.
    Gives: the skill by `command_name` or `tool_input.skill`, with `command_args` or `args`; None
    for any other event.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("place.skill_call")


def place(event: Event, runs: list[Run]) -> Move | None:
    """The move that the event makes, on the run whose start it belongs to.

    Takes: a hook event, and the runs of its conversation.
    Gives: the move, placed by `session_id`, by a missing `agent_id` for the main conversation, by
    the `agent_id` that the PostToolUse of an Agent call tied to a start, and by the skill that a
    typed command or a result names; a reporter's Bash call as a `report` move with the report its
    output gives; None where the event lies outside each run, such as an `agent_id` that no start
    ties.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("place.place")
