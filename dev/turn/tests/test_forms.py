"""Each form a judgment is given in, checked against the run's items and the work, and the parts
of the work an item asked of each part is judged in."""

import json
import os
import unittest

from helpers import (
    CHECKED,
    EACH_GOOD,
    EACH_ITEM,
    FOUND,
    GOOD,
    ITEM_B1,
    ITEM_F1,
    ITEMS,
    LESSON,
    QUESTION,
    SECTIONED,
    STOPPED_B1,
    TURN,
    WAITS,
    RepoTest,
    forms,
    testing,
)

(schema,) = testing.lane_code(TURN, "schema")

WORK = ["README.md"]
# The form files of the roles, as lane's in_form holds each role's reply to its own.
FORM_FILES = os.path.join(TURN, "forms")


class FormTest(RepoTest):
    def said(self, data, form):
        """What is wrong with a reply of the data in the form, over the run's two items."""
        return forms.check(json.dumps(data), ITEMS, WORK, form, [])

    def each_said(self, data, form, items=(EACH_ITEM,)):
        """What is wrong with a form over the items, an item asked of each part among them, on a
        work of two parts."""
        self.write("README.md", SECTIONED)
        return forms.check(json.dumps(data), list(items), WORK, form, [EACH_ITEM])


class TestItems(FormTest):
    def test_a_reply_that_is_not_an_object_of_its_lists_is_told_its_shape(self):
        # Given: a reply that is not JSON, JSON that is not an object, and an object missing one
        # of the lists its form takes
        # When: each is checked by the claim's form, and by the reading's
        # Then: each is told the shape to give, the lists its form takes
        for text in ("good", "[]", '{"items": []}'):
            with self.subTest(text=text):
                said = forms.check(text, ITEMS, WORK, forms.CLAIM, [])
                self.assertEqual(said, ['give it as JSON: {"items": [...], "questions": [...]}'])
        said = forms.check("good", ITEMS, WORK, forms.FIRST_READING, [])
        self.assertEqual(said, ['give it as JSON: {"items": [...]}'])

    def test_each_item_out_of_place_is_named_by_its_checklist_and_id(self):
        # Given: a claim naming an item no checklist holds, then another, then one item twice
        # and one of no shape it takes, then another of none
        # When: it is checked
        # Then: each is named in full with what is wrong, not only the first
        bare = ITEM_B1
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
            forms.CLAIM,
        )
        self.assertIn("checklists/readme.md B-8 is not an item judged here", "\n".join(said))
        self.assertIn("checklists/readme.md B-9 is not an item judged here", "\n".join(said))
        self.assertIn("checklists/readme.md F-1 is given twice", "\n".join(said))
        self.assertEqual(sum("B-1 must hold" in s for s in said), 1)
        self.assertEqual(sum("B-1 is given twice" in s for s in said), 1)

    def test_an_item_named_by_its_checklist_s_whole_path_is_the_item_the_ccs_names(self):
        # Given: a claim naming every item by the whole path of its checklist, as each role is
        # given the checklists, one of them asked of each part of the work
        # When: it is checked against the items as the CCS names them
        # Then: it is filled
        whole = os.path.abspath("checklists/readme.md")
        items = [dict(GOOD, checklist=whole), dict(EACH_GOOD, checklist=whole)]
        said = self.each_said({"items": items, "questions": []}, forms.CLAIM, (ITEMS[0], EACH_ITEM))
        self.assertEqual(said, [])

    def test_an_item_naming_no_checklist_is_told_to_name_it(self):
        # Given: a claim with an item that names no checklist, and one whose checklist is no path
        # When: it is checked
        # Then: each is shown as it was given and told to name its checklist
        bare = {"item": "F-1", "good": "it", "lines": ["README.md:1-3"]}
        said = self.said({"items": [bare, dict(bare, checklist=1)], "questions": []}, forms.CLAIM)
        for item in (bare, dict(bare, checklist=1)):
            with self.subTest(item=item):
                self.assertIn(f"{json.dumps(item)} is not an item judged here", "\n".join(said))

    def test_an_item_of_no_shape_is_told_the_shapes_it_takes(self):
        # Given: an item holding none of the shapes its form takes
        # When: it is checked by a form of one shape, and by a form of two
        # Then: it is told the one shape, or the two
        bare = ITEM_F1
        said = self.said({"items": [bare, WAITS], "questions": [QUESTION]}, forms.LEFT)
        self.assertEqual(said, ['checklists/readme.md F-1 must hold "question"'])
        said = self.said({"items": [bare, STOPPED_B1]}, forms.FIRST_READING)
        self.assertEqual(
            said,
            [
                (
                    'checklists/readme.md F-1 must hold one of "good" with "lines" or "places" with'
                    ' "did" with "lacking"'
                )
            ],
        )

    def test_an_item_of_two_shapes_is_told_the_shapes_it_takes(self):
        # Given: a reading whose F-1 holds a Good with its lines and a stop as well
        both = dict(GOOD, places=["README.md:1-3"], did="read it", lacking="nothing")
        # When: it is checked
        # Then: F-1 is told the shapes it takes, one of them
        said = self.said({"items": [both, STOPPED_B1]}, forms.FIRST_READING)
        self.assertEqual(
            said,
            [
                (
                    'checklists/readme.md F-1 must hold one of "good" with "lines" or "places" with'
                    ' "did" with "lacking"'
                )
            ],
        )

    def test_an_item_waiting_on_a_question_not_given_is_named(self):
        # Given: an item waiting on question 0, where questions count from 1, and one waiting on
        # question 2 where one is given
        # When: each is checked
        # Then: it is told the question is not given
        for number in (0, 2):
            with self.subTest(number=number):
                said = self.said(
                    {"items": [GOOD, dict(WAITS, question=number)], "questions": [QUESTION]},
                    forms.CLAIM,
                )
                self.assertIn(
                    f"question {number} is waited on but not given; add it to the questions", said
                )

    def test_items_waiting_on_each_question_given_pass(self):
        # Given: two questions, one item waiting on each
        # When: it is checked
        # Then: it passes, each number from 1 to the count of the questions given
        second = dict(QUESTION, question="Which name?")
        both = {"items": [dict(WAITS, item="F-1"), dict(WAITS, question=2)]}
        said = self.said(dict(both, questions=[QUESTION, second]), forms.CLAIM)
        self.assertEqual(said, [])

    def test_a_question_that_is_not_a_number_or_without_its_words_stops(self):
        # Given: an item waiting on a question named by its words, a question with no recommended
        # answer, and one of empty words
        # When: each is checked
        # Then: each is named with what to give
        for data, words in (
            (
                {"items": [GOOD, dict(WAITS, question="Which?")], "questions": [QUESTION]},
                '"question" is not a number',
            ),
            (
                {"items": [GOOD, WAITS], "questions": [{"question": "Which?"}]},
                'question 1 must hold "question" and "recommended"',
            ),
            (
                {"items": [GOOD, WAITS], "questions": [dict(QUESTION, question=" ")]},
                'question 1 must hold "question" and "recommended"',
            ),
            (
                {"items": [GOOD, dict(WAITS, question=True)], "questions": [QUESTION]},
                '"question" is not a number',
            ),
        ):
            with self.subTest(words=words):
                said = self.said(data, forms.CLAIM)
                self.assertIn(words, "\n".join(said))


class TestFirstReading(FormTest):
    def test_a_first_user_gives_every_item_a_good_or_where_and_how_it_stopped(self):
        # Given: a first user's reading giving one item a Good and the other the places it looked,
        # what it did there and what it did not get; one leaving an item out; and one giving an
        # item asked of each part where it stopped in place of its parts
        # When: it is checked
        # Then: the first and the third pass, and the second is told the item left out
        self.assertEqual(self.said({"items": [GOOD, STOPPED_B1]}, forms.FIRST_READING), [])
        said = self.said({"items": [GOOD]}, forms.FIRST_READING)
        self.assertEqual(
            said, ["checklists/readme.md B-1 is left out; give every item judged here"]
        )
        each = dict(STOPPED_B1, item="B-2", places=["README.md:5-7"])
        said = self.each_said(
            {"items": [GOOD, STOPPED_B1, each]}, forms.FIRST_READING, ITEMS + [EACH_ITEM]
        )
        self.assertEqual(said, [])

    def test_a_stop_without_what_it_did_and_did_not_get_stops(self):
        # Given: a stop giving the places alone, and stops whose words of what it did or did not
        # get are empty
        # When: each is checked
        # Then: the first is told the shape a stop takes, and each other the key left empty
        places = {k: v for k, v in STOPPED_B1.items() if k in ("checklist", "item", "places")}
        said = self.said({"items": [GOOD, places]}, forms.FIRST_READING)
        self.assertEqual(len(said), 1, said)
        self.assertIn('"places" with "did" with "lacking"', said[0])
        for key in ("did", "lacking"):
            with self.subTest(key=key):
                said = self.said(
                    {"items": [GOOD, dict(STOPPED_B1, **{key: " "})]}, forms.FIRST_READING
                )
                self.assertEqual(
                    said, [f'checklists/readme.md B-1 has an empty "{key}"; say it in words']
                )

    def test_a_stop_names_where_its_good_is_not_found(self):
        # Given: a stop with the places its Good is not found, with none, with places no list, or
        # with lines outside the work
        # When: each is checked
        # Then: the first passes, and each other is named
        self.assertEqual(self.said({"items": [GOOD, STOPPED_B1]}, forms.FIRST_READING), [])
        for places, said in (
            ([], "names no lines"),
            ("README.md:3", "names no lines"),
            (["README.md:9"], "README.md:9 is not lines of the work"),
        ):
            with self.subTest(places=places):
                item = dict(STOPPED_B1, places=places)
                said_now = self.said({"items": [GOOD, item]}, forms.FIRST_READING)
                self.assertEqual(len(said_now), 1, said_now)
                self.assertIn(said, said_now[0])


class TestClaim(FormTest):
    def test_a_claim_of_every_item_good_or_waiting_passes(self):
        # Given: the generator's claim, one item Good and the other waiting on a question
        # When: it is checked
        # Then: it passes, as nothing beside the items and questions is asked of it
        said = self.said({"items": [GOOD, WAITS], "questions": [QUESTION]}, forms.CLAIM)
        self.assertEqual(said, [])

    def test_a_claim_asking_before_any_work_is_made_gives_the_items_waiting_alone(self):
        # Given: a generator's reply asking a question before making anything, naming only the
        # item that waits on it; and a claim asking nothing that leaves an item out
        # When: each is checked
        # Then: the first passes, as no Good is set before the work is made, and the second is
        # told the item left out
        self.assertEqual(self.said({"items": [WAITS], "questions": [QUESTION]}, forms.CLAIM), [])
        said = self.said({"items": [GOOD], "questions": []}, forms.CLAIM)
        self.assertEqual(
            said, ["checklists/readme.md B-1 is left out; give every item judged here"]
        )


class TestCheck(FormTest):
    """The orchestrator's check of the CCS, before any work is made."""

    def test_a_check_asks_its_questions_of_an_item(self):
        # Given: a check whose question no item waits on
        # When: it is checked
        # Then: the question is named
        can = [dict(i, can="the decisions") for i in ITEMS]
        said = self.said({"items": can, "questions": [QUESTION]}, forms.CHECK)
        self.assertEqual(
            said, ["question 1 has no item waiting on it; name it at the item it settles"]
        )

    def test_a_check_asking_a_question_still_gives_every_item(self):
        # Given: the orchestrator's check of the CCS naming only the item waiting on its question
        # When: it is checked
        # Then: it is told the item left out, as the check finds for every item what gives its Good
        said = self.said({"items": [WAITS], "questions": [QUESTION]}, forms.CHECK)
        self.assertEqual(
            said, ["checklists/readme.md F-1 is left out; give every item judged here"]
        )


class TestLeft(FormTest):
    def test_every_item_left_waits_on_a_question(self):
        # Given: the orchestrator's questions for the items two rounds left without Good, and one
        # giving an item a Good in place of a question
        # When: each is checked
        # Then: the first passes, and the second is told the item takes a question
        both = {"items": [dict(WAITS, item="F-1"), WAITS], "questions": [QUESTION]}
        self.assertEqual(self.said(both, forms.LEFT), [])
        said = self.said({"items": [GOOD, WAITS], "questions": [QUESTION]}, forms.LEFT)
        self.assertEqual(said, ['checklists/readme.md F-1 must hold "question"'])

    def test_questions_for_the_items_left_are_held_to_their_form(self):
        # Given: the orchestrator's questions for the items left, one without the answer it
        # recommends, and a reply with no list of questions
        # When: each is checked
        # Then: each is told what to give
        items = [dict(WAITS, item="F-1"), WAITS]
        said = self.said({"items": items, "questions": [{"question": "Which?"}]}, forms.LEFT)
        self.assertEqual(len(said), 1, said)
        self.assertIn('question 1 must hold "question" and "recommended"', said[0])
        said = self.said({"items": items}, forms.LEFT)
        self.assertEqual(said, ['give it as JSON: {"items": [...], "questions": [...]}'])


class TestParts(FormTest):
    """A work is split into its parts: a document's sections under its top headings, with the
    title and opening as one, and each other file whole."""

    def test_a_document_is_split_at_its_top_headings(self):
        # Given: a README of a title, an opening and two sections, one with a heading under it,
        # and a heading of its own level inside a fence
        # When: it is split
        # Then: the title and opening are one part, and each section another, from its heading
        # to the line before the next
        self.write(
            "README.md",
            "# x\n\nopening\n## A\n\n### a\n\n```\n## not one\n```\n## B\nb\n",
        )
        self.assertEqual(
            forms.parts(["README.md"]), ["README.md:1-3", "README.md:4-10", "README.md:11-12"]
        )

    def test_a_heading_in_a_fence_of_tildes_or_an_indented_one_opens_no_part(self):
        for fence in ("~~~", "  ```"):
            with self.subTest(fence=fence):
                # Given: a README whose top heading in a fence of tildes, or an indented one, stands
                # between its opening and its one section
                self.write("README.md", f"# x\n\n{fence}\n## not one\n{fence}\n## B\nb\n")
                # When: it is split
                # Then: the fence lies in the opening's part
                self.assertEqual(forms.parts(["README.md"]), ["README.md:1-5", "README.md:6-7"])

    def test_a_heading_of_another_level_or_in_the_frontmatter_opens_no_part(self):
        # Given: a README with a heading of the level above a top one and one below it after its
        # opening, and frontmatter holding a line written as a top heading
        self.write("README.md", "---\nname: x\n## not one\n---\n# x\n\n# y\n### z\n## B\nb\n")
        # When: it is split
        # Then: its one top heading alone opens a part
        self.assertEqual(forms.parts(["README.md"]), ["README.md:1-8", "README.md:9-10"])

    def test_a_document_opening_with_a_section_has_no_opening_part(self):
        # Given: a document whose first line is a top heading, and one with none
        # When: each is split
        # Then: the first is its sections alone, and the second is one part
        self.write("a.md", "## A\na\n## B\n")
        self.write("b.md", "# b\n\nonly\n")
        self.assertEqual(forms.parts(["a.md", "b.md"]), ["a.md:1-2", "a.md:3-3", "b.md:1-3"])

    def test_any_other_file_is_one_part_and_an_empty_file_none(self):
        # Given: a script of three lines holding a line that opens like a heading, and an empty
        # file
        # When: they are split
        # Then: the script is one part, and the empty file gives none
        self.write("x.py", "a = 1\n## b\nc = 2\n")
        self.write("e.md", "")
        self.assertEqual(forms.parts(["x.py", "e.md"]), ["x.py:1-3"])

    def test_a_file_of_the_work_not_written_yet_has_no_part(self):
        # Given: a work of two files, one not written yet
        # When: it is split
        # Then: the file written gives its part alone
        self.assertEqual(forms.parts(["new.md", "README.md"]), ["README.md:1-3"])

    def test_an_item_asked_of_each_part_with_a_good_for_every_part_passes(self):
        # Given: an item asked of each part, given a Good for each part at lines inside it
        # When: it is checked by the forms that give Goods
        # Then: it passes
        for form in (forms.CLAIM, forms.FIRST_READING):
            with self.subTest(form=form):
                data = {"items": [GOOD, dict(GOOD, item="B-1"), EACH_GOOD], "questions": []}
                self.assertEqual(self.each_said(data, form, ITEMS + [EACH_ITEM]), [])

    def test_an_item_given_at_the_wrong_scope_stops(self):
        # Given: an item asked of each part given one Good with its lines, and an item of its part
        # given a Good for each part
        # When: they are checked
        # Then: each is told the shapes its scope takes
        one = dict(EACH_ITEM, good="the reader uses it", lines=["README.md:1-7"])
        said = self.each_said(
            {"items": [one, dict(EACH_GOOD, item="F-1")]},
            forms.FIRST_READING,
            [EACH_ITEM, ITEMS[0]],
        )
        self.assertEqual(
            said,
            [
                (
                    'checklists/readme.md B-2 must hold one of "parts" or "places" with "did" with'
                    ' "lacking", as it is asked of each part'
                ),
                (
                    'checklists/readme.md F-1 must hold one of "good" with "lines" or "places" with'
                    ' "did" with "lacking"'
                ),
            ],
        )

    def test_parts_out_of_their_form_stop(self):
        # Given: an item asked of each part whose parts leave one out, name one not of the work,
        # give one twice, name lines outside their part, give a part of no shape, empty words, or
        # parts as no list
        # When: each is checked
        # Then: each is named with what to give
        first, second = EACH_GOOD["parts"]
        for parts, said in (
            ([first], "README.md:5-7 has no Good; give a Good for every part"),
            (
                [first, dict(second, part="README.md:5-6")],
                (
                    "README.md:5-6 is not a part of the work; give each as one of"
                    " `README.md:1-4`, `README.md:5-7`"
                ),
            ),
            ([first, first, second], "README.md:1-4 is given twice"),
            (
                [first, dict(second, lines=["README.md:4-5"])],
                "README.md:4-5 is not inside its part",
            ),
            ([first, dict(second, lines=["x.md:6"])], "x.md:6 is not lines of the work"),
            ([first, {"part": "README.md:5-7", "good": "x"}], 'part 2 must hold "part", "good"'),
            ([first, dict(second, why="x")], 'part 2 must hold "part", "good"'),
            ([first, "README.md:5-7"], 'must hold "part", "good" and "lines"'),
            ([first, dict(second, good=" ")], 'must hold "part", "good" and "lines"'),
            ("README.md:1-4", "gives its parts as no list"),
        ):
            with self.subTest(parts=parts):
                given = {"items": [dict(EACH_GOOD, parts=parts)]}
                said_now = self.each_said(given, forms.FIRST_READING)
                self.assertEqual(len(said_now), 1, said_now)
                self.assertIn(said, said_now[0])
                self.assertTrue(said_now[0].startswith("checklists/readme.md B-2"), said_now)

    def test_lines_are_inside_their_part_in_its_own_file_alone(self):
        # Given: a work of three files, a script whose name sorts before a document of two parts
        # and one whose name sorts after it, and an item asked of each part whose Goods name lines
        # from each part's first line
        # When: the document's second part names its own lines, or lines of the same numbers in
        # either script
        # Then: the first passes, and each other is named
        self.write("README.md", SECTIONED)
        self.write("0.py", "x\n" * 7)
        self.write("z.py", "x\n" * 7)
        work = ["README.md", "0.py", "z.py"]
        rest = [{"part": f"{p}:1-7", "good": "x", "lines": [f"{p}:1"]} for p in ("0.py", "z.py")]
        for lines, said in (("README.md:5-7", 0), ("0.py:5-7", 1), ("z.py:5-7", 1)):
            with self.subTest(lines=lines):
                second = dict(EACH_GOOD["parts"][1], lines=[lines])
                item = dict(EACH_GOOD, parts=[EACH_GOOD["parts"][0], second, *rest])
                text = json.dumps({"items": [item]})
                found = forms.check(text, [EACH_ITEM], work, forms.FIRST_READING, [EACH_ITEM])
                self.assertEqual(len(found), said, found)

    def test_lines_named_by_a_whole_path_are_inside_their_part(self):
        # Given: an item asked of each part whose Goods name their lines by whole paths, as a role
        # given whole paths names them
        # When: it is checked
        # Then: it passes, as each line is inside its part however the path is written
        parts = [dict(p, lines=[self.here(p["lines"][0])]) for p in EACH_GOOD["parts"]]
        said = self.each_said({"items": [dict(EACH_GOOD, parts=parts)]}, forms.FIRST_READING)
        self.assertEqual(said, [])

    def test_every_part_of_no_shape_is_named(self):
        # Given: an item asked of each part whose two parts both hold no Good
        # When: it is checked
        # Then: both are named
        parts = [{"part": p["part"]} for p in EACH_GOOD["parts"]]
        said = self.each_said({"items": [dict(EACH_GOOD, parts=parts)]}, forms.FIRST_READING)
        self.assertEqual([s.split(": ")[1][:6] for s in said], ["part 1", "part 2"])

    def test_every_part_out_of_place_is_named(self):
        # Given: an item asked of each part whose two parts both name lines outside them
        # When: it is checked
        # Then: both are named
        parts = [dict(p, lines=["README.md:1-7"]) for p in EACH_GOOD["parts"]]
        said = self.each_said({"items": [dict(EACH_GOOD, parts=parts)]}, forms.FIRST_READING)
        self.assertEqual(len(said), 2, said)


class TestLines(FormTest):
    def test_lines_inside_the_work_pass(self):
        # Given: the work of three lines
        # When: a Good names its first line, its last, a range ending before its end, or one line
        # alone
        # Then: each passes
        for lines in ("README.md:1-1", "README.md:2-3", "README.md:1-2", "README.md:3"):
            with self.subTest(lines=lines):
                said = self.said(
                    {"items": [dict(FOUND, lines=[lines]), STOPPED_B1]}, forms.FIRST_READING
                )
                self.assertEqual(said, [])

    def test_lines_the_work_does_not_hold_stop(self):
        # Given: the work of three lines, and a file beside it that is not of the work
        # When: a Good names lines from 0, lines past the work's end, lines running backwards,
        # lines of the file not of the work, or a path with no lines
        # Then: the lines are named with the form they take
        self.write("CHANGELOG.md", "# Changelog\n")
        for lines in (
            "README.md:0-1",
            "README.md:2-9",
            "README.md:3-1",
            "CHANGELOG.md:1",
            "docs/start.md:1",
            "README.md",
        ):
            with self.subTest(lines=lines):
                said = self.said(
                    {"items": [dict(FOUND, lines=[lines]), STOPPED_B1]}, forms.FIRST_READING
                )
                self.assertEqual(len(said), 1, said)
                self.assertIn(f"{lines} is not lines of the work", said[0])
                self.assertIn("<path>:<from>-<to>", said[0])


class TestLessons(FormTest):
    """The learner gives what fell short in the run and why, each lesson the project's own or
    general and resting on the words of a record it was shown."""

    def setUp(self):
        super().setUp()
        self.records = [self.given_record("first-user", "{}"), self.given_record("generator", "{}")]

    def lessons(self, **reply):
        """What is wrong with the learner's reply, by default one general lesson, the records
        those the test has written."""
        reply = dict({"lessons": [LESSON], "checked": CHECKED}, **reply)
        return forms.learnt(json.dumps(reply), self.records)

    def test_lessons_resting_on_words_of_the_records_pass(self):
        # Given: a lesson of the project's own and a general one, each quoting a record, and a
        # reply with no lesson but what it checked
        # When: it is checked
        # Then: it passes
        lessons = [
            dict(LESSON, whose=w, grounds=[{"record": 2, "quote": "{}"}])
            for w in ("own", "general")
        ]
        self.assertEqual(self.lessons(lessons=lessons), [])
        self.assertEqual(self.lessons(lessons=[]), [])

    def test_a_lesson_out_of_its_form_stops(self):
        # Given: a lesson neither own nor general, one with empty words, one with other keys, one
        # quoting no record, a record not given, or words the record does not hold
        # When: it is checked
        # Then: each is named with what to give
        for lesson, said in (
            (dict(LESSON, whose="caller"), 'lesson 1 must hold "lesson" in words, "whose"'),
            (dict(LESSON, lesson=" "), 'lesson 1 must hold "lesson" in words, "whose"'),
            (dict(LESSON, why="x"), 'lesson 1 must hold "lesson" in words, "whose"'),
            ({"whose": "own", "lesson": "x"}, 'lesson 1 must hold "lesson" in words, "whose"'),
            ("read it", 'lesson 1 must hold "lesson" in words, "whose"'),
            (dict(LESSON, grounds=[]), "lesson 1 gives its grounds as no list"),
            (dict(LESSON, grounds={"record": 1}), "lesson 1 gives its grounds as no list"),
            (dict(LESSON, grounds=[{"record": 3, "quote": "I"}]), "ground 1 must hold"),
            (dict(LESSON, grounds=[{"record": 0, "quote": "I"}]), "ground 1 must hold"),
            (dict(LESSON, grounds=[{"record": True, "quote": "I"}]), "ground 1 must hold"),
            (dict(LESSON, grounds=[{"record": 1, "quote": ""}]), "ground 1 must hold"),
            (dict(LESSON, grounds=[{"record": 1}]), "ground 1 must hold"),
            (dict(LESSON, grounds=[{"record": 1, "quote": "{}", "x": 1}]), "ground 1 must hold"),
            (dict(LESSON, grounds=["I"]), "ground 1 must hold"),
            (dict(LESSON, grounds=[{"record": 1, "quote": "I closed it."}]), "is not in record 1"),
        ):
            with self.subTest(lesson=lesson):
                said_now = self.lessons(lessons=[lesson])
                self.assertEqual(len(said_now), 1, said_now)
                self.assertIn(said, said_now[0])

    def test_every_lesson_out_of_its_form_is_named(self):
        # Given: two lessons neither own nor general
        # When: they are checked
        # Then: both are named
        said = self.lessons(lessons=[dict(LESSON, whose="caller")] * 2)
        self.assertEqual([s[:8] for s in said], ["lesson 1", "lesson 2"])

    def test_a_ground_is_found_in_the_record_it_numbers(self):
        # Given: three records, each with words of its own
        # When: a lesson quotes each record's words by its number, or the third's words by
        # another number
        # Then: each found where it numbers passes, and the other is named
        self.records = [self.given_record(f"r{n}", f"words of {n}") for n in (1, 2, 3)]
        for n in (1, 2, 3):
            with self.subTest(n=n):
                ground = {"record": n, "quote": f"words of {n}"}
                self.assertEqual(self.lessons(lessons=[dict(LESSON, grounds=[ground])]), [])
        ground = {"record": 2, "quote": "words of 3"}
        said = self.lessons(lessons=[dict(LESSON, grounds=[ground])])
        self.assertIn("is not in record 2", said[0])

    def test_no_lessons_or_no_scope_checked_stops(self):
        # Given: a reply with no lessons, lessons that are no list, or no scope checked
        # When: it is checked
        # Then: each is named
        for reply, said in (
            ({"checked": CHECKED}, 'give "lessons"'),
            ({"lessons": LESSON, "checked": CHECKED}, 'give "lessons"'),
            ({"lessons": []}, 'give "checked"'),
            ({"lessons": [], "checked": " "}, 'give "checked"'),
            ([], 'give it as JSON: {"lessons": [...], "checked": "..."}'),
        ):
            with self.subTest(reply=reply):
                said_now = forms.learnt(json.dumps(reply), self.records)
                self.assertEqual(len(said_now), 1, said_now)
                self.assertIn(said, said_now[0])


class TestSchemas(FormTest):
    """Each role's reply is held, as it is written, to its JSON Schema by lane's in_form, and then
    by the flow; a reply the flow takes is one the schema takes."""

    def out_of(self, name, value):
        """Where the value is out of the role's schema of the name, None where it holds."""
        with open(os.path.join(FORM_FILES, name), encoding="utf-8") as f:
            form = json.load(f)
        schema.checked(form)
        return schema.held(form, value)

    def test_there_is_a_form_for_each_role_that_replies(self):
        # Given: turn's forms
        # When: they are listed
        # Then: there is one for the generator, the first user and the learner, and none else
        self.assertEqual(
            sorted(os.listdir(FORM_FILES)), ["claim.json", "learnt.json", "reading.json"]
        )

    def test_each_reply_the_flow_takes_is_one_its_schema_takes(self):
        # Given: a claim, a claim asking before making, a reading and the learner's lessons, each
        # taken by the flow
        # When: each is held to its role's schema
        # Then: each holds
        for name, value in (
            ("claim.json", {"items": [GOOD, WAITS, EACH_GOOD], "questions": [QUESTION]}),
            ("claim.json", {"items": [WAITS], "questions": [QUESTION]}),
            ("reading.json", {"items": [FOUND, STOPPED_B1, EACH_GOOD]}),
            ("learnt.json", {"lessons": [LESSON, dict(LESSON, whose="own")], "checked": CHECKED}),
            ("learnt.json", {"lessons": [], "checked": CHECKED}),
        ):
            with self.subTest(name=name, value=value):
                self.assertIsNone(self.out_of(name, value))

    def test_the_shapes_of_an_item_are_the_choices_its_form_file_gives(self):
        # Given: a form file whose item is a choice of two shapes, each requiring the checklist,
        # the ID and keys of its own
        choice = {"type": "object", "required": ["checklist", "item", "a", "b"]}
        defs = {"item": {"anyOf": [{"$ref": "#/$defs/x"}, {"$ref": "#/$defs/y"}]}, "x": choice}
        defs["y"] = dict(choice, required=["checklist", "item", "c"])
        self.write_json("form.json", {"type": "object", "$defs": defs})
        # When: the shapes of its item are read
        # Then: they are each choice's own keys, in the order of the choices
        self.assertEqual(forms.shapes("form.json"), (("a", "b"), ("c",)))

    def test_an_item_of_two_shapes_or_a_key_of_its_own_is_out_of_its_schema(self):
        for item in (dict(GOOD, places=["README.md:1-3"], did="x", lacking="y"), dict(GOOD, x=1)):
            with self.subTest(item=item):
                # Given: a reading whose item holds a Good and a stop, or a key no shape has
                # When: it is held to the first user's schema
                # Then: it is out at the item
                out = self.out_of("reading.json", {"items": [item]})
                self.assertEqual(out.told()[: len("$.items[0]")], "$.items[0]")

    def test_a_lesson_neither_own_nor_general_is_out_of_its_schema(self):
        # Given: the learner's lesson said to be for a role
        # When: it is held to the learner's schema
        # Then: it is out at the lesson's whose
        reply = {"lessons": [dict(LESSON, whose="generator")], "checked": CHECKED}
        out = self.out_of("learnt.json", reply)
        self.assertEqual(out.told()[: len("$.lessons[0].whose")], "$.lessons[0].whose")


if __name__ == "__main__":
    unittest.main()
