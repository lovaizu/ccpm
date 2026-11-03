"""read_only: a file is read only where it is one of the inputs the lane names or lies in one that
is a folder, each named from the folder the call is made in."""

import os
import unittest

import helpers
from helpers import read_only


class TestAllows(helpers.PluginTest):
    def test_an_input_named_or_under_a_folder_named_is_read(self):
        for path, takes, through in (
            ("notes.md", ["notes.md"], True),
            (os.path.join(self.base, "notes.md"), ["notes.md"], True),
            ("docs/a.md", ["docs/"], True),
            ("README.md", ["notes.md"], False),
            ("docs-old/a.md", ["docs"], False),
        ):
            with self.subTest(path=path, takes=takes):
                # Given: read_only naming a file or a folder
                # When: the subagent reads it, by its name or its whole path, a file under the
                # folder, another file, or one in a folder whose name begins with it
                # Then: what it names goes through, and the rest is stopped
                self.assertEqual(read_only.allows(path, takes, self.plugin, self.base), through)


if __name__ == "__main__":
    unittest.main()
