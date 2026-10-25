"""The steps the layer writes: the proposal printed for the building AI's OK, each step as it would
read; each lane's sentence put at the end of its step, and the sentences of lanes no longer laid
there taken out, the rest of the step as it was."""

import json
import os
import unittest

import helpers
from laying import ENTRY, LANES, PRINTED, PUSH, PUSHED, LayTest


class TestPrint(LayTest):
    def test_the_proposal_is_printed_as_the_building_ai_reads_it(self):
        # Given: the proposal of hands_off on step 3 of changelog-writer
        # When: it is printed
        # Then: the lane shows under its action with its hook, and the step as it would read
        self.assertEqual(self.lay("print", self.proposal_file), (0, PRINTED))

    def test_printing_changes_nothing(self):
        # Given: the proposal
        # When: it is printed
        self.lay("print", self.proposal_file)
        # Then: the subagent's file is as it was, no hooks are written, and the proposal is kept
        self.assertEqual(self.read(self.agent_file), helpers.STEPS)
        self.assertFalse(os.path.exists(os.path.join(self.plugin, "hooks")))
        self.assertTrue(os.path.exists(self.proposal_file))

    def test_each_step_is_printed_apart(self):
        # Given: lanes on two steps
        proposal = self.proposal()
        proposal["subagents"][0]["steps"].insert(0, {"step": 1, "lanes": LANES})
        self.propose(proposal)
        # When: it is printed
        # Then: each step is printed as one alone is, a blank line between them
        one = PRINTED.replace("step 3", "step 1").replace(
            "3. Write the new entries into `CHANGELOG.md`.",
            "1. Read the commits since the last release.",
        )
        self.assertEqual(self.lay("print", self.proposal_file), (0, one + "\n" + PRINTED))

    def test_lanes_of_several_actions_line_up(self):
        # Given: two lanes on one step, standing in for lanes of two actions
        two = [*LANES, {"lane": "hands_off", "takes": ["npm publish"]}]
        self.propose(self.proposal(two))
        # When: it is printed
        # Then: each lane is a line of its own, their hooks lined up
        self.assertIn(
            "  run: Do not run `git commit` or `git push`.  hook hands_off\n"
            "  run: Do not run `npm publish`.               hook hands_off\n",
            self.lay("print", self.proposal_file)[1],
        )

    def test_what_a_hook_holds_beyond_its_sentence_is_printed_beside_it(self):
        # Given: wait_for on step 3, taking the approval and two commands it holds back
        wait = [{"lane": "wait_for", "takes": ["OK", "lay.py write", "git push"]}]
        self.propose(self.proposal(wait))
        # When: it is printed
        # Then: the sentence shows the approval alone, and the commands held back follow its hook
        self.assertIn(
            "  wait: Do not go on until `OK`.  hook wait_for, holding back `lay.py write`,"
            " `git push`\n",
            self.lay("print", self.proposal_file)[1],
        )


class TestWriteStep(LayTest):
    def test_the_sentence_is_put_at_the_end_of_the_step(self):
        # Given: the proposal
        # When: it is written
        self.assertEqual(self.lay("write", self.proposal_file)[0], 0)
        # Then: step 3 ends with the sentence, before its Out line, the rest as it was
        self.assertEqual(
            self.read(self.agent_file),
            helpers.LAID,
        )

    def test_a_step_over_several_lines_gets_the_sentence_on_its_last(self):
        # Given: step 3 going on over a second line
        two_lines = helpers.STEPS.replace(
            "`CHANGELOG.md`.\n", "`CHANGELOG.md`,\n   newest first.\n"
        )
        self.write(self.agent_file, two_lines)
        # When: the proposal is printed and written
        printed = self.lay("print", self.proposal_file)[1]
        self.lay("write", self.proposal_file)
        # Then: the step reads with its first line as it was and the sentence after its last
        step = "3. Write the new entries into `CHANGELOG.md`,\n   newest first. " + helpers.SENTENCE
        self.assertTrue(printed.endswith("\n\n" + step + "\n"), printed)
        self.assertEqual(
            self.read(self.agent_file),
            two_lines.replace("newest first.\n", f"newest first. {helpers.SENTENCE}\n"),
        )

    def test_a_sentence_the_step_already_says_is_not_written_again(self):
        # Given: the proposal written once
        self.lay("write", self.proposal_file)
        laid = self.read(self.agent_file)
        self.propose(self.proposal())
        # When: it is written again
        self.lay("write", self.proposal_file)
        # Then: the step says the sentence once
        self.assertEqual(self.read(self.agent_file), laid)

    def test_a_sentence_said_on_a_line_before_the_steps_last_is_not_written_again(self):
        # Given: step 3 saying the sentence on its first line, going on over a second
        said = helpers.STEPS.replace(
            "`CHANGELOG.md`.\n", f"`CHANGELOG.md`. {helpers.SENTENCE}\n   Newest first.\n"
        )
        self.write(self.agent_file, said)
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: the step is as it was
        self.assertEqual(self.read(self.agent_file), said)


class TestLayAgain(LayTest):
    """Laying again: the sentence of each lane the subagent's hook held before and the proposal no
    longer lays on its step taken out of the step, the rest of it as it was."""

    def lay_again(self, proposal):
        """Writes the proposal of lane's README, then proposes the one given."""
        self.lay("write", self.proposal_file)
        self.propose(proposal)

    def lay_before(self, name, number):
        """Lays hands_off of lane's README on the step of the number of the subagent of the name,
        as hooks/lanes.json and hooks.json hold it once laid."""
        steps = [{"step": number, "lanes": LANES}]
        laid = {"subagents": [{"name": name, "steps": steps}]}
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)
        entry = json.loads(json.dumps(ENTRY).replace("changelog-writer", name))
        hooks = {"hooks": {"PreToolUse": [entry]}}
        self.write_json(os.path.join(self.plugin, "hooks", "hooks.json"), hooks)

    def test_a_lane_laid_again_taking_other_things_has_its_old_sentence_taken_out(self):
        # Given: hands_off laid on step 3 taking `git commit` and `git push`, proposed again taking
        # `git push` alone
        self.lay_again(self.proposal(PUSH))
        # When: it is printed and written
        printed = self.lay("print", self.proposal_file)[1]
        self.lay("write", self.proposal_file)
        # Then: the step says the new sentence alone, as printed, the rest as it was
        laid = helpers.STEPS.replace("`CHANGELOG.md`.\n", f"`CHANGELOG.md`. {PUSHED}\n")
        self.assertEqual(self.read(self.agent_file), laid)
        self.assertTrue(
            printed.endswith(f"\n\n3. Write the new entries into `CHANGELOG.md`. {PUSHED}\n"),
            printed,
        )

    def test_a_lane_on_a_step_the_proposal_no_longer_has_is_taken_out_of_it(self):
        # Given: hands_off laid on steps 1 and 3, proposed again on step 3 alone
        proposal = self.proposal()
        proposal["subagents"][0]["steps"].insert(0, {"step": 1, "lanes": LANES})
        self.propose(proposal)
        self.lay_again(self.proposal())
        # When: it is printed and written
        printed = self.lay("print", self.proposal_file)[1]
        self.lay("write", self.proposal_file)
        # Then: step 1 reads as before any lane was laid, shown so after step 3, and step 3 keeps
        # its sentence
        self.assertEqual(self.read(self.agent_file), helpers.LAID)
        self.assertTrue(
            printed.endswith(
                PRINTED
                + "\nNo lanes on step 1 of changelog-writer now, their sentences taken out:\n"
                "\n1. Read the commits since the last release.\n"
            ),
            printed,
        )

    def test_a_lane_laid_on_a_step_the_steps_no_longer_have_is_passed_over(self):
        # Given: hooks/lanes.json laying hands_off on step 9 of the subagent, which its Steps do not
        # have, and its hook
        self.lay_before("changelog-writer", 9)
        # When: the proposal is printed and written
        printed = self.lay("print", self.proposal_file)
        self.lay("write", self.proposal_file)
        # Then: step 3 alone is printed and written, the rest of the file as it was
        self.assertEqual(printed, (0, PRINTED))
        self.assertEqual(self.read(self.agent_file), helpers.LAID)

    def test_a_sentence_no_lane_of_the_subagent_laid_stays(self):
        # Given: step 3 saying the sentence, hooks/lanes.json laying its lane on step 3 of another
        # subagent alone, and hands_off proposed on step 3 taking `git push` alone
        self.write(self.agent_file, helpers.LAID)
        self.lay_before("other", 3)
        self.propose(self.proposal(PUSH))
        # When: it is written
        self.lay("write", self.proposal_file)
        # Then: the step keeps the sentence and gets the new one after it
        self.assertEqual(
            self.read(self.agent_file),
            helpers.LAID.replace(f"{helpers.SENTENCE}\n", f"{helpers.SENTENCE} {PUSHED}\n"),
        )

    def test_a_sentence_kept_by_the_proposal_stays_in_its_place(self):
        # Given: two lanes laid on step 3, proposed again with the first taking other things and
        # the second as it was
        two = [*LANES, {"lane": "hands_off", "takes": ["npm publish"]}]
        self.propose(self.proposal(two))
        self.lay_again(self.proposal([*PUSH, two[1]]))
        # When: it is written
        self.lay("write", self.proposal_file)
        # Then: the second's sentence stays where it was, the new one after it
        self.assertEqual(
            self.read(self.agent_file),
            helpers.STEPS.replace(
                "`CHANGELOG.md`.\n",
                f"`CHANGELOG.md`. Do not run `npm publish`. {PUSHED}\n",
            ),
        )


if __name__ == "__main__":
    unittest.main()
