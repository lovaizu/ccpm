"""S3 of dev/rn/architecture.md, picking up, one test for each of its paths: the user types /rn:up
alone in a new conversation, and tree.py cuts the planner's start from the runs under .rn/: none
with work left, more than one, or one, at a point open or ready to make. rn's guard runs real, by
its hook entries, through Lane's double of Claude Code."""

from __future__ import annotations

import helpers
from helpers import GOAL, RUN


class Pickup(helpers.FlowTest):
    def picks_up(self):
        """The user types /rn:up alone, and the main conversation starts the planner with its cut:
        the planner, its values, and the cut."""
        self.begins()
        printed = self.main_runs("start", "planner")
        planner = self.new("planner")
        self.starts(planner, printed)
        return planner, helpers.json.loads(printed.splitlines()[0]), printed

    def test_no_work_left_gives_done(self):
        planner, values, cut = self.picks_up()
        self.assertIsNone(values["run"])
        self.assertIn("rn has no work left to pick up", cut)
        self.gives(planner, "done")
        self.assertEqual(self.ends(planner), ["rn: planner gave `done`. Start no more subagents."])

    def test_more_than_one_run_left_asks_which(self):
        self.lays(helpers.walkthrough(), ".rn/20261107-tidy-readme")
        self.lays(helpers.walkthrough(), RUN)
        planner, _, cut = self.picks_up()
        self.assertIn(f"- .rn/20261107-tidy-readme: {GOAL}\n- {RUN}: {GOAL}", cut)
        self.gives(planner, "asks")
        self.assertEqual(self.ends(planner), ["rn: planner gave `asks`. Start no more subagents."])

    def test_one_run_left_at_a_point_open_picks_up_there(self):
        self.commits(helpers.decided(helpers.walkthrough(), 1, "Q6", "the list", None))
        planner, values, cut = self.picks_up()
        self.assertEqual(values["run"], RUN)
        self.assertIn("Give `asks`", cut)
        self.assertEqual(self.main_runs("status"), f'Picking up "{GOAL}" at 1. README.md.\n')
        self.assertEqual(self.gave(self.runs(planner, self.tree_command("commit", RUN))), "asks")
        self.gives(planner, "asks")
        self.assertEqual(self.ends(planner), ["rn: planner gave `asks`. Start no more subagents."])
        self.assertIn("- D1Q6-1 the list: open.", self.main_runs("points"))

    def test_a_run_named_picks_up_from_its_folder(self):
        tree = helpers.walkthrough()
        tree["deliverables"][0]["status"] = "doing"
        self.commits(tree)
        self.lays(helpers.walkthrough(), ".rn/20261107-tidy-readme")
        self.begins()
        self.hands({"run": RUN})
        planner, values = self.cut_and_start("planner")
        self.assertEqual(values["run"], RUN)
        self.assertEqual(self.gave(self.runs(planner, self.tree_command("commit", RUN))), "ready")
        self.gives(planner, "ready")
        self.assertTrue(
            self.ends(planner)[0].startswith("rn: planner gave `ready`. Start `rn:generator`.")
        )
