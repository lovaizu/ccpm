"""The unit cases of record/form.py, which decides a Record's form on disk: an entry added, a record
read, and a result kept. An entry is a step from 1 up or a practice by an ID of the form N<n>.<m>,
with where its result lies, a path and a line or lines, so the cases take step 1, step 0, IDs in
and out of that form, places in and out of theirs, several entries at once and none; a record not
yet there, one in form, and one out of it."""

from __future__ import annotations

import os
from typing import Any

import pytest
from fault import CantRun, Wrong
from record import form
from record.form import Entry, Kept

from dev.rn.tests.unit import rn_data as d

STEP = Entry("generator", 1, None, "invoicer/__init__.py:1")
PRACTICE = Entry("code", None, "N6.2", "tests/test_lines.py:12-30")


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
        Entry("generator", 0, None, "a.py:1"),
        Entry("code", None, "X1", "a.py:1"),
        Entry("code", None, "N6", "a.py:1"),
        Entry("generator", 1, None, ""),
        Entry("generator", 1, None, "a.py"),
        Entry("generator", 1, None, "a.py:0"),
        Entry("generator", 1, None, "Read the Cut."),
        Entry("generator", 1, "N6.2", "a.py:1"),
        Entry("generator", None, None, "a.py:1"),
        Entry("", 1, None, "a.py:1"),
    ],
)
def test_an_entry_out_of_its_form_is_refused(tmp_path: Any, entry: Entry) -> None:
    """Given: no record at the path.
    When: an entry is added after one in form, with step 0, an ID out of the form N<n>.<m>, no
    place, a place with no line, line 0, or words, both a step and a practice, neither, or no
    prompt or best practice.
    Then: it's refused, and no record is made."""
    path = os.path.join(tmp_path, "record.json")
    with pytest.raises(Wrong):
        form.add(path, STEP, entry)
    assert not os.path.exists(path)


@pytest.mark.supports("test_record_py_refuses_an_entry_out_of_its_form")
def test_no_entry_is_refused(tmp_path: Any) -> None:
    """Given: no record at the path.
    When: no entry is added.
    Then: it's refused, and no record is made."""
    path = os.path.join(tmp_path, "record.json")
    with pytest.raises(Wrong):
        form.add(path)
    assert not os.path.exists(path)


@pytest.mark.supports("test_a_generators_done_result_is_kept_in_its_record")
def test_several_entries_added_at_once_are_read_back_in_their_order(tmp_path: Any) -> None:
    """Given: no record at the path.
    When: a step and a practice are added at once.
    Then: the record reads back both in the order given."""
    path = os.path.join(tmp_path, "record.json")
    form.add(path, STEP, PRACTICE)
    assert form.read(path).entries == (STEP, PRACTICE)


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
        {"entries": [{"of": "generator", "step": 0, "where": "a.py:1"}]},
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
