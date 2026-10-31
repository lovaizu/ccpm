"""Property-based tests of where Claude Code keeps its records: each behavior over a kind of path,
checked on many paths Hypothesis makes, new on every run, CI included."""

import os
import unittest

from helpers import record, testing
from test_record import KeptTest

hypothesis = testing.hypothesis()
given = hypothesis.given
st = hypothesis.strategies


class TestFolders(KeptTest):
    @given(st.text(st.characters(blacklist_categories=("Cs",)), max_size=100))
    def test_any_path_names_its_folder_by_letters_digits_and_hyphens(self, top):
        # Given: any path short enough to name its folder whole
        # When: its folder is looked for
        # Then: each ASCII letter and digit stands as it is, and each UTF-16 unit of any other
        # character as `-`, as JavaScript counts them
        want = "".join(
            c if c.isascii() and c.isalnum() else "-" * (len(c.encode("utf-16-le")) // 2)
            for c in top
        )
        self.assertEqual(record.folders(top), [os.path.join(self.projects, want)])


if __name__ == "__main__":
    unittest.main()
