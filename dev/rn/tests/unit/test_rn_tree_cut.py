"""The unit cases of tree/cut.py, which decides the Cut of each start of a role. The Cut turns on
the role, which deliverables are doing, which of them a start that runs holds, whether the
deliverable was done before, and where a start of the deliverable stood, so the cases take each
role and one that isn't rn's, none doing, the first and the second held, a deliverable never done
and one done before, each group of an evaluator, and a start that stood at a step; and the Cut
that a start took, by its record, or a record that names no start."""

from __future__ import annotations

import copy
import os
from typing import Any

import pytest
from fault import Wrong
from tree import cut, place, practices, rounds
from tree.more import More
from tree.place import Place

from dev.rn.tests.unit import rn_data as d

BOTH_DOING = d.with_status(d.walkthrough_tree(), "doing", "doing")


def doing_run(tmp: Any, data: dict[str, Any] | None = None) -> Any:
    run = d.run_of(d.repository(str(tmp)))
    d.tree_written(run, data or BOTH_DOING)
    return run


def judged_round(run: Any) -> None:
    """invoicer's first round made and answered by each group of the code best practice, which a
    round of content judges, committed."""
    d.write_json(os.path.join(run.worktree, rounds.made_path(run, "invoicer", True)), d.made())
    for group, judged in enumerate(practices.judged_by(run, d.RN, "code")):
        if judged.kind == "code":
            answers = rounds.answers_path(run, "invoicer", group)
            d.write_json(os.path.join(run.worktree, answers), d.answers(list(judged.conditions)))
    d.git(run.worktree, "add", "-A")
    d.git(run.worktree, "commit", "-q", "-m", "Round 1")


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


@pytest.mark.supports("test_a_request_starts_a_run_anew_with_the_tree_keepers_start_first")
def test_no_tree_keeper_start_is_due_while_one_runs(tmp_path: Any) -> None:
    """Given: a run with the walkthrough's tree, whose tree-keeper runs.
    When: the Cut of the tree-keeper's next start is asked.
    Then: it gives none, as the main conversation resumes the tree-keeper that runs."""
    run = doing_run(tmp_path)
    first = cut.next_start(run, d.design(BOTH_DOING), "tree-keeper", [])
    assert first is not None
    assert cut.next_start(run, d.design(BOTH_DOING), "tree-keeper", [dict(first.values)]) is None


@pytest.mark.supports("test_the_generator_starts_with_its_cut_of_the_first_deliverable_doing")
def test_the_generators_cut_is_of_the_first_deliverable_doing(tmp_path: Any) -> None:
    """Given: a run with both of the walkthrough's deliverables doing, and no start running.
    When: the Cut of the generator's next start is asked.
    Then: it names invoicer, its kind, its best practices, where it writes its Made, and the part
    of the tree it makes it from, with only its own decision, and no commit it was done at, as it
    was never done."""
    run = doing_run(tmp_path)
    given = cut.next_start(run, d.design(BOTH_DOING), "generator", [])
    assert given is not None
    assert given.part["deliverable"] == "invoicer" and given.part["kind"] == "code"
    part = given.part["cut"]
    assert isinstance(part, dict) and part["name"] == "Type hints in each file of invoicer"
    assert [e["condition"] for e in part["decisions"]] == ["N1"]
    assert part["more"] == []
    assert "done_at" not in part


@pytest.mark.supports("test_a_deliverable_done_before_is_reworked_from_the_commit_it_was_done_at")
def test_the_generators_cut_of_a_deliverable_done_before_gives_the_commit_it_was_done_at(
    tmp_path: Any,
) -> None:
    """Given: a run whose design tree marked invoicer done, then doing again, with no start running.
    When: the Cut of the generator's next start is asked.
    Then: its part of the tree gives the commit that marked invoicer done."""
    run = doing_run(tmp_path, d.with_status(d.walkthrough_tree(), "done", "open"))
    done_at = d.git(run.worktree, "rev-parse", "HEAD").strip()
    data = d.with_status(d.walkthrough_tree(), "doing", "open")
    d.tree_written(run, data)
    given = cut.next_start(run, d.design(data), "generator", [])
    assert given is not None and given.part["deliverable"] == "invoicer"
    assert d.part(given)["cut"]["done_at"] == done_at


@pytest.mark.supports("test_a_deliverable_done_before_is_reworked_from_the_commit_it_was_done_at")
def test_a_generator_starts_a_new_round_once_a_decision_changes_after_the_rounds_cut(
    tmp_path: Any,
) -> None:
    """Given: a run with invoicer alone doing, made in its first round with no More kept, answered,
    and then its decision of N1 changed in the design tree.
    When: the Cut of the generator's next start is asked.
    Then: it's of invoicer, writing its Made in round 2 by the code best practice, as the rounds of
    content start again from the design."""
    data = d.with_status(d.walkthrough_tree(), "doing", "open")
    run = doing_run(tmp_path, data)
    judged_round(run)
    changed = copy.deepcopy(data)
    (decision,) = changed["deliverables"][0]["necessary_conditions"][0]["decisions"]
    decision["decided"] = "each file of invoicer but its tests"
    d.tree_written(run, changed)
    given = cut.next_start(run, d.design(changed), "generator", [])
    assert given is not None and given.part["deliverable"] == "invoicer"
    assert given.values["made"] == rounds.made_path(run, "invoicer", True)
    assert str(given.part["best_practice"]).rstrip("/").endswith("best-practices/code")


@pytest.mark.supports("test_a_more_the_people_fall_short_by_reaches_the_next_rounds_generator")
def test_the_next_rounds_cut_carries_each_more_kept_with_its_best_practice_and_decision(
    tmp_path: Any,
) -> None:
    """Given: a run with invoicer alone doing, made in its first round and answered, its decision of
    N1 changed,
    and the more of N2 of refactor-code kept, naming that decision.
    When: the Cut of the generator's next start is asked.
    Then: it's of invoicer's round 2, and its part of the tree carries the More kept with its best
    practice, condition, decision, and good_when."""
    data = d.with_status(d.walkthrough_tree(), "doing", "open")
    run = doing_run(tmp_path, data)
    judged_round(run)
    changed = copy.deepcopy(data)
    (decision,) = changed["deliverables"][0]["necessary_conditions"][0]["decisions"]
    decision["decided"] = "each file of invoicer but its tests"
    d.tree_written(run, changed)
    path = "deliverables/0/necessary_conditions/0/decisions/0"
    kept = More("invoicer", "refactor-code", "N2", path, "Each name says what it holds.")
    rounds.keep_more(run, [kept])
    given = cut.next_start(run, d.design(changed), "generator", [])
    assert given is not None and given.values["made"] == rounds.made_path(run, "invoicer", True)
    assert d.part(given)["cut"]["more"] == [
        {
            "best_practice": "refactor-code",
            "condition": "N2",
            "decision": path,
            "good_when": "Each name says what it holds.",
        }
    ]


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


@pytest.mark.supports("test_a_round_of_structure_follows_the_rounds_of_content")
def test_a_round_of_content_answered_with_no_decision_changed_gives_one_of_structure(
    tmp_path: Any,
) -> None:
    """Given: a run with invoicer alone doing, made in its first round and answered by each group
    of the code best practice, with no decision under it changed since the round's cut.
    When: the Cut of a generator's and of an evaluator's next start is asked.
    Then: the generator's is of round 2 by the refactor-code best practice, and no evaluator's is
    due, as the round of content is judged whole."""
    data = d.with_status(d.walkthrough_tree(), "doing", "open")
    run = doing_run(tmp_path, data)
    judged_round(run)
    given = cut.next_start(run, d.design(data), "generator", [])
    assert given is not None and given.values["made"] == rounds.made_path(run, "invoicer", True)
    assert str(given.part["best_practice"]).rstrip("/").endswith("best-practices/refactor-code")
    assert cut.next_start(run, d.design(data), "evaluator", []) is None


@pytest.mark.supports("test_a_node_with_no_file_gets_no_round")
def test_a_node_with_no_file_gets_no_generator(tmp_path: Any) -> None:
    """Given: a run whose first deliverable doing is a node with no file.
    When: the Cut of the generator's next start is asked.
    Then: it's of the second deliverable."""
    data = copy.deepcopy(BOTH_DOING)
    data["deliverables"][0]["file"] = False
    given = cut.next_start(doing_run(tmp_path, data), d.design(data), "generator", [])
    assert given is not None and given.part["deliverable"] == "invoicer/py.typed"


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
@pytest.mark.parametrize(
    "name",
    [
        "nobody.json",
        "001-generator.json",
        "001-generator.invoicer.json",
        "001-evaluator.invoicer.r1.json",
        "001-generator.nowhere.r1.json",
    ],
)
def test_a_record_that_names_no_start_is_refused(tmp_path: Any, name: str) -> None:
    """Given: a run with no start.
    When: the Cut is asked by a record that names no role, no start of a round, a start out of its
    form, an evaluator's start with no group, or a deliverable the tree doesn't hold.
    Then: it's refused."""
    run = doing_run(tmp_path)
    with pytest.raises(Wrong):
        cut.of_record(run, os.path.join(run.folder, "records", name))
