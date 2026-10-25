"""in_form: a write of the output the lane takes is held to the form it takes, a file of the plugin,
before it is made: a Write by its content, an Edit by the file's text with the edit made, and a
command writing it stopped, as its text cannot be read; a write out of the form is told the
sentence, with the point it is out by on the next line."""

import json
import os
import unittest
from unittest import mock

import helpers
from helpers import in_form
from test_guard import GuardTest

# The form of the output, a file of the plugin: a changelog entry as JSON.
FORM = {
    "type": "object",
    "properties": {"version": {"type": "string"}},
    "required": ["version"],
    "additionalProperties": False,
}
TAKES = ["entry.json", "${CLAUDE_PLUGIN_ROOT}/forms/entry.json"]
SENTENCE = "Write `entry.json` in the form of `${CLAUDE_PLUGIN_ROOT}/forms/entry.json`."


class InFormTest(helpers.PluginTest):
    """A test whose calls are made in `base`, the plugin `notes` holding the form."""

    def setUp(self) -> None:
        super().setUp()
        self.write_json(os.path.join(self.plugin, "forms", "entry.json"), FORM)

    def drifts(self, tool, given, takes=TAKES):
        """What the call of the tool with the input drifts from in_form by."""
        made = helpers.acted(tool, given, self.base)
        return in_form.drifts(made, takes, self.plugin)

    def wrote(self, content, path="entry.json"):
        """What a Write of the content to the path drifts by."""
        return self.drifts("Write", {"file_path": path, "content": content})


class TestWrite(InFormTest):
    def test_a_write_of_the_output_in_its_form_is_no_drift(self):
        # Given: in_form taking entry.json and its form
        # When: a Write gives it JSON of the form
        # Then: it is no drift
        self.assertFalse(self.wrote('{"version": "1.0"}'))

    def test_a_write_of_the_output_out_of_its_form_gives_the_point(self):
        for content, told in (
            ('{"version": 1}', "$.version: expected a string, found 1"),
            ("{}", '$: expected the key "version", found an object without it'),
            ("version: 1", 'line 1, column 1: expected JSON (Expecting value), found "version: 1"'),
        ):
            with self.subTest(content=content):
                # Given: in_form taking entry.json and its form
                # When: a Write gives it text out of the form
                # Then: it drifts by the point it is out by
                self.assertEqual(self.wrote(content), told)

    def test_a_write_of_another_file_is_no_drift(self):
        # Given: in_form taking entry.json
        # When: a Write gives another file text out of the form
        # Then: it is no drift, as the lane holds its output alone
        self.assertFalse(self.wrote("x", "notes.json"))

    def test_the_output_is_named_from_the_folder_the_call_is_made_in(self):
        # Given: in_form taking entry.json
        # When: a Write names it by its whole path, with text out of the form
        # Then: it drifts
        self.assertTrue(self.wrote("{}", os.path.join(self.base, "entry.json")))


class TestEdit(InFormTest):
    def test_an_output_taken_from_the_home_folder_is_the_one_there(self):
        # Given: in_form taking an output named from the home folder, `base` here
        takes = ["~/entry.json", TAKES[1]]
        with mock.patch.dict(os.environ, {"HOME": self.base}):
            # When: a Write gives that file text out of its form
            given = {"file_path": "entry.json", "content": "{}"}
            # Then: it drifts by the point it is out by
            told = '$: expected the key "version", found an object without it'
            self.assertEqual(self.drifts("Write", given, takes), told)

    def test_an_edit_leaving_the_output_in_its_form_is_no_drift(self):
        # Given: the output in its form
        self.write("entry.json", '{"version": "1.0"}')
        # When: an Edit changes its version to another text
        given = {"file_path": "entry.json", "old_string": "1.0", "new_string": "1.1"}
        # Then: it is no drift
        self.assertFalse(self.drifts("Edit", given))

    def test_an_edit_taking_the_output_out_of_its_form_gives_the_point(self):
        # Given: the output in its form
        self.write("entry.json", '{"version": "1.0"}')
        # When: an Edit makes its version a number
        given = {"file_path": "entry.json", "old_string": '"1.0"', "new_string": "1"}
        # Then: it drifts by the point the file would be out by
        self.assertEqual(self.drifts("Edit", given), "$.version: expected a string, found 1")

    def test_an_edit_the_tool_would_refuse_is_no_drift(self):
        # Given: the output, without the text an Edit would replace
        self.write("entry.json", "{}")
        # When: the Edit is made
        given = {"file_path": "entry.json", "old_string": "x", "new_string": "y"}
        # Then: it is no drift, as the tool writes nothing
        self.assertFalse(self.drifts("Edit", given))


class TestCommand(InFormTest):
    def test_a_command_writing_the_output_drifts_saying_to_write_it_by_a_tool(self):
        for command in ('echo \'{"version": "1.0"}\' > entry.json', "rm entry.json"):
            with self.subTest(command=command):
                # Given: in_form taking entry.json
                # When: a command writes it, even in its form
                # Then: it drifts, as a command's text cannot be read, saying to write it by Write
                # or Edit
                self.assertEqual(
                    self.drifts("Bash", {"command": command}),
                    "`entry.json`: expected a write by Write or Edit, whose text is held to the"
                    " form, found a command writing it",
                )

    def test_a_command_writing_another_file_or_none_is_no_drift(self):
        for command in ("echo x > notes.json", "cat entry.json"):
            with self.subTest(command=command):
                # Given: in_form taking entry.json
                # When: a command writes another file, or only reads the output
                # Then: it is no drift
                self.assertFalse(self.drifts("Bash", {"command": command}))


class TestForm(InFormTest):
    def test_a_form_of_the_plugin_is_read(self):
        # Given: the form, a file of the plugin
        # When: it is read for the lane
        # Then: it is the schema
        self.assertEqual(in_form.form(self.plugin, TAKES[1]), FORM)

    def test_a_form_out_of_the_plugin_is_refused(self):
        # Given: a form beside the plugin, out of it
        self.write_json(os.path.join(self.base, "form.json"), FORM)
        # When: it is read for the lane
        # Then: it is refused, as installing copies the plugin's folder alone
        with self.assertRaises(ValueError) as refused:
            in_form.form(self.plugin, "${CLAUDE_PLUGIN_ROOT}/../form.json")
        self.assertIn("out of the plugin", str(refused.exception))

    def test_a_form_linked_from_the_plugin_is_read(self):
        # Given: the form, a link in the plugin to a file beside it, as a plugin takes another's
        self.write_json(os.path.join(self.base, "form.json"), FORM)
        os.symlink(
            os.path.join("..", "..", "form.json"), os.path.join(self.plugin, "forms", "linked.json")
        )
        # When: it is read for the lane
        # Then: it is the schema, as installing copies the file a link points to into the plugin
        self.assertEqual(in_form.form(self.plugin, "${CLAUDE_PLUGIN_ROOT}/forms/linked.json"), FORM)

    def test_a_form_not_named_from_the_plugins_folder_is_refused(self):
        for named in ("forms/entry.json", os.path.join(self.plugin, "forms", "entry.json")):
            with self.subTest(named=named):
                # Given: the form named from the folder the subagent works in, or by a whole path
                # When: it is read for the lane
                # Then: it is refused, as the subagent reads it where Claude Code puts the
                # plugin's folder in for ${CLAUDE_PLUGIN_ROOT}, wherever the plugin is installed
                with self.assertRaises(ValueError) as refused:
                    in_form.form(self.plugin, named)
                self.assertIn(
                    "named as ${CLAUDE_PLUGIN_ROOT}/<path in the plugin>", str(refused.exception)
                )

    def test_a_form_gone_since_the_lane_was_laid_stops_the_write_saying_so(self):
        # Given: in_form whose form is no longer there
        os.remove(os.path.join(self.plugin, "forms", "entry.json"))
        # When: the output is written
        told = self.wrote('{"version": "1.0"}')
        # Then: it drifts, saying the form cannot be read and to stop for the plugin to be fixed
        named = os.path.join(self.plugin, "forms", "entry.json")
        self.assertTrue(told.startswith(f"the form `{named}` cannot be read: "), told)
        self.assertTrue(
            told.endswith(
                ". Stop here and reply that the plugin's maker must fix the form and lay its lanes"
                " again with `lay.py write`."
            ),
            told,
        )


class TestGuard(GuardTest):
    """in_form laid on step 3 of changelog-writer, run by the guard as Claude Code runs it."""

    LAID = ((3, "in_form", TAKES),)

    def setUp(self) -> None:
        super().setUp()
        self.write_json(os.path.join(self.plugin, "forms", "entry.json"), FORM)

    def written(self, content):
        """The guard on changelog-writer writing entry.json with the content."""
        event = self.called("Write", {"file_path": "entry.json", "content": content})
        return self.guard(json.dumps(event))

    def test_a_step_still_saying_the_sentence_as_written_holds(self):
        # Given: in_form on step 3, the step saying ${CLAUDE_PLUGIN_ROOT} as `lay.py write` writes it
        # When: changelog-writer writes entry.json in its form
        # Then: the step is read as holding the sentence, not as changed
        self.assertNotIn("no longer says", self.written('{"version": "1.0"}')[1])

    def test_a_write_out_of_the_form_is_stopped_with_the_sentence_and_the_point(self):
        # Given: in_form on step 3 of changelog-writer
        # When: changelog-writer writes entry.json out of its form
        # Then: the call is stopped, and the subagent told the sentence headed by the plugin, the
        # plugin's folder put in for ${CLAUDE_PLUGIN_ROOT} as in the step it reads, and the point
        # on the next line
        told = SENTENCE.replace("${CLAUDE_PLUGIN_ROOT}", self.plugin)
        self.assertEqual(
            self.written('{"version": 1}'),
            ("told", f"notes: {told}\n$.version: expected a string, found 1"),
        )

    def test_a_write_in_the_form_is_let_through(self):
        # Given: in_form on step 3 of changelog-writer
        # When: changelog-writer writes entry.json in its form
        # Then: the call goes on, nothing said
        self.assertEqual(self.written('{"version": "1.0"}'), ("", ""))


if __name__ == "__main__":
    unittest.main()
