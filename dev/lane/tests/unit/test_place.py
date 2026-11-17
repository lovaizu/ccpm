"""The unit cases of place.py, how the guard reads each hook event as Lane's data and places it,
through `place`: each kind of What an event is, and each way it lies on its Runs and its Start, in
a Run, aside, or outside every Run."""

from __future__ import annotations

import dataclasses
from typing import Any

import lane_data as d
import pytest
from place import (
    AgentPosted,
    Call,
    EndAsked,
    Notification,
    Prompt,
    ResultPosted,
    SkillCall,
    StartCall,
    ToolCall,
    place,
)

WRITER = d.start("writer", agent_id="a01")
RUN = d.run(starts=(WRITER,), due=())
NOTIFICATION = (
    "<task-notification><task-id>a01</task-id><status>{status}</status>"
    '<summary>Agent "writer" {status}</summary></task-notification>'
)


def placed(name: str, *runs: Any, **fields: Any) -> Any:
    """The event placed in a conversation of the Runs, with the walkthrough's lanes.json."""
    return place(d.event(name, **fields), d.conversation(*runs), d.lanes_file(), d.ROOT)


@pytest.mark.supports("test_up_shows_the_walkthroughs_proposal")
def test_a_typed_command_is_a_persons_skill_call() -> None:
    """Given: a UserPromptExpansion of /changelog:write 0.2.0.
    When: place reads it.
    Then: it is a SkillCall of changelog's write by a person, with the words 0.2.0."""
    got = placed("UserPromptExpansion", command_name="changelog:write", command_args="0.2.0")
    assert got.what == SkillCall("changelog", "write", "0.2.0")


@pytest.mark.supports("test_an_ai_lays_by_its_own_run_of_lay")
def test_a_skill_tool_call_is_an_ais_skill_call() -> None:
    """Given: the main conversation's PreToolUse of the Skill tool on lane:up with changelog.
    When: place reads it.
    Then: it is a SkillCall of lane's up by an AI, with the words changelog."""
    got = placed(
        "PreToolUse", tool_name="Skill", tool_input={"skill": "lane:up", "args": "changelog"}
    )
    assert got.what == SkillCall("lane", "up", "changelog")


@pytest.mark.supports("test_a_move_that_waits_for_the_person_lets_the_turn_end")
def test_a_persons_reply_is_a_prompt_on_each_run() -> None:
    """Given: write's Run, and a UserPromptSubmit of the person's reply.
    When: place reads it.
    Then: it is a Prompt of the reply, on write's Run."""
    got = placed("UserPromptSubmit", RUN, prompt="yes")
    assert got.what == Prompt("yes") and got.runs == (RUN,)


@pytest.mark.supports("test_a_subagent_stopped_by_task_stop_is_due_again")
@pytest.mark.parametrize("status, killed", [("completed", False), ("killed", True)])
def test_a_subagents_end_reaching_the_main_conversation_is_a_notification(
    status: str, killed: bool
) -> None:
    """Given: write's Run with writer's Start tied to a01, and a task-notification of a01, completed
    or killed by TaskStop.
    When: place reads it.
    Then: it is a Notification of a01, killed only where TaskStop stopped it."""
    got = placed("UserPromptSubmit", RUN, prompt=NOTIFICATION.format(status=status))
    assert got.what == Notification("a01", killed)


@pytest.mark.supports("test_calls_that_keep_every_lane_go_through")
def test_a_subagents_call_is_a_tool_call_on_its_starts_run() -> None:
    """Given: write's Run with writer's Start tied to a01, and a01's Bash call.
    When: place reads it.
    Then: it is a ToolCall of the command, from writer's Start, on write's Run."""
    got = placed(
        "PreToolUse",
        RUN,
        agent_id="a01",
        tool_name="Bash",
        tool_input={"command": "git log --oneline"},
    )
    assert isinstance(got.what, ToolCall) and got.what.call.input == {
        "command": "git log --oneline"
    }
    assert (got.runs, got.start, got.agent_id) == ((RUN,), WRITER, "a01")


@pytest.mark.supports("test_the_walkthroughs_run_moves_in_the_order_the_user_set")
def test_an_agent_call_is_a_start() -> None:
    """Given: write's Run, and the main conversation's Agent call of changelog:writer.
    When: place reads it.
    Then: it is a StartCall of writer with its text, not a resume, from the main conversation."""
    tool_input = {"subagent_type": "changelog:writer", "prompt": "Carry out your steps"}
    got = placed("PreToolUse", RUN, tool_name="Agent", tool_input=tool_input, tool_use_id="toolu_1")
    assert got.what == StartCall("writer", True, "Carry out your steps", False, "toolu_1")
    assert got.start is None


@pytest.mark.supports("test_a_subagents_start_of_a_role_is_stopped")
def test_an_agent_call_of_no_role_of_the_plugin_is_a_start_not_ours() -> None:
    """Given: write's Run, and writer's Agent call of Explore, which isn't changelog's.
    When: place reads it.
    Then: it is a StartCall of Explore that isn't the plugin's, from writer's Start."""
    tool_input = {"subagent_type": "Explore", "prompt": "Find the tests"}
    got = placed(
        "PreToolUse",
        RUN,
        agent_id="a01",
        tool_name="Agent",
        tool_input=tool_input,
        tool_use_id="toolu_2",
    )
    assert got.what == StartCall("Explore", False, "Find the tests", False, "toolu_2")
    assert got.start == WRITER


@pytest.mark.supports("test_a_resume_where_the_routes_open_none_moves_no_run")
def test_a_send_message_to_a_roles_subagent_is_a_resume() -> None:
    """Given: write's Run with writer's Start tied to a01, and SendMessage to a01.
    When: place reads it.
    Then: it is a StartCall of writer that resumes it, naming a01."""
    tool_input = {"to": "a01", "message": "Which version?"}
    got = placed(
        "PreToolUse", RUN, tool_name="SendMessage", tool_input=tool_input, tool_use_id="t2"
    )
    assert got.what == StartCall("writer", True, "Which version?", True, "t2", "a01")


@pytest.mark.supports("test_a_resume_a_route_makes_due_adds_a_start_and_moves_the_run")
def test_a_subagents_call_after_its_resume_lies_on_the_resumed_start() -> None:
    """Given: write's Run with writer's Start tied to a01, ended, and its resumed Start tied to
    a01 too.
    When: place reads a01's Bash call.
    Then: it lies on the resumed Start."""
    ended = dataclasses.replace(WRITER, results=("written",), ended=True)
    resumed = dataclasses.replace(WRITER, tool_use_id="t2", resumed=True)
    got = placed(
        "PreToolUse",
        d.run(starts=(ended, resumed), due=()),
        agent_id="a01",
        tool_name="Bash",
        tool_input={"command": "git log --oneline"},
    )
    assert got.start == resumed


@pytest.mark.supports("test_a_start_whose_subagent_starts_after_its_post_tool_use_is_held")
def test_the_post_tool_use_of_an_agent_call_ties_its_agent() -> None:
    """Given: the PostToolUse of the Agent call toolu_1, naming agentId a01.
    When: place reads it.
    Then: it is an AgentPosted of toolu_1 and a01."""
    got = placed(
        "PostToolUse",
        RUN,
        tool_name="Agent",
        tool_use_id="toolu_1",
        tool_response={"agentId": "a01"},
    )
    assert got.what == AgentPosted("toolu_1", "a01")


@pytest.mark.supports("test_a_result_is_added_for_the_subagents_start")
def test_the_post_tool_use_of_result_py_is_a_result() -> None:
    """Given: a01's PostToolUse of `result.py writer written`, which gave 0.
    When: place reads it.
    Then: it is a ResultPosted of writer's `written`."""
    command = f"{d.RESULT} writer written"
    got = placed(
        "PostToolUse",
        RUN,
        agent_id="a01",
        tool_name="Bash",
        tool_input={"command": command},
        tool_response={"stdout": "", "stderr": ""},
    )
    assert got.what == ResultPosted("writer", "written")


@pytest.mark.supports("test_an_end_with_no_result_is_stopped_with_its_last_steps_sentence")
@pytest.mark.parametrize("name, agent", [("Stop", None), ("SubagentStop", "a01")])
def test_an_end_is_an_end_asked_with_its_last_message(name: str, agent: Any) -> None:
    """Given: the main conversation's Stop, or a01's SubagentStop, with its last message.
    When: place reads it.
    Then: it is an EndAsked with the message, from the Start the agent is tied to."""
    got = placed(name, RUN, agent_id=agent, last_message="Done.")
    assert got.what == EndAsked("Done.")
    assert got.start == (WRITER if agent else None)


@pytest.mark.supports("test_calls_outside_the_run_go_unchecked")
def test_an_event_with_no_run_lies_outside() -> None:
    """Given: a conversation with no Run, and the main conversation's Bash call.
    When: place reads it.
    Then: it lies on no Run."""
    got = placed("PreToolUse", tool_name="Bash", tool_input={"command": "git status"})
    assert got.runs == ()


@pytest.mark.supports("test_calls_outside_the_run_go_unchecked")
def test_an_untied_subagents_event_lies_outside() -> None:
    """Given: write's Run, and a Bash call of a02, which no Start ties.
    When: place reads it.
    Then: it lies on no Run, from no Start."""
    got = placed("PreToolUse", RUN, agent_id="a02", tool_name="Bash", tool_input={"command": "ls"})
    assert got.runs == () and got.start is None


@pytest.mark.supports("test_another_plugins_skill_no_move_names_is_checked_as_a_call")
def test_a_skill_call_of_another_plugin_is_a_call() -> None:
    """Given: write's Run, with writer's start due.
    When: place reads the main conversation's Skill call of lint:check.
    Then: it is a ToolCall of the Skill tool, on write's Run."""
    tool_input = {"skill": "lint:check", "args": ""}
    run = d.run()
    got = placed("PreToolUse", run, tool_name="Skill", tool_input=tool_input)
    assert got.what == ToolCall(Call("Skill", tool_input, d.REPO, d.REPO))
    assert got.runs == (run,)

