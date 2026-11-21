"""The unit cases of rounds/course.py, which Round a deliverable takes next: one for each row of
next_of's decision table, in the order its contract gives, each row's boundaries of LIMIT in each
stage, the last Round picked among several, and each transition that a run brings: a point kept as
an open decision and then answered, a generator's made with no evaluator yet, an evaluator's
findings, a stage at LIMIT whose findings left the orchestrator keeps as open decisions, which
then waits on the sign-off before the answer, and a pause that leaves a Round with its Cut and no
result, of the generator or of the evaluator, at Round 1 and at LIMIT, which spends no Round."""

from __future__ import annotations

import os
from collections.abc import Sequence
from typing import Any

import pytest
import rn_files
from rounds.course import LIMIT, Done, Next, next_of
from rounds.files import Round

COMMAND = rn_files.COMMAND


@pytest.fixture
def results(tmp_path: Any) -> str:
    """The folder where the case writes each role's result, to read it back as its use does."""
    return str(tmp_path)


def read_back(folder: str, name: str, value: Any) -> Any:
    """The value written as JSON in the folder and read back from its file."""
    path = os.path.join(folder, f"{name}.json")
    rn_files.write_json(path, value)
    return rn_files.read_json(path)


def rounds(folder: str, *each: tuple[str, int, Any, Any]) -> list[Done]:
    """The command's Rounds, each by its stage, number, generator's result, and evaluator's
    result, None where the role wrote none, each result read back from JSON."""
    found: list[Done] = []
    for stage, number, made, judged in each:
        place = rn_files.round_of(os.path.join(folder, "run"), COMMAND, stage, number)
        generator = None if made is None else read_back(folder, f"g-{stage}-{number}", made)
        evaluator = None if judged is None else read_back(folder, f"e-{stage}-{number}", judged)
        found.append(Done(Round(place, COMMAND, stage, number), generator, evaluator))
    return found


def node(good: bool | Sequence[str] = False, open_decision: bool = False, folder: str = "") -> Any:
    """The command's open node, of the kind light, its conditions good as given, N1 holding an
    answered decision and, where `open_decision`, an open one, as a point or a finding left is
    kept; read back from JSON where a folder is given."""
    decisions = [rn_files.decision("the tax rate", "with each invoice", "user")]
    if open_decision:
        decisions.append(rn_files.decision("a comma in a line", None))
    given = rn_files.decided(
        rn_files.open_node(rn_files.COMMAND_NAME, COMMAND, "light", ["invoicer/lines.py"], good),
        {"N1": decisions},
    )
    return read_back(folder, "node", given) if folder else given


MADE_ALL = rn_files.made([("N1", ["print"]), ("N2", ["print"]), ("N3", ["print"])], [COMMAND])
POINTED = rn_files.point("Should a line's quantity default to 1?")
SHORT = rn_files.judged([("N2", ["print"]), ("N3", ["print"])], [("N1", "They print it.")])
GOOD = rn_files.judged([("N1", ["print"]), ("N2", ["print"]), ("N3", ["print"])])


# The answer, where a decision of the node is open.


@pytest.mark.supports("test_a_deliverable_whose_point_waits_on_the_user_gets_no_cut")
def test_an_open_decision_waits_on_the_answer_after_a_point(results: str):
    """Given the command whose generator gave a point in content-1, kept as an open decision of N1
    When what it waits on is asked
    Then it waits on the answer, with no stage, resuming nothing"""
    done = rounds(results, ("content", 1, POINTED, None))
    assert next_of(node(open_decision=True, folder=results), done, False) == Next(
        "answer", None, False
    )


@pytest.mark.supports("test_a_deliverable_whose_point_waits_on_the_user_gets_no_cut")
def test_an_open_decision_waits_on_the_answer_before_the_evaluator_due(results: str):
    """Given the command made in content-1 with no evaluator yet, and an open decision of N1, as
    the orchestrator keeps a point that the user settles
    When what it waits on is asked
    Then it waits on the answer, the first row that holds"""
    done = rounds(results, ("content", 1, MADE_ALL, None))
    assert next_of(node(open_decision=True, folder=results), done, False) == Next(
        "answer", None, False
    )


@pytest.mark.supports("test_a_deliverable_whose_point_waits_on_the_user_gets_no_cut")
def test_an_open_decision_waits_on_the_answer_with_no_round_yet(results: str):
    """Given the command with no Round, and an open decision of N1 that the plan left for the user
    When what it waits on is asked
    Then it waits on the answer"""
    assert next_of(node(open_decision=True, folder=results), [], False) == Next(
        "answer", None, False
    )


# The generator resuming the last Round, where its last result is `point`.


@pytest.mark.supports(
    "test_a_resumed_generator_after_its_answer_ends_with_made_and_the_evaluator_is_due"
)
def test_a_point_answered_resumes_the_generator_in_its_round(results: str):
    """Given the command whose generator gave a point in content-1, now answered by the user
    When what it waits on is asked
    Then the generator resumes the last Round, of the stage content"""
    done = rounds(results, ("content", 1, POINTED, None))
    assert next_of(node(folder=results), done, False) == Next("generator", "content", True)


@pytest.mark.supports(
    "test_a_resumed_generator_after_its_answer_ends_with_made_and_the_evaluator_is_due"
)
def test_a_point_answered_in_a_later_round_resumes_that_one(results: str):
    """Given the command judged short in content-1, whose generator gave a point in content-2, now
    answered
    When what it waits on is asked
    Then the generator resumes content-2, the last Round, and not the first"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", 2, POINTED, None))
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next(
        "generator", "content", True
    )


@pytest.mark.supports(
    "test_a_resumed_generator_after_its_answer_ends_with_made_and_the_evaluator_is_due"
)
def test_a_point_answered_in_a_refactor_round_resumes_it(results: str):
    """Given the guide-like command, refactored, judged good in content-1, whose generator gave a
    point in refactor-1, now answered
    When what it waits on is asked
    Then the generator resumes refactor-1"""
    done = rounds(results, ("content", 1, MADE_ALL, GOOD), ("refactor", 1, POINTED, None))
    assert next_of(node(True, folder=results), done, True) == Next("generator", "refactor", True)


# The evaluator in the last Round, where the generator made it and the evaluator wrote nothing.


@pytest.mark.supports("test_a_generators_made_makes_the_evaluator_due_in_the_same_round")
def test_a_round_made_with_no_evaluator_yet_waits_on_the_evaluator(results: str):
    """Given the command made in content-1, no evaluator's result yet
    When what it waits on is asked
    Then the evaluator in the last Round, of the stage content"""
    done = rounds(results, ("content", 1, MADE_ALL, None))
    assert next_of(node(folder=results), done, False) == Next("evaluator", "content", False)


@pytest.mark.supports("test_a_generators_made_makes_the_evaluator_due_in_the_same_round")
def test_a_refactor_round_made_waits_on_its_evaluator(results: str):
    """Given the command judged good in content-1 and made in refactor-1, no evaluator yet
    When what it waits on is asked
    Then the evaluator in refactor-1"""
    done = rounds(results, ("content", 1, MADE_ALL, GOOD), ("refactor", 1, MADE_ALL, None))
    assert next_of(node(True, folder=results), done, True) == Next("evaluator", "refactor", False)


@pytest.mark.supports("test_a_pause_stops_the_evaluator_too")
def test_a_round_made_after_an_earlier_one_judged_waits_on_its_evaluator(results: str):
    """Given the command judged short in content-1 and made in content-2, its evaluator stopped by
    a pause with no result
    When what it waits on is asked
    Then the evaluator in content-2, the last Round, and not a new Round from content-1's
    findings"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", 2, MADE_ALL, None))
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next(
        "evaluator", "content", False
    )


# The generator in a new content Round, where there's no Round yet.


@pytest.mark.supports(
    "test_a_signoff_of_the_plan_makes_it_done_and_starts_the_generator_of_each_deliverable_due"
)
@pytest.mark.parametrize("refactors", [False, True])
def test_no_round_yet_waits_on_the_generator_in_a_new_content_round(results: str, refactors: bool):
    """Given the command with no Round and no open decision, its kind refactored or not
    When what it waits on is asked
    Then the generator in a new Round of the stage content"""
    assert next_of(node(folder=results), [], refactors) == Next("generator", "content", False)


# A condition not good: a new Round of the last stage below LIMIT, else the orchestrator.


@pytest.mark.supports("test_an_evaluators_findings_go_to_the_next_rounds_generator_as_given")
def test_a_condition_short_after_one_content_round_gets_another(results: str):
    """Given the command judged short on N1 in content-1, LIMIT being 2
    When what it waits on is asked
    Then the generator in a new content Round"""
    assert LIMIT == 2
    done = rounds(results, ("content", 1, MADE_ALL, SHORT))
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next(
        "generator", "content", False
    )


@pytest.mark.supports("test_a_deliverable_short_after_two_content_rounds_gets_no_third")
def test_a_condition_short_after_limit_content_rounds_waits_on_the_orchestrator(results: str):
    """Given the command judged short on N1 in content-1 and content-2, LIMIT Rounds of content
    When what it waits on is asked
    Then the orchestrator, with no stage, as no third content Round comes"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", 2, MADE_ALL, SHORT))
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next(
        "orchestrator", None, False
    )


@pytest.mark.supports("test_a_deliverable_short_after_two_content_rounds_gets_no_third")
def test_a_condition_short_after_one_refactor_round_gets_another_whatever_content_took(
    results: str,
):
    """Given the command judged good in content-1 and content-2, then short on N1 in refactor-1
    When what it waits on is asked
    Then the generator in a new refactor Round, the last Round's stage, counting refactor alone"""
    done = rounds(
        results,
        ("content", 1, MADE_ALL, SHORT),
        ("content", 2, MADE_ALL, GOOD),
        ("refactor", 1, MADE_ALL, SHORT),
    )
    assert next_of(node(["N2", "N3"], folder=results), done, True) == Next(
        "generator", "refactor", False
    )


@pytest.mark.supports("test_a_deliverable_short_after_two_content_rounds_gets_no_third")
def test_a_condition_short_after_limit_refactor_rounds_waits_on_the_orchestrator(results: str):
    """Given the command judged good in content-1, then short on N1 in refactor-1 and refactor-2
    When what it waits on is asked
    Then the orchestrator"""
    done = rounds(
        results,
        ("content", 1, MADE_ALL, GOOD),
        ("refactor", 1, MADE_ALL, SHORT),
        ("refactor", 2, MADE_ALL, SHORT),
    )
    assert next_of(node(["N2", "N3"], folder=results), done, True) == Next(
        "orchestrator", None, False
    )


@pytest.mark.supports("test_an_evaluators_findings_go_to_the_next_rounds_generator_as_given")
def test_a_condition_the_node_holds_short_counts_though_the_evaluator_found_it_good(results: str):
    """Given the command judged good on each condition in content-1, the node holding N1 not good
    When what it waits on is asked
    Then the generator in a new content Round, as the node's conditions decide, not the
    evaluator's"""
    done = rounds(results, ("content", 1, MADE_ALL, GOOD))
    assert next_of(node(["N2", "N3"], folder=results), done, True) == Next(
        "generator", "content", False
    )


# Each condition good: a refactor Round where the kind is refactored and has none, else sign-off.


@pytest.mark.supports(
    "test_a_deliverable_with_each_condition_good_is_refactored_by_its_refactor_best_practice"
)
def test_each_condition_good_after_content_gets_a_refactor_round(results: str):
    """Given a refactored kind's deliverable judged good in content-1, each condition good
    When what it waits on is asked
    Then the generator in a new refactor Round"""
    done = rounds(results, ("content", 1, MADE_ALL, GOOD))
    assert next_of(node(True, folder=results), done, True) == Next("generator", "refactor", False)


@pytest.mark.supports(
    "test_a_deliverable_with_each_condition_good_is_refactored_by_its_refactor_best_practice"
)
def test_each_condition_good_after_a_refactor_round_waits_on_the_signoff(results: str):
    """Given a refactored kind's deliverable judged good in content-1 and refactor-1
    When what it waits on is asked
    Then the sign-off"""
    done = rounds(results, ("content", 1, MADE_ALL, GOOD), ("refactor", 1, MADE_ALL, GOOD))
    assert next_of(node(True, folder=results), done, True) == Next("sign-off", None, False)


@pytest.mark.supports(
    "test_a_finding_the_people_would_never_meet_is_dropped_by_holding_its_condition_good"
)
def test_each_condition_good_of_a_kind_not_refactored_waits_on_the_signoff(results: str):
    """Given the command, of the kind light, which isn't refactored, judged short on N1 in
    content-1, the orchestrator holding N1 good as its people would never meet it
    When what it waits on is asked
    Then the sign-off"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT))
    assert next_of(node(True, folder=results), done, False) == Next("sign-off", None, False)


@pytest.mark.supports("test_a_deliverable_short_after_two_content_rounds_gets_no_third")
def test_each_condition_good_after_limit_content_rounds_isnt_held_back_by_the_limit(results: str):
    """Given a refactored kind's deliverable judged short in content-1 and good in content-2
    When what it waits on is asked
    Then the generator in a new refactor Round, the limit counting each stage apart"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", 2, MADE_ALL, GOOD))
    assert next_of(node(True, folder=results), done, True) == Next("generator", "refactor", False)


# A pause that leaves a Round with its Cut and no result.


@pytest.mark.supports(
    "test_a_pick_up_starts_the_stopped_generator_again_in_its_round_with_a_fresh_cut"
)
def test_a_round_whose_generator_was_stopped_resumes_it_there(results: str):
    """Given the command whose generator, in content-1, was stopped by a pause before it wrote a
    result
    When what it waits on is asked
    Then the generator in the last Round again, content-1, as S2 starts each role stopped again
    from the Round's files, not a new Round"""
    done = rounds(results, ("content", 1, None, None))
    assert next_of(node(folder=results), done, False) == Next("generator", "content", True)


@pytest.mark.supports(
    "test_a_pick_up_starts_the_stopped_generator_again_in_its_round_with_a_fresh_cut"
)
def test_a_second_round_whose_generator_was_stopped_resumes_it_there(results: str):
    """Given the command judged short in content-1, whose generator, in content-2, was stopped by a
    pause before it wrote a result
    When what it waits on is asked
    Then the generator in content-2 again, not the orchestrator, as the Round was never made"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", 2, None, None))
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next(
        "generator", "content", True
    )


@pytest.mark.supports(
    "test_a_pick_up_starts_the_stopped_generator_again_in_its_round_with_a_fresh_cut"
)
def test_a_refactor_round_whose_generator_was_stopped_resumes_it_there(results: str):
    """Given a refactored kind's command judged good in content-1, whose generator, in refactor-1,
    was stopped by a pause before it wrote a result
    When what it waits on is asked
    Then the generator in refactor-1 again, not a new refactor Round or the sign-off"""
    done = rounds(results, ("content", 1, MADE_ALL, GOOD), ("refactor", 1, None, None))
    assert next_of(node(True, folder=results), done, True) == Next("generator", "refactor", True)


@pytest.mark.supports(
    "test_a_pick_up_starts_the_stopped_generator_again_in_its_round_with_a_fresh_cut"
)
def test_a_round_at_limit_whose_generator_was_stopped_resumes_it_not_the_orchestrator(
    results: str,
):
    """Given the command judged short in content-1, and the LIMIT-th Round, content-2, whose
    generator a pause stopped before it wrote a result
    When what it waits on is asked
    Then the generator in content-2 again, spending no Round, as the stopped Round was never
    made"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", LIMIT, None, None))
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next(
        "generator", "content", True
    )


@pytest.mark.supports("test_a_pick_up_starts_the_stopped_evaluator_again_in_its_round")
@pytest.mark.parametrize("number", [1, LIMIT])
def test_a_round_whose_evaluator_was_stopped_waits_on_the_evaluator_there(
    results: str, number: int
):
    """Given the command made in content-<number>, Round 1 or the LIMIT-th, each Round before it
    judged short, its evaluator stopped by a pause before it wrote a result
    When what it waits on is asked
    Then the evaluator in that Round"""
    each = [("content", n, MADE_ALL, SHORT) for n in range(1, number)]
    done = rounds(results, *each, ("content", number, MADE_ALL, None))
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next(
        "evaluator", "content", False
    )


# The sign-off past the limit, with the findings left kept as open decisions.


@pytest.mark.supports("test_a_finding_left_past_two_content_rounds_goes_to_the_user_as_a_proposal")
def test_findings_kept_open_past_limit_content_rounds_wait_on_the_signoff(results: str):
    """Given the command judged short on N1 in content-1 and content-2, LIMIT Rounds each with
    both results, and the finding left kept as an open decision of N1
    When what it waits on is asked
    Then the sign-off, before the answer that the open decision would ask"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", 2, MADE_ALL, SHORT))
    assert next_of(node(["N2", "N3"], open_decision=True, folder=results), done, False) == Next(
        "sign-off", None, False
    )


@pytest.mark.supports("test_a_finding_left_past_two_content_rounds_goes_to_the_user_as_a_proposal")
def test_findings_kept_open_past_limit_refactor_rounds_wait_on_the_signoff(results: str):
    """Given a refactored kind's command judged good in content-1, short on N1 in refactor-1 and
    refactor-2, and the finding left kept as an open decision of N1
    When what it waits on is asked
    Then the sign-off"""
    done = rounds(
        results,
        ("content", 1, MADE_ALL, GOOD),
        ("refactor", 1, MADE_ALL, SHORT),
        ("refactor", 2, MADE_ALL, SHORT),
    )
    assert next_of(node(["N2", "N3"], open_decision=True, folder=results), done, True) == Next(
        "sign-off", None, False
    )


@pytest.mark.supports("test_a_deliverable_short_after_two_content_rounds_gets_no_third")
def test_an_open_decision_below_limit_waits_on_the_answer_not_the_signoff(results: str):
    """Given the command judged short on N1 in content-1 alone, one Round below LIMIT, and an
    open decision of N1
    When what it waits on is asked
    Then the answer, as the stage hasn't LIMIT Rounds"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT))
    assert next_of(node(["N2", "N3"], open_decision=True, folder=results), done, False) == Next(
        "answer", None, False
    )


@pytest.mark.supports("test_a_deliverable_whose_point_waits_on_the_user_gets_no_cut")
def test_a_point_open_in_the_limit_round_waits_on_the_answer_not_the_signoff(results: str):
    """Given the command judged short in content-1, whose generator gave a point in content-2, the
    LIMIT-th Round, kept as an open decision of N1, with no evaluator's result
    When what it waits on is asked
    Then the answer, as the LIMIT-th Round lacks its evaluator's result"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", 2, POINTED, None))
    assert next_of(node(["N2", "N3"], open_decision=True, folder=results), done, False) == Next(
        "answer", None, False
    )


@pytest.mark.supports("test_a_deliverable_short_after_two_content_rounds_gets_no_third")
def test_limit_rounds_judged_with_no_decision_open_wait_on_the_orchestrator(results: str):
    """Given the command judged short on N1 in content-1 and content-2, and no decision open, as
    the orchestrator hasn't kept the finding left yet
    When what it waits on is asked
    Then the orchestrator, to keep it, and not the sign-off"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", 2, MADE_ALL, SHORT))
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next(
        "orchestrator", None, False
    )


@pytest.mark.supports("test_a_finding_left_past_two_content_rounds_goes_to_the_user_as_a_proposal")
def test_the_last_stage_counts_for_the_signoff_past_limit_not_an_earlier_one(results: str):
    """Given a refactored kind's command judged short in content-1 and content-2, then good after
    the orchestrator held N1 good, and short on N2 in refactor-1, one refactor Round, with an open
    decision of N1 left from content
    When what it waits on is asked
    Then the answer, as the last Round's stage, refactor, hasn't LIMIT Rounds"""
    done = rounds(
        results,
        ("content", 1, MADE_ALL, SHORT),
        ("content", 2, MADE_ALL, SHORT),
        ("refactor", 1, MADE_ALL, SHORT),
    )
    assert next_of(node(["N1", "N3"], open_decision=True, folder=results), done, True) == Next(
        "answer", None, False
    )


# Past the limit, an open decision of a condition not good is a proposal, and one of a condition
# good a point: the decision table of which open decisions the node holds.


def with_open(good: Sequence[str], on: Sequence[str], folder: str) -> Any:
    """The command's open node, its conditions good as given, with an open decision of each
    condition of `on`, read back from JSON."""
    given = rn_files.decided(
        rn_files.open_node(rn_files.COMMAND_NAME, COMMAND, "light", ["invoicer/lines.py"], good),
        {each: [rn_files.decision(f"the point of {each}", None)] for each in on},
    )
    return read_back(folder, "node", given)


@pytest.mark.supports("test_a_finding_left_past_two_content_rounds_goes_to_the_user_as_a_proposal")
@pytest.mark.parametrize(
    ("good", "on", "waits_on"),
    [
        (["N2", "N3"], ["N1"], "sign-off"),
        (["N3"], ["N1", "N2"], "sign-off"),
        (["N1", "N2", "N3"], ["N1"], "answer"),
        (["N2", "N3"], ["N2"], "answer"),
        (["N2", "N3"], ["N1", "N2"], "answer"),
        (["N3"], ["N1"], "orchestrator"),
    ],
)
def test_open_decisions_past_limit_are_proposals_of_conditions_not_good_and_points_of_good_ones(
    results: str, good: list[str], on: list[str], waits_on: str
):
    """Given the command judged short in content-1 and content-2, LIMIT Rounds each with both
    results, its conditions good as given, and an open decision of each condition of `on`
    When what it waits on is asked
    Then the sign-off where each open decision is of a condition not good and each condition not
    good keeps one; the answer where an open decision is of a condition good, a point; and the
    orchestrator where a condition not good keeps none yet"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", 2, MADE_ALL, SHORT))
    assert next_of(with_open(good, on, results), done, False) == Next(waits_on, None, False)


@pytest.mark.supports("test_a_deliverable_whose_point_waits_on_the_user_gets_no_cut")
@pytest.mark.parametrize("number", sorted({1, LIMIT - 1}))
def test_an_open_decision_of_a_condition_not_good_below_limit_is_a_point(results: str, number: int):
    """Given the command judged short on N1 in content-1 to content-<number>, below LIMIT, and an
    open decision of N1
    When what it waits on is asked
    Then the answer, as below the limit an open decision is a point, not a proposal"""
    done = rounds(results, *[("content", each, MADE_ALL, SHORT) for each in range(1, number + 1)])
    assert next_of(with_open(["N2", "N3"], ["N1"], results), done, False) == Next(
        "answer", None, False
    )
