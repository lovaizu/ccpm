"""domain/trees.py, the design tree: its form, each node's ID and key, a change found and the nodes
it touches, a tree edit applied, the order's faults, the decisions open, and the tree shown."""

from __future__ import annotations

import copy
import unittest

import helpers
from helpers import trees

FINDER = {"readme": ["Q1", "Q2"], "code": ["Q1"], "meta": [], "research": [], "plan": []}.get


def small() -> dict:
    """A tree of two deliverables, the second taking from the first, each with its intents, the
    first's Q2 holding two decisions."""
    return {
        "goal": {"decided": "g", "by": "user"},
        "deliverables": [
            {
                "name": "r",
                "path": "README.md",
                "kind": "readme",
                "inputs": [],
                "preconditions": [],
                "status": "doing",
                "intents": [
                    {"id": "Q1", "good": False, "decisions": []},
                    {
                        "id": "Q2",
                        "good": False,
                        "decisions": [
                            {"about": "a", "decided": "x", "by": "user"},
                            {"about": "b", "decided": None},
                        ],
                    },
                ],
            },
            {
                "name": "c",
                "path": "c.py",
                "kind": "code",
                "inputs": ["README.md"],
                "preconditions": [],
                "status": "open",
                "intents": [{"id": "Q1", "good": False, "decisions": []}],
            },
        ],
    }


class Load(helpers.testing.FolderTest):
    def test_a_tree_in_form_is_read(self):
        # Given: the walkthrough's tree on disk
        self.write_json("t.json", helpers.walkthrough())
        # When: it's read
        # Then: it's the tree
        self.assertEqual(trees.load("t.json"), helpers.walkthrough())

    def test_a_tree_out_of_form_is_refused_with_where(self):
        # Given: a tree whose goal names no one who settled it
        self.write_json("t.json", {"goal": {"decided": "g"}, "deliverables": []})
        # When: it's read
        # Then: it's refused, naming the form's point
        with self.assertRaises(helpers.files.Unreadable) as stop:
            trees.load("t.json")
        self.assertIn("t.json is out of its form: $.goal", str(stop.exception))


class Nodes(unittest.TestCase):
    def test_each_node_has_its_id_and_key_in_order(self):
        # Given: the small tree
        # When: rn lists its nodes
        found = trees.nodes(small())
        # Then: the goal, each deliverable, each intent and each decision, in order
        self.assertEqual(
            [n for n, _ in found],
            ["goal", "D1", "D1Q1", "D1Q2", "D1Q2-1", "D1Q2-2", "D2", "D2Q1"],
        )
        self.assertEqual(dict(found)["D1Q2-2"], ("x", "README.md", "Q2", "b"))
        self.assertEqual(trees.where(small(), "D2"), ("d", "c.py"))
        self.assertIsNone(trees.where(small(), "D9"))

    def test_the_deliverable_at_hand_is_the_first_not_done(self):
        tree = small()
        self.assertEqual(trees.at_hand(tree), 1)
        tree["deliverables"][0] = helpers.done("README.md", "r")
        self.assertEqual(trees.at_hand(tree), 2)
        tree["deliverables"][1]["status"] = "done"
        self.assertIsNone(trees.at_hand(tree))


class Changed(unittest.TestCase):
    def test_every_node_is_new_with_no_tree_before(self):
        self.assertEqual(trees.changed(None, small()), set(trees.content(small())))

    def test_a_node_whose_content_differs_or_that_went(self):
        # Given: the small tree, its Q1 made good, its decision a settled, and D2 removed
        after = copy.deepcopy(small())
        after["deliverables"][0]["intents"][0]["good"] = True
        after["deliverables"][0]["intents"][1]["decisions"][1].update(decided="y", by="user")
        del after["deliverables"][1]
        # When: rn finds the change
        found = trees.changed(small(), after)
        # Then: the intent, the decision, and each node of D2
        self.assertEqual(
            found,
            {
                ("i", "README.md", "Q1"),
                ("x", "README.md", "Q2", "b"),
                ("d", "c.py"),
                ("i", "c.py", "Q1"),
            },
        )

    def test_no_change_of_the_same_tree(self):
        self.assertEqual(trees.changed(small(), small()), set())


class Touched(unittest.TestCase):
    def test_a_decision_touches_up_to_the_goal_its_later_decisions_and_neighbours(self):
        # Given: the small tree, D1's first decision changed
        before = small()
        after = copy.deepcopy(before)
        after["deliverables"][0]["intents"][1]["decisions"][0]["decided"] = "z"
        keys = trees.changed(before, after)
        # When: rn lists the nodes it touches
        # Then: up to the goal, the later decision, and D2, which takes from D1
        self.assertEqual(trees.touched(before, after, keys), ["goal", "D1", "D1Q2", "D1Q2-2", "D2"])

    def test_an_intent_touches_the_later_decisions_and_neighbours(self):
        before = small()
        after = copy.deepcopy(before)
        after["deliverables"][0]["intents"][0]["good"] = True
        keys = trees.changed(before, after)
        self.assertEqual(
            trees.touched(before, after, keys), ["goal", "D1", "D1Q2-1", "D1Q2-2", "D2"]
        )

    def test_a_deliverable_touches_its_decisions_and_what_it_takes_from(self):
        # Given: D2 set doing, which takes from D1
        before = small()
        after = copy.deepcopy(before)
        after["deliverables"][1]["status"] = "doing"
        keys = trees.changed(before, after)
        self.assertEqual(trees.touched(before, after, keys), ["goal", "D1"])
        # And: D1 set otherwise touches its own decisions and D2
        after = copy.deepcopy(before)
        after["deliverables"][0]["name"] = "s"
        keys = trees.changed(before, after)
        self.assertEqual(trees.touched(before, after, keys), ["goal", "D1Q2-1", "D1Q2-2", "D2"])

    def test_the_goal_touches_every_deliverable(self):
        before = small()
        after = copy.deepcopy(before)
        after["goal"]["decided"] = "h"
        self.assertEqual(trees.touched(before, after, trees.changed(before, after)), ["D1", "D2"])

    def test_a_node_removed_touches_what_stood_over_it(self):
        # Given: D1's open decision removed
        before = small()
        after = copy.deepcopy(before)
        del after["deliverables"][0]["intents"][1]["decisions"][1]
        keys = trees.changed(before, after)
        # Then: its intent, its deliverable, the goal, and D2
        self.assertEqual(trees.touched(before, after, keys), ["goal", "D1", "D1Q2", "D2"])
        # And: D1 removed touches the goal, and D2, which takes from it, alone
        after = copy.deepcopy(before)
        del after["deliverables"][0]
        keys = trees.changed(before, after)
        self.assertEqual(trees.touched(before, after, keys), ["goal", "D1"])

    def test_nothing_where_each_node_is_new(self):
        self.assertEqual(trees.touched(None, small(), trees.changed(None, small())), [])


class Apply(unittest.TestCase):
    def applied(self, *nodes, answers=()):
        """The small tree the edit of the nodes and answers makes."""
        edit = {"grounds": "g", "nodes": list(nodes), "answers": list(answers)}
        return trees.apply(small(), edit, FINDER)

    def refused(self, *nodes, answers=()):
        """Why the small tree refuses the edit."""
        with self.assertRaises(trees.Refused) as stop:
            self.applied(*nodes, answers=answers)
        return str(stop.exception)

    def test_the_goal_is_set(self):
        after = self.applied({"id": "goal", "decided": "h", "by": "maker"})
        self.assertEqual(after["goal"], {"decided": "h", "by": "maker"})

    def test_a_deliverable_is_added_first_after_one_or_after_one_added_before(self):
        given = {"name": "n", "kind": "readme", "inputs": [], "preconditions": []}
        after = self.applied(
            {"after": "goal", "path": "a.md", **given},
            {"after": "D1", "path": "b.md", **given},
            {"after": "b.md", "path": "e.md", **given},
        )
        paths = [d["path"] for d in after["deliverables"]]
        self.assertEqual(paths, ["a.md", "README.md", "b.md", "e.md", "c.py"])
        self.assertEqual(
            after["deliverables"][0],
            {
                "name": "n",
                "path": "a.md",
                "kind": "readme",
                "inputs": [],
                "preconditions": [],
                "status": "open",
                "intents": [
                    {"id": "Q1", "good": False, "decisions": []},
                    {"id": "Q2", "good": False, "decisions": []},
                ],
            },
        )

    def test_a_deliverable_of_a_kind_with_no_best_practice_has_no_intent_yet(self):
        given = {"name": "n", "path": "m.1", "kind": "man-page", "inputs": [], "preconditions": []}
        after = self.applied({"after": "D2", **given})
        self.assertEqual(after["deliverables"][2]["intents"], [])

    def test_a_deliverable_added_needs_its_fields_and_a_place(self):
        self.assertEqual(
            self.refused({"after": "goal", "name": "n"}),
            "goal: a deliverable added needs path, kind, inputs, preconditions",
        )
        self.assertEqual(
            self.refused({"after": "D1Q1", "name": "n"}),
            "D1Q1: a deliverable goes after the goal or a deliverable",
        )

    def test_a_deliverable_is_set_or_removed(self):
        after = self.applied({"id": "D2", "status": "doing", "name": "m"})
        self.assertEqual(
            (after["deliverables"][1]["status"], after["deliverables"][1]["name"]), ("doing", "m")
        )
        after = self.applied({"id": "D1", "remove": True})
        self.assertEqual([d["path"] for d in after["deliverables"]], ["c.py"])

    def test_a_kind_changed_takes_its_new_kinds_intents(self):
        after = self.applied({"id": "D2", "kind": "readme"})
        self.assertEqual([i["id"] for i in after["deliverables"][1]["intents"]], ["Q1", "Q2"])

    def test_a_deliverable_done_keeps_one_line_once_each_intent_is_good(self):
        good = [{"id": f"D1Q{n}", "good": True} for n in (1, 2)]
        after = self.applied(*good, {"id": "D1", "status": "done"})
        self.assertEqual(
            after["deliverables"][0],
            {"name": "r", "path": "README.md", "kind": "readme", "status": "done"},
        )
        self.assertEqual(
            self.refused({"id": "D1", "status": "done"}),
            "D1: it isn't done while Q1, Q2 isn't good",
        )

    def test_a_deliverable_done_stays_done(self):
        good = [{"id": f"D1Q{n}", "good": True} for n in (1, 2)]
        tree = trees.apply(
            small(), {"grounds": "g", "nodes": [*good, {"id": "D1", "status": "done"}]}, FINDER
        )
        with self.assertRaises(trees.Refused) as stop:
            trees.apply(tree, {"grounds": "g", "nodes": [{"id": "D1", "status": "doing"}]}, FINDER)
        self.assertEqual(str(stop.exception), "D1: a deliverable done stays done")

    def test_a_decision_is_added_at_an_intent_or_set_by_what_its_about(self):
        after = self.applied(
            {"id": "D1Q1", "about": "c", "decided": None},
            {"id": "D1Q2", "about": "a", "decided": "w", "by": "reasoning"},
        )
        intents = after["deliverables"][0]["intents"]
        self.assertEqual(intents[0]["decisions"], [{"about": "c", "decided": None}])
        self.assertEqual(
            intents[1]["decisions"][0], {"about": "a", "decided": "w", "by": "reasoning"}
        )

    def test_an_intent_is_made_good(self):
        after = self.applied({"id": "D2Q1", "good": True})
        self.assertTrue(after["deliverables"][1]["intents"][0]["good"])

    def test_a_decision_is_set_opened_or_removed(self):
        after = self.applied({"id": "D1Q2-2", "decided": "y", "by": "research"})
        self.assertEqual(
            after["deliverables"][0]["intents"][1]["decisions"][1],
            {"about": "b", "decided": "y", "by": "research"},
        )
        after = self.applied({"id": "D1Q2-1", "decided": None})
        self.assertEqual(
            after["deliverables"][0]["intents"][1]["decisions"][0], {"about": "a", "decided": None}
        )
        after = self.applied({"id": "D1Q2-1", "remove": True})
        self.assertEqual(len(after["deliverables"][0]["intents"][1]["decisions"]), 1)

    def test_a_decision_settled_by_no_one_is_refused(self):
        self.assertEqual(
            self.refused({"id": "D1Q2-2", "decided": "y"}),
            "D1Q2-2: the decision b is settled by no one: name its by",
        )
        self.assertEqual(
            self.refused({"id": "D1Q1", "about": "c", "decided": "y"}),
            "D1Q1: the decision c is settled by no one: name its by",
        )

    def test_a_node_no_tree_holds_is_refused_each_on_a_line(self):
        self.assertEqual(
            self.refused({"id": "D9"}, answers=[{"id": "D8", "holds": True}]),
            "D9 is no node of the tree\nD8 is no node of the tree",
        )

    def test_an_answer_that_a_decision_no_longer_holds_opens_it(self):
        after = self.applied(
            answers=[{"id": "D1Q2-1", "holds": False}, {"id": "D2", "holds": True}]
        )
        self.assertEqual(
            after["deliverables"][0]["intents"][1]["decisions"][0], {"about": "a", "decided": None}
        )

    def test_an_answer_that_a_node_no_decision_no_longer_holds_is_refused(self):
        self.assertEqual(
            self.refused(answers=[{"id": "D2", "holds": False}]),
            "D2 is no decision: change it among the nodes instead",
        )

    def test_an_answer_of_a_decision_the_edit_removed_opens_nothing(self):
        after = self.applied(
            {"id": "D1Q2-1", "remove": True}, answers=[{"id": "D1Q2-1", "holds": False}]
        )
        self.assertEqual(
            after["deliverables"][0]["intents"][1]["decisions"], [{"about": "b", "decided": None}]
        )

    def test_the_tree_given_is_left_as_it_was(self):
        tree = small()
        trees.apply(
            tree, {"grounds": "g", "nodes": [{"id": "goal", "decided": "h", "by": "user"}]}, FINDER
        )
        self.assertEqual(tree, small())


class Faults(unittest.TestCase):
    def faults(self, tree, files=()):
        """The tree's faults, the files given there."""
        return trees.faults(tree, lambda p: p in files, FINDER)

    def test_a_tree_in_order_has_none(self):
        self.assertEqual(self.faults(small()), [])

    def test_a_path_held_twice(self):
        tree = small()
        tree["deliverables"][1]["path"] = "README.md"
        tree["deliverables"][1]["inputs"] = []
        self.assertEqual(self.faults(tree), ["two deliverables are at README.md"])

    def test_a_deliverable_before_what_it_takes_from(self):
        tree = small()
        tree["deliverables"].reverse()
        self.assertEqual(self.faults(tree), ["D1 takes README.md in its inputs, which comes later"])
        tree = small()
        tree["deliverables"][0]["preconditions"] = ["README.md"]
        self.assertEqual(
            self.faults(tree), ["D1 takes README.md in its preconditions, which comes later"]
        )

    def test_an_input_that_is_neither_a_deliverable_nor_a_file(self):
        tree = small()
        tree["deliverables"][0]["inputs"] = ["dev/pv.md", "gone.md"]
        self.assertEqual(
            self.faults(tree, files=("dev/pv.md",)),
            ["D1 names gone.md in its inputs, neither a deliverable nor a file"],
        )

    def test_a_kind_with_no_best_practice_nor_a_meta_deliverable_before_it(self):
        tree = small()
        tree["deliverables"][1].update(kind="man-page", intents=[])
        self.assertEqual(
            self.faults(tree), ["D2's kind man-page has no best practice, nor a meta one before it"]
        )
        meta = {
            "name": "m",
            "path": ".rn/r/best-practices/man-page/",
            "kind": "meta",
            "inputs": [],
            "preconditions": [],
            "status": "open",
            "intents": [],
        }
        tree["deliverables"].insert(1, meta)
        self.assertEqual(self.faults(tree), [])

    def test_a_meta_deliverable_whose_kind_no_later_deliverable_takes(self):
        tree = small()
        meta = {
            "name": "m",
            "path": ".rn/r/best-practices/man-page",
            "kind": "meta",
            "inputs": [],
            "preconditions": [],
            "status": "open",
            "intents": [],
        }
        tree["deliverables"].append(meta)
        self.assertEqual(
            self.faults(tree), ["D3 makes the kind man-page, which no later deliverable takes"]
        )

    def test_a_research_deliverable_no_later_one_takes_from(self):
        tree = small()
        research = {
            "name": "s",
            "path": "notes.md",
            "kind": "research",
            "inputs": [],
            "preconditions": [],
            "status": "open",
            "intents": [],
        }
        tree["deliverables"].insert(0, research)
        self.assertEqual(self.faults(tree), ["D1 is research that no later deliverable takes from"])
        tree["deliverables"][2]["preconditions"] = ["notes.md"]
        self.assertEqual(self.faults(tree), [])

    def test_intents_unlike_the_kinds(self):
        tree = small()
        tree["deliverables"][0]["intents"].reverse()
        self.assertEqual(
            self.faults(tree), ["D1's intents aren't those of its kind readme, in their order"]
        )

    def test_a_deliverable_done_is_held_only_to_its_order(self):
        tree = small()
        tree["deliverables"][0] = {
            "name": "r",
            "path": "README.md",
            "kind": "gone",
            "status": "done",
        }
        self.assertEqual(self.faults(tree), [])


class Shown(unittest.TestCase):
    def test_the_decisions_open_of_a_deliverable(self):
        found = trees.open_decisions(small(), 1)
        self.assertEqual(found, [("D1Q2-2", {"about": "b", "decided": None})])
        self.assertEqual(trees.open_decisions(small(), 2), [])

    def test_the_tree_is_shown_with_each_id(self):
        tree = small()
        tree["deliverables"][1]["intents"][0]["good"] = True
        tree["deliverables"].append(
            {"name": "d", "path": "d.md", "kind": "readme", "status": "done"}
        )
        said = trees.view(tree, lambda kind: {"readme": {"Q1": "Does it?"}}.get(kind, {}))
        self.assertEqual(
            said,
            "- goal: g (user)\n"
            "- D1 README.md: r (kind readme, doing)\n"
            "  - D1Q1, not good yet: Does it?\n"
            "  - D1Q2, not good yet:\n"
            "    - D1Q2-1 a: x (user)\n"
            "    - D1Q2-2 b: open\n"
            "- D2 c.py: c (kind code, open); inputs README.md\n"
            "  - D2Q1, good:\n"
            "- D3 d.md: d (kind readme, done)",
        )
