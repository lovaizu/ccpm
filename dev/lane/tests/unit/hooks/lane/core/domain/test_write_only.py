"""write_only: a file is written only where it is one of the outputs the lane names or lies in one
that is a folder, each named from the folder the call is made in."""

import os
import unittest

import helpers
from helpers import write_only


class TestAllows(helpers.PluginTest):
    def allows(self, path: str, takes: list) -> bool:
        """Whether write_only taking the outputs lets a write of the path, made in base, through."""
        return write_only.allows(path, takes, self.plugin, self.base)

    def test_an_output_named_is_written(self):
        for path in ("CHANGELOG.md", os.path.join(self.base, "CHANGELOG.md"), "./CHANGELOG.md"):
            with self.subTest(path=path):
                # Given: write_only naming CHANGELOG.md
                # When: the subagent writes it, by its name, its whole path, or from ./
                # Then: it goes through
                self.assertTrue(self.allows(path, ["CHANGELOG.md"]))

    def test_any_other_file_is_stopped(self):
        for path in ("README.md", "docs/CHANGELOG.md", "/tmp/CHANGELOG.md", "CHANGELOG.md.bak"):
            with self.subTest(path=path):
                # Given: write_only naming CHANGELOG.md
                # When: the subagent writes another file, one of the name in another folder, or
                # one whose name begins with it
                # Then: it is stopped
                self.assertFalse(self.allows(path, ["CHANGELOG.md"]))

    def test_a_folder_named_lets_every_file_under_it_be_written(self):
        for path, through in (
            ("notes/a.md", True),
            ("notes/deep/b.md", True),
            ("notes", True),
            ("notes-old/a.md", False),
            ("notes/../a.md", False),
        ):
            with self.subTest(path=path):
                # Given: write_only naming the folder notes/
                # When: the subagent writes a file under it, deeper, the folder itself, one in a
                # folder whose name begins with it, or one named through it out of it
                # Then: what lies in it goes through, and the rest is stopped
                self.assertEqual(self.allows(path, ["notes/"]), through)

    def test_a_file_reached_through_a_link_is_the_file_it_reaches(self):
        # Given: a link out.md to CHANGELOG.md, and write_only naming CHANGELOG.md
        self.write("CHANGELOG.md", "")
        os.symlink("CHANGELOG.md", "out.md")
        # When: the subagent writes the link
        # Then: it goes through, as what it writes is CHANGELOG.md
        self.assertTrue(self.allows("out.md", ["CHANGELOG.md"]))

    def test_one_of_several_outputs_is_written(self):
        # Given: write_only naming two outputs
        # When: the subagent writes the second
        # Then: it goes through
        self.assertTrue(self.allows("b.md", ["a.md", "b.md"]))


if __name__ == "__main__":
    unittest.main()
