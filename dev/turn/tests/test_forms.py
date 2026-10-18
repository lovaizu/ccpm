import json

from helpers import GOOD, QUESTION, SENT_BACK, UNSOURCED, WAITS, RepoTest, forms

ITEMS = [
    {"checklist": "checklists/readme.md", "item": "F-1"},
    {"checklist": "checklists/readme.md", "item": "B-1"},
]
WORK = ["README.md"]


class FormTest(RepoTest):
    def said(self, data, form, sources=()):
        return forms.check(json.dumps(data), ITEMS, WORK, form, sources=sources)


class TestItems(FormTest):
    def test_each_item_out_of_place_is_named_by_its_checklist_and_id(self):
        # Given: a reading naming an item no checklist holds, then another, then one item twice
        # and one of no shape it takes, then another of none
        # When: it is checked
        # Then: each is named in full with what is wrong, not only the first
        bare = {"checklist": "checklists/readme.md", "item": "B-1"}
        said = self.said(
            {
                "items": [
                    dict(GOOD, item="B-8"),
                    dict(GOOD, item="B-9"),
                    GOOD,
                    GOOD,
                    bare,
                    bare,
                ],
                "questions": [],
            },
            forms.DECISION,
        )
        self.assertIn("checklists/readme.md B-8 is not an item judged here", "\n".join(said))
        self.assertIn("checklists/readme.md B-9 is not an item judged here", "\n".join(said))
        self.assertIn("checklists/readme.md F-1 is given twice", "\n".join(said))
        self.assertEqual(sum("B-1 must hold" in s for s in said), 1)
        self.assertEqual(sum("B-1 is given twice" in s for s in said), 1)

    def test_an_item_of_no_shape_is_told_the_shapes_it_takes(self):
        # Given: an item holding none of the shapes its form takes
        # When: it is checked by a form of one shape, and by a form of three
        # Then: it is told the one shape, or the three
        bare = {"checklist": "checklists/readme.md", "item": "F-1"}
        said = self.said({"items": [bare]}, forms.GOOD)
        self.assertEqual(said, ['checklists/readme.md F-1 must hold "good" with "lines"'])
        said = self.said({"items": [bare, SENT_BACK], "questions": []}, forms.DECISION)
        self.assertEqual(
            said,
            ['checklists/readme.md F-1 must hold one of "good" with "lines", "question" or "gets"'],
        )

    def test_a_check_asks_its_questions_of_an_item(self):
        # Given: a check whose question no item waits on
        # When: it is checked
        # Then: the question is named
        can = [dict(i, can="the decisions") for i in ITEMS]
        said = self.said({"items": can, "questions": [QUESTION]}, forms.CHECK)
        self.assertEqual(
            said, ["question 1 has no item waiting on it; name it at the item it settles"]
        )

    def test_an_item_waiting_on_question_zero_is_named(self):
        # Given: an item waiting on question 0, where questions count from 1
        # When: it is checked
        # Then: it is told the question is not given
        said = self.said(
            {"items": [GOOD, dict(WAITS, question=0)], "questions": [QUESTION]},
            forms.DECISION,
        )
        self.assertIn("question 0 is waited on but not given; add it to the questions", said)


class TestLines(FormTest):
    def test_lines_inside_the_work_pass(self):
        # Given: the work of three lines
        # When: a Good names its first line, its last, a range ending before its end, or one line
        # alone
        # Then: each passes
        for lines in ("README.md:1-1", "README.md:2-3", "README.md:1-2", "README.md:3"):
            with self.subTest(lines=lines):
                said = self.said(
                    {"items": [dict(GOOD, lines=[lines]), SENT_BACK], "questions": []},
                    forms.DECISION,
                )
                self.assertEqual(said, [])

    def test_lines_from_zero_stop(self):
        # Given: the work, whose lines count from 1
        # When: a Good names lines from 0
        # Then: the lines are named
        said = self.said(
            {"items": [dict(GOOD, lines=["README.md:0-1"]), SENT_BACK], "questions": []},
            forms.DECISION,
        )
        self.assertEqual(len(said), 1)
        self.assertIn("README.md:0-1 is not lines of the work", said[0])

    def test_a_file_beside_a_folder_named_is_not_inside_it(self):
        # Given: sources naming the folder docs, and a file outside it
        # When: a statement rests on that file
        # Then: the file is named as not a source
        self.write("other.md", "x\n")
        statement = {"lines": ["README.md:3-3"], "from": ["other.md:1-1"]}
        reply = {"items": [GOOD, WAITS], "questions": [QUESTION], "statements": [statement]}
        said = self.said(reply, forms.CLAIM, sources=("docs",))
        self.assertEqual(len(said), 1)
        self.assertIn("other.md:1-1 is not lines of the CCS or a file it names", said[0])


class TestStatements(FormTest):
    def test_each_statement_short_of_its_keys_is_named(self):
        # Given: two statements sent back, each without what the receiver gets
        # When: they are checked
        # Then: each is named with the keys it must hold
        short = {"lines": UNSOURCED["lines"]}
        said = self.said(
            {"items": [GOOD, SENT_BACK], "questions": [], "unsourced": [short, short]},
            forms.READING,
        )
        self.assertEqual(
            said,
            [
                'statement 1 of unsourced must hold {"lines", "gets"} alone',
                'statement 2 of unsourced must hold {"lines", "gets"} alone',
            ],
        )
