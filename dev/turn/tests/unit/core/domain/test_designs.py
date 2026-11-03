"""designs.py: the design tree asks the template's questions as the template asks them; the work's
parts each hold every decision joined to their own and paths of the work none other holds; a
remake names decisions and questions of the tree; and the decisions split into the branches that
build on none in another."""

import unittest

import helpers
from helpers import decision, designs, question

STANDARD = helpers.RUN["standard.json"]


def tree(*decisions):
    """The run's design tree with the decisions given in place of its own."""
    made = helpers.run()["design-tree.json"]
    made["decisions"] = list(decisions)
    return made


class TestAsked(unittest.TestCase):
    def test_a_tree_asking_each_question_as_written_has_no_fault(self):
        self.assertEqual(designs.asked(helpers.RUN["design-tree.json"], STANDARD, "readme"), [])

    def test_a_question_left_out_a_question_reworded_and_one_the_template_has_not(self):
        # Given: Q1 reworded, Q2 left out, and a question the template has not
        made = helpers.run()["design-tree.json"]
        made["questions"] = [
            {"id": question(1), "what": "Other words?"},
            {"id": question(3), "what": STANDARD["benefits"][2]["what"]},
            {"id": question(9), "what": "More?"},
        ]
        # Then: each is named, in the template's order, then the one it has not
        self.assertEqual(
            designs.asked(made, STANDARD, "readme"),
            [
                "readme/Q1 is not asked as the template asks it: Can the reader say what it does?",
                "the tree does not ask readme/Q2: Can the reader get the result?",
                "readme/Q9 is no question of the template",
            ],
        )

    def test_a_question_is_named_with_the_kind_given(self):
        self.assertEqual(
            designs.asked(helpers.RUN["design-tree.json"], STANDARD, "man-page")[0],
            "the tree does not ask man-page/Q1: Can the reader say what it does?",
        )


class TestReworded(unittest.TestCase):
    def test_a_question_in_words_that_sort_before_or_after_the_template_s(self):
        made = helpers.run()["design-tree.json"]
        made["questions"][0]["what"] = "A question in other words?"
        made["questions"][2]["what"] = "Zero answers?"
        self.assertEqual(
            designs.asked(made, STANDARD, "readme"),
            [
                "readme/Q1 is not asked as the template asks it: Can the reader say what it does?",
                (
                    "readme/Q3 is not asked as the template asks it: Does each answer come when"
                    " needed?"
                ),
            ],
        )


class TestBranches(unittest.TestCase):
    def test_decisions_joined_by_building_on_go_together(self):
        made = tree(
            decision("D1", [question(1)]),
            decision("D2", [question(2)]),
            decision("D3", [question(1)], ["D1"]),
        )
        self.assertEqual(designs.branches(made), [["D1", "D3"], ["D2"]])

    def test_a_decision_that_serves_another_goes_with_it(self):
        made = tree(
            decision("D1", [question(1)]), decision("D2", ["D1"]), decision("D3", [question(2)])
        )
        self.assertEqual(designs.branches(made), [["D1", "D2"], ["D3"]])

    def test_a_join_found_late_takes_in_a_branch_made_before(self):
        # Given: D1 and D2 apart, then D3 building on both
        made = tree(
            decision("D1", [question(1)]),
            decision("D2", [question(2)]),
            decision("D3", [question(3)], ["D2", "D1"]),
        )
        self.assertEqual(designs.branches(made), [["D1", "D2", "D3"]])

    def test_a_tree_of_no_decision_has_no_branch(self):
        self.assertEqual(designs.branches(tree()), [])


class TestParted(unittest.TestCase):
    def test_each_branch_becomes_a_part_its_paths_open(self):
        made = tree(decision("D1", [question(1)]), decision("D2", [question(2)]))
        work = {"paths": ["a.py", "b.py"], "commands": [], "parts": []}
        self.assertEqual(
            designs.parted(work, made),
            {
                "paths": ["a.py", "b.py"],
                "commands": [],
                "parts": [
                    {"id": "P1", "decisions": ["D1"], "paths": []},
                    {"id": "P2", "decisions": ["D2"], "paths": []},
                ],
            },
        )

    def test_a_part_of_the_same_decisions_keeps_its_paths(self):
        made = tree(decision("D1", [question(1)]), decision("D2", [question(2)]))
        work = {
            "paths": ["a.py", "b.py"],
            "commands": [],
            "parts": [{"id": "P7", "decisions": ["D2"], "paths": ["b.py"]}],
        }
        self.assertEqual(
            designs.parted(work, made)["parts"],
            [
                {"id": "P1", "decisions": ["D1"], "paths": []},
                {"id": "P2", "decisions": ["D2"], "paths": ["b.py"]},
            ],
        )

    def test_a_work_of_one_part_gives_it_every_path(self):
        made = tree(decision("D1", [question(1)]), decision("D2", ["D1"]))
        work = {"paths": ["README.md"], "commands": [], "parts": []}
        self.assertEqual(
            designs.parted(work, made)["parts"],
            [{"id": "P1", "decisions": ["D1", "D2"], "paths": ["README.md"]}],
        )


class TestWorkFaults(unittest.TestCase):
    def test_the_run_s_work_has_none(self):
        self.assertEqual(
            designs.work_faults(helpers.RUN["work.json"], helpers.RUN["design-tree.json"]), []
        )

    def test_each_way_a_part_fails_is_named(self):
        made = tree(
            decision("D1", [question(1)]),
            decision("D2", [question(2)]),
            decision("D3", ["D2"]),
            decision("D4", [question(3)]),
        )
        work = {
            "paths": ["a.md", "b.md"],
            "commands": [],
            "parts": [
                {"id": "P1", "decisions": ["D1", "D2", "D9"], "paths": ["a.md", "c.md"]},
                {"id": "P2", "decisions": ["D1", "D3"], "paths": ["a.md"]},
                {"id": "P3", "decisions": ["D4"], "paths": []},
            ],
        }
        self.assertEqual(
            designs.work_faults(work, made),
            [
                "P1 names D9, which is no decision of the tree",
                "P1's path c.md is none of the work's paths",
                "P3 has no paths",
                "D1 is in P1 and P2",
                "a.md is in P1 and P2",
                "D3 of P2 is joined to D2 of P1: a part holds every decision joined to its own",
            ],
        )

    def test_a_decision_in_no_part_and_a_work_of_no_path(self):
        made = tree(decision("D1", [question(1)]), decision("D2", [question(2)]))
        work = {
            "paths": [],
            "commands": [],
            "parts": [{"id": "P1", "decisions": ["D1"], "paths": []}],
        }
        self.assertEqual(
            designs.work_faults(work, made),
            ["the work has no paths", "P1 has no paths", "D2 is in no part"],
        )

    def test_a_path_under_a_folder_of_the_work_is_the_work_s(self):
        made = tree(decision("D1", [question(1)]))
        work = {
            "paths": ["src"],
            "commands": [],
            "parts": [{"id": "P1", "decisions": ["D1"], "paths": ["src/a.py"]}],
        }
        self.assertEqual(designs.work_faults(work, made), [])

    def test_a_path_that_only_begins_as_a_folder_of_the_work_is_not_under_it(self):
        made = tree(decision("D1", [question(1)]))
        work = {
            "paths": ["src"],
            "commands": [],
            "parts": [{"id": "P1", "decisions": ["D1"], "paths": ["srcx/a.py"]}],
        }
        self.assertEqual(
            designs.work_faults(work, made), ["P1's path srcx/a.py is none of the work's paths"]
        )


class TestUnder(unittest.TestCase):
    def test_a_path_is_under_itself_and_its_folder_alone(self):
        self.assertTrue(designs.under("b.md", ["b.md"]))
        self.assertTrue(designs.under("src/a.py", ["src/"]))
        for path in ("a.md", "c.md", "srcx/a.py"):
            with self.subTest(path=path):
                self.assertFalse(designs.under(path, ["b.md", "src"]))


class TestRemakeFaults(unittest.TestCase):
    def test_a_remake_of_the_tree_s_decisions_and_questions_has_none(self):
        remake = {"decisions": [{"decision": "D2", "question": question(2), "good_when": "w"}]}
        self.assertEqual(designs.remake_faults(remake, helpers.RUN["design-tree.json"]), [])

    def test_a_decision_or_question_the_tree_has_not(self):
        remake = {"decisions": [{"decision": "D9", "question": question(9), "good_when": "w"}]}
        self.assertEqual(
            designs.remake_faults(remake, helpers.RUN["design-tree.json"]),
            [
                "the remake names D9, which is no decision of the tree",
                "the remake names readme/Q9, which is no question of the tree",
            ],
        )


class TestCheck(helpers.RunTest):
    def test_a_run_that_holds_has_no_fault(self):
        self.lay()
        self.assertEqual(designs.check(self.folder), [])

    def test_the_faults_of_the_tree_the_work_and_the_remake_together(self):
        made = helpers.run()
        made["design-tree.json"]["questions"].pop()
        made["work.json"]["parts"][0]["paths"] = []
        made["remake.json"] = {
            "decisions": [{"decision": "D9", "question": question(1), "good_when": "w"}]
        }
        self.lay(made)
        self.assertEqual(
            designs.check(self.folder),
            [
                "the tree does not ask readme/Q3: Does each answer come when needed?",
                "P1 has no paths",
                "the remake names D9, which is no decision of the tree",
            ],
        )

    def test_a_run_before_its_work_and_remake_checks_the_tree_alone(self):
        made = helpers.run()
        del made["work.json"]
        self.lay(made)
        self.assertEqual(designs.check(self.folder), [])

    def test_a_file_out_of_its_form_cannot_be_checked(self):
        made = helpers.run()
        made["design-tree.json"] = {"questions": []}
        self.lay(made)
        with self.assertRaises(helpers.files.Unreadable) as refused:
            designs.check(self.folder)
        self.assertIn("design-tree.json is out of its form", str(refused.exception))


if __name__ == "__main__":
    unittest.main()
