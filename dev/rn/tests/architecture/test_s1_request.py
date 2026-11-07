"""S1 of dev/rn/architecture.md, a request, one test for each of its paths: the user types /rn:up
with what they want, tree.py makes the run's folder and cuts the planner's start, the planner
drafts the goal and commits it on the work's branch, and the main conversation puts the goal to
the user. rn's guard runs real, by its hook entries, through Lane's double of Claude Code."""

from __future__ import annotations

import json
import os
from unittest import mock

import helpers
from helpers import GOAL, RUN, repository, runs


class Request(helpers.FlowTest):
    def test_the_goal_drafted_from_the_request_is_put_to_the_user(self):
        # Given: the user types /rn:up with what they want, and the main conversation hands it
        lines = self.begins()
        self.assertTrue(lines[-1].startswith("rn: Start `rn:planner`."), lines)
        with mock.patch.object(runs, "today", return_value="20261108"):
            said = self.hands({"request": "tidy dry run"})
        self.assertIn(f"the change for {RUN} is kept", said)
        # When: the main conversation starts the planner with its cut, which drafts the goal,
        # writes it, and commits
        planner, values = self.cut_and_start("planner")
        self.assertEqual(values["run"], RUN)
        printed = self.plans(
            planner,
            values,
            {
                "grounds": "The goal drafted from the request.",
                "nodes": [{"id": "goal", "decided": GOAL, "by": "maker"}],
            },
        )
        self.assertEqual(self.gave(printed), "asks")
        self.gives(planner, "asks")
        # Then: the run ends, the goal committed on the work's branch
        self.assertEqual(self.ends(planner), ["rn: planner gave `asks`. Start no more subagents."])
        self.assertEqual(
            repository.ran("git", "branch", "--show-current"), "rn/20261108-tidy-dry-run"
        )
        self.assertEqual(
            json.loads(repository.committed(RUN, runs.tree_path(RUN)) or "{}")["goal"]["by"],
            "maker",
        )
        # And: the main conversation reads the goal to confirm, which it puts to the user
        self.assertEqual(
            self.main_runs("points"), f"Run: {RUN}\nThe goal, to confirm, at goal: {GOAL}\n"
        )
        self.assertTrue(self.claude.end_turn().made)

    def test_a_start_with_other_text_than_the_cut_is_stopped(self):
        self.begins()
        with mock.patch.object(runs, "today", return_value="20261108"):
            self.hands({"request": "tidy dry run"})
        printed = self.main_runs("start", "planner")
        told = self.claude.start(None, self.new("planner"), printed + "\nAnd make the README too.")
        self.assertFalse(told.made)
        self.assertIn("printed as its prompt, word for word", told.reason())

    def test_the_planner_writes_nothing_but_its_edit(self):
        self.begins()
        with mock.patch.object(runs, "today", return_value="20261108"):
            self.hands({"request": "tidy dry run"})
        planner, _ = self.cut_and_start("planner")
        told = self.does(
            planner, "Write", file_path=os.path.join(self.repo, runs.tree_path(RUN)), content="{}"
        )
        self.assertFalse(told.made)
        self.assertIn("Write only", told.reason())
