"""The unit cases of tree/records.py, which decides where each start's record lies and the order its
name keeps, and of tree/results.py, which decides how a Made and Answers are read. A record's path
turns on how many records the run holds and how many starts take one, so the cases take none, one,
and one taken but not yet written. A Made and Answers are each read in their form, out of it, at
the least each list may hold, or missing, and a Made keys each More kept by its best practice and
necessary condition, as the kind's best practice and the refactor one share condition IDs."""

from __future__ import annotations

import os
from typing import Any

import pytest
from fault import CantRun, Wrong
from tree import records, results
from tree.results import Settled

from dev.rn.tests.unit import rn_data as d


def touch(path: str) -> str:
    return d.write_json(path, {"entries": []})


@pytest.mark.supports("test_a_request_starts_a_run_anew_with_the_tree_keepers_start_first")
def test_the_first_record_lies_in_the_runs_records_and_names_its_role(tmp_path: Any) -> None:
    """Given: a run whose records/ holds none.
    When: the path of a new start of the tree-keeper is asked.
    Then: it lies in the run's records/, and its role reads back as tree-keeper."""
    run = d.run_of(d.repository(str(tmp_path)))
    path = records.new_record(run, "tree-keeper", [])
    assert os.path.dirname(os.path.join(run.worktree, path)) == os.path.join(run.folder, "records")
    assert records.role_of(path) == "tree-keeper"


@pytest.mark.supports("test_a_second_generator_starts_with_the_next_deliverable_doing")
def test_a_new_record_comes_after_each_held_and_each_taken(tmp_path: Any) -> None:
    """Given: a run whose records/ holds the tree-keeper's record, and a generator's record taken by
    a start that runs but not yet written.
    When: the path of a new start of the generator is asked.
    Then: it comes after both in the order of the starts."""
    run = d.run_of(d.repository(str(tmp_path)))
    keeper = records.new_record(run, "tree-keeper", [])
    touch(os.path.join(run.worktree, keeper))
    taken = records.new_record(run, "generator", [])
    path = records.new_record(run, "generator", [taken])
    assert path not in (keeper, taken)
    touch(os.path.join(run.worktree, taken))
    touch(os.path.join(run.worktree, path))
    assert records.in_order(run) == (keeper, taken, path)


@pytest.mark.supports("test_up_alone_in_the_runs_worktree_picks_up_where_it_stopped")
def test_a_run_with_no_record_has_none_in_order(tmp_path: Any) -> None:
    """Given: a run whose records/ holds none.
    When: the records in the order of the starts are asked.
    Then: it gives none."""
    assert records.in_order(d.run_of(d.repository(str(tmp_path)))) == ()


@pytest.mark.supports("test_up_alone_at_the_root_picks_up_the_one_run_left")
def test_the_orchestrators_record_lies_in_records_apart_from_each_start(tmp_path: Any) -> None:
    """Given: a run whose records/ holds a generator's record.
    When: the orchestrator's record is asked, and the records in the order of the starts.
    Then: the orchestrator's lies in the run's records/, and isn't among the starts' records."""
    run = d.run_of(d.repository(str(tmp_path)))
    generator = records.new_record(run, "generator", [])
    touch(os.path.join(run.worktree, generator))
    mine = records.orchestrator_record(run)
    assert os.path.dirname(os.path.join(run.worktree, mine)) == os.path.join(run.folder, "records")
    touch(os.path.join(run.worktree, mine))
    assert records.in_order(run) == (generator,)


@pytest.mark.supports("test_up_alone_in_the_runs_worktree_picks_up_where_it_stopped")
@pytest.mark.parametrize("path", ["README.md", ".rn/x/design-tree.json", ""])
def test_a_path_that_names_no_record_has_no_role(path: str) -> None:
    """Given: a path that names no record of a run.
    When: its role is asked.
    Then: it's refused."""
    with pytest.raises(Wrong):
        records.role_of(path)


@pytest.mark.supports("test_the_round_gives_each_evaluators_answers_and_what_the_generator_made")
def test_a_made_in_its_form_is_read(tmp_path: Any) -> None:
    """Given: a generator's Made with one decision carried out and one point settled.
    When: it's read.
    Then: it gives where it carries out the decision, no More kept, and the point with its
    ground."""
    given = results.read_made(d.write_json(os.path.join(tmp_path, "made.json"), d.made()))
    assert given.decisions == {"deliverables/0/necessary_conditions/0/decisions/0": "invoicer"}
    assert dict(given.more) == {}
    assert given.settled == (
        Settled(
            "the type of amounts and rates", "Decimal", "the code already computes with Decimal"
        ),
    )


@pytest.mark.supports("test_a_more_the_people_fall_short_by_reaches_the_next_rounds_generator")
def test_a_made_keeps_the_more_of_each_best_practice_apart(tmp_path: Any) -> None:
    """Given: a Made that makes the More kept of N2 of code good in one place, and that of N2 of
    refactor-code in another.
    When: it's read.
    Then: it gives each place under its best practice and N2."""
    held = {
        **d.made(),
        "more": [
            {"best_practice": "code", "condition": "N2", "where": "invoicer/totals.py"},
            {"best_practice": "refactor-code", "condition": "N2", "where": "invoicer/tax.py"},
        ],
    }
    given = results.read_made(d.write_json(os.path.join(tmp_path, "made.json"), held))
    assert dict(given.more) == {
        ("code", "N2"): "invoicer/totals.py",
        ("refactor-code", "N2"): "invoicer/tax.py",
    }


@pytest.mark.supports("test_the_round_gives_each_evaluators_answers_and_what_the_generator_made")
@pytest.mark.parametrize(
    "held",
    [
        {"decisions": [], "more": []},
        {**d.made(), "extra": 1},
        {**d.made(), "settled": [{}]},
        {**d.made(), "more": [{"condition": "N2", "where": "invoicer"}]},
    ],
)
def test_a_made_out_of_its_form_is_refused(tmp_path: Any, held: Any) -> None:
    """Given: a Made that lacks settled, holds a field its form has no place for, settles a point
    with nothing in it, or makes a More kept good with no best practice.
    When: it's read.
    Then: it's refused."""
    with pytest.raises(Wrong):
        results.read_made(d.write_json(os.path.join(tmp_path, "made.json"), held))


@pytest.mark.supports("test_the_round_gives_each_evaluators_answers_and_what_the_generator_made")
def test_answers_with_a_line_for_each_good_and_a_good_when_for_each_more_are_read(
    tmp_path: Any,
) -> None:
    """Given: an evaluator's Answers with N1 good on one line, and N2 in more.
    When: they're read.
    Then: they give N1's line, and N2's good_when."""
    held = {
        "good": [{"question": "N1", "lines": ["def total(lines, rate):"]}],
        "more": [{"question": "N2", "good_when": "A caller sees each argument's type."}],
    }
    given = results.read_answers(d.write_json(os.path.join(tmp_path, "answers.json"), held))
    assert given.good == {"N1": ("def total(lines, rate):",)}
    assert given.more == {"N2": "A caller sees each argument's type."}


@pytest.mark.supports("test_the_round_gives_each_evaluators_answers_and_what_the_generator_made")
@pytest.mark.parametrize(
    "held",
    [
        {"good": [{"question": "N1", "lines": []}], "more": []},
        {"good": [], "more": [{"question": "N2"}]},
        {"good": []},
    ],
)
def test_answers_out_of_their_form_are_refused(tmp_path: Any, held: Any) -> None:
    """Given: Answers with a good of no line, a more with no good_when, or no more.
    When: they're read.
    Then: they're refused."""
    with pytest.raises(Wrong):
        results.read_answers(d.write_json(os.path.join(tmp_path, "answers.json"), held))


@pytest.mark.supports("test_the_round_gives_each_evaluators_answers_and_what_the_generator_made")
def test_a_made_missing_cant_be_read(tmp_path: Any) -> None:
    """Given: no file of a Made.
    When: it's read.
    Then: it couldn't run."""
    with pytest.raises(CantRun):
        results.read_made(os.path.join(tmp_path, "made.json"))


@pytest.mark.supports("test_the_round_gives_each_evaluators_answers_and_what_the_generator_made")
def test_answers_missing_cant_be_read(tmp_path: Any) -> None:
    """Given: no file of Answers.
    When: they're read.
    Then: they couldn't run."""
    with pytest.raises(CantRun):
        results.read_answers(os.path.join(tmp_path, "answers.json"))
