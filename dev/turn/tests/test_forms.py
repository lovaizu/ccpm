"""Each form a judgment is given in, checked against the run's items and the work, and the parts
of the work an item asked of each part is judged in."""

import json
import os
import unittest

from helpers import (
    CHOSEN,
    EACH_GOOD,
    EACH_ITEM,
    FOUND,
    ITEM_B1,
    ITEM_F1,
    ITEMS,
    MADE,
    MADE_B1,
    NEED,
    NEEDED_B1,
    SECTIONED,
    TURN,
    RepoTest,
    forms,
    testing,
    work_parts,
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

    def write_bytes(self, path, data):
        """Writes the bytes at the path, as a file that is not text, its folder already made."""
        with open(path, "wb") as f:
            f.write(data)


class TestItems(FormTest):
    def test_a_reply_that_is_not_an_object_of_its_lists_is_told_its_shape(self):
        # Given: a reply that is not JSON, JSON that is not an object, and an object missing one
        # of the lists its form takes
        # When: each is checked by the claim's form, and by the reading's
        # Then: each is told the shape to give, the lists its form takes
        for text in ("good", "[]", '{"items": []}'):
            with self.subTest(text=text):
                said = forms.check(text, ITEMS, WORK, forms.CLAIM, [])
                self.assertEqual(said, ['give it as JSON: {"items": [...], "chosen": [...]}'])
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
                    dict(MADE, item="B-8"),
                    dict(MADE, item="B-9"),
                    MADE,
                    MADE,
                    bare,
                    bare,
                ],
                "chosen": [],
            },
            forms.CLAIM,
        )
        self.assertIn("checklists/readme.md B-8 is not an item judged here", "\n".join(said))
        self.assertIn("checklists/readme.md B-9 is not an item judged here", "\n".join(said))
        self.assertIn("checklists/readme.md F-1 is given twice", "\n".join(said))
        self.assertEqual(sum("B-1 must hold" in s for s in said), 1)
        self.assertEqual(sum("B-1 is given twice" in s for s in said), 1)

    def test_an_item_named_by_its_checklist_s_whole_path_is_the_item_the_ccs_names(self):
        # Given: a reading naming every item by the whole path of its checklist, as each role is
        # given the checklists, one of them asked of each part of the work
        # When: it is checked against the items as the CCS names them
        # Then: it is filled
        whole = os.path.abspath("checklists/readme.md")
        items = [dict(FOUND, checklist=whole), dict(EACH_GOOD, checklist=whole)]
        said = self.each_said({"items": items}, forms.FIRST_READING, (ITEMS[0], EACH_ITEM))
        self.assertEqual(said, [])

    def test_an_item_naming_no_checklist_is_told_to_name_it(self):
        # Given: a claim with an item that names no checklist, and one whose checklist is no path
        # When: it is checked
        # Then: each is shown as it was given and told to name its checklist
        bare = {"item": "F-1", "lines": ["README.md:1-3"]}
        claim = {"items": [bare, dict(bare, checklist=1)], "chosen": []}
        said = self.said(claim, forms.CLAIM)
        for item in (bare, dict(bare, checklist=1)):
            with self.subTest(item=item):
                self.assertIn(f"{json.dumps(item)} is not an item judged here", "\n".join(said))

    def test_an_item_of_no_shape_is_told_the_shapes_it_takes(self):
        # Given: an item holding none of the shapes its form takes
        # When: it is checked by a form of one shape, and by a form of two
        # Then: it is told the one shape, or the two
        bare = ITEM_F1
        said = self.said({"items": [bare, MADE_B1], "chosen": []}, forms.CLAIM)
        self.assertEqual(said, ['checklists/readme.md F-1 must hold "lines"'])
        said = self.said({"items": [bare, NEEDED_B1]}, forms.FIRST_READING)
        self.assertEqual(said, ['checklists/readme.md F-1 must hold one of "lines" or "need"'])

    def test_an_item_of_two_shapes_is_told_the_shapes_it_takes(self):
        # Given: a reading whose F-1 holds its lines and what the receiver would need as well
        both = dict(FOUND, need=NEED)
        # When: it is checked
        # Then: F-1 is told the shapes it takes, one of them
        said = self.said({"items": [both, NEEDED_B1]}, forms.FIRST_READING)
        self.assertEqual(said, ['checklists/readme.md F-1 must hold one of "lines" or "need"'])


class TestFirstReading(FormTest):
    def test_a_first_user_gives_every_item_its_lines_or_what_the_receiver_would_need(self):
        # Given: a first user's reading giving one item its lines and the other what the receiver
        # would need; one leaving an item out; and one giving an item asked of each part what the
        # receiver would need
        # When: it is checked
        # Then: the first and the third pass, and the second is told the item left out
        self.assertEqual(self.said({"items": [FOUND, NEEDED_B1]}, forms.FIRST_READING), [])
        said = self.said({"items": [FOUND]}, forms.FIRST_READING)
        self.assertEqual(
            said, ["checklists/readme.md B-1 is left out; give every item judged here"]
        )
        each = dict(NEEDED_B1, item="B-2")
        said = self.each_said(
            {"items": [FOUND, NEEDED_B1, each]}, forms.FIRST_READING, ITEMS + [EACH_ITEM]
        )
        self.assertEqual(said, [])

    def test_what_the_receiver_would_need_is_said_in_words(self):
        # Given: a reading whose need is blanks alone, and one whose need is no text
        # When: each is checked
        # Then: each is told to say it in words
        for need in (" ", 1):
            with self.subTest(need=need):
                said = self.said(
                    {"items": [FOUND, dict(NEEDED_B1, need=need)]}, forms.FIRST_READING
                )
                self.assertEqual(
                    said, ['checklists/readme.md B-1 has an empty "need"; say it in words']
                )


class TestClaim(FormTest):
    def test_a_claim_of_every_item_at_its_lines_passes(self):
        # Given: the generator's claim, every item at the lines that give its Good, naming a
        # choice it made
        # When: it is checked
        # Then: it passes
        claim = {"items": [MADE, MADE_B1], "chosen": [CHOSEN]}
        self.assertEqual(self.said(claim, forms.CLAIM), [])

    def test_an_item_claimed_gives_its_lines_alone(self):
        # Given: claims whose item gives its lines with words beside them, an answer of the
        # first user's form, or no lines
        # When: each is checked
        # Then: the first two are told the shape a claimed item takes, the third to give lines
        claim = {"chosen": []}
        for item in (dict(MADE, evidence="cat -n README.md"), dict(ITEM_F1, need=NEED)):
            with self.subTest(item=item):
                said = self.said(dict(claim, items=[item, MADE_B1]), forms.CLAIM)
                self.assertEqual(said, ['checklists/readme.md F-1 must hold "lines"'])
        said = self.said(dict(claim, items=[dict(MADE, lines=[]), MADE_B1]), forms.CLAIM)
        self.assertEqual(len(said), 1, said)
        self.assertIn("F-1 names no lines", said[0])

    def test_a_claim_leaving_an_item_out_is_told_it(self):
        # Given: a claim that leaves an item out
        # When: it is checked
        # Then: it is told the item left out
        said = self.said({"items": [MADE], "chosen": []}, forms.CLAIM)
        self.assertEqual(
            said, ["checklists/readme.md B-1 is left out; give every item judged here"]
        )

    def test_a_claim_names_each_choice_it_made_with_why_in_words(self):
        # Given: claims whose choices are not a list, or hold one that is no object, without its
        # why, with empty words, or with a key of its own
        # When: each is checked
        # Then: the first is told the shape to give, and each other the choice with what to give
        claim = {"items": [MADE, MADE_B1]}
        said = self.said(dict(claim, chosen={}), forms.CLAIM)
        self.assertEqual(said, ['give it as JSON: {"items": [...], "chosen": [...]}'])
        for choice in (
            "people.csv",
            {"chosen": "people.csv"},
            dict(CHOSEN, why=" "),
            dict(CHOSEN, chosen=1),
            dict(CHOSEN, seen="x"),
        ):
            with self.subTest(choice=choice):
                said = self.said(dict(claim, chosen=[CHOSEN, choice]), forms.CLAIM)
                self.assertEqual(
                    said,
                    ['choice 2 must hold "chosen" and "why", what was chosen and why, in words'],
                )


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
            work_parts.parts(["README.md"]), ["README.md:1-3", "README.md:4-10", "README.md:11-12"]
        )

    def test_a_heading_in_a_fence_of_tildes_or_an_indented_one_opens_no_part(self):
        for fence in ("~~~", "  ```"):
            with self.subTest(fence=fence):
                # Given: a README whose top heading in a fence of tildes, or an indented one, stands
                # between its opening and its one section
                self.write("README.md", f"# x\n\n{fence}\n## not one\n{fence}\n## B\nb\n")
                # When: it is split
                # Then: the fence lies in the opening's part
                self.assertEqual(
                    work_parts.parts(["README.md"]), ["README.md:1-5", "README.md:6-7"]
                )

    def test_a_heading_of_another_level_or_in_the_frontmatter_opens_no_part(self):
        # Given: a README with a heading of the level above a top one and one below it after its
        # opening, and frontmatter holding a line written as a top heading
        self.write("README.md", "---\nname: x\n## not one\n---\n# x\n\n# y\n### z\n## B\nb\n")
        # When: it is split
        # Then: its one top heading alone opens a part
        self.assertEqual(work_parts.parts(["README.md"]), ["README.md:1-8", "README.md:9-10"])

    def test_a_document_opening_with_a_section_has_no_opening_part(self):
        # Given: a document whose first line is a top heading, and one with none
        # When: each is split
        # Then: the first is its sections alone, and the second is one part
        self.write("a.md", "## A\na\n## B\n")
        self.write("b.md", "# b\n\nonly\n")
        self.assertEqual(work_parts.parts(["a.md", "b.md"]), ["a.md:1-2", "a.md:3-3", "b.md:1-3"])

    def test_any_other_file_is_one_part_and_an_empty_file_none(self):
        # Given: a script of three lines holding a line that opens like a heading, and an empty
        # file
        # When: they are split
        # Then: the script is one part, and the empty file gives none
        self.write("x.py", "a = 1\n## b\nc = 2\n")
        self.write("e.md", "")
        self.assertEqual(work_parts.parts(["x.py", "e.md"]), ["x.py:1-3"])

    def test_a_file_of_the_work_not_written_yet_has_no_part(self):
        # Given: a work of two files, one not written yet
        # When: it is split
        # Then: the file written gives its part alone
        self.assertEqual(work_parts.parts(["new.md", "README.md"]), ["README.md:1-3"])

    def test_a_folder_of_the_work_is_split_as_each_file_in_it_is(self):
        # Given: a work of a folder holding a document of two parts, a script in a folder below
        # it and a file that is not text, and of a folder not made yet
        self.write("guide/b.md", "# b\n\nopening\n## B\nb\n")
        self.write("guide/a/x.py", "x = 1\n")
        self.write_bytes("guide/c.png", b"\x89PNG\xff\xfe\n")
        # When: it is split
        # Then: each text file in the folder, at any depth, is split as a file of the work is, in
        # the order of their paths, and the file that is not text and the folder not made give
        # none
        self.assertEqual(
            work_parts.parts(["guide", "new"]),
            ["guide/a/x.py:1-1", "guide/b.md:1-3", "guide/b.md:4-5"],
        )

    def test_the_files_of_the_work_are_each_file_it_names_and_each_in_a_folder_it_names(self):
        # Given: a work of a file, a file not written yet, and a folder holding two files, one in
        # a folder below it
        self.write("guide/b.md", "b\n")
        self.write("guide/a/x.py", "x\n")
        # When: its files are asked for
        # Then: each file named is itself, and the folder is each file in it, by the path from
        # the folder as the work names it, in the order of their paths
        self.assertEqual(
            work_parts.files(["README.md", "new.md", "guide"]),
            ["README.md", "new.md", "guide/a/x.py", "guide/b.md"],
        )

    def test_an_item_asked_of_each_part_with_lines_in_every_part_passes(self):
        # Given: an item asked of each part, given lines in each part of the work
        # When: it is checked by the forms that give lines
        # Then: it passes
        for form, items in (
            (forms.FIRST_READING, [FOUND, NEEDED_B1]),
            (forms.CLAIM, [MADE, MADE_B1]),
        ):
            with self.subTest(form=form):
                data = {"items": [*items, EACH_GOOD], "chosen": []}
                self.assertEqual(self.each_said(data, form, ITEMS + [EACH_ITEM]), [])

    def test_an_item_not_asked_of_each_part_takes_lines_in_one_part(self):
        # Given: an item of its part given lines in the first part of a work of two
        # When: it is checked
        # Then: it passes, as only an item asked of each part is held to every part
        said = self.each_said(
            {"items": [dict(FOUND, lines=["README.md:3"])]}, forms.FIRST_READING, [ITEMS[0]]
        )
        self.assertEqual(said, [])

    def test_lines_of_an_item_asked_of_each_part_out_of_their_parts_stop(self):
        # Given: an item asked of each part whose lines leave a part without any, run across two
        # parts, name lines not of the work, or are no list
        # When: each is checked
        # Then: each is named with what to give
        for lines, said in (
            (
                ["README.md:3"],
                (
                    "README.md:5-7 holds none of its lines; give lines in every part, as the item"
                    " has its Good only where every part holds it"
                ),
            ),
            (
                ["README.md:3", "README.md:4-5"],
                (
                    "README.md:4-5 is not inside one part of the work; give each range inside one"
                    " of `README.md:1-4`, `README.md:5-7`"
                ),
            ),
            (["README.md:3", "x.md:6"], "x.md:6 is not lines of the work"),
            ("README.md:3", "names no lines"),
        ):
            with self.subTest(lines=lines):
                said_now = self.each_said(
                    {"items": [dict(EACH_GOOD, lines=lines)]}, forms.FIRST_READING
                )
                self.assertEqual(len(said_now), 1, said_now)
                self.assertIn(said, said_now[0])
                self.assertTrue(said_now[0].startswith("checklists/readme.md B-2"), said_now)

    def test_lines_are_inside_their_part_in_its_own_file_alone(self):
        # Given: a work of three files, a script whose name sorts before a document of two parts
        # and one whose name sorts after it, and an item asked of each part whose lines name
        # each part's first line
        # When: the document's second part is given by its own lines, or by lines of the same
        # numbers in either script
        # Then: the first passes, and each other is named
        self.write("README.md", SECTIONED)
        self.write("0.py", "x\n" * 7)
        self.write("z.py", "x\n" * 7)
        work = ["README.md", "0.py", "z.py"]
        for lines, said in (("README.md:5-7", 0), ("0.py:5-7", 1), ("z.py:5-7", 1)):
            with self.subTest(lines=lines):
                item = dict(EACH_GOOD, lines=["README.md:3", lines, "0.py:1", "z.py:1"])
                text = json.dumps({"items": [item]})
                found = forms.check(text, [EACH_ITEM], work, forms.FIRST_READING, [EACH_ITEM])
                self.assertEqual(len(found), said, found)

    def test_lines_named_by_a_whole_path_are_inside_their_part(self):
        # Given: an item asked of each part whose lines are named by whole paths, as a role given
        # whole paths names them
        # When: it is checked
        # Then: it passes, as each line is inside its part however the path is written
        lines = [self.here(line) for line in EACH_GOOD["lines"]]
        said = self.each_said({"items": [dict(EACH_GOOD, lines=lines)]}, forms.FIRST_READING)
        self.assertEqual(said, [])

    def test_every_part_holding_none_of_the_lines_is_named(self):
        # Given: a work of three parts, and an item asked of each part whose lines lie in the first
        # alone
        self.write("README.md", "# x\n\na\n## A\nb\n## B\nc\n")
        # When: it is checked
        # Then: both other parts are named
        text = json.dumps({"items": [dict(EACH_GOOD, lines=["README.md:3"])]})
        said = forms.check(text, [EACH_ITEM], WORK, forms.FIRST_READING, [EACH_ITEM])
        self.assertEqual(
            [s.split(": ")[1].split(" ")[0] for s in said], ["README.md:4-5", "README.md:6-7"]
        )

    def test_every_range_out_of_its_part_is_named(self):
        # Given: an item asked of each part whose two ranges both run across the parts
        # When: it is checked
        # Then: both are named
        lines = ["README.md:1-7", "README.md:4-5"]
        said = self.each_said({"items": [dict(EACH_GOOD, lines=lines)]}, forms.FIRST_READING)
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
                    {"items": [dict(FOUND, lines=[lines]), NEEDED_B1]}, forms.FIRST_READING
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
                    {"items": [dict(FOUND, lines=[lines]), NEEDED_B1]}, forms.FIRST_READING
                )
                self.assertEqual(len(said), 1, said)
                self.assertIn(f"{lines} is not lines of the work", said[0])
                self.assertIn("<path>:<from>-<to>", said[0])

    def test_lines_of_a_file_in_a_folder_of_the_work_pass(self):
        # Given: a work of a folder, holding a file and a file in a folder below it
        self.write("guide/a.md", "a\n")
        self.write("guide/sub/b.md", "b\nc\n")
        # When: a Good names lines of each, by the path from the folder or by the whole path
        # Then: each passes
        for lines in ("guide/a.md:1", "guide/sub/b.md:1-2", self.here("guide/sub/b.md:2")):
            with self.subTest(lines=lines):
                text = json.dumps({"items": [dict(FOUND, lines=[lines])]})
                said = forms.check(text, [ITEM_F1], ["guide"], forms.FIRST_READING, [])
                self.assertEqual(said, [])

    def test_lines_out_of_the_files_of_a_folder_of_the_work_stop(self):
        # Given: a work of a folder holding a file and a file that is not text, a folder beside it
        # whose name begins with the folder's, and a file of that name
        self.write("guide/a.md", "a\n")
        self.write_bytes("guide/c.png", b"\x89PNG\xff\xfe\n")
        self.write("guide2/a.md", "a\n")
        self.write("guide.md", "a\n")
        # When: a Good names lines past the file's end, lines of the file not text, of the folder
        # itself, or of a file beside the folder
        # Then: each is named as not lines of the work
        for lines in ("guide/a.md:2", "guide/c.png:1", "guide:1", "guide2/a.md:1", "guide.md:1"):
            with self.subTest(lines=lines):
                text = json.dumps({"items": [dict(FOUND, lines=[lines])]})
                said = forms.check(text, [ITEM_F1], ["guide"], forms.FIRST_READING, [])
                self.assertEqual(len(said), 1, said)
                self.assertIn(f"{lines} is not lines of the work", said[0])


class TestSchemas(FormTest):
    """Each role's reply is held, as it is written, to its JSON Schema by lane's in_form, and then
    by turn's check of it; a reply the check takes is one the schema takes."""

    def out_of(self, name, value):
        """Where the value is out of the role's schema of the name, None where it holds."""
        with open(os.path.join(FORM_FILES, name), encoding="utf-8") as f:
            form = json.load(f)
        schema.checked(form)
        return schema.held(form, value)

    def test_there_is_a_form_for_each_role_that_replies(self):
        # Given: turn's forms
        # When: they are listed
        # Then: there is one for the generator and the first user, and none else
        self.assertEqual(sorted(os.listdir(FORM_FILES)), ["claim.json", "reading.json"])

    def test_each_reply_turn_takes_is_one_its_schema_takes(self):
        # Given: a claim and a reading, each taken by turn's check of it
        # When: each is held to its role's schema
        # Then: each holds
        for name, value in (
            ("claim.json", {"items": [MADE, MADE_B1, EACH_GOOD], "chosen": [CHOSEN]}),
            ("reading.json", {"items": [FOUND, NEEDED_B1, EACH_GOOD]}),
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
        for item in (dict(FOUND, need=NEED), dict(FOUND, x=1)):
            with self.subTest(item=item):
                # Given: a reading whose item holds its lines and a need, or a key no shape has
                # When: it is held to the first user's schema
                # Then: it is out at the item
                out = self.out_of("reading.json", {"items": [item]})
                self.assertEqual(out.told()[: len("$.items[0]")], "$.items[0]")


if __name__ == "__main__":
    unittest.main()
