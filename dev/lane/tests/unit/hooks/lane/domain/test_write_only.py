"""The cases of write_only's check, which stops a write of a file outside the outputs."""

from helpers import lanes, testing, write_only

CONTEXT = lanes.Context((), ())


class TestCheck(testing.FolderTest):
    def given(self, *paths):
        return {"output": [f"{self.base}/{p}" for p in paths]}

    def call(self, tool, **given):
        return lanes.Call(tool, given, self.base)

    def test_a_write_of_an_output_goes_on(self):
        call = self.call("Write", file_path=f"{self.base}/CHANGELOG.md", content="")
        self.assertIsNone(write_only.check(call, self.given("CHANGELOG.md"), CONTEXT))

    def test_a_write_under_an_output_folder_goes_on(self):
        call = self.call("Write", file_path=f"{self.base}/notes/a.md", content="")
        self.assertIsNone(write_only.check(call, self.given("notes"), CONTEXT))

    def test_a_write_of_a_file_beside_a_folder_of_the_same_start_is_broken(self):
        call = self.call("Write", file_path=f"{self.base}/notes2/a.md", content="")
        self.assertEqual(
            write_only.check(call, self.given("notes"), CONTEXT),
            f"The call writes {self.base}/notes2/a.md.",
        )

    def test_an_edit_of_another_file_is_broken(self):
        call = self.call("Edit", file_path=f"{self.base}/README.md")
        self.assertEqual(
            write_only.check(call, self.given("CHANGELOG.md"), CONTEXT),
            f"The call writes {self.base}/README.md.",
        )

    def test_a_relative_path_reads_from_the_folder_the_call_runs_in(self):
        call = self.call("Edit", file_path="CHANGELOG.md")
        self.assertIsNone(write_only.check(call, self.given("CHANGELOG.md"), CONTEXT))

    def test_a_notebook_edit_of_another_file_is_broken(self):
        call = self.call("NotebookEdit", notebook_path=f"{self.base}/n.ipynb")
        self.assertEqual(
            write_only.check(call, self.given("CHANGELOG.md"), CONTEXT),
            f"The call writes {self.base}/n.ipynb.",
        )

    def test_a_read_goes_on(self):
        call = self.call("Read", file_path=f"{self.base}/README.md")
        self.assertIsNone(write_only.check(call, self.given("CHANGELOG.md"), CONTEXT))
