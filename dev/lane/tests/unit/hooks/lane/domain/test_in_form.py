"""The cases of in_form: what a role writes to its output held to a JSON Schema or a Markdown
template, before the write and again as the role gives its result."""

import json

from helpers import in_form, lanes, testing

CONTEXT = lanes.Context((), ())
SCHEMA = {
    "type": "object",
    "required": ["version"],
    "additionalProperties": False,
    "properties": {"version": {"type": "string"}},
}
TEMPLATE = "---\ntitle: x\nversion: y\n---\n\n# Notes\n\n## Added\n\n## Fixed\n"


class FormTest(testing.FolderTest):
    def given(self, output="notes.json", form="form.json"):
        self.write("form.json", json.dumps(SCHEMA))
        self.write("form.md", TEMPLATE)
        return {"output": [f"{self.base}/{output}"], "form": [f"{self.base}/{form}"]}

    def write_call(self, name, content):
        return lanes.Call(
            "Write", {"file_path": f"{self.base}/{name}", "content": content}, self.base
        )


class TestJson(FormTest):
    def test_a_json_output_in_its_form_goes_on(self):
        call = self.write_call("notes.json", '{"version": "1.0"}')
        self.assertIsNone(in_form.check(call, self.given(), CONTEXT))

    def test_a_json_output_out_of_its_form_is_broken_with_where(self):
        call = self.write_call("notes.json", '{"version": 1}')
        self.assertEqual(
            in_form.check(call, self.given(), CONTEXT),
            f"The content is out of `{self.base}/form.json`: $.version: expected a string, found 1",
        )

    def test_output_that_is_no_json_is_broken_with_where(self):
        call = self.write_call("notes.json", "{")
        self.assertEqual(
            in_form.check(call, self.given(), CONTEXT),
            "The content is no JSON at line 1, column 2: Expecting property name enclosed in double"
            " quotes",
        )

    def test_each_line_of_a_jsonl_output_is_held_to_the_form(self):
        call = self.write_call("notes.jsonl", '{"version": "1"}\n{"version": 2}\n')
        self.assertEqual(
            in_form.check(call, self.given("notes.jsonl"), CONTEXT),
            f"Line 2 is out of `{self.base}/form.json`: $.version: expected a string, found 2",
        )

    def test_an_edit_is_held_with_its_change_made(self):
        self.write("notes.json", '{"version": "1.0"}')
        call = lanes.Call(
            "Edit",
            {"file_path": f"{self.base}/notes.json", "old_string": '"1.0"', "new_string": "2"},
            self.base,
        )
        self.assertIn(
            "expected a string, found 2", in_form.check(call, self.given(), CONTEXT) or ""
        )

    def test_an_edit_of_every_match_changes_each(self):
        self.write("notes.json", '{"version": "a"}')
        given = {
            "file_path": f"{self.base}/notes.json",
            "old_string": "a",
            "new_string": "b",
            "replace_all": True,
        }
        call = lanes.Call("Edit", given, self.base)
        self.assertIsNone(in_form.check(call, self.given(), CONTEXT))

    def test_a_jsonl_output_whose_lines_each_hold_goes_on(self):
        call = self.write_call("notes.jsonl", '{"version": "1"}\n\n{"version": "2"}\n')
        self.assertIsNone(in_form.check(call, self.given("notes.jsonl"), CONTEXT))

    def test_an_edit_of_an_output_not_there_is_held_as_its_new_text(self):
        call = lanes.Call(
            "Edit",
            {
                "file_path": f"{self.base}/notes.json",
                "old_string": "",
                "new_string": '{"version": 1}',
            },
            self.base,
        )
        self.assertIn(
            "expected a string, found 1", in_form.check(call, self.given(), CONTEXT) or ""
        )

    def test_a_read_goes_on(self):
        call = lanes.Call("Read", {"file_path": f"{self.base}/notes.json"}, self.base)
        self.assertIsNone(in_form.check(call, self.given(), CONTEXT))

    def test_a_write_of_another_file_goes_on(self):
        call = self.write_call("other.json", "{")
        self.assertIsNone(in_form.check(call, self.given(), CONTEXT))

    def test_a_form_that_isnt_one_lane_reads_cannot_be_checked(self):
        given = self.given()
        self.write("form.json", json.dumps({"type": "integer", "minimum": 1}))
        with self.assertRaisesRegex(lanes.Unchecked, r"is no form that Lane reads: \$: `minimum`"):
            in_form.check(self.write_call("notes.json", "1"), given, CONTEXT)

    def test_a_form_that_isnt_there_cannot_be_checked(self):
        given = {"output": [f"{self.base}/notes.json"], "form": [f"{self.base}/gone.json"]}
        with self.assertRaisesRegex(lanes.Unchecked, r"gone\.json isn't there"):
            in_form.check(self.write_call("notes.json", "1"), given, CONTEXT)

    def test_an_output_in_one_of_several_forms_goes_on(self):
        given = self.given()
        given["form"].insert(0, f"{self.base}/form.md")
        self.assertIsNone(
            in_form.check(self.write_call("notes.json", '{"version": "1"}'), given, CONTEXT)
        )


class TestMarkdown(FormTest):
    def test_markdown_with_each_heading_and_key_of_its_template_goes_on(self):
        text = "---\ntitle: a\nversion: 1\nextra: z\n---\n# Notes\n## Added\n- x\n## Fixed\n"
        call = self.write_call("notes.md", text)
        self.assertIsNone(in_form.check(call, self.given("notes.md", "form.md"), CONTEXT))

    def test_markdown_missing_a_heading_of_its_template_is_broken(self):
        call = self.write_call("notes.md", "---\ntitle: a\nversion: 1\n---\n# Notes\n## Added\n")
        self.assertEqual(
            in_form.check(call, self.given("notes.md", "form.md"), CONTEXT),
            f"The content is out of `{self.base}/form.md`: it lacks the heading `## Fixed`.",
        )

    def test_markdown_with_its_headings_out_of_order_is_broken(self):
        call = self.write_call(
            "notes.md", "---\ntitle: a\nversion: 1\n---\n# Notes\n## Fixed\n## Added\n"
        )
        self.assertIn(
            "it lacks the heading `## Fixed`",
            in_form.check(call, self.given("notes.md", "form.md"), CONTEXT) or "",
        )

    def test_markdown_missing_a_frontmatter_key_of_its_template_is_broken(self):
        call = self.write_call("notes.md", "---\ntitle: a\n---\n# Notes\n## Added\n## Fixed\n")
        self.assertEqual(
            in_form.check(call, self.given("notes.md", "form.md"), CONTEXT),
            f"The content is out of `{self.base}/form.md`: its frontmatter lacks the key"
            " `version`.",
        )


class TestEnd(FormTest):
    def test_an_output_there_in_its_form_keeps_the_lane(self):
        given = self.given()
        self.write("notes.json", '{"version": "1"}')
        self.assertIsNone(in_form.end(given, [], CONTEXT))

    def test_an_output_there_out_of_its_form_breaks_the_lane(self):
        given = self.given()
        self.write("notes.json", "[]")
        self.assertEqual(
            in_form.end(given, [], CONTEXT),
            f"`{self.base}/notes.json` is out of `{self.base}/form.json`: $: expected an object,"
            " found []",
        )

    def test_an_output_not_there_keeps_the_lane(self):
        self.assertIsNone(in_form.end(self.given(), [], CONTEXT))
