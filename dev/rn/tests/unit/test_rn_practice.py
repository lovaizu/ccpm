"""The unit cases of practice.py, where each kind's best practice lies and what of it each role
gets: `kinds` of rn's best practices, and of a folder with none; `read` of a best practice, one
missing, and one that isn't JSON; `judged` without any practice; and `refactoring` of a kind of
code, of general, and of another kind.
dev/scripts/practices.py holds each of rn's best practices to its schema."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
import rn_files
from fault import Wrong
from practice import judged, kinds, read, refactoring


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


def test_kinds_are_rns_best_practices_by_their_folders_names() -> None:
    """Given rn's folder
    When the kinds are asked
    Then each is rn's, by its folder's name"""
    assert normalized(kinds(rn_files.RN)) == normalized(rns_kinds())


def test_kinds_leave_out_a_folder_with_no_best_practice_json(tmp_path: Any) -> None:
    """Given a plugin folder whose best practices hold general, and readme with a template alone
    When the kinds are asked
    Then general alone is a kind"""
    top = os.path.join(str(tmp_path), "domain", "best-practices")
    rn_files.write_json(
        os.path.join(top, "general", "best-practice.json"), rn_files.practice("general")
    )
    os.makedirs(os.path.join(top, "readme"))
    with open(os.path.join(top, "readme", "template.md"), "w", encoding="utf-8") as f:
        f.write("# notes\n")
    assert normalized(kinds(str(tmp_path))) == {"general": os.path.join(top, "general")}


def test_read_gives_the_best_practice_json():
    """Given rn's best practice of the kind general
    When its folder is read
    Then it gives its best-practice.json as the JSON holds it"""
    assert read(os.path.join(rn_files.PRACTICES, "general")) == rn_files.practice("general")


def test_read_of_a_folder_with_no_best_practice_is_refused_naming_the_file(tmp_path: Any):
    """Given a folder with no best-practice.json
    When it is read
    Then it raises Wrong naming best-practice.json"""
    with pytest.raises(Wrong, match="best-practice.json"):
        read(str(tmp_path))


def test_read_of_a_best_practice_that_isnt_json_is_refused_naming_the_file(tmp_path: Any):
    """Given a folder whose best-practice.json isn't JSON
    When it is read
    Then it raises Wrong naming best-practice.json"""
    with open(os.path.join(str(tmp_path), "best-practice.json"), "w", encoding="utf-8") as f:
        f.write("{goal")
    with pytest.raises(Wrong, match="best-practice.json"):
        read(str(tmp_path))


def test_judged_gives_the_goal_and_each_condition_without_its_practice():
    """Given rn's best practice of the kind readme, read from JSON
    When what an evaluator judges by is asked
    Then it gives the goal's what and each factor, each condition with its id, about, and what
    alone, in the best practice's order, with no why and no item"""
    given = judged(rn_files.practice("readme"))
    assert given == rn_files.judged_by("readme")
    assert "items" not in json.dumps(given) and '"why"' not in json.dumps(given)


@pytest.mark.parametrize(
    ("kind", "by"),
    [("test-design", "refactor-code"), ("general", None), ("invoice", "refactor-doc")],
)
def test_refactoring_of_a_kind(kind: str, by: str | None):
    """Given a kind of code, general, or another kind, one that the work made among them
    When the kind it's refactored by is asked
    Then it gives refactor-code, None, or refactor-doc"""
    assert refactoring(kind) == by
