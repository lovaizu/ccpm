"""The unit cases of domain/results.py: whether a result is one that the role may give, and which
Result a run of result.py gave, from the moment that tells it ran, through `may_give` and
`given`."""

from __future__ import annotations

import pytest
from domain.event import COMMAND, RAN, Call
from domain.results import given, may_give
from domain.run_record import Result
from lane_parts import PLUGIN_ROOT, event, laid_set, run, two_skills, writer_running

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)


def ran(command: str, agent: str = "", role: str = "", failed: bool = False):
    """The moment that tells the command ran, by the subagent where one is given."""
    return event(RAN, agent=agent, role=role, call=Call(COMMAND, command=command), failed=failed)


def result_command(role: str, result: str) -> str:
    return f"python3 {PLUGIN_ROOT}/hooks/lane/result.py {role} {result}"


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
def test_a_subagents_run_of_result_py_that_gave_0_gives_its_result_for_its_start():
    """Given a Run in which writer, subagent a1 of Start 1, runs
    When the moment tells that a1's `result.py writer written` ran and gave 0
    Then it gave the Result `written` of a1 for Start 1"""
    moment = ran(result_command("writer", "written"), "a1", "changelog:writer")
    assert given(moment, laid_set(), [writer_running()]) == Result("writer", "written", "a1", 1)


@pytest.mark.supports("test_the_skills_own_result_where_a_move_starts_no_more_ends_the_run")
def test_the_main_conversations_run_of_result_py_gives_the_result_of_the_skill_it_names():
    """Given the Runs of `write` and of `review` in the conversation
    When the moment tells that the main conversation's `result.py review good` ran and gave 0
    Then it gave the Result `good` of the skill `review`, of no Start"""
    runs = [run(), run(skill="review")]
    moment = ran(result_command("review", "good"))
    assert given(moment, two_skills(), runs) == Result("review", "good", "", 0)


@pytest.mark.supports(
    "test_result_py_refuses_a_result_that_the_role_may_not_give_with_those_it_may"
)
def test_a_run_of_result_py_that_gave_other_than_0_gives_no_result():
    """Given a Run in which writer, subagent a1, runs
    When the moment tells that a1's `result.py writer done` ran and failed
    Then it gave no Result"""
    moment = ran(result_command("writer", "done"), "a1", "changelog:writer", failed=True)
    assert given(moment, laid_set(), [writer_running()]) is None


@pytest.mark.supports("test_an_end_with_no_result_is_held_with_the_sentence_of_the_last_step")
def test_result_py_at_the_end_of_a_longer_command_gives_no_result():
    """Given a Run in which writer, subagent a1, runs
    When the moment tells that a1's `git status && result.py writer written` ran and gave 0
    Then it gave no Result, as the command isn't result.py's word for word"""
    moment = ran(f"git status && {result_command('writer', 'written')}", "a1", "changelog:writer")
    assert given(moment, laid_set(), [writer_running()]) is None


@pytest.mark.supports("test_a_subagent_of_a_role_that_no_start_of_the_run_ties_goes_unchecked")
def test_a_run_of_result_py_by_a_subagent_that_no_start_ties_gives_no_result():
    """Given a Run whose Start 1 ties writer's subagent a1
    When the moment tells that subagent a7's `result.py writer written` ran and gave 0
    Then it gave no Result, as no Start ties a7"""
    moment = ran(result_command("writer", "written"), "a7", "changelog:writer")
    assert given(moment, laid_set(), [writer_running()]) is None
