"""The unit cases of domain/lanes/__init__.py: which lane types there are, and the check of a call
or an end against every Lane of a role, through `types`, `type_of`, `may_run`, `check_call`, and
`check_end`."""

from __future__ import annotations

import pytest
from domain.event import COMMAND, WRITE, Call
from domain.fault import Fault
from domain.laid_set import Lane
from domain.lanes import PASSES, End, Where, check_call, check_end, may_run, type_of, types
from lane_example import TYPES
from lane_parts import LANES, PLUGIN_ROOT, ROOT

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)

WHERE = Where(ROOT, ROOT)
WRITER = tuple(lane for lane in LANES if lane.role == "writer")
RESULT = f"python3 {PLUGIN_ROOT}/hooks/lane/result.py writer written"


@pytest.mark.supports(
    "test_lay_types_gives_each_type_with_what_it_takes_the_steps_it_suits_and_its_sentence"
)
def test_there_are_six_lane_types():
    """Given Lane's lane types
    When they are asked for
    Then they are run_only, write_only, read_never, names_printed, ends_checked, and
    gives_result, each under its own name"""
    found = types()
    assert set(found) == set(TYPES)
    assert all(each.name == name for name, each in found.items())


@pytest.mark.supports("test_lay_print_refuses_a_lane_of_a_type_there_isnt")
def test_a_type_there_isnt_raises_a_fault_naming_each_type_there_is():
    """Given Lane's lane types
    When the type `run_never` is asked for
    Then a Fault names `run_never` and `run_only`"""
    with pytest.raises(Fault, match="run_never") as raised:
        type_of("run_never")
    assert "run_only" in raised.value.why


@pytest.mark.supports(
    "test_a_command_not_word_for_word_is_stopped_with_the_steps_sentence_and_the_commands"
)
def test_the_commands_a_role_may_run_are_those_of_each_lane_with_its_plugins_folder():
    """Given writer's Lanes of the walkthrough
    When the commands writer may run are asked
    Then they are `git log --oneline` and result.py's command with the plugin's folder, as the
    walkthrough's stop shows"""
    assert may_run(WRITER, PLUGIN_ROOT) == ("git log --oneline", RESULT)


@pytest.mark.supports(
    "test_a_command_not_word_for_word_is_stopped_with_the_steps_sentence_and_the_commands"
)
def test_a_command_named_by_two_lanes_is_given_once():
    """Given two run_only Lanes of writer that both take `git log --oneline`
    When the commands writer may run are asked
    Then `git log --oneline` is given once"""
    twice = (*WRITER, Lane("writer", 1, "agents/writer.md", "run_only", ("git log --oneline",), ""))
    assert may_run(twice, PLUGIN_ROOT).count("git log --oneline") == 1


@pytest.mark.supports("test_a_call_that_keeps_every_lane_of_its_role_passes")
def test_a_call_that_keeps_every_lane_gives_none_and_passes():
    """Given writer's Lanes of the walkthrough
    When writer runs `git log --oneline`
    Then no Lane is broken"""
    call = Call(COMMAND, command="git log --oneline")
    assert check_call(WRITER, call, {}, WHERE, PLUGIN_ROOT) == (None, PASSES)


@pytest.mark.supports(
    "test_a_command_not_word_for_word_is_stopped_with_the_steps_sentence_and_the_commands"
)
def test_a_call_that_breaks_a_lane_gives_that_lane():
    """Given writer's Lanes of the walkthrough
    When writer runs `git status`
    Then the Lane of step 2 is broken, with each command writer may run"""
    lane, verdict = check_call(WRITER, Call(COMMAND, command="git status"), {}, WHERE, PLUGIN_ROOT)
    assert lane == WRITER[0] and not verdict.passes and RESULT in verdict.may


@pytest.mark.supports("test_a_write_of_a_file_that_no_write_only_lane_takes_is_stopped")
def test_a_call_that_breaks_a_later_lane_gives_that_lane():
    """Given writer's Lanes of the walkthrough
    When writer writes NOTES.md
    Then the Lane of step 3 is broken"""
    lane, _ = check_call(WRITER, Call(WRITE, path=f"{ROOT}/NOTES.md"), {}, WHERE, PLUGIN_ROOT)
    assert lane == WRITER[1]


@pytest.mark.supports(
    "test_a_call_that_the_guard_cant_check_is_stopped_with_why_and_who_must_fix_it"
)
def test_a_lane_of_a_type_there_isnt_raises_a_fault():
    """Given a Lane of writer of the type `run_never`
    When writer runs `git status`
    Then the check raises a Fault"""
    odd = (Lane("writer", 2, "agents/writer.md", "run_never", ("ls",), ""),)
    with pytest.raises(Fault):
        check_call(odd, Call(COMMAND, command="git status"), {}, WHERE, PLUGIN_ROOT)


@pytest.mark.supports("test_an_end_with_no_result_is_held_with_the_sentence_of_the_last_step")
def test_an_end_with_no_result_gives_the_gives_result_lane():
    """Given writer's Lanes of the walkthrough
    When writer ends with no result given
    Then the Lane of step 4 is broken"""
    lane, verdict = check_end(WRITER, End("writer", "Done."), WHERE)
    assert lane == WRITER[2] and not verdict.passes


@pytest.mark.supports(
    "test_the_command_gives_the_first_start_and_each_result_gives_the_next_until_no_more"
)
def test_an_end_that_keeps_every_lane_gives_none_and_passes():
    """Given writer's Lanes of the walkthrough
    When writer ends having given `written`
    Then no Lane is broken"""
    assert check_end(WRITER, End("writer", "Done.", result="written"), WHERE) == (None, PASSES)
