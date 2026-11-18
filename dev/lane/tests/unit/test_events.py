"""The unit cases of events.py, Claude Code's hooks as the guard meets them, through `read_event`,
`write_answer`, and `hook_entries`: an event read by its kind and caller, each input it refuses,
and each kind of event's answer, stopped or not."""

from __future__ import annotations

import json
import os

import lane_data as d
import pytest
from events import Answer, NotAnEvent, hook_entries, read_event, write_answer

HOOKS = os.path.join(os.path.dirname(d.__file__), *[".."] * 3, "plugins", "lane", "hooks")


@pytest.mark.supports("test_a_call_that_breaks_a_lane_gets_its_steps_sentence")
def test_a_subagents_call_is_read_with_its_agent() -> None:
    """Given: a PreToolUse of a Bash call with an agent_id and agent_type.
    When: read_event reads it.
    Then: the Event holds the name, session, cwd, agent, tool, and its input."""
    text = d.payload(
        "PreToolUse",
        agent_id="a01",
        agent_type="changelog:writer",
        tool_name="Bash",
        tool_input={"command": "git log --oneline"},
        tool_use_id="toolu_1",
    )
    event = read_event(text)
    assert (event.name, event.session_id, event.cwd) == ("PreToolUse", d.SESSION, d.REPO)
    assert (event.agent_id, event.agent_type) == ("a01", "changelog:writer")
    assert event.tool_input == {"command": "git log --oneline"}


@pytest.mark.supports("test_the_turns_end_while_a_start_is_due_is_stopped")
def test_a_main_conversations_event_has_no_agent() -> None:
    """Given: a Stop with no agent_id, and its last message.
    When: read_event reads it.
    Then: the Event's agent_id and tool fields are None, and its last message is kept."""
    event = read_event(d.payload("Stop", last_assistant_message="Shall I go on?"))
    assert event.agent_id is None and event.tool_name is None
    assert event.last_message == "Shall I go on?"


@pytest.mark.supports("test_up_shows_the_walkthroughs_proposal")
def test_a_typed_command_is_read_with_its_name_and_words() -> None:
    """Given: a UserPromptExpansion of /lane:up changelog.
    When: read_event reads it.
    Then: the Event holds the command's name and the words after it."""
    text = d.payload(
        "UserPromptExpansion",
        prompt="/lane:up changelog",
        command_name="lane:up",
        command_args="changelog",
    )
    event = read_event(text)
    assert (event.command_name, event.command_args) == ("lane:up", "changelog")


@pytest.mark.supports("test_a_call_the_guard_cant_check_is_stopped_with_who_must_fix_it")
@pytest.mark.parametrize(
    "text",
    [
        "not json",
        "[]",
        json.dumps({"session_id": d.SESSION}),
        json.dumps({"hook_event_name": "Stop"}),
    ],
    ids=["not JSON", "not an object", "no hook_event_name", "no session_id"],
)
def test_input_that_isnt_an_event_is_refused(text: str) -> None:
    """Given: standard input that isn't a hook event in Claude Code's form.
    When: read_event reads it.
    Then: it raises NotAnEvent."""
    with pytest.raises(NotAnEvent):
        read_event(text)


@pytest.mark.supports("test_a_call_that_breaks_a_lane_gets_its_steps_sentence")
def test_a_stopped_call_is_denied_with_the_words() -> None:
    """Given: a PreToolUse, and the guard's answer that stops it with words.
    When: write_answer writes it.
    Then: the hook exits 0 with a PreToolUse permissionDecision of deny, its reason the words."""
    out = write_answer(d.event("PreToolUse", tool_name="Bash"), Answer(True, "Run only."))
    specific = json.loads(out.stdout)["hookSpecificOutput"]
    assert out.code == 0
    assert specific["permissionDecision"] == "deny"
    assert specific["permissionDecisionReason"] == "Run only."


@pytest.mark.supports("test_calls_that_keep_every_lane_go_through")
def test_a_call_let_through_says_nothing() -> None:
    """Given: a PreToolUse, and an answer that doesn't stop it and says nothing.
    When: write_answer writes it.
    Then: the hook exits 0, denies nothing, and writes nothing to standard error."""
    out = write_answer(d.event("PreToolUse", tool_name="Bash"), Answer(False, ""))
    assert out.code == 0 and "deny" not in out.stdout and out.stderr == ""


@pytest.mark.supports("test_an_end_with_no_result_is_stopped_with_its_last_steps_sentence")
@pytest.mark.parametrize("name", ["Stop", "SubagentStop"])
def test_a_stopped_end_is_blocked_with_the_words(name: str) -> None:
    """Given: a Stop or SubagentStop, and an answer that stops it with words.
    When: write_answer writes it.
    Then: the hook gives the decision block, its reason the words."""
    output = json.loads(write_answer(d.event(name), Answer(True, "End by running.")).stdout)
    assert output["decision"] == "block" and output["reason"] == "End by running."


@pytest.mark.supports("test_the_walkthroughs_run_moves_in_the_order_the_user_set")
@pytest.mark.parametrize("name", ["UserPromptSubmit", "UserPromptExpansion", "PostToolUse"])
def test_words_that_dont_stop_reach_the_model(name: str) -> None:
    """Given: an event that the guard answers with the moves due, without stopping it.
    When: write_answer writes it.
    Then: the words reach the model as the event's additionalContext."""
    words = "changelog: Start `changelog:writer` with `Carry out your steps`."
    output = json.loads(write_answer(d.event(name), Answer(False, words)).stdout)
    assert output["hookSpecificOutput"] == {"hookEventName": name, "additionalContext": words}


@pytest.mark.supports("test_kept_results_off_the_routes_stop_the_command")
@pytest.mark.parametrize("name", ["UserPromptSubmit", "UserPromptExpansion"])
def test_a_stopped_prompt_is_blocked_with_the_words(name: str) -> None:
    """Given: a person's prompt, and an answer that stops it with why and who must fix it.
    When: write_answer writes it.
    Then: the hook gives the decision block, its reason the words."""
    output = json.loads(write_answer(d.event(name), Answer(True, "Fix records.")).stdout)
    assert output["decision"] == "block" and output["reason"] == "Fix records."


@pytest.mark.supports("test_yes_lays_the_proposal_into_the_plugin")
def test_lanes_entries_run_the_guard_on_each_event_it_needs() -> None:
    """Given: Lane's code.
    When: hook_entries gives Lane's entries of hooks.json.
    Then: eight events, PostToolUseFailure and SubagentStart among them as S4 draws, each running
    hook.py by python3 with onFailure block."""
    entries = hook_entries()
    events = {"UserPromptSubmit", "UserPromptExpansion", "PreToolUse", "PostToolUse", "Stop"}
    assert set(entries) == {*events, "SubagentStop", "PostToolUseFailure", "SubagentStart"}
    for groups in entries.values():
        ((hook,),) = [group["hooks"] for group in groups]
        assert (hook["command"], hook["onFailure"]) == ("python3", "block")
        assert hook["args"] == ["${CLAUDE_PLUGIN_ROOT}/hooks/lane/hook.py"]
