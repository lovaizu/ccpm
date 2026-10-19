import json
import os

from helpers import (
    CHECKED,
    EACH_GOOD,
    GOOD,
    LESSON,
    MARKED,
    PARTS,
    QUESTION,
    SECTIONED,
    SENT_BACK,
    STATEMENT,
    UNSOURCED,
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
    def said(self, data, form, sources=(), records=()):
        return forms.check(json.dumps(data), ITEMS, WORK, form, sources=sources, records=records)

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
    def test_a_first_user_gives_every_item_a_good_or_the_places_it_looked(self):
        # Given: a first user's reading giving one item a Good and the other places, one leaving
        # an item out, and one giving an item asked of each part places in place of its parts
        # When: it is checked
        # Then: the first and the third pass, and the second is told the item left out
        stopped = {"checklist": "checklists/readme.md", "item": "B-1", "places": ["README.md:1"]}
        self.assertEqual(self.said({"items": [GOOD, stopped]}, forms.FIRST_READING), [])
        said = self.said({"items": [GOOD]}, forms.FIRST_READING)
        self.assertEqual(
            said, ["checklists/readme.md B-1 is left out; give every item judged here"]
        )
        each = dict(EACH_ITEM, places=["README.md:5-7"])
        said = self.each_said({"items": [GOOD, stopped, each]}, forms.FIRST_READING)
        self.assertEqual(said, [])


# An item the first user stopped at, offered to hold.
STOPS = [{"checklist": "checklists/readme.md", "item": "B-1", "places": ["README.md:1"]}]


class TestHeld(FormTest):
    def test_what_is_held_of_the_items_offered_passes(self):
        # Given: an offer of one item to hold
        # When: the orchestrator holds it, or none, in a ```json fence or not
        # Then: it passes
        held = {"held": [{"checklist": "checklists/readme.md", "item": "B-1"}]}
        for text in (
            json.dumps(held),
            json.dumps({"held": []}),
            f"```json\n{json.dumps(held)}\n```",
        ):
            with self.subTest(text=text):
                self.assertEqual(forms.held(text, STOPS), [])

    def test_what_is_held_out_of_its_form_is_named(self):
        # Given: an offer of one item to hold
        # When: what is held is no object, not a list, an item of other keys or of its checklist
        # alone, or not offered
        # Then: each is named
        item = {"checklist": "checklists/readme.md", "item": "B-1"}
        for given, said in (
            ([], ['give it as JSON: {"held": [...]}']),
            ({"held": "B-1"}, ['give it as JSON: {"held": [...]}']),
            (
                {"held": [dict(item, places=[])]},
                [
                    '{"checklist": "checklists/readme.md", "item": "B-1", "places": []} is not an item offered; hold each by its checklist and ID'
                ],
            ),
            (
                {"held": [dict(item, item="F-1")]},
                [
                    "checklists/readme.md F-1 is not an item offered; hold each by its checklist and ID"
                ],
            ),
            (
                {"held": [{"checklist": "checklists/readme.md"}]},
                [
                    '{"checklist": "checklists/readme.md"} is not an item offered; hold each by its checklist and ID'
                ],
            ),
            ({"held": [item, item]}, ["checklists/readme.md B-1 is given twice; hold each once"]),
        ):
            with self.subTest(given=given):
                self.assertEqual(forms.held(json.dumps(given), STOPS), said)


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
                "README.md:5-6 is not a part of the work",
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


class TestStatements(FormTest):
    def test_each_statement_short_of_its_keys_is_named(self):
        # Given: two statements sent back, each without what the receiver gets
        # When: they are checked
        # Then: each is named with the keys it must hold
        short = {"lines": UNSOURCED["lines"]}
        more = dict(UNSOURCED, why="x")
        said = self.said(
            {
                "items": [GOOD, SENT_BACK],
                "questions": [],
                "statements": [MARKED],
                "unsourced": [short, more],
            },
            forms.READING,
        )
        self.assertEqual(
            said,
            [
                'statement 1 of unsourced must hold {"lines", "gets"} alone',
                'statement 2 of unsourced must hold {"lines", "gets"} alone',
            ],
        )

    def test_statements_sent_back_as_no_list_stop(self):
        # Given: a reading sending back one statement bare, not in a list
        # When: it is checked
        # Then: it is told to give them as a list
        said = self.said(
            {"items": [GOOD, SENT_BACK], "questions": [], "statements": [], "unsourced": UNSOURCED},
            forms.READING,
        )
        self.assertEqual(said, ['"unsourced" is not a list; give it as [{"lines", "gets"}, ...]'])

    def test_a_reading_marking_each_statement_passes(self):
        # Given: a reading marking one statement a decision and one how the product behaves, and
        # one marking none, as the work makes no statement of its subject
        # When: it is checked
        # Then: it passes
        behaves = dict(MARKED, kind="behavior")
        for marked in ([MARKED, behaves], []):
            with self.subTest(marked=marked):
                reading = {"items": [GOOD, SENT_BACK], "questions": [], "statements": marked}
                self.assertEqual(self.said(reading, forms.READING), [])

    def test_marks_out_of_their_form_stop(self):
        # Given: a reading with no marks, marks that are no list, and marks of no kind, beside
        # grounds, or with lines outside the work
        # When: it is checked
        # Then: each is named with the form a mark takes
        shape = 'give "statements": [{"lines": [...], "kind": ...}, ...]'
        held = 'must hold "lines" and "kind", "decision" or "behavior", alone'
        for marked, said in (
            (None, shape),
            (MARKED, shape),
            ([dict(MARKED, kind="fact")], f"statement 1 of statements {held}"),
            ([STATEMENT], f"statement 1 of statements {held}"),
            ([{"kind": "decision"}], f"statement 1 of statements {held}"),
            ([dict(MARKED, lines=["docs/start.md:1"])], "is not lines of the work"),
        ):
            with self.subTest(marked=marked):
                reading: dict = {"items": [GOOD, SENT_BACK], "questions": []}
                if marked is not None:
                    reading["statements"] = marked
                said_now = self.said(reading, forms.READING)
                self.assertEqual(len(said_now), 1, said_now)
                self.assertIn(said, said_now[0])

    def test_every_mark_out_of_its_form_is_named(self):
        # Given: a reading with two marks of no kind
        # When: it is checked
        # Then: each is named
        bad = dict(MARKED, kind="fact")
        reading = {"items": [GOOD, SENT_BACK], "questions": [], "statements": [bad, bad]}
        said = self.said(reading, forms.READING)
        self.assertEqual(
            [s.split(" must")[0] for s in said],
            ["statement 1 of statements", "statement 2 of statements"],
        )


class TestOverlap(FormTest):
    """A statement marked as how the product behaves is shown by a run of the generator's only
    where their lines lie on each other, in the same file."""

    def test_lines_on_each_other_in_one_file_overlap(self):
        # Given: a line inside a range, a range across another's end, and one line named alone
        # When: they are compared
        # Then: each overlaps
        for lines, others in (
            (["README.md:3-3"], ["README.md:2-4"]),
            (["README.md:1-3"], ["README.md:3-5"]),
            (["README.md:4"], ["README.md:4"]),
            (["README.md:3"], ["README.md:1-3"]),
        ):
            with self.subTest(lines=lines, others=others):
                self.assertTrue(forms.overlap(lines, others))
                self.assertTrue(forms.overlap(others, lines))

    def test_lines_apart_or_in_other_files_do_not_overlap(self):
        # Given: ranges apart in one file, and the same lines in two files
        # When: they are compared, each way
        # Then: none overlaps
        for lines, others in (
            (["README.md:1-2"], ["README.md:3-4"]),
            (["README.md:2-4"], ["README.md:5"]),
            (["README.md:3-3"], ["docs/start.md:3-3"]),
        ):
            with self.subTest(lines=lines, others=others):
                self.assertFalse(forms.overlap(lines, others))
                self.assertFalse(forms.overlap(others, lines))


class TestGrounds(FormTest):
    """A statement of the work rests on the words of the CCS or its files, quoted as written, and,
    for one of how the product behaves, on a command the generator ran and what it printed."""

    def setUp(self):
        super().setUp()
        self.write("csvtidy.py", "def tidy(cell):\n    return cell.strip()\n")
        self.sources: tuple[str, ...] = ("notes/readme.decisions.md", "csvtidy.py")
        self.record = self.given_record(
            "generator",
            "{}",
            ("Bash", {"command": "printf ' a \\t' | python3 csvtidy.py"}, "a\n(exit 0)"),
            ("Bash", {"command": "ls"}),
        )

    def claim(self, *statements):
        reply = {"items": [GOOD, WAITS], "questions": [QUESTION], "statements": list(statements)}
        return self.said(reply, forms.CLAIM, self.sources, (self.record,))

    def test_a_statement_quoting_its_source_as_written_passes(self):
        # Given: a statement quoting a line of the decisions, and one quoting code across its
        # line break as one line
        # When: it is checked
        # Then: it passes, as the words are there, whatever space lies between them
        code = {"path": "csvtidy.py", "quote": "def tidy(cell): return cell.strip()"}
        self.assertEqual(self.claim(STATEMENT, dict(STATEMENT, quotes=[code])), [])

    def test_a_quote_not_in_its_file_as_written_stops(self):
        # Given: a quote with a word changed, one with its line numbers, and one of a file the CCS
        # does not name
        # When: it is checked
        # Then: each is named, with what to give instead
        self.write("other.md", "# Decisions\n")
        for quote, said in (
            (
                {"path": "csvtidy.py", "quote": "return cell.lower()"},
                "quote 1 is not in csvtidy.py",
            ),
            ({"path": "csvtidy.py", "quote": "1\tdef tidy(cell):"}, "quote 1 is not in csvtidy.py"),
            ({"path": "other.md", "quote": "# Decisions"}, "other.md is not the CCS or a file"),
            ({"path": "README.md", "quote": "# csvtidy"}, "README.md is not the CCS or a file"),
        ):
            with self.subTest(quote=quote):
                said_now = self.claim(dict(STATEMENT, quotes=[quote]))
                self.assertEqual(len(said_now), 1, said_now)
                self.assertIn(f"statement 1 of statements: {said}", said_now[0])

    def test_quotes_out_of_their_form_stop(self):
        # Given: quotes that are no list, an empty list as the only grounds, or hold other keys or
        # empty words
        # When: they are checked
        # Then: each is named with the form a quote takes, or the grounds a statement holds
        for quotes, said in (
            ("# Decisions", "gives its quotes as no list"),
            ([], 'and "quotes", "ran" or both'),
            ([{"path": "csvtidy.py"}], 'quote 1 must hold "path" and "quote"'),
            ([{"path": "csvtidy.py", "quote": " "}], 'quote 1 must hold "path" and "quote"'),
            ([{"path": 1, "quote": "x"}], 'quote 1 must hold "path" and "quote"'),
            ([dict(STATEMENT["quotes"][0], line="1")], 'quote 1 must hold "path" and "quote"'),
        ):
            with self.subTest(quotes=quotes):
                said_now = self.claim(dict(STATEMENT, quotes=quotes))
                self.assertEqual(len(said_now), 1, said_now)
                self.assertIn(said, said_now[0])

    def test_every_quote_out_of_place_is_named(self):
        # Given: two quotes out of their form, then two of files the CCS does not name, then two
        # not in their file
        # When: they are checked
        # Then: each is named, not only the first
        wrong = {"path": "csvtidy.py", "quote": "return cell.lower()"}
        for quotes, said in (
            ([{"path": "csvtidy.py"}] * 2, "must hold"),
            ([{"path": "README.md", "quote": "x"}] * 2, "is not the CCS"),
            ([wrong, wrong], "is not in csvtidy.py"),
        ):
            with self.subTest(said=said):
                said_now = self.claim(dict(STATEMENT, quotes=quotes))
                self.assertEqual(sum(said in s for s in said_now), 2, said_now)

    def test_a_file_beside_a_folder_named_is_not_inside_it(self):
        # Given: sources naming the folder docs, and a file outside it
        # When: a statement quotes that file
        # Then: the file is named as not a source
        self.write("other.md", "x\n")
        self.sources = ("docs",)
        said = self.claim(dict(STATEMENT, quotes=[{"path": "other.md", "quote": "x"}]))
        self.assertEqual(
            said, ["statement 1 of statements: other.md is not the CCS or a file it names"]
        )

    def test_a_statement_resting_on_a_command_it_ran_passes(self):
        # Given: a statement of how csvtidy behaves, resting on a command the generator ran, with
        # words of what it printed, and another on that run and a quote
        # When: it is checked
        # Then: it passes
        ran = {"command": "printf ' a \\t' | python3 csvtidy.py", "output": "a (exit 0)"}
        lines = {"lines": ["README.md:3-3"], "kind": "behavior", "ran": [ran]}
        self.assertEqual(self.claim(lines, dict(lines, quotes=STATEMENT["quotes"])), [])

    def test_a_run_not_in_the_generators_record_stops(self):
        # Given: a command never run, a command run with words it did not print, and one whose
        # output the record does not hold
        # When: it is checked
        # Then: each is named as no command run with what it printed
        for ran in (
            {"command": "python3 csvtidy.py --help", "output": "usage"},
            {"command": "python3 csvtidy.py --help", "output": "a"},
            {"command": "printf ' a \\t' | python3 csvtidy.py | head", "output": "a"},
            {"command": "printf", "output": "a"},
            {"command": "printf ' a \\t' | python3 csvtidy.py", "output": "b"},
            {"command": "ls", "output": "README.md"},
        ):
            with self.subTest(ran=ran):
                said_now = self.claim(
                    {"lines": ["README.md:3-3"], "kind": "behavior", "ran": [ran]}
                )
                self.assertEqual(len(said_now), 1, said_now)
                self.assertIn("run 1 is not a command you ran with Bash", said_now[0])

    def test_runs_out_of_their_form_stop(self):
        # Given: runs that are no list, an empty list as the only grounds, or hold other keys
        # When: they are checked
        # Then: each is named with the form a run takes, or the grounds a statement holds
        for ran, said in (
            ({"command": "ls"}, "gives its runs as no list"),
            ([], 'and "quotes", "ran" or both'),
            ([{"command": "ls"}], 'run 1 must hold "command" and "output"'),
            ([{"command": "ls", "output": " "}], 'run 1 must hold "command" and "output"'),
            ([{"command": "ls", "output": "a", "why": "x"}], 'run 1 must hold "command"'),
            (["ls"], 'run 1 must hold "command" and "output"'),
        ):
            with self.subTest(ran=ran):
                said_now = self.claim({"lines": ["README.md:3-3"], "kind": "behavior", "ran": ran})
                self.assertEqual(len(said_now), 1, said_now)
                self.assertIn(said, said_now[0])

    def test_a_run_is_found_in_a_record_whose_results_come_as_parts(self):
        # Given: a record whose tool result is given as a list of text parts, beside entries that
        # are not the generator's own messages
        # When: a statement rests on that run
        # Then: it passes
        parts = [{"type": "text", "text": "a"}, {"type": "text", "text": "(exit 0)"}]
        self.record = self.given_record("parts", "{}", ("Bash", {"command": "ls"}, parts))
        with open(self.record, "a", encoding="utf-8") as f:
            f.write(json.dumps({"type": "progress", "data": {}}) + "\n")
            f.write(json.dumps({"type": "user", "message": {"content": "go on"}}) + "\n")
        ran = {"command": "ls", "output": "a (exit 0)"}
        self.assertEqual(
            self.claim({"lines": ["README.md:3-3"], "kind": "behavior", "ran": [ran]}), []
        )

    def test_a_run_is_found_among_bash_s_own_uses_and_results_alone(self):
        # Given: a record holding, beside a Bash use and its result, parts of other types and tools
        # holding a command, and parts of other types answering the Bash use
        # When: a statement rests on a command of those parts, or on words of those answers
        # Then: it stops, as only a Bash use and the tool result answering it show a run
        def part(kind, **fields):
            return {"type": kind, **fields}

        def use(kind, name, n):
            return part(kind, name=name, id=f"x{n}", input={"command": f"cmd{n}"})

        def back(kind, n, words):
            return part(kind, tool_use_id=f"x{n}", content=words)

        parts = [
            use("server_tool_use", "Bash", 1),
            use("web_fetch", "Bash", 2),
            use("tool_use", "Agent", 3),
            use("tool_use", "Monitor", 4),
            use("tool_use", "Bash", 5),
            back("tool_result", 1, "one"),
            back("tool_result", 2, "two"),
            back("tool_result", 3, "three"),
            back("tool_result", 4, "four"),
            back("text", 5, "five"),
            back("web_fetch_result", 5, "six"),
            back("tool_result", 5, "done"),
        ]
        self.record = os.path.join(self.repo, "parts.jsonl")
        with open(self.record, "w", encoding="utf-8") as f:
            f.write(json.dumps({"type": "assistant", "message": {"content": parts}}) + "\n")
        for command, output in (
            ("cmd1", "one"),
            ("cmd2", "two"),
            ("cmd3", "three"),
            ("cmd4", "four"),
            ("cmd5", "five"),
            ("cmd5", "six"),
        ):
            with self.subTest(command=command, output=output):
                ran = {"command": command, "output": output}
                said_now = self.claim(
                    {"lines": ["README.md:3-3"], "kind": "behavior", "ran": [ran]}
                )
                self.assertEqual(len(said_now), 1, said_now)
        ran = {"command": "cmd5", "output": "done"}
        self.assertEqual(
            self.claim({"lines": ["README.md:3-3"], "kind": "behavior", "ran": [ran]}), []
        )

    def test_a_statement_with_no_grounds_or_other_keys_stops(self):
        # Given: a statement with lines and its mark alone, one with an old key beside its quotes,
        # one with no lines, one with no mark or a mark of no kind, and one that is no object
        # When: it is checked
        # Then: each is named with the keys a statement holds
        shape = ' must hold "lines", "kind", "decision" or "behavior", and "quotes", "ran" or both'
        for statement in (
            {"lines": ["README.md:3-3"], "kind": "decision"},
            dict(STATEMENT, **{"from": ["csvtidy.py:1-1"]}),
            {"kind": "decision", "quotes": STATEMENT["quotes"]},
            {"lines": ["README.md:3-3"], "quotes": STATEMENT["quotes"]},
            dict(STATEMENT, kind="fact"),
            "README.md:3-3",
        ):
            with self.subTest(statement=statement):
                self.assertEqual(
                    self.claim(statement, statement),
                    [f"statement 1 of statements{shape}", f"statement 2 of statements{shape}"],
                )

    def test_an_empty_list_beside_the_grounds_its_mark_asks_passes(self):
        # Given: a decision with its quotes and "ran" as an empty list, and a behavior with its run
        # and "quotes" as an empty list, as the generator's form shows both
        # When: they are checked
        # Then: both pass, an empty list giving no grounds and asking for none
        ran = {"command": "printf ' a \\t' | python3 csvtidy.py", "output": "a"}
        self.assertEqual(
            self.claim(
                dict(STATEMENT, ran=[]),
                {"lines": ["README.md:3-3"], "kind": "behavior", "quotes": [], "ran": [ran]},
            ),
            [],
        )

    def test_a_statement_is_grounded_as_its_mark_asks(self):
        # Given: a statement of how the product behaves resting on quotes alone, and a decision
        # resting on a run alone
        # When: it is checked
        # Then: the first is told to give a run or be taken out, and the second to give quotes
        ran = {"command": "printf ' a \\t' | python3 csvtidy.py", "output": "a"}
        said = self.claim(
            dict(STATEMENT, kind="behavior"),
            {"lines": ["README.md:3-3"], "kind": "decision", "ran": [ran]},
        )
        behaves = (
            'statement 1 of statements tells how the product behaves; give "ran", a command you'
            " ran that shows it, or take it out of the work"
        )
        decided = (
            'statement 2 of statements is a decision; give "quotes", the words of the CCS or its'
            " files that say it, or take it out of the work"
        )
        self.assertEqual(said, [behaves, decided])

    def test_statements_given_as_no_list_stop(self):
        # Given: a claim with no statements, and one with statements that are no list
        # When: it is checked
        # Then: it is told to give each statement with its grounds
        reply = {"items": [GOOD, WAITS], "questions": [QUESTION]}
        for statements in ((), (STATEMENT,)):
            with self.subTest(statements=statements):
                given = dict(reply, statements=statements[0]) if statements else reply
                said = self.said(given, forms.CLAIM, self.sources, (self.record,))
                self.assertEqual(len(said), 1, said)
                self.assertIn('give "statements": [{"lines": [...], "kind": ..., "quotes"', said[0])


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
