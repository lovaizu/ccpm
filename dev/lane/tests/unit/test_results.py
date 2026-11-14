"""The unit cases of domain/results.py: whether a result is one that the role may give, and the
Result recorded for the Start of the subagent that gave it, through `may_give` and `record`."""

from __future__ import annotations

import pytest
from domain.event import COMMAND, Call
from domain.fault import Fault
from domain.results import may_give, record
from domain.run_record import Result
from lane_parts import PLUGIN_ROOT, laid_set, run, writer_running

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)


def result_call(role: str, result: str) -> Call:
    return Call(COMMAND, command=f"python3 {PLUGIN_ROOT}/hooks/lane/result.py {role} {result}")


@pytest.mark.supports(
    "test_result_py_refuses_a_result_that_the_role_may_not_give_with_those_it_may"
)
def test_the_results_a_role_may_give_are_those_its_gives_result_lane_takes():
    """Given the walkthrough's laid set
    When the results of reviewer, and of a role with no gives_result Lane, are asked
    Then reviewer's are `more` and `good`, and the other's none"""
    assert may_give(laid_set(), "reviewer") == ("more", "good")
    assert may_give(laid_set(), "helper") == ()


@pytest.mark.supports(
    "test_the_command_gives_the_first_start_and_each_result_gives_the_next_until_no_more"
)
def test_a_result_the_role_may_give_is_recorded_for_the_start_of_its_subagent():
    """Given a Run in which writer, subagent a1 of Start 1, ran result.py, as the guard let through
    When writer's `written` is recorded
    Then the Run holds the Result `written` of a1 for Start 1"""
    given = writer_running()
    given.calls.append(("a1", result_call("writer", "written")))
    recorded = record(given, laid_set(), "writer", "written")
    assert recorded == Result("writer", "written", "a1", 1)
    assert given.results == [recorded]


@pytest.mark.supports("test_the_skills_own_result_where_a_move_starts_no_more_ends_the_run")
def test_the_skills_result_is_recorded_for_the_main_conversation():
    """Given a Run in which the main conversation ran `result.py write good`
    When the skill's `good` is recorded
    Then the Run holds the Result `good` of the main conversation, of no Start"""
    given = run()
    given.calls.append(("", result_call("write", "good")))
    assert record(given, laid_set(), "write", "good") == Result("write", "good", "", 0)


@pytest.mark.supports(
    "test_result_py_refuses_a_result_that_the_role_may_not_give_with_those_it_may"
)
def test_a_result_the_role_may_not_give_raises_a_fault_naming_those_it_may():
    """Given a Run in which reviewer ran `result.py reviewer done`
    When reviewer's `done` is recorded
    Then a Fault names `more` and `good`, and the Run holds no Result"""
    given = run()
    given.calls.append(("a2", result_call("reviewer", "done")))
    with pytest.raises(Fault, match="more") as raised:
        record(given, laid_set(), "reviewer", "done")
    assert "good" in raised.value.why and given.results == []


@pytest.mark.supports("test_an_end_with_no_result_is_held_with_the_sentence_of_the_last_step")
def test_a_result_with_no_call_of_result_py_in_the_run_raises_a_fault():
    """Given a Run in which reviewer ran `git status && result.py reviewer good`, which the Run
    holds as no call of result.py
    When reviewer's `good` is recorded
    Then a Fault says no call of result.py by reviewer is in the Run"""
    given = writer_running()
    command = f"git status && python3 {PLUGIN_ROOT}/hooks/lane/result.py reviewer good"
    given.calls.append(("a2", Call(COMMAND, command=command)))
    with pytest.raises(Fault, match="result.py"):
        record(given, laid_set(), "reviewer", "good")
