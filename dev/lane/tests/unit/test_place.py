"""The unit cases of place.py, how the guard reads each hook event as Lane's data and places it,
through `place`: each kind of What an event is, and each way it lies on its Runs and its Start, in
a Run, aside, or outside every Run."""

from __future__ import annotations

import dataclasses
from typing import Any

import lane_data as d
import pytest
from form import Move
from place import (
    AgentPosted,
    Call,
    EndAsked,
    Notification,
    PrintPosted,
    Prompt,
    ResultPosted,
    SkillCall,
    StartCall,
    ToolCall,
    place,
)
from run_record import Shown
from runs import Approval

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
    assert got.what == SkillCall("changelog", "write", "person", "0.2.0")


@pytest.mark.supports("test_an_ai_lays_by_its_own_run_of_lay")
def test_a_skill_tool_call_is_an_ais_skill_call() -> None:
    """Given: the main conversation's PreToolUse of the Skill tool on lane:up with changelog.
    When: place reads it.
    Then: it is a SkillCall of lane's up by an AI, with the words changelog."""
    got = placed(
        "PreToolUse", tool_name="Skill", tool_input={"skill": "lane:up", "args": "changelog"}
    )
    assert got.what == SkillCall("lane", "up", "ai", "changelog")


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


@pytest.mark.supports("test_what_print_showed_is_kept_in_ups_run")
def test_the_post_tool_use_of_print_is_what_it_showed() -> None:
    """Given: up's Run, and the PostToolUse of lay.py print, whose output names ID b9fd8fd8.
    When: place reads it.
    Then: it is a PrintPosted of b9fd8fd8 with the output."""
    up = d.run(skill="up", due=())
    output = "Routes of write...\nID: b9fd8fd8\nReply yes to lay these into changelog."
    got = placed(
        "PostToolUse",
        up,
        tool_name="Bash",
        tool_input={"command": "python3 /lane/scripts/lay.py print changelog < /tmp/p.json"},
        tool_response={"stdout": output, "stderr": ""},
    )
    assert got.what == PrintPosted("b9fd8fd8", output)


@pytest.mark.supports("test_an_ais_run_keeps_a_persons_waiting_proposal")
def test_what_print_showed_lies_on_the_run_whose_call_came_last() -> None:
    """Given: two Runs of up, the first a person's, the second an AI's, called after it.
    When: place reads the PostToolUse of lay.py print, whose output names ID c0ffee00.
    Then: it lies on the AI's Run alone."""
    first = d.run(skill="up", id="r1", due=())
    second = d.run(skill="up", id="r2", by="ai", due=())
    got = placed(
        "PostToolUse",
        first,
        second,
        tool_name="Bash",
        tool_input={"command": "python3 /lane/scripts/lay.py print changelog < /tmp/p.json"},
        tool_response={"stdout": "ID: c0ffee00\n", "stderr": ""},
    )
    assert got.runs == (second,)


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


@pytest.mark.supports("test_the_run_stands_aside_while_another_plugins_skill_runs")
def test_the_main_conversations_event_while_every_run_stands_aside_lies_outside() -> None:
    """Given: write's Run, standing aside, and the main conversation's Bash call.
    When: place reads it.
    Then: it lies on no Run."""
    aside = d.run(aside=True)
    assert placed("PreToolUse", aside, tool_name="Bash", tool_input={"command": "ls"}).runs == ()


@pytest.mark.supports("test_the_move_after_another_plugins_skill_brings_the_run_back")
def test_the_main_conversations_start_due_on_an_aside_run_lies_on_it() -> None:
    """Given: write's Run, standing aside with writer's start due after lint's run hands back.
    When: place reads the main conversation's Agent call of changelog:writer.
    Then: it lies on write's Run."""
    aside = d.run(aside=True)
    tool_input = {"subagent_type": "changelog:writer", "prompt": "Carry out your steps"}
    got = placed("PreToolUse", aside, tool_name="Agent", tool_input=tool_input, tool_use_id="t1")
    assert got.runs == (aside,)


@pytest.mark.supports("test_the_move_after_another_plugins_skill_brings_the_run_back")
def test_the_main_conversations_start_not_due_on_an_aside_run_lies_outside() -> None:
    """Given: write's Run, standing aside with writer's start due after lint's run hands back.
    When: place reads the main conversation's Agent call of changelog:reviewer.
    Then: it lies on no Run."""
    aside = d.run(aside=True)
    tool_input = {"subagent_type": "changelog:reviewer", "prompt": "Carry out your steps"}
    got = placed("PreToolUse", aside, tool_name="Agent", tool_input=tool_input, tool_use_id="t1")
    assert got.runs == ()


@pytest.mark.supports("test_another_plugins_skill_no_move_names_is_checked_as_a_call")
def test_a_skill_call_of_another_plugin_that_no_move_names_is_a_call() -> None:
    """Given: write's Run, with writer's start due.
    When: place reads the main conversation's Skill call of lint:check, which no move names.
    Then: it is a ToolCall of the Skill tool, on write's Run."""
    tool_input = {"skill": "lint:check", "args": ""}
    run = d.run()
    got = placed("PreToolUse", run, tool_name="Skill", tool_input=tool_input)
    assert got.what == ToolCall(Call("Skill", tool_input, d.REPO, d.REPO))
    assert got.runs == (run,)


@pytest.mark.supports("test_the_run_stands_aside_while_another_plugins_skill_runs")
def test_a_skill_call_of_another_plugin_that_a_move_names_is_a_skill_call() -> None:
    """Given: write's Run, with the call of lint:check due.
    When: place reads the main conversation's Skill call of lint:check.
    Then: it is a SkillCall of lint's check by an AI."""
    run = d.run(due=(Move("call", skill="lint:check"),))
    tool_input = {"skill": "lint:check", "args": ""}
    got = placed("PreToolUse", run, tool_name="Skill", tool_input=tool_input)
    assert got.what == SkillCall("lint", "check", "ai", "")


@pytest.mark.supports("test_an_ais_run_keeps_a_persons_waiting_proposal")
def test_a_call_of_write_lies_on_the_run_of_up_that_showed_its_id() -> None:
    """Given: two Runs of up, the first a person's that showed b9fd8fd8, the second an AI's that
    showed c0ffee00.
    When: place reads the Bash call `lay.py write changelog b9fd8fd8`.
    Then: it lies on the person's Run alone."""
    first = d.run(skill="up", id="r1", shown=(Shown("r1", "b9fd8fd8", "..."),), due=())
    second = d.run(
        skill="up",
        id="r2",
        by="ai",
        shown=(Shown("r2", "c0ffee00", "..."),),
        approvals=(Approval("c0ffee00", "ai"),),
        due=(),
    )
    command = "python3 /lane/scripts/lay.py write changelog b9fd8fd8"
    got = placed("PreToolUse", first, second, tool_name="Bash", tool_input={"command": command})
    assert got.runs == (first,)


@pytest.mark.supports("test_a_lay_chained_after_another_command_waits_for_the_persons_reply")
@pytest.mark.parametrize(
    "command",
    [
        "python3 /lane/scripts/lay.py write changelog b9fd8fd8; echo laid",
        "python3 /lane/scripts/lay.py write changelog b9fd8fd8&&echo laid",
        "true;lay.py write changelog b9fd8fd8",
    ],
    ids=["a command after it", "a command after it, with no space", "a command before it"],
)
def test_a_call_of_write_chained_with_another_command_lies_on_the_run_that_showed_its_id(
    command: str,
) -> None:
    """Given: two Runs of up, the first a person's that showed b9fd8fd8, the second an AI's that
    showed c0ffee00.
    When: place reads a Bash call that runs `lay.py write changelog b9fd8fd8` chained with another
    command.
    Then: it lies on the person's Run alone, as the ID is read apart from the command beside it."""
    first = d.run(skill="up", id="r1", shown=(Shown("r1", "b9fd8fd8", "..."),), due=())
    second = d.run(skill="up", id="r2", by="ai", shown=(Shown("r2", "c0ffee00", "..."),), due=())
    got = placed("PreToolUse", first, second, tool_name="Bash", tool_input={"command": command})
    assert got.runs == (first,)
