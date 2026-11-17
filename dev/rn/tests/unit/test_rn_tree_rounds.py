"""The unit cases of tree/rounds.py, which decides where each round of a deliverable keeps its files
and which round is the latest. Each path turns on how many rounds the deliverable has, none, one,
or two, and whether a start opens a new one; each Answers is given by its group; each More kept is
written and read back, or none, one for each best practice and necessary condition; and the tree at
a round's cut is the one its opening commit holds."""

from __future__ import annotations

import os
from typing import Any

import pytest
from fault import Wrong
from tree import records, rounds
from tree.more import More

from dev.rn.tests.unit import rn_data as d

EACH = pytest.mark.xfail(strict=True, raises=NotImplementedError, reason="rounds.each is empty")
KEPT = pytest.mark.xfail(
    strict=True,
    raises=NotImplementedError,
    reason="rounds.keep_more and rounds.kept_more have empty bodies",
)

GOOD_WHEN = "A caller's editor shows the type of each argument as they type the call."
N2_DECISION = "deliverables/0/necessary_conditions/1/decisions/0"


def a_more(best_practice: str, good_when: str = GOOD_WHEN, deliverable: str = "invoicer") -> More:
    """A more of N2 of the best practice, naming the decision under N2 of invoicer."""
    return More(deliverable, best_practice, "N2", N2_DECISION, good_when)


def a_run(tmp: Any) -> Any:
    run = d.run_of(d.repository(str(tmp)))
    d.tree_written(run, d.with_status(d.walkthrough_tree(), "doing", "doing"))
    return run


def opened(run: Any, deliverable: str = "invoicer") -> str:
    """A new round of the deliverable opened by the generator's Made written in it and committed;
    gives the Made's path from the worktree."""
    path = rounds.made_path(run, deliverable, True)
    d.write_json(os.path.join(run.worktree, path), d.made())
    d.git(run.worktree, "add", "-A")
    d.git(run.worktree, "commit", "-q", "-m", "A round")
    return path


@pytest.mark.supports("test_the_generator_starts_with_its_cut_of_the_first_deliverable_doing")
def test_the_first_made_lies_in_the_runs_rounds(tmp_path: Any) -> None:
    """Given: a run whose invoicer has no round.
    When: where a generator that opens a new round writes its Made is asked.
    Then: it lies in the run's rounds/."""
    run = a_run(tmp_path)
    path = rounds.made_path(run, "invoicer", True)
    assert os.path.join(run.worktree, path).startswith(os.path.join(run.folder, "rounds") + os.sep)


@pytest.mark.supports("test_a_more_the_people_fall_short_by_reaches_the_next_rounds_generator")
def test_a_new_round_lies_apart_from_the_last_and_a_start_in_it_stays(tmp_path: Any) -> None:
    """Given: a run whose invoicer has one round.
    When: where a generator writes its Made is asked, opening a new round and not.
    Then: the new round's lies apart from the first's, and one not opening a round gives the
    first's."""
    run = a_run(tmp_path)
    first = opened(run)
    assert rounds.made_path(run, "invoicer", False) == first
    assert os.path.dirname(rounds.made_path(run, "invoicer", True)) != os.path.dirname(first)


@pytest.mark.supports("test_one_evaluator_starts_for_each_group_of_necessary_conditions")
def test_each_group_writes_its_answers_apart_in_the_latest_round(tmp_path: Any) -> None:
    """Given: a run whose invoicer has one round.
    When: where the evaluators of groups 0 and 1 write their Answers is asked.
    Then: each lies apart, in the round of the Made."""
    run = a_run(tmp_path)
    made = opened(run)
    first, second = rounds.answers_path(run, "invoicer", 0), rounds.answers_path(run, "invoicer", 1)
    assert first != second
    assert os.path.dirname(first) == os.path.dirname(made) == os.path.dirname(second)


@pytest.mark.supports("test_a_command_tried_leaves_the_worktree_as_it_was_and_is_kept")
def test_a_try_record_lies_in_the_latest_round_and_none_without_one(tmp_path: Any) -> None:
    """Given: a run whose invoicer has one round, and whose invoicer/py.typed has none.
    When: where each keeps its Try record is asked.
    Then: invoicer's lies in its round, and invoicer/py.typed's is refused."""
    run = a_run(tmp_path)
    made = opened(run)
    assert os.path.dirname(rounds.try_path(run, "invoicer")) == os.path.dirname(made)
    with pytest.raises(Wrong):
        rounds.try_path(run, "invoicer/py.typed")


@pytest.mark.supports("test_each_steps_end_commits_the_work_with_its_place")
def test_a_place_lies_in_the_round_of_its_start(tmp_path: Any) -> None:
    """Given: a run whose invoicer has one round, and a record that names no start.
    When: where the Place of a start whose record lies in the run, and of the other, is asked.
    Then: the first lies in the run's rounds/, and the other is refused."""
    run = a_run(tmp_path)
    opened(run)
    started = records.new_record(run, "generator", [])
    d.write_json(os.path.join(run.worktree, started), {"entries": []})
    place = os.path.join(run.worktree, rounds.place_path(run, started))
    assert place.startswith(os.path.join(run.folder, "rounds") + os.sep)
    record = os.path.relpath(os.path.join(run.folder, "records", "nobody.json"), run.worktree)
    with pytest.raises(Wrong):
        rounds.place_path(run, record)


@EACH
@pytest.mark.supports("test_every_round_of_a_deliverable_is_read_for_its_lessons")
def test_each_round_is_given_the_latest_last(tmp_path: Any) -> None:
    """Given: a run whose invoicer has two rounds, the first with the Answers of group 1 alone.
    When: each round of invoicer is asked.
    Then: it gives both, numbered 1 and 2, each with its Made, the first with its Answers under
    group 1, and the second with none."""
    run = a_run(tmp_path)
    opened(run)
    d.write_json(
        os.path.join(run.worktree, rounds.answers_path(run, "invoicer", 1)), d.answers(["N1"])
    )
    opened(run)
    each = rounds.each(run, "invoicer")
    assert [r.number for r in each] == [1, 2]
    assert set(each[0].answers) == {1} and not each[1].answers
    assert all(r.made is not None for r in each)


@EACH
@pytest.mark.supports("test_the_round_gives_each_evaluators_answers_and_what_the_generator_made")
def test_a_deliverable_with_no_round_is_refused(tmp_path: Any) -> None:
    """Given: a run whose invoicer has no round.
    When: each round of invoicer is asked.
    Then: it's refused."""
    with pytest.raises(Wrong):
        rounds.each(a_run(tmp_path), "invoicer")


@KEPT
@pytest.mark.supports("test_a_more_the_people_fall_short_by_reaches_the_next_rounds_generator")
def test_a_more_kept_is_read_back_for_the_next_round(tmp_path: Any) -> None:
    """Given: a run whose invoicer has one round, and nothing kept yet.
    When: the More kept is asked, then the more of N2 of code is kept, and asked again.
    Then: first none, then the more of N2 with its best practice and decision, and keeping it
    gives the path written."""
    run = a_run(tmp_path)
    opened(run)
    assert rounds.kept_more(run, "invoicer") == ()
    kept = a_more("code")
    written = rounds.keep_more(run, [kept])
    assert written and all(os.path.isfile(os.path.join(run.worktree, p)) for p in written)
    assert rounds.kept_more(run, "invoicer") == (kept,)


@KEPT
@pytest.mark.supports("test_a_more_the_people_fall_short_by_reaches_the_next_rounds_generator")
def test_a_more_kept_is_one_for_each_best_practice_and_condition(tmp_path: Any) -> None:
    """Given: a run whose invoicer has one round, with the more of N2 of code kept.
    When: the more of N2 of refactor-code is kept, then the more of N2 of code again with another
    good_when.
    Then: both N2s are kept apart, and the code one holds the later good_when."""
    run = a_run(tmp_path)
    opened(run)
    rounds.keep_more(run, [a_more("code")])
    refactor = a_more("refactor-code")
    rounds.keep_more(run, [refactor])
    later = a_more("code", "Each argument's type shows as the caller types the call.")
    rounds.keep_more(run, [later])
    assert set(rounds.kept_more(run, "invoicer")) == {refactor, later}


@KEPT
@pytest.mark.supports("test_a_more_kept_with_no_decision_changed_is_refused")
def test_a_more_of_a_deliverable_with_no_round_is_refused(tmp_path: Any) -> None:
    """Given: a run whose invoicer/py.typed has no round.
    When: a more of it is kept.
    Then: it's refused."""
    with pytest.raises(Wrong):
        rounds.keep_more(a_run(tmp_path), [a_more("code", deliverable="invoicer/py.typed")])


@pytest.mark.supports("test_a_more_kept_with_no_decision_changed_is_refused")
def test_the_tree_at_the_rounds_cut_is_the_one_its_opening_commit_holds(tmp_path: Any) -> None:
    """Given: a run whose invoicer's round opened on the walkthrough's tree, which changed after.
    When: the tree at the round's cut is asked.
    Then: it gives the tree as the round opened on it."""
    run = a_run(tmp_path)
    at_open = d.read_json(os.path.join(run.folder, "design-tree.json"))
    opened(run)
    later = d.walkthrough_tree()
    later["goal"]["by"] = "reasoning"
    d.tree_written(run, later)
    assert rounds.at_cut(run, "invoicer").data == at_open
