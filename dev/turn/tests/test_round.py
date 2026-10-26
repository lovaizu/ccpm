"""Within a round, the generator and the first user, once they have replied, are sent what comes
next by message, each working on with what it has read."""

import json
import os
import unittest
from unittest import mock

from helpers import (
    CLAIM,
    FIRST_READ,
    FOUND,
    GOOD,
    IDS,
    QUESTION,
    RESULT,
    STOPPED_B1,
    WAITED,
    WAITS,
    RepoTest,
    run,
)


class RoundTest(RepoTest):
    """A round in which the generator and the first user, once they have replied, are sent what
    comes next by message."""

    def setUp(self):
        super().setUp()
        self.started()
        self.due(self.replied(CLAIM))

    def stopped(self):
        """The first user stops at an item, and the script tells and sends it back to the
        generator by message; the message move."""
        return self.due(self.replied({"items": FIRST_READ}))

    def later(self, reply):
        """What the script prints asked with nothing, while the first pause of its wait has the
        role sent a message write its reply, then handed the role's end."""
        path = self.prompt()["reply"]

        def pause(seconds):
            """The role writes its reply while the flow waits."""
            self.write(path, json.dumps(reply))

        with mock.patch.object(run, "WAIT", 3), mock.patch.object(run.time, "sleep", pause):
            self.assertEqual(self.next(), {"waiting": self.state()["next"]["agent"]})
        return self.next(self.ended(self.state()["next"]))


class TestGeneratorKept(RoundTest):
    def test_a_generator_that_replied_is_sent_the_first_users_stop_by_message(self):
        # Given: a generator that replied, and a first user stopping at an item
        # When: the orchestrator goes on
        # Then: the generator is sent, by its agent ID, the item as the first user gave it and
        # where it replies, and its old reply is removed
        move = self.stopped()
        self.assertEqual(move["tool"], "SendMessage")
        self.assertEqual(move["input"]["to"], IDS["turn:generator"])
        message = json.loads(move["input"]["message"])
        reply = self.kept("generator.json")
        self.assertEqual(message, {"sent_back": [STOPPED_B1], "reply": reply})
        self.assertFalse(os.path.exists(self.kept("generator.json")))

    def test_a_message_keeps_letters_beyond_ascii_as_they_are(self):
        # Given: a first user that says in Japanese what it did where it stopped
        # When: the generator is sent the stop
        # Then: the words stand in the message as they are
        stop = dict(STOPPED_B1, did="冒頭を読んだ")
        move = self.due(self.replied({"items": [FOUND, stop]}))
        self.assertIn("冒頭を読んだ", move["input"]["message"])

    def test_a_reply_is_waited_for_a_second_at_a_time_within_the_shell_s_two_minutes(self):
        # Given: a generator sent the first user's stop, which never replies
        # When: the orchestrator goes on, with the wait as turn has it
        # Then: the script waits a second at a time, a hundred times, then says it is waiting
        self.stopped()
        with mock.patch.object(run, "WAIT", WAITED), mock.patch.object(run.time, "sleep") as sleep:
            self.assertEqual(self.next(), {"waiting": "turn:generator"})
        self.assertEqual(sleep.call_args_list, [mock.call(1)] * 100)

    def test_the_messaged_generators_reply_is_waited_for_and_the_first_user_sent_it(self):
        # Given: a generator sent the first user's stop
        # When: the orchestrator goes on, and the reply comes during the wait
        # Then: the first user, kept started, is sent the work made again by message, with its
        # parts as the remake left them, as a remake may add a section
        self.stopped()
        self.write("README.md", "# x\n\nx does y.\n\n## Use\n\nRun x.\n")
        move = self.due(self.later(CLAIM))
        self.assertEqual(move["input"]["to"], IDS["turn:first-user"])
        expected = {
            "remade": [self.here("README.md")],
            "parts": [self.here("README.md:1-4"), self.here("README.md:5-7")],
            "reply": self.kept("first-user.json"),
        }
        self.assertEqual(json.loads(move["input"]["message"]), expected)

    def test_a_reply_not_come_within_the_wait_leaves_the_run_waiting(self):
        # Given: a generator sent the first user's stop
        # When: the orchestrator goes on and no reply comes within the wait
        # Then: the script says it is still waiting on the generator, and goes on once it comes
        self.stopped()
        with mock.patch.object(run, "WAIT", 2), mock.patch.object(run.time, "sleep") as sleep:
            self.assertEqual(self.next(), {"waiting": "turn:generator"})
        self.assertEqual(sleep.call_count, 2)
        self.assertEqual(self.due(self.later(CLAIM))["tool"], "SendMessage")

    def test_a_reading_before_the_messaged_generator_replied_stops(self):
        # Given: a generator sent a message, not ended yet
        # When: the orchestrator gives a reading of its own, words that are no JSON, or the end
        # of another agent
        # Then: it stops, saying the run waits on the generator's end, by its ID
        self.stopped()
        for given in (CLAIM, "ended", {"ended": "aother"}, {"ended": " "}):
            with self.subTest(given=given):
                self.assertIn(
                    "turn: the run waits on the end of turn:generator, agent agen; once a message"
                    " says it ended, run `turn.py next",
                    self.refused(given),
                )

    def test_a_reply_written_is_taken_only_once_its_role_has_ended(self):
        # Given: a generator sent the first user's stop, which writes its reply and runs on
        # When: the orchestrator goes on with nothing, then with the generator's end
        # Then: the script waits no more once the reply is there, still waiting on the generator,
        # as a role may still change its reply, and takes the reply once it has ended
        self.stopped()
        self.write(self.prompt()["reply"], json.dumps(CLAIM))
        with mock.patch.object(run, "WAIT", WAITED), mock.patch.object(run.time, "sleep") as sleep:
            self.assertEqual(self.next(), {"waiting": "turn:generator"})
        self.assertEqual(sleep.call_count, 0)
        move = self.due(self.next({"ended": IDS["turn:generator"]}))
        self.assertEqual(move["input"]["to"], IDS["turn:first-user"])

    def test_a_role_ended_without_its_reply_is_told_to_write_it(self):
        # Given: a generator sent the first user's stop, which ends without writing its reply
        # When: the orchestrator goes on with its end
        # Then: the generator is sent where to write its reply, and the run waits on its end again
        self.stopped()
        out = self.next({"ended": IDS["turn:generator"]})
        reply = self.kept("generator.json")
        self.assertEqual(
            out["move"]["input"],
            {
                "to": IDS["turn:generator"],
                "message": f"Write your reply to {reply} in your form; it is not there",
            },
        )
        self.assertEqual(self.next(), {"waiting": "turn:generator"})


class TestFirstUserKept(RoundTest):
    def test_a_first_user_finding_every_good_has_the_run_return(self):
        # Given: a first user finding every item's Good
        # When: the orchestrator goes on
        # Then: the run returns, no role of the round sent more
        out = self.replied({"items": [FOUND, dict(FOUND, item="B-1")]})
        self.assertEqual(self.returned(out), {"returned": RESULT})

    def test_the_first_user_sends_back_three_times_a_round_at_most(self):
        # Given: a first user that stops at an item each time it reads
        # When: the round goes on
        # Then: the generator is sent it three times, and the fourth stop ends the round, the
        # item made again in the next
        for _ in range(3):
            self.assertEqual(self.stopped()["input"]["to"], IDS["turn:generator"])
            self.due(self.later(CLAIM))
        out = self.replied({"items": FIRST_READ})
        self.assertIn("round 2", out["line"])

    def test_the_round_s_sending_back_counts_anew_in_the_next_round(self):
        # Given: a first round whose sending back was spent
        # When: the second round's first user stops at an item
        # Then: the generator is sent it again by message
        for _ in range(3):
            self.stopped()
            self.due(self.later(CLAIM))
        self.due(self.replied({"items": FIRST_READ}))
        self.assertEqual(self.due(self.made())["tool"], "Agent")
        self.assertEqual(self.stopped()["input"]["to"], IDS["turn:generator"])

    def test_a_question_from_the_generator_sent_back_is_sent_at_once_then_answered_by_message(
        self,
    ):
        # Given: a generator, sent the first user's stop, that replies with a question
        # When: the orchestrator goes on, and the answer is handed on
        # Then: the run asks at once; the generator is sent the answer by message, and its claim
        # sends the first user the work made again
        self.stopped()
        out = self.later({"items": [GOOD, WAITS], "questions": [QUESTION], "chosen": []})
        self.assertEqual(self.heard(out), {"asked": RESULT})
        move = self.due(self.answered())
        self.assertEqual(move["input"]["to"], IDS["turn:generator"])
        self.assertIn("answers", json.loads(move["input"]["message"]))
        self.assertEqual(self.due(self.later(CLAIM))["input"]["to"], IDS["turn:first-user"])


if __name__ == "__main__":
    unittest.main()
