"""The unit cases of domain/lanes/gives_result.py: a role ends only once it gave one of the results
it takes by result.py."""

from __future__ import annotations

import pytest
from domain.event import COMMAND, Call
from domain.lanes import PASSES, End, Where
from domain.lanes.gives_result import LANE_TYPE
from lane_parts import REVIEWER_END, ROOT, WRITER_END

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)

WHERE = Where(ROOT, ROOT)
RESULT_PY = "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py"


@pytest.mark.supports("test_lay_print_shows_each_step_as_it_will_read_with_the_routes_and_an_id")
def test_the_sentence_of_one_result_names_its_command():
    """Given a gives_result Lane of writer that takes `written`
    When its sentence is made
    Then it reads as the walkthrough shows for writer's step 4"""
    assert LANE_TYPE.sentence("writer", ("written",)) == WRITER_END


@pytest.mark.supports("test_lay_print_shows_each_step_as_it_will_read_with_the_routes_and_an_id")
def test_the_sentence_of_two_results_joins_their_commands_by_or():
    """Given a gives_result Lane of reviewer that takes `more` and `good`
    When its sentence is made
    Then it reads as the walkthrough shows for reviewer's step 2"""
    assert LANE_TYPE.sentence("reviewer", ("more", "good")) == REVIEWER_END


@pytest.mark.supports("test_lay_print_shows_each_step_as_it_will_read_with_the_routes_and_an_id")
def test_it_lets_the_role_run_the_command_of_each_result():
    """Given a gives_result Lane of reviewer that takes `more` and `good`
    When its commands are asked
    Then they are `result.py reviewer more` and `result.py reviewer good`"""
    expected = (f"{RESULT_PY} reviewer more", f"{RESULT_PY} reviewer good")
    assert LANE_TYPE.commands("reviewer", ("more", "good")) == expected


@pytest.mark.supports("test_lay_print_refuses_a_lane_of_a_type_there_isnt")
def test_a_lane_that_takes_no_result_cant_stand():
    """Given a gives_result Lane that takes nothing
    When its faults are asked
    Then it has one"""
    assert LANE_TYPE.faults("writer", (), False)


@pytest.mark.supports("test_lay_print_refuses_a_lane_of_a_type_there_isnt")
def test_a_result_of_more_than_one_word_cant_stand():
    """Given a gives_result Lane that takes `not yet`
    When its faults are asked
    Then it has one naming `not yet`"""
    faults = LANE_TYPE.faults("writer", ("not yet",), False)
    assert faults and "not yet" in faults[0]


@pytest.mark.supports("test_a_call_that_keeps_every_lane_of_its_role_passes")
def test_an_end_after_a_result_it_takes_passes():
    """Given a gives_result Lane of reviewer that takes `more` and `good`
    When reviewer ends having given `good`
    Then the end passes"""
    assert LANE_TYPE.check_end(("more", "good"), End("reviewer", "", result="good"), WHERE).passes


@pytest.mark.supports("test_an_end_with_no_result_is_held_with_the_sentence_of_the_last_step")
def test_an_end_with_no_result_fails():
    """Given a gives_result Lane of reviewer that takes `more` and `good`
    When reviewer ends with `No more entries` and no result given
    Then the end fails"""
    assert not LANE_TYPE.check_end(
        ("more", "good"), End("reviewer", "No more entries"), WHERE
    ).passes


@pytest.mark.supports("test_an_end_with_no_result_is_held_with_the_sentence_of_the_last_step")
def test_an_end_after_a_result_it_doesnt_take_fails():
    """Given a gives_result Lane of reviewer that takes `more` and `good`
    When reviewer ends having given `done`
    Then the end fails"""
    assert not LANE_TYPE.check_end(
        ("more", "good"), End("reviewer", "", result="done"), WHERE
    ).passes


@pytest.mark.supports(
    "test_up_again_on_unchanged_steps_proposes_each_step_without_the_text_lane_laid"
)
def test_a_step_that_holds_the_sentence_says_it_already():
    """Given writer's step 4 that ends with its gives_result sentence
    When it's asked whether the step says the sentence
    Then it does"""
    step = f"4. Reply with the entries you wrote. {WRITER_END}"
    assert LANE_TYPE.said(step, "writer", ("written",))


@pytest.mark.supports("test_a_call_that_keeps_every_lane_of_its_role_passes")
def test_a_call_isnt_held():
    """Given a gives_result Lane of writer that takes `written`
    When writer runs `git log --oneline`
    Then the Lane gives PASSES"""
    call = Call(COMMAND, command="git log --oneline")
    assert LANE_TYPE.check_call(("written",), call, {}, WHERE, ()) == PASSES
