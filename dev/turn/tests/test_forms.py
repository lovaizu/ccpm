import json

from helpers import (
    CHECKED,
    EACH_GOOD,
    GOOD,
    LESSON,
    PARTS,
    QUESTION,
    SECTIONED,
    SENT_BACK,
    STOPPED,
    WAITS,
    RepoTest,
    forms,
)

ITEMS = [
    {"checklist": "checklists/readme.md", "item": "F-1"},
    {"checklist": "checklists/readme.md", "item": "B-1"},
]
WORK = ["README.md"]


EACH_ITEM = {"checklist": "checklists/readme.md", "item": "B-2"}


class FormTest(RepoTest):
    def said(self, data, form, records=()):
        return forms.check(json.dumps(data), ITEMS, WORK, form, records=records)

    def each_said(self, data, form):
        """What is wrong with a form over the items and an item asked of each part, on a work of
        two parts."""
        self.write("README.md", SECTIONED)
        each = [(EACH_ITEM["checklist"], EACH_ITEM["item"])]
        return forms.check(json.dumps(data), ITEMS + [EACH_ITEM], WORK, form, each=each)


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
            [
                (
                    'checklists/readme.md F-1 must hold one of "good" with "lines", "question" or'
                    ' "gets" with "places"'
                )
            ],
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


class TestFirstReading(FormTest):
    def test_a_first_user_gives_every_item_a_good_or_where_and_how_it_stopped(self):
        # Given: a first user's reading giving one item a Good and the other the places it looked,
        # what it did there and what it did not get; one leaving an item out; and one giving an
        # item asked of each part where it stopped in place of its parts
        # When: it is checked
        # Then: the first and the third pass, and the second is told the item left out
        self.assertEqual(self.said({"items": [GOOD, STOPPED]}, forms.FIRST_READING), [])
        said = self.said({"items": [GOOD]}, forms.FIRST_READING)
        self.assertEqual(
            said, ["checklists/readme.md B-1 is left out; give every item judged here"]
        )
        each = dict(STOPPED, item="B-2", places=["README.md:5-7"])
        said = self.each_said({"items": [GOOD, STOPPED, each]}, forms.FIRST_READING)
        self.assertEqual(said, [])

    def test_a_stop_without_what_it_did_and_did_not_get_stops(self):
        # Given: a stop giving the places alone, and stops whose words of what it did or did not
        # get are empty
        # When: each is checked
        # Then: the first is told the shape a stop takes, and each other the key left empty
        places = {k: v for k, v in STOPPED.items() if k in ("checklist", "item", "places")}
        said = self.said({"items": [GOOD, places]}, forms.FIRST_READING)
        self.assertEqual(len(said), 1, said)
        self.assertIn('"places" with "did" with "lacking"', said[0])
        for key in ("did", "lacking"):
            with self.subTest(key=key):
                said = self.said(
                    {"items": [GOOD, dict(STOPPED, **{key: " "})]}, forms.FIRST_READING
                )
                self.assertEqual(
                    said, [f'checklists/readme.md B-1 has an empty "{key}"; say it in words']
                )


class TestClaim(FormTest):
    def test_a_claim_of_every_item_good_or_waiting_passes(self):
        # Given: the generator's claim, one item Good and the other waiting on a question
        # When: it is checked
        # Then: it passes, as nothing beside the items and questions is asked of it
        said = self.said({"items": [GOOD, WAITS], "questions": [QUESTION]}, forms.CLAIM)
        self.assertEqual(said, [])


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
        for form in (forms.GOOD, forms.CLAIM, forms.DECISION):
            with self.subTest(form=form):
                items = [EACH_GOOD] if form is forms.GOOD else [GOOD, WAITS, EACH_GOOD]
                data = {"items": items, "questions": [QUESTION], "statements": []}
                self.assertEqual(self.each_said(data, form), [])
        self.assertEqual(forms.parts(WORK), PARTS)

    def test_an_item_given_at_the_wrong_scope_stops(self):
        # Given: an item asked of each part given one Good with its lines, and an item of its part
        # given a Good for each part
        # When: they are checked
        # Then: each is told the shapes its scope takes
        one = dict(EACH_ITEM, good="the reader uses it", lines=["README.md:1-7"])
        said = self.each_said({"items": [one, dict(EACH_GOOD, item="F-1")]}, forms.GOOD)
        self.assertEqual(
            said,
            [
                'checklists/readme.md B-2 must hold "parts", as it is asked of each part',
                'checklists/readme.md F-1 must hold "good" with "lines"',
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
                said_now = self.each_said({"items": [dict(EACH_GOOD, parts=parts)]}, forms.GOOD)
                self.assertEqual(len(said_now), 1, said_now)
                self.assertIn(said, said_now[0])
                self.assertTrue(said_now[0].startswith("checklists/readme.md B-2"), said_now)

    def test_lines_are_inside_their_part_in_its_own_file_alone(self):
        # Given: a work of three files, a script whose name sorts before a document of two parts
        # and one whose name sorts after it, and an item asked of each part whose Goods name lines from each part's first
        # line
        # When: the document's second part names its own lines, or lines of the same numbers in
        # either script
        # Then: the first passes, and each other is named
        self.write("README.md", SECTIONED)
        self.write("0.py", "x\n" * 7)
        self.write("z.py", "x\n" * 7)
        work = ["README.md", "0.py", "z.py"]
        rest = [{"part": f"{p}:1-7", "good": "x", "lines": [f"{p}:1"]} for p in ("0.py", "z.py")]
        each = [(EACH_ITEM["checklist"], EACH_ITEM["item"])]
        for lines, said in (("README.md:5-7", 0), ("0.py:5-7", 1), ("z.py:5-7", 1)):
            with self.subTest(lines=lines):
                second = dict(EACH_GOOD["parts"][1], lines=[lines])
                item = dict(EACH_GOOD, parts=[EACH_GOOD["parts"][0], second, *rest])
                text = json.dumps({"items": [item]})
                found = forms.check(text, ITEMS + [EACH_ITEM], work, forms.GOOD, each=each)
                self.assertEqual(len(found), said, found)

    def test_lines_named_by_a_whole_path_are_inside_their_part(self):
        # Given: an item asked of each part whose Goods name their lines by whole paths, as a role
        # given whole paths names them
        # When: it is checked
        # Then: it passes, as each line is inside its part however the path is written
        parts = [dict(p, lines=[self.here(p["lines"][0])]) for p in EACH_GOOD["parts"]]
        said = self.each_said({"items": [dict(EACH_GOOD, parts=parts)]}, forms.GOOD)
        self.assertEqual(said, [])

    def test_every_part_out_of_place_is_named(self):
        # Given: an item asked of each part whose two parts both name lines outside them
        # When: it is checked
        # Then: both are named
        parts = [dict(p, lines=["README.md:1-7"]) for p in EACH_GOOD["parts"]]
        said = self.each_said({"items": [dict(EACH_GOOD, parts=parts)]}, forms.GOOD)
        self.assertEqual(len(said), 2, said)

    def test_an_item_sent_back_names_where_its_good_is_not_found(self):
        # Given: an item sent back with the places its Good is not found, with none, with places
        # no list, or with lines outside the work
        # When: each is checked
        # Then: the first passes, and each other is named
        self.assertEqual(
            self.said({"items": [GOOD, SENT_BACK], "questions": []}, forms.DECISION), []
        )
        for places, said in (
            ([], "names no lines"),
            ("README.md:3", "names no lines"),
            (["README.md:9"], "README.md:9 is not lines of the work"),
        ):
            with self.subTest(places=places):
                item = dict(SENT_BACK, places=places)
                said_now = self.said({"items": [GOOD, item], "questions": []}, forms.DECISION)
                self.assertEqual(len(said_now), 1, said_now)
                self.assertIn(said, said_now[0])


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


class TestLessons(FormTest):
    """The learner gives how the run went, each lesson resting on the words of a record it was
    shown."""

    def setUp(self):
        super().setUp()
        self.records: tuple[str, ...] = (
            self.given_record("first-user", "{}"),
            self.given_record("evaluator", "{}"),
        )

    def lessons(self, **reply):
        reply = dict({"process": [LESSON], "checked": CHECKED}, **reply)
        return self.said(reply, forms.LEARNT, records=self.records)

    def test_lessons_resting_on_words_of_the_records_pass(self):
        # Given: a lesson for each role, the orchestrator's included, each quoting a record, and a
        # reply with no lesson but what it checked
        # When: it is checked
        # Then: it passes
        roles = ("orchestrator", "generator", "first-user", "evaluator", "learner")
        lessons = [dict(LESSON, role=r, grounds=[{"record": 2, "quote": "{}"}]) for r in roles]
        self.assertEqual(self.lessons(process=lessons), [])
        self.assertEqual(self.lessons(process=[]), [])

    def test_a_lesson_out_of_its_form_stops(self):
        # Given: a lesson for no role of turn, one with empty words, one with other keys, one
        # quoting no record, a record not given, or words the record does not hold
        # When: it is checked
        # Then: each is named with what to give
        for lesson, said in (
            (dict(LESSON, role="caller"), 'lesson 1 must hold "role", one of'),
            (dict(LESSON, lesson=" "), 'lesson 1 must hold "role", one of'),
            (dict(LESSON, why="x"), 'lesson 1 must hold "role", one of'),
            ({"role": "generator", "lesson": "x"}, 'lesson 1 must hold "role", one of'),
            ("read it", 'lesson 1 must hold "role", one of'),
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
                said_now = self.lessons(process=[lesson])
                self.assertEqual(len(said_now), 1, said_now)
                self.assertIn(said, said_now[0])

    def test_every_lesson_out_of_its_form_is_named(self):
        # Given: two lessons for no role of turn
        # When: they are checked
        # Then: both are named
        said = self.lessons(process=[dict(LESSON, role="caller")] * 2)
        self.assertEqual([s[:8] for s in said], ["lesson 1", "lesson 2"])

    def test_a_ground_is_found_in_the_record_it_numbers(self):
        # Given: three records, each with words of its own
        # When: a lesson quotes each record's words by its number, or the third's words by
        # another number
        # Then: each found where it numbers passes, and the other is named
        self.records = tuple(self.given_record(f"r{n}", f"words of {n}") for n in (1, 2, 3))
        for n in (1, 2, 3):
            with self.subTest(n=n):
                ground = {"record": n, "quote": f"words of {n}"}
                self.assertEqual(self.lessons(process=[dict(LESSON, grounds=[ground])]), [])
        ground = {"record": 2, "quote": "words of 3"}
        said = self.lessons(process=[dict(LESSON, grounds=[ground])])
        self.assertIn("is not in record 2", said[0])

    def test_no_process_or_no_scope_checked_stops(self):
        # Given: a reply with no process, process that is no list, or no scope checked
        # When: it is checked
        # Then: each is named
        for reply, said in (
            ({"checked": CHECKED}, 'give "process"'),
            ({"process": LESSON, "checked": CHECKED}, 'give "process"'),
            ({"process": []}, 'give "checked"'),
            ({"process": [], "checked": " "}, 'give "checked"'),
            ([], 'give it as JSON: {"process": [...], "checked": "..."}'),
        ):
            with self.subTest(reply=reply):
                said_now = self.said(reply, forms.LEARNT, records=self.records)
                self.assertEqual(len(said_now), 1, said_now)
                self.assertIn(said, said_now[0])


# What the learner found, offered to the orchestrator to take.
OFFER = {"process": [LESSON, dict(LESSON, role="learner")], "checked": CHECKED}


class TestTaken(FormTest):
    """The orchestrator takes, of what the learner found, what holds."""

    def test_what_is_taken_from_the_offer_passes(self):
        # Given: the learner's findings offered
        # When: the orchestrator takes the second lesson, or none
        # Then: it passes
        for taken in ({"process": [2]}, {"process": []}):
            with self.subTest(taken=taken):
                self.assertEqual(forms.taken(json.dumps(taken), OFFER), [])

    def test_what_is_not_in_the_offer_or_out_of_its_form_stops(self):
        # Given: the learner's findings offered
        # When: the orchestrator takes a lesson numbered past the last, from 0, twice, or not a
        # number, or gives no JSON or no list
        # Then: each is named
        for taken, said in (
            ({"process": [3]}, "lesson 3 is not one of 1 to 2"),
            ({"process": [0]}, "lesson 0 is not one of 1 to 2"),
            ({"process": [True]}, "lesson True is not one of 1 to 2"),
            ({"process": [1, 1]}, "lesson 1 is given twice"),
            ({"process": 1}, 'give it as JSON: {"process": [...]}'),
            ("taken", 'give it as JSON: {"process": [...]}'),
        ):
            with self.subTest(taken=taken):
                text = taken if isinstance(taken, str) else json.dumps(taken)
                said_now = forms.taken(text, OFFER)
                self.assertEqual(len(said_now), 1, said_now)
                self.assertIn(said, said_now[0])
