"""The unit cases of steering/rounds.py, each Round and Fix of a task read from its folder: none
where it has none yet; each in the order made, with each role's result it holds; a result out of
its schema refused; and each result of the work out of its schema named."""

from __future__ import annotations

import os
from typing import Any

import pytest
import rn_files
from fault import Wrong
from place import WorkPlace
from steering.rounds import entries, faults, folder_of

MADE = {"result": "made", "files": [rn_files.COMMAND]}


def test_a_task_with_no_folder_has_no_entry(tmp_path: Any) -> None:
    """Given a folder of a task's Rounds that doesn't exist.
    When its entries are read.
    Then there are none."""
    assert entries(str(tmp_path / "none"), rn_files.SCHEMAS) == []


def test_each_entry_comes_in_the_order_made_with_its_results(tmp_path: Any) -> None:
    """Given a task's folder with 10-content holding a generator's result, 02-content holding
    none, 03-fix, and a file that names no entry.
    When its entries are read.
    Then 02-content, 03-fix, and 10-content come in that order, each with the results it holds."""
    root = str(tmp_path)
    rn_files.write_json(os.path.join(root, "10-content", "generator.json"), MADE)
    os.makedirs(os.path.join(root, "02-content"))
    os.makedirs(os.path.join(root, "03-fix"))
    rn_files.write_json(os.path.join(root, "notes.json"), {})
    found = [(each.stage, each.number, each.results) for each in entries(root, rn_files.SCHEMAS)]
    assert found == [("content", 2, {}), ("fix", 3, {}), ("content", 10, {"generator": MADE})]


def test_a_result_out_of_its_schema_is_refused(tmp_path: Any) -> None:
    """Given a Round whose generator's result has a word its schema doesn't take.
    When its entries are read.
    Then Wrong names the generator's result."""
    rn_files.write_json(
        os.path.join(str(tmp_path), "01-content", "generator.json"), {"result": "x"}
    )
    with pytest.raises(Wrong, match="the generator's result"):
        entries(str(tmp_path), rn_files.SCHEMAS)


def test_each_result_of_the_work_out_of_its_schema_is_named(tmp_path: Any) -> None:
    """Given the work whose task 001 holds a generator's result made and task 002 one out of its
    schema.
    When the work's faults are asked.
    Then the one of task 002 alone is named."""
    work = WorkPlace(str(tmp_path), "20261126-invoice-from-statement")
    rn_files.write_json(os.path.join(folder_of(work, "001"), "01-content", "generator.json"), MADE)
    bad = os.path.join(folder_of(work, "002"), "01-content", "generator.json")
    rn_files.write_json(bad, {"result": "x"})
    found = faults(work, rn_files.SCHEMAS)
    assert (len(found), bad in found[0]) == (1, True)
