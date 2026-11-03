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

    def test_a_sentence_gone_is_taken_out_and_a_new_one_put_in(self):
        # Given: step 2 saying run_only's sentence, which the proposal no longer lays there
        lines = [f"2. Write. {helpers.RUN}\n"]
        given = {"span": (0, 1), "lanes": helpers.STEPS[1]["lanes"], "gone": [helpers.RUN]}
        # When: it is read as laid
        # Then: the old sentence is gone, the new one in its place at the end
        self.assertEqual(steps.read_as_laid(lines, given), [f"2. Write. {helpers.WRITE}\n"])


class TestStepsLaid(unittest.TestCase):
    def agent(self, laid_steps: list) -> dict:
        """writer as the proposal gives it, with the lines of the README's writer laid."""
        lines = helpers.LAID.splitlines(keepends=True)
        given = [{**s, "span": (6 + s["step"], 7 + s["step"])} for s in laid_steps]
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
        self.assertEqual(found[1]["span"], (8, 9))

    def test_a_step_laid_before_that_the_file_no_longer_has_is_left_out(self):
        # Given: a lane laid before on step 9, which writer's file no longer has
        before = {"writer": [{"step": 9, "lanes": helpers.STEPS[0]["lanes"]}]}
        # When: the steps to lay are found for the README's proposal
        found = steps.steps_laid(before, self.agent(helpers.STEPS))
        # Then: they are the proposal's alone
        self.assertEqual([s["step"] for s in found], [2, 3])


if __name__ == "__main__":
    unittest.main()
