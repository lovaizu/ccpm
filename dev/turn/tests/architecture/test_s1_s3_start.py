"""S1 and S3 of dev/turn/architecture.md, the start, one test for each of its paths: Turn's
guard and Pin's run real, by each plugin's hook entries on its Rules laid, through a double of
Claude Code; plan.py and Pin's check.py run real, by the commands the rules name; doubles stand in
for the starter, up, the planner, the pinner and the user."""

import json
import os
import unittest

import helpers
from helpers import asked, runs, told

# The README's purpose as the pinner puts it, while the goal's grounds are empty.
GOAL = (
    "**Purpose**: the README's purpose is what every decision of the README is weighed by.\n"
    "**To-be**: one sentence that says who reads the README, and what they do with it.\n"
    '**As-is**: your words are "a README for tidy", and the repository has no other document.\n'
    "**Gap**: your words do not say who reads the README.\n"
    "**Proposal**: someone with a cluttered Downloads folder learns what tidy does, installs it"
    " and sorts their folder with it; yes?"
)
FACT = 'Found: setup.cfg:9 "python_requires = >=3.9", so tidy needs Python 3.9. Is that right?'


def opened(tree, *names):
    """The tree with each decision of the names open."""
    for d in tree["decisions"]:
        if d["id"] in names:
            d.update(decided=None, settled_by=None, grounds=[])
    return tree


class Start(helpers.TurnTest):
    def test_the_kind_named_begins_a_new_run_and_hands_pin_the_design_tree(self):
        # Given: the person types /turn:up a README for tidy, and up is told to start the planner
        context = self.begins("a README for tidy")
        self.assertIn("turn: Start `turn:planner`.", "\n".join(context))
        # When: up starts the planner, which begins the run of the kind its words name
        planner = self.new("planner")
        request = self.begun("a README for tidy", planner)
        # Then: the run is with Pin, its hand-over asking each question of a README under the goal
        # as the planner reads it, not yet confirmed, and the Request names the design tree
        design = os.path.join(self.folder, runs.DESIGN)
        self.assertEqual(runs.current(self.run_file())["at"], "pin")
        handed = helpers.tree.load(self.at(design))
        self.assertEqual(handed["questions"], runs.questions("readme", helpers.README_PRACTICE))
        self.assertEqual((handed["goal"]["grounds"], handed["decisions"]), ([], []))
        self.assertEqual(request, runs.request(design, "a README for tidy"))
        # When: up starts the pinner with the Request as given, which asks the goal
        started = self.starts(helpers.PINNER, request)
        pinner_part = helpers.entry_of(helpers.PIN, "core", "roles", "pinner.md")
        self.assertTrue(any(pinner_part in said for said in started.context))
        tree = opened(helpers.tidy_tree(), "D1", "D2", "D3")
        tree["goal"] = handed["goal"]
        heard = self.pinner_asks(design, tree, GOAL)
        # Then: the person hears the goal as the pinner gave it, the first point that is theirs
        self.assertEqual((heard, self.heard), (GOAL, [GOAL]))

    def test_the_kind_left_open_is_asked_and_its_answer_begins_the_run(self):
        # Given: a request that names no kind
        self.begins("something that explains tidy")
        planner = self.new("planner")
        self.starts(planner, json.dumps({"run": self.folder}) + "\nsomething that explains tidy")
        # When: the planner finds no Run, gives asks and ends with the kind to confirm
        self.assertIn("holds no Run yet", self.plans(planner, "check"))
        self.gives(planner, "asks")
        question = f"{helpers.FOR_THE_PERSON}\nA README for tidy, a document. Right?"
        # Then: up is told to put the point to the person, and passes the kind on as given
        self.assertEqual(self.ends(planner, question), [asked("turn:planner")])
        self.assertEqual(self.passes(planner), "A README for tidy, a document. Right?")
        # When: the person answers, and the planner, resumed, begins the run of that kind
        self.answers("right", planner)
        # Then: up is told to start the pinner, on the Request that names the hand-over
        request = self.hands_over(planner, request="something that explains tidy")
        self.assertTrue(self.claude.start(None, helpers.PINNER, request).made)

    def test_a_kind_new_to_turn_has_its_best_practice_handed_over_first(self):
        # Given: a request for a man page, which Turn has no best practice of
        self.begins("a man page for tidy")
        planner = self.new("planner")
        self.starts(planner, json.dumps({"run": self.folder}) + "\na man page for tidy")
        self.plans(planner, "check")
        # When: the planner begins the run with no purpose of the kind, which plan.py refuses
        self.calls(planner, request="a man page for tidy", kind="man-page")
        refused = self.does(
            planner,
            "Bash",
            command=f"python3 {helpers.TURN}/scripts/plan.py start {self.folder}",
            description="d",
        )
        self.assertEqual(refused.made, True)
        self.assertIn("write into call.json its kind_goal", self.claude.printed)
        # And: it adds the kind's purpose to the Call and begins again
        purpose = "Someone who types man tidy learns each option and what it does."
        self.calls(planner, request="a man page for tidy", kind="man-page", kind_goal=purpose)
        request = self.plans(planner, "start").split("\n", 1)[1].rstrip("\n")
        self.plans(planner, "check")
        self.gives(planner, "handed")
        # Then: the run makes the best practice first, by meta, then the man page; the hand-over
        # puts meta's questions under the kind's purpose; and up is told to start the pinner
        self.assertEqual(self.ends(planner, request), [told("planner", "handed", "pin:pinner")])
        works = self.run_file()["works"]
        self.assertEqual(
            [(w["kind"], w["at"]) for w in works], [("meta", "pin"), ("man-page", "waits")]
        )
        design = os.path.join(self.folder, "best-practice", runs.DESIGN)
        handed = helpers.tree.load(self.at(design))
        self.assertEqual(handed["goal"], {"what": purpose, "grounds": []})
        self.assertEqual(handed["questions"][0]["id"], "meta/Q1")
        self.assertEqual(request.split("\n")[0], json.dumps({"design": design}))
        self.assertTrue(self.claude.start(None, helpers.PINNER, request).made)

    def test_a_stopped_run_whose_design_is_open_goes_on_through_pin(self):
        # Given: a run stopped while Pin settled its design, the walkthrough's run still open
        self.lays("pin", opened(helpers.tidy_tree(), "D2"))
        # When: the person types /turn:up with the run's folder, and the planner, started with it,
        # hands the design to Pin to go on with
        self.begins(self.folder)
        planner = self.new("planner")
        self.starts(planner, json.dumps({"run": self.folder}) + "\n" + self.folder)
        self.assertIn("is with Pin", self.plans(planner, "check"))
        request = self.plans(planner, "hand").split("\n", 1)[1].rstrip("\n")
        self.plans(planner, "check")
        self.gives(planner, "handed")
        # Then: up is told to start the pinner with a Request naming the design tree as it lies
        design = os.path.join(self.folder, runs.DESIGN)
        self.assertEqual(self.ends(planner, request), [told("planner", "handed", "pin:pinner")])
        self.assertEqual(request, json.dumps({"design": design}))
        self.starts(helpers.PINNER, request)
        self.assertTrue(self.does(helpers.PINNER, "Read", file_path=design).made)
        self.assertEqual(helpers.tree.load(self.at(design)), opened(helpers.tidy_tree(), "D2"))

    def test_a_stopped_run_whose_design_is_confirmed_goes_on_at_the_rounds(self):
        # Given: a run stopped in its rounds, its design read out
        self.lays("rounds", helpers.tidy_tree(), **helpers.READ_OUT)
        # When: the person types /turn:up with the run's folder, and the planner goes on at the
        # rounds
        self.begins(self.folder)
        planner = self.new("planner")
        self.starts(planner, json.dumps({"run": self.folder}) + "\n" + self.folder)
        self.assertIn("in its rounds", self.plans(planner, "check"))
        line = self.plans(planner, "ready").split("\n", 1)[1].rstrip("\n")
        self.gives(planner, "ready")
        # Then: up is told to start the generator, with the line that names the run's work
        self.assertEqual(self.ends(planner, line), [told("planner", "ready", "turn:generator")])
        self.assertEqual(
            json.loads(line),
            {
                "run": self.folder,
                "work": ["README.md"],
                "answers": os.path.join(self.folder, "verification", "generator.json"),
            },
        )
        generator = self.new("generator")
        self.starts(generator, line)
        self.assertIn(
            "round 1 of readme is of what the work says",
            self.runs(generator, f"python3 {helpers.TURN}/scripts/rounds.py round {self.folder}"),
        )

    def test_a_change_named_is_handed_to_pin_with_the_change(self):
        # Given: a run whose README was handed back
        self.lays("done", helpers.tidy_tree(), **helpers.READ_OUT)
        # When: the person names the run's folder and a change
        words = f"{self.folder} the walkthrough should use ten files"
        self.begins(words)
        planner = self.new("planner")
        self.starts(planner, json.dumps({"run": self.folder}) + "\n" + words)
        self.assertIn("The run is done", self.plans(planner, "check"))
        printed = self.plans(planner, "hand").split("\n", 1)[1].rstrip("\n")
        self.plans(planner, "check")
        self.gives(planner, "handed")
        request = f"{printed}\nthe walkthrough should use ten files"
        # Then: the work is with Pin again, and up is told to start the pinner with the change
        self.assertEqual(self.ends(planner, request), [told("planner", "handed", "pin:pinner")])
        self.assertEqual(runs.current(self.run_file())["at"], "pin")
        self.assertTrue(self.claude.start(None, helpers.PINNER, request).made)


class TestCallingAI(helpers.TurnTest):
    """S3: the calling AI starts up with the request and the points it settled."""

    starter = helpers.CALLER
    folder = os.path.join(".caller", "readme")

    def test_its_kind_goal_and_decisions_are_handed_over_word_for_word_and_the_goal_not_put(self):
        # Given: the calling AI's request, with its kind, goal, a decision and the run's folder
        goal = {
            "what": "Someone with a cluttered Downloads folder learns what tidy does.",
            "grounds": ["the person told the calling AI, 2026-11-03"],
        }
        settled = {**helpers.tidy_tree()["decisions"][1], "contributes_to": [], "builds_on": []}
        settled.update(settled_by="maker", grounds=["the person told the calling AI, 2026-11-03"])
        given = {"kind": "readme", "goal": goal, "decisions": [settled], "run": self.folder}
        call = json.dumps({"request": "the README of this repository", "given": given})
        words = f"the README of this repository\n{call}"
        self.begins(words)
        # When: up starts the planner in the folder the calling AI gave, which takes its points
        # as given and begins the run
        planner = self.new("planner")
        request = self.begun(words, planner, request="the README of this repository", given=given)
        # Then: the hand-over holds the goal and the decision word for word, the goal confirmed,
        # so Pin puts it to no one
        handed = helpers.tree.load(self.at(self.folder, runs.DESIGN))
        self.assertEqual((handed["goal"], handed["decisions"]), (goal, [settled]))
        # When: the pinner joins the decision to its question and asks a fact first
        self.starts(helpers.PINNER, request)
        tree = helpers.tidy_tree(D2={**settled, "contributes_to": ["readme/Q5"]})
        tree["goal"] = goal
        heard = self.pinner_asks(os.path.join(self.folder, runs.DESIGN), opened(tree, "D3"), FACT)
        # Then: the calling AI passes the fact on as given, and the goal was never put
        self.assertEqual(self.heard, [FACT])
        self.assertNotIn("Purpose", heard)


if __name__ == "__main__":
    unittest.main()
