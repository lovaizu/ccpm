"""The form a file of the plugin gives: a `.json` file a JSON Schema, a `.md` file a Markdown
template, any other refused; and a written text held to it, as JSON, as JSON on each line for an
output named `.jsonl`, or as Markdown."""

import os
import unittest

from helpers import forms, template, testing

SCHEMA = {"type": "object", "properties": {"a": {"type": "string"}}, "required": ["a"]}


class FormTest(testing.FolderTest):
    def form(self, name, text):
        """The form read from a file of the name holding the text."""
        self.write(name, text)
        return forms.read(os.path.join(self.base, name))


class TestRead(FormTest):
    def test_a_json_file_gives_its_schema(self):
        # Given: a .json file holding a schema lane reads
        # When: it is read as a form
        # Then: the form is the schema
        self.assertEqual(self.form("f.json", '{"type": "string"}'), {"type": "string"})

    def test_a_markdown_file_gives_its_template(self):
        # Given: a .md file holding a template
        # When: it is read as a form
        # Then: the form is the template
        self.assertEqual(self.form("f.md", "## A\n"), template.Template([], [(2, "A")]))

    def test_a_file_lane_cannot_read_as_a_form_is_refused_saying_why(self):
        for name, text, named in (
            ("f.json", "{", "is no form lane reads: Expecting property name"),
            ("f.json", "null", "$: expected a schema object, found null"),
            ("f.json", '{"format": "date"}', "`format` is no keyword"),
            ("f.md", "text\n", "no heading"),
            ("f.yaml", "a: b\n", "neither a .json schema nor a .md template"),
        ):
            with self.subTest(name=name, text=text):
                # Given: a file holding no form lane reads
                # When: it is read as a form
                # Then: it is refused, saying why
                with self.assertRaises(ValueError) as refused:
                    self.form(name, text)
                self.assertIn(named, str(refused.exception))

    def test_a_form_not_there_is_refused(self):
        for name in ("none.json", "none.md"):
            with self.subTest(name=name):
                # Given: no file at the path
                # When: it is read as a form
                # Then: it is refused, saying it cannot be read
                with self.assertRaises(ValueError) as refused:
                    forms.read(os.path.join(self.base, name))
                self.assertIn("cannot be read", str(refused.exception))


class TestHeld(FormTest):
    def test_json_in_the_form_holds(self):
        # Given: a schema
        # When: JSON of it is written to a .json output
        # Then: it holds
        self.assertEqual(forms.held(SCHEMA, "out.json", '{"a": "x"}\n'), "")

    def test_json_out_of_the_form_gives_its_place(self):
        # Given: a schema
        # When: JSON out of it is written
        # Then: the point is given at its place in the value
        self.assertEqual(
            forms.held(SCHEMA, "out.json", '{"a": 1}'), "$.a: expected a string, found 1"
        )

    def test_text_that_is_no_json_gives_its_line_and_column(self):
        for text, told in (
            (
                '{\n  "a": "x"\n  "b": 1}',
                'line 3, column 3: expected JSON (Expecting \',\' delimiter), found "\\"b\\": 1}"',
            ),
            ("", "line 1, column 1: expected JSON (Expecting value), found the end of the line"),
            (
                '{"a" 1,\n"b": 2}',
                "line 1, column 6: expected JSON (Expecting ':' delimiter), found \"1,\"",
            ),
        ):
            with self.subTest(text=text):
                # Given: a schema
                # When: text that is no JSON, or none, is written
                # Then: the point is given at its line and column, with what stands there
                self.assertEqual(forms.held(SCHEMA, "out.json", text), told)

    def test_jsonl_holds_each_line_to_the_form(self):
        for text, told in (
            ('{"a": "x"}\n{"a": "y"}\n', ""),
            ("", ""),
            ('{"a": "x"}\n{"a": 2}\n', "line 2, $.a: expected a string, found 2"),
            ('{"a": "x"}\n{"a": "y"}\n{"a": 3}\n', "line 3, $.a: expected a string, found 3"),
            (
                '{"a": "x"}\n\n{"a": "y"}\n',
                "line 2, column 1: expected JSON (Expecting value), found the end of the line",
            ),
            (
                '{"a": "x"}\n{"a":\n',
                "line 2, column 6: expected JSON (Expecting value), found the end of the line",
            ),
        ):
            with self.subTest(text=text):
                # Given: a schema
                # When: lines of JSON are written to a .jsonl output, one out of the form, an empty
                # line or one cut, or none
                # Then: each line is held to the form, a point given at its line
                self.assertEqual(forms.held(SCHEMA, "out.jsonl", text), told)

    def test_markdown_is_held_to_its_template(self):
        # Given: a template of one heading
        asked = template.read("## Why\n")
        # When: Markdown with it and without it is written
        # Then: the first holds, the second gives the heading expected
        self.assertEqual(forms.held(asked, "out.md", "## Why\n"), "")
        self.assertIn('expected the heading "## Why"', forms.held(asked, "out.md", "# x\n"))


if __name__ == "__main__":
    unittest.main()
