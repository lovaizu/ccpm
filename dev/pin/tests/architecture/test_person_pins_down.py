"""The person runs /pin:down, O1 of pin's UX, each path of its sequence in dev/pin/architecture.md
from start to end: a double of the pinner writes the tree each step calls for in .pin/, and
check.py, run by the command pin:down names from the folder the pinner works in, reads it from
disk and gives the Check result the step calls for."""

import unittest

import helpers
from helpers import decision

SOURCE = 'scripts/sync.py:14 "datetime.fromisoformat(fields[3])"'
CONFIRMED = "the person confirmed, 2026-11-03"


class TestPersonPinsDown(helpers.PinnerTest):
    def test_the_main_flow_ends_in_the_walkthrough_tree_with_no_decision_open(self):
        # Given: the plan; the pinner writes the goal to confirm, the questions, every decision open
        self.writes_new()
        # When: the check runs
        # Then: the tree holds, the decisions that build on none open to decide now
        self.assertEqual(self.checked(), self.holds("D1", "D2"))
        # When: the person confirms the goal
        self.confirms_goal()
        # Then: the tree holds, the same decisions open
        self.assertEqual(self.checked(), self.holds("D1", "D2"))
        # When: the person confirms the fact the researcher found, written into the grounds of the
        # decision it settles, which builds on one still open
        self.rests("D3", SOURCE, CONFIRMED)
        # Then: the tree holds, that decision still open, waiting for its turn
        self.assertEqual(self.checked(), self.holds("D1", "D2"))
        # When: the pinner settles the decision that follows from the goal
        self.decides("D2", "reasoning", "the goal, and Q2")
        # Then: the tree holds, the person's decision open
        self.assertEqual(self.checked(), self.holds("D1"))
        # When: the person makes their decision
        self.decides("D1", "user", "the person, 2026-11-03")
        # Then: the tree holds, the decision the fact settles open now
        self.assertEqual(self.checked(), self.holds("D3"))
        # When: in its turn, the pinner decides it by the fact confirmed
        self.decides("D3", "research")
        # Then: the tree holds with no decision open
        self.assertEqual(self.checked(), self.holds())
        # When: the person confirms the design, and the check runs once more
        # Then: the tree holds with no decision open, and is the walkthrough's
        self.assertEqual(self.checked(), self.holds())
        self.assertEqual(self.read_json(self.path), helpers.walkthrough())

    def test_a_tree_the_check_finds_a_problem_in_is_mended_until_it_holds(self):
        # Given: a first tree with a question no decision serves and a decision that serves none
        self.writes_new()
        serving = self.tree["decisions"].pop(1)
        self.tree["decisions"].append(decision("D4", contributes_to=[]))
        self.writes()
        # When: the check runs
        # Then: it names the question and the decision
        self.assertEqual(
            self.checked(),
            self.does_not_hold(
                "Q2 is served by no decision.", "D4 reaches no question, so it serves nothing."
            ),
        )
        # When: the pinner gives the question a decision, and cuts the one that serves nothing
        self.tree["decisions"][1:] = [serving]
        self.writes()
        # Then: the tree holds
        self.assertEqual(self.checked(), self.holds("D1", "D2"))

    def test_a_fact_the_person_corrects_is_decided_by_the_person(self):
        # Given: the goal confirmed and the person's decision made
        self.writes_new()
        self.confirms_goal()
        self.decides("D1", "user", "the person, 2026-11-03")
        # When: the person corrects the fact found, and the pinner writes the decision by them
        self.decides(
            "D3",
            "user",
            SOURCE,
            "the person: it is local time with its offset, 2026-11-03",
            what="ISO 8601, in local time with its offset",
        )
        # Then: the tree holds, only the decision the pinner settles left open
        self.assertEqual(self.checked(), self.holds("D2"))

    def test_a_fact_only_the_person_knows_is_kept_and_its_decision_waits_its_turn(self):
        # Given: the goal confirmed
        self.writes_new()
        self.confirms_goal()
        # When: the person tells a fact the person's decision rests on, written into its grounds
        self.rests("D1", "the person: a phone app reads the list too, 2026-11-03")
        # Then: the tree holds, and that decision is still open to decide
        self.assertEqual(self.checked(), self.holds("D1", "D2"))
        # When: the person then makes the decision
        self.decides("D1", "user", "the person, 2026-11-03")
        # Then: the tree holds, the decision that builds on it open now
        self.assertEqual(self.checked(), self.holds("D2", "D3"))

    def test_a_decision_the_person_leaves_to_the_pinner_is_decided_by_reasoning(self):
        # Given: the goal confirmed
        self.writes_new()
        self.confirms_goal()
        # When: the person answers "you decide", and the pinner settles it, saying so
        self.decides("D1", "reasoning", "the person left it to the pinner, 2026-11-03", "Q1")
        # Then: the tree holds, the others open
        self.assertEqual(self.checked(), self.holds("D2", "D3"))

    def test_a_point_an_answer_raises_is_added_open_and_then_settled(self):
        # Given: the goal confirmed and the person's decision made
        self.writes_new()
        self.confirms_goal()
        self.decides("D1", "user", "the person, 2026-11-03")
        # When: the answer raises a point not in the tree, added open, joined to what it serves
        # and builds on
        self.tree["decisions"].append(
            decision("D4", what="How tags are given", contributes_to=["D1"], builds_on=["D1"])
        )
        self.writes()
        # Then: the tree holds, the new point open to decide now
        self.assertEqual(self.checked(), self.holds("D2", "D3", "D4"))
        # When: the person decides it
        self.decides("D4", "user", "the person, 2026-11-03", what="a list of texts")
        # Then: the tree holds, it no longer open
        self.assertEqual(self.checked(), self.holds("D2", "D3"))

    def test_a_wrap_up_leaves_the_open_decisions_open_and_the_tree_holds(self):
        # Given: the goal confirmed and the pinner's decision settled
        self.writes_new()
        self.confirms_goal()
        self.decides("D2", "reasoning", "the goal, and Q2")
        # When: the person asks to wrap up, the pinner asks no more, and the person confirms the
        # design with the rest left open
        # Then: the tree holds, the decision left open named
        self.assertEqual(self.checked(), self.holds("D1"))
        kept = self.read_json(self.path)["decisions"]
        self.assertEqual([d["id"] for d in kept if d["decided"] is None], ["D1", "D3"])

    def test_a_change_to_the_design_opens_its_decision_and_each_on_it_to_settle_again(self):
        # Given: the walkthrough's tree, every decision settled, shown as the design
        self.writes()
        # When: the person changes the fields each note has, and the pinner opens that decision
        # again with the one that builds on it
        self.opens("D1", "D3")
        # Then: the tree holds, the changed decision open to decide now
        self.assertEqual(self.checked(), self.holds("D1"))
        # When: the person decides it again, and confirms the fact again
        self.decides("D1", "user", "the person, 2026-11-04", what="id, title and updated")
        self.decides("D3", "research", "the person confirmed, 2026-11-04")
        # Then: the tree holds with no decision open
        self.assertEqual(self.checked(), self.holds())

    def test_a_tree_a_stopped_run_left_is_gone_on_from_where_it_stopped(self):
        # Given: a tree a stopped run left in .pin/: the goal confirmed and one decision settled
        self.writes_new()
        self.confirms_goal()
        self.decides("D2", "reasoning", "the goal, and Q2")
        # When: a new conversation's pinner reads the tree from disk, and runs the check
        self.tree = self.read_json(self.path)
        # Then: the tree holds, only what is still open to decide named
        self.assertEqual(self.checked(), self.holds("D1"))
        # When: it goes on, the person deciding and confirming the fact
        self.decides("D1", "user", "the person, 2026-11-04")
        self.decides("D3", "research", SOURCE, "the person confirmed, 2026-11-04")
        # Then: the tree holds with no decision open
        self.assertEqual(self.checked(), self.holds())


if __name__ == "__main__":
    unittest.main()
