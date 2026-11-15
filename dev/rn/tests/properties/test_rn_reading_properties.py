"""The property-based cases of what rn reads from outside its code, as rn's Test strategy names
them: the design tree, the records, and the adapters' input. Whatever JSON or text they're given,
each either reads it or refuses it in the way its contract names, and never fails otherwise, as a
fault of the input is the user's or a role's to mend, never a crash of rn's."""

from __future__ import annotations

import io
import json
import os
import tempfile
from typing import Any

import pytest
from fault import Wrong
from hypothesis import given
from hypothesis import strategies as st
from record import form
from tree import design
from tree.runs import Run

from dev.rn.tests.unit import rn_data as d

pytestmark = pytest.mark.xfail(strict=True, reason="rn's readers have empty bodies")

JSON = st.recursive(
    st.none() | st.booleans() | st.integers() | st.text(max_size=8),
    lambda inner: (
        st.lists(inner, max_size=4) | st.dictionaries(st.text(max_size=8), inner, max_size=4)
    ),
    max_leaves=12,
)
# What a design tree and a record hold, with values of any JSON, so that the cases reach their
# checks past the top level.
TREE = st.fixed_dictionaries({"goal": JSON, "deliverables": st.lists(JSON, max_size=3)})
RECORD = st.fixed_dictionaries({"entries": st.lists(JSON, max_size=3)}, optional={"kept": JSON})


@pytest.mark.supports("test_tree_py_refuses_a_change_that_leaves_the_design_trees_form")
@given(st.one_of(JSON, TREE))
def test_any_design_tree_is_read_or_refused_as_out_of_form(held: Any) -> None:
    """Given: a run whose design-tree.json holds any JSON.
    When: the tree is read.
    Then: it gives the tree as held, or it's refused as out of form."""
    with tempfile.TemporaryDirectory() as folder:
        with open(os.path.join(folder, "design-tree.json"), "w", encoding="utf-8") as f:
            json.dump(held, f)
        try:
            tree = design.read(Run("20261115-x", folder, "rn-20261115-x", folder))
        except Wrong:
            return
        assert tree.data == held


@pytest.mark.supports("test_record_py_refuses_an_entry_out_of_its_form")
@given(st.one_of(JSON, RECORD))
def test_any_record_is_read_or_refused_as_out_of_form(held: Any) -> None:
    """Given: a record that holds any JSON.
    When: it's read.
    Then: it gives as many entries as it holds, or it's refused as out of form."""
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "record.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(held, f)
        try:
            record = form.read(path)
        except Wrong:
            return
        assert isinstance(held, dict) and len(record.entries) == len(held["entries"])


@pytest.mark.supports("test_up_alone_in_the_runs_worktree_picks_up_where_it_stopped")
@given(st.one_of(st.text(max_size=40), JSON.map(json.dumps)))
def test_any_input_of_the_adapter_of_records_gives_results_or_why(given_text: str) -> None:
    """Given: a folder in no run's worktree, and any text on the adapter of records' standard
    input.
    When: the adapter runs.
    Then: it gives 0 with results in Lane's form, or 1 with why, and no traceback."""
    with tempfile.TemporaryDirectory() as folder:
        code, out, err = d.adapter("records").main(io.StringIO(given_text), folder)
    assert code in (0, 1) and "Traceback" not in err
    if code == 0:
        assert set(json.loads(out)) == {"results"}


@pytest.mark.supports("test_a_request_starts_a_run_anew_with_the_tree_keepers_start_first")
@given(st.one_of(st.text(max_size=40), JSON.map(json.dumps)))
def test_any_input_of_the_adapter_of_a_starts_text_gives_a_text_none_or_why(
    given_text: str,
) -> None:
    """Given: a folder in no run's worktree, and any text on the adapter of a start's text's
    standard input.
    When: the adapter runs for the generator.
    Then: it gives 1 with why, and no traceback, as no run's worktree holds the folder."""
    with tempfile.TemporaryDirectory() as folder:
        code, out, err = d.adapter("text").main(["generator"], io.StringIO(given_text), folder)
    assert (code, out) == (1, "") and err and "Traceback" not in err
