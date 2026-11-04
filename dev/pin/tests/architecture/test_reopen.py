"""A caller's role reopens a decision with pin:down, each path of the sequence in
dev/pin/architecture.md from start to end: a double of the role, the pinner, reads the tree with
every decision settled, writes it with the point opened or added, and check.py, run by the command
pin:down names from the folder the role works in, reads it from disk and names the decisions open
to decide now, from which the loop of O2 goes on."""

import unittest

import helpers
from helpers import decision


class TestReopen(helpers.PinnerTest):
    def test_a_decision_reopened_opens_each_that_builds_on_it_and_keeps_the_persons_words(self):
        # Given: the walkthrough's tree, every decision settled, as the role reads it
        self.writes()
        self.tree = self.read_json(self.path)
        # When: the caller names the fields of a note to settle again, and the role opens that
        # decision with the one that builds on it
        self.opens("D1", "D3")
        # Then: the tree holds, the reopened decision open to decide now
        self.assertEqual(self.checked(), self.holds("D1"))
        # And: the person's words stay in the grounds of each decision opened
        kept = self.read_json(self.path)["decisions"]
        self.assertEqual(
            [d["grounds"] for d in kept], [d["grounds"] for d in helpers.WALKTHROUGH["decisions"]]
        )

    def test_a_point_no_decision_holds_is_added_open(self):
        # Given: the walkthrough's tree, every decision settled, as the role reads it
        self.writes()
        self.tree = self.read_json(self.path)
        # When: the caller names a point no decision holds, and the role adds it open, joined to
        # what it serves and builds on
        self.tree["decisions"].append(
            decision(
                "D4", what="Whether updated holds seconds", contributes_to=["D3"], builds_on=["D3"]
            )
        )
        self.writes()
        # Then: the tree holds, the added decision open to decide now
        self.assertEqual(self.checked(), self.holds("D4"))


if __name__ == "__main__":
    unittest.main()
