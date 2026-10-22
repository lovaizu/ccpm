"""as_printed: once a command the lane takes has run and printed, a hand-on, an Agent call's prompt or
a SendMessage's message, is a drift until one holds what it printed word for word, a heading line
beside it allowed; held from the subagent's record. Every other call is not."""

import json
import unittest

import helpers
from helpers import as_printed, call
from test_guard import GuardTest

# The command the lane takes, as lane:up's step names it, run as the AI writes it once Claude Code
# has put lane's folder in for `${CLAUDE_PLUGIN_ROOT}`.
TAKES = ["lay.py print"]
PRINT = "python3 /home/u/.claude/plugins/lane/scripts/lay.py print /home/u/data/notes.json"
# What it printed, as the Bash tool gives it back, and a heading lane:up puts above it.
OUTPUT = "Lanes on step 3 of changelog-writer:\n  run: Do not run `git push`.  hook hands_off\n"
HEADING = "lane:up proposes these lanes; send OK or what to change."


def printed(output=OUTPUT, command=PRINT, failed=False):
    """A Bash call of the command in the record, which gave back the output, failed or not."""
    return ("Bash", {"command": command}, output, failed)


def send(message):
    """A SendMessage call of the message to the main conversation, in the record."""
    return ("SendMessage", {"to": "main", "message": message, "summary": "s"}, '{"success":true}')


class AsPrintedTest(helpers.PluginTest):
    def drifts(self, calls, message, tool="SendMessage", takes=TAKES):
        """Whether a hand-on of the message, after the calls in the subagent's record, drifts."""
        self.record(calls)
        field = call.HANDS.get(tool, "command")
        given = {"to": "main", "message": message} if tool == "SendMessage" else {field: message}
        return as_printed.drifts(call.read(self.called(tool, given)), takes)


class TestDrift(AsPrintedTest):
    def test_a_hand_on_of_something_else_after_the_print_drifts(self):
        for tool in ("SendMessage", "Agent"):
            with self.subTest(tool=tool):
                # Given: the command run, having printed
                # When: the subagent hands on, by SendMessage or the Agent tool, something else
                # Then: it is a drift
                self.assertTrue(self.drifts([printed()], "lane:up proposes hands_off.", tool))

    def test_the_print_changed_or_with_more_than_one_line_beside_it_drifts(self):
        for what, message in {
            "a word changed": OUTPUT.replace("push", "commit"),
            "two lines beside it": f"{HEADING}\n{OUTPUT}\nSay OK.",
            "a code fence around it": f"```\n{OUTPUT}```",
            "nothing": "",
        }.items():
            with self.subTest(what=what):
                # Given: the command run, having printed
                # When: the subagent hands on the print so
                # Then: it is a drift
                self.assertTrue(self.drifts([printed()], message))

    def test_a_hand_on_after_one_stopped_drifts_still(self):
        # Given: the command run, then a hand-on of something else, stopped
        calls = [printed(), send("lane:up proposes hands_off.")]
        # When: the subagent hands on something else again
        # Then: it is a drift still
        self.assertTrue(self.drifts(calls, "lane:up proposes hands_off on step 3."))

    def test_a_run_after_the_print_was_handed_on_is_due_again(self):
        # Given: the command run and its print handed on, then run again, printing anew
        calls = [printed(), send(OUTPUT), printed(OUTPUT.replace("push", "commit"))]
        # When: the subagent hands on the first print
        # Then: it is a drift, as the last print is due
        self.assertTrue(self.drifts(calls, OUTPUT))

    def test_the_same_print_run_again_after_it_was_handed_on_is_due_again(self):
        # Given: the command run and its print handed on, then run again, printing the same
        calls = [printed(), send(OUTPUT), printed()]
        # When: the subagent hands on something else
        # Then: it is a drift, as the hand-on before was of the run before
        self.assertTrue(self.drifts(calls, "lane:up asks: is that all?"))

    def test_a_message_of_no_text_drifts(self):
        # Given: the command run, having printed
        self.record([printed()])
        event = self.called("SendMessage", {"to": "main", "message": {"type": "shutdown"}})
        # When: the subagent sends a message of no text
        # Then: it is a drift
        self.assertTrue(as_printed.drifts(call.read(event), TAKES))


class TestLetThrough(AsPrintedTest):
    def test_the_print_handed_on_as_it_is_is_no_drift(self):
        for what, message in {
            "alone": OUTPUT,
            "without its last line break": OUTPUT.rstrip("\n"),
            "under a heading": f"{HEADING}\n{OUTPUT}",
            "under a heading and a blank line": f"{HEADING}\n\n{OUTPUT}",
            "above a line": f"{OUTPUT}\nSend OK or what to change.",
        }.items():
            with self.subTest(what=what):
                # Given: the command run, having printed
                # When: the subagent hands on the print so
                # Then: it is no drift
                self.assertFalse(self.drifts([printed()], message))

    def test_the_print_under_a_heading_that_holds_it_too_is_held(self):
        # Given: a print of `0`, as Hypothesis found it, under a heading `00` holding it too
        # When: whether the hand-on holds the print is read
        # Then: it does, the print read after the heading
        self.assertTrue(as_printed.holds("00\n0", "0"))

    def test_the_print_handed_on_by_the_agent_tool_is_no_drift(self):
        # Given: the command run, having printed
        # When: the subagent starts an agent with the print as its prompt
        # Then: it is no drift
        self.assertFalse(self.drifts([printed()], OUTPUT, "Agent"))

    def test_a_print_given_back_among_blanks_is_held_without_them(self):
        # Given: the command run, given back with blank lines around what it printed
        # When: the subagent hands on the print alone
        # Then: it is no drift
        self.assertFalse(self.drifts([printed(f"\n\n{OUTPUT}\n\n")], OUTPUT))

    def test_any_hand_on_once_the_print_was_handed_on_is_no_drift(self):
        # Given: the command run and its print handed on
        calls = [printed(), send(f"{HEADING}\n{OUTPUT}")]
        # When: the subagent hands on something else, such as a point to ask
        # Then: it is no drift
        self.assertFalse(self.drifts(calls, "lane:up asks: is CHANGELOG.md the only file?"))

    def test_with_nothing_printed_to_hand_on_any_hand_on_is_no_drift(self):
        for what, calls in {
            "the command not run": [helpers.bash("ls")],
            "another command of the same script run": [
                printed(command=PRINT.replace("print", "write"))
            ],
            "the command failed": [
                printed("Exit code 1\nlay.py: the proposal names no plugin", failed=True)
            ],
            "the command printed nothing": [printed("(Bash completed with no output)")],
            "the command not back yet": [printed("")],
        }.items():
            with self.subTest(what=what):
                # Given: no print of the command left to hand on
                # When: the subagent hands on something else
                # Then: it is no drift
                self.assertFalse(self.drifts(calls, "lane:up found: the plugin names no agents."))

    def test_a_failed_run_after_a_print_handed_on_leaves_nothing_due(self):
        # Given: the command's print handed on, then the command run again, failing
        failed = printed("Exit code 1\nlay.py: there is no file", failed=True)
        # When: the subagent hands on something else
        # Then: it is no drift
        self.assertFalse(self.drifts([printed(), send(OUTPUT), failed], "lane:up found: x"))

    def test_the_print_of_any_command_taken_may_be_handed_on(self):
        # Given: a lane taking two commands, the second run, having printed
        takes = ["lay.py write", "lay.py print"]
        # When: the subagent hands on its print
        # Then: it is no drift
        self.assertFalse(self.drifts([printed()], OUTPUT, takes=takes))

    def test_a_call_that_hands_nothing_on_is_no_drift(self):
        # Given: the command run, having printed
        # When: the subagent runs a command
        # Then: it is no drift
        self.assertFalse(self.drifts([printed()], "ls", "Bash"))

    def test_with_no_record_found_any_hand_on_is_no_drift(self):
        # Given: no record of the subagent where Claude Code keeps it
        event = self.called("SendMessage", {"to": "main", "message": "x"})
        # When: it hands on
        # Then: it is no drift, as what it printed before is not known
        self.assertFalse(as_printed.drifts(call.read(event), TAKES))


class TestGuard(GuardTest):
    """as_printed laid on step 4 of changelog-writer, run as Claude Code runs the hook."""

    def setUp(self) -> None:
        super().setUp()
        laid = helpers.LAID.replace("wrote.\n", "wrote. Hand on `lay.py print` as it is.\n")
        self.write(self.agent_file, laid)
        self.record([printed()])

    def sent(self, message):
        """What the guard does on a SendMessage of the message after the print."""
        event = self.called("SendMessage", {"to": "main", "message": message})
        return self.guard(json.dumps(event), (helpers.AGENT, "4:as_printed:lay.py print"))

    def test_a_hand_on_of_something_else_is_stopped_with_the_sentence(self):
        # Given: changelog-writer's record of the command run, having printed
        # When: it sends something else
        # Then: the call is stopped, and the subagent told the sentence headed by the plugin
        expected = (2, "notes: Hand on `lay.py print` as it is.\n")
        self.assertEqual(self.sent("lane:up proposes hands_off."), expected)

    def test_the_print_handed_on_under_a_heading_goes_on(self):
        # Given: changelog-writer's record of the command run, having printed
        # When: it sends the print under a heading
        # Then: the call goes on, nothing said
        self.assertEqual(self.sent(f"{HEADING}\n{OUTPUT}"), (0, ""))


if __name__ == "__main__":
    unittest.main()
