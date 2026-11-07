"""edit_only: once an output the lane names is there, it is changed only with Edit; a Write makes
it while it is not there, a NotebookEdit never changes it, and any other file is not the lane's."""

import os
import unittest

import helpers
from helpers import edit_only


class TestAllows(helpers.PluginTest):
    def allows(self, tool: str, path: str, takes: list) -> bool:
        """Whether edit_only taking the outputs lets the tool's write of the path, made in base,
        through."""
        return edit_only.allows(tool, path, takes, self.plugin, self.base)

    def test_an_output_there_is_changed_by_edit_alone(self):
        for tool, through in (("Edit", True), ("Write", False), ("NotebookEdit", False)):
            with self.subTest(tool=tool):
                # Given: design-tree.md there, and edit_only naming it
                self.write("design-tree.md", "# Design tree\n")
                # When: the subagent changes it with the tool
                # Then: Edit goes through, and Write and NotebookEdit are stopped
                self.assertEqual(self.allows(tool, "design-tree.md", ["design-tree.md"]), through)

    def test_an_output_not_yet_there_is_made_by_write(self):
        # Given: edit_only naming design-tree.md, which is not there
        # When: the subagent makes it with Write
        # Then: it goes through
        self.assertTrue(self.allows("Write", "design-tree.md", ["design-tree.md"]))

    def test_a_file_under_an_output_folder_is_held_alike(self):
        # Given: edit_only naming the folder plans/, a file under it there
        self.write("plans/a/design-tree.md", "x")
        # When: the subagent writes that file whole, and another not yet there
        # Then: the first is stopped, and the second goes through
        self.assertFalse(self.allows("Write", "plans/a/design-tree.md", ["plans/"]))
        self.assertTrue(self.allows("Write", "plans/b/design-tree.md", ["plans/"]))

    def test_any_other_file_is_not_held(self):
        # Given: README.md there, and edit_only naming design-tree.md
        self.write("README.md", "x")
        # When: the subagent writes README.md whole
        # Then: it goes through, as the lane holds its outputs alone
        self.assertTrue(self.allows("Write", "README.md", ["design-tree.md"]))

    def test_an_output_reached_through_a_link_is_held(self):
        # Given: a link tree.md to design-tree.md, which is there, and edit_only naming it
        self.write("design-tree.md", "x")
        os.symlink("design-tree.md", "tree.md")
        # When: the subagent writes the link whole
        # Then: it is stopped, as what it writes is the output
        self.assertFalse(self.allows("Write", "tree.md", ["design-tree.md"]))


if __name__ == "__main__":
    unittest.main()
