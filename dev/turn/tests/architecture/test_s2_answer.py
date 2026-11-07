"""S2 of dev/turn/architecture.md, an answer, one test for each of its paths, each run once with
the main conversation as the starter, and once with the user's AI: Turn's guard and
Pin's run real, by each plugin's hook entries on its Rules laid, through a double of Claude Code;
plan.py, rounds.py and Pin's check.py run real, by the commands the rules name; doubles stand in
for the starter, up, the planner, the pinner, the generator and the user."""

import json
import os
import unittest

import helpers
from helpers import runs, told

FACT = 'Found: setup.cfg:9 "python_requires = >=3.9", so tidy needs Python 3.9. Is that right?'
RUN_POINT = (
    "**Purpose**: the walkthrough lets a newcomer see what tidy does to a folder like theirs.\n"
    "**To-be**: one run whose output shows the reader their files sorted.\n"
    "**As-is**: tidy moves files at once, and tidy --dry-run only shows what it would move.\n"
    "**Gap**: tidy alone and tidy --dry-run first both show it, and nothing found favors either.\n"
    "**Proposal**: tidy --dry-run on a folder of five files, then tidy; yes?"
)
DESIGN = (
    "Goal: someone with a cluttered Downloads folder learns what tidy does, installs it and sorts"
    " their folder. (you)\n"
    "- The walkthrough runs tidy --dry-run, then tidy, on five files. (you)\n"
    "- Requirements: Python 3.9 or later. (found, you confirmed)\n"
    "Do we understand the README the same way?"
)


def opened(*names):
    """tidy's design with each decision of the names open."""
    return helpers.tidy_tree(
        **{n: {"decided": None, "settled_by": None, "grounds": []} for n in names}
    )


class Answer(helpers.TurnTest):
    """A path of an answer: the run begun and its design handed to Pin, or its kind asked."""

    def request(self, words):
        """The request the starter starts up with: the person's words, or the calling AI's with its
        JSON line naming the run's folder."""
        if self.starter is None:
            return words
        given = {"run": self.folder}
        return f"{words}\n{json.dumps({'request': words, 'given': given})}"

    def design(self):
        return os.path.join(self.folder, runs.DESIGN)

    def with_pin(self, tree, point):
        """The run begun on a README for tidy, the pinner started on the Request, having written
        the tree and ended with the point, which the person heard."""
        words = self.request("a README for tidy")
        self.begins(words)
        request = self.begun(words, self.new("planner"), request=words.split("\n")[0])
        self.starts(helpers.PINNER, request)
        self.assertEqual(self.pinner_asks(self.design(), tree, point), point)

    def test_an_answer_to_the_kind_resumes_the_planner_word_for_word(self):
        # Given: the planner asked the kind, which reached the person
        words = self.request("something that explains tidy")
        self.begins(words)
        planner = self.new("planner")
        self.starts(planner, json.dumps({"run": self.folder}) + "\n" + words)
        self.plans(planner, "check")
        self.gives(planner, "asks")
        self.ends(planner, f"{helpers.FOR_THE_PERSON}\nA README for tidy, a document. Right?")
        self.passes(planner)
        # When: the person answers, and up resumes the planner with the answer whole
        self.answers("yes, a README", planner)
        # Then: the planner, resumed, begins the run of the kind they answered
        self.hands_over(planner, request="something that explains tidy")
        self.assertEqual(json.loads(self.read(self.at(self.folder, runs.CALL)))["kind"], "readme")

    def test_an_answer_to_a_point_reaches_the_pinner_which_asks_the_next(self):
        # Given: the pinner showed the person a fact
        self.with_pin(opened("D2", "D3"), FACT)
        # When: the person answers right, and up resumes the pinner with it
        self.answers("right", helpers.PINNER)
        # Then: the pinner writes the fact confirmed, and its next point reaches the person
        confirmed = opened("D2")
        heard = self.pinner_asks(self.design(), confirmed, RUN_POINT)
        self.assertEqual(self.heard, [FACT, RUN_POINT])
        self.assertEqual((heard, helpers.tree.load(self.at(self.design()))), (RUN_POINT, confirmed))

    def test_any_words_while_a_point_waits_reach_the_pinner_word_for_word(self):
        # Given: the walkthrough's run put to the person
        self.with_pin(opened("D2"), RUN_POINT)
        # When: the person asks something back instead of answering
        words = "what does --dry-run print for a file with no extension?"
        self.answers(words, helpers.PINNER)
        # Then: the pinner holds their words as given, under the Answer's line, and goes on
        kept = os.path.join(self.base, "lane")
        records = [
            os.path.join(folder, name)
            for folder, _, names in os.walk(kept)
            for name in names
            if name == f"{helpers.PINNER.agent_id}.jsonl"
        ]
        self.assertTrue(records)
        sent = f"{helpers.ANSWERED}\n{words}"
        self.assertTrue(all(json.dumps(sent)[1:-1] in self.read(r) for r in records))
        self.assertEqual(self.pinner_asks(self.design(), opened("D2"), RUN_POINT), RUN_POINT)

    def test_the_design_confirmed_is_read_out_and_the_rounds_start(self):
        # Given: the whole design put to the person
        self.with_pin(helpers.tidy_tree(), DESIGN)
        # When: the person confirms it, and the pinner writes their words and gives done
        self.answers("yes", helpers.PINNER)
        confirmed = helpers.tidy_tree()
        confirmed["goal"]["grounds"].append("the person confirmed the design: yes, 2026-11-04")
        after = self.pinner_done(self.design(), confirmed)
        # Then: up is told to start the planner, which reads the design out and gives ready
        self.assertEqual(after, [told("pin:pinner", "done", "turn:planner")])
        line = self.reads_out(self.new("planner"), self.design(), helpers.READ_OUT)
        work = runs.current(self.run_file())
        self.assertEqual(
            {k: work[k] for k in ("paths", "commands", "files", "at")},
            {**helpers.READ_OUT, "at": "rounds"},
        )
        # And: up starts the generator with the planner's line, whose first round is of content
        generator = self.new("generator")
        self.starts(generator, line)
        printed = self.runs(
            generator, f"python3 {helpers.TURN}/scripts/rounds.py round {self.folder}"
        )
        self.assertIn("round 1 of readme is of what the work says", printed)
        # And: nothing of the design's answers was put to the person but the pinner's points
        self.assertEqual(self.heard, [DESIGN])


class TestPersonAnswers(Answer):
    """S2: the person answers through the main conversation. S4, the calling AI passing the answer
    back, has no test, as Lane resumes a role only with the person's own words."""


# The paths run in the class above alone.
del Answer

if __name__ == "__main__":
    unittest.main()
