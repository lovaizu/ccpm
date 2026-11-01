"""follow_next: held from the first run of a script the lane takes on. Once the script has printed a
move, one JSON line of a tool and its input, each call, and the subagent's end, is a drift until a
call is that tool with each field printed equal; once the move is taken, each call, and the end, is
a drift until the script runs again. A run of the script is never a drift, a run that fails changes
nothing of what is due, and once the last run printed no move the subagent is free; held from the
calls the subagent made before, on a tool call and as the subagent is about to end."""

import json
import unittest

import helpers
from helpers import follow_next
from test_guard import GuardTest

# The script the lane takes, as a step names it, and a run of it as the AI writes it.
TAKES = ["scripts/next.py go"]
NEXT = "python3 /home/u/.claude/plugins/notes/scripts/next.py go /tmp/run"
# The move it prints: a Bash call of a command, and the line it prints it on.
MOVE = {"tool": "Bash", "input": {"command": "git status"}}
LINE = json.dumps(MOVE)
# Another move it prints, and what it prints for no move.
PUSH = json.dumps({"tool": "Bash", "input": {"command": "git push"}})
NONE = "The work is done."
# The move taken, as the record holds it.
TAKEN = helpers.bash("git status")


def ran(output=LINE, command=NEXT):
    """A Bash call of the command in the record, which gave back the output."""
    return ("Bash", {"command": command}, output)


def failed(output=PUSH):
    """A run of the script in the record that failed, exiting other than 0, giving back the
    output."""
    return ("Bash", {"command": NEXT}, helpers.Failed(output))


class FollowNextTest(helpers.PluginTest):
    def drifts(self, calls, tool="Bash", given=None):
        """Whether a call of the tool with the input, after the calls in the record, drifts."""
        self.record(calls)
        given = {"command": "git status"} if given is None else given
        return follow_next.drifts(
            helpers.call_of(self.called(tool, given)), TAKES, helpers.NO_PLUGIN, helpers.ports.move
        )

    def ends(self, calls):
        """Whether the subagent drifts, about to end after the calls in its record."""
        self.record(calls)
        end = helpers.end_of(self.stopped("Done."))
        return follow_next.drifts(end, TAKES, helpers.NO_PLUGIN, helpers.ports.move)


class TestMoveDue(FollowNextTest):
    """A move printed by the last run, not taken since."""

    def test_a_call_other_than_the_move_printed_drifts(self):
        for what, (tool, given) in {
            "another command": ("Bash", {"command": "git diff"}),
            "another tool": ("Read", {"command": "git status"}),
            "yet another tool": ("Agent", {"command": "git status"}),
            "a field printed left out": ("Bash", {"description": "status"}),
        }.items():
            with self.subTest(what=what):
                # Given: the script run, having printed the move
                # When: the subagent's next call is not that move
                # Then: it is a drift
                self.assertTrue(self.drifts([ran()], tool, given))

    def test_another_call_after_one_stopped_drifts_still(self):
        # Given: the script run, then a call other than the move, stopped
        calls = [ran(), helpers.bash("git diff")]
        # When: the subagent makes another call other than the move
        # Then: it is a drift still
        self.assertTrue(self.drifts(calls, given={"command": "git log"}))

    def test_the_move_of_a_new_run_is_held_after_the_last_was_taken(self):
        # Given: the script run and its move taken, then run again, printing another move
        # When: the subagent takes the first move again
        # Then: it is a drift, as the last move printed is due
        self.assertTrue(self.drifts([ran(), TAKEN, ran(PUSH)]))

    def test_the_same_move_printed_again_after_it_was_taken_is_due_again(self):
        # Given: the script run and its move taken, then run again, printing the same move
        calls = [ran(), TAKEN, ran()]
        # When: the subagent makes another call
        # Then: it is a drift, as the move taken before was of the run before
        self.assertTrue(self.drifts(calls, given={"command": "ls"}))

    def test_a_move_printed_alone_over_lines_is_held(self):
        # Given: the script run, having printed the move alone, over several lines
        # When: the subagent's next call is not that move
        # Then: it is a drift, the print read as JSON as the run's values are
        self.assertTrue(self.drifts([ran(json.dumps(MOVE, indent=2))], given={"command": "ls"}))

    def test_the_last_move_printed_is_held(self):
        # Given: the script run, having printed two moves among other lines
        output = "\n".join(["moves:", json.dumps({"tool": "Read", "input": {}}), LINE, "done"])
        # When: the subagent takes the first
        # Then: it is a drift
        self.assertTrue(self.drifts([ran(output)], "Read", {}))

    def test_the_move_printed_taken_is_no_drift(self):
        for what, given in {
            "as printed": {"command": "git status"},
            "with fields not printed": {"command": "git status", "description": "status"},
        }.items():
            with self.subTest(what=what):
                # Given: the script run, having printed the move
                # When: the subagent's next call is the move
                # Then: it is no drift
                self.assertFalse(self.drifts([ran()], "Bash", given))

    def test_a_move_of_another_tool_taken_is_no_drift(self):
        # Given: the script run, having printed a move starting an agent
        move = {"tool": "Agent", "input": {"subagent_type": "notes:maker"}}
        # When: the subagent starts that agent, with fields not printed
        # Then: it is no drift
        given = {**move["input"], "prompt": "Make x."}
        self.assertFalse(self.drifts([ran(json.dumps(move))], "Agent", given))

    def test_the_move_printed_after_other_lines_is_read(self):
        # Given: the script run, having printed the move after a line of its own
        # When: the subagent takes the move
        # Then: it is no drift
        self.assertFalse(self.drifts([ran(f"Next move:\n{LINE}\n")]))


class TestRunDue(FollowNextTest):
    """The move printed by the last run taken, the script not run since."""

    def test_any_call_once_the_move_was_taken_drifts(self):
        for what, (tool, given) in {
            "another command": ("Bash", {"command": "ls"}),
            "the move again": ("Bash", {"command": "git status"}),
            "another tool": ("Read", {"file_path": "a"}),
        }.items():
            with self.subTest(what=what):
                # Given: the script run and its move taken
                # When: the subagent makes any call but a run of the script
                # Then: it is a drift, as the script is to be run again
                self.assertTrue(self.drifts([ran(), TAKEN], tool, given))

    def test_a_call_after_one_stopped_drifts_still(self):
        # Given: the script run, its move taken, then another call, stopped
        # When: the subagent makes another call
        # Then: it is a drift still
        self.assertTrue(self.drifts([ran(), TAKEN, helpers.bash("ls")], given={"command": "pwd"}))


class TestRun(FollowNextTest):
    """A run of the script, whatever is due."""

    def test_a_run_of_the_script_is_no_drift(self):
        for what, calls in {
            "before the first run": [],
            "with the move due": [ran()],
            "once the move is taken": [ran(), TAKEN],
            "once a run printed no move": [ran(NONE)],
        }.items():
            with self.subTest(what=what):
                # Given: the record of what is due
                # When: the subagent runs the script
                # Then: it is no drift
                self.assertFalse(self.drifts(calls, given={"command": NEXT}))

    def test_a_run_not_yet_back_leaves_the_move_due(self):
        # Given: the script run, having printed the move, then run again, the record holding that
        # run and not yet what it gave back, as Claude Code may write the call being checked
        # before its PreToolUse hook runs
        # When: the subagent makes another call
        # Then: it is a drift, as the move printed is due
        self.assertTrue(self.drifts([ran(), ran(None)], given={"command": "ls"}))


class TestFailedRun(FollowNextTest):
    """A run of the script that failed, exiting other than 0, changes nothing of what is due of
    the calls, and lets the subagent end, so its report of the failure reaches whoever started
    it."""

    def test_a_failed_run_leaves_what_was_due(self):
        for what, (calls, tool, given, drifts) in {
            "the move due, another call": ([ran()], "Bash", {"command": "ls"}, True),
            "the move due, the move": ([ran()], "Bash", {"command": "git status"}, False),
            "the run due": ([ran(), TAKEN], "Bash", {"command": "ls"}, True),
            "before the first run": ([], "Bash", {"command": "ls"}, False),
            "after a run printing no move": ([ran(NONE)], "Bash", {"command": "ls"}, False),
        }.items():
            with self.subTest(what=what):
                # Given: what was due, then a run of the script that failed, printing a move
                # When: the subagent makes a call
                # Then: it drifts as it would with no failed run
                self.assertEqual(self.drifts([*calls, failed()], tool, given), drifts)

    def test_ending_after_a_failed_last_run_is_no_drift(self):
        for what, calls in {
            "the move due": [ran(), failed()],
            "the run due": [ran(), TAKEN, failed()],
            "nothing due": [ran(NONE), failed()],
            "the first run failed": [failed()],
            "a call after the failed run": [ran(), TAKEN, failed(), helpers.bash("ls")],
        }.items():
            with self.subTest(what=what):
                # Given: what was due, then a run of the script that failed, the last run of it
                # When: the subagent is about to end
                # Then: it is no drift
                self.assertFalse(self.ends(calls))

    def test_ending_after_a_run_that_did_not_fail_since_a_failed_one_is_held(self):
        # Given: a run of the script that failed, then one printing a move
        # When: the subagent is about to end
        # Then: it is a drift, as the move is due
        self.assertTrue(self.ends([failed(), ran()]))


class TestFree(FollowNextTest):
    def test_with_no_move_printed_last_any_call_is_no_drift(self):
        for what, calls in {
            "the script not run": [helpers.bash("ls")],
            "the script run with other words": [ran(command=NEXT.replace("go", "given"))],
            "nothing printed back": [ran("")],
            "no JSON printed": [ran("Exit code 1\nnext.py: no run")],
            "JSON of no object": [ran("[1]")],
            "a move of no tool": [ran(json.dumps({"input": {}}))],
            "a move whose tool is no text": [ran(json.dumps({"tool": 1, "input": {}}))],
            "a move of no input object": [ran(json.dumps({"tool": "Bash", "input": "ls"}))],
            "the move taken, then a run printing none": [ran(), TAKEN, ran(NONE)],
        }.items():
            with self.subTest(what=what):
                # Given: no move printed by the script's last run, or no run
                # When: the subagent makes any call
                # Then: it is no drift
                self.assertFalse(self.drifts(calls, given={"command": "ls"}))


class TestEnd(FollowNextTest):
    """follow_next as the subagent is about to end."""

    def test_ending_with_a_move_or_a_run_due_drifts(self):
        for what, calls in {
            "right after the print": [ran()],
            "after another call": [ran(), helpers.bash("git diff")],
            "after the move of the run before": [ran(), TAKEN, ran()],
            "once the move is taken": [ran(), TAKEN],
            "before the script's first run": [helpers.bash("ls")],
            "with no call made": [],
        }.items():
            with self.subTest(what=what):
                # Given: the script run, having printed a move not taken since, or one taken with
                # the script not run since, or the script not yet run
                # When: the subagent is about to end
                # Then: it is a drift
                self.assertTrue(self.ends(calls))

    def test_ending_with_nothing_due_is_no_drift(self):
        for what, calls in {
            "the script run, printing no move": [ran('{"returned": "r.json"}')],
            "the move taken, the script run again, printing none": [ran(), TAKEN, ran(NONE)],
        }.items():
            with self.subTest(what=what):
                # Given: no move printed by the script left to take, and no run due
                # When: the subagent is about to end
                # Then: it is no drift
                self.assertFalse(self.ends(calls))


class TestGuard(GuardTest):
    """follow_next laid on step 2 of changelog-writer, run as Claude Code runs the hook."""

    FOLLOW = "Take each move `scripts/next.py go` prints, until it prints none."

    LAID = ((2, "follow_next", TAKES),)

    def setUp(self) -> None:
        super().setUp()
        self.record([ran()])

    def moved(self, command):
        """What the guard does on a Bash call of the command after the move printed."""
        event = self.called("Bash", {"command": command})
        return self.guard(json.dumps(event))

    def test_another_move_is_stopped_with_the_sentence(self):
        # Given: changelog-writer's record of the script run, having printed the move
        # When: it runs another command
        # Then: the call is stopped, and the subagent told the sentence headed by the plugin
        self.assertEqual(self.moved("git diff"), ("told", f"notes: {self.FOLLOW}"))

    def test_the_move_printed_goes_on(self):
        # Given: changelog-writer's record of the script run, having printed the move
        # When: it takes the move
        # Then: the call goes on, nothing said
        self.assertEqual(self.moved("git status"), ("", ""))

    def ended(self):
        """What the guard does as the subagent is about to end."""
        return self.guard(json.dumps(self.stopped("Done.")), entry="subagentstop.py")

    def test_ending_before_the_move_is_taken_is_kept_going_with_the_sentence(self):
        # Given: changelog-writer's record of the script run, having printed the move
        # When: it is about to end
        # Then: it is kept going, and told the sentence headed by the plugin
        self.assertEqual(self.ended(), ("told", f"notes: {self.FOLLOW}"))

    def test_ending_once_the_move_is_taken_is_kept_going_with_the_sentence(self):
        # Given: changelog-writer's record of the script run and the move taken
        self.record([ran(), TAKEN])
        # When: it is about to end
        # Then: it is kept going, and told the sentence headed by the plugin
        self.assertEqual(self.ended(), ("told", f"notes: {self.FOLLOW}"))

    def test_ending_once_the_script_printed_no_move_ends(self):
        # Given: changelog-writer's record of the script run, the move taken, and the script run
        # again, printing no move
        self.record([ran(), TAKEN, ran(NONE)])
        # When: it is about to end
        # Then: it ends, nothing said
        self.assertEqual(self.ended(), ("", ""))


if __name__ == "__main__":
    unittest.main()
