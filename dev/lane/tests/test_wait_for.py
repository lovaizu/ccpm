"""wait_for: a run of a command the lane holds back is a drift unless a message holding the approval
has reached the subagent since it last asked, by SendMessage or by a reply that ended its turn, read
from its record; every other call is not."""

import unittest

import helpers
from helpers import wait_for
from test_guard import GuardTest

# The approval and the command held back, as a step takes them, and a run of the command
# as the AI writes it.
TAKES = ["OK", "memo.py publish"]
PUBLISH = "python3 /home/u/.claude/plugins/memo/scripts/memo.py publish memo.md"
# The subagent asking its caller, by SendMessage.
ASK = (
    "SendMessage",
    {"to": "main", "message": "The memo is ready; may I publish it?"},
    '{"success":true}',
)
# The subagent asking by a reply that ends its turn.
REPLY = helpers.replied("The memo is ready; send OK to publish it.")


class WaitForTest(helpers.PluginTest):
    def drifts(self, calls, command=PUBLISH, takes=TAKES):
        """Whether a run of the command, after the calls and messages in the record, drifts."""
        self.record(calls)
        return wait_for.drifts(helpers.call_of(self.event(command)), takes, helpers.NO_PLUGIN)


class TestDrift(WaitForTest):
    def test_the_held_command_run_without_the_approval_drifts(self):
        for what, calls in {
            "no message since asking": [ASK],
            "a message without it": [ASK, helpers.from_main("Shorten the memo first.")],
            "the approval before asking again": [ASK, helpers.from_main("OK"), ASK],
            "the approval before a reply asking": [ASK, helpers.from_main("OK"), REPLY],
            "the approval inside a word": [ASK, helpers.from_main("BOOKED")],
        }.items():
            with self.subTest(what=what):
                # Given: the subagent's record of no approval since it last asked
                # When: it runs the command held back
                # Then: it is a drift
                self.assertTrue(self.drifts(calls))

    def test_a_command_held_back_as_the_step_writes_it_is_held(self):
        # Given: the command held back as the step writes it, with no approval since asking
        takes = ["OK", 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memo.py" publish']
        # When: the subagent runs it with its plugin's folder put in
        # Then: it is a drift
        self.assertTrue(self.drifts([ASK], takes=takes))

    def test_the_approval_in_the_prompt_drifts_once_the_subagent_has_asked(self):
        # Given: a subagent started with the approval in its prompt, which has asked since
        takes = ["steps", "memo.py publish"]
        # When: it runs the command held back
        # Then: it is a drift, as the prompt reached it before it asked
        self.assertTrue(self.drifts([ASK], takes=takes))

    def test_each_command_held_back_is_held(self):
        # Given: a lane holding back two commands, and no approval since asking
        takes = ["OK", "git commit", "git push"]
        # When: the subagent runs the second
        # Then: it is a drift
        self.assertTrue(self.drifts([ASK], "git push origin work", takes))

    def test_the_approval_in_the_words_of_main_alone_drifts(self):
        # Given: an approval that only the words Claude Code puts around a message hold
        takes = ["coordinator", "memo.py publish"]
        # When: the subagent runs the command held back after a message without it
        # Then: it is a drift
        self.assertTrue(self.drifts([ASK, helpers.from_main("Go on.")], takes=takes))


class TestLetThrough(WaitForTest):
    def test_the_held_command_run_after_the_approval_is_no_drift(self):
        for what, calls in {
            "from the main conversation": [ASK, helpers.from_main("OK, go on.")],
            "from another subagent": [ASK, helpers.from_subagent("OK")],
            "resuming it after a reply that asked": [REPLY, helpers.from_main("OK")],
            "in another case": [ASK, helpers.from_main("ok")],
            "before other messages": [ASK, helpers.from_main("OK"), helpers.from_main("Thanks.")],
        }.items():
            with self.subTest(what=what):
                # Given: the subagent's record of a message holding the approval since it asked
                # When: it runs the command held back
                # Then: it is no drift
                self.assertFalse(self.drifts(calls))

    def test_the_approval_in_the_prompt_before_any_ask_is_no_drift(self):
        # Given: a subagent started with the approval in its prompt, which has not asked
        takes = ["steps", "memo.py publish"]
        # When: it runs the command held back
        # Then: it is no drift, as the prompt reached it since it began
        self.assertFalse(self.drifts([helpers.bash("ls")], takes=takes))

    def test_a_command_not_held_back_is_no_drift(self):
        # Given: no approval since asking
        # When: the subagent runs another command of the same script
        # Then: it is no drift
        self.assertFalse(self.drifts([ASK], PUBLISH.replace("publish", "draft")))


class TestGuard(GuardTest):
    """wait_for laid on step 4 of changelog-writer, run as Claude Code runs the hook."""

    LAID = ((4, "wait_for", ["OK", "memo.py publish"]),)

    def written_after(self, calls):
        """What the guard does on a run of the command held back after the calls."""
        self.record(calls)
        return self.guard(self.stream(PUBLISH))

    def test_the_held_command_without_the_approval_is_stopped_with_the_sentence(self):
        # Given: changelog-writer's record of asking, and no answer since
        # When: it runs the command held back
        # Then: the call is stopped, and the subagent told the sentence, the approval alone
        self.assertEqual(self.written_after([ASK]), ("told", "notes: Do not go on until `OK`."))

    def test_the_held_command_after_the_approval_goes_on(self):
        # Given: changelog-writer's record of asking, and the approval sent back
        # When: it runs the command held back
        # Then: the call goes on, nothing said
        self.assertEqual(self.written_after([ASK, helpers.from_main("OK")]), ("", ""))


if __name__ == "__main__":
    unittest.main()
