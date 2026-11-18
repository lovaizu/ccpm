"""The unit cases of tree/course.py, which decides the course of a deliverable's rounds. The course
turns on how many rounds of content and of structure ran since the latest sign-off, whether each
round's groups answered, whether a decision changed since the latest round's cut and under which
condition, and which conditions a More kept names, so the cases take a first round, a round of
content after a change and after none, the limit of each kind, the groups of a later round, and a
deliverable put up and sent back."""

from __future__ import annotations

import copy
import os
from typing import Any

import pytest
from tree import course, practices, rounds, sign_offs
from tree.more import More
from tree.sign_offs import Kind

from dev.rn.tests.unit import rn_data as d

DATA = d.with_status(d.walkthrough_tree(), "doing", "open")


def a_run(tmp: Any) -> Any:
    run = d.run_of(d.repository(str(tmp)))
    d.tree_written(run, DATA)
    return run


def round_judged(run: Any, tree: dict[str, Any], structure: bool = False) -> None:
    """invoicer's next round made with the tree written, and answered by each group that it
    judges, of the code best practice or of refactor-code, all committed at once."""
    d.write_json(os.path.join(run.folder, "design-tree.json"), tree)
    d.write_json(os.path.join(run.worktree, rounds.made_path(run, "invoicer", True)), d.made())
    judged = course.rounds_of(run, d.RN, d.design(tree), "invoicer")[-1]
    groups = practices.judged_by(run, d.RN, "code")
    assert judged.structure == structure
    for group in judged.groups:
        path = rounds.answers_path(run, "invoicer", group)
        d.write_json(os.path.join(run.worktree, path), d.answers(list(groups[group].conditions)))
    d.git(run.worktree, "add", "-A")
    d.git(run.worktree, "commit", "-q", "-m", "A round")


def n1_changed(tree: dict[str, Any], to: str) -> dict[str, Any]:
    changed = copy.deepcopy(tree)
    changed["deliverables"][0]["necessary_conditions"][0]["decisions"][0]["decided"] = to
    return changed


def content(run: Any) -> tuple[int, ...]:
    """The number of each group of the code best practice."""
    return tuple(
        n for n, g in enumerate(practices.judged_by(run, d.RN, "code")) if g.kind == "code"
    )


@pytest.mark.supports("test_a_round_of_structure_follows_the_rounds_of_content")
def test_a_deliverable_with_no_round_takes_a_first_round_of_content(tmp_path: Any) -> None:
    """Given: invoicer with no round.
    When: its next round is asked.
    Then: it's round 1, of content."""
    run = a_run(tmp_path)
    assert course.next_round(run, d.RN, d.design(DATA), "invoicer") == course.Round(1, False, ())


@pytest.mark.supports("test_a_round_of_structure_follows_the_rounds_of_content")
def test_a_round_not_yet_answered_whole_gives_no_next_round(tmp_path: Any) -> None:
    """Given: invoicer's first round made, with no Answers.
    When: its next round is asked.
    Then: none is, as the round waits for its evaluators."""
    run = a_run(tmp_path)
    d.write_json(os.path.join(run.worktree, rounds.made_path(run, "invoicer", True)), d.made())
    assert course.next_round(run, d.RN, d.design(DATA), "invoicer") is None


@pytest.mark.supports("test_a_round_of_structure_follows_the_rounds_of_content")
def test_a_first_round_judges_each_group_of_the_kinds_best_practice(tmp_path: Any) -> None:
    """Given: invoicer's first round made.
    When: its course is asked.
    Then: it's of content, judging each group of the code best practice."""
    run = a_run(tmp_path)
    round_judged(run, DATA)
    assert course.rounds_of(run, d.RN, d.design(DATA), "invoicer") == (
        course.Round(1, False, content(run)),
    )


@pytest.mark.supports("test_a_round_of_structure_follows_the_rounds_of_content")
def test_a_later_round_of_content_judges_only_the_groups_whose_decisions_changed(
    tmp_path: Any,
) -> None:
    """Given: invoicer's first round judged, then its decision of N1 changed.
    When: its next round is asked, and then its course once that round is made.
    Then: round 2 is of content, judging only the group that holds N1."""
    run = a_run(tmp_path)
    round_judged(run, DATA)
    changed = n1_changed(DATA, "each file of invoicer but its tests")
    assert course.next_round(run, d.RN, d.design(changed), "invoicer") == course.Round(2, False, ())
    round_judged(run, changed)
    later = course.rounds_of(run, d.RN, d.design(changed), "invoicer")[-1]
    held = practices.judged_by(run, d.RN, "code")
    assert [held[g].conditions for g in later.groups] == [held[0].conditions]
    assert "N1" in held[0].conditions


@pytest.mark.supports("test_a_round_of_structure_follows_the_rounds_of_content")
def test_two_rounds_of_content_give_one_of_structure_even_with_a_change(tmp_path: Any) -> None:
    """Given: invoicer's two rounds of content judged, then its decision of N1 changed again.
    When: its next round is asked.
    Then: round 3 is of structure, as two rounds of content ran."""
    run = a_run(tmp_path)
    round_judged(run, DATA)
    second = n1_changed(DATA, "each file of invoicer but its tests")
    round_judged(run, second)
    third = n1_changed(DATA, "each file")
    assert course.next_round(run, d.RN, d.design(third), "invoicer") == course.Round(3, True, ())


@pytest.mark.supports("test_a_round_of_structure_follows_the_rounds_of_content")
def test_a_round_of_structure_judges_the_refactor_groups_and_then_only_those_of_a_more(
    tmp_path: Any,
) -> None:
    """Given: invoicer's round of content and then one of structure judged, the More of N2 of
    refactor-code kept with a decision changed, and a third round made.
    When: its course is asked.
    Then: round 2 judges each group of refactor-code, and round 3 only the one that holds N2."""
    run = a_run(tmp_path)
    round_judged(run, DATA)
    round_judged(run, DATA, structure=True)
    changed = n1_changed(DATA, "each file of invoicer but its tests")
    path = "deliverables/0/necessary_conditions/0/decisions/0"
    rounds.keep_more(run, [More("invoicer", "refactor-code", "N2", path, "Each name says.")])
    round_judged(run, changed, structure=True)
    each = course.rounds_of(run, d.RN, d.design(changed), "invoicer")
    held = practices.judged_by(run, d.RN, "code")
    refactor = tuple(n for n, g in enumerate(held) if g.kind == "refactor-code")
    assert each[1].groups == refactor
    assert [held[g].kind for g in each[2].groups] == ["refactor-code"]
    assert all("N2" in held[g].conditions for g in each[2].groups)


@pytest.mark.supports("test_a_round_of_structure_follows_the_rounds_of_content")
def test_two_rounds_of_structure_or_one_with_no_change_end_the_rounds(tmp_path: Any) -> None:
    """Given: invoicer's round of content and one of structure judged, with no decision changed;
    then a second round of structure after a change, judged, and another change.
    When: its next round, and its last, are asked at each.
    Then: no next round is, each time, as the deliverable is ready to put up, and the last is
    none until the second round of structure, round 3, ran."""
    run = a_run(tmp_path)
    round_judged(run, DATA)
    round_judged(run, DATA, structure=True)
    assert course.next_round(run, d.RN, d.design(DATA), "invoicer") is None
    changed = n1_changed(DATA, "each file of invoicer but its tests")
    assert course.next_round(run, d.RN, d.design(changed), "invoicer") == course.Round(3, True, ())
    assert course.last(run, d.RN, d.design(changed), "invoicer") == 0
    round_judged(run, changed, structure=True)
    again = n1_changed(DATA, "each file")
    assert course.next_round(run, d.RN, d.design(again), "invoicer") is None
    assert course.last(run, d.RN, d.design(again), "invoicer") == 3


@pytest.mark.supports("test_a_deliverable_sent_back_starts_its_rounds_again")
def test_a_deliverable_put_up_and_sent_back_starts_its_rounds_again(tmp_path: Any) -> None:
    """Given: invoicer's two rounds of content and two of structure judged, then put up, which
    keeps round 4, and sent back with its decision of N1 changed.
    When: its next round is asked.
    Then: round 5 is of content, as the rounds since the sign-off are none."""
    run = a_run(tmp_path)
    round_judged(run, DATA)
    second = n1_changed(DATA, "each file of invoicer but its tests")
    round_judged(run, second)
    round_judged(run, second, structure=True)
    third = n1_changed(DATA, "each file")
    round_judged(run, third, structure=True)
    put = sign_offs.put_up(run, Kind.DELIVERABLE, "invoicer")
    assert put.round == 4 and sign_offs.as_json(put)["round"] == 4
    sign_offs.decide(run, False)
    fourth = n1_changed(DATA, "each file but __init__.py")
    assert course.next_round(run, d.RN, d.design(fourth), "invoicer") == course.Round(5, False, ())
    assert course.of_structure(run, d.RN, d.design(fourth), "invoicer", 5) is False
