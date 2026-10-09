"""Every state of fw's task table can go on, or go back to the user: the call that leaves each state
is let through once the task's CCS holds what that step needs, and nothing the hooks do ever stops
the conductor from asking the user or ending its turn."""

import json
import os
import unittest

from support import FW, Repo, ccs


class Flow(Repo):
    def state(self):
        return ccs.state(os.path.join(self.root, ".mock/greeting"))

    def test_a_task_goes_from_fill_through_a_fix_and_a_recheck_to_judge(self):
        # Given a task with nothing done
        self.assertEqual(self.state(), "fill")
        self.write("make", self.ready("make"))
        # When the maker is started and agrees, then works
        self.turn("make", go=False)
        # Then
        self.assertEqual(self.state(), "align-make")
        self.update("make", "goal_orientation", ("agreed", "write it"))
        self.assertEqual(self.state(), "make")
        # When the maker makes the work
        self.write("make", self.ready("make"))
        self.turn("make", made="hello\n")
        self.assertEqual(self.state(), "align-use")
        # When the first user is aligned, then uses it
        self.write("use", self.ready("use"))
        self.turn("use", go=False)
        self.assertEqual(self.state(), "align-use")
        self.update("use", "goal_orientation", ("agreed", "read it"))
        self.assertEqual(self.state(), "use")
        self.write("use", self.ready("use"))
        self.turn("use")
        self.assertEqual(self.state(), "align-learn")
        # When the learner is aligned, then learns
        self.write("learn", self.ready("learn"))
        self.turn("learn", go=False)
        self.update("learn", "goal_orientation", ("agreed", "learn"))
        self.assertEqual(self.state(), "learn")
        self.write("learn", self.ready("learn"))
        self.turn("learn")
        self.assertEqual(self.state(), "judge")
        # When the conductor judges a difference and has it fixed
        self.write("make", self.ready("make", ("goal_orientation", "fix", "greeting.txt:1 no sender"),
                                                ("goal_orientation", "keep", "the greeting")))
        self.turn("make", made="hello\nfrom: mock\n")
        self.assertEqual(self.state(), "align-recheck")
        # When the first user rechecks the stumbled place
        self.write("use", self.ready("use", ("goal_orientation", "recheck", "greeting.txt:1")))
        self.turn("use", go=False)
        self.update("use", "goal_orientation", ("agreed", "redo line 1"))
        self.assertEqual(self.state(), "recheck")
        self.write("use", self.ready("use", ("goal_orientation", "recheck", "greeting.txt:1")))
        self.turn("use")
        self.assertEqual(self.state(), "align-learn")
        self.write("learn", self.ready("learn"))
        self.turn("learn")
        # Then the task is back at judge, and its result file can be written
        self.assertEqual(self.state(), "judge")
        self.assertEqual(self.pre("Write", {"file_path": ".mock/open/01-report-greeting.md"})[0], 0)

    def test_a_maker_that_returns_without_making_sends_the_task_back_to_fill(self):
        # Given a maker that replies to go without changing the work
        self.write("make", self.ready("make"))
        # When
        self.turn("make", made=None)
        # Then
        self.assertEqual(self.state(), "fill")
        self.write("make", self.ready("make"))
        self.assertEqual(self.pre("Agent", {"subagent_type": "fw:maker", "prompt": "request .mock/greeting/make.yaml"})[0], 0)

    def test_the_hooks_never_stop_asking_the_user_or_ending_a_turn(self):
        # Given fw's hooks
        with open(os.path.join(FW, "hooks", "hooks.json")) as f:
            hooks = json.load(f)["hooks"]
        # When they are read
        matchers = [h["matcher"] for h in hooks["PreToolUse"]]
        # Then they act on no turn end and no user prompt, and not on asking the user
        self.assertEqual(sorted(hooks), ["PreToolUse", "SubagentStop"])
        self.assertEqual(matchers, ["Agent|SendMessage|Write"])
        self.assertEqual(self.pre("AskUserQuestion", {"questions": []}), (0, "", ""))

    def test_writing_the_steering_while_waiting_for_the_user_is_never_stopped(self):
        # Given a task waiting for the user, or backing up to fix the steering with them
        self.write("make", self.ready("make"))
        # When the conductor writes the steering
        code = self.pre("Write", {"file_path": os.path.join(self.root, ".mock/steering.md")})[0]
        # Then
        self.assertEqual(code, 0)

    def test_every_state_a_task_can_be_in_tells_the_conductor_what_to_do_next(self):
        # Given the states the record can show, and what state.py says for each
        import state
        # When each is printed for a task in that state
        # Then each has its next step, and the task in fill is printed as such
        self.assertEqual(sorted(state.NEXT), sorted(["fill", "align-make", "make", "align-use", "use",
                                                     "align-recheck", "recheck", "align-learn", "learn", "judge"]))
        printed = self.run_state()
        self.assertTrue(printed.startswith("state: fill\nnext: Fill make.yaml"))

    def run_state(self):
        import io
        import runpy
        import sys
        from contextlib import redirect_stdout
        from unittest import mock
        out = io.StringIO()
        with mock.patch.object(sys, "argv", ["state.py", os.path.join(self.root, ".mock/greeting")]), redirect_stdout(out):
            runpy.run_path(os.path.join(FW, "scripts", "state.py"), run_name="__main__")
        return out.getvalue()


if __name__ == "__main__":
    unittest.main()
