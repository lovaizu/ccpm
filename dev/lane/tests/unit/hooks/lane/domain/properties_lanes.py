"""Property-based tests of the lanes: a command goes through only where it is one named, the blanks
around it aside, and a file only where it lies in an output named; a lane's takes fill its places
in order, none lost; and an item's ID is answered only by itself, standing as a word of its own; on
many inputs Hypothesis makes, new on every run, CI included."""

import os
import string
import unittest

from helpers import every_item, lanes, run_only, testing, write_only

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


class TestPlaces(unittest.TestCase):
    @given(st.sampled_from(sorted(lanes.LANES)), st.lists(COMMANDS, min_size=2, max_size=5))
    def test_takes_fill_the_places_in_order_none_lost(self, lane, takes):
        # Given: a lane and two or more takes
        # When: they are put in its places
        placed = lanes.placed(lane, takes)
        # Then: read in the order of the places, they are the takes, each place holding one or more
        self.assertEqual([t for p in lanes.places(lane) for t in placed[p]], takes)
        self.assertTrue(all(placed.values()))


# An ID as the items port reads one: capitals, a hyphen or not, and a number.
IDS = st.from_regex(r"[A-Z]{1,2}-?[0-9]{1,3}", fullmatch=True)


class TestEveryItem(unittest.TestCase):
    @given(IDS, IDS, st.sampled_from(["", " ", ": ", "\n"]))
    def test_an_id_is_answered_only_by_itself(self, key, other, after):
        # Given: an answer naming one ID, followed by a blank, a colon, a line break, or a word
        # run on to it
        # When: an ID is looked for in it
        # Then: it is found only where it is the same, standing as a word of its own
        found = every_item.stands(key, f"{other}{after}done")
        self.assertEqual(found, key == other and after != "")


if __name__ == "__main__":
    unittest.main()
