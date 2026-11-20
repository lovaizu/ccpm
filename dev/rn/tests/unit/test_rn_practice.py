"""The unit cases of practice.py, where each kind's best practice lies and what of it each role
gets: `kinds` of rn's own best practices, and of a run's own beside them, before them, and a folder
of neither; `read` of a best practice that holds its form, one missing, one that isn't JSON, and one
out of its form; `items` at each stage, of kinds whose conditions lie out of their IDs' order, and
of a stage of neither; `judged` without any practice; and `refactoring` of each of rn's kinds and
of a kind near one named. `read` holds a best practice to rn's own form,
domain/schemas/best-practice.schema.json, which rn installs."""

from __future__ import annotations

import json
import os
import shutil
from typing import Any

import pytest
import rn_files
from fault import Wrong
from practice import items, judged, kinds, read, refactoring

pytestmark = pytest.mark.xfail(strict=True, reason="practice.py's bodies raise NotImplementedError")


def rns_kinds() -> dict[str, str]:
    """Each folder of rn's best practices that holds a best-practice.json, by its name."""
    return {
        name: os.path.join(rn_files.PRACTICES, name)
        for name in os.listdir(rn_files.PRACTICES)
        if os.path.isfile(os.path.join(rn_files.PRACTICES, name, "best-practice.json"))
    }


def normalized(found: dict[str, str]) -> dict[str, str]:
    """Each kind's folder, normalized, so that a closing `/` tells nothing apart."""
    return {kind: os.path.normpath(folder) for kind, folder in found.items()}


@pytest.fixture
def worktree(tmp_path: Any) -> str:
    """A run's worktree with no best practice of its own."""
    folder = os.path.join(str(tmp_path), "worktree")
    os.makedirs(folder)
    return folder


def own(worktree: str, kind: str, practice: Any) -> str:
    """Writes the run's own best practice of the kind, and gives its folder."""
    folder = os.path.join(worktree, ".rn", "best-practices", kind)
    rn_files.write_json(os.path.join(folder, "best-practice.json"), practice)
    return folder


@pytest.mark.supports("test_a_runs_own_best_practice_is_taken_before_rns")
def test_kinds_of_a_run_with_none_of_its_own_are_rns(worktree: str):
    """Given a run's worktree with no .rn/best-practices/
    When the kinds are asked
    Then each is rn's, by its folder's name"""
    assert normalized(kinds(rn_files.RN, worktree)) == normalized(rns_kinds())


@pytest.mark.supports("test_a_runs_own_best_practice_is_taken_before_rns")
def test_kinds_take_a_runs_own_best_practice_before_rns(worktree: str):
    """Given a run's worktree holding its own best practice of the kind light
    When the kinds are asked
    Then light is the run's own folder, and each other kind rn's"""
    folder = own(worktree, "light", rn_files.practice("light"))
    expected = rns_kinds()
    expected["light"] = folder
    assert normalized(kinds(rn_files.RN, worktree)) == normalized(expected)


@pytest.mark.supports("test_a_runs_own_best_practice_is_taken_before_rns")
def test_kinds_add_each_kind_made_on_the_run(worktree: str):
    """Given a run's worktree holding its own best practices of two kinds rn has none of,
    `invoice` and `guide`, made by meta deliverables
    When the kinds are asked
    Then each of rn's kinds and both of the run's are given"""
    expected = rns_kinds()
    for kind in ("invoice", "guide"):
        expected[kind] = own(worktree, kind, rn_files.practice("light"))
    assert normalized(kinds(rn_files.RN, worktree)) == normalized(expected)


@pytest.mark.supports("test_a_runs_own_best_practice_is_taken_before_rns")
def test_kinds_leave_out_a_folder_with_no_best_practice_json(worktree: str):
    """Given a run's worktree whose .rn/best-practices/readme/ holds a template alone, and whose
    .rn/best-practices/notes/ holds a README alone
    When the kinds are asked
    Then readme is rn's, and notes is no kind"""
    for kind, name in (("readme", "template.md"), ("notes", "README.md")):
        path = os.path.join(worktree, ".rn", "best-practices", kind, name)
        os.makedirs(os.path.dirname(path))
        with open(path, "w", encoding="utf-8") as f:
            f.write("# notes\n")
    assert normalized(kinds(rn_files.RN, worktree)) == normalized(rns_kinds())


@pytest.mark.supports("test_a_runs_own_best_practice_is_taken_before_rns")
def test_kinds_of_a_plugin_with_one_best_practice_is_that_one(tmp_path: Any, worktree: str):
    """Given an rn whose domain/best-practices/ holds light alone
    When the kinds are asked
    Then light alone is given"""
    plugin = os.path.join(str(tmp_path), "rn")
    folder = os.path.join(plugin, "domain", "best-practices", "light")
    shutil.copytree(os.path.join(rn_files.PRACTICES, "light"), folder)
    assert normalized(kinds(plugin, worktree)) == {"light": os.path.normpath(folder)}


@pytest.mark.supports("test_a_runs_own_best_practice_is_taken_before_rns")
def test_read_of_a_folder_with_no_best_practice_is_refused_naming_the_file(tmp_path: Any):
    """Given a folder with no best-practice.json
    When it is read
    Then it raises Wrong naming best-practice.json"""
    with pytest.raises(Wrong, match="best-practice.json"):
        read(str(tmp_path))


@pytest.mark.supports("test_a_runs_own_best_practice_is_taken_before_rns")
def test_read_of_a_best_practice_that_isnt_json_is_refused_naming_the_file(tmp_path: Any):
    """Given a folder whose best-practice.json isn't JSON
    When it is read
    Then it raises Wrong naming best-practice.json"""
    with open(os.path.join(str(tmp_path), "best-practice.json"), "w", encoding="utf-8") as f:
        f.write("{goal")
    with pytest.raises(Wrong, match="best-practice.json"):
        read(str(tmp_path))


@pytest.mark.supports("test_a_runs_own_best_practice_is_taken_before_rns")
def test_read_of_a_best_practice_out_of_its_form_is_refused_naming_its_first_fault(tmp_path: Any):
    """Given a folder whose best-practice.json is light's without its inputs, which its form
    requires
    When it is read
    Then it raises Wrong naming best-practice.json and inputs"""
    practice = rn_files.practice("light")
    del practice["inputs"]
    rn_files.write_json(os.path.join(str(tmp_path), "best-practice.json"), practice)
    with pytest.raises(Wrong, match="best-practice.json") as raised:
        read(str(tmp_path))
    assert "inputs" in str(raised.value)


@pytest.mark.supports("test_the_generators_make_is_held_to_its_best_practices_make_items")
def test_items_of_light_at_each_stage_are_its_ids_in_order():
    """Given rn's light best practice, read from JSON
    When its items at decide, and at make, are asked
    Then decide gives N1.1, N1.2, N1.3, and make N1.4, N1.5, N2.1, N3.1, each its condition's ID
    and its place among the condition's items"""
    practice = rn_files.practice("light")
    assert items(practice, "decide") == ["N1.1", "N1.2", "N1.3"]
    assert items(practice, "make") == ["N1.4", "N1.5", "N2.1", "N3.1"]


@pytest.mark.supports("test_the_generators_make_is_held_to_its_best_practices_make_items")
@pytest.mark.parametrize("kind", ["readme", "test-design", "meta", "design-tree"])
@pytest.mark.parametrize("at", ["decide", "make"])
def test_items_keep_the_best_practices_order_whatever_its_ids(kind: str, at: str):
    """Given rn's best practice of the kind, read from JSON, test-design's and meta's conditions
    lying out of their IDs' order, and design-tree's with no make item under N1
    When its items at the stage are asked
    Then each item of the stage is given in the best practice's order, by its condition's ID and
    its place among the condition's items"""
    assert items(rn_files.practice(kind), at) == rn_files.items_at(kind, at)


@pytest.mark.supports("test_the_generators_make_is_held_to_its_best_practices_make_items")
def test_items_of_a_best_practice_with_none_at_the_stage_are_none():
    """Given light's best practice with each item marked make
    When its items at decide are asked
    Then there are none"""
    practice = rn_files.practice("light")
    for factor in practice["goal"]["critical_success_factors"]:
        for each in factor["necessary_conditions"]:
            for item in each["items"]:
                item["at"] = "make"
    assert items(practice, "decide") == []


@pytest.mark.supports("test_the_generators_make_is_held_to_its_best_practices_make_items")
@pytest.mark.parametrize("at", ["Make", "deciding", "", "try"])
def test_items_at_a_stage_of_neither_are_refused(at: str):
    """Given rn's light best practice
    When its items at a stage that is neither decide nor make are asked
    Then it raises Wrong"""
    with pytest.raises(Wrong):
        items(rn_files.practice("light"), at)


@pytest.mark.supports("test_the_evaluators_cut_holds_only_what_the_people_have")
@pytest.mark.parametrize("kind", ["light", "readme", "test-design"])
def test_judged_gives_the_goal_and_each_condition_without_its_practice(kind: str):
    """Given rn's best practice of the kind, read from JSON
    When what an evaluator judges by is asked
    Then it gives the goal's what and each factor, each condition with its id, about, and what
    alone, in the best practice's order, with no why and no item"""
    given = judged(rn_files.practice(kind))
    assert given == rn_files.judged_by(kind)
    assert "items" not in json.dumps(given) and '"why"' not in json.dumps(given)


CODE_KINDS = ("code", "software-design", "test-design", "test-implementation")


@pytest.mark.supports(
    "test_a_deliverable_with_each_condition_good_is_refactored_by_its_refactor_best_practice"
)
@pytest.mark.parametrize("kind", sorted(rns_kinds()))
def test_refactoring_of_each_of_rns_kinds(kind: str):
    """Given each kind of rn's best practices
    When the kind it's refactored by is asked
    Then code, software-design, test-design, and test-implementation give refactor-code, light
    None, and every other kind refactor-doc"""
    by = "refactor-code" if kind in CODE_KINDS else None if kind == "light" else "refactor-doc"
    assert refactoring(kind) == by


@pytest.mark.supports(
    "test_a_deliverable_with_each_condition_good_is_refactored_by_its_refactor_best_practice"
)
@pytest.mark.parametrize("kind", ["codes", "Code", "code-review", "test", "lights", "invoice", ""])
def test_refactoring_of_a_kind_near_one_named_is_refactor_doc(kind: str):
    """Given a kind that nearly matches code or light, or one that a run made, such as `invoice`
    When the kind it's refactored by is asked
    Then it gives refactor-doc, as each other kind does"""
    assert refactoring(kind) == "refactor-doc"


@pytest.mark.supports("test_a_runs_own_best_practice_is_taken_before_rns")
@pytest.mark.parametrize("kind", sorted(rns_kinds()))
def test_read_holds_each_of_rns_best_practices_to_rns_form(kind: str):
    """Given each of rn's best practices, which domain/schemas/best-practice.schema.json holds
    When its folder is read
    Then it gives its best-practice.json as the JSON holds it, refusing none"""
    assert read(os.path.join(rn_files.PRACTICES, kind)) == rn_files.practice(kind)


@pytest.mark.supports("test_a_runs_own_best_practice_is_taken_before_rns")
@pytest.mark.parametrize(
    ("broken", "named"),
    [
        (lambda p: p.update(notes="more"), "notes"),
        (lambda p: p["goal"].update(critical_success_factors=[]), "critical_success_factors"),
        (
            lambda p: p["goal"]["critical_success_factors"][0]["necessary_conditions"][0]["items"][
                0
            ].update(at="try"),
            "at",
        ),
        (
            lambda p: p["goal"]["critical_success_factors"][0]["necessary_conditions"][0].update(
                why=""
            ),
            "why",
        ),
    ],
)
def test_read_of_a_best_practice_out_of_rns_form_is_refused_naming_its_place(
    tmp_path: Any, broken: Any, named: str
):
    """Given a run's own best practice that leaves rn's form at one place: a key the form doesn't
    hold, no factor, an item at a stage of neither, or an empty why
    When it is read
    Then it raises Wrong naming best-practice.json and that place"""
    practice = rn_files.practice("light")
    broken(practice)
    rn_files.write_json(os.path.join(str(tmp_path), "best-practice.json"), practice)
    with pytest.raises(Wrong, match="best-practice.json") as raised:
        read(str(tmp_path))
    assert named in str(raised.value)
