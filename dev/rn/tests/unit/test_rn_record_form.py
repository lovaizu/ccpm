"""The unit cases of record/form.py, which decides a Record's form on disk: an entry added, a record
read, and a result kept. An entry is a step from 1 up or a practice by an ID of the form N<n>.<m>,
with what it left, so the cases take step 1, step 0, IDs in and out of that form, and what it left
of one character and of none; a record not yet there, one in form, and one out of it."""

from __future__ import annotations

import os
from typing import Any

import pytest
from fault import CantRun, Wrong
from record import form
from record.form import Entry, Kept

from dev.rn.tests.unit import rn_data as d

STEP = Entry("generator", 1, None, "Read the Cut.")
PRACTICE = Entry("code", None, "N6.2", "Wrote the test first.")


@pytest.mark.supports("test_a_generators_done_result_is_kept_in_its_record")
def test_entries_added_are_read_back_in_their_order(tmp_path: Any) -> None:
    """Given: no record at the path.
    When: a step and then a practice are added.
    Then: the record is made, and reads back both in the order added, with no result kept."""
    path = os.path.join(tmp_path, "records", "1-generator.json")
    form.add(path, STEP)
    form.add(path, PRACTICE)
    assert form.read(path).entries == (STEP, PRACTICE)
    assert form.read(path).kept is None


@pytest.mark.supports("test_record_py_refuses_an_entry_out_of_its_form")
@pytest.mark.parametrize(
    "entry",
    [
        Entry("generator", 0, None, "x"),
        Entry("code", None, "X1", "x"),
        Entry("code", None, "N6", "x"),
        Entry("generator", 1, None, ""),
        Entry("generator", 1, "N6.2", "x"),
        Entry("generator", None, None, "x"),
    ],
)
def test_an_entry_out_of_its_form_is_refused(tmp_path: Any, entry: Entry) -> None:
    """Given: no record at the path.
    When: an entry is added with step 0, an ID out of the form N<n>.<m>, nothing it left, both a
    step and a practice, or neither.
    Then: it's refused, and no record is made."""
    path = os.path.join(tmp_path, "record.json")
    with pytest.raises(Wrong):
        form.add(path, entry)
    assert not os.path.exists(path)


@pytest.mark.supports("test_record_py_refuses_an_entry_out_of_its_form")
def test_an_entry_that_left_one_character_is_taken(tmp_path: Any) -> None:
    """Given: no record at the path.
    When: a step is added that left one character.
    Then: the record reads it back."""
    path = os.path.join(tmp_path, "record.json")
    form.add(path, Entry("generator", 1, None, "x"))
    assert form.read(path).entries == (Entry("generator", 1, None, "x"),)


@pytest.mark.supports("test_up_alone_in_the_runs_worktree_picks_up_where_it_stopped")
def test_a_record_not_yet_there_reads_with_no_entries(tmp_path: Any) -> None:
    """Given: no record at the path.
    When: it's read.
    Then: it gives no entry and no result kept."""
    held = form.read(os.path.join(tmp_path, "record.json"))
    assert held.entries == () and held.kept is None


@pytest.mark.supports("test_up_alone_in_the_runs_worktree_picks_up_where_it_stopped")
@pytest.mark.parametrize(
    "held",
    [
        {"entries": [{"of": "generator", "step": 0, "gave": "x"}]},
        {"items": []},
        [],
        {"entries": [], "kept": {}},
    ],
)
def test_a_record_out_of_its_form_is_refused(tmp_path: Any, held: Any) -> None:
    """Given: a record with step 0, no entries, not an object, or a result kept with no role.
    When: it's read.
    Then: it's refused."""
    with pytest.raises(Wrong):
        form.read(d.write_json(os.path.join(tmp_path, "record.json"), held))


@pytest.mark.supports("test_up_alone_in_the_runs_worktree_picks_up_where_it_stopped")
def test_a_record_that_cant_be_read_cant_run(tmp_path: Any) -> None:
    """Given: a folder at the record's path.
    When: it's read.
    Then: it couldn't run."""
    path = os.path.join(tmp_path, "record.json")
    os.makedirs(path)
    with pytest.raises(CantRun):
        form.read(path)


@pytest.mark.supports("test_a_generators_done_result_is_kept_in_its_record")
def test_a_result_kept_is_read_back_beside_the_entries(tmp_path: Any) -> None:
    """Given: a record with a step.
    When: the generator's result done is kept.
    Then: the record reads back the step, and done kept by the generator."""
    path = os.path.join(tmp_path, "record.json")
    form.add(path, STEP)
    form.keep(path, Kept("generator", "done"))
    held = form.read(path)
    assert held.entries == (STEP,) and held.kept == Kept("generator", "done")
