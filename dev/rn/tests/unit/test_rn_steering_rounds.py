"""The unit cases of steering/rounds.py, each Round and Fix of a deliverable read from its folder:
none where it has none yet; each in the order made, with each role's result it holds; and a
result out of its schema refused."""

from __future__ import annotations

import os
from typing import Any

import pytest
import rn_files
from fault import Wrong
from steering.rounds import entries

MADE = {"result": "made", "files": [rn_files.COMMAND]}


def test_a_deliverable_with_no_folder_has_no_entry(tmp_path: Any) -> None:
    """Given a folder of a deliverable's Rounds that doesn't exist.
    When its entries are read.
    Then there are none."""
    assert entries(str(tmp_path / "none"), rn_files.SCHEMAS) == []


def test_each_entry_comes_in_the_order_made_with_its_results(tmp_path: Any) -> None:
    """Given a deliverable's folder with content-10 holding a generator's result, content-2 holding
    none, fix-3, and a file that names no entry.
    When its entries are read.
    Then content-2, fix-3, and content-10 come in that order, each with the results it holds."""
    root = str(tmp_path)
    rn_files.write_json(os.path.join(root, "content-10", "generator.json"), MADE)
    os.makedirs(os.path.join(root, "content-2"))
    os.makedirs(os.path.join(root, "fix-3"))
    rn_files.write_json(os.path.join(root, "notes.json"), {})
    found = [(each.stage, each.number, each.results) for each in entries(root, rn_files.SCHEMAS)]
    assert found == [("content", 2, {}), ("fix", 3, {}), ("content", 10, {"generator": MADE})]


def test_a_result_out_of_its_schema_is_refused(tmp_path: Any) -> None:
    """Given a Round whose generator's result has a word its schema doesn't take.
    When its entries are read.
    Then Wrong names the generator's result."""
    rn_files.write_json(os.path.join(str(tmp_path), "content-1", "generator.json"), {"result": "x"})
    with pytest.raises(Wrong, match="the generator's result"):
        entries(str(tmp_path), rn_files.SCHEMAS)
