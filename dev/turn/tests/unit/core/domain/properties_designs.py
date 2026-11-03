"""Properties over many design trees and templates: the branches hold each decision once and no
join crosses two of them, and the parts made from them hold the work's design; the groups hold each
question once, and two questions asking of one part, or both of the whole, share a group."""

import unittest

import helpers
from helpers import designs, templates

hypothesis = helpers.testing.hypothesis()
given, st = hypothesis.given, hypothesis.strategies


@st.composite
def trees(draw) -> dict:
    """A design tree of up to eight decisions, each serving a question or decisions before it and
    building on decisions before it."""
    decisions: list[dict] = []
    for n in range(1, draw(st.integers(0, 8)) + 1):
        before = [d["id"] for d in decisions]
        serves = draw(
            st.lists(st.sampled_from(["Q1", *before]), min_size=1, max_size=3, unique=True)
        )
        on = draw(st.lists(st.sampled_from(before), max_size=2, unique=True)) if before else []
        decisions.append(helpers.decision(f"D{n}", serves, on))
    return {"questions": [{"id": "Q1", "what": "q"}], "decisions": decisions}


@st.composite
def templates_drawn(draw) -> dict:
    """A template's questions, each about one to three of five parts, or about the whole."""
    parts = ["a", "b", "c", "d", "e", "the whole"]
    abouts = draw(
        st.lists(st.lists(st.sampled_from(parts), min_size=1, max_size=3, unique=True), min_size=1)
    )
    return {"benefits": [{"id": f"Q{n}", "about": ", ".join(a)} for n, a in enumerate(abouts, 1)]}


class TestBranches(unittest.TestCase):
    @given(trees())
    def test_each_decision_lies_in_one_branch_and_no_join_crosses_two(self, tree):
        found = designs.branches(tree)
        flat = [d for b in found for d in b]
        self.assertEqual(sorted(flat), sorted(d["id"] for d in tree["decisions"]))
        where = {d: n for n, b in enumerate(found) for d in b}
        for a, b in designs.joins(tree):
            self.assertEqual(where[a], where[b])

    @given(trees())
    def test_the_parts_made_hold_the_tree_once_each_given_its_paths(self, tree):
        work = designs.parted({"paths": ["w"], "commands": [], "parts": []}, tree)
        for part in work["parts"]:
            part["paths"] = [f"w/{part['id']}"]
        self.assertEqual(designs.work_faults(work, tree), [])


class TestGroups(unittest.TestCase):
    @given(templates_drawn())
    def test_each_question_lies_in_one_group_with_each_sharing_a_part(self, data):
        found = templates.groups(data, "k")
        where = {q: n for n, g in enumerate(found) for q in g["questions"]}
        self.assertEqual(sorted(where), sorted(f"k/{q['id']}" for q in data["benefits"]))
        abouts = {
            f"k/{q['id']}": {a.strip() for a in q["about"].split(",")} for q in data["benefits"]
        }
        for q, a in abouts.items():
            for r, b in abouts.items():
                whole = "the whole" in a and "the whole" in b
                plain = "the whole" not in a and "the whole" not in b and a & b
                if whole or plain:
                    self.assertEqual(where[q], where[r])


if __name__ == "__main__":
    unittest.main()
