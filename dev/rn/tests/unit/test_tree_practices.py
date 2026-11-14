"""The unit cases of tree/practices.py, how tree.py reads a best practice, through `loads`, `find`,
`load`, `groups`, and `finisher`, on rn's own best practices and on one made on a run."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
from fault import Wrong
from rn_example import RN, text_of, write
from tree.practices import (
    DECIDE,
    MAKE,
    REFACTOR_CODE,
    REFACTOR_DOC,
    Practice,
    find,
    finisher,
    groups,
    load,
    loads,
)

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")

CODE = os.path.join(RN, "domain", "best-practices", "code", "best-practice.json")


@pytest.mark.supports(
    "test_once_the_generator_is_done_an_evaluator_starts_for_each_group_side_by_side"
)
def test_loads_reads_each_condition_with_its_group_and_practices_in_order():
    """Given rn's code best practice
    When it's read
    Then it holds N1 to N8 in order, N1 of C1 and N8 of C3, and N1's first practice decided"""
    read = loads(text_of(CODE), "code", CODE)
    assert [each.id for each in read.conditions] == [f"N{n}" for n in range(1, 9)]
    assert (read.conditions[0].group, read.conditions[-1].group) == ("C1", "C3")
    assert read.conditions[0].practices[0] == Practice(
        "N1.1", DECIDE, read.conditions[0].practices[0].text
    )


@pytest.mark.supports(
    "test_a_generator_whose_record_skips_the_practices_of_its_best_practice_is_held_at_its_end"
)
def test_loads_numbers_each_practice_by_its_place_and_reads_its_phase():
    """Given rn's code best practice, whose N1 has three practices of deciding and two of making
    When it's read
    Then N1's practices are N1.1 to N1.5, the last two made"""
    first = loads(text_of(CODE), "code", CODE).conditions[0]
    assert [(each.id, each.at) for each in first.practices][3:] == [("N1.4", MAKE), ("N1.5", MAKE)]


@pytest.mark.parametrize("text", ["{", "[]", '{"goal": {}}'])
@pytest.mark.supports(
    "test_once_the_generator_is_done_an_evaluator_starts_for_each_group_side_by_side"
)
def test_loads_refuses_a_text_that_isnt_a_best_practice(text: str):
    """Given `{`, a list, or a goal with no factors
    When it's read
    Then it's refused, naming the file"""
    with pytest.raises(Wrong, match="odd.json"):
        loads(text, "odd", "odd.json")


@pytest.mark.supports(
    "test_once_the_generator_is_done_an_evaluator_starts_for_each_group_side_by_side"
)
def test_groups_are_the_critical_success_factors_in_order():
    """Given rn's code best practice
    When its groups are asked for
    Then they're C1, C2, and C3"""
    assert groups(loads(text_of(CODE), "code", CODE)) == ("C1", "C2", "C3")


@pytest.mark.supports("test_a_best_practice_made_on_a_run_is_taken_over_rns_own_of_its_kind")
def test_find_gives_rns_own_where_no_run_made_one(tmp_path: Any):
    """Given a worktree with no .rn/best-practices/
    When the code best practice is found
    Then it's rn's own"""
    assert find(str(tmp_path), RN, "code") == CODE


@pytest.mark.supports("test_a_best_practice_made_on_a_run_is_taken_over_rns_own_of_its_kind")
def test_find_takes_one_made_on_a_run_over_rns_own(tmp_path: Any):
    """Given a worktree whose .rn/best-practices/code/ holds a best practice
    When the code best practice is found
    Then it's the one made on the run"""
    made = write(str(tmp_path), ".rn/best-practices/code/best-practice.json", text_of(CODE))
    assert find(str(tmp_path), RN, "code") == made


@pytest.mark.supports("test_a_best_practice_made_on_a_run_is_taken_over_rns_own_of_its_kind")
def test_find_gives_one_made_on_a_run_of_a_kind_rn_has_none_of(tmp_path: Any):
    """Given a worktree whose .rn/best-practices/changelog/ holds a best practice
    When the changelog best practice is found
    Then it's the one made on the run"""
    made = write(str(tmp_path), ".rn/best-practices/changelog/best-practice.json", text_of(CODE))
    assert find(str(tmp_path), RN, "changelog") == made


@pytest.mark.supports("test_a_best_practice_made_on_a_run_is_taken_over_rns_own_of_its_kind")
def test_find_refuses_a_kind_neither_holds(tmp_path: Any):
    """Given a worktree with no best practice of its own
    When the changelog best practice is found
    Then it's refused, naming changelog"""
    with pytest.raises(Wrong, match="changelog"):
        find(str(tmp_path), RN, "changelog")


@pytest.mark.supports("test_a_best_practice_made_on_a_run_is_taken_over_rns_own_of_its_kind")
def test_load_reads_the_one_find_gives(tmp_path: Any):
    """Given a worktree whose code best practice has only its first condition
    When the code best practice is loaded
    Then it holds that one condition"""
    whole = json.loads(text_of(CODE))
    first = whole["goal"]["critical_success_factors"][0]
    first["necessary_conditions"] = first["necessary_conditions"][:1]
    whole["goal"]["critical_success_factors"] = [first]
    write(str(tmp_path), ".rn/best-practices/code/best-practice.json", json.dumps(whole))
    assert [each.id for each in load(str(tmp_path), RN, "code").conditions] == ["N1"]


@pytest.mark.parametrize(
    ("kind", "path", "finished_by"),
    [
        ("code", "invoicer/", REFACTOR_CODE),
        ("specific", "tests/test_total.py", REFACTOR_CODE),
        ("specific", "docs/usage.md", REFACTOR_DOC),
        ("readme", "README.md", REFACTOR_DOC),
        ("meta", ".rn/best-practices/code/", REFACTOR_DOC),
    ],
)
@pytest.mark.supports(
    "test_a_generator_whose_record_skips_its_refactor_practices_is_held_at_its_end"
)
def test_finisher_gives_refactor_code_for_code_and_refactor_doc_for_a_document(
    kind: str, path: str, finished_by: str
):
    """Given a deliverable of code, of the kind specific in a Python file or a Markdown file, a
    README, or a best practice
    When the refactor best practice that finishes it is asked for
    Then it's refactor-code for code and the Python file, and refactor-doc for each other"""
    assert finisher(kind, path) == finished_by
