"""S2 of dev/rn/architecture.md, a point settled, one test for each of its paths: the main
conversation reads the points open, puts the user's to them, and calls /rn:up with the change; the
planner writes each decision, lays out the plan where the goal is newly the user's, answers each
node the change touches, and commits, giving asks while a point is open and ready once none is.
rn's guard runs real, by its hook entries, through Lane's double of Claude Code."""

from __future__ import annotations

import helpers
from helpers import GOAL, RUN, repository, runs

PLAN = [
    {"id": "goal", "decided": GOAL, "by": "user"},
    {
        "after": "goal",
        "name": "the dry run in Walkthrough",
        "path": "README.md",
        "kind": "readme",
        "inputs": ["dev/product-vision.md"],
        "preconditions": [],
    },
    {
        "after": "README.md",
        "name": "the option --dry-run",
        "path": "tidy/cli.py",
        "kind": "code",
        "inputs": ["README.md"],
        "preconditions": [],
    },
    {"id": "goal", "decided": GOAL, "by": "user"},
]


class Point(helpers.FlowTest):
    def settles(self, change):
        """The main conversation calls /rn:up with the change, hands it, and starts the planner
        with its cut: the planner and its values."""
        lines = self.calls_up()
        self.assertTrue(lines[-1].startswith("rn: Start `rn:planner`."), lines)
        self.hands(change)
        return self.cut_and_start("planner")

    def test_the_goal_confirmed_lays_the_plan_and_its_first_point(self):
        # Given: the goal drafted and committed, which the user confirms
        self.commits(helpers.walkthrough("maker") | {"deliverables": []})
        planner, values = self.settles(
            {"run": RUN, "decisions": [{"at": "goal", "decided": GOAL, "by": "user"}]}
        )
        # When: the planner writes the goal as the user's, lays out the plan back from it with the
        # README's point open, and commits
        edit = {"grounds": "The plan, back from the goal.", "nodes": PLAN[:3]}
        point = {
            "grounds": "The README's point.",
            "nodes": [{"id": "D1Q6", "about": "the list", "decided": None}],
        }
        printed = self.plans(planner, values, edit, point)
        self.gives(planner, self.gave(printed))
        # Then: the run ends at asks, and the points show the plan and the point
        self.assertEqual(self.ends(planner), ["rn: planner gave `asks`. Start no more subagents."])
        said = self.main_runs("points")
        self.assertIn(
            "1. README.md: the dry run in Walkthrough\n2. tidy/cli.py: the option --dry-run", said
        )
        self.assertIn("- D1Q6-1 the list: open.", said)

    def test_a_point_settled_by_the_user_each_node_answered_gives_ready(self):
        # Given: the plan laid with the README's point open, which the user answers
        self.commits(helpers.decided(helpers.walkthrough(), 1, "Q6", "the list", None))
        planner, values = self.settles(
            {"run": RUN, "decisions": [{"at": "D1Q6-1", "decided": "each file", "by": "user"}]}
        )
        # When: the planner writes it, which lists each node it touches
        self.writes(
            planner,
            values["edit"],
            {
                "grounds": "The list.",
                "nodes": [{"id": "D1Q6-1", "decided": "each file", "by": "user"}],
            },
        )
        said = self.runs(planner, self.tree_command("write", RUN, values["edit"]))
        self.assertIn("goal, D1, D1Q6, D2", said)
        # And: Lane holds its end until it commits, which tree.py holds until it answers each
        self.assertIn(
            "deliver {run}` not run",
            self.claude.call(
                planner,
                "Bash",
                {
                    "command": f"python3 {helpers.RN}/hooks/lane/result.py planner asks",
                    "description": "d",
                },
            ).reason(),
        )
        answers = [{"id": n, "holds": True} for n in ("goal", "D1", "D1Q6", "D2")]
        printed = self.plans(
            planner,
            values,
            {"grounds": "Ready.", "nodes": [{"id": "D1", "status": "doing"}], "answers": answers},
        )
        self.assertEqual(self.gave(printed), "ready")
        self.gives(planner, "ready")
        # Then: Lane names the generator's start to the main conversation
        lines = self.ends(planner)
        self.assertTrue(
            lines[0].startswith("rn: planner gave `ready`. Start `rn:generator`."), lines
        )
        self.assertIn("rn: The list. Ready.", repository.messages(RUN)[-1])

    def test_a_change_out_of_form_is_handed_again(self):
        self.commits(helpers.walkthrough())
        self.calls_up()
        said = self.hands({"run": RUN, "decisions": [{"at": "goal", "decided": GOAL}]})
        self.assertIn("tree.py: the change is out of its form", said)
        self.assertIsNone(runs.pending(RUN))

    def test_an_edit_that_breaks_the_tree_is_mended(self):
        self.commits(helpers.decided(helpers.walkthrough(), 1, "Q6", "the list", None))
        planner, values = self.settles(
            {"run": RUN, "decisions": [{"at": "D1Q6-1", "decided": "each file", "by": "user"}]}
        )
        self.writes(
            planner,
            values["edit"],
            {"grounds": "Order.", "nodes": [{"id": "D1", "inputs": ["tidy/cli.py"]}]},
        )
        said = self.runs(planner, self.tree_command("write", RUN, values["edit"]))
        self.assertIn("D1 takes tidy/cli.py in its inputs, which comes later", said)
        self.assertEqual(self.tree_now()["deliverables"][0]["inputs"], ["dev/product-vision.md"])
