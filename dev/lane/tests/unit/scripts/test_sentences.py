"""The cases of sentences.py's contract: the lanes' sentences put into a part's steps, taken out of
them, and brought to the current wording, every other word left as it was."""

from helpers import sentences, step, testing

TEXT = "# writer\n\n1. Read\n   the file.\n2. Write it.\n\nAfter.\n"


def said(text, adds, drops=None):
    return sentences.said(text, step.numbered(text), adds, drops or {})


class TestSaid(testing.FolderTest):
    def test_a_sentence_ends_its_step(self):
        self.assertEqual(
            said(TEXT, {2: ["Write only `a`."]}),
            "# writer\n\n1. Read\n   the file.\n2. Write it. Write only `a`.\n\nAfter.\n",
        )

    def test_a_sentence_ends_the_last_line_of_a_step_of_several_lines(self):
        self.assertEqual(
            said(TEXT, {1: ["Read `a` to its end."]}),
            "# writer\n\n1. Read\n   the file. Read `a` to its end.\n2. Write it.\n\nAfter.\n",
        )

    def test_several_sentences_end_their_step_in_their_order(self):
        self.assertEqual(
            said("1. Do.\n", {1: ["A.", "B."]}),
            "1. Do. A. B.\n",
        )

    def test_a_sentence_the_step_says_already_is_said_once(self):
        self.assertEqual(said("1. Do. A.\n", {1: ["A."]}), "1. Do. A.\n")

    def test_a_sentence_dropped_is_taken_out_with_the_blank_before_it(self):
        self.assertEqual(said("1. Do. A. Then.\n", {}, {1: ["A."]}), "1. Do. Then.\n")

    def test_a_sentence_dropped_that_the_step_doesnt_say_leaves_it(self):
        self.assertEqual(said("1. Do.\n", {}, {1: ["A."]}), "1. Do.\n")

    def test_a_sentence_dropped_that_begins_another_dropped_one_takes_neither_apart(self):
        self.assertEqual(
            said("1. Do. End. Then more.\n", {1: ["End. Then more."]}, {1: ["End."]}),
            "1. Do. End. Then more.\n",
        )

    def test_a_sentence_dropped_and_added_moves_to_the_end(self):
        self.assertEqual(said("1. A. Do.\n", {1: ["A."]}, {1: ["A."]}), "1. Do. A.\n")

    def test_a_step_with_no_sentence_given_is_left_as_it_was(self):
        self.assertEqual(said(TEXT, {}), TEXT)


class TestReworded(testing.FolderTest):
    def test_an_earlier_wording_is_put_in_the_current_one_in_its_place(self):
        text = "1. Do. Old. Then.\n"
        self.assertEqual(
            sentences.reworded(text, step.numbered(text), [("Old.", "New.")]),
            "1. Do. New. Then.\n",
        )

    def test_a_current_sentence_that_an_earlier_one_begins_is_left_as_it_is(self):
        text = "1. Do. End. Then more.\n"
        self.assertEqual(
            sentences.reworded(text, step.numbered(text), [("End.", "End. Then more.")]), text
        )

    def test_words_outside_the_steps_are_left_as_they_were(self):
        text = "Old.\n\n1. Do.\n"
        self.assertEqual(sentences.reworded(text, step.numbered(text), [("Old.", "New.")]), text)
