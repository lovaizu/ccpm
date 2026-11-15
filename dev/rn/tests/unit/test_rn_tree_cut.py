"""The unit cases of tree/cut.py, which decides the Cut of each start of a role. The Cut turns on
the role, which deliverables are doing, which of them a start that runs holds, and where a start of
the deliverable stood, so the cases take each role and one that isn't rn's, none doing, the first
and the second held, each group of an evaluator, and a start that stood at a step; and the Cut
that a start took, by its record, or a record that names no start."""

from __future__ import annotations

import os
from typing import Any

import pytest
from fault import Wrong
from tree import cut, place, rounds
from tree.place import Place

from dev.rn.tests.unit import rn_data as d

pytestmark = pytest.mark.xfail(strict=True, reason="tree/cut.py has empty bodies")

BOTH_DOING = d.with_status(d.walkthrough_tree(), "doing", "doing")


def doing_run(tmp: Any, data: dict[str, Any] | None = None) -> Any:
    run = d.run_of(d.repository(str(tmp)))
    d.tree_written(run, data or BOTH_DOING)
    return run


@pytest.mark.supports("test_a_request_starts_a_run_anew_with_the_tree_keepers_start_first")
def test_the_tree_keepers_cut_names_the_design_tree_and_its_best_practice(tmp_path: Any) -> None:
    """Given: a run with the walkthrough's tree.
    When: the Cut of the tree-keeper's next start is asked, with no start running.
    Then: it gives the tree-keeper's run values, its record in the run's records/, the run's
    design-tree.json, and the design tree best practice's folder, and its part holds no more."""
    run = doing_run(tmp_path)
    given = cut.next_start(run, d.design(BOTH_DOING), "tree-keeper", [])
    assert given is not None and given.role == "tree-keeper"
    assert set(given.part) == {"record", "tree", "best_practice"}
    assert d.part(given)["tree"].endswith(os.path.join(".rn", d.NAME, "design-tree.json"))
    assert given.values["record"] == given.part["record"]


@pytest.mark.supports("test_the_generator_starts_with_its_cut_of_the_first_deliverable_doing")
def test_the_generators_cut_is_of_the_first_deliverable_doing(tmp_path: Any) -> None:
    """Given: a run with both of the walkthrough's deliverables doing, and no start running.
    When: the Cut of the generator's next start is asked.
    Then: it names invoicer, its kind, its best practices, where it writes its Made, and the part
    of the tree it makes it from, with only its own decision."""
    run = doing_run(tmp_path)
    given = cut.next_start(run, d.design(BOTH_DOING), "generator", [])
    assert given is not None
    assert given.part["deliverable"] == "invoicer" and given.part["kind"] == "code"
    part = given.part["cut"]
    assert isinstance(part, dict) and part["name"] == "Type hints in each file of invoicer"
    assert [e["condition"] for e in part["decisions"]] == ["N1"]
    assert part["more"] == []


@pytest.mark.supports("test_a_second_generator_starts_with_the_next_deliverable_doing")
def test_a_deliverable_that_a_start_runs_on_is_passed_over(tmp_path: Any) -> None:
    """Given: a run with both deliverables doing, and a generator running on invoicer.
    When: the Cut of the generator's next start is asked.
    Then: it's of invoicer/py.typed, with a record other than the running start's."""
    run = doing_run(tmp_path)
    first = cut.next_start(run, d.design(BOTH_DOING), "generator", [])
    assert first is not None
    second = cut.next_start(run, d.design(BOTH_DOING), "generator", [dict(first.values)])
    assert second is not None and second.part["deliverable"] == "invoicer/py.typed"
    assert second.values["record"] != first.values["record"]


@pytest.mark.supports("test_no_generator_start_is_due_while_every_deliverable_doing_waits")
def test_no_work_waits_where_none_is_doing_or_each_is_held(tmp_path: Any) -> None:
    """Given: a run with no deliverable doing, and a run with both doing and a generator running on
    each.
    When: the Cut of the generator's next start is asked of each.
    Then: each gives none."""
    idle = doing_run(tmp_path / "idle", d.walkthrough_tree())
    assert cut.next_start(idle, d.design(), "generator", []) is None
    run = doing_run(tmp_path / "busy")
    tree = d.design(BOTH_DOING)
    first = cut.next_start(run, tree, "generator", [])
    assert first is not None
    second = cut.next_start(run, tree, "generator", [dict(first.values)])
    assert second is not None
    assert cut.next_start(run, tree, "generator", [dict(first.values), dict(second.values)]) is None


@pytest.mark.supports("test_one_evaluator_starts_for_each_group_of_necessary_conditions")
def test_each_evaluator_takes_the_first_group_that_no_running_start_holds(tmp_path: Any) -> None:
    """Given: a run with invoicer alone doing, made in its first round.
    When: the Cut of an evaluator's next start is asked, then again with that start running.
    Then: the first names the code best practice's first group, and the second its next group,
    each with only what the deliverable's people have."""
    data = d.with_status(d.walkthrough_tree(), "doing", "open")
    run = doing_run(tmp_path, data)
    d.write_json(os.path.join(run.worktree, rounds.made_path(run, "invoicer", True)), d.made())
    tree = d.design(data)
    first = cut.next_start(run, tree, "evaluator", [])
    assert first is not None and first.part["conditions"] == ["N1", "N2", "N3"]
    second = cut.next_start(run, tree, "evaluator", [dict(first.values)])
    assert second is not None and second.part["conditions"] == ["N4", "N5", "N6", "N7"]
    people = {"record", "deliverable", "name", "best_practice", "conditions", "answers"}
    assert set(first.part) == people


@pytest.mark.supports("test_up_alone_in_the_runs_worktree_picks_up_where_it_stopped")
def test_a_start_of_a_deliverable_that_stood_at_a_step_starts_at_it(tmp_path: Any) -> None:
    """Given: a run with invoicer doing, whose generator stood at step 2 by its Place.
    When: the Cut of the generator's next start is asked.
    Then: its part names step 2."""
    data = d.with_status(d.walkthrough_tree(), "doing", "open")
    run = doing_run(tmp_path, data)
    first = cut.next_start(run, d.design(data), "generator", [])
    assert first is not None
    record = first.values["record"]
    place.write(rounds.place_path(run, record), Place(record, 2, ("invoicer/totals.py",)))
    again = cut.next_start(run, d.design(data), "generator", [])
    assert again is not None and d.part(again)["cut"]["step"] == 2


@pytest.mark.supports("test_a_role_starts_with_only_the_cut_that_tree_py_gave_for_it")
def test_a_role_that_isnt_rns_is_refused(tmp_path: Any) -> None:
    """Given: a run with both deliverables doing.
    When: the Cut of a start of the role writer is asked.
    Then: it's refused, naming the role."""
    with pytest.raises(Wrong, match="writer"):
        cut.next_start(doing_run(tmp_path), d.design(BOTH_DOING), "writer", [])


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
def test_the_cut_a_start_took_is_given_by_its_record(tmp_path: Any) -> None:
    """Given: a run whose generator's start took the Cut of invoicer, its round opened.
    When: the Cut is asked by the start's record.
    Then: it gives the same Cut."""
    run = doing_run(tmp_path)
    given = cut.next_start(run, d.design(BOTH_DOING), "generator", [])
    assert given is not None
    d.write_json(os.path.join(run.worktree, str(given.part["made"])), d.made())
    d.git(run.worktree, "add", "-A")
    d.git(run.worktree, "commit", "-q", "-m", "The round")
    assert cut.of_record(run, given.values["record"]) == given


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
def test_a_record_that_names_no_start_is_refused(tmp_path: Any) -> None:
    """Given: a run with no start.
    When: the Cut is asked by a record that names no start of the run.
    Then: it's refused, naming the record."""
    run = doing_run(tmp_path)
    with pytest.raises(Wrong):
        cut.of_record(run, os.path.join(run.folder, "records", "nobody.json"))
