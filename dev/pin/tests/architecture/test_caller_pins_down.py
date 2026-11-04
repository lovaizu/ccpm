"""A caller's role has a work's design pinned down, O2 of pin's UX, each path of its sequence in
dev/pin/architecture.md from start to end: a double of the role, the pinner, writes the tree each
step calls for at the path the caller names, with keys of the caller's own, and check.py, run by
the command pin:down names from the folder the role works in, reads it from disk and gives the
Check result the step calls for. The person's answers reach the double through the main
conversation, which no tree shows, so each answer is the tree it writes."""

import os
import unittest

import helpers
from helpers import decision

PERSON = "the person's answer, word for word, 2026-11-03"


class TestCallerPinsDown(helpers.PinnerTest):
    path = os.path.join("work", "notes-json", "design-tree.json")

    def writes_settled_points(self) -> None:
        """Writes the caller's settled points as the first tree: the goal confirmed and the fields
        of a note decided, each open decision as the pinner writes it, and keys of the caller's
        own on the tree and on a decision."""
        self.writes_new()
        self.tree["goal"]["grounds"] = ["the caller, 2026-11-03"]
        self.tree["caller"] = {"work": "notes-json", "step": "design"}
        self.at("D1")["part"] = "README"
        self.decides("D1", "user", "the caller, 2026-11-03")

    def test_the_main_flow_from_the_callers_points_keeps_its_keys_to_the_end(self):
        # Given: the caller's settled points written as the first tree
        self.writes_settled_points()
        given = self.read_json(self.path)
        # When: the check runs
        # Then: the tree holds, what the caller left open to decide now
        self.assertEqual(self.checked(), self.holds("D2", "D3"))
        # When: the pinner settles the decision that follows from the goal
        self.decides("D2", "reasoning", "the goal, and Q2")
        # Then: the tree holds, the decision the fact settles open
        self.assertEqual(self.checked(), self.holds("D3"))
        # When: the person confirms the fact through the main conversation
        self.decides(
            "D3", "research", 'scripts/sync.py:14 "datetime.fromisoformat(fields[3])"', PERSON
        )
        # Then: the tree holds with no decision open
        self.assertEqual(self.checked(), self.holds())
        # When: the person confirms the design, and the check runs once more
        # Then: the tree holds with no decision open, the caller's points and keys as given
        self.assertEqual(self.checked(), self.holds())
        kept = self.read_json(self.path)
        self.assertEqual(
            (kept["goal"], kept["caller"], kept["decisions"][0]),
            (given["goal"], given["caller"], given["decisions"][0]),
        )

    def test_a_tree_mended_keeps_the_callers_points_as_given(self):
        # Given: the caller's settled points, with a question the caller gave and no decision
        # serves
        self.writes_settled_points()
        serving = self.tree["decisions"].pop(1)
        self.writes()
        given = self.read_json(self.path)
        # When: the check runs
        # Then: it names the question
        self.assertEqual(self.checked(), self.does_not_hold("Q2 is served by no decision."))
        # When: the pinner gives the question a decision, the caller's points kept as given
        self.tree["decisions"].insert(1, serving)
        self.writes()
        # Then: the tree holds, and the caller's points are as given
        self.assertEqual(self.checked(), self.holds("D2", "D3"))
        kept = self.read_json(self.path)
        self.assertEqual(
            (kept["goal"], kept["questions"], kept["caller"], kept["decisions"][0]),
            (given["goal"], given["questions"], given["caller"], given["decisions"][0]),
        )

    def test_a_wrap_up_through_the_main_conversation_leaves_the_rest_open(self):
        # Given: the caller's settled points, and the pinner's decision settled
        self.writes_settled_points()
        self.decides("D2", "reasoning", "the goal, and Q2")
        # When: the person's answer, given on by the main conversation, asks to wrap up, the
        # pinner leaves the open decision open, and the person confirms the design
        # Then: the tree holds, the decision left open named
        self.assertEqual(self.checked(), self.holds("D3"))

    def test_a_change_to_the_design_opens_its_decision_and_each_on_it_to_settle_again(self):
        # Given: the caller's settled points, every decision since settled, shown as the design
        self.writes_settled_points()
        self.decides("D2", "reasoning", "the goal, and Q2")
        self.decides("D3", "research", PERSON)
        self.tree["decisions"].append(
            decision(
                "D4", what="Whether updated holds seconds", contributes_to=["D3"], builds_on=["D3"]
            )
        )
        self.decides("D4", "reasoning", "D3", what="it holds seconds")
        # When: the person changes the form of updated, and the main conversation resumes the
        # pinner with the change; it opens that decision again with the one built on it
        self.opens("D3", "D4")
        # Then: the tree holds, the changed decision open to decide now
        self.assertEqual(self.checked(), self.holds("D3"))
        # When: the person decides it again, and the pinner settles the one built on it
        self.decides("D3", "user", PERSON, what="ISO 8601, with its offset")
        # Then: the tree holds, the one built on it open now
        self.assertEqual(self.checked(), self.holds("D4"))
        self.decides("D4", "reasoning", "D3", what="it holds seconds")
        # Then: the tree holds with no decision open
        self.assertEqual(self.checked(), self.holds())


if __name__ == "__main__":
    unittest.main()
