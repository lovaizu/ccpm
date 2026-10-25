"""A Markdown template: the keys its frontmatter names and the headings it holds, in order and
level, checked in a written file, text in `<...>` and body text free; frontmatter read as `key:
value` lines alone, anything else refused rather than guessed."""

import unittest

from helpers import template

# A template of both kinds: frontmatter keys, one value free and one plain, and headings.
FORM = """---
name: <name>
status: draft
---

# <title>

Free text the writer replaces.

## What it should be

## Why
"""
# A file written in that form, with text and a heading of its own between.
WRITTEN = """---
name: notes
status: 'draft'
extra: kept
---

# Notes

Body.

## What it should be

### A heading of its own

## Why

More.
"""


def held(text, form=FORM):
    """The point the text is out of the template by; "" where it holds."""
    return template.held(template.read(form), text)


class TestRead(unittest.TestCase):
    def test_the_keys_and_headings_of_a_template_are_read(self):
        # Given: the template above
        # When: it is read
        read = template.read(FORM)
        # Then: its keys with their values as written, and its headings with their levels, in order
        self.assertEqual(read.keys, [("name", "<name>"), ("status", "draft")])
        self.assertEqual(read.headings, [(1, "<title>"), (2, "What it should be"), (2, "Why")])

    def test_a_template_of_headings_alone_or_keys_alone_is_read(self):
        for form in ("## A\n", "---\na: b\n---\n"):
            with self.subTest(form=form):
                # Given: a template of one kind alone
                # When: it is read
                # Then: it is read, as either alone checks something
                self.assertIsInstance(template.read(form), template.Template)

    def test_a_template_checking_nothing_is_refused(self):
        for form in ("", "Text alone.\n", "---\n---\nText.\n", "```\n# in code\n```\n"):
            with self.subTest(form=form):
                # Given: a template with no heading and no frontmatter key
                # When: it is read
                # Then: it is refused, as it would check nothing
                with self.assertRaises(ValueError) as refused:
                    template.read(form)
                self.assertIn("no heading and no frontmatter key", str(refused.exception))

    def test_a_template_whose_frontmatter_cannot_be_read_is_refused(self):
        # Given: a template whose frontmatter nests a mapping
        # When: it is read
        # Then: it is refused, naming the line
        with self.assertRaises(ValueError) as refused:
            template.read("---\na:\n  b: c\n---\n# T\n")
        self.assertIn("line 3:", str(refused.exception))


class TestFrontmatter(unittest.TestCase):
    def test_key_value_lines_are_read_as_text(self):
        for line, value in (
            ("a: b", "b"),
            ("a: b c ", "b c"),
            ("a:", ""),
            ("a: 'b''s'", "b's"),
            ('a: "b"', "b"),
            ("a: b # a comment", "b"),
            ("a: b\t# a comment", "b"),
            ("a: [b, c]", "[b, c]"),
            ("a.b-c_1: d", "d"),
            ("a: b#c", "b#c"),
            ("a: ''", ""),
            ("a: \"b''c\"", "b''c"),
        ):
            with self.subTest(line=line):
                # Given: frontmatter of one key: value line
                # When: it is read
                # Then: the value is its text, quotes and a comment taken off
                self.assertEqual(
                    template.keys(["---", line, "---"]),
                    {"a" if line[1] == ":" else "a.b-c_1": (2, value)},
                )

    def test_blank_and_comment_lines_are_left_out(self):
        # Given: frontmatter with a blank line and a comment between its keys
        # When: it is read
        # Then: the keys alone are read, each with its line
        self.assertEqual(
            template.keys(["---", "a: b", "", "  # c", "d: e", "---"]),
            {"a": (2, "b"), "d": (5, "e")},
        )

    def test_what_the_reader_cannot_read_is_refused_naming_the_line(self):
        for lines, named in (
            (["a: |", "  b"], 'line 2: expected a "key: value" line lane reads, found "a: |"'),
            (["a: >-", "  b"], "line 2:"),
            (["a:", "  b: c"], 'found "  b: c"'),
            (["a:", "- b"], 'found "- b"'),
            (["a: b", "  c"], 'found "  c"'),
            (["a: 'b"], "line 2:"),
            (['a: "b'], "line 2:"),
            (["a: 'b'c'"], "line 2:"),
            (['a: "b"c"'], "line 2:"),
            (['a: "b\\n"'], "line 2:"),
            (["a: 'b' # c"], "line 2:"),
            (["a: &x b"], "line 2:"),
            (["a: *x"], "line 2:"),
            (["a: !t b"], "line 2:"),
            (["a: b: c"], "line 2:"),
            (["a:b"], "line 2:"),
            (["'a': b"], "line 2:"),
            (["a: '"], "line 2:"),
            (["a: b", "a: c"], 'line 3: expected each key once, found "a" again'),
        ):
            with self.subTest(lines=lines):
                # Given: frontmatter holding a block scalar, a nested mapping, a list, a value over
                # several lines, an unclosed or escaped quote, an anchor, an alias, a tag, a key
                # not plain, or a key twice
                # When: it is read
                # Then: it is refused, naming the line, rather than guessed
                with self.assertRaises(ValueError) as refused:
                    template.keys(["---", *lines, "---"])
                self.assertIn(named, str(refused.exception))

    def test_frontmatter_never_closed_is_refused(self):
        # Given: a file opening frontmatter it never closes
        # When: it is read
        # Then: it is refused, naming the line it opens on
        with self.assertRaises(ValueError) as refused:
            template.keys(["---", "a: b"])
        self.assertEqual(
            str(refused.exception), 'line 1: expected frontmatter closed by "---", found none'
        )

    def test_a_file_without_frontmatter_has_no_keys(self):
        for lines in ([], ["# T"], ["--- "], ["title: x"]):
            with self.subTest(lines=lines):
                # Given: a file not opening with `---`
                # When: its frontmatter is read
                # Then: there is none
                self.assertIsNone(template.keys(lines))


class TestHeadings(unittest.TestCase):
    def test_atx_headings_are_read_with_their_level_and_line(self):
        lines = ["# One", "text", "   ## Two ##", "###### Six", "####### Seven", "#NoSpace", "##"]
        # Given: headings of each level, one with closing marks, and lines that are no headings
        # When: the headings are read
        # Then: each heading's line, level and text, closing marks taken off
        self.assertEqual(
            template.headings(lines, 0),
            [(1, 1, "One"), (3, 2, "Two"), (4, 6, "Six"), (7, 2, "")],
        )

    def test_a_heading_text_keeps_a_mark_inside_a_word(self):
        # Given: a heading whose text ends in a word holding #
        # When: it is read
        # Then: the mark is kept
        self.assertEqual(template.headings(["## C#"], 0), [(1, 2, "C#")])

    def test_headings_in_code_fences_are_no_headings(self):
        lines = [
            "# Out",
            "```sh",
            "# in",
            "~~~",
            "````",
            "# Out again",
            "~~~~",
            "# in",
            "~~~",
            "# still in",
            "~~~~~",
            "# After",
            "```",
            "# never closed",
        ]
        # Given: headings inside fences of backticks and tildes, a fence closed only by its own
        # mark at its length or longer, and one never closed
        # When: the headings are read
        # Then: those outside the fences alone are headings
        self.assertEqual([h[2] for h in template.headings(lines, 0)], ["Out", "Out again", "After"])

    def test_headings_are_read_from_the_line_given(self):
        # Given: lines before the body
        # When: the headings are read from the second line
        # Then: those before it are left out, each line still counted from the file's first
        self.assertEqual(template.headings(["# A", "# B"], 1), [(2, 1, "B")])


class TestHeld(unittest.TestCase):
    def test_a_file_in_the_form_holds(self):
        # Given: the template, and a file with its keys and headings, and more of its own
        # When: the file is held to the template
        # Then: it holds
        self.assertEqual(held(WRITTEN), "")

    def test_a_free_part_holds_any_text_but_none(self):
        for text, holds in (("Any text", True), ("", False)):
            with self.subTest(text=text):
                # Given: a template whose heading is all free
                # When: a heading of the text is written
                # Then: any text holds it, and none does not
                self.assertEqual(held(f"## {text}\n", "## <title>\n") == "", holds)

    def test_a_heading_with_a_free_part_holds_the_rest_as_written(self):
        for text, holds in (("Step 3: write", True), ("Step 3 write", False), ("Step : x", False)):
            with self.subTest(text=text):
                # Given: a heading with a free part between plain text
                # When: a heading is written
                # Then: it holds where the plain text is as written and the free parts hold text
                self.assertEqual(held(f"## {text}\n", "## Step <n>: <name>\n") == "", holds)

    def test_plain_text_in_a_template_is_taken_as_written(self):
        # Given: a heading of characters a pattern would read otherwise
        # When: a heading only a pattern would hold is written
        # Then: it does not hold
        self.assertNotEqual(held("## Ab\n", "## A.\n"), "")

    def test_a_file_out_of_the_form_gives_its_line_what_was_expected_and_found(self):
        for written, told in (
            ("# Notes\nBody.\n", 'line 1: expected frontmatter opened by "---", found "# Notes"'),
            ("name: n\n", 'line 1: expected frontmatter opened by "---", found "name: n"'),
            ("", 'line 1: expected frontmatter opened by "---", found an empty file'),
            ("---\nname: n\n", 'line 1: expected frontmatter closed by "---", found none'),
            ("---\nname: n\n---\n", 'line 1: expected the frontmatter key "status", found none'),
            ("---\nname:\nstatus: draft\n---\n", 'line 2: expected "name: <name>", found "name: "'),
            (
                "---\nname: n\nstatus: done\n---\n",
                'line 3: expected "status: draft", found "status: done"',
            ),
            (
                "---\nname: n\n  x: y\n---\n",
                'line 3: expected a "key: value" line lane reads, found "  x: y"',
            ),
            (
                "---\nname: n\nstatus: draft\n---\n# T\n## Why\n",
                'from line 6: expected the heading "## What it should be", found none',
            ),
            (
                "---\nname: n\nstatus: draft\n---\n# T\n### What it should be\n## Why\n",
                (
                    'from line 6: expected the heading "## What it should be",'
                    ' found "### What it should be" at line 6'
                ),
            ),
            (
                "---\nname: n\nstatus: draft\n---\n# T\n# What it should be\n## Why\n",
                (
                    'from line 6: expected the heading "## What it should be",'
                    ' found "# What it should be" at line 6'
                ),
            ),
            (
                "---\nname: n\nstatus: draft\n---\n# T\n## Why\n## What it should be\n",
                'from line 8: expected the heading "## Why", found none',
            ),
            (
                "---\nname: n\nstatus: draft\n---\n## T\n",
                'from line 5: expected the heading "# <title>", found "## T" at line 5',
            ),
        ):
            with self.subTest(written=written):
                # Given: the template
                # When: a file out of it is held to it
                # Then: the one point it is out by is given, at its line
                self.assertEqual(held(written), told)

    def test_each_heading_of_the_template_takes_a_heading_of_its_own(self):
        for written, told in (
            ("## X\n## A\n", 'from line 3: expected the heading "## A", found none'),
            ("## A\n## A\n", ""),
        ):
            with self.subTest(written=written):
                # Given: a template of one heading twice
                # When: a file with it once, or twice, is held to it
                # Then: once is out after it, twice holds
                self.assertEqual(held(written, "## A\n## A\n"), told)

    def test_the_heading_after_one_found_is_looked_for_right_after_it(self):
        # Given: a template of two headings
        # When: a file with two headings of its own before them is held to it
        # Then: it holds, the second found right after the first
        self.assertEqual(held("## X\n## Y\n## A\n## B\n", "## A\n## B\n"), "")

    def test_a_heading_is_taken_at_its_first_place_that_holds(self):
        # Given: a template of two headings
        # When: a file with the first before and after the second is held to it
        # Then: it holds, the first taken where it comes first
        self.assertEqual(held("## A\n## B\n## A\n", "## A\n## B\n"), "")

    def test_a_heading_missing_is_looked_for_after_the_first_place_the_one_before_holds(self):
        # Given: a template of two headings
        # When: a file with the first twice and the second not at all is held to it
        # Then: the second is expected from the line after the first's first place
        self.assertEqual(
            held("## A\n## A\n", "## A\n## C\n"),
            'from line 2: expected the heading "## C", found none',
        )

    def test_a_heading_found_at_another_level_is_the_first_of_them(self):
        # Given: a template of one heading with a free part
        # When: a file has two headings of it at other levels
        # Then: the first of them is named as found
        self.assertEqual(
            held("### Why 1\n#### Why 2\n", "## Why <n>\n"),
            'from line 1: expected the heading "## Why <n>", found "### Why 1" at line 1',
        )

    def test_headings_are_looked_for_from_the_line_after_the_frontmatter(self):
        for written, told in (
            ("---\na: b\n---\n## X\n", 'from line 4: expected the heading "## Why", found none'),
            ("---\n## X\n", 'from line 1: expected the heading "## Why", found none'),
        ):
            with self.subTest(written=written):
                # Given: a template of headings alone
                # When: a file with frontmatter closed, or opened and never closed, and no heading
                # of it is held to it
                # Then: the heading is expected from the first line after the frontmatter, or from
                # the first line where none is closed
                self.assertEqual(held(written, "## Why\n"), told)

    def test_a_heading_in_a_code_fence_does_not_hold_the_form(self):
        # Given: a template of one heading
        # When: a file holds it only inside a code fence
        # Then: it is out
        self.assertNotEqual(held("```\n## Why\n```\n", "## Why\n"), "")

    def test_without_frontmatter_in_the_template_a_files_own_is_left_unread(self):
        # Given: a template of headings alone
        # When: a file with frontmatter the reader cannot read, holding a line like a heading,
        # and the headings, is held to it
        # Then: it holds, its frontmatter left out of the headings
        self.assertEqual(held("---\na:\n  # x\n---\n## Why\n", "## Why\n"), "")

    def test_without_frontmatter_in_the_template_a_file_opening_with_a_rule_is_all_body(self):
        # Given: a template of headings alone
        # When: a file opening with `---` it never closes, a rule, then the heading, is held to it
        # Then: it holds, the whole file read for headings
        self.assertEqual(held("---\n## Why\n", "## Why\n"), "")

    def test_frontmatter_lines_are_no_headings(self):
        # Given: a template of headings alone
        # When: a file whose only line like the heading is in its frontmatter is held to it
        # Then: it is out
        self.assertNotEqual(held("---\n# Why\n---\n", "# Why\n"), "")


if __name__ == "__main__":
    unittest.main()
