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
        # The lines a Read gives where its call names no limit, as the Read tool documents it.
        default = set(range(1, 2001))
        for given, lines in (
            ({"offset": 3, "limit": 2}, {3, 4}),
            ({"offset": 5, "limit": 1}, {5}),
            ({}, default),
            ({"offset": 0}, default),
            ({"limit": 0}, default),
            ({"limit": -1}, default),
            ({"offset": "3", "limit": "2"}, default),
        ):
            with self.subTest(given=given):
                # Given: a Grep of a.md, a Read of another file, and a Read of a.md from the offset
                # for the limit, or of none of them
                calls = [
                    helpers.kept_call("Grep", path="a.md"),
                    helpers.kept_call("Read", file_path="b.md", offset=9, limit=1),
                    helpers.kept_call("Read", file_path="a.md", **given),
                ]
                found = helpers.did(self.base, self.plugin, calls)
                # When: the lines read of a.md are read
                # Then: they are those the Read covered, counting from line 1, and the first
                # 2000 where it names no limit of one line or more
                self.assertEqual(done.lines_read(found, f"{self.base}/a.md"), lines)
        self.assertEqual(done.lines_read(found, f"{self.base}/c.md"), set())

    def test_a_file_is_under_a_place_where_it_is_the_place_or_lies_in_it(self):
        for file, under in (
            ("/p/src", True),
            ("/p/src/a.py", True),
            ("/p/srcs", False),
            ("/p/sr", False),
            ("/p/a", False),
        ):
            with self.subTest(file=file):
                # Given: the place /p/src
                # When: a file is held to it
                # Then: it is under it where it is the place or lies in it, by whole names
                self.assertEqual(done.under(file, "/p/src"), under)

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
