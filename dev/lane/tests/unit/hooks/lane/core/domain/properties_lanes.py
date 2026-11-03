"""Property-based tests of run_only and write_only: a command goes through only where it is one
named, the blanks around it aside, and a file only where it lies in an output named; on many
inputs Hypothesis makes, new on every run, CI included."""

import os
import string
import unittest

from helpers import run_only, testing, write_only

hypothesis = testing.hypothesis()
given = hypothesis.given
st = hypothesis.strategies

# A command as a step names one: words of printable characters, one blank between them.
WORD = st.text(string.ascii_letters + string.digits + "-_./=$'\"&|;", min_size=1, max_size=6)
COMMANDS = st.lists(WORD, min_size=1, max_size=4).map(" ".join)
# A name of a file or folder, none of them `.` or `..`.
NAMES = st.text(string.ascii_letters + string.digits + "_-", min_size=1, max_size=6)


class TestRunOnly(unittest.TestCase):
    @given(st.lists(COMMANDS, min_size=1, max_size=3), COMMANDS, st.sampled_from(["", " ", "\n"]))
    def test_a_command_goes_through_only_where_it_is_one_named(self, takes, command, blank):
        # Given: run_only naming some commands, and a command run with blanks around it or none
        # When: it is judged
        # Then: it goes through exactly where it is one of them
        through = run_only.allows(blank + command + blank, takes, "/p", "/w")
        self.assertEqual(through, command in takes)


class TestWriteOnly(unittest.TestCase):
    @given(st.lists(NAMES, min_size=1, max_size=3), st.lists(NAMES, min_size=1, max_size=3))
    def test_a_file_goes_through_only_where_it_lies_in_the_output_named(self, folder, path):
        # Given: write_only naming a folder, and a file named from the folder the call is made in
        output, file = os.path.join(*folder), os.path.join(*path)
        # When: it is judged
        through = write_only.allows(file, [output], "/p", "/nowhere")
        # Then: it goes through exactly where its names begin with the folder's
        self.assertEqual(through, path[: len(folder)] == folder)


if __name__ == "__main__":
    unittest.main()
