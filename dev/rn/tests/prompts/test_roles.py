"""The unit tests of the prompts of rn's roles, each `agents/<role>.md` with `domain/<role>.md`:
the role runs alone on Opus, k = 3 times for each case, in the worktree of the walkthrough's run of
invoicer with tree.py and throwaway.py real, and each case passes only where all k runs pass,
deciding by code each point that a run's record shows. Each case names the integration case whose
role, played by the test there, it shows the real role keeping."""

from __future__ import annotations

import json

import pytest
from rn_example import ANSWER, ANSWERED, HINTS, POINT, WITH_POINT, condition, decided, plan
from rn_prompt_runs import Setting, role_runs

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")

GROUNDS = "The main conversation's grounds:\n"
TOTALS = """\
\"\"\"The totals of an invoice.\"\"\"
from decimal import Decimal

from invoicer.lines import Line
from invoicer.tax import with_tax


def subtotal(lines: list[Line]) -> Decimal:
    return sum((line.value() for line in lines), Decimal("0"))


def total(lines: list[Line], rate: Decimal) -> Decimal:
    return with_tax(subtotal(lines), rate)
"""
TYPED_HINTS = Setting(files={"invoicer/totals.py": TOTALS})


@pytest.mark.supports(
    "test_the_users_answer_written_with_its_ground_marks_the_hints_doing_and_checks_the_path_up"
)
def test_the_tree_keeper_writes_the_users_answer_by_the_user_and_ends_done():
    """Given the plan with the point on each file open
    When the tree-keeper is resumed with the user's answer, `each file`, word for word
    Then on every run it runs `tree.py write`, the tree at its end holds the answer by the user, and
    it gives `done`"""
    resume = f"{GROUNDS}The user answered the point.\nThe person's words, word for word:\n{ANSWER}"
    done = role_runs("tree-keeper", WITH_POINT, setting=Setting(resume=resume))
    assert all(
        any("tree.py write" in c for c in run.commands) and run.result == "done" for run in done
    )
    trees = [
        json.loads(run.files[".rn/20261114-type-hints-for-invoicer/design-tree.json"])
        for run in done
    ]
    assert all(
        tree["deliverables"][0]["necessary_conditions"][2]["decisions"][0]["by"] == "user"
        for tree in trees
    )


@pytest.mark.supports(
    "test_a_users_point_written_open_keeps_the_deliverable_it_lies_under_from_doing"
)
def test_the_tree_keeper_writes_a_point_it_isnt_given_the_answer_to_as_open():
    """Given the plan with the point answered
    When the tree-keeper is resumed with a new point, how amounts are typed, as a decision still
    open
    Then on every run the tree at its end holds that decision with `decided` null"""
    resume = f"{GROUNDS}A point that's the user's, still open: how amounts are typed."
    done = role_runs("tree-keeper", ANSWERED, setting=Setting(resume=resume))
    texts = [run.files[".rn/20261114-type-hints-for-invoicer/design-tree.json"] for run in done]
    assert all('"decided": null' in text and "amounts" in text for text in texts)


@pytest.mark.supports(
    "test_a_generator_whose_record_holds_each_step_and_practice_ends_with_its_result_kept"
)
def test_the_generator_makes_the_hints_tries_them_in_a_copy_and_ends_done():
    """Given the plan with the point answered, the hints doing
    When a generator of the hints starts with its cut
    Then on every run it writes only under invoicer/ and the run's folder, runs mypy only through
    throwaway.py, and gives `done`"""
    done = role_runs("generator", ANSWERED, (HINTS,))
    assert all(run.result == "done" for run in done)
    assert all(all(w.startswith((HINTS, ".rn/")) for w in run.writes) for run in done)
    assert all(all("throwaway.py try" in c for c in run.commands if "mypy" in c) for run in done)


@pytest.mark.supports(
    "test_a_generator_that_asks_ends_with_asks_and_the_next_one_starts_from_the_decision"
)
def test_the_generator_asks_where_the_design_leaves_a_point_open():
    """Given the plan whose hints hold the point on each file open
    When a generator of the hints starts with its cut
    Then on every run it gives `asks`, its reply naming the point, and writes no file of invoicer"""
    done = role_runs("generator", WITH_POINT, (HINTS,))
    assert all(run.result == "asks" and "each file" in run.reply for run in done)
    assert not any(w.startswith(HINTS) for run in done for w in run.writes)


@pytest.mark.supports(
    "test_a_generator_that_lacks_a_tool_ends_with_lacks_and_is_resumed_once_cleared"
)
def test_the_generator_hands_back_a_missing_tool_and_looks_for_no_way_round():
    """Given the plan with the point answered, and no mypy on the PATH
    When a generator of the hints starts with its cut
    Then on every run it gives `lacks`, naming mypy, and installs nothing"""
    done = role_runs("generator", ANSWERED, (HINTS,), Setting(without=("mypy",)))
    assert all(run.result == "lacks" and "mypy" in run.reply for run in done)
    assert not any("pip install" in c for run in done for c in run.commands)


@pytest.mark.supports(
    "test_once_the_generator_is_done_an_evaluator_starts_for_each_group_side_by_side"
)
def test_the_evaluator_answers_each_condition_of_its_group_with_lines_of_the_deliverable():
    """Given the hints written with their types, and the round's evaluator of C1
    When it starts with its cut
    Then on every run its Answers answer N1, N2, and N3, each met with a line of invoicer/ or not
    met with what the people lack, and it gives `done`"""
    done = role_runs("evaluator", ANSWERED, (HINTS, "C1"), TYPED_HINTS)
    answered = [
        json.loads(next(v for k, v in run.files.items() if k.endswith("answers-C1.json")))
        for run in done
    ]
    ids = [{each["question"] for each in a["met"] + a["not_met"]} for a in answered]
    assert all(found == {"N1", "N2", "N3"} for found in ids) and all(
        run.result == "done" for run in done
    )


@pytest.mark.supports("test_an_evaluator_that_reads_the_generators_cut_is_stopped")
def test_the_evaluator_reads_nothing_of_how_the_deliverable_was_made():
    """Given the hints written with their types, and the round's evaluator of C2
    When it starts with its cut
    Then on no run does it read the design tree, a generator's cut, or a record"""
    done = role_runs("evaluator", ANSWERED, (HINTS, "C2"), TYPED_HINTS)
    made = ("design-tree.json", "/records/", "cut")
    assert not any(
        any(part in r for part in made) for run in done for r in run.reads if "evaluator" not in r
    )


@pytest.mark.supports(
    "test_an_evaluators_end_is_held_until_its_answers_name_each_condition_of_its_group"
)
def test_the_evaluator_says_what_the_people_lack_and_never_how_to_fix_it():
    """Given the hints with `total` still untyped, and the round's evaluator of C1
    When it starts with its cut
    Then on every run its Answers hold a condition not met, and no lack names a type to add"""
    changed = plan(condition("N3", decided(POINT, ANSWER, "user")))
    done = role_runs("evaluator", changed, (HINTS, "C1"))
    lacks = [
        each["lacks"]
        for run in done
        for k, v in run.files.items()
        if k.endswith("answers-C1.json")
        for each in json.loads(v)["not_met"]
    ]
    assert lacks and not any("-> Decimal" in lack or "add a" in lack.lower() for lack in lacks)
