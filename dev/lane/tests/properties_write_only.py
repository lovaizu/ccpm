"""Property-based tests of write_only: on any path in the folder the call is made in, written by a tool
or by a command's redirect, checked on many paths Hypothesis makes, new on every run, CI included."""

import shlex
import string
import unittest

import helpers
from helpers import NO_PLUGIN, testing, write_only

hypothesis = testing.hypothesis()
given = hypothesis.given
st = hypothesis.strategies

# A path in the folder, named from it: one that neither begins at the top nor climbs out of it.
PATHS = st.text(string.ascii_letters + string.digits + "._/", min_size=1, max_size=12).filter(
    lambda n: not n.startswith(("/", "-")) and ".." not in n
)


class TestAnyPath(testing.FolderTest):
    def drifts(self, path, takes):
        """Whether a Write of the path and a command writing it by a redirect each drift from
        write_only taking the outputs."""
        events = [
            {"tool_name": "Write", "tool_input": {"file_path": path}},
            {"tool_name": "Bash", "tool_input": {"command": f"echo x > {shlex.quote(path)}"}},
        ]
        return [
            write_only.drifts(helpers.call_of({"cwd": self.base, **e}), takes, NO_PLUGIN)
            for e in events
        ]

    @given(PATHS)
    def test_a_write_of_the_output_is_no_drift(self, path):
        # Given: write_only taking any path in the folder
        # When: a tool or a command writes it
        # Then: neither is a drift
        self.assertEqual(self.drifts(path, [path]), [False, False])

    @given(PATHS)
    def test_a_write_of_another_path_drifts(self, path):
        # Given: write_only taking any path in the folder
        # When: a tool or a command writes another file beside it
        # Then: both are drifts
        self.assertEqual(self.drifts(path + "x", [path]), [True, True])


if __name__ == "__main__":
    unittest.main()
