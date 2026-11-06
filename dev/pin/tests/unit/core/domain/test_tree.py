"""tree.py, what a design tree is and when it holds: the Markdown file read into the form the checks
take, or refused with why; a tree written as that Markdown; each way the tree fails to hold; and
the decisions open to be decided now."""

import unittest

import helpers
from helpers import decision, made, settled, testing, tree

# The README walkthrough's tree as its Markdown nests it: D3 serves no question, so it stands under
# D1, the decision it first builds on, and names D1, which it serves, on its Also line.
WALKTHROUGH = """\
# Design tree

Goal: Scripts that read `notes list` get its notes as JSON, so they stop parsing text.
- Grounds: the person, 2026-11-03

- **Q1** Can each script that reads notes list read the JSON as it is?
  - **D1 The form of the JSON**: one JSON array, one object for each note (user)
    - Grounds: the person, 2026-11-03
    - **D3 The form of updated**: ISO 8601, as the text gives it (research)
      - Grounds: scripts/sync.py:14 "datetime.fromisoformat(fields[3])"
      - Grounds: the person confirmed, 2026-11-03
      - Also serves: D1
- **Q2** Do people who read notes list by eye see the same as before?
  - **D2 Whether text stays the default**: it stays; JSON only with --json (reasoning)
    - Grounds: the goal, and Q2
"""
# A tree's first lines, the goal with no grounds, for a test to add its list to.
HEAD = "# Design tree\n\nGoal: the goal\n\n"


def read_or_why(text: str) -> str:
    """Why read refuses the text."""
    try:
        tree.read(text)
    except tree.Unreadable as refused:
        return str(refused)
    raise AssertionError(f"read took {text!r}")


class TestRead(unittest.TestCase):
    def test_the_walkthrough_is_read_as_its_nesting_says(self):
        # Given: the README walkthrough's Markdown
        # When: it is read
        # Then: each question serves the goal, each decision serves the question it stands under,
        # D3 builds on D1, which it stands under, and serves D1 by its Also line
        self.assertEqual(
            tree.read(WALKTHROUGH),
            {
                "goal": {
                    "what": (
                        "Scripts that read `notes list` get its notes as JSON, so they stop"
                        " parsing text."
                    ),
                    "grounds": ["the person, 2026-11-03"],
                },
                "questions": [
                    {
                        "id": "Q1",
                        "what": "Can each script that reads notes list read the JSON as it is?",
                    },
                    {
                        "id": "Q2",
                        "what": "Do people who read notes list by eye see the same as before?",
                    },
                ],
                "decisions": [
                    {
                        "id": "D1",
                        "what": "The form of the JSON",
                        "contributes_to": ["Q1"],
                        "builds_on": [],
                        "decided": "one JSON array, one object for each note",
                        "settled_by": "user",
                        "grounds": ["the person, 2026-11-03"],
                    },
                    {
                        "id": "D3",
                        "what": "The form of updated",
                        "contributes_to": ["D1"],
                        "builds_on": ["D1"],
                        "decided": "ISO 8601, as the text gives it",
                        "settled_by": "research",
                        "grounds": [
                            'scripts/sync.py:14 "datetime.fromisoformat(fields[3])"',
                            "the person confirmed, 2026-11-03",
                        ],
                    },
                    decision(
                        "D2",
                        what="Whether text stays the default",
                        contributes_to=["Q2"],
                        decided="it stays; JSON only with --json",
                        settled_by="reasoning",
                        grounds=["the goal, and Q2"],
                    ),
                ],
            },
        )

    def test_the_readme_walkthrough_is_this_tree(self):
        # Given: the tree the README's walkthrough keeps
        # When: it is read
        # Then: it is the tree these tests read
        self.assertEqual(helpers.walkthrough(), tree.read(WALKTHROUGH))

    def test_open_and_who_settled_are_read_from_the_end_of_the_line(self):
        cases = [
            ("open", None, None),
            ("open (user)", None, "user"),
            ("kept (as given) (maker)", "kept (as given)", "maker"),
            ("x: y (reasoning)", "x: y", "reasoning"),
            ("no one named", "no one named", None),
        ]
        for given, decided, by in cases:
            with self.subTest(given=given):
                # Given: a decision whose line ends so
                text = f"{HEAD}- **Q1** q?\n  - **D1 what: it is**: {given}\n"
                # When: it is read
                d = tree.read(text)["decisions"][0]
                # Then: what is decided and who settled it are as the end says, the what whole
                self.assertEqual(
                    (d["what"], d["decided"], d["settled_by"]), ("what: it is", decided, by)
                )

    def test_a_decision_at_the_top_serves_only_what_its_also_lines_name(self):
        # Given: a decision at the top of the list, beside the question, with Also lines
        text = (
            f"{HEAD}- **Q1** q?\n  - **D1 a**: open\n"
            "- **D2 b**: open\n  - Also serves: Q1, D1\n  - Also builds on: D1\n"
        )
        # When: it is read
        d2 = tree.read(text)["decisions"][1]
        # Then: it serves and builds on what its Also lines name, and nothing more
        self.assertEqual((d2["contributes_to"], d2["builds_on"]), (["Q1", "D1"], ["D1"]))

    def test_a_decision_under_a_question_builds_on_what_its_also_line_names(self):
        # Given: a decision under Q1 with both Also lines
        text = (
            f"{HEAD}- **Q1** q?\n  - **D1 a**: open\n  - **D2 b**: open\n"
            "    - Also serves: Q2\n    - Also builds on: D1\n- **Q2** r?\n"
        )
        # When: it is read
        d2 = tree.read(text)["decisions"][1]
        # Then: it serves Q1 and then Q2, and builds on D1
        self.assertEqual((d2["contributes_to"], d2["builds_on"]), (["Q1", "Q2"], ["D1"]))

    def test_a_tree_with_no_question_is_read(self):
        # Given: the goal and its grounds alone
        # When: it is read
        # Then: it has no question and no decision, which the checks name as a gap
        self.assertEqual(
            tree.read("# Design tree\n\nGoal: g\n- Grounds: the person\n"),
            {"goal": {"what": "g", "grounds": ["the person"]}, "questions": [], "decisions": []},
        )

    def test_each_line_out_of_form_is_named(self):
        cases = [
            ("Design tree\n\nGoal: g\n", "line 1 must be `# Design tree`"),
            ("# Design tree\nGoal: g\n", "line 2 must be empty"),
            ("# Design tree\n\nThe goal: g\n", "line 3 must be `Goal: <one sentence>`"),
            ("# Design tree\n", "line 3 must be `Goal: <one sentence>`"),
            (
                "# Design tree\n\nGoal: g\n- **Q1** q?\n",
                "line 4 must be empty, between the goal and its questions",
            ),
            (f"{HEAD}- **Q1** q?\n\n- **Q2** r?\n", "line 6 is empty, inside the list"),
            (
                f"{HEAD}- **Q1** q?\n   - **D1 a**: open\n",
                "line 6 must be indented by two spaces for each item it stands under",
            ),
            (
                f"{HEAD}- **Q1** q?\n    - **D1 a**: open\n",
                "line 6 must be indented by two spaces for each item it stands under",
            ),
            (
                f"{HEAD}- **Q1** q?\n  - **Q2** r?\n",
                "line 6: a question stands at the top of the list, under the goal alone",
            ),
            (
                f"{HEAD}- **Q1** q?\n  - Grounds: g\n",
                "line 6: a Grounds line stands under a decision",
            ),
            (f"{HEAD}- Also serves: Q1\n", "line 5: an Also serves line stands under a decision"),
            (
                f"{HEAD}- **Q1** q?\n  - **D1 a**: open\n    - Also serves: Q1 D1\n",
                "line 7: an Also serves line takes IDs joined by `, `",
            ),
            (
                f"{HEAD}- **Q1** q?\n  - **D1 a**: open\n    - Also builds on: \n",
                "line 7: an Also builds on line takes IDs joined by `, `",
            ),
            (f"{HEAD}- **Q1** q?\n  - **D1 a**: \n", "line 6 is none of the tree's lines"),
            (f"{HEAD}- **Q1** q?\n  - **D1 a** open\n", "line 6 is none of the tree's lines"),
            (f"{HEAD}- **Q1**\n", "line 5 is none of the tree's lines"),
            (f"{HEAD}- **Q1 1** q?\n", "line 5 is none of the tree's lines"),
            (f"{HEAD}- **Q1** q?\n  - Grounds:\n", "line 6 is none of the tree's lines"),
            (f"{HEAD}* **Q1** q?\n", "line 5 is none of the tree's lines"),
        ]
        for text, why in cases:
            with self.subTest(text=text):
                # Given: a text with the line so
                # When: it is read
                # Then: it is refused, naming the line and what it must be
                self.assertIn(why, read_or_why(text))

    def test_the_lines_under_a_decision_keep_their_order(self):
        under = "  - **D1 a**: open\n"
        order = (
            "line 8: the lines under D1 go in the order Grounds, Also serves, Also builds on,"
            " then the decisions under it, each Also line once"
        )
        cases = [
            "    - Also serves: Q1\n    - Grounds: g\n",
            "    - Also builds on: D2\n    - Also serves: Q1\n",
            "    - Also serves: Q1\n    - Also serves: Q1\n",
            "    - **D2 b**: open\n    - Grounds: g\n",
        ]
        for lines in cases:
            with self.subTest(lines=lines):
                # Given: the lines under D1 out of their order
                text = f"{HEAD}- **Q1** q?\n{under}{lines}"
                # When: it is read
                # Then: it is refused, naming the line and the order
                self.assertIn(order, read_or_why(text))

    def test_the_list_of_a_tree_names_the_forms_of_its_lines(self):
        # Given: a line that is none of the tree's
        # When: it is read
        # Then: the fault gives each form a line may take
        self.assertEqual(
            read_or_why(f"{HEAD}- Q1 q?\n"),
            "line 5 is none of the tree's lines: a question `- **<ID>** <intent>`, a decision"
            " `- **<ID> <what is decided>**: <what was decided, or open> (<user, research,"
            " reasoning or maker>)`, `- Grounds: <text>`, `- Also serves: <IDs>` or"
            " `- Also builds on: <IDs>`",
        )

    def test_every_fault_is_named_at_once_a_line_each(self):
        # Given: a text with two lines out of form
        text = f"{HEAD}- **Q1** q?\n  - Grounds: g\n  - **Q2** r?\n"
        # When: it is read
        # Then: both are named, a line each
        self.assertEqual(
            read_or_why(text).splitlines(),
            [
                "line 6: a Grounds line stands under a decision",
                "line 7: a question stands at the top of the list, under the goal alone",
            ],
        )

    def test_an_item_under_a_line_out_of_form_is_read_under_its_parent(self):
        # Given: a question nested under another, out of form, with a decision under it
        text = f"{HEAD}- **Q1** q?\n  - **Q2** r?\n    - **D1 a**: open\n"
        # When: it is read
        # Then: the question alone is named, the decision taken as standing under Q1
        self.assertEqual(
            read_or_why(text),
            "line 6: a question stands at the top of the list, under the goal alone",
        )

    def test_the_ids_named_are_held_to_the_tree(self):
        cases = [
            (f"{HEAD}- **Q1** q?\n  - **Q1 a**: open\n", "the ID Q1 is used twice"),
            (
                f"{HEAD}- **Q1** q?\n  - **D1 a**: open\n    - Also serves: Q9\n",
                "D1 contributes to Q9, which is not in the tree",
            ),
            (
                f"{HEAD}- **Q1** q?\n  - **D1 a**: open\n    - Also builds on: Q1\n",
                "D1 builds on Q1, which is not a decision of the tree",
            ),
            (
                f"{HEAD}- **Q1** q?\n  - **D1 a**: open\n    - Also serves: D1\n",
                "D1 contributes to itself",
            ),
            (
                f"{HEAD}- **Q1** q?\n  - **D1 a**: open\n    - Also builds on: D1\n",
                "D1 builds on itself",
            ),
        ]
        for text, why in cases:
            with self.subTest(why=why):
                # Given: a tree naming the ID so
                # When: it is read
                # Then: it is refused, saying which ID and how
                self.assertIn(why, read_or_why(text))

    def test_a_text_ending_in_a_line_break_or_not_is_read_alike(self):
        # Given: the walkthrough with no line break at its end
        # When: it is read
        # Then: it is read as with one
        self.assertEqual(tree.read(WALKTHROUGH.rstrip("\n")), tree.read(WALKTHROUGH))


class TestLoad(testing.FolderTest):
    def test_a_file_in_form_is_read(self):
        # Given: the walkthrough's tree in a file
        self.write("design-tree.md", WALKTHROUGH)
        # When: it is loaded
        # Then: it is the tree its text holds
        self.assertEqual(tree.load("design-tree.md"), tree.read(WALKTHROUGH))

    def test_a_missing_file_is_refused(self):
        # Given: no file at the path
        # When: it is loaded
        with self.assertRaises(tree.Unreadable) as refused:
            tree.load("gone.md")
        # Then: it is refused, naming the path
        self.assertEqual(str(refused.exception), "there is no file gone.md")

    def test_a_file_not_text_is_refused(self):
        # Given: a file whose bytes are not UTF-8
        with open("design-tree.md", "wb") as f:
            f.write(b"\xff\xfe")
        # When: it is loaded
        with self.assertRaises(tree.Unreadable) as refused:
            tree.load("design-tree.md")
        # Then: it is refused, saying so
        self.assertEqual(str(refused.exception), "it is not text in UTF-8")

    def test_a_tree_saved_is_its_markdown_in_a_folder_made(self):
        # Given: the walkthrough's tree
        # When: it is saved into a folder not yet there
        tree.save("new/design-tree.md", tree.read(WALKTHROUGH))
        # Then: the file holds its Markdown
        self.assertEqual(self.read("new/design-tree.md"), WALKTHROUGH)

    def test_a_tree_saved_by_a_bare_name_lies_in_the_folder_it_is_saved_from(self):
        # Given: the walkthrough's tree
        # When: it is saved by a name with no folder
        tree.save("design-tree.md", tree.read(WALKTHROUGH))
        # Then: the file there holds its Markdown
        self.assertEqual(self.read("design-tree.md"), WALKTHROUGH)


class TestMarkdown(unittest.TestCase):
    def test_the_walkthrough_is_written_as_its_readme_shows_it(self):
        # Given: the walkthrough's tree
        # When: it is written as Markdown
        # Then: it is the text the README keeps
        self.assertEqual(tree.markdown(tree.read(WALKTHROUGH)), WALKTHROUGH)

    def test_a_decision_stands_under_the_first_question_it_serves(self):
        # Given: D1 serves D2 and then Q2, and builds on D2
        data = made(
            decision("D2"),
            decision("D1", contributes_to=["D2", "Q2"], builds_on=["D2"]),
            questions=("Q1", "Q2"),
        )
        # When: the tree is written
        # Then: D1 stands under Q2, and names D2 on each Also line
        self.assertEqual(
            tree.markdown(data),
            "# Design tree\n\nGoal: the goal\n- Grounds: the person\n\n"
            "- **Q1** does Q1 hold?\n  - **D2 what D2 decides**: open\n"
            "- **Q2** does Q2 hold?\n  - **D1 what D1 decides**: open\n"
            "    - Also serves: D2\n    - Also builds on: D2\n",
        )

    def test_a_decision_serving_no_question_stands_under_the_one_it_first_builds_on(self):
        # Given: D2 serves D1 alone, and builds on D1 and D3
        data = made(
            decision("D1"),
            decision("D3"),
            decision("D2", contributes_to=["D1"], builds_on=["D1", "D3"]),
        )
        # When: the tree is written
        # Then: D2 stands under D1, naming what else it serves and builds on
        self.assertIn(
            "  - **D1 what D1 decides**: open\n    - **D2 what D2 decides**: open\n"
            "      - Also serves: D1\n      - Also builds on: D3\n",
            tree.markdown(data),
        )

    def test_a_decision_with_no_place_stands_at_the_top_after_the_questions(self):
        # Given: D2 serves nothing and builds on nothing; D3 and D4 serve no question and build on
        # each other in a loop
        data = made(
            decision("D1"),
            decision("D2", contributes_to=[]),
            decision("D3", contributes_to=[], builds_on=["D4"]),
            decision("D4", contributes_to=[], builds_on=["D3"]),
        )
        # When: the tree is written
        # Then: each stands at the top, after the questions, in the tree's order
        self.assertTrue(
            tree.markdown(data).endswith(
                "- **D2 what D2 decides**: open\n"
                "- **D3 what D3 decides**: open\n  - Also builds on: D4\n"
                "- **D4 what D4 decides**: open\n  - Also builds on: D3\n"
            )
        )

    def test_a_decision_under_a_loop_stands_under_it(self):
        # Given: D2 and D3 build on each other, serving no question, and D4 builds on D2
        data = made(
            decision("D1"),
            decision("D2", contributes_to=[], builds_on=["D3"]),
            decision("D3", contributes_to=[], builds_on=["D2"]),
            decision("D4", contributes_to=[], builds_on=["D2"]),
        )
        # When: the tree is written
        written = tree.markdown(data)
        # Then: the loop stands at the top, and D4 under D2
        self.assertIn(
            "- **D2 what D2 decides**: open\n  - Also builds on: D3\n"
            "  - **D4 what D4 decides**: open\n",
            written,
        )
        self.assertEqual(tree.read(written)["decisions"][2]["builds_on"], ["D2"])

    def test_who_settled_a_decision_ends_its_line(self):
        # Given: D1 decided by the person, and D2 open with a settled_by
        data = made(settled("D1"), decision("D2", settled_by="maker"))
        # When: the tree is written
        written = tree.markdown(data)
        # Then: each line ends with who settled it, open where it is not decided
        self.assertIn("- **D1 what D1 decides**: D1 decided (user)\n", written)
        self.assertIn("- **D2 what D2 decides**: open (maker)\n", written)


class TestFormFaults(unittest.TestCase):
    def test_each_missing_or_mistyped_part_is_named(self):
        cases = [
            ("goal", None, "goal must be an object with what and grounds"),
            ("goal", {"what": "", "grounds": []}, "goal.what must be one line of text, not empty"),
            ("goal", {"what": "a\nb", "grounds": []}, "goal.what must be one line of text"),
            ("goal", {"what": "g", "grounds": "x"}, "goal.grounds must be a list of texts"),
            ("goal", {"what": "g", "grounds": [1]}, "goal.grounds must be a list of texts"),
            ("questions", {}, "questions must be a list"),
            ("questions", ["Q1"], "questions[0] must be an object with id and what"),
            ("questions", [{"id": "", "what": "w"}], "questions[0].id must be an ID"),
            ("questions", [{"id": "Q 1", "what": "w"}], "questions[0].id must be an ID"),
            ("questions", [{"id": "Q1"}], "questions[0].what must be one line of text"),
            ("decisions", None, "decisions must be a list"),
            ("decisions", [7], "decisions[0] must be an object"),
        ]
        for key, value, why in cases:
            with self.subTest(key=key, value=value):
                # Given: the walkthrough's tree with the part so, or left out where None
                data = helpers.walkthrough()
                if value is None:
                    del data[key]
                else:
                    data[key] = value
                # When: its form is checked
                # Then: the part is named with what it must be
                self.assertIn(why, "\n".join(tree.form_faults(data)))

    def test_a_tree_not_an_object_is_out_of_form(self):
        # Given: a list
        # When: its form is checked
        # Then: it is named as no tree
        self.assertEqual(
            tree.form_faults([]), ["the tree must be an object with goal, questions and decisions"]
        )

    def test_each_mistyped_field_of_a_decision_is_named(self):
        cases = [
            ({"id": 3}, "decisions[0].id must be an ID"),
            ({"id": "D,1"}, "decisions[0].id must be an ID"),
            ({"what": ""}, "decisions[0].what must be one line of text, not empty, with no `**`"),
            ({"what": "a **b**"}, "decisions[0].what must be one line of text, not empty, with no"),
            ({"contributes_to": "Q1"}, "decisions[0].contributes_to must be a list of IDs"),
            ({"builds_on": [1]}, "decisions[0].builds_on must be a list of IDs"),
            (
                {"decided": ""},
                "decisions[0].decided must be one line of text, not empty and not `open`, or null",
            ),
            ({"decided": "open"}, "decisions[0].decided must be one line of text"),
            ({"decided": 1}, "decisions[0].decided must be one line of text"),
            (
                {"settled_by": "chance"},
                "decisions[0].settled_by must be user, research, reasoning or maker, or null",
            ),
            ({"grounds": None}, "decisions[0].grounds must be a list of texts"),
            ({"grounds": ["a\nb"]}, "decisions[0].grounds must be a list of texts"),
        ]
        for given, why in cases:
            with self.subTest(given=given):
                # Given: a tree whose one decision has the field so
                data = made(decision("D1", **given))
                # When: its form is checked
                # Then: the field is named with what it must be
                self.assertIn(why, "\n".join(tree.form_faults(data)))

    def test_a_missing_field_of_a_decision_is_named(self):
        # Given: a decision with no builds_on
        lacking = decision("D1")
        del lacking["builds_on"]
        # When: its form is checked
        # Then: the field is named
        self.assertEqual(
            tree.form_faults(made(lacking)), ["decisions[0].builds_on must be a list of IDs"]
        )

    def test_each_who_a_decision_may_be_settled_by_is_in_form(self):
        for by in tree.SETTLED_BY:
            with self.subTest(by=by):
                # Given: a decision settled by the person, a fact found, what follows, or the
                # maker AI that handed the tree over
                # When: its form is checked
                # Then: it is in form
                self.assertEqual(tree.form_faults(made(settled("D1", settled_by=by))), [])

    def test_the_ids_are_held_once_the_parts_are_in_form(self):
        # Given: a decision with the ID of a question
        # When: its form is checked
        # Then: the ID is named
        self.assertEqual(
            tree.form_faults(made(decision("Q1", contributes_to=[]))), ["the ID Q1 is used twice"]
        )


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
        # Given: D1 and D2 build on each other, read from Markdown, so each ID is a text of its own
        text = f"{HEAD}- **Q1** q?\n  - **D1 a**: open\n    - Also builds on: D2\n"
        text += "  - **D2 b**: open\n    - Also builds on: D1\n"
        # When: the problems are found
        # Then: the loop is named
        self.assertEqual(
            tree.problems(tree.read(text)),
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
