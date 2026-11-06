"""S3 of dev/pin/architecture.md, an answer, one test for each of its paths, each run once on a run
the person began by typing `/pin:down`, and once on one the user's AI began by calling the skill
with its own design tree: Pin's guard runs real, by Pin's hook entries on Pin's Rules laid, through
a double of Claude Code; check.py runs real, by the command the pinner's rule names; doubles stand
in for the orchestrator, the main conversation, for the pinner and for the person, a set
answer."""

import os
import unittest
from typing import Any

import helpers
from helpers import check, testing

CONFIRMED = "the person confirmed, 2026-11-03"
FACT = (
    "For the person:\nFound: scripts/sync.py:14 reads `updated` with"
    " `datetime.fromisoformat(fields[3])`, so it expects ISO 8601. Is that right?"
)
DESIGN = (
    "For the person:\n"
    "Goal: scripts that read `notes list` get its notes as JSON. (you)\n"
    "- The output is one JSON array, one object for each note. (you)\n"
    "- The text output stays the default; JSON comes only with --json. (follows from the goal)\n"
    "- `updated` stays in ISO 8601, as the text gives it. (found, you confirmed)\n"
    "Do we understand the plan the same way?"
)
OPEN = {"decided": None, "settled_by": None}
AI_SETTLED = {
    "decided": "it stays; JSON only with --json",
    "settled_by": "maker",
    "grounds": ["the person told their AI, 2026-11-02"],
}


class Answer(helpers.PinnerTest):
    """A path of an answer: the design tree as the start before left it, the pinner started on it
    and ended with a point, which the orchestrator put to the person as given."""

    def state(self, **given: dict[str, Any]) -> dict[str, Any]:
        """The walkthrough's design, the goal confirmed and every decision settled, each decision of
        a name given changed so; the second the user's AI's where it called the skill."""
        data = helpers.walkthrough()
        if self.called:
            data["decisions"][2].update(AI_SETTLED)
        for d in data["decisions"]:
            d.update(given.get(d["id"], {}))
        return data

    def waits(self, data: dict[str, Any], reply: str) -> None:
        """The start before: the design tree lies as data, the run begins and the pinner is started
        on it, checks it, gives asks and ends with the reply, which the person hears as given."""
        self.lies(data)
        self.starts("notes list should give JSON as well")
        self.assertEqual(self.checks()[0], 0)
        self.assertTrue(self.gives("asks").made)
        self.assertEqual(self.ends(reply), reply.split("\n", 1)[1])

    def settles(self, data: dict[str, Any]) -> tuple[int, str]:
        """The pinner writes the data, which goes through, and runs the check: the Check result."""
        written = self.writes(data)
        self.assertEqual((written.made, written.said), (True, {}))
        return self.checks()

    def design(self) -> str:
        """The whole design as the pinner shows it, the user's AI's point marked its own where it
        called the skill."""
        if not self.called:
            return DESIGN
        return DESIGN.replace("(follows from the goal)", "(your AI)")

    def asks_next(self, reply: str) -> None:
        """The pinner gives asks, which goes through, and ends with the reply, which the person
        hears as given."""
        gave = self.gives("asks")
        self.assertEqual((gave.made, gave.said), (True, {}))
        self.assertEqual(self.ends(reply), reply.split("\n", 1)[1])

    def test_a_fact_confirmed_is_written_into_the_grounds_its_decision_left_open(self):
        # Given: the fact the form of updated rests on put to the person, the decision under it
        # open
        self.waits(self.state(D1=OPEN, D3={**OPEN, "grounds": []}), FACT)
        # When: the person answers right, and the pinner writes the fact and their confirmation
        # into the decision's grounds, leaving it open
        self.answers("right")
        confirmed = self.state(D1=OPEN, D3={**OPEN, "grounds": [helpers.FOUND, CONFIRMED]})
        # Then: the file holds, the decision it builds on open now and it waiting for that one
        self.assertEqual(self.settles(confirmed), self.holds("D1"))
        self.assertEqual(self.on_disk(), confirmed)
        self.asks_next(helpers.FORM)

    def test_a_fact_corrected_decides_its_decision_by_the_person(self):
        # Given: the fact put to the person, the decision it rests on open now
        self.waits(self.state(D3={**OPEN, "grounds": []}), FACT)
        # When: the person corrects it, and the pinner writes the decision by their word
        self.answers("No: it is local time with its offset")
        corrected = self.state(
            D3={
                "decided": "ISO 8601, in local time with its offset",
                "settled_by": "user",
                "grounds": [
                    helpers.FOUND,
                    "the person: it is local time with its offset, 2026-11-03",
                ],
            }
        )
        # Then: the file holds with no decision open, the correction kept, and the whole design
        # goes out
        self.assertEqual(self.settles(corrected), self.holds())
        self.assertEqual(self.on_disk()["decisions"][1], corrected["decisions"][1])
        self.asks_next(self.design())

    def test_a_decision_made_is_settled_by_the_person_and_each_on_it_follows(self):
        # Given: the form of the JSON put to the person, the fact under it confirmed
        self.waits(self.state(D1=OPEN, D3=OPEN), helpers.FORM)
        # When: the person answers yes, and the pinner writes their decision
        self.answers("yes, jq reads it whole")
        made = self.state(D3=OPEN)
        made["decisions"][0]["grounds"] = ["the person: yes, jq reads it whole, 2026-11-03"]
        # Then: the file holds, the decision built on it open now
        self.assertEqual(self.settles(made), self.holds("D3"))
        # When: the pinner settles that one by the fact confirmed
        made["decisions"][1].update(helpers.WALKTHROUGH["decisions"][1])
        # Then: the file holds with no decision open, and the whole design goes out
        self.assertEqual(self.settles(made), self.holds())
        self.assertEqual(self.on_disk()["decisions"][0]["settled_by"], "user")
        self.asks_next(self.design())

    def test_a_decision_left_to_pin_is_settled_by_reasoning_saying_so(self):
        # Given: the form of the JSON put to the person
        self.waits(self.state(D1=OPEN, D3=OPEN), helpers.FORM)
        # When: the person leaves it to Pin, and the pinner settles it by reasoning, saying so
        self.answers("you decide")
        left = self.state(D3=OPEN)
        left["decisions"][0].update(
            settled_by="reasoning",
            grounds=[
                "the person left it to Pin, 2026-11-03",
                "jq and json.load read an array whole",
            ],
        )
        # Then: the file holds, the decision built on it open now
        self.assertEqual(self.settles(left), self.holds("D3"))
        left["decisions"][1].update(helpers.WALKTHROUGH["decisions"][1])
        self.assertEqual(self.settles(left), self.holds())
        self.asks_next(self.design())

    def test_a_point_an_answer_raises_is_added_open_joined_and_then_settled(self):
        # Given: the form of the JSON put to the person
        self.waits(self.state(D1=OPEN, D3=OPEN), helpers.FORM)
        # When: the person answers yes and raises a point the file does not hold, which the pinner
        # adds open, joined to what it serves and builds on
        self.answers("yes, and tags must come as a list")
        raised = self.state(D3=OPEN)
        raised["decisions"][0]["grounds"] = ["the person: yes, 2026-11-03"]
        raised["decisions"].append(
            helpers.decision(
                "D4",
                what="The form of tags",
                contributes_to=["D1"],
                builds_on=["D1"],
                grounds=["the person: tags must come as a list, 2026-11-03"],
            )
        )
        # Then: the file holds, the new point open now beside the one built on the decision made
        self.assertEqual(self.settles(raised), self.holds("D3", "D4"))
        # When: the pinner settles both, the new one by the person's words
        raised["decisions"][1].update(helpers.WALKTHROUGH["decisions"][1])
        raised["decisions"][3].update(decided="a list of texts", settled_by="user")
        # Then: the file holds with no decision open
        self.assertEqual(self.settles(raised), self.holds())
        self.asks_next(self.design())

    def test_a_change_to_the_design_opens_its_decision_and_each_on_it_settled_again(self):
        # Given: the whole design put to the person
        settled = self.state()
        self.waits(settled, self.design())
        # When: the person changes the form of the JSON, and the pinner opens it and the decision
        # built on it, their grounds kept
        self.answers("make it one object a line")
        opened = self.state(D1=OPEN, D3=OPEN)
        # Then: the file holds, the changed decision open now and the other waiting for it
        self.assertEqual(self.settles(opened), self.holds("D1"))
        self.assertEqual(
            self.on_disk()["decisions"][1]["grounds"], settled["decisions"][1]["grounds"]
        )
        self.asks_next(helpers.FORM)
        # When: the person decides it again, and the pinner settles the one built on it again
        self.answers("no: one object a line")
        again = self.state(D3=OPEN)
        again["decisions"][0].update(decided="one JSON object a line, one for each note")
        self.assertEqual(self.settles(again), self.holds("D3"))
        again["decisions"][1].update(helpers.WALKTHROUGH["decisions"][1])
        # Then: the file holds with no decision open, and the design goes out again
        self.assertEqual(self.settles(again), self.holds())
        self.asks_next(self.design())

    def test_a_wrap_up_leaves_the_open_decisions_open_and_shows_the_design(self):
        # Given: the form of the JSON put to the person
        before = self.state(D1=OPEN, D3=OPEN)
        self.waits(before, helpers.FORM)
        # When: the person asks to wrap up; the pinner changes nothing and runs the check
        self.answers("wrap up")
        # Then: the file holds as it was, its open decisions open, and the design goes out with
        # them marked open
        self.assertEqual(self.checks(), self.holds("D1"))
        self.assertEqual(self.on_disk(), before)
        self.asks_next(
            self.design().replace("note. (you)", "note. (open)").replace("(found, you", "(open")
        )

    def test_the_design_confirmed_is_written_and_its_path_handed_back(self):
        # Given: the whole design put to the person
        self.waits(self.state(), self.design())
        # When: the person confirms it, and the pinner writes their words into the goal's grounds
        self.answers("yes")
        confirmed = self.state()
        confirmed["goal"]["grounds"].append("the person confirmed the design: yes, 2026-11-03")
        checked = self.settles(confirmed)
        # Then: the file holds with no decision open
        self.assertEqual(checked, self.holds())
        # When: it gives done and ends with the path and what the check printed
        gave = self.gives("done")
        handed = f"For the person:\nThe design is in {self.path}.\n{checked[1]}"
        heard = self.ends(handed, told=helpers.END)
        # Then: done goes through, the main conversation is told to start no more, and the
        # orchestrator hands on the path as given and gives done, which goes through
        self.assertEqual((gave.made, gave.said), (True, {}))
        self.assertIn(self.path, heard)
        self.assertIn(check.HOLDS, heard)
        back = self.hands_back()
        self.assertEqual((back.made, back.said), (True, {}))
        # And: the run has ended, so a start of the pinner after it is held to nothing
        after = self.claude.start(None, testing.Run("pin:pinner", "p2"), "{}")
        self.assertTrue(after.made)
        self.assertNotIn(helpers.WAIT, after.context)
        if self.called:
            # And: the user's AI reads the design to build on it, which Pin's guard does not hold
            read = self.claude.call(None, "Read", {"file_path": os.path.join(self.repo, self.path)})
            self.assertEqual((read.made, read.said), (True, {}))
            self.assertEqual(self.on_disk(), confirmed)
            self.assertEqual(self.on_disk()["decisions"][2]["settled_by"], "maker")

    def test_a_start_made_while_a_point_waits_is_stopped_told_to_put_it(self):
        # Given: the form of the JSON put to the person
        self.waits(self.state(D1=OPEN, D3=OPEN), helpers.FORM)
        # When: the orchestrator starts the pinner again in place of putting the answer back
        again = self.claude.start(None, testing.Run("pin:pinner", "p2"), "{}")
        # Then: it is stopped, told to put the point and resume the pinner with the answer
        self.assertFalse(again.made)
        self.assertEqual(again.reason(), f"{helpers.FOLLOWED}\n{helpers.ASKED}")


class TestPersonTyped(Answer):
    """S3 on a run the person began by typing /pin:down."""


class TestAICalled(Answer):
    """S3 on a run the user's AI began by calling the skill, its design tree at its own path, its
    decision settled by maker."""

    called = True
    path = helpers.AIS


del Answer

if __name__ == "__main__":
    unittest.main()
