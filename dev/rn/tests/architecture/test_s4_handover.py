"""S4 of dev/rn/architecture.md, the work handed over, the path where git can't push: the planner
commits the deliverable done on the work's branch, keeps the commit, names what's missing in its
message, and gives its result as the rest of the work goes on. The path where it pushes and opens
the draft pull request, and the report once the work has no deliverable left, run in
test_s2_s3_turns.py. rn's guard runs real, by its hook entries, through Lane's double of Claude
Code."""

from __future__ import annotations

import os

import helpers
from helpers import NOTES, RUN, repository, runs


class Handover(helpers.FlowTest):
    def test_a_push_git_cant_make_is_named_the_commit_kept(self):
        # Given: the note's turn of how it reads came back good, with no remote to push to
        self.write_json(
            os.path.join(RUN, "best-practices", "note", "best-practice.json"), helpers.NOTE
        )
        tree = helpers.note_tree()
        for i in tree["deliverables"][0]["necessary_conditions"]:
            i["good"] = True
        self.commits(tree)
        round_ = os.path.join(RUN, "turns", "01-notes-md-reading", "01")
        self.write(NOTES, helpers.NOTED)
        self.write_json(
            os.path.join(round_, runs.MADE), {"made": [NOTES], "decided": [], "open": []}
        )
        ids = [f"Q{n}" for n in range(1, 9)]
        self.write_json(
            os.path.join(round_, "evaluator-G1.json"),
            {"met": [{"question": q, "lines": ["tidy"]} for q in ids], "not_met": [], "open": []},
        )
        # When: the planner, started on the turn, sets the note done and delivers it
        self.begins()
        planner, values = self.cut_and_start("planner")
        self.writes(
            planner,
            values["edit"],
            {"grounds": "The note reads well.", "nodes": [{"id": "D1", "status": "done"}]},
        )
        self.runs(planner, self.tree_command("write", RUN, values["edit"]))
        answers = {
            "grounds": "The goal holds.",
            "nodes": [],
            "answers": [{"id": "goal", "holds": True}],
        }
        self.writes(planner, values["edit"], answers)
        self.runs(planner, self.tree_command("write", RUN, values["edit"]))
        printed = self.runs(planner, self.tree_command("deliver", RUN))
        # Then: the commit stays on the branch, and the planner names what's missing
        self.assertIn(
            f"rn: committed {NOTES} on rn/20261108-tidy-dry-run, which isn't pushed:", printed
        )
        self.assertIn("Name what's missing in your message for the user.", printed)
        self.assertIn(NOTES, repository.ran("git", "show", "--name-only", "--format=", "HEAD"))
        self.gives(planner, self.gave(printed))
        self.assertEqual(self.ends(planner), ["rn: planner gave `done`. Start no more subagents."])
