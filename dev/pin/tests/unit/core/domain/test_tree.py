"""tree.py, what a design tree is and when it holds: the file read into the form the checks take,
or refused with why; each way the tree fails to hold; and the decisions open to be decided now."""

import json
import unittest

import helpers
from helpers import decision, made, settled, testing, tree


class TestLoad(testing.FolderTest):
    def loaded_or_why(self, data: object) -> str:
        """Why load refuses the data written as the tree's file."""
        self.write("design-tree.json", json.dumps(data))
        with self.assertRaises(tree.Unreadable) as refused:
            tree.load("design-tree.json")
        return str(refused.exception)

    def test_a_tree_in_form_is_given_as_read(self):
        # Given: the README walkthrough's tree, with a key of a caller's own
        kept = helpers.walkthrough()
        kept["kind"] = "readme"
        self.write_json("design-tree.json", kept)
        # When: it is loaded
        # Then: it is given as it was written, the caller's key kept
        self.assertEqual(tree.load("design-tree.json"), kept)

    def test_a_missing_file_is_refused(self):
        # Given: no file at the path
        # When: it is loaded
        with self.assertRaises(tree.Unreadable) as refused:
            tree.load("gone.json")
        # Then: it is refused, naming the path
        self.assertEqual(str(refused.exception), "there is no file gone.json")

    def test_a_file_not_json_is_refused_with_where(self):
        # Given: a file whose text is not JSON
        self.write("design-tree.json", '{"goal": ')
        # When: it is loaded
        with self.assertRaises(tree.Unreadable) as refused:
            tree.load("design-tree.json")
        # Then: it is refused, with the line and column JSON stopped at
        self.assertTrue(
            str(refused.exception).startswith("it is not JSON: Expecting value at line 1 column 10")
        )

    def test_a_tree_not_an_object_is_refused(self):
        # Given: JSON that is a list
        # When: it is loaded
        # Then: it is refused, saying what it must be
        self.assertEqual(
            self.loaded_or_why([]),
            "the tree must be an object with goal, questions and decisions",
        )

    def test_each_missing_or_mistyped_key_is_named(self):
        cases = [
            ("goal", None, "goal must be an object with what and grounds"),
            ("goal", {"what": "", "grounds": []}, "goal.what must be a text that is not empty"),
            ("goal", {"what": "g", "grounds": "x"}, "goal.grounds must be a list of texts"),
            ("goal", {"what": "g", "grounds": [1]}, "goal.grounds must be a list of texts"),
            ("questions", {}, "questions must be a list"),
            ("questions", ["Q1"], "questions[0] must be an object with id and what"),
            ("questions", [{"id": "", "what": "w"}], "questions[0].id must be a text"),
            ("questions", [{"id": "Q1"}], "questions[0].what must be a text that is not empty"),
            ("decisions", None, "decisions must be a list"),
            ("decisions", [7], "decisions[0] must be an object"),
        ]
        for key, value, why in cases:
            with self.subTest(key=key, value=value):
                # Given: the walkthrough's tree with the key set so, or left out where None
                data = helpers.walkthrough()
                if value is None:
                    del data[key]
                else:
                    data[key] = value
                # When: it is loaded
                # Then: it is refused, naming the key and what it must be
                self.assertIn(why, self.loaded_or_why(data))

    def test_each_mistyped_field_of_a_decision_is_named(self):
        cases = [
            ({"id": 3}, "decisions[0].id must be a text that is not empty"),
            ({"what": ""}, "decisions[0].what must be a text that is not empty"),
            ({"contributes_to": "Q1"}, "decisions[0].contributes_to must be a list of IDs"),
            ({"builds_on": [1]}, "decisions[0].builds_on must be a list of IDs"),
            ({"decided": ""}, "decisions[0].decided must be a text that is not empty, or null"),
            ({"decided": 1}, "decisions[0].decided must be a text that is not empty, or null"),
            (
                {"settled_by": "chance"},
                "decisions[0].settled_by must be user, research or reasoning, or null",
            ),
            ({"grounds": None}, "decisions[0].grounds must be a list of texts"),
        ]
        for given, why in cases:
            with self.subTest(given=given):
                # Given: a tree whose one decision has the field so
                data = made(decision("D1", **given))
                # When: it is loaded
                # Then: it is refused, naming the field and what it must be
                self.assertIn(why, self.loaded_or_why(data))

    def test_a_missing_field_of_a_decision_is_named(self):
        # Given: a decision with no builds_on
        lacking = decision("D1")
        del lacking["builds_on"]
        # When: the tree is loaded
        # Then: it is refused, naming the field
        self.assertIn(
            "decisions[0].builds_on must be a list of IDs", self.loaded_or_why(made(lacking))
        )

    def test_every_fault_of_the_form_is_named_at_once(self):
        # Given: a tree with two faults
        data = made(decision("D1", what=""), decision("D2", grounds="x"))
        # When: it is loaded
        # Then: both are named, a line each
        self.assertEqual(
            self.loaded_or_why(data).splitlines(),
            [
                "decisions[0].what must be a text that is not empty",
                "decisions[1].grounds must be a list of texts",
            ],
        )

    def test_an_id_used_twice_is_refused(self):
        # Given: a decision with the ID of a question
        # When: the tree is loaded
        # Then: it is refused, naming the ID
        self.assertIn(
            "the ID Q1 is used twice", self.loaded_or_why(made(decision("Q1", contributes_to=[])))
        )

    def test_an_id_named_that_is_not_in_the_tree_is_refused(self):
        cases = [
            ({"contributes_to": ["Q9"]}, "D1 contributes to Q9, which is not in the tree"),
            ({"builds_on": ["D9"]}, "D1 builds on D9, which is not a decision of the tree"),
            ({"builds_on": ["Q1"]}, "D1 builds on Q1, which is not a decision of the tree"),
            ({"contributes_to": ["D1"]}, "D1 contributes to itself"),
            ({"builds_on": ["D1"]}, "D1 builds on itself"),
        ]
        for given, why in cases:
            with self.subTest(given=given):
                # Given: a decision naming the ID so
                # When: the tree is loaded
                # Then: it is refused, saying which ID and how
                self.assertIn(why, self.loaded_or_why(made(decision("D1", **given))))


class TestProblems(unittest.TestCase):
    def test_the_walkthrough_tree_holds(self):
        # Given: the README walkthrough's tree
        # When: its problems are found
        # Then: there are none
        self.assertEqual(tree.problems(helpers.walkthrough()), [])

    def test_a_goal_with_no_question_is_a_gap(self):
        # Given: a tree with no question
        # When: its problems are found
        # Then: the goal is named as having none
        self.assertEqual(
            tree.problems(made(questions=())),
            ["The goal has no question that must hold for it."],
        )

    def test_a_question_no_decision_serves_is_a_gap(self):
        # Given: two questions, a decision serving the first alone
        # When: the problems are found
        # Then: the second is named as served by none
        self.assertEqual(
            tree.problems(made(decision("D1"), questions=("Q1", "Q2"))),
            ["Q2 is served by no decision."],
        )

    def test_a_question_served_through_a_decision_is_still_a_gap(self):
        # Given: D2 serves D1, and D1 serves Q1; Q2 is served by nothing directly
        d1 = decision("D1")
        d2 = decision("D2", contributes_to=["D1"])
        # When: the problems are found
        # Then: Q2 is named, and D2 reaching Q1 through D1 is no problem
        self.assertEqual(
            tree.problems(made(d1, d2, questions=("Q1", "Q2"))),
            ["Q2 is served by no decision."],
        )

    def test_a_decision_that_contributes_to_nothing_reaches_no_question(self):
        # Given: a decision that contributes to nothing
        # When: the problems are found
        # Then: it is named as reaching no question
        self.assertEqual(
            tree.problems(made(decision("D1"), decision("D2", contributes_to=[]))),
            ["D2 reaches no question, so it serves nothing."],
        )

    def test_decisions_that_serve_only_each_other_reach_no_question(self):
        # Given: D2 and D3 contribute only to each other
        d2 = decision("D2", contributes_to=["D3"])
        d3 = decision("D3", contributes_to=["D2"])
        # When: the problems are found
        # Then: each is named
        self.assertEqual(
            tree.problems(made(decision("D1"), d2, d3)),
            [
                "D2 reaches no question, so it serves nothing.",
                "D3 reaches no question, so it serves nothing.",
            ],
        )

    def test_a_decision_reaching_a_question_through_a_loop_reaches_it(self):
        # Given: D2 contributes to D3 and back, and D3 also to D1, which serves Q1
        d2 = decision("D2", contributes_to=["D3"])
        d3 = decision("D3", contributes_to=["D2", "D1"])
        # When: the problems are found
        # Then: there are none
        self.assertEqual(tree.problems(made(decision("D1"), d2, d3)), [])

    def test_a_decision_decided_before_one_it_builds_on_is_out_of_order(self):
        # Given: D2 is decided while D1, which it builds on, is open
        # When: the problems are found
        # Then: D2 is named, with D1
        self.assertEqual(
            tree.problems(made(decision("D1"), settled("D2", builds_on=["D1"]))),
            ["D2 is decided before D1, which it builds on and which is still open."],
        )

    def test_an_open_decision_on_an_open_one_is_in_order(self):
        # Given: D2 and D1 both open, D2 building on D1
        # When: the problems are found
        # Then: there are none
        self.assertEqual(tree.problems(made(decision("D1"), decision("D2", builds_on=["D1"]))), [])

    def test_decisions_that_build_on_each_other_are_a_loop(self):
        # Given: D1 builds on D3, D3 on D2, and D2 on D1
        d1 = decision("D1", builds_on=["D3"])
        d2 = decision("D2", builds_on=["D1"])
        d3 = decision("D3", builds_on=["D2"])
        # When: the problems are found
        # Then: the loop is named once, from its first decision in the tree
        self.assertEqual(
            tree.problems(made(d1, d2, d3)),
            ["D1, D3 and D2 build on one another in a loop, so none can be decided first."],
        )

    def test_the_shortest_loop_from_a_decision_is_named(self):
        # Given: D1 builds on D2 and D3; D2 builds on D1; D3 on D4, and D4 on D1
        loops = [
            decision("D1", builds_on=["D2", "D3"]),
            decision("D2", builds_on=["D1"]),
            decision("D3", builds_on=["D4"]),
            decision("D4", builds_on=["D1"]),
        ]
        # When: the problems are found
        # Then: the loop of D1 and D2 alone is named, as D3 and D4 loop through D1
        self.assertEqual(
            tree.problems(made(*loops)),
            ["D1 and D2 build on one another in a loop, so none can be decided first."],
        )

    def test_a_loop_read_from_a_file_is_found(self):
        # Given: D1 and D2 build on each other, read from JSON, so each ID is a text of its own
        data = json.loads(
            json.dumps(made(decision("D1", builds_on=["D2"]), decision("D2", builds_on=["D1"])))
        )
        # When: the problems are found
        # Then: the loop is named
        self.assertEqual(
            tree.problems(data),
            ["D1 and D2 build on one another in a loop, so none can be decided first."],
        )

    def test_two_loops_are_each_named(self):
        # Given: D1 and D2 build on each other, and D3 and D4 too
        loops = [
            decision("D1", builds_on=["D2"]),
            decision("D2", builds_on=["D1"]),
            decision("D3", builds_on=["D4"]),
            decision("D4", builds_on=["D3"]),
        ]
        # When: the problems are found
        # Then: each loop is named
        self.assertEqual(
            tree.problems(made(*loops)),
            [
                "D1 and D2 build on one another in a loop, so none can be decided first.",
                "D3 and D4 build on one another in a loop, so none can be decided first.",
            ],
        )

    def test_a_decision_on_a_loop_is_not_named_as_in_it(self):
        # Given: D1 and D2 build on each other, and D3 builds on D1
        loop = [
            decision("D1", builds_on=["D2"]),
            decision("D2", builds_on=["D1"]),
            decision("D3", builds_on=["D1"]),
        ]
        # When: the problems are found
        # Then: the loop alone is named
        self.assertEqual(
            tree.problems(made(*loop)),
            ["D1 and D2 build on one another in a loop, so none can be decided first."],
        )

    def test_a_decision_settled_with_nothing_it_rests_on_is_assumed(self):
        cases = [
            (
                {"decided": "x", "settled_by": None, "grounds": ["g"]},
                "D1 is decided, but not by whom or what: give its settled_by.",
            ),
            (
                {"decided": None, "settled_by": "user", "grounds": []},
                "D1 has a settled_by, but is not decided: give what was decided.",
            ),
            (
                {"decided": "x", "settled_by": "research", "grounds": []},
                "D1 is decided on no ground: give what it rests on.",
            ),
        ]
        for given, why in cases:
            with self.subTest(given=given):
                # Given: a decision settled so
                # When: the problems are found
                # Then: it is named, with what it lacks
                self.assertEqual(tree.problems(made(decision("D1", **given))), [why])

    def test_problems_come_in_the_order_of_the_checks(self):
        # Given: a tree with a gap, a decision reaching nothing and one out of order
        data = made(
            decision("D1"),
            settled("D2", contributes_to=[]),
            settled("D3", builds_on=["D1"]),
            questions=("Q1", "Q2"),
        )
        # When: the problems are found
        # Then: the gap first, then what reaches nothing, then the order
        self.assertEqual(
            tree.problems(data),
            [
                "Q2 is served by no decision.",
                "D2 reaches no question, so it serves nothing.",
                "D3 is decided before D1, which it builds on and which is still open.",
            ],
        )


class TestReady(unittest.TestCase):
    def test_open_decisions_on_decided_ones_are_ready_in_tree_order(self):
        # Given: D1 decided; D3 and D2 open on it; D4 open on D2
        data = made(
            settled("D1"),
            decision("D3", builds_on=["D1"]),
            decision("D2", builds_on=["D1"]),
            decision("D4", builds_on=["D2"]),
        )
        # When: the decisions ready are found
        # Then: D3 and D2, as the tree lists them
        self.assertEqual(tree.ready(data), ["D3", "D2"])

    def test_no_decision_is_ready_where_all_are_decided(self):
        # Given: the walkthrough's tree, every decision decided
        # When: the decisions ready are found
        # Then: none
        self.assertEqual(tree.ready(helpers.walkthrough()), [])


if __name__ == "__main__":
    unittest.main()
