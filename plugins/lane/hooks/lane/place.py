"""Which run, start, role, and step each move of a conversation belongs to, and what kind of move it
is, by what Claude Code's hook events carry, as dev/lane/claude-code-states.md lists."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from record import Run
from report import Report

# A hook event as Claude Code sends it on standard input.
Event = dict[str, Any]


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
    """One move placed on its run: its `kind`, one of `call`, `start`, `tie`, `queue`, `drop`,
    `read`, `report`, `end`, `turn_end`, `typed`, and `result_reached`; the role whose steps hold
    it, the subagent's agent type, or the skill's name of the run for the main conversation; the
    subagent's `agent_id`, None for the main conversation; the step its start stands at; and the
    report where a reporter made the move."""

    kind: str
    event: Event
    run: Run
    role: str
    agent_id: str | None
    step: str | None
    report: Report | None


def skill_call(event: Event) -> SkillCall | None:
    """The skill that the event calls.

    Takes: a UserPromptExpansion, or a PostToolUse of Skill, so that a Skill call denied at its
    PreToolUse calls no skill.
    Gives: the skill by `command_name` or `tool_input.skill`, with `command_args` or `args`; None
    for any other event.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("place.skill_call")


def opening(event: Event, runs: list[Run]) -> list[Run]:
    """The runs whose plugin's folder the event first lets the guard read from the transcript.

    Takes: a hook event, and the runs of its conversation.
    Gives: each run with no folder yet, at an event of the main conversation after the skill's
    call, as the transcript holds the skill's base directory only from then: any event with no
    `agent_id` but the UserPromptExpansion of the call and the PreToolUse and PostToolUse of its
    Skill call; none at a subagent's event.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("place.opening")


def place(event: Event, runs: list[Run]) -> Move | None:
    """The move that the event makes, on the run whose start it belongs to.

    Takes: a hook event, and the runs of its conversation.
    Gives: the move, placed by `session_id`, by a missing `agent_id` for the main conversation, by
    the `agent_id` that the PostToolUse of an Agent call tied to a start, and by the skill that a
    typed command or a result names; a reporter's Bash call as a `report` move with the report that
    report.read_report gives of its output; the PostToolUse of a SendMessage as a `tie` where it
    resumed the subagent, and as a `queue` where it queued the message to a subagent that still
    runs; that subagent's SubagentStop as the `end` of the pass that ran, on the start tied to it
    before, with the resume queued still untied; None where the event lies outside each run, such
    as an `agent_id` that no start ties.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("place.place")
