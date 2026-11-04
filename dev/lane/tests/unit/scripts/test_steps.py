"""Each step of a subagent as lay.py writes it: the sentence of each lane laid there before that
the proposal no longer lays taken out, each new sentence put at the end of the step, the rest as
it was; and the steps lay.py writes, with those whose lanes are all taken out."""

import unittest

import helpers
from helpers import steps

LINES = [
    "## Steps\n",
    "\n",
    "1. Read.\n",
    "2. Write the entries,\n",
    "   one a line.\n",
    "   - Out: e\n",
]


class TestReadAsLaid(unittest.TestCase):
    def test_each_sentence_is_put_at_the_end_of_the_steps_text(self):
        # Given: step 2 going on in a second line, with a list under it
        given = {"span": (3, 5), "lanes": helpers.STEPS[1]["lanes"], "gone": []}
        # When: it is read as laid
        # Then: the sentence ends its text, on its last line, the list left as it is
        self.assertEqual(
            steps.read_as_laid(LINES, given),
            ["2. Write the entries,\n", f"   one a line. {helpers.WRITE}\n"],
        )

    def test_a_sentence_the_step_says_already_is_not_put_in_again(self):
        # Given: step 2 saying write_only's sentence already
        lines = [f"2. Write. {helpers.WRITE}\n"]
        given = {"span": (0, 1), "lanes": helpers.STEPS[1]["lanes"], "gone": []}
        # When: it is read as laid
        # Then: it is as it was
        self.assertEqual(steps.read_as_laid(lines, given), lines)

    def test_a_sentence_said_on_a_line_before_the_last_is_not_put_in_again(self):
        # Given: step 2 saying write_only's sentence on its first line, going on in a second
        lines = [f"2. Write. {helpers.WRITE}\n", "   One a line.\n"]
        given = {"span": (0, 2), "lanes": helpers.STEPS[1]["lanes"], "gone": []}
        # When: it is read as laid
        # Then: it is as it was
        self.assertEqual(steps.read_as_laid(lines, given), lines)

    def test_a_sentence_gone_is_taken_out_and_a_new_one_put_in(self):
        # Given: step 2 saying run_only's sentence, which the proposal no longer lays there
        lines = [f"2. Write. {helpers.RUN}\n"]
        given = {"span": (0, 1), "lanes": helpers.STEPS[1]["lanes"], "gone": [helpers.RUN]}
        # When: it is read as laid
        # Then: the old sentence is gone, the new one in its place at the end
        self.assertEqual(steps.read_as_laid(lines, given), [f"2. Write. {helpers.WRITE}\n"])


# writer's last step laying its result command, and the step saying the sentence in a wording lane
# never laid.
ENDS = [{"lane": "result", "takes": [f"{helpers.GIVE} writer written"]}]
NEVER = f"Finish by running `{helpers.GIVE} writer written`."


class TestReworded(unittest.TestCase):
    def test_a_sentence_in_an_earlier_wording_is_put_in_the_current_one(self):
        # Given: writer's last step saying its result sentence in the wording laid before
        lines = [f"4. Reply. {helpers.END_WRITER_EARLIER}\n"]
        given = {"span": (0, 1), "lanes": ENDS}
        # When: it is reworded
        # Then: it says the sentence in the current wording, in the same place
        self.assertEqual(steps.reworded(lines, given), [f"4. Reply. {helpers.END_WRITER}\n"])

    def test_a_sentence_in_its_current_wording_is_left_as_it_is(self):
        # Given: the step saying the current wording, which begins with the earlier one
        lines = [f"4. Reply. {helpers.END_WRITER}\n"]
        given = {"span": (0, 1), "lanes": ENDS}
        # When: it is reworded
        # Then: it is as it was
        self.assertEqual(steps.reworded(lines, given), lines)

    def test_a_wording_lane_never_laid_is_not_taken_for_an_earlier_one(self):
        # Given: the step saying the result command in words lane never laid
        lines = [f"4. Reply. {NEVER}\n"]
        given = {"span": (0, 1), "lanes": ENDS}
        # When: it is reworded
        # Then: it is as it was
        self.assertEqual(steps.reworded(lines, given), lines)

    def test_an_earlier_wording_on_a_line_before_the_last_is_put_in_the_current_one_there(self):
        # Given: the step saying the earlier wording on its first line, going on in a second
        lines = [f"4. Reply. {helpers.END_WRITER_EARLIER}\n", "   One a line.\n", "5. Rest.\n"]
        given = {"span": (0, 2), "lanes": ENDS}
        # When: it is reworded
        # Then: the first line says the current wording, the second as it was, and no line out of
        # the step is given
        self.assertEqual(
            steps.reworded(lines, given), [f"4. Reply. {helpers.END_WRITER}\n", "   One a line.\n"]
        )

    def test_a_step_read_as_laid_has_an_earlier_wording_replaced_not_added_beside(self):
        # Given: the step saying the earlier wording, laid again with the same command
        lines = [f"4. Reply. {helpers.END_WRITER_EARLIER}\n"]
        given = {"span": (0, 1), "lanes": ENDS, "gone": []}
        # When: it is read as laid
        # Then: it says the current wording once, in place of the earlier
        self.assertEqual(steps.read_as_laid(lines, given), [f"4. Reply. {helpers.END_WRITER}\n"])

    def test_a_sentence_gone_in_an_earlier_wording_is_taken_out(self):
        # Given: the step saying the earlier wording of a result the proposal no longer lays
        lines = [f"4. Reply. {helpers.END_WRITER_EARLIER}\n"]
        gone = [helpers.END_WRITER, helpers.END_WRITER_EARLIER]
        given = {"span": (0, 1), "lanes": [], "gone": gone}
        # When: it is read as laid
        # Then: the sentence is gone from it
        self.assertEqual(steps.read_as_laid(lines, given), ["4. Reply.\n"])


class TestStepsLaid(unittest.TestCase):
    def agent(self, laid_steps: list) -> dict:
        """writer as the proposal gives it, with the lines of the README's writer laid."""
        lines = helpers.LAID.splitlines(keepends=True)
        given = [{**s, "span": (7 + s["step"], 8 + s["step"])} for s in laid_steps]
        return {"name": "writer", "lines": lines, "steps": given}

    def test_the_proposals_steps_are_laid_with_what_is_gone_from_each(self):
        # Given: run_only laid before on step 2, and a proposal laying write_only alone there
        before = {"writer": [helpers.STEPS[0]]}
        agent = self.agent([{"step": 2, "lanes": helpers.STEPS[1]["lanes"]}])
        # When: the steps to lay are found
        found = steps.steps_laid(before, agent)
        # Then: step 2 is laid, with run_only's sentence gone from it
        self.assertEqual([(s["step"], s["gone"]) for s in found], [(2, [helpers.RUN])])

    def test_a_step_whose_lanes_are_all_left_out_is_laid_with_none(self):
        # Given: the README's lanes laid before, and a proposal laying step 3 alone
        before = {"writer": helpers.STEPS}
        agent = self.agent([helpers.STEPS[1]])
        # When: the steps to lay are found
        found = steps.steps_laid(before, agent)
        # Then: step 2 is laid too, with no lane and its sentence gone, after the proposal's
        self.assertEqual(
            [(s["step"], s["lanes"], s["gone"]) for s in found],
            [(3, helpers.STEPS[1]["lanes"], []), (2, [], [helpers.RUN])],
        )
        self.assertEqual(found[1]["span"], (9, 10))

    def test_a_sentence_gone_is_taken_out_in_its_current_wording_then_each_earlier(self):
        # Given: writer's result laid before on step 4, and a proposal laying none there
        before = {"writer": [{"step": 4, "lanes": ENDS}]}
        lines = helpers.WRITER_LAID.splitlines(keepends=True)
        agent = {"name": "writer", "lines": lines, "steps": []}
        # When: the steps to lay are found
        found = steps.steps_laid(before, agent)
        # Then: step 4 is laid with no lane, its sentence gone in the current wording and the
        # earlier, the current first, as the earlier begins it
        gone = [helpers.END_WRITER, helpers.END_WRITER_EARLIER]
        self.assertEqual([(s["step"], s["lanes"], s["gone"]) for s in found], [(4, [], gone)])

    def test_a_step_laid_before_that_the_file_no_longer_has_is_left_out(self):
        # Given: a lane laid before on step 9, which writer's file no longer has
        before = {"writer": [{"step": 9, "lanes": helpers.STEPS[0]["lanes"]}]}
        # When: the steps to lay are found for the README's proposal
        found = steps.steps_laid(before, self.agent(helpers.STEPS))
        # Then: they are the proposal's alone
        self.assertEqual([s["step"] for s in found], [2, 3])


if __name__ == "__main__":
    unittest.main()
