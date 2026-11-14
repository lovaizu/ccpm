"""The unit cases of hooks/lane/hook.py, the guard's entry: each hook event of the recorded runs of
Claude Code read into the guard's form, through `read`, each decision given in the form Claude
Code's hooks reference sets, through `answer`, and a payload it can't read stopped, through
`main`."""

from __future__ import annotations

import json
from typing import Any

import hook
import pytest
from claude_code import (
    COMPACT,
    REFERENCE,
    RUN,
    SEND_MESSAGE,
    SKILL,
    SKILL_WHILE_SUBAGENT,
    TASK_STOP,
    WORKTREE,
    line,
)
from domain.event import (
    BEGUN,
    CALL,
    COMMAND,
    ENDS,
    ENTER,
    OTHER,
    RAN,
    REACHED,
    READ,
    RESUME,
    START,
    STOP_TASK,
    TURN_ENDS,
    TYPED,
    WRITE,
)
from domain.event import SKILL as SKILL_CALL
from domain.fault import Fault
from domain.guard import LET_THROUGH, Decision

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)

ENV = {"CLAUDE_PROJECT_DIR": "/repo"}


def payload(record: str, event: str, **fields: Any) -> str:
    """The payload of the recorded line, with `<repo>` as /repo and the fields given, as JSON."""
    given = line(record, event)["payload"]
    given.update(fields)
    return json.dumps(given).replace("<repo>", "/repo")


@pytest.mark.supports("test_a_call_that_keeps_every_lane_of_its_role_passes")
def test_a_subagents_bash_call_reads_as_a_call_of_a_command_by_it():
    """Given the recorded PreToolUse of writer's `git log --oneline`
    When it's read
    Then it's a CALL of COMMAND `git log --oneline` by writer's subagent, at /repo"""
    name, moment = hook.read(payload(RUN, "writer runs git log"), ENV)
    assert (name, moment.moment, moment.role, moment.root) == (
        "PreToolUse",
        CALL,
        "changelog:writer",
        "/repo",
    )
    assert moment.agent and moment.call and moment.call.kind == COMMAND
    assert (
        moment.call.command == line(RUN, "writer runs git log")["payload"]["tool_input"]["command"]
    )


@pytest.mark.supports("test_a_write_of_a_file_that_no_write_only_lane_takes_is_stopped")
def test_a_write_call_reads_as_a_write_of_its_path():
    """Given the recorded PreToolUse of writer's Write of CHANGELOG.md
    When it's read
    Then it's a CALL of WRITE of that path"""
    _, moment = hook.read(payload(RUN, "writer writes CHANGELOG.md"), ENV)
    given = line(RUN, "writer writes CHANGELOG.md")["payload"]["tool_input"]["file_path"]
    assert moment.call and (moment.call.kind, moment.call.path) == (
        WRITE,
        given.replace("<repo>", "/repo"),
    )


@pytest.mark.supports("test_a_write_of_a_file_that_no_write_only_lane_takes_is_stopped")
def test_an_edit_call_reads_as_a_write_of_its_path():
    """Given a PreToolUse of an Edit, its input as the hooks reference gives it
    When it's read
    Then it's a CALL of WRITE of its `file_path`"""
    shown = line(REFERENCE, "an Edit call's input")
    text = payload(
        RUN,
        "the main conversation runs lay.py print",
        tool_name="Edit",
        tool_input=shown["tool_input"],
    )
    _, moment = hook.read(text, ENV)
    assert moment.call and (moment.call.kind, moment.call.path) == (WRITE, "/path/to/file.txt")


@pytest.mark.supports(
    "test_a_read_of_a_path_that_read_never_keeps_unread_is_stopped_and_its_bang_part_passes"
)
def test_a_read_call_reads_as_a_read_of_its_path():
    """Given a PreToolUse of a Read, its input as the hooks reference gives it
    When it's read
    Then it's a CALL of READ of its `file_path`"""
    shown = line(REFERENCE, "a Read call's input")
    text = payload(RUN, "writer runs git log", tool_name="Read", tool_input=shown["tool_input"])
    _, moment = hook.read(text, ENV)
    assert moment.call and (moment.call.kind, moment.call.path) == (READ, "/path/to/file.txt")


@pytest.mark.supports("test_a_start_that_the_moves_dont_open_is_stopped_with_the_moves")
def test_an_agent_call_reads_as_a_start_of_its_type_with_its_text():
    """Given the recorded PreToolUse of the main conversation's start of writer
    When it's read
    Then it's a CALL of START of `changelog:writer` with its prompt, by the main conversation"""
    recorded = line(RUN, "the main conversation starts writer in the background")["payload"]
    _, moment = hook.read(
        payload(RUN, "the main conversation starts writer in the background"), ENV
    )
    assert moment.agent == "" and moment.call
    assert (moment.call.kind, moment.call.role, moment.call.text) == (
        START,
        "changelog:writer",
        recorded["tool_input"]["prompt"],
    )


@pytest.mark.supports("test_a_resume_that_the_moves_dont_open_is_stopped_with_the_moves")
def test_a_send_message_call_reads_as_a_resume_of_its_subagent():
    """Given the recorded PreToolUse of a resume by SendMessage
    When it's read
    Then it's a CALL of RESUME of the subagent `to` names, with its message"""
    recorded = line(SEND_MESSAGE, "the main conversation resumes helper by SendMessage")["payload"]
    _, moment = hook.read(
        payload(SEND_MESSAGE, "the main conversation resumes helper by SendMessage"), ENV
    )
    assert moment.call and (moment.call.kind, moment.call.agent) == (
        RESUME,
        recorded["tool_input"]["to"],
    )


@pytest.mark.supports(
    "test_a_subagent_that_ends_with_no_result_as_task_stop_stopped_it_opens_no_route"
)
def test_a_task_stop_call_reads_as_a_stop_of_its_subagent():
    """Given the recorded PreToolUse of TaskStop
    When it's read
    Then it's a CALL of STOP_TASK of `task_id`'s subagent"""
    _, moment = hook.read(
        payload(TASK_STOP, "the main conversation stops sleeper by TaskStop"), ENV
    )
    assert moment.call and (moment.call.kind, moment.call.agent) == (STOP_TASK, "a84016c8746847ffa")


@pytest.mark.supports(
    "test_an_ai_that_called_up_by_the_skill_tool_lays_by_its_own_run_of_lay_write"
)
def test_a_skill_call_reads_as_a_call_of_its_skill_with_its_args():
    """Given the recorded PreToolUse of a call of `lane:up` by the Skill tool
    When it's read
    Then it's a CALL of SKILL of `lane:up` with its args"""
    recorded = line(SKILL, "the main conversation calls lane:up by the Skill tool")["payload"]
    _, moment = hook.read(
        payload(SKILL, "the main conversation calls lane:up by the Skill tool"), ENV
    )
    assert moment.call and (moment.call.kind, moment.call.skill, moment.call.args) == (
        SKILL_CALL,
        recorded["tool_input"]["skill"],
        recorded["tool_input"].get("args", ""),
    )


@pytest.mark.supports("test_a_run_value_holds_each_subagent_to_the_value_of_its_own_start")
def test_an_enter_worktree_call_reads_as_enter():
    """Given the recorded PreToolUse of EnterWorktree
    When it's read
    Then it's a CALL of ENTER"""
    _, moment = hook.read(
        payload(WORKTREE, "the main conversation enters a worktree by EnterWorktree"), ENV
    )
    assert moment.call and moment.call.kind == ENTER


@pytest.mark.supports(
    "test_the_command_gives_the_first_start_and_each_result_gives_the_next_until_no_more"
)
def test_a_typed_command_of_a_skill_reads_as_typed_with_its_command_and_args():
    """Given the recorded UserPromptExpansion of the typed `/lane:up changelog`
    When it's read
    Then it's TYPED of the command `lane:up` with the args `changelog`"""
    _, moment = hook.read(payload(RUN, "the typed /lane:up expands"), ENV)
    assert (moment.moment, moment.command, moment.args) == (TYPED, "lane:up", "changelog")


@pytest.mark.supports("test_a_persons_yes_lays_the_proposal_and_validation_passes")
def test_a_persons_prompt_reads_as_typed_with_its_words():
    """Given the recorded UserPromptSubmit of the person's `yes`
    When it's read
    Then it's TYPED with the prompt `yes` and no command"""
    _, moment = hook.read(payload(RUN, "a person replies yes"), ENV)
    assert (moment.moment, moment.prompt, moment.command) == (TYPED, "yes", "")


@pytest.mark.supports(
    "test_the_command_gives_the_first_start_and_each_result_gives_the_next_until_no_more"
)
def test_a_task_notification_reads_as_reached_with_its_subagent_status_and_result():
    """Given the recorded prompt that tells writer's end
    When it's read
    Then it's REACHED of writer's subagent, `completed`, with its result"""
    _, moment = hook.read(payload(RUN, "writer's end reaches the main conversation"), ENV)
    assert (moment.moment, moment.agent, moment.status) == (
        REACHED,
        "a6253d9786133b1e1",
        "completed",
    )
    assert moment.message.startswith("written")


@pytest.mark.supports(
    "test_a_subagent_that_ends_with_no_result_as_task_stop_stopped_it_opens_no_route"
)
def test_a_task_notification_of_a_stopped_subagent_reads_as_killed():
    """Given the recorded prompt that tells the end of a subagent that TaskStop stopped
    When it's read
    Then it's REACHED with the status `killed`"""
    recorded = "the stopped sleeper's notification reaches the main conversation"
    _, moment = hook.read(payload(TASK_STOP, recorded), ENV)
    assert (moment.moment, moment.status) == (REACHED, "killed")


@pytest.mark.supports(
    "test_the_command_gives_the_first_start_and_each_result_gives_the_next_until_no_more"
)
def test_a_start_that_ran_reads_as_begun_of_the_subagent_its_response_names():
    """Given the recorded PostToolUse of writer's start in the background
    When it's read
    Then it's BEGUN of the `agentId` that its response names, of `changelog:writer`"""
    _, moment = hook.read(payload(RUN, "writer runs in the background"), ENV)
    assert (moment.moment, moment.agent, moment.role) == (
        BEGUN,
        "a6253d9786133b1e1",
        "changelog:writer",
    )


@pytest.mark.supports(
    "test_a_subagent_whose_start_comes_after_its_agent_calls_post_tool_use_is_tied_to_its_start"
)
def test_a_start_whose_post_tool_use_comes_before_its_subagent_starts_reads_as_begun():
    """Given the recorded PostToolUse of sleeper's start that Claude Code 2.1.325 sent before
    sleeper's SubagentStart
    When it's read
    Then it's BEGUN of the `agentId` that its response names, of `rec:sleeper`"""
    recorded = line(SKILL_WHILE_SUBAGENT, "sleeper runs in the background")["payload"]
    _, moment = hook.read(payload(SKILL_WHILE_SUBAGENT, "sleeper runs in the background"), ENV)
    assert (moment.moment, moment.agent, moment.role) == (
        BEGUN,
        recorded["tool_response"]["agentId"],
        "rec:sleeper",
    )


@pytest.mark.supports(
    "test_a_background_subagents_calls_after_a_later_prompt_are_held_by_its_own_start"
)
def test_a_subagents_call_after_a_later_prompt_reads_as_its_own_by_its_agent_id():
    """Given the recorded PreToolUse of sleeper's `echo after-sleep`, which carries the
    `prompt_id` of a prompt typed after sleeper started
    When it's read
    Then it's a CALL by sleeper's `agent_id`, of `rec:sleeper`"""
    event = "sleeper runs `echo after-sleep`"
    recorded = line(SKILL_WHILE_SUBAGENT, event)["payload"]
    _, moment = hook.read(payload(SKILL_WHILE_SUBAGENT, event), ENV)
    assert (moment.moment, moment.agent, moment.role) == (
        CALL,
        recorded["agent_id"],
        "rec:sleeper",
    )


@pytest.mark.supports("test_a_call_that_keeps_every_lane_of_its_role_passes")
def test_an_event_with_no_agent_id_reads_as_the_main_conversations():
    """Given the recorded PreToolUse of the main conversation's `lay.py print`
    When it's read
    Then it's a CALL with no agent and no role"""
    _, moment = hook.read(payload(RUN, "the main conversation runs lay.py print"), ENV)
    assert (moment.moment, moment.agent, moment.role) == (CALL, "", "")


@pytest.mark.supports(
    "test_compact_while_a_subagent_runs_lets_the_summary_end_and_holds_the_subagent_after_it"
)
def test_the_compaction_summarys_end_reads_as_ends_with_no_role():
    """Given the recorded SubagentStop of the compaction's summary, whose `agent_type` is empty
    When it's read
    Then it's ENDS of its `agent_id`, with no role"""
    recorded = line(COMPACT, "the compaction's summary ends")["payload"]
    _, moment = hook.read(payload(COMPACT, "the compaction's summary ends"), ENV)
    assert (moment.moment, moment.agent, moment.role) == (ENDS, recorded["agent_id"], "")


@pytest.mark.supports(
    "test_an_end_that_starts_no_line_with_a_line_that_its_command_printed_is_held"
)
def test_a_command_that_ran_reads_as_ran_with_what_it_printed():
    """Given the recorded PostToolUse of `git log` that ran
    When it's read
    Then it's RAN of that command, with its stdout as what it printed, not failed"""
    recorded = line(RUN, "git log ran")["payload"]
    _, moment = hook.read(payload(RUN, "git log ran"), ENV)
    assert (moment.moment, moment.failed) == (RAN, False)
    assert moment.printed == recorded["tool_response"]["stdout"]


@pytest.mark.supports("test_an_end_with_no_result_is_held_with_the_sentence_of_the_last_step")
def test_a_command_that_failed_reads_as_ran_and_failed():
    """Given the recorded PostToolUseFailure of a command
    When it's read
    Then it's RAN and failed"""
    _, moment = hook.read(payload(RUN, "a command fails"), ENV)
    assert (moment.moment, moment.failed) == (RAN, True)


@pytest.mark.supports("test_an_end_with_no_result_is_held_with_the_sentence_of_the_last_step")
def test_a_subagent_stop_reads_as_ends_and_again_once_stopped_before():
    """Given the recorded SubagentStop of writer, and the one after its end was stopped
    When each is read
    Then each is ENDS with writer's last message, the second `again`"""
    _, first = hook.read(payload(RUN, "writer ends"), ENV)
    _, again = hook.read(payload(RUN, "writer ends again after its end was stopped"), ENV)
    assert (first.moment, first.again, again.again) == (ENDS, False, True)


@pytest.mark.supports("test_the_main_conversation_may_stop_while_a_subagent_runs")
def test_a_stop_reads_as_the_turn_ending_with_each_subagent_that_runs():
    """Given the recorded Stop while writer runs
    When it's read
    Then it's TURN_ENDS, naming writer's subagent as one that runs"""
    recorded = line(RUN, "the main conversation stops while writer runs")["payload"]
    _, moment = hook.read(payload(RUN, "the main conversation stops while writer runs"), ENV)
    assert moment.moment == TURN_ENDS
    assert moment.running == tuple(task["id"] for task in recorded["background_tasks"])


@pytest.mark.supports("test_after_compact_the_run_goes_on_with_the_start_due")
def test_an_event_lane_holds_nothing_on_reads_as_other():
    """Given the recorded SessionStart, and PreCompact of /compact
    When each is read
    Then each is OTHER"""
    _, started = hook.read(payload(RUN, "session started"), ENV)
    _, compacting = hook.read(payload(COMPACT, "the person compacts the conversation"), ENV)
    assert (started.moment, compacting.moment) == (OTHER, OTHER)


@pytest.mark.supports(
    "test_a_call_that_the_guard_cant_check_is_stopped_with_why_and_who_must_fix_it"
)
def test_a_payload_that_isnt_json_raises_a_fault_with_lane_to_fix_it():
    """Given a payload `not json`
    When it's read
    Then a Fault says so, with Lane to fix it"""
    with pytest.raises(Fault) as raised:
        hook.read("not json", ENV)
    assert raised.value.who == "Lane"


@pytest.mark.supports(
    "test_a_command_not_word_for_word_is_stopped_with_the_steps_sentence_and_the_commands"
)
def test_a_stop_of_a_call_is_a_pretooluse_denial_with_its_reason():
    """Given a stop with `changelog: Run only `git log --oneline`.`
    When it's answered on PreToolUse
    Then the answer exits 0 with a denial whose reason is that text"""
    code, out, _ = hook.answer("PreToolUse", Decision(stop=True, said="changelog: Run only x."))
    specific = json.loads(out)["hookSpecificOutput"]
    assert code == 0 and specific["permissionDecision"] == "deny"
    assert specific["permissionDecisionReason"] == "changelog: Run only x."


@pytest.mark.supports(
    "test_the_main_conversation_stopping_while_a_start_is_due_and_none_runs_is_held"
)
def test_a_stop_of_the_turns_end_is_a_block_with_its_reason():
    """Given a stop with reviewer's start
    When it's answered on Stop
    Then the answer exits 0 with `decision` `block` and that reason"""
    code, out, _ = hook.answer("Stop", Decision(stop=True, said="changelog: Start reviewer."))
    assert (code, json.loads(out)) == (
        0,
        {"decision": "block", "reason": "changelog: Start reviewer."},
    )


@pytest.mark.supports("test_an_end_with_no_result_is_held_with_the_sentence_of_the_last_step")
def test_a_stop_of_a_subagents_end_is_a_block_with_its_reason():
    """Given a stop with the sentence of reviewer's last step
    When it's answered on SubagentStop
    Then the answer exits 0 with `decision` `block` and that reason"""
    code, out, _ = hook.answer("SubagentStop", Decision(stop=True, said="changelog: End by x."))
    assert (code, json.loads(out)) == (0, {"decision": "block", "reason": "changelog: End by x."})


@pytest.mark.supports(
    "test_the_command_gives_the_first_start_and_each_result_gives_the_next_until_no_more"
)
def test_context_beside_a_prompt_is_additional_context():
    """Given a decision that lets the prompt through with writer's start as context
    When it's answered on UserPromptSubmit
    Then the answer exits 0 with that context as `additionalContext`"""
    code, out, _ = hook.answer("UserPromptSubmit", Decision(context="changelog: Start writer."))
    specific = json.loads(out)["hookSpecificOutput"]
    assert code == 0 and specific == {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": "changelog: Start writer.",
    }


@pytest.mark.supports("test_a_call_that_keeps_every_lane_of_its_role_passes")
def test_letting_through_with_nothing_to_add_exits_0_and_prints_nothing():
    """Given a decision that lets the call through with nothing to add
    When it's answered on PreToolUse
    Then the answer exits 0 and prints nothing"""
    assert hook.answer("PreToolUse", LET_THROUGH) == (0, "", "")


@pytest.mark.supports(
    "test_kept_results_that_dont_follow_the_routes_stop_the_command_with_who_must_fix_it"
)
def test_a_stop_of_a_typed_command_blocks_the_prompt_with_its_reason():
    """Given a stop that names reviewer's `good` and who must fix it
    When it's answered on UserPromptExpansion
    Then the answer exits 0 with `decision` `block` and that reason"""
    code, out, _ = hook.answer("UserPromptExpansion", Decision(stop=True, said="fix it"))
    assert code == 0 and json.loads(out)["decision"] == "block"


@pytest.mark.supports(
    "test_a_call_that_the_guard_cant_check_is_stopped_with_why_and_who_must_fix_it"
)
def test_a_payload_that_cant_be_read_is_answered_with_a_stop_and_who_must_fix_it():
    """Given a payload `not json`
    When the guard runs on it
    Then it gives other than 0, or a stop, saying that Lane must fix it"""
    code, out, err = hook.main("not json", ENV)
    assert code != 0 or "deny" in out
    assert "Lane" in out + err
