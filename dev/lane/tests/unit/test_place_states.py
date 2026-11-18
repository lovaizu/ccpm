"""The state transition cases of place.py's `place`: each state of a conversation's Runs and
Starts that the guard places an event in, with each kind of hook event that can reach it, one
that the state doesn't expect included, and where each lies: the Start, by its call, and the
Runs."""

from __future__ import annotations

import dataclasses
from typing import Any

import lane_data as d
import pytest
from place import place

WRITER = d.start("writer", agent_id="a01")
RESUMED = dataclasses.replace(WRITER, tool_use_id="toolu_w2", resumed=True)
REVIEWER = d.start("reviewer", agent_id="a02")

# Each state of the conversation, by its Runs.
TIED = (d.run(starts=(WRITER,), due=()),)
UNTIED = (d.run(starts=(dataclasses.replace(WRITER, agent_id=None),)),)
RESUMED_BEFORE_END = (
    d.run(starts=(dataclasses.replace(WRITER, results=("written",)), RESUMED), due=()),
)
ENDED = dataclasses.replace(WRITER, ended=True)
CLOSING = (d.run(starts=(ENDED,), due=(), ended=True, closing=True),)
CLOSED = (d.run(starts=(ENDED,), due=(), ended=True),)
TWO_RUNS = (
    d.run(starts=(WRITER,), due=()),
    d.run(starts=(REVIEWER,), due=(), id="r2", skill="check"),
)


def notification(called: str | None, agent: str = "a01") -> dict[str, Any]:
    """The fields of a subagent's end as it reaches the main conversation, naming the call it ends
    where `called` gives one."""
    named = f"<tool-use-id>{called}</tool-use-id>" if called else ""
    prompt = (
        f"<task-notification><task-id>{agent}</task-id>{named}"
        "<status>completed</status></task-notification>"
    )
    return {"name": "UserPromptSubmit", "prompt": prompt}


# Each kind of event, as the fields of its hook event.
SUBAGENTS_CALL = {
    "name": "PreToolUse",
    "agent_id": "a01",
    "tool_name": "Bash",
    "tool_input": {"command": "ls"},
}
SUBAGENTS_STOP = {"name": "SubagentStop", "agent_id": "a01", "last_message": "Done."}
END_OF_FIRST = notification("toolu_writer")
END_OF_RESUME = notification("toolu_w2")
END_NAMING_NONE = notification(None)
MAINS_CALL = {"name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "ls"}}
MAINS_STOP = {"name": "Stop", "last_message": "Done."}
PROMPT = {"name": "UserPromptSubmit", "prompt": "yes"}


def lies(runs: tuple[Any, ...], fields: dict[str, Any]) -> tuple[str | None, tuple[str, ...]]:
    """The call of the Start the event lies on, None for none, and the ids of its Runs."""
    got = place(d.event(**fields), d.conversation(*runs), d.lanes_file(), d.ROOT)
    return (got.start.tool_use_id if got.start else None), tuple(r.id for r in got.runs)


@pytest.mark.supports(
    "test_a_call_that_breaks_a_lane_gets_its_steps_sentence",
    "test_an_end_with_no_result_is_stopped_with_its_last_steps_sentence",
    "test_an_end_that_reaches_after_a_resume_ends_only_the_pass_it_names",
    "test_a_call_of_the_main_conversation_that_breaks_a_lane_is_stopped",
    "test_calls_outside_the_run_go_unchecked",
)
@pytest.mark.parametrize(
    ("state", "fields", "then"),
    [
        pytest.param(TIED, SUBAGENTS_CALL, ("toolu_writer", ("r1",)), id="tied-subagents-call"),
        pytest.param(TIED, SUBAGENTS_STOP, ("toolu_writer", ("r1",)), id="tied-subagents-stop"),
        pytest.param(TIED, END_OF_FIRST, ("toolu_writer", ("r1",)), id="tied-end-of-its-call"),
        pytest.param(
            TIED,
            END_OF_RESUME,
            ("toolu_writer", ("r1",)),
            id="tied-end-naming-a-call-it-didnt-make",
        ),
        pytest.param(TIED, END_NAMING_NONE, ("toolu_writer", ("r1",)), id="tied-end-naming-none"),
        pytest.param(TIED, MAINS_CALL, (None, ("r1",)), id="tied-mains-call"),
        pytest.param(TIED, MAINS_STOP, (None, ("r1",)), id="tied-mains-stop"),
        pytest.param(TIED, PROMPT, (None, ("r1",)), id="tied-prompt"),
        pytest.param(UNTIED, SUBAGENTS_CALL, (None, ()), id="untied-subagents-call"),
        pytest.param(UNTIED, END_OF_FIRST, (None, ()), id="untied-end"),
        pytest.param(UNTIED, MAINS_CALL, (None, ("r1",)), id="untied-mains-call"),
        pytest.param(
            RESUMED_BEFORE_END, SUBAGENTS_CALL, ("toolu_w2", ("r1",)), id="resumed-subagents-call"
        ),
        pytest.param(
            RESUMED_BEFORE_END, SUBAGENTS_STOP, ("toolu_w2", ("r1",)), id="resumed-subagents-stop"
        ),
        pytest.param(
            RESUMED_BEFORE_END,
            END_OF_FIRST,
            ("toolu_writer", ("r1",)),
            id="resumed-end-of-the-first-call",
        ),
        pytest.param(
            RESUMED_BEFORE_END, END_OF_RESUME, ("toolu_w2", ("r1",)), id="resumed-end-of-the-resume"
        ),
        pytest.param(
            RESUMED_BEFORE_END, END_NAMING_NONE, ("toolu_w2", ("r1",)), id="resumed-end-naming-none"
        ),
        pytest.param(CLOSING, MAINS_CALL, (None, ()), id="closing-mains-call"),
        pytest.param(CLOSING, MAINS_STOP, (None, ("r1",)), id="closing-mains-stop"),
        pytest.param(CLOSING, PROMPT, (None, ("r1",)), id="closing-prompt"),
        pytest.param(CLOSING, SUBAGENTS_CALL, (None, ()), id="closing-subagents-call"),
        pytest.param(CLOSING, END_OF_FIRST, (None, ()), id="closing-end"),
        pytest.param(CLOSED, MAINS_STOP, (None, ()), id="closed-mains-stop"),
        pytest.param(CLOSED, PROMPT, (None, ()), id="closed-prompt"),
        pytest.param(
            TWO_RUNS, SUBAGENTS_CALL, ("toolu_writer", ("r1",)), id="two-runs-first-subagents-call"
        ),
        pytest.param(
            TWO_RUNS,
            dict(SUBAGENTS_CALL, agent_id="a02"),
            ("toolu_reviewer", ("r2",)),
            id="two-runs-second-subagents-call",
        ),
        pytest.param(TWO_RUNS, MAINS_CALL, (None, ("r1", "r2")), id="two-runs-mains-call"),
    ],
)
def test_an_event_in_each_state_of_the_conversation(
    state: tuple[Any, ...], fields: dict[str, Any], then: tuple[str | None, tuple[str, ...]]
) -> None:
    """Given: a Run whose writer Start is tied, untied, or resumed before the end of its first
    call; a Run that its skill's Result ended in this turn, or before it; or two Runs.
    When: a subagent's call or end, its end reaching the main conversation naming its call, the
    resume's, or none, or the main conversation's call, end, or prompt comes.
    Then: a subagent's event lies on the latest Start tied to its agent_id, and an end that
    reaches the main conversation on the Start of the call it names, or the latest where it names
    none of them; the main conversation's lies on each Run going, its end and a prompt on a Run
    still closing too; an event of an agent_id that no Start of a going Run ties lies outside."""
    assert lies(state, fields) == then
