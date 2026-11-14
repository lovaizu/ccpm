"""The unit cases of tree/record.py, the form of a role's record, through `add`, `load`, and
`keep_result`. An entry's ID is a step's number from 1 or a practice's ID, so the cases take each
end of the numbers it takes, as boundary value analysis does."""

from __future__ import annotations

import os
from typing import Any

import pytest
from tree.fault import Wrong
from tree.record import Entry, Record, add, keep_result, load

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")


@pytest.fixture
def path(tmp_path: Any) -> str:
    return os.path.join(str(tmp_path), "records", "generator-1.json")


@pytest.mark.supports("test_record_refuses_an_id_that_is_neither_a_step_nor_a_practice")
def test_add_makes_the_record_with_its_first_entry(path: str):
    """Given no record
    When step 1 of generator is added
    Then the record holds that one entry"""
    assert add(path, Entry("generator", "1", "Read the cut.")) == Record(
        (Entry("generator", "1", "Read the cut."),)
    )


@pytest.mark.supports("test_record_refuses_an_id_that_is_neither_a_step_nor_a_practice")
def test_add_keeps_each_entry_in_the_order_added(path: str):
    """Given a record holding step 1 of generator
    When the practice N1.1 of code is added
    Then the record holds step 1 and then N1.1"""
    add(path, Entry("generator", "1", "Read the cut."))
    add(path, Entry("code", "N1.1", "Listed the decisions."))
    assert [each.id for each in load(path).entries] == ["1", "N1.1"]


@pytest.mark.parametrize("id", ["1", "12", "N1.1", "N16.9"])
@pytest.mark.supports("test_record_refuses_an_id_that_is_neither_a_step_nor_a_practice")
def test_add_takes_a_step_from_1_and_a_practice_id(path: str, id: str):
    """Given no record
    When step 1, step 12, practice N1.1, or practice N16.9 is added
    Then the record holds it"""
    assert add(path, Entry("generator", id, "Done.")).entries[-1].id == id


@pytest.mark.parametrize("id", ["0", "-1", "step-one", "N1", "N1.", "n1.1", ""])
@pytest.mark.supports("test_record_refuses_an_id_that_is_neither_a_step_nor_a_practice")
def test_add_refuses_an_id_neither_a_step_from_1_nor_a_practice(path: str, id: str):
    """Given no record
    When step 0, step -1, `step-one`, `N1`, `N1.`, `n1.1`, or no ID is added
    Then it's refused, naming what an ID takes, and no record is made"""
    with pytest.raises(Wrong, match="N6.2"):
        add(path, Entry("generator", id, "Done."))
    assert not os.path.exists(path)


@pytest.mark.supports("test_record_refuses_an_id_that_is_neither_a_step_nor_a_practice")
def test_add_refuses_an_entry_that_gave_nothing(path: str):
    """Given no record
    When step 1 is added with nothing it gave
    Then it's refused, naming `gave`"""
    with pytest.raises(Wrong, match="gave"):
        add(path, Entry("generator", "1", ""))


@pytest.mark.supports("test_record_refuses_an_id_that_is_neither_a_step_nor_a_practice")
def test_load_of_no_record_is_an_empty_one(path: str):
    """Given no record
    When it's loaded
    Then it holds nothing"""
    assert load(path) == Record()


@pytest.mark.supports("test_record_refuses_an_id_that_is_neither_a_step_nor_a_practice")
def test_load_refuses_a_record_out_of_its_form(path: str):
    """Given a record holding an entry with no `gave`
    When it's loaded
    Then it's refused, naming the file"""
    os.makedirs(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write('{"entries": [{"of": "generator", "step": 1}]}')
    with pytest.raises(Wrong, match="generator-1.json"):
        load(path)


@pytest.mark.supports(
    "test_a_generator_whose_record_holds_each_step_and_practice_ends_with_its_result_kept"
)
def test_keep_result_keeps_it_beside_the_entries(path: str):
    """Given a record holding step 1
    When `done` is kept
    Then the record holds step 1 and the result `done`"""
    add(path, Entry("generator", "1", "Read the cut."))
    keep_result(path, "done")
    assert load(path) == Record((Entry("generator", "1", "Read the cut."),), "done")
