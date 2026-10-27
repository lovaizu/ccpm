"""Within a round, the generator and the first user, once they have replied, are sent what comes
next by message, each working on with what it has read."""

import fcntl
import json
import os
import unittest
from unittest import mock

from helpers import (
    ANSWER,
    CLAIM,
    END,
    FIRST_READ,
    FOUND,
    FOUND_B1,
    HOOK,
    IDS,
    ITEM_B1,
    MESSAGE,
    OUTSIDE,
    PASSED,
    QUESTION,
    RESULT,
    STOPPED_B1,
    WAITED,
    WAITS,
    RepoTest,
    flow,
)

# The generator's claim once the first user's stop at B-1 is sent back: B-1 alone, mended.
MENDED = {"items": [dict(PASSED, item="B-1")], "questions": [], "chosen": []}


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
        role sent a message write its reply and end, its record holding the message and the reply
        ending its turn."""
        step = self.state()["next"]

        def pause(seconds):
            """The role writes its reply and ends while the flow waits."""
            self.write(step["prompt"]["reply"], json.dumps(reply))
            self.recorded(step["to"], MESSAGE, END)

        with mock.patch.object(flow, "WAIT", 3), mock.patch.object(flow.time, "sleep", pause):
            return self.next()


class TestGeneratorKept(RoundTest):
    def test_a_generator_that_replied_is_sent_the_first_users_stop_by_message(self):
        # Given: a generator that replied, and a first user stopping at an item
        # When: the orchestrator goes on
        # Then: the generator is sent, by its agent ID, the item as the first user gave it, with
        # its files as the CCS names them now, and its old reply is removed
        move = self.stopped()
        self.assertEqual(move["tool"], "SendMessage")
        self.assertEqual(move["input"]["to"], IDS["turn:generator"])
        message = json.loads(move["input"]["message"])
        self.assertEqual(message, dict(self.files("turn:generator"), sent_back=[STOPPED_B1]))
        self.assertFalse(os.path.exists(self.kept("generator.json")))

    def test_a_message_keeps_letters_beyond_ascii_as_they_are(self):
        # Given: a first user that says in Japanese what it did where it stopped
        # When: the generator is sent the stop
        # Then: the words stand in the message as they are
        stop = dict(STOPPED_B1, did="冒頭を読んだ")
        move = self.due(self.replied({"items": [FOUND, stop]}))
        self.assertIn("冒頭を読んだ", move["input"]["message"])

    def test_a_reply_is_waited_for_a_second_at_a_time_within_the_shell_s_ten_minutes(self):
        # Given: a generator sent the first user's stop, which never replies
        # When: the orchestrator goes on, with the wait as turn has it
        # Then: the script waits a second at a time, nine minutes in all, as one move within the
        # ten minutes the orchestrator's step gives the shell, then says it is waiting
        self.stopped()
        with (
            mock.patch.object(flow, "WAIT", WAITED),
            mock.patch.object(flow.time, "sleep") as sleep,
        ):
            self.assertEqual(self.next(), {"waiting": "turn:generator"})
        self.assertEqual(sleep.call_args_list, [mock.call(1)] * 540)

    def test_the_messaged_generators_reply_is_waited_for_and_the_first_user_sent_it(self):
        # Given: a generator sent the first user's stop
        # When: the orchestrator goes on, and the reply comes during the wait
        # Then: the first user, kept started, is sent the work made again by message, with its
        # parts as the remake left them, as a remake may add a section
        self.stopped()
        self.write("README.md", "# x\n\nx does y.\n\n## Use\n\nRun x.\n")
        move = self.due(self.later(MENDED))
        self.assertEqual(move["input"]["to"], IDS["turn:first-user"])
        files = self.files("turn:first-user")
        expected = {
            "remade": files.pop("work"),
            "gaps": MENDED["items"],
            "parts": [self.here("README.md:1-4"), self.here("README.md:5-7")],
            **files,
        }
        self.assertEqual(json.loads(move["input"]["message"]), expected)

    def test_a_reply_not_come_within_the_wait_leaves_the_run_waiting(self):
        # Given: a generator sent the first user's stop
        # When: the orchestrator goes on and no reply comes within the wait
        # Then: the script says it is still waiting on the generator, and goes on once it comes
        self.stopped()
        with mock.patch.object(flow, "WAIT", 2), mock.patch.object(flow.time, "sleep") as sleep:
            self.assertEqual(self.next(), {"waiting": "turn:generator"})
        self.assertEqual(sleep.call_count, 2)
        self.assertEqual(self.due(self.later(MENDED))["tool"], "SendMessage")

    def test_a_second_next_while_the_first_still_waits_stops(self):
        # Given: a generator sent the first user's stop, and a `turn.py next` of the run still
        # waiting on its end, as one Claude Code moved to the background past its timeout
        self.stopped()
        with open(self.kept("next.lock"), "w", encoding="utf-8") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            # When: the orchestrator runs `turn.py next` again
            out = self.refused()
        # Then: it stops, saying the other still runs and to take the move it prints, and takes no
        # move of the run; once the other has ended, the run goes on
        self.assertIn(
            f"turn: another `turn.py next {RESULT}` still runs, waiting on a role's end; wait for"
            " it to end and take the move it prints",
            out,
        )
        self.assertEqual(self.next(), {"waiting": "turn:generator"})

    def test_anything_handed_on_while_a_messaged_role_runs_stops(self):
        # Given: a generator sent a message, not ended yet
        # When: the orchestrator gives a reading of its own, words that are no JSON, or the end
        # of the generator's agent
        # Then: it stops, saying the run reads the generator's end itself, by its ID, and is to be
        # gone on with with nothing
        self.stopped()
        for given in (CLAIM, "ended", {"ended": "agen"}):
            with self.subTest(given=given):
                self.assertIn(
                    "turn: the run waits on the end of turn:generator, agent agen, which it reads"
                    " in the agent's record; run `turn.py next .tasks/readme-result.json` with"
                    " nothing",
                    self.refused(given),
                )

    def test_a_reply_written_is_taken_only_once_its_role_has_ended(self):
        # Given: a generator sent the first user's stop, which writes its reply and runs on, its
        # record holding the message and no reply after it
        # When: the orchestrator goes on with nothing, then again once the record holds the reply
        # ending its turn
        # Then: the script waits the whole wait, as a role may still change its reply, and takes
        # the reply once the role has ended
        self.stopped()
        self.write(self.prompt()["reply"], json.dumps(MENDED))
        self.recorded(IDS["turn:generator"], MESSAGE)
        with (
            mock.patch.object(flow, "WAIT", WAITED),
            mock.patch.object(flow.time, "sleep") as sleep,
        ):
            self.assertEqual(self.next(), {"waiting": "turn:generator"})
        self.assertEqual(sleep.call_count, 540)
        self.recorded(IDS["turn:generator"], END)
        move = self.due(self.next())
        self.assertEqual(move["input"]["to"], IDS["turn:first-user"])

    def test_a_reply_ending_an_earlier_turn_is_not_the_end_of_the_message_sent(self):
        # Given: a generator whose record ends with the reply ending its first turn, sent the first
        # user's stop that has not reached its record yet
        # When: the orchestrator goes on with nothing
        # Then: the script still waits on the generator, not telling it to write a reply
        self.recorded(IDS["turn:generator"], MESSAGE, END)
        self.stopped()
        self.assertEqual(self.next(), {"waiting": "turn:generator"})

    def test_a_reply_a_stop_hook_kept_going_is_not_the_end(self):
        # Given: a generator sent the first user's stop, which wrote its reply and ended its turn,
        # a stop hook then keeping it going
        # When: the orchestrator goes on with nothing, then again once it ends its turn again
        # Then: the script waits on the generator, then takes its reply
        self.stopped()
        self.write(self.prompt()["reply"], json.dumps(MENDED))
        self.recorded(IDS["turn:generator"], MESSAGE, END, HOOK)
        self.assertEqual(self.next(), {"waiting": "turn:generator"})
        self.recorded(IDS["turn:generator"], END)
        self.assertEqual(self.due(self.next())["input"]["to"], IDS["turn:first-user"])

    def test_a_role_ended_without_its_reply_is_told_to_write_it(self):
        # Given: a generator sent the first user's stop, which ends without writing its reply
        # When: the orchestrator goes on with nothing
        # Then: the generator is sent where to write its reply, and the run waits on its end again
        self.stopped()
        self.recorded(IDS["turn:generator"], MESSAGE, END)
        out = self.next()
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
            self.due(self.later(MENDED))
        out = self.replied({"items": FIRST_READ})
        self.assertIn("round 2", self.line_of(out))

    def test_the_round_s_sending_back_counts_anew_in_the_next_round(self):
        # Given: a first round whose sending back was spent
        # When: the second round's first user stops at an item
        # Then: the generator is sent it again by message
        for _ in range(3):
            self.stopped()
            self.due(self.later(MENDED))
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
        out = self.later({"items": [WAITS], "questions": [QUESTION], "chosen": []})
        self.assertEqual(self.heard(out), {"asked": RESULT})
        move = self.due(self.answered())
        self.assertEqual(move["input"]["to"], IDS["turn:generator"])
        self.assertIn("answers", json.loads(move["input"]["message"]))
        self.assertEqual(self.due(self.later(MENDED))["input"]["to"], IDS["turn:first-user"])


# The generator's claim once the first user's stop at B-1 is sent back: B-1 lying outside the
# purpose, with why.
HELD = {"items": [dict(ITEM_B1, outside=OUTSIDE)], "questions": [], "chosen": []}


class TestGaps(RoundTest):
    """A gap the first user sends back is settled by one exchange: the generator mends it or says
    why it lies outside the purpose, and the first user, given that answer, holds it or lets it go;
    a gap still held against the generator's reason is a question of the purpose."""

    def test_a_remake_claims_the_items_sent_back_alone(self):
        # Given: a generator sent the first user's stop at B-1
        self.stopped()
        # When: it claims every item again
        out = self.later(CLAIM)
        # Then: it is sent what is wrong, F-1 not judged in a remake, as an item not sent back
        # stands as it was
        self.assertEqual(out["move"]["input"]["to"], IDS["turn:generator"])
        self.assertIn(
            "checklists/readme.md F-1 is not an item judged here", out["move"]["input"]["message"]
        )

    def test_a_gap_held_outside_the_purpose_reaches_the_first_user_with_its_reason(self):
        # Given: a generator sent the first user's stop at B-1
        self.stopped()
        # When: it says why the gap lies outside the purpose
        out = self.later(HELD)
        # Then: a line says it answered one gap, and the first user is sent the answer with the
        # work, to hold the gap or let it go
        self.assertIn("turn:generator answered 1 gap.", out["line"])
        self.assertEqual(json.loads(out["move"]["input"]["message"])["gaps"], HELD["items"])

    def test_a_gap_let_go_by_the_first_user_lets_the_run_return(self):
        # Given: a generator that held B-1's gap outside the purpose, its answer sent to the
        # first user
        self.stopped()
        self.due(self.later(HELD))
        # When: the first user lets it go, giving B-1 its Good
        out = self.replied({"items": [FOUND, FOUND_B1]})
        # Then: the run returns
        self.assertEqual(self.returned(out), {"returned": RESULT})

    def test_a_gap_still_held_against_the_generator_s_reason_is_a_question_at_once(self):
        # Given: a generator that held B-1's gap outside the purpose, its answer sent to the
        # first user
        self.stopped()
        self.due(self.later(HELD))
        # When: the first user still stops at B-1
        out = self.replied({"items": FIRST_READ})
        # Then: B-1 is shown at once, with the generator's reason, for a question of the purpose,
        # though the round may still send back, as another making would not settle it
        self.assertEqual(
            out,
            {
                "line": "turn: turn:first-user found the Good of 1 of 2 items.",
                "left": [dict(STOPPED_B1, outside=OUTSIDE)],
            },
        )
        self.assertEqual(self.state()["sent"], 1)

    def differed(self, answer):
        """The generator, sent the first user's stop at B-1, holds its gap outside the purpose, the
        first user still holds it, and the question the orchestrator words for it is answered; the
        move then."""
        self.due(self.later(HELD))
        self.replied({"items": FIRST_READ})
        self.next({"items": [WAITS], "questions": [QUESTION]})
        return self.due(self.answered(answer))

    def test_once_answered_the_gap_is_made_again_in_its_round(self):
        # Given: a gap still held against the generator's reason, asked of the calling AI
        self.stopped()
        # When: the answer is handed on
        move = self.differed("MIT")
        # Then: the generator, kept started, is sent the stop with the answer, in the same round,
        # the round's sending back not spent on it
        self.assertEqual(move["input"]["to"], IDS["turn:generator"])
        files = self.files("turn:generator")
        self.assertEqual(
            json.loads(move["input"]["message"]),
            dict(files, sent_back=[STOPPED_B1], answers=[dict(ANSWER, answer="MIT")]),
        )
        self.assertEqual((self.state()["round"], self.state()["sent"]), (1, 1))

    def test_a_gap_settled_again_is_sent_its_own_answer_alone(self):
        # Given: a gap held against the generator's reason and answered, then held so again
        self.stopped()
        self.differed("first")
        # When: the second answer is handed on
        move = self.differed("second")
        # Then: the generator is sent the second answer alone, as it holds the first already
        sent = json.loads(move["input"]["message"])["answers"]
        self.assertEqual([a["answer"] for a in sent], ["second"])

    def test_a_first_user_started_anew_reads_the_work_on_its_own_first(self):
        # Given: a round ending with B-1 without Good, and the next round's generator holding its
        # gap outside the purpose
        with mock.patch.object(flow, "SENDS", 0):
            self.due(self.replied({"items": FIRST_READ}))
        out = self.made(dict(ITEM_B1, outside=OUTSIDE))
        # When: the next round's first user is started, and stops at B-1
        move = self.due(out)
        stop = self.replied({"items": FIRST_READ})
        # Then: it is started without the generator's answer, as it reads the work on its own
        # first, and its stop is sent back to the generator, not asked
        self.assertNotIn(OUTSIDE, move["input"]["prompt"])
        self.assertEqual(stop["move"]["input"]["to"], IDS["turn:generator"])


if __name__ == "__main__":
    unittest.main()
