"""The unit cases of tree/rounds.py, where each round of a deliverable keeps its records and their
forms, through `folder`, `latest`, `load`, `parse_answers`, `parse_made`, `keep_try`,
`keep_more`, and `keep_place`."""

from __future__ import annotations

import os
from typing import Any

import pytest
from fault import Wrong
from rn_example import DECIMAL, HINTS, POINT, SETTLED, TYPED
from rn_parts import RUN
from tree.rounds import (
    Answers,
    Good,
    Made,
    More,
    MoreKept,
    Place,
    Round,
    Settled,
    Tried,
    folder,
    keep_more,
    keep_place,
    keep_try,
    latest,
    load,
    parse_answers,
    parse_made,
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
    "test_a_more_the_people_fall_short_by_changes_its_decision_and_reaches_the_next_round"
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
    "test_a_more_the_people_fall_short_by_changes_its_decision_and_reaches_the_next_round"
)
def test_keep_more_keeps_the_more_in_the_last_round(run: str):
    """Given the hints' round 1
    When a `more` of N2 is kept
    Then round 1 holds it, for the round after it"""
    os.makedirs(folder(run, HINTS, 1))
    more = MoreKept("N2", "A caller tells a rate by its type.")
    keep_more(run, HINTS, more)
    assert load(run, HINTS, 1).more == (more,)


@pytest.mark.supports("test_a_generators_place_commits_its_work_with_the_step_it_stands_at")
def test_keep_place_keeps_each_place_with_the_last_of_each_role_last(run: str):
    """Given the hints' round 1
    When the generator's Place at step 3 and then at step 4 are kept
    Then the round's Places end with the one at step 4"""
    os.makedirs(folder(run, HINTS, 1))
    keep_place(run, HINTS, Place("generator", 3, ("invoicer/lines.py",)))
    keep_place(run, HINTS, Place("generator", 4, ("invoicer/tax.py",)))
    assert load(run, HINTS, 1).places[-1] == Place("generator", 4, ("invoicer/tax.py",))


@pytest.mark.supports("test_an_evaluators_place_commits_its_work_with_its_group_and_step")
def test_keep_place_keeps_an_evaluators_place_with_its_group(run: str):
    """Given the hints' round 1 with the generator at step 7
    When the evaluator of C1 keeps its Place at step 2
    Then the round's Places end with the evaluator of C1 at step 2, after the generator's"""
    os.makedirs(folder(run, HINTS, 1))
    keep_place(run, HINTS, Place("generator", 7))
    keep_place(run, HINTS, Place("evaluator", 2, group="C1"))
    assert load(run, HINTS, 1).places == (Place("generator", 7), Place("evaluator", 2, group="C1"))


@pytest.mark.supports(
    "test_the_orchestrator_gets_the_round_and_puts_up_the_points_the_generator_settled"
)
def test_parse_made_reads_each_decision_more_kept_and_point_settled():
    """Given what the hints' generator made, naming the point on each file and the point on amounts
    it settled without asking
    When it's read
    Then it holds the decision with where it lies, no More kept, and the point settled with its
    ground"""
    given = {
        "decisions": [{"about": POINT, "where": "invoicer/"}],
        "lacks": [],
        "settled": [SETTLED],
    }
    assert parse_made(given, "made.json") == Made(
        ((POINT, "invoicer/"),),
        (),
        (Settled(SETTLED["point"], DECIMAL, SETTLED["ground"]),),
    )


@pytest.mark.parametrize(
    "given",
    [
        {"decisions": [], "more": []},
        {"decisions": [], "more": [], "settled": [dict(SETTLED, ground="")]},
        {"decisions": [], "more": [], "settled": [{"point": "x", "decided": "y"}]},
    ],
)
@pytest.mark.supports(
    "test_the_orchestrator_gets_the_round_and_puts_up_the_points_the_generator_settled"
)
def test_parse_made_refuses_a_point_settled_without_its_ground(given: Any):
    """Given what a generator made with no `settled`, or a point settled with an empty ground or
    none
    When it's read
    Then it's refused, naming the file"""
    with pytest.raises(Wrong, match="made.json"):
        parse_made(given, "made.json")


@pytest.mark.supports("test_a_generators_place_commits_its_work_with_the_step_it_stands_at")
def test_load_of_a_round_not_kept_holds_nothing(run: str):
    """Given no folder of the hints' round 3
    When it's loaded
    Then it's round 3 with nothing kept"""
    assert load(run, HINTS, 3) == Round(HINTS, 3)


@pytest.mark.supports(
    "test_an_evaluators_end_is_held_until_its_answers_name_each_condition_of_its_group"
)
def test_parse_answers_reads_each_condition_in_good_and_in_more():
    """Given an evaluator's Answers on C1, N1 in good with one line and N2 in more
    When they're read
    Then they hold N1 in good with its line and N2 with its good_when"""
    given = {
        "good": [{"question": "N1", "lines": ["invoicer/totals.py:3"]}],
        "more": [{"question": "N2", "good_when": "A caller tells a rate by its type."}],
    }
    assert parse_answers(given, "C1", "a.json") == Answers(
        "C1",
        (Good("N1", ("invoicer/totals.py:3",)),),
        (More("N2", "A caller tells a rate by its type."),),
    )


@pytest.mark.parametrize(
    "given",
    [
        {"good": [{"question": "N1", "lines": []}], "more": []},
        {"good": [{"question": "N1"}], "more": []},
        {"good": []},
        {"good": [], "more": [{"question": "N2", "good_when": "x", "fix": "y"}]},
        "N1 in good",
    ],
)
@pytest.mark.supports(
    "test_an_evaluators_end_is_held_until_its_answers_name_each_condition_of_its_group"
)
def test_parse_answers_refuses_answers_out_of_their_form(given: Any):
    """Given a condition in good with no line, one with no lines, no `more`, a good_when with a fix
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
