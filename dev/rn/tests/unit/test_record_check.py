"""The unit cases of record/check.py, rn's check of a role's end, through `record_faults`,
`made_faults`, `answers_faults`, and `check`. Whether a record passes turns on each step being
there, in order, and on each practice lying in a step that takes its phase, so the cases take one
for each combination, as decision table testing does."""

from __future__ import annotations

import os
from typing import Any

import pytest
from fault import CantRun
from record.check import answers_faults, check, made_faults, record_faults
from record.form import Entry, Record
from record.steps import Step
from rn_example import HINTS, POINT, RN
from rn_parts import ANSWERED, RUN
from tree.cut import Cut
from tree.practices import DECIDE, MAKE, BestPractice, NecessaryCondition, Practice
from tree.rounds import Answers, Good, More, MoreKept

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")

STEPS = (
    Step("generator", 1, "Read."),
    Step("generator", 2, "Decide.", DECIDE),
    Step("generator", 3, "Make.", MAKE),
)
CODE = BestPractice(
    "code",
    (
        NecessaryCondition(
            "N1",
            "C1",
            "One place?",
            (Practice("N1.1", DECIDE, "List."), Practice("N1.2", MAKE, "State.")),
        ),
    ),
)
FULL = (
    Entry("generator", "1", "Read."),
    Entry("code", "N1.1", "Listed."),
    Entry("generator", "2", "Decided."),
    Entry("code", "N1.2", "Stated."),
    Entry("generator", "3", "Made."),
)
REFACTOR = BestPractice(
    "refactor-code",
    (NecessaryCondition("N1", "C1", "Reads as meant?", (Practice("N1.1", MAKE, "Rename."),)),),
)
GENERATOR = Cut(
    "generator",
    RUN,
    "r",
    deliverable=HINTS,
    decisions=(ANSWERED,),
    more=(MoreKept("N2", "good_when"),),
)
EVALUATOR = Cut("evaluator", RUN, "r", deliverable=HINTS, group="C1", conditions=("N1", "N2"))


@pytest.mark.supports(
    "test_a_generator_whose_record_holds_each_step_and_practice_ends_with_its_result_kept"
)
def test_a_record_with_each_step_and_each_practice_in_its_phase_has_no_fault():
    """Given steps 1 to 3, and each practice recorded before the step that takes its phase ends
    When the record is checked
    Then it has no fault"""
    assert record_faults(Record(FULL), STEPS, (CODE,)) == ()


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_record_without_a_step_names_it():
    """Given the full record without step 3
    When it's checked
    Then the fault names step 3 of generator"""
    (fault,) = record_faults(Record(FULL[:-1]), STEPS, (CODE,))
    assert "step 3" in fault and "generator" in fault


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_record_with_steps_out_of_order_names_the_step_out_of_order():
    """Given step 2 recorded before step 1
    When it's checked
    Then a fault names step 1"""
    swapped = (FULL[2], FULL[1], FULL[0], FULL[3], FULL[4])
    assert any("step 1" in fault for fault in record_faults(Record(swapped), STEPS, (CODE,)))


@pytest.mark.supports(
    "test_a_generator_whose_record_skips_the_practices_of_its_best_practice_is_held_at_its_end"
)
def test_a_record_without_a_practice_names_it():
    """Given the full record without N1.2
    When it's checked
    Then the fault names N1.2 of code"""
    (fault,) = record_faults(Record(FULL[:3] + FULL[4:]), STEPS, (CODE,))
    assert "N1.2" in fault and "code" in fault


@pytest.mark.supports(
    "test_a_generator_whose_record_skips_its_refactor_practices_is_held_at_its_end"
)
def test_a_record_without_a_practice_of_the_refactor_best_practice_names_it_by_its_kind():
    """Given the full record of the code best practice, and the refactor-code best practice beside
    it, none of whose practices it holds
    When it's checked against both
    Then the fault names N1.1 of refactor-code"""
    (fault,) = record_faults(Record(FULL), STEPS, (CODE, REFACTOR))
    assert "N1.1" in fault and "refactor-code" in fault


@pytest.mark.supports(
    "test_a_generator_whose_record_skips_the_practices_of_its_best_practice_is_held_at_its_end"
)
def test_a_practice_of_making_recorded_while_deciding_names_it():
    """Given N1.2, of making, recorded before step 2, the step of deciding, ends
    When it's checked
    Then the fault names N1.2"""
    early = (FULL[0], FULL[1], FULL[3], FULL[2], FULL[4])
    assert any("N1.2" in fault for fault in record_faults(Record(early), STEPS, (CODE,)))


@pytest.mark.supports(
    "test_a_turn_that_puts_work_up_is_held_until_the_orchestrators_record_holds_each_step"
)
def test_a_record_of_a_role_with_no_best_practice_needs_only_its_steps():
    """Given the steps alone recorded, and no best practice
    When it's checked
    Then it has no fault"""
    steps_only = (FULL[0], FULL[2], FULL[4])
    assert record_faults(Record(steps_only), STEPS, ()) == ()


@pytest.mark.supports(
    "test_a_generator_whose_made_leaves_out_a_decision_of_its_cut_is_held_at_its_end"
)
def test_made_naming_each_decision_and_more_kept_has_no_fault():
    """Given the generator's cut with the answer and a More kept of N2
    When what it made names both
    Then it has no fault"""
    assert made_faults(GENERATOR, (POINT,), ("N2",)) == ()


@pytest.mark.supports(
    "test_a_generator_whose_made_leaves_out_a_decision_of_its_cut_is_held_at_its_end"
)
def test_made_leaving_out_a_decision_names_it():
    """Given the generator's cut with the answer
    When what it made names no decision
    Then the fault names the point"""
    (fault,) = made_faults(GENERATOR, (), ("N2",))
    assert POINT in fault


@pytest.mark.supports("test_the_next_round_is_made_from_the_decision_changed_and_the_more_kept")
def test_made_leaving_out_a_more_kept_names_its_condition():
    """Given the generator's cut with a More kept of N2
    When what it made names no More kept
    Then the fault names N2"""
    (fault,) = made_faults(GENERATOR, (POINT,), ())
    assert "N2" in fault


@pytest.mark.supports(
    "test_an_evaluator_whose_answers_leave_a_condition_of_its_group_is_held_at_its_end"
)
def test_answers_of_each_condition_of_the_group_have_no_fault():
    """Given an evaluator of C1, whose conditions are N1 and N2
    When its Answers meet N1 and not N2
    Then they have no fault"""
    answers = Answers("C1", (Good("N1", ("invoicer/totals.py:3",)),), (More("N2", "good_when"),))
    assert answers_faults(EVALUATOR, answers) == ()


@pytest.mark.supports(
    "test_an_evaluator_whose_answers_leave_a_condition_of_its_group_is_held_at_its_end"
)
def test_answers_leaving_a_condition_unanswered_name_it():
    """Given an evaluator of C1
    When its Answers meet N1 alone
    Then the fault names N2"""
    (fault,) = answers_faults(EVALUATOR, Answers("C1", (Good("N1", ("x",)),)))
    assert "N2" in fault


@pytest.mark.supports(
    "test_an_evaluator_whose_answers_leave_a_condition_of_its_group_is_held_at_its_end"
)
def test_answers_of_a_condition_outside_the_group_name_it():
    """Given an evaluator of C1
    When its Answers also meet N8
    Then a fault names N8"""
    met = (Good("N1", ("x",)), Good("N8", ("y",)))
    assert any(
        "N8" in fault for fault in answers_faults(EVALUATOR, Answers("C1", met, (More("N2", "z"),)))
    )


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_check_of_a_cut_that_isnt_there_cant_run(tmp_path: Any):
    """Given no cut at the path given
    When the generator's end is checked
    Then the check can't run, naming the path"""
    missing = os.path.join(str(tmp_path), "cut.json")
    with pytest.raises(CantRun, match="cut.json"):
        check("generator", "done", missing, str(tmp_path), RN)
