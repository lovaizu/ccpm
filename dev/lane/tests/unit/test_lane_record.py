"""The unit cases of hooks/lane/record.py: runs, one for each class of a conversation's record, and
add, one for each class of entries it adds, with the transitions of the record that Lane's list of
Claude Code's states brings about: a run added at the skill's call, its folder at the next event,
each later entry after the ones before, a start kept with its prompt and the steps given for it, and
two conversations apart."""

from __future__ import annotations

import os
import stat

import lane_entries
import pytest
from record import Entry, add, runs

RUN: Entry = {"kind": "run", "run": "r1", "skill": "log:up", "words": "1.2.0"}
FOLDER: Entry = {"kind": "folder", "run": "r1", "plugin_root": "/plugins/log"}
START: Entry = lane_entries.start("toolu_1")
TIE: Entry = lane_entries.tie("toolu_1", "a1")


@pytest.mark.supports("test_another_conversation_in_the_repository_is_held_to_no_run_of_the_first")
def test_a_conversation_with_no_record_has_no_run():
    """Given no record of the conversation
    When Lane reads its runs
    Then there's none"""
    assert runs("session-1") == []


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
def test_a_run_added_at_the_skills_call_has_no_folder():
    """Given a conversation with no record
    When Lane adds a run of log:up with the words 1.2.0
    Then the record holds that run, with no folder and its one entry"""
    add("session-1", [RUN])
    [run] = runs("session-1")
    assert (run.id, run.session_id, run.skill, run.words) == ("r1", "session-1", "log:up", "1.2.0")
    assert run.plugin_root is None
    assert run.entries == [RUN]


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
def test_a_folder_added_after_the_run_gives_the_run_its_folder():
    """Given a run with no folder
    When Lane adds the run's folder
    Then the run has that folder"""
    add("session-1", [RUN])
    add("session-1", [FOLDER])
    assert runs("session-1")[0].plugin_root == "/plugins/log"


@pytest.mark.supports("test_the_results_of_two_subagents_are_both_kept")
def test_entries_added_at_once_and_after_keep_their_order():
    """Given a run with its folder
    When Lane adds a start and its tie in one write, and then a result
    Then the run's entries are the run, its folder, the start, the tie, and the result, in order"""
    result: Entry = {"kind": "result", "run": "r1", "agent_id": "a1", "result": "written"}
    add("session-1", [RUN, FOLDER])
    add("session-1", [START, TIE])
    add("session-1", [result])
    assert runs("session-1")[0].entries == [RUN, FOLDER, START, TIE, result]


@pytest.mark.supports(
    "test_a_role_with_no_fixed_steps_takes_them_from_the_plugins_adapter_for_each_start"
)
def test_a_start_is_kept_with_its_prompt_and_the_steps_given_for_it():
    """Given a run with its folder
    When Lane adds a start with the prompt that the main conversation gave it and the steps that
    the plugin's adapter of the rules gave
    Then the run's last entry holds both as they were given"""
    given: Entry = {
        **START,
        "prompt": "Write docs/changes/1.2.0.md.",
        "steps": [{"name": "write", "rules": [{"type": "writes", "paths": ["docs/"]}]}],
    }
    add("session-1", [RUN, FOLDER])
    add("session-1", [given])
    assert runs("session-1")[0].entries[-1] == given


@pytest.mark.supports("test_the_plugins_command_typed_again_once_its_run_ended_adds_a_new_run")
def test_two_runs_of_one_conversation_each_hold_their_own_entries():
    """Given a run r1 of log:up for 1.2.0 with a start
    When Lane adds a run r2 of log:up for 1.3.0, and a start of it
    Then the conversation has both runs, in order, each with its own entries"""
    other: Entry = {"kind": "run", "run": "r2", "skill": "log:up", "words": "1.3.0"}
    writer: Entry = {"kind": "start", "run": "r2", "role": "log:writer", "tool_use_id": "toolu_2"}
    add("session-1", [RUN, FOLDER, START])
    add("session-1", [other, writer])
    first, second = runs("session-1")
    assert (first.words, second.words) == ("1.2.0", "1.3.0")
    assert first.entries == [RUN, FOLDER, START]
    assert second.entries == [other, writer]


@pytest.mark.supports("test_another_conversation_in_the_repository_is_held_to_no_run_of_the_first")
def test_each_conversation_has_a_record_of_its_own():
    """Given a run of the conversation session-1
    When Lane reads the runs of session-2
    Then there's none"""
    add("session-1", [RUN])
    assert runs("session-2") == []


@pytest.mark.supports("test_after_compact_the_run_goes_on_with_its_starts_due")
def test_the_record_lies_in_the_systems_temporary_folder(temp: str):
    """Given the system's temporary folder of the case
    When Lane adds a run
    Then the record lies in that folder, and nowhere else"""
    add("session-1", [RUN])
    assert os.listdir(temp)


@pytest.mark.supports("test_after_compact_the_run_goes_on_with_its_starts_due")
def test_a_record_that_cant_be_written_is_refused(temp: str):
    """Given a system's temporary folder that can't be written
    When Lane adds a run
    Then it refuses with OSError"""
    os.chmod(temp, stat.S_IRUSR | stat.S_IXUSR)
    try:
        with pytest.raises(OSError):
            add("session-1", [RUN])
    finally:
        os.chmod(temp, stat.S_IRWXU)
