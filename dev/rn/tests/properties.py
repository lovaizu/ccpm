"""Property-based tests of rn's code: no node's ID of a tree stands as a word inside another's, as
Lane's every_item counts an ID answered by the words a file holds; a change never lists among the
nodes it touches a node it changed; a file named out of the home is never made in a throwaway try;
and a run's name is always one word of the shell; on many inputs Hypothesis makes, new on every
run, CI included."""

from __future__ import annotations

import importlib
import os
import string
import sys
import unittest

import helpers
from helpers import runs, testing, trees, tries

# Lane's every_item, taken as rn takes Lane's code, through its link.
sys.path.insert(0, os.path.join(helpers.RN, "hooks", "lane", "domain"))
every_item = importlib.import_module("lanes.every_item")

hypothesis = testing.hypothesis()
given = hypothesis.given
st = hypothesis.strategies

# An intent's ID, as a best practice names one, and what a decision is about.
IDS = st.from_regex(r"Q[1-9][0-9]?", fullmatch=True)
ABOUTS = st.text(string.ascii_lowercase + " ", min_size=1, max_size=8)


@st.composite
def shapes(draw):
    """A tree of a few deliverables, each a few intents of distinct IDs, each a few decisions."""
    deliverables = []
    for n in range(draw(st.integers(1, 3))):
        ids = draw(st.lists(IDS, min_size=1, max_size=3, unique=True))
        intents = [
            {
                "id": i,
                "good": draw(st.booleans()),
                "decisions": [
                    {"about": a, "decided": "x", "by": "user"}
                    for a in draw(st.lists(ABOUTS, max_size=3, unique=True))
                ],
            }
            for i in ids
        ]
        deliverables.append(
            {
                "name": "n",
                "path": f"d{n}.md",
                "kind": "readme",
                "inputs": [f"d{n - 1}.md"] if n and draw(st.booleans()) else [],
                "preconditions": [],
                "status": "open",
                "intents": intents,
            }
        )
    return {"goal": {"decided": "g", "by": "user"}, "deliverables": deliverables}


class TestTrees(unittest.TestCase):
    @given(shapes())
    def test_no_id_stands_as_a_word_inside_another(self, tree):
        # Given: a tree's nodes, each by its ID
        ids = [n for n, _ in trees.nodes(tree)]
        # When: rn looks for each ID in each other ID
        # Then: none stands there as a word of its own
        for a in ids:
            for b in ids:
                if a != b:
                    self.assertFalse(every_item.answered(a, b), (a, b))

    @given(shapes(), shapes())
    def test_a_change_never_touches_a_node_it_changed(self, before, after):
        keys = trees.changed(before, after)
        found = dict(trees.nodes(after))
        for node in trees.touched(before, after, keys):
            self.assertNotIn(found[node], keys)


class TestTries(unittest.TestCase):
    @given(st.lists(st.sampled_from(["..", ".", "a", "b", "/"]), min_size=1, max_size=4))
    def test_a_path_out_of_the_home_is_never_taken_as_under_it(self, parts):
        path = "/".join(parts)
        inside = os.path.normpath(os.path.join("/home", path)).startswith("/home/")
        if tries.under_home(path):
            self.assertTrue(inside, path)


class TestRuns(unittest.TestCase):
    @given(st.text(max_size=40))
    def test_a_runs_name_is_one_word_of_the_shell(self, request):
        name = runs.words(request)
        self.assertRegex(name, r"^[a-z0-9]+(-[a-z0-9]+)*$")
