"""S2 and S3 of dev/rn/architecture.md, a deliverable made in turns, one test for each of its paths:
the generator makes it and tries its commands in a throwaway copy, an evaluator for each group of
the kind's intents judges it at once, the planner makes each intent good, a turn of how it reads
follows, and the planner commits the deliverable done and pushes it; a point the generator or an
evaluator finds open ends the run, and a shortfall starts the next round. rn's guard runs real, by
its hook entries, through Lane's double of Claude Code, on a deliverable of the kind note, whose
best practice the run keeps as its own."""

from __future__ import annotations

import os
import subprocess

import helpers
from helpers import NOTED, NOTES, RUN, repository, runs
from unit.domain.test_repository import gh


class Turns(helpers.FlowTest):
    def setUp(self) -> None:
        super().setUp()
        self.write_json(
            os.path.join(RUN, "best-practices", "note", "best-practice.json"), helpers.NOTE
        )
        self.commits(helpers.note_tree())
        subprocess.run(
            ["git", "init", "-q", "--bare", os.path.join(self.base, "origin.git")], check=True
        )
        self.git("remote", "add", "origin", os.path.join(self.base, "origin.git"))
        self.env["PATH"] = f"{gh(os.path.join(self.base, 'bin'), False)}:{self.env['PATH']}"
        # The user types /rn:up alone, and the planner picks the run up, ready to make the note.
        self.begins()
        planner, _ = self.cut_and_start("planner")
        self.assertEqual(self.gave(self.runs(planner, self.tree_command("commit", RUN))), "ready")
        self.gives(planner, "ready")
        self.assertTrue(
            self.ends(planner)[0].startswith("rn: planner gave `ready`. Start `rn:generator`.")
        )

    def generates(self, record=None, text=NOTED):
        """The generator makes the note by its practices, writes its record, tries its commands,
        checks the record, and gives the result it names: what Lane gives the main conversation."""
        generator, values = self.cut_and_start("generator")
        self.writes(generator, NOTES, text)
        for path in [*(values["inputs"] or []), NOTES]:
            self.reads(generator, path)
        made = record or {"made": [NOTES], "commands": ["cat NOTES.md"], "decided": [], "open": []}
        self.writes(generator, values["record"], made)
        self.runs(generator, f"python3 {helpers.RN}/scripts/throwaway.py {RUN}")
        printed = self.runs(generator, self.tree_command("record", values["record"]))
        self.gives(generator, self.gave(printed))
        return self.ends(generator)

    def evaluates(self, groups, lacks=(), open_=()):
        """An evaluator for each group, all started at once, each reading the note and the try
        record, writing its answers, checking them, and giving the result they name: what Lane gives
        the main conversation after the last ends."""
        started = []
        for _ in groups:
            printed = self.main_runs("start", "evaluator")
            run = self.new("evaluator")
            told = self.claude.start(None, run, printed)
            self.assertTrue(told.made, told.said)
            started.append((run, helpers.json.loads(printed.splitlines()[0])))
        self.assertTrue(self.claude.end_turn().made)
        after: list[str] = []
        for (run, values), ids in zip(started, groups):
            for path in [*values["files"], values["try"]]:
                self.reads(run, path)
            answers = {
                "met": [
                    {"question": q, "lines": ["tidy --dry-run"]} for q in ids if q not in lacks
                ],
                "not_met": [
                    {"question": q, "lacks": "they can't tell what moves"}
                    for q in ids
                    if q in lacks
                ],
                "open": [
                    {"question": q, "about": "the order", "what": "dry run first?"}
                    for q in ids
                    if q in open_
                ],
            }
            self.writes(run, values["answers"], answers)
            printed = self.runs(run, self.tree_command("record", values["answers"]))
            self.gives(run, self.gave(printed))
            after = self.ends(run)
        return after

    def plans_turn(self, *nodes):
        """The planner, started on the turn come back good, writes the nodes, answers each node
        touched, and commits or delivers: what it printed, and the planner."""
        planner, values = self.cut_and_start("planner")
        self.writes(
            planner, values["edit"], {"grounds": "The turn came back good.", "nodes": list(nodes)}
        )
        said = self.runs(planner, self.tree_command("write", RUN, values["edit"]))
        touched = (
            said.split("holding or not: ")[1].rstrip(".\n").split(", ")
            if "holding or not" in said
            else []
        )
        if touched:
            self.writes(
                planner,
                values["edit"],
                {
                    "grounds": "Each holds.",
                    "nodes": [],
                    "answers": [{"id": n, "holds": True} for n in touched],
                },
            )
            self.runs(planner, self.tree_command("write", RUN, values["edit"]))
        verb = "deliver" if any(n.get("status") == "done" for n in nodes) else "commit"
        return self.runs(planner, self.tree_command(verb, RUN)), planner

    def test_a_deliverable_made_judged_read_and_handed_over(self):
        # When: the generator makes the note, and an evaluator for each group finds it good
        self.assertTrue(
            self.generates()[0].startswith("rn: generator gave `made`. Start `rn:evaluator`.")
        )
        lines = self.evaluates([["Q1"], ["Q2"]])
        good = "rn: The 2 runs of evaluator gave `good`. Start `rn:planner`."
        self.assertTrue(lines[0].startswith(good), lines)
        # And: the planner makes each intent good, and commits
        printed, planner = self.plans_turn(
            {"id": "D1Q1", "good": True}, {"id": "D1Q2", "good": True}
        )
        self.assertEqual(self.gave(printed), "ready")
        self.gives(planner, "ready")
        self.assertTrue(
            self.ends(planner)[0].startswith("rn: planner gave `ready`. Start `rn:generator`.")
        )
        # And: a turn of how it reads, by refactor-doc, whose one group finds it good
        self.assertTrue(
            self.generates({"made": [NOTES], "decided": [], "open": []})[0].startswith(
                "rn: generator gave `made`."
            )
        )
        lines = self.evaluates([[f"Q{n}" for n in range(1, 9)]])
        self.assertTrue(
            lines[0].startswith("rn: evaluator gave `good`. Start `rn:planner`."), lines
        )
        # Then: the planner sets it done and delivers it, the work done
        printed, planner = self.plans_turn({"id": "D1", "status": "done"})
        self.assertIn("pushed: https://github.com/tidy-sort/tidy/pull/8", printed)
        self.assertIn("Done: NOTES.md is changed.", printed)
        self.gives(planner, "done")
        self.assertEqual(self.ends(planner), ["rn: planner gave `done`. Start no more subagents."])
        self.assertIn(NOTES, repository.ran("git", "show", "--name-only", "--format=", "HEAD"))
        self.assertEqual(self.tree_now()["deliverables"][0]["status"], "done")

    def test_a_point_the_generator_finds_open_ends_the_run(self):
        record = {
            "made": [NOTES],
            "decided": [],
            "open": [{"intent": "Q1", "about": "the order", "what": "dry run first?"}],
        }
        self.assertEqual(
            self.generates(record), ["rn: generator gave `open`. Start no more subagents."]
        )
        self.assertIn("- D1Q1 the order: dry run first?. Q1:", self.main_runs("points"))

    def test_a_point_an_evaluator_finds_open_ends_the_run(self):
        self.generates()
        lines = self.evaluates([["Q1"], ["Q2"]], open_=["Q2"])
        self.assertEqual(
            lines[-1], "rn: The 2 runs of evaluator gave `open`. Start no more subagents."
        )
        self.assertIn("- D1Q2 the order: dry run first?.", self.main_runs("points"))

    def test_a_shortfall_starts_the_next_round_with_what_the_people_lack(self):
        self.generates()
        lines = self.evaluates([["Q1"], ["Q2"]], lacks=["Q1"])
        more = "rn: The 2 runs of evaluator gave `more`. Start `rn:generator`."
        self.assertTrue(lines[-1].startswith(more), lines)
        printed = self.main_runs("start", "generator")
        self.assertIn("- Q1: they can't tell what moves", printed)
        self.assertIn(os.path.join(RUN, "turns", "01-notes-md", "02"), printed)

    def test_an_evaluator_reads_only_what_the_people_have(self):
        self.generates()
        printed = self.main_runs("start", "evaluator")
        run = self.new("evaluator")
        self.starts(run, printed)
        told = self.does(run, "Read", file_path=os.path.join(self.repo, runs.tree_path(RUN)))
        self.assertFalse(told.made)
        self.assertIn("Read only", told.reason())
