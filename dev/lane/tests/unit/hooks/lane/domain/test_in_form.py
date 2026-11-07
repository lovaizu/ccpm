"""in_form: a write of an output the lane names held to the form it names, a file of the plugin
named from its folder, before the write is made: a Write by its content, an Edit by the file's text
with the edit made; and, as the subagent gives its result, each output there held to it again."""

import json
import os
import unittest

import helpers
from helpers import in_form

FORM = "${CLAUDE_PLUGIN_ROOT}/forms/entry.json"
SCHEMA = {"type": "object", "required": ["version"], "properties": {"version": {"type": "string"}}}
OUT = '$: expected the key "version", found an object without it'


class InFormTest(helpers.PluginTest):
    def setUp(self) -> None:
        super().setUp()
        self.write_json(os.path.join(self.plugin, "forms", "entry.json"), SCHEMA)
        self.places = {"output": ["entry.json"], "form": [FORM]}

    def out_of(self, tool: str, **given: object) -> str:
        """The point a call of the tool with the input is out of the form by."""
        return in_form.out_of(tool, given, self.places, self.plugin, self.base)


class TestForm(InFormTest):
    def test_a_form_named_from_the_plugins_folder_is_read(self):
        # Given: the form named from the plugin's folder
        # When: it is read
        # Then: it is the schema, and nothing refuses it
        self.assertEqual(in_form.form(FORM, self.plugin), SCHEMA)
        self.assertEqual(in_form.refused(FORM, self.plugin), "")

    def test_a_form_that_cannot_be_laid_is_refused_saying_why(self):
        self.write(os.path.join(self.base, "out.json"), "{}")
        for named, said in (
            ("forms/entry.json", "is not named as ${CLAUDE_PLUGIN_ROOT}/<path in the plugin>"),
            ("${CLAUDE_PLUGIN_ROOT}/../out.json", "lies out of the plugin"),
            ("${CLAUDE_PLUGIN_ROOT}/forms/gone.json", "cannot be read"),
        ):
            with self.subTest(named=named):
                # Given: a form named from the project, out of the plugin, or not there
                # When: it is held for laying
                # Then: it is refused, saying why
                self.assertIn(
                    f"names the form {named}, which {said}", in_form.refused(named, self.plugin)
                )


class TestOutOf(InFormTest):
    def test_a_write_in_the_form_goes_through_and_one_out_of_it_is_told_the_point(self):
        for content, point in (('{"version": "1.0"}', ""), ("{}", OUT)):
            with self.subTest(content=content):
                # Given: in_form holding entry.json to the schema
                # When: the subagent writes it in the form, or out of it
                # Then: the first goes through, and the second is told the point
                self.assertEqual(
                    self.out_of("Write", file_path="entry.json", content=content), point
                )

    def test_an_edit_is_held_by_the_files_text_with_the_edit_made(self):
        self.write("entry.json", '{"version": "1.0"}')
        for old, new, everywhere, point in (
            ("1.0", "1.1", False, ""),
            ('"version"', '"v"', False, OUT),
            ("nothing", "x", False, ""),
            ("", "x", False, ""),
            ('"', "'", True, "line 1, column 2: expected JSON"),
        ):
            with self.subTest(old=old):
                # Given: entry.json in the form
                # When: an edit keeps it so, takes the key out, finds no text, has no text, or
                # changes each quote
                told = self.out_of(
                    "Edit",
                    file_path="entry.json",
                    old_string=old,
                    new_string=new,
                    replace_all=everywhere,
                )
                # Then: what keeps the form, or changes nothing, goes through, and the rest is
                # told the point
                self.assertTrue(told.startswith(point) if point else told == "")

    def test_an_edit_replaces_the_first_text_found_or_each_where_it_says_all(self):
        self.write("entry.json", "a a a")
        for everywhere, text in (
            (True, "b b b"),
            (False, "b a a"),
            (None, "b a a"),
            ("y", "b a a"),
            (1, "b a a"),
        ):
            with self.subTest(everywhere=everywhere):
                # Given: a file holding a three times
                given: dict[str, object] = {"old_string": "a", "new_string": "b"}
                if everywhere is not None:
                    given["replace_all"] = everywhere
                # When: an Edit replaces a by b, with replace_all true, false, not given, or not
                # a bool
                # Then: each a is replaced where it is true, and the first alone otherwise, as
                # Edit makes it
                path = os.path.join(self.base, "entry.json")
                self.assertEqual(in_form.text_written("Edit", given, path), text)

    def test_an_edit_of_a_file_not_there_changes_nothing(self):
        # Given: entry.json not there
        # When: the subagent edits it
        # Then: nothing is told, as the edit cannot be made
        self.assertEqual(
            self.out_of("Edit", file_path="entry.json", old_string="a", new_string="b"), ""
        )

    def test_a_write_of_another_file_or_a_notebooks_edit_of_the_output(self):
        # Given: in_form on entry.json
        # When: the subagent writes another file, or edits the output as a notebook
        # Then: the first is not held, and the second is stopped, no form holding a notebook
        self.assertEqual(self.out_of("Write", file_path="other.json", content="x"), "")
        self.assertEqual(
            self.out_of("NotebookEdit", notebook_path="entry.json", new_source="x"),
            "`entry.json`: expected a write by Write or Edit, found NotebookEdit",
        )
        # And: where two outputs name it, the first is named
        self.places["output"] = ["entry.json", "./"]
        self.assertEqual(
            self.out_of("NotebookEdit", notebook_path="entry.json", new_source="x"),
            "`entry.json`: expected a write by Write or Edit, found NotebookEdit",
        )

    def test_one_of_several_forms_held_is_enough(self):
        # Given: a second form, a template
        self.write(os.path.join(self.plugin, "forms", "entry.md"), "# Entry\n")
        self.places["form"].append("${CLAUDE_PLUGIN_ROOT}/forms/entry.md")
        # When: the subagent writes text held to the second alone, or to neither
        # Then: the first goes through, and the second is told the first form's point
        self.assertEqual(self.out_of("Write", file_path="entry.json", content="# Entry\n"), "")
        told = self.out_of("Write", file_path="entry.json", content="x")
        self.assertTrue(told.startswith("line 1, column 1: expected JSON"))


class TestMissing(InFormTest):
    def test_each_output_there_is_held_again_as_the_result_is_given(self):
        found = helpers.did(self.base, self.plugin)
        for text, said in (
            (None, ""),
            (json.dumps({"version": "1"}), ""),
            ("{}", f"`entry.json`: {OUT}"),
        ):
            with self.subTest(text=text):
                # Given: entry.json not there, in the form, or out of it, as a command wrote it
                if text is not None:
                    self.write("entry.json", text)
                # When: the subagent gives its result
                # Then: only the output out of the form is told, with its point
                self.assertEqual(in_form.missing(self.places, found), said)


if __name__ == "__main__":
    unittest.main()
