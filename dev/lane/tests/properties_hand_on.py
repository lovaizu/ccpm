"""Property-based tests of the lanes on handing on and waiting: as_printed on any print and heading,
the move port on any move printed, wait_for on any approval; checked on many inputs Hypothesis
makes, new on every run, CI included."""

import json
import string
import unittest

from helpers import as_printed, ports, testing, wait_for

hypothesis = testing.hypothesis()
given = hypothesis.given
st = hypothesis.strategies

# What a command prints, as the lane holds it, blanks around it left out, and a line of text.
OUTPUTS = st.text(min_size=1).map(str.strip).filter(bool)
LINES = st.text().filter(lambda t: len(t.splitlines()) <= 1)
# A move: a tool's name and an input of text fields.
MOVES = st.tuples(st.text(min_size=1), st.dictionaries(st.text(), st.text()))
# An approval of word characters, and what may stand around it in a message.
APPROVALS = st.text(string.ascii_letters + string.digits, min_size=1, max_size=8)
AROUND = st.text(string.punctuation.replace("_", "") + " \n", max_size=5)


class TestAsPrinted(unittest.TestCase):
    @given(OUTPUTS, LINES)
    def test_any_print_under_any_heading_line_is_held(self, output, heading):
        # Given: any print, and any line of text
        # When: it is handed on alone, or under the line
        # Then: each holds the print
        for text in (output, f"{heading}\n{output}"):
            self.assertTrue(as_printed.holds(text, output), text)


class TestFollowNext(unittest.TestCase):
    @given(MOVES, st.lists(st.text().filter(lambda t: "\n" not in t and "\r" not in t)))
    def test_any_move_printed_last_is_read(self, move, before):
        # Given: any move, printed as one JSON line after any lines of text
        tool, given_input = move
        line = json.dumps({"tool": tool, "input": given_input})
        # When: the move is read from what was printed, at the move port
        # Then: it is the move printed
        found = ports.read("move", {"output": "\n".join([*before, line])})
        self.assertEqual(found, {"move": {"tool": tool, "input": given_input}})


class TestWaitFor(unittest.TestCase):
    @given(APPROVALS, AROUND, AROUND)
    def test_any_approval_as_words_of_their_own_approves(self, approval, before, after):
        # Given: any approval, in a message with no word character next to it
        # When: whether the message approves is read
        # Then: it does, in its own case or another
        for message in (f"{before}{approval}{after}", f"{before}{approval.swapcase()}{after}"):
            self.assertTrue(wait_for.approves(message, approval), message)

    @given(APPROVALS, st.sampled_from(string.ascii_letters + string.digits + "_"))
    def test_any_approval_inside_a_longer_word_does_not_approve(self, approval, letter):
        # Given: any approval, with a word character next to it
        # When: whether the message approves is read
        # Then: it does not
        for message in (f"{letter}{approval}", f"{approval}{letter}"):
            self.assertFalse(wait_for.approves(message, approval), message)


if __name__ == "__main__":
    unittest.main()
