"""S1 and S3 of dev/pin/architecture.md, the start, one test for each of its paths: Pin's guard runs
real, by Pin's hook entries on Pin's Rules laid, through a double of Claude Code; check.py runs
real, by the command the pinner's rule names; doubles stand in for the go-between, the main
conversation in S1 and the maker AI in S3, for the pinner, and for the person."""

import os
import unittest

import helpers
from helpers import new, tree

PLAN = "notes list should give JSON as well"
GOAL = (
    "For the person:\n"
    "**Purpose**: the goal is what every decision of the plan is weighed by.\n"
    "**To-be**: one sentence that says who gains from the change, and how.\n"
    '**As-is**: your words are "notes list should give JSON as well".\n'
    "**Gap**: they do not say who reads the JSON, or what it spares them.\n"
    "**Proposal**: scripts that read `notes list` get its notes as JSON; yes?"
)
CONFIRMED = "the person, 2026-11-03"
# What the pinner is told where it gives its result with the design file changed since its check.
UNCHECKED = (
    "pin: After changing `{design}`, pass `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check.py"
    " {design}`.\n`.pin/20261103-notes-json/design-tree.md` changed with no test passed after"
)


def walkthrough_with(**given: dict) -> dict:
    """The walkthrough's design tree, each decision of a name given changed so."""
    data = helpers.walkthrough()
    for d in data["decisions"]:
        d.update(given.get(d["id"], {}))
    return data


class TestPersonStarts(helpers.PinnerTest):
    """S1: the person types /pin:down; the main conversation is the go-between."""

    def test_the_go_between_takes_its_steps_from_its_part_named_by_pin_down(self):
        # Given: pin:down, the go-between's entry, and the pinner's entry
        skill = helpers.entry("skills", "down", "SKILL.md")
        agent = helpers.entry("agents", "pinner.md")
        # Then: pin:down names the go-between's part, there in Pin; the pinner runs in the
        # background and names its own part
        self.assertIn("`${CLAUDE_PLUGIN_ROOT}/core/roles/go-between.md`", skill)
        self.assertTrue(os.path.isfile(os.path.join(helpers.PIN, "core", "roles", "go-between.md")))
        self.assertIn("\nbackground: true\n", agent)
        self.assertIn("`${CLAUDE_PLUGIN_ROOT}/core/roles/pinner.md`", agent)

    def test_a_new_plan_gets_a_new_design_file_and_the_goal_is_put(self):
        # Given: no design file in .pin/, and the go-between starting the pinner with the plan
        self.starts(PLAN)
        # When: the pinner writes the goal to confirm, the questions and each decision open, and
        # runs the check
        written = self.writes(new(helpers.WALKTHROUGH))
        checked = self.checks()
        # Then: the write goes through, and the file holds, the decisions on none open now
        self.assertEqual((written.made, written.said), (True, {}))
        self.assertEqual(checked, self.holds("D1", "D2"))
        self.assertEqual(self.on_disk(), new(helpers.WALKTHROUGH))
        # When: it gives asks and ends with the goal
        gave = self.gives("asks")
        heard = self.ends(GOAL)
        # Then: the result goes through, and the person hears the goal as the pinner put it
        self.assertEqual((gave.made, gave.said), (True, {}))
        self.assertEqual(heard, GOAL.split("\n", 1)[1])

    def test_a_stopped_runs_design_file_is_gone_on_from_and_nothing_is_asked_again(self):
        # Given: a design file a stopped run left in .pin/, the goal confirmed and the pinner's own
        # decision settled
        left = walkthrough_with(D1=new(helpers.WALKTHROUGH)["decisions"][0])
        left["decisions"][1].update(
            decided=None, settled_by=None, grounds=[helpers.FOUND, CONFIRMED]
        )
        self.lies(left)
        # When: the go-between finds the file whose goal is this plan's, and starts the pinner on
        # it; the pinner reads it and runs the check
        self.assertEqual(self.picks("get its notes as JSON"), helpers.PERSONS)
        self.starts(PLAN)
        read = self.reads(self.path)
        checked = self.checks()
        # Then: the file holds, only the person's decision open now, and nothing is changed
        self.assertTrue(read.made)
        self.assertEqual(checked, self.holds("D1"))
        self.assertEqual(self.on_disk(), left)
        # When: it gives asks and ends with that decision, the next point
        self.assertTrue(self.gives("asks").made)
        heard = self.ends(helpers.FORM)
        # Then: the person hears that decision, and not the goal or the fact they confirmed again
        self.assertEqual(heard, helpers.FORM.split("\n", 1)[1])
        self.assertNotIn("Found:", heard)

    def test_a_design_file_the_check_finds_at_fault_is_mended(self):
        # Given: the pinner started on a new plan
        self.starts(PLAN)
        # When: it writes a first tree whose second question nothing serves, and runs the check
        faulty = new(helpers.WALKTHROUGH)
        faulty["decisions"][2]["contributes_to"] = ["Q1"]
        self.writes(faulty)
        checked = self.checks()
        # Then: the check names the question
        self.assertEqual(
            checked, (1, f"check.py: {self.path} does not hold:\n- Q2 is served by no decision.\n")
        )
        # When: it gives its result with the file not passed
        stopped = self.gives("asks")
        # Then: the result is stopped with the sentence of its rule
        self.assertFalse(stopped.made)
        self.assertEqual(stopped.reason(), UNCHECKED)
        # When: it mends the file and runs the check again
        self.writes(new(helpers.WALKTHROUGH))
        # Then: the file holds, and its result goes through
        self.assertEqual(self.checks(), self.holds("D1", "D2"))
        self.assertTrue(self.gives("asks").made)
        self.ends(GOAL)


class TestPinnerHeld(helpers.PinnerTest):
    """S1 and S3: the guard stops a call or an end of the pinner that breaks its rules."""

    def setUp(self) -> None:
        super().setUp()
        self.starts(PLAN)
        self.writes(new(helpers.WALKTHROUGH))
        self.checks()

    def test_the_pinner_writing_another_file_is_stopped(self):
        # When: the pinner writes a file other than the design file
        told = self.writes(new(helpers.WALKTHROUGH), path="notes.py")
        # Then: it is stopped with the sentence of its rule, and the file is not written
        self.assertEqual(told.decision(), "deny")
        self.assertEqual(told.reason(), "pin: Write only `{design}`.")
        self.assertEqual(self.read(os.path.join(self.repo, "notes.py")), helpers.NOTES["notes.py"])

    def test_the_pinner_running_another_command_is_stopped(self):
        for command in ("git log --oneline", f"python3 - < {self.path}", f"{self.check}; ls"):
            with self.subTest(command=command):
                # When: the pinner runs a command that is not its check
                told = self.runs(command)
                # Then: it is stopped, told the check command it may run, its path put in
                self.assertEqual(told.decision(), "deny")
                self.assertIn(f"`{self.check}`", told.reason())

    def test_the_pinner_writing_the_design_file_whole_once_it_is_made_is_stopped(self):
        # When: the pinner writes the design file, made already, whole with Write
        before = self.read(os.path.join(self.repo, self.path))
        told = self.rewrites(walkthrough_with(D2={"decided": "x", "settled_by": "reasoning"}))
        # Then: it is stopped with the sentence of its rule, and the file is as it was
        self.assertEqual(told.decision(), "deny")
        self.assertEqual(told.reason(), "pin: Once `{design}` is made, change it only with Edit.")
        self.assertEqual(self.read(os.path.join(self.repo, self.path)), before)

    def test_the_pinner_changing_the_design_file_with_edit_goes_through(self):
        # When: the pinner reads the design file and changes it with Edit
        told = self.writes(walkthrough_with(D2={"decided": "x", "settled_by": "reasoning"}))
        # Then: the change goes through, and the file holds it
        self.assertEqual((told.made, told.said), (True, {}))
        self.assertEqual(self.on_disk()["decisions"][2]["decided"], "x")

    def test_the_pinner_writing_the_design_file_by_a_command_or_a_script_is_stopped(self):
        before = self.read(os.path.join(self.repo, self.path))
        for command in (
            f"sed -i s/open/x/ {self.path}",
            f"python3 -c \"open('{self.path}', 'w').write('')\"",
            f"python3 {helpers.PIN}/scripts/check.py {self.path} > {self.path}",
        ):
            with self.subTest(command=command):
                # When: the pinner runs a command or a script that writes the design file
                told = self.runs(command)
                # Then: it is stopped, told the check it may run, and the file is as it was
                self.assertEqual(told.decision(), "deny")
                self.assertIn(f"`{self.check}`", told.reason())
                self.assertEqual(self.read(os.path.join(self.repo, self.path)), before)

    def test_the_pinner_ending_with_the_file_changed_since_its_last_check_is_stopped(self):
        # When: the pinner changes the file after its check, and gives its result
        self.writes(walkthrough_with(D2={"decided": "x", "settled_by": "reasoning"}))
        told = self.gives("asks")
        # Then: the result is stopped with the sentence of its rule
        self.assertEqual(told.decision(), "deny")
        self.assertEqual(told.reason(), UNCHECKED)
        # When: it ends with no result
        ended = self.claude.stop(helpers.PINNER)
        # Then: it is kept going once, told the commands it ends by
        self.assertFalse(ended.made)
        self.assertIn("result.py pinner asks", ended.reason())


MAKER_SETTLED = {
    "id": "D2",
    "what": "Whether text stays the default",
    "contributes_to": ["Q2"],
    "builds_on": [],
    "decided": "it stays; JSON only with --json",
    "settled_by": "maker",
    "grounds": ["the person told the maker AI, 2026-11-02"],
}


def handed_over() -> dict:
    """The maker AI's hand-over: the goal with its grounds, the questions and its settled decision,
    every other decision open."""
    data = new(helpers.WALKTHROUGH)
    data["goal"]["grounds"] = ["the maker AI's request, 2026-11-02"]
    data["decisions"][2] = dict(MAKER_SETTLED)
    return data


class TestMakerStarts(helpers.PinnerTest):
    """S3: the maker AI is the go-between, and hands over in the design file at its own path."""

    starter = helpers.MAKER
    path = helpers.MAKERS

    def test_the_hand_over_keeps_the_makers_points_and_its_goal_is_not_put(self):
        # Given: the maker AI writes its hand-over at its path, which Pin's guard does not hold
        written = self.claude.call(
            helpers.MAKER,
            "Write",
            {
                "file_path": os.path.join(self.repo, self.path),
                "content": tree.markdown(handed_over()),
            },
        )
        self.assertEqual((written.made, written.said), (True, {}))
        # When: it starts the pinner with the path; the pinner reads the file and runs the check
        self.starts("Settle the design of a --json option on notes list with the person.")
        self.reads(self.path)
        checked = self.checks()
        # Then: the file holds, the maker AI's decision not open
        self.assertEqual(checked, self.holds("D1"))
        self.assertEqual(self.on_disk(), handed_over())
        # When: the pinner reads the fact the form of updated rests on, gives asks and ends with
        # the person's decision
        self.assertTrue(self.reads("scripts/sync.py").made)
        self.assertTrue(self.gives("asks").made)
        heard = self.ends(helpers.FORM)
        # Then: the maker AI gets that decision, not the goal, and the file is as handed over
        self.assertEqual(heard, helpers.FORM.split("\n", 1)[1])
        self.assertEqual(self.on_disk(), handed_over())

    def test_a_point_the_makers_work_found_opens_it_and_each_decision_built_on_it(self):
        # Given: a settled design, the maker AI's decision among it
        settled = helpers.walkthrough()
        settled["decisions"][2] = dict(MAKER_SETTLED)
        self.lies(settled)
        # When: the maker AI starts the pinner again with the point its work found, the form of the
        # JSON; the pinner opens it and the decision built on it, and runs the check
        self.starts("The work found that a phone app reads the list: the form of the JSON again.")
        reopened = walkthrough_with(
            D1={"decided": None, "settled_by": None},
            D3={"decided": None, "settled_by": None},
        )
        reopened["decisions"][2] = dict(MAKER_SETTLED)
        self.writes(reopened)
        checked = self.checks()
        # Then: the file holds, the opened decision open now and the one built on it waiting for
        # it, their grounds kept, the maker AI's decision as it was
        self.assertEqual(checked, self.holds("D1"))
        self.assertEqual(
            self.on_disk()["decisions"][1]["grounds"], settled["decisions"][1]["grounds"]
        )
        self.assertEqual(self.on_disk()["decisions"][2], MAKER_SETTLED)
        self.assertTrue(self.gives("asks").made)
        self.ends(helpers.FORM)


if __name__ == "__main__":
    unittest.main()
