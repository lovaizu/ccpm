"""The unit cases of domain/lanes/run_only.py: a role runs only the commands that its step names,
word for word, or another command that it may run."""

from __future__ import annotations

import pytest
from domain.event import COMMAND, WRITE, Call
from domain.lanes import PASSES, End, Where
from domain.lanes.run_only import LANE_TYPE
from lane_parts import PLUGIN_ROOT, ROOT

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)

WHERE = Where(ROOT, ROOT)
RESULT = f"python3 {PLUGIN_ROOT}/hooks/lane/result.py writer written"
MAY_RUN = ("git log --oneline", RESULT)


@pytest.mark.supports(
    "test_lay_types_gives_each_type_with_what_it_takes_the_steps_it_suits_and_its_sentence"
)
def test_the_sentence_of_one_command_names_it_in_backticks():
    """Given a run_only Lane that takes `git log --oneline`
    When its sentence is made
    Then it reads `Run only `git log --oneline`.`, as the walkthrough shows"""
    assert LANE_TYPE.sentence("writer", ("git log --oneline",)) == "Run only `git log --oneline`."


@pytest.mark.supports(
    "test_up_again_after_the_steps_changed_shows_the_lanes_of_the_steps_as_they_now_read"
)
def test_the_sentence_of_two_commands_joins_them_by_or():
    """Given a run_only Lane that takes `git log --oneline` and `git show {commit}`
    When its sentence is made
    Then it reads `Run only `git log --oneline` or `git show {commit}`.`"""
    sentence = LANE_TYPE.sentence("writer", ("git log --oneline", "git show {commit}"))
    assert sentence == "Run only `git log --oneline` or `git show {commit}`."


@pytest.mark.supports("test_lay_print_refuses_a_lane_of_a_type_there_isnt")
def test_a_lane_that_takes_no_command_cant_stand():
    """Given a run_only Lane that takes nothing
    When its faults are asked
    Then it has one"""
    assert LANE_TYPE.faults("writer", (), False)


@pytest.mark.supports("test_lay_print_shows_each_step_as_it_will_read_with_the_routes_and_an_id")
def test_a_lane_that_takes_a_command_stands():
    """Given a run_only Lane that takes `git log --oneline`
    When its faults are asked
    Then it has none"""
    assert LANE_TYPE.faults("writer", ("git log --oneline",), False) == []


@pytest.mark.supports(
    "test_up_again_on_unchanged_steps_proposes_each_step_without_the_text_lane_laid"
)
def test_a_step_that_holds_the_sentence_word_for_word_says_it_already():
    """Given a step that ends with `Run only `git log --oneline`.`
    When it's asked whether the step says the sentence
    Then it does"""
    step = "2. Read the commits with `git log --oneline`. Run only `git log --oneline`."
    assert LANE_TYPE.said(step, "writer", ("git log --oneline",))


@pytest.mark.supports(
    "test_up_again_on_unchanged_steps_proposes_each_step_without_the_text_lane_laid"
)
def test_a_step_that_says_the_rule_in_other_words_says_it_not():
    """Given a step that says `Run nothing but git log.`
    When it's asked whether the step says the sentence
    Then it doesn't"""
    step = "2. Read the commits with `git log --oneline`. Run nothing but git log."
    assert not LANE_TYPE.said(step, "writer", ("git log --oneline",))


@pytest.mark.supports("test_lay_print_shows_each_step_as_it_will_read_with_the_routes_and_an_id")
def test_the_commands_it_lets_the_role_run_are_those_it_takes():
    """Given a run_only Lane that takes `git log --oneline` and `git show {commit}`
    When its commands are asked
    Then they are those two, in order"""
    takes = ("git log --oneline", "git show {commit}")
    assert LANE_TYPE.commands("writer", takes) == takes


@pytest.mark.supports("test_a_call_that_keeps_every_lane_of_its_role_passes")
def test_a_command_that_the_role_may_run_passes():
    """Given a run_only Lane that takes `git log --oneline`
    When writer runs `git log --oneline`
    Then the call passes"""
    call = Call(COMMAND, command="git log --oneline")
    assert LANE_TYPE.check_call(("git log --oneline",), call, {}, WHERE, MAY_RUN).passes


@pytest.mark.supports("test_a_call_that_keeps_every_lane_of_its_role_passes")
def test_the_command_of_result_py_passes_as_one_the_role_may_run():
    """Given a run_only Lane that takes `git log --oneline`, and writer may run result.py
    When writer runs `python3 <plugin>/hooks/lane/result.py writer written`
    Then the call passes"""
    call = Call(COMMAND, command=RESULT)
    assert LANE_TYPE.check_call(("git log --oneline",), call, {}, WHERE, MAY_RUN).passes


@pytest.mark.supports(
    "test_a_command_not_word_for_word_is_stopped_with_the_steps_sentence_and_the_commands"
)
def test_a_command_not_word_for_word_fails_with_each_command_the_role_may_run():
    """Given a run_only Lane that takes `git log --oneline`
    When writer runs `git -C /repo log --oneline`
    Then the call fails, giving each command writer may run"""
    call = Call(COMMAND, command="git -C /repo log --oneline")
    verdict = LANE_TYPE.check_call(("git log --oneline",), call, {}, WHERE, MAY_RUN)
    assert (verdict.passes, verdict.may) == (False, MAY_RUN)


@pytest.mark.supports("test_a_call_that_keeps_every_lane_of_its_role_passes")
def test_a_call_that_runs_no_command_isnt_held():
    """Given a run_only Lane that takes `git log --oneline`
    When writer writes CHANGELOG.md
    Then the Lane gives PASSES"""
    call = Call(WRITE, path="CHANGELOG.md")
    assert LANE_TYPE.check_call(("git log --oneline",), call, {}, WHERE, MAY_RUN) == PASSES


@pytest.mark.supports("test_a_call_that_keeps_every_lane_of_its_role_passes")
def test_an_end_isnt_held():
    """Given a run_only Lane that takes `git log --oneline`
    When writer ends
    Then the Lane gives PASSES"""
    assert LANE_TYPE.check_end(("git log --oneline",), End("writer", "Done."), WHERE) == PASSES
