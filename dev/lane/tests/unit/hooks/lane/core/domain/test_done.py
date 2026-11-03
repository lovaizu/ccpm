"""What a subagent did, as an end lane holds it: the files its calls kept wrote, and the lines of a
file its Read calls covered."""

import unittest

import helpers
from helpers import done


class TestDone(helpers.PluginTest):
    def test_the_files_written_are_those_of_write_edit_and_notebookedit_in_order(self):
        calls = [
            helpers.kept_call("Write", file_path="a.md", content="x"),
            helpers.kept_call("Bash", command="ls"),
            helpers.kept_call("NotebookEdit", notebook_path="b.ipynb", new_source="x"),
            helpers.kept_call("Edit", file_path=1),
        ]
        # Given: a Write, a command, a NotebookEdit, and an Edit of no path
        found = helpers.did(self.base, self.plugin, calls)
        # When: the files written are read
        # Then: they are those of the Write and the NotebookEdit, by their whole paths
        self.assertEqual(done.written(found, calls), [f"{self.base}/a.md", f"{self.base}/b.ipynb"])

    def test_the_lines_read_are_those_each_read_of_the_file_covered(self):
        calls = [
            helpers.kept_call("Read", file_path="a.md", offset=3, limit=2),
            helpers.kept_call("Read", file_path="b.md"),
            helpers.kept_call("Grep", path="a.md"),
            helpers.kept_call("Read", file_path="a.md", limit=0),
        ]
        # Given: a Read of lines 3 and 4 of a.md, one of another file, a Grep of it, and a Read
        # of a limit of none
        found = helpers.did(self.base, self.plugin, calls)
        # When: the lines read of a.md are read
        # Then: they are 3 and 4, and those a Read gives by default
        self.assertEqual(
            done.lines_read(found, f"{self.base}/a.md"), set(range(1, done.READ_LINES + 1))
        )
        self.assertEqual(done.lines_read(found, f"{self.base}/c.md"), set())

    def test_a_files_text_or_none_where_it_cannot_be_read(self):
        self.write("a.md", "x")
        self.write("b.bin", "")
        with open("b.bin", "wb") as f:
            f.write(b"\xff")
        # Given: a text file, a file of no text, and none
        # When: each is read
        # Then: the text, and none for the others
        self.assertEqual(
            [done.text(f"{self.base}/{n}") for n in ("a.md", "b.bin", "c.md")], ["x", None, None]
        )


if __name__ == "__main__":
    unittest.main()
