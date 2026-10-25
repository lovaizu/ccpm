"""follow_next: once a script the lane takes has printed a move, one JSON line of a tool and its
input, each call, and the subagent's end, is a drift until a call is that tool with each field
printed equal; held from the calls the subagent made before, on a tool call and as the subagent is
about to end. Every other call, and end, is not."""

import json
import unittest

import helpers
from helpers import follow_next
from test_guard import GuardTest

# The script the lane takes, as a step names it, and a run of it as the AI writes it.
TAKES = ["scripts/turn.py next"]
NEXT = "python3 /home/u/.claude/plugins/turn/scripts/turn.py next /tmp/run"
# The move it prints: a Bash call of a command, and the line it prints it on.
MOVE = {"tool": "Bash", "input": {"command": "git status"}}
LINE = json.dumps(MOVE)


def ran(output=LINE, command=NEXT):
    """A Bash call of the command in the record, which gave back the output."""
    return ("Bash", {"command": command}, output)


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


class TestDrift(FollowNextTest):
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
        again = ran(json.dumps({"tool": "Bash", "input": {"command": "git push"}}))
        # When: the subagent takes the first move again
        # Then: it is a drift, as the last move printed is due
        self.assertTrue(self.drifts([ran(), helpers.bash("git status"), again]))

    def test_the_same_move_printed_again_after_it_was_taken_is_due_again(self):
        # Given: the script run and its move taken, then run again, printing the same move
        calls = [ran(), helpers.bash("git status"), ran()]
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


class TestLetThrough(FollowNextTest):
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
        move = {"tool": "Agent", "input": {"subagent_type": "turn:maker", "prompt": "Make x."}}
        # When: the subagent starts that agent
        # Then: it is no drift
        self.assertFalse(self.drifts([ran(json.dumps(move))], "Agent", move["input"]))

    def test_the_move_printed_after_other_lines_is_read(self):
        # Given: the script run, having printed the move after a line of its own
        # When: the subagent takes the move
        # Then: it is no drift
        self.assertFalse(self.drifts([ran(f"Next move:\n{LINE}\n")]))

    def test_any_call_once_the_move_was_taken_is_no_drift(self):
        # Given: the script run and its move taken
        # When: the subagent makes any other call
        # Then: it is no drift
        self.assertFalse(self.drifts([ran(), helpers.bash("git status")], given={"command": "ls"}))

    def test_with_no_move_printed_any_call_is_no_drift(self):
        for what, calls in {
            "the script not run": [helpers.bash("ls")],
            "the script run with other words": [ran(command=NEXT.replace("next", "given"))],
            "nothing printed back yet": [ran("")],
            "no JSON printed": [ran("Exit code 1\nturn.py: no run")],
            "JSON of no object": [ran("[1]")],
            "a move of no tool": [ran(json.dumps({"input": {}}))],
            "a move whose tool is no text": [ran(json.dumps({"tool": 1, "input": {}}))],
            "a move of no input object": [ran(json.dumps({"tool": "Bash", "input": "ls"}))],
        }.items():
            with self.subTest(what=what):
                # Given: no move printed by the script
                # When: the subagent makes any call
                # Then: it is no drift
                self.assertFalse(self.drifts(calls, given={"command": "ls"}))


class TestEnd(FollowNextTest):
    """follow_next as the subagent is about to end."""

    def test_ending_before_the_move_printed_is_taken_drifts(self):
        for what, calls in {
            "right after the print": [ran()],
            "after another call": [ran(), helpers.bash("git diff")],
            "after the move of the run before": [ran(), helpers.bash("git status"), ran()],
        }.items():
            with self.subTest(what=what):
                # Given: the script run, having printed a move not taken since
                # When: the subagent is about to end
                # Then: it is a drift, as the move is its next
                self.assertTrue(self.ends(calls))

    def test_ending_with_no_move_due_is_no_drift(self):
        for what, calls in {
            "the move taken": [ran(), helpers.bash("git status")],
            "the script not run": [helpers.bash("ls")],
            "the script run, printing no move": [ran('{"returned": "r.json"}')],
            "the script run again, printing no move": [ran(), ran('{"asked": "r.json"}')],
        }.items():
            with self.subTest(what=what):
                # Given: no move printed by the script left to take
                # When: the subagent is about to end
                # Then: it is no drift
                self.assertFalse(self.ends(calls))


class TestGuard(GuardTest):
    """follow_next laid on step 2 of changelog-writer, run as Claude Code runs the hook."""

    FOLLOW = "Take the next move `scripts/turn.py next` printed."

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

    def test_ending_once_the_move_is_taken_ends(self):
        # Given: changelog-writer's record of the script run and the move taken
        self.record([ran(), helpers.bash("git status")])
        # When: it is about to end
        # Then: it ends, nothing said
        self.assertEqual(self.ended(), ("", ""))


if __name__ == "__main__":
    unittest.main()
