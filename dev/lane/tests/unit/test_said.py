"""The unit cases of domain/said.py: the words that the guard gives, through `moves`, `gave`,
`ended_without`, `stop`, and `cant_check`, each line as the walkthrough shows it."""

from __future__ import annotations

import pytest
from domain.laid_set import NO_MORE, START, Move
from domain.said import cant_check, ended_without, gave, moves, stop

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)

CARRY = {"writer": "Carry out your steps", "reviewer": "Carry out your steps"}
RESULT = "python3 /repo/changelog/hooks/lane/result.py writer written"


@pytest.mark.supports(
    "test_the_command_gives_the_first_start_and_each_result_gives_the_next_until_no_more"
)
def test_one_start_due_reads_as_the_walkthrough_shows():
    """Given the move that starts writer, with `Carry out your steps`
    When the moves are told
    Then they read ``changelog: Start `changelog:writer` with `Carry out your steps`.``"""
    told = moves("changelog", (Move(START, "writer"),), CARRY)
    assert told == "changelog: Start `changelog:writer` with `Carry out your steps`."


@pytest.mark.supports(
    "test_several_moves_let_the_skills_steps_choose_among_them_and_stop_any_other"
)
def test_several_moves_name_each_start_and_start_no_more():
    """Given the moves start writer and start no more
    When the moves are told
    Then they name writer's start with its text and `Start no more subagents.`"""
    told = moves("changelog", (Move(START, "writer"), Move(NO_MORE)), CARRY)
    assert "Start `changelog:writer` with `Carry out your steps`" in told
    assert "Start no more subagents." in told


@pytest.mark.supports(
    "test_the_command_gives_the_first_start_and_each_result_gives_the_next_until_no_more"
)
def test_a_result_given_reads_as_the_walkthrough_shows():
    """Given writer gave `written`, and reviewer's start is due
    When it's told
    Then it reads ``changelog: writer gave `written`. Start `changelog:reviewer` with `Carry out
    your steps`.``"""
    told = gave("changelog", "writer", "written", (Move(START, "reviewer"),), CARRY)
    expected = (
        "changelog: writer gave `written`. Start `changelog:reviewer` with `Carry out your steps`."
    )
    assert told == expected


@pytest.mark.supports(
    "test_the_command_gives_the_first_start_and_each_result_gives_the_next_until_no_more"
)
def test_the_last_result_reads_start_no_more():
    """Given reviewer gave `good`, and the move starts no more
    When it's told
    Then it reads ``changelog: reviewer gave `good`. Start no more subagents.``"""
    told = gave("changelog", "reviewer", "good", (Move(NO_MORE),), CARRY)
    assert told == "changelog: reviewer gave `good`. Start no more subagents."


@pytest.mark.supports(
    "test_a_subagent_that_ends_with_no_result_as_task_stop_stopped_it_opens_no_route"
)
def test_an_end_with_no_result_names_the_role():
    """Given writer's subagent ended with no Result
    When it's told
    Then it names writer, and says it gave no result"""
    told = ended_without("changelog", "writer")
    assert told.startswith("changelog: ") and "writer" in told and "no result" in told.lower()


@pytest.mark.supports(
    "test_a_command_not_word_for_word_is_stopped_with_the_steps_sentence_and_the_commands"
)
def test_a_stop_with_commands_reads_as_the_walkthrough_shows():
    """Given the sentence `Run only `git log --oneline`.` and the commands writer may run
    When the stop is told
    Then it reads the sentence, and on the next line each command, as the walkthrough shows"""
    told = stop("changelog", "Run only `git log --oneline`.", ("git log --oneline", RESULT), "")
    assert told == (
        "changelog: Run only `git log --oneline`.\n"
        f"The commands you may run, each word for word: `git log --oneline`, `{RESULT}`."
    )


@pytest.mark.supports("test_an_end_with_no_result_is_held_with_the_sentence_of_the_last_step")
def test_a_stop_with_no_commands_is_the_sentence_alone():
    """Given the sentence of reviewer's step 2 and no command reviewer may run but result.py's,
    which the sentence names
    When the stop is told with no commands
    Then it reads the sentence alone, after the plugin's name"""
    sentence = "End by running `python3 /repo/changelog/hooks/lane/result.py reviewer good`."
    assert stop("changelog", sentence, (), "") == f"changelog: {sentence}"


@pytest.mark.supports(
    "test_an_end_whose_check_of_the_plugins_own_gives_other_than_0_is_held_with_what_it_printed"
)
def test_a_stop_with_what_a_command_printed_holds_it():
    """Given an ends_checked sentence, and its command printed `no entry for --lines`
    When the stop is told
    Then it holds the sentence and `no entry for --lines`"""
    told = stop("changelog", "End once `python3 check.py` gives 0.", (), "no entry for --lines\n")
    assert "End once `python3 check.py` gives 0." in told and "no entry for --lines" in told


@pytest.mark.supports(
    "test_a_call_that_the_guard_cant_check_is_stopped_with_why_and_who_must_fix_it"
)
def test_what_cant_be_checked_says_why_and_who_must_fix_it():
    """Given why, `hooks/lanes.json isn't JSON`, and who, `the plugin's maker`
    When it's told
    Then it names both"""
    told = cant_check("changelog", "hooks/lanes.json isn't JSON", "the plugin's maker")
    assert "hooks/lanes.json isn't JSON" in told and "the plugin's maker" in told
