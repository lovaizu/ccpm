"""Properties of tree.py over many design trees: a tree built from the goal down, each decision
serving a question or one made before it and building only on decisions before it, holds, and
gives as ready exactly the open decisions on decided ones; cutting every contribution of one
decision makes it reach no question; and a decision decided on an open one is out of order."""

import unittest

import helpers
from helpers import tree

hypothesis = helpers.testing.hypothesis()
given, st = hypothesis.given, hypothesis.strategies


@st.composite
def grown(draw) -> dict:
    """A design tree grown from the goal down: questions Q1 to Qn, each served by a decision, and
    decisions each serving a question or a decision before it, building on decisions before it,
    and decided only where each it builds on is decided."""
    questions = [f"Q{n}" for n in range(1, draw(st.integers(1, 4)) + 1)]
    decisions: list[dict] = []
    for q in questions:
        decisions.append(helpers.decision(f"D{len(decisions) + 1}", contributes_to=[q]))
    for _ in range(draw(st.integers(0, 6))):
        before = [d["id"] for d in decisions]
        serves = draw(
            st.lists(st.sampled_from(questions + before), min_size=1, max_size=3, unique=True)
        )
        on = draw(st.lists(st.sampled_from(before), max_size=3, unique=True))
        decisions.append(
            helpers.decision(f"D{len(decisions) + 1}", contributes_to=serves, builds_on=on)
        )
    by_id = {d["id"]: d for d in decisions}
    for d in decisions:
        if draw(st.booleans()) and all(by_id[i]["decided"] is not None for i in d["builds_on"]):
            d.update(decided="x", settled_by=draw(st.sampled_from(tree.SETTLED_BY)), grounds=["g"])
    return helpers.made(*decisions, questions=tuple(questions))


class TestProperties(unittest.TestCase):
    @given(grown())
    def test_a_tree_grown_from_the_goal_down_holds(self, data):
        self.assertEqual(tree.form_faults(data), [])
        self.assertEqual(tree.problems(data), [])

    @given(grown())
    def test_ready_is_each_open_decision_on_decided_ones(self, data):
        decided = {d["id"] for d in data["decisions"] if d["decided"] is not None}
        for d in data["decisions"]:
            on_decided = d["decided"] is None and set(d["builds_on"]) <= decided
            self.assertEqual(d["id"] in tree.ready(data), on_decided)

    @given(grown(), st.data())
    def test_a_decision_cut_from_all_it_serves_reaches_no_question(self, data, drawn):
        cut = drawn.draw(st.sampled_from(data["decisions"]))
        cut["contributes_to"] = []
        self.assertIn(
            f"{cut['id']} reaches no question, so it serves nothing.", tree.problems(data)
        )

    @given(grown(), st.data())
    def test_a_decision_decided_on_an_open_one_is_out_of_order(self, data, drawn):
        open_ones = [d["id"] for d in data["decisions"] if d["decided"] is None]
        hypothesis.assume(open_ones)
        on = drawn.draw(st.sampled_from(open_ones))
        late = helpers.settled("Dx", builds_on=[on])
        data["decisions"].append(late)
        self.assertIn(
            f"Dx is decided before {on}, which it builds on and which is still open.",
            tree.problems(data),
        )


if __name__ == "__main__":
    unittest.main()
