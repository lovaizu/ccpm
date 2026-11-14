"""The unit cases of tree/rounds.py, where each round of a deliverable keeps its records and their
forms, through `folder`, `latest`, `load`, `parse_answers`, `keep_try`, `keep_lack`, and
`keep_place`."""

from __future__ import annotations

import os
from typing import Any

import pytest
from rn_example import HINTS, TYPED
from rn_parts import RUN
from tree.fault import Wrong
from tree.rounds import (
    Answers,
    LackKept,
    Met,
    NotMet,
    Place,
    Round,
    Tried,
    folder,
    keep_lack,
    keep_place,
    keep_try,
    latest,
    load,
    parse_answers,
)

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")

TRIED = Tried("python3 -m pytest -q", 0, "1 passed")


@pytest.fixture
def run(tmp_path: Any) -> str:
    return os.path.join(str(tmp_path), RUN)


@pytest.mark.supports("test_a_generators_place_commits_its_work_with_the_step_it_stands_at")
def test_folder_names_a_deliverable_by_its_path_with_each_slash_as_two_dashes(run: str):
    """Given the run's folder
    When the folders of the hints' round 1 and the typed marker's round 2 are asked for
    Then they're rounds/invoicer--/1 and rounds/invoicer--py.typed/2 in it"""
    assert folder(run, HINTS, 1) == os.path.join(run, "rounds", "invoicer--", "1")
    assert folder(run, TYPED, 2) == os.path.join(run, "rounds", "invoicer--py.typed", "2")


@pytest.mark.supports("test_the_hints_once_due_start_a_generator_with_the_cut_of_its_first_round")
def test_latest_of_a_deliverable_with_no_round_is_0(run: str):
    """Given a run with no round of the hints
    When the hints' last round is asked for
    Then it's 0"""
    assert latest(run, HINTS) == 0


@pytest.mark.supports(
    "test_a_lack_the_people_fall_short_by_changes_its_decision_and_reaches_the_next_round"
)
def test_latest_is_the_highest_round_kept(run: str):
    """Given the hints' rounds 1, 2, and 10 kept
    When the hints' last round is asked for
    Then it's 10, by number and not by name"""
    for number in (1, 2, 10):
        os.makedirs(folder(run, HINTS, number))
    assert latest(run, HINTS) == 10


@pytest.mark.supports("test_a_try_runs_the_command_in_a_copy_and_keeps_it_in_the_rounds_try_record")
def test_keep_try_adds_each_command_to_the_rounds_try_record_in_order(run: str):
    """Given the hints' round 1 with no Try record
    When two commands tried are kept
    Then the round holds both, in the order kept, in try.json"""
    second = Tried("mypy --strict invoicer", 1, "error")
    keep_try(run, HINTS, 1, TRIED)
    path = keep_try(run, HINTS, 1, second)
    assert path == os.path.join(folder(run, HINTS, 1), "try.json")
    assert load(run, HINTS, 1).tried == (TRIED, second)


@pytest.mark.supports(
    "test_a_lack_the_people_fall_short_by_changes_its_decision_and_reaches_the_next_round"
)
def test_keep_lack_keeps_the_lack_in_the_last_round(run: str):
    """Given the hints' round 1
    When a lack of N2 is kept
    Then round 1 holds it, for the round after it"""
    os.makedirs(folder(run, HINTS, 1))
    lack = LackKept("N2", "A caller can't tell a rate from an amount.")
    keep_lack(run, HINTS, lack)
    assert load(run, HINTS, 1).lacks == (lack,)


@pytest.mark.supports("test_a_generators_place_commits_its_work_with_the_step_it_stands_at")
def test_keep_place_keeps_each_place_with_the_last_of_each_role_last(run: str):
    """Given the hints' round 1
    When the generator's Place at step 3 and then at step 4 are kept
    Then the round's Places end with the one at step 4"""
    os.makedirs(folder(run, HINTS, 1))
    keep_place(run, HINTS, Place("generator", 3, ("invoicer/lines.py",)))
    keep_place(run, HINTS, Place("generator", 4, ("invoicer/tax.py",)))
    assert load(run, HINTS, 1).places[-1] == Place("generator", 4, ("invoicer/tax.py",))


@pytest.mark.supports("test_a_generators_place_commits_its_work_with_the_step_it_stands_at")
def test_load_of_a_round_not_kept_holds_nothing(run: str):
    """Given no folder of the hints' round 3
    When it's loaded
    Then it's round 3 with nothing kept"""
    assert load(run, HINTS, 3) == Round(HINTS, 3)


@pytest.mark.supports(
    "test_an_evaluators_end_is_held_until_its_answers_name_each_condition_of_its_group"
)
def test_parse_answers_reads_each_condition_met_and_not_met():
    """Given an evaluator's Answers on C1, N1 met with one line and N2 not met
    When they're read
    Then they hold N1 met with its line and N2 with what the people lack"""
    given = {
        "met": [{"question": "N1", "lines": ["invoicer/totals.py:3"]}],
        "not_met": [{"question": "N2", "lacks": "A caller can't tell a rate from an amount."}],
    }
    assert parse_answers(given, "C1", "a.json") == Answers(
        "C1",
        (Met("N1", ("invoicer/totals.py:3",)),),
        (NotMet("N2", "A caller can't tell a rate from an amount."),),
    )


@pytest.mark.parametrize(
    "given",
    [
        {"met": [{"question": "N1", "lines": []}], "not_met": []},
        {"met": [{"question": "N1"}], "not_met": []},
        {"met": []},
        {"met": [], "not_met": [{"question": "N2", "lacks": "x", "fix": "y"}]},
        "N1 met",
    ],
)
@pytest.mark.supports(
    "test_an_evaluators_end_is_held_until_its_answers_name_each_condition_of_its_group"
)
def test_parse_answers_refuses_answers_out_of_their_form(given: Any):
    """Given a condition met with no line, one with no lines, no `not_met`, a lack with a fix
    beside it, or plain words
    When they're read
    Then they're refused, naming the file"""
    with pytest.raises(Wrong, match="a.json"):
        parse_answers(given, "C1", "a.json")


@pytest.mark.supports("test_a_try_runs_the_command_in_a_copy_and_keeps_it_in_the_rounds_try_record")
def test_load_refuses_a_try_record_out_of_its_form_naming_it(run: str):
    """Given the hints' round 1 whose try.json holds `[`
    When the round is loaded
    Then it's refused, naming try.json"""
    os.makedirs(folder(run, HINTS, 1))
    with open(os.path.join(folder(run, HINTS, 1), "try.json"), "w", encoding="utf-8") as f:
        f.write("[")
    with pytest.raises(Wrong, match="try.json"):
        load(run, HINTS, 1)
