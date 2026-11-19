"""The property-based tests of reading the design tree and the Rounds, as rn's Test strategy names
them: an AI writes each, so the run's folder takes forms that no developer foresees. Each finds no
counterexample, by hypothesis, and quality.sh runs them in CI."""

from __future__ import annotations

import json
import os
import tempfile
from typing import Any

import pytest
from fault import Wrong
from hypothesis import given
from hypothesis import strategies as st
from rn_bench import RN, plan
from tree import design, rounds

# Any value that JSON holds.
JSON = st.recursive(
    st.none() | st.booleans() | st.integers() | st.text(max_size=8),
    lambda inner: (
        st.lists(inner, max_size=3) | st.dictionaries(st.text(max_size=8), inner, max_size=3)
    ),
    max_leaves=8,
)
# A start of a Round: its number, whether it's the generator, its group, and its slot.
STARTS = st.sets(
    st.tuples(
        st.integers(1, 12),
        st.booleans(),
        st.sampled_from(["C1", "C2", "C10"]),
        st.integers(1, 11),
    ),
    max_size=8,
)


def name(generator: bool, group: str, slot: int) -> str:
    """The file name of a start's Cut, without `.cut.json`."""
    base = "generator" if generator else f"evaluator-{group}"
    return base + (f".{slot}" if slot > 1 else "")


@pytest.mark.supports("test_each_rounds_results_lie_beside_their_cuts")
@given(STARTS, st.data())
def test_each_gives_one_start_for_each_cut_in_the_order_they_were_cut(
    starts: set[tuple[int, bool, str, int]], data: Any
):
    """Given any Cuts of any Rounds, of the generator or an evaluator of a group, in any slot,
    each with its result beside it or none
    When rounds.each reads them
    Then it gives one start for each Cut, by the Round's number, the generator first, the
    evaluators by their group, and each by its slot, with its result where one is there"""
    held = {(r, g, "" if g else c, s) for r, g, c, s in starts}
    with_result = data.draw(st.sets(st.sampled_from(sorted(held)))) if held else set()
    with tempfile.TemporaryDirectory() as run:
        for number, generator, group, slot in held:
            folder = os.path.join(run, "rounds", str(number))
            os.makedirs(folder, exist_ok=True)
            base = os.path.join(folder, name(generator, group, slot))
            with open(base + ".cut.json", "w", encoding="utf-8") as f:
                json.dump({"slot": slot}, f)
            if (number, generator, group, slot) in with_result:
                with open(base + ".json", "w", encoding="utf-8") as f:
                    json.dump({"result": "made"}, f)
        got = [(s.round, s.role == "generator", s.group, s.slot) for s in rounds.each(run)]
        results = {
            (s.round, s.role == "generator", s.group, s.slot) for s in rounds.each(run) if s.result
        }
    assert got == sorted(held, key=lambda s: (s[0], not s[1], s[2], s[3]))
    assert results == with_result


def places(value: Any, at: tuple[Any, ...] = ()) -> list[tuple[Any, ...]]:
    """Each place in a JSON value, by the keys and indexes that lead to it."""
    found = [at]
    if isinstance(value, dict):
        found += [p for k, v in value.items() for p in places(v, (*at, k))]
    elif isinstance(value, list):
        found += [p for i, v in enumerate(value) for p in places(v, (*at, i))]
    return found


def put(value: Any, at: tuple[Any, ...], new: Any) -> Any:
    """The value with what lies at the place given replaced by `new`."""
    if not at:
        return new
    value[at[0]] = put(value[at[0]], at[1:], new)
    return value


@pytest.mark.supports("test_an_edit_out_of_form_is_refused_before_its_commit")
@given(st.data(), JSON)
def test_a_design_tree_with_any_value_anywhere_is_held_or_refused(data: Any, new: Any):
    """Given the walkthrough's plan with any value of JSON put in place of any part of it
    When design.read reads it
    Then it gives the tree or refuses with Wrong, and with nothing else"""
    tree = plan()
    tree = put(tree, data.draw(st.sampled_from(places(tree))), new)
    with tempfile.TemporaryDirectory() as top:
        run = os.path.join(top, ".rn", "20261119-invoices")
        os.makedirs(run)
        with open(os.path.join(run, "design-tree.json"), "w", encoding="utf-8") as f:
            json.dump(tree, f)
        try:
            design.read(run, RN)
        except Wrong:
            pass
