"""S2 of dev/turn/architecture.md, the rounds, one test for each of its paths: Turn's guard
and Pin's run real, by each plugin's hook entries on its Rules laid, through a double of Claude
Code; plan.py, rounds.py, throwaway.py and Pin's check.py run real, by the commands the rules name;
doubles stand in for the starter, up, the planner, the pinner, the generator, the evaluator and the
user. Each path starts where a run stopped in its rounds goes on, as the start's paths have the
rounds begin."""

import json
import os
import unittest

import helpers
from helpers import runs, told

READ_BETTER = "# tidy\n\ntidy sorts your Downloads folder into a folder for each kind of file.\n"


def evaluators(n, on, to):
    """What up is told once the n runs of the evaluator gave the result."""
    start = f"Start `{to}`." if to else "Start no more subagents."
    return [f"turn: The {n} runs of evaluator gave `{on}`. {start}"]


class TestRounds(helpers.InRoundsTest):
    def met_content(self):
        """A round of what the work says, every question met: what up was told after the last run,
        and the lines of the evaluator's runs."""
        phase, lines, after = self.generates(self.line)
        self.assertEqual((phase, after), ("content", [told("generator", "made", "turn:evaluator")]))
        self.assertEqual(len(lines), len(helpers.practices.groups(helpers.PRACTICE, "readme")))
        return self.evaluates(lines), lines

    def back_to_pin(self, after, changed):
        """The planner, started with the run's folder alone, hands each shortfall to Pin; the pinner
        writes the design changed so and gives done; the planner reads it out: the generator's line
        and the Request the pinner was started with."""
        self.assertEqual(after[-1].split(". ")[-1], "Start `turn:planner`.")
        planner = self.new("planner")
        self.starts(planner, json.dumps({"run": self.folder}))
        self.assertIn("fell short", self.plans(planner, "check"))
        request = self.plans(planner, "hand").split("\n", 1)[1].rstrip("\n")
        self.plans(planner, "check")
        self.gives(planner, "handed")
        self.assertEqual(self.ends(planner, request), [told("planner", "handed", "pin:pinner")])
        design = os.path.join(self.folder, runs.DESIGN)
        self.starts(helpers.PINNER, request)
        after = self.pinner_done(design, changed)
        self.assertEqual(after, [told("pin:pinner", "done", "turn:planner")])
        return self.reads_out(self.new("planner"), design, helpers.READ_OUT), request

    def test_every_question_met_in_both_phases_hands_the_work_back(self):
        # Given: a round of what the README says, which every run of the evaluator meets
        after, lines = self.met_content()
        # Then: up is told the result of the runs at once, and to start the generator again
        self.assertEqual(after, evaluators(len(lines), "met", "turn:generator"))
        # When: up starts it with the line the evaluator ended with, for a round of how it reads
        line = self.last[f"e{self.made}"]
        phase, lines, after = self.generates(line, READ_BETTER)
        self.assertEqual(phase, "reading")
        # And: every run of that round meets every question of how a document reads
        after = self.evaluates(lines)
        # Then: up is told to start the planner, which hands the work back
        self.assertEqual(after, [told("evaluator", "good", "turn:planner")])
        planner = self.new("planner")
        self.starts(planner, json.dumps({"run": self.folder}))
        self.assertIn("met every question", self.plans(planner, "check"))
        message = self.plans(planner, "next").split("\n", 1)[1].rstrip("\n")
        self.gives(planner, "done")
        self.assertEqual(self.ends(planner, message), [told("planner", "done")])
        # And: up passes the Done message on as given, the README written and kept
        self.assertEqual(self.passes(planner), runs.done(runs.current(self.run_file())))
        self.assertEqual(self.read(self.at("README.md")), READ_BETTER)
        self.assertTrue(os.path.exists(self.at(self.folder, "verification", "1", "round.json")))

    def test_a_run_short_beside_runs_met_goes_back_to_pin_then_to_a_content_round(self):
        # Given: a round of what the README says, whose walkthrough's question one run finds not met
        _, lines, _ = self.generates(self.line)
        after = self.evaluates(lines, short={"readme/Q2"})
        # Then: up is told `more`, first of the results, and to start the planner
        self.assertEqual(after, evaluators(len(lines), "more", "turn:planner"))
        # When: the shortfall goes to Pin, which settles the walkthrough's run again
        changed = helpers.tidy_tree(
            helpers.PRACTICE, D2={"decided": "tidy --dry-run, then tidy, on six files"}
        )
        line, request = self.back_to_pin(after, changed)
        # Then: the Request carried the shortfall with the decisions that serve its question
        self.assertIn("- readme/Q2: the user lacks readme/Q2 (D2, D3)", request)
        # And: the next round is of what the work says, on the design changed
        self.assertEqual(self.generates(line)[0], "content")

    def test_the_generators_point_left_open_goes_back_to_pin(self):
        # Given: the generator finds the design leaves open which folder the walkthrough sorts
        phase, lines, after = self.generates(self.line, opens={"readme/Q2"})
        # Then: it gives open, ends with no line for the evaluator, and up is told the planner
        self.assertEqual((phase, lines), ("content", []))
        self.assertEqual(after, [told("generator", "open", "turn:planner")])
        # When: the planner hands it to Pin, which settles it
        changed = helpers.tidy_tree(
            helpers.PRACTICE, D2={"decided": "tidy --dry-run ~/Downloads, then tidy"}
        )
        _, request = self.back_to_pin(after, changed)
        # Then: the Request carried the point open
        self.assertIn("- readme/Q2, left open: what readme/Q2 needs changes (D2, D3)", request)

    def test_a_reading_run_short_gives_reword_and_another_reading_round(self):
        # Given: the content met, and a round of how the README reads that falls short
        self.met_content()
        _, lines, _ = self.generates(self.last[f"e{self.made}"], READ_BETTER)
        after = self.evaluates(lines, short={"refactor-doc/Q5"})
        # Then: up is told reword, and to start the generator, for another round of how it reads
        self.assertEqual(after, [told("evaluator", "reword", "turn:generator")])
        self.assertEqual(self.generates(self.last[f"e{self.made}"], READ_BETTER)[0], "reading")

    def test_a_reading_run_that_would_change_what_the_work_says_goes_back_to_pin(self):
        # Given: the content met, and a round of how it reads whose run finds what it says must
        # change
        self.met_content()
        _, lines, _ = self.generates(self.last[f"e{self.made}"], READ_BETTER)
        after = self.evaluates(lines, short={"refactor-doc/Q1"}, opens={"refactor-doc/Q1"})
        # Then: up is told more, and to start the planner, which takes it back to Pin
        self.assertEqual(after, [told("evaluator", "more", "turn:planner")])
        changed = helpers.tidy_tree(
            helpers.PRACTICE, D1={"decided": "a newcomer, who sorts Downloads once a week"}
        )
        line, request = self.back_to_pin(after, changed)
        self.assertIn("refactor-doc/Q1, left open", request)
        # And: the next round is of what the work says
        self.assertEqual(self.generates(line)[0], "content")

    def test_an_evaluator_that_reads_the_design_or_the_ways_is_stopped(self):
        # Given: the runs of the evaluator started on a round of what the README says
        _, lines, _ = self.generates(self.line)
        run = self.new("evaluator")
        self.assertTrue(self.claude.start(None, run, lines[0]).made)
        # When: it reads the design tree, the best practice with its ways, and the generator's
        # Answers
        for path in (
            os.path.join(self.folder, runs.DESIGN),
            runs.practice_in(runs.REPOSITORY, "readme"),
            os.path.join(self.folder, "verification", "generator.json"),
        ):
            read = self.does(run, "Read", file_path=path)
            # Then: each read is stopped with the rule it breaks
            self.assertFalse(read.made, path)
            self.assertIn("Read only", read.reason())

    def test_a_run_that_ends_with_no_result_is_started_again(self):
        # Given: a round of what the README says, its second run of the evaluator ending with no
        # result after it was kept going once
        _, lines, _ = self.generates(self.line)
        after = self.evaluates(lines, none=2)
        # Then: once the others have ended, up is told to start the evaluator again
        self.assertEqual(
            after, ["turn: evaluator ended with no result. Start `turn:evaluator` again."]
        )
        # When: up starts it again with the same line, and it meets its questions
        after = self.evaluates([lines[1]])
        # Then: the runs' result is taken, and up is told to start the generator
        self.assertEqual(after, evaluators(len(lines), "met", "turn:generator"))


class TestNewKind(helpers.InRoundsTest):
    """The rounds of a new kind's best practice, made first."""

    made_at = runs.practice_in(runs.REPOSITORY, "man-page")

    def lays_rounds(self):
        meta = runs.read_practice(runs.practice_in(runs.OWN, "meta"))
        tree = {
            "goal": {"what": "Someone who types man tidy learns each option.", "grounds": ["yes"]},
            "questions": runs.questions("meta", meta),
            "decisions": [
                {
                    "id": "D1",
                    "what": "The parts a man page has",
                    "contributes_to": [q["id"] for q in runs.questions("meta", meta)],
                    "builds_on": [],
                    "decided": "NAME, SYNOPSIS, OPTIONS and EXAMPLES",
                    "settled_by": "reasoning",
                    "grounds": ["the goal"],
                }
            ],
        }
        call = {
            "request": "a man page for tidy",
            "kind": "man-page",
            "reading": "refactor-doc",
            "goal": "Someone who types man tidy learns each option.",
            "kind_goal": "Someone who types man for a command learns each of its options.",
        }
        self.lays("rounds", tree, call)

    def test_a_best_practice_met_in_both_phases_hands_the_work_by_it_to_pin(self):
        # Given: the best practice of man-page made and met in both phases
        made = json.dumps(helpers.PRACTICE, indent=1)
        _, lines, _ = self.generates(self.line, made)
        self.evaluates(lines)
        _, lines, _ = self.generates(self.last[f"e{self.made}"], made)
        after = self.evaluates(lines)
        self.assertEqual(after, [told("evaluator", "good", "turn:planner")])
        # When: the planner ends the best practice's work
        planner = self.new("planner")
        self.starts(planner, json.dumps({"run": self.folder}))
        request = self.plans(planner, "next").split("\n", 1)[1].rstrip("\n")
        self.gives(planner, "handed")
        # Then: up is told to start the pinner on the man page's design, whose questions are the
        # best practice's just made, and its Markdown lies beside it
        self.assertEqual(self.ends(planner, request), [told("planner", "handed", "pin:pinner")])
        design = os.path.join(self.folder, runs.DESIGN)
        self.assertEqual(request.split("\n")[0], json.dumps({"design": design}))
        self.assertEqual(helpers.tree.load(self.at(design))["questions"][0]["id"], "man-page/Q1")
        self.assertTrue(os.path.exists(self.at(runs.REPOSITORY, "man-page", "best-practice.md")))
        self.assertTrue(self.claude.start(None, helpers.PINNER, request).made)


if __name__ == "__main__":
    unittest.main()
