"""The unit cases of tree/cut.py, each role's Cut, through `cut`, `save`, `load`, and `values`,
on a run's folder that each test writes as tree.py keeps it."""

from __future__ import annotations

import os
from typing import Any

import pytest
from rn_example import GOAL, HINTS, TYPED
from rn_parts import ANSWERED, PLAN_SIGNED, RUN, doing, hints, typed, walkthrough
from tree import design, sign_offs
from tree.cut import EVALUATOR, GENERATOR, TREE_KEEPER, cut, load, save, values
from tree.design import Decision
from tree.fault import Wrong
from tree.rounds import LackKept, Place, folder, keep_lack, keep_place

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")

TYPED_DECISION = Decision("Where the marker lies", "invoicer/py.typed, empty", "reasoning")


@pytest.fixture
def run(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> str:
    """The run's folder, from the root of a worktree of the test's own, holding the walkthrough's
    tree with the hints doing and the typed marker holding a decision of its own."""
    root = str(tmp_path)
    monkeypatch.chdir(root)
    os.makedirs(os.path.join(root, RUN))
    design.save(RUN, walkthrough(doing(hints(ANSWERED)), typed(TYPED_DECISION)))
    sign_offs.save(RUN, PLAN_SIGNED)
    return RUN


@pytest.mark.supports("test_the_tree_keeper_starts_with_its_cut_of_the_run_alone")
def test_the_tree_keepers_cut_names_the_runs_design_tree(run: str):
    """Given the run
    When the tree-keeper's cut is asked for
    Then it names the run and its design-tree.json, and no deliverable"""
    found = cut(run, TREE_KEEPER)
    assert (found.run, found.tree) == (run, os.path.join(run, "design-tree.json"))
    assert found.deliverable == "" and found.decisions == ()


@pytest.mark.supports("test_the_hints_once_due_start_a_generator_with_the_cut_of_its_first_round")
def test_the_generators_cut_of_the_hints_is_of_round_1_with_the_goal_and_its_decisions(run: str):
    """Given the hints doing, with no round yet
    When the generator's cut of the hints is asked for
    Then it's of round 1, with the goal, the kind code, and the answer, and no lack or Place"""
    found = cut(run, GENERATOR, HINTS)
    assert (found.round, found.goal, found.kind) == (1, GOAL, "code")
    assert found.decisions == (ANSWERED,) and found.lacks == () and found.place is None


@pytest.mark.supports("test_a_generators_cut_holds_its_deliverables_decisions_and_no_others")
def test_the_generators_cut_holds_no_decision_of_another_deliverable(run: str):
    """Given the typed marker holding a decision of its own
    When the generator's cut of the hints is asked for
    Then that decision isn't in it"""
    assert TYPED_DECISION not in cut(run, GENERATOR, HINTS).decisions


@pytest.mark.supports(
    "test_a_lack_the_people_fall_short_by_changes_its_decision_and_reaches_the_next_round"
)
def test_after_a_round_with_a_lack_kept_the_generators_cut_is_of_the_next_round_with_it(run: str):
    """Given the hints' round 1 with a lack of N2 kept
    When the generator's cut of the hints is asked for
    Then it's of round 2 and holds the lack"""
    os.makedirs(folder(run, HINTS, 1))
    lack = LackKept("N2", "A caller can't tell a rate from an amount.")
    keep_lack(run, HINTS, lack)
    found = cut(run, GENERATOR, HINTS)
    assert found.round == 2 and found.lacks == (lack,)


@pytest.mark.supports("test_the_picked_up_generator_starts_at_the_step_it_stood_at")
def test_a_round_whose_generator_stood_at_a_step_picks_up_in_the_same_round_at_that_place(run: str):
    """Given the hints' round 1 with the generator's Place at step 4, and no Answers
    When the generator's cut of the hints is asked for
    Then it's of round 1 with that Place"""
    os.makedirs(folder(run, HINTS, 1))
    keep_place(run, HINTS, Place("generator", 4))
    found = cut(run, GENERATOR, HINTS)
    assert found.round == 1 and found.place == Place("generator", 4)


@pytest.mark.supports(
    "test_once_the_generator_is_done_an_evaluator_starts_for_each_group_side_by_side"
)
def test_the_evaluators_cut_is_of_the_last_round_and_its_groups_conditions_alone(run: str):
    """Given the hints' round 1
    When the evaluator's cut of the hints for C3 is asked for
    Then it's of round 1, with C3's one condition, N8, and no decision"""
    os.makedirs(folder(run, HINTS, 1))
    found = cut(run, EVALUATOR, HINTS, "C3")
    assert (found.round, found.group, found.conditions) == (1, "C3", ("N8",))
    assert found.decisions == ()


@pytest.mark.parametrize(
    ("role", "more"),
    [
        ("reviewer", ()),
        (GENERATOR, (TYPED,)),
        (GENERATOR, ("README.md",)),
        (EVALUATOR, (HINTS, "C9")),
        (GENERATOR, ()),
    ],
)
@pytest.mark.supports("test_the_hints_once_due_start_a_generator_with_the_cut_of_its_first_round")
def test_cut_refuses_a_role_deliverable_or_group_that_isnt_one_there_is(
    run: str, role: str, more: tuple[str, ...]
):
    """Given the run, the typed marker open
    When the cut of `reviewer`, of a generator of the typed marker or of README.md, of an evaluator
    of the group C9, or of a generator of no deliverable is asked for
    Then it's refused"""
    with pytest.raises(Wrong):
        cut(run, role, *more)


@pytest.mark.supports(
    "test_once_the_generator_is_done_an_evaluator_starts_for_each_group_side_by_side"
)
def test_save_gives_each_start_a_record_of_its_own_and_load_reads_the_cut_back(run: str):
    """Given the generator's cut of the hints
    When it's saved twice
    Then each holds a path and a record of its own in the run's records/, and each loads back as
    saved"""
    found = cut(run, GENERATOR, HINTS)
    first, second = save(found), save(found)
    assert first.record != second.record
    assert first.record.startswith(os.path.join(run, "records", ""))
    assert load(first.path) == first


@pytest.mark.supports("test_the_hints_once_due_start_a_generator_with_the_cut_of_its_first_round")
def test_values_of_the_generators_cut_are_those_its_in_schema_names_each_a_string(run: str):
    """Given the generator's cut of the hints, saved
    When its run values are asked for
    Then they're record, run, deliverable, kind, round, cut, and made, each a string"""
    saved = save(cut(run, GENERATOR, HINTS))
    given = values(saved)
    assert set(given) == {"record", "run", "deliverable", "kind", "round", "cut", "made"}
    assert (given["round"], given["cut"]) == ("1", saved.path)


@pytest.mark.supports(
    "test_once_the_generator_is_done_an_evaluator_starts_for_each_group_side_by_side"
)
def test_values_of_the_evaluators_cut_are_those_its_in_schema_names(run: str):
    """Given the evaluator's cut of the hints for C1, saved
    When its run values are asked for
    Then they're record, run, deliverable, best_practice, group, round, cut, and answers"""
    os.makedirs(folder(run, HINTS, 1))
    given = values(save(cut(run, EVALUATOR, HINTS, "C1")))
    assert set(given) == {
        "record",
        "run",
        "deliverable",
        "best_practice",
        "group",
        "round",
        "cut",
        "answers",
    }


@pytest.mark.supports("test_the_tree_keeper_starts_with_its_cut_of_the_run_alone")
def test_load_refuses_a_file_that_isnt_a_cut(run: str):
    """Given a file holding `{}`
    When it's loaded as a cut
    Then it's refused, naming the file"""
    with open("odd.json", "w", encoding="utf-8") as f:
        f.write("{}")
    with pytest.raises(Wrong, match="odd.json"):
        load("odd.json")
