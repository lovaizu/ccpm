"""Within a round, the generator and the first user, once they have replied, are sent what comes
next by message, each working on with what it has read."""

import fcntl
import json
import os
import shutil
import sys
import unittest
from unittest import mock

from helpers import (
    CLAIM,
    END,
    FIRST_READ,
    FOUND,
    FOUND_B1,
    HOOK,
    IDS,
    MADE,
    MESSAGE,
    NEEDED_B1,
    QUESTION,
    RESULT,
    WAITED,
    WAITS,
    RepoTest,
    flow,
)

# The generator's claim once what the receiver would need at B-1 is sent: B-1 alone, made again.
MENDED = {"items": [dict(MADE, item="B-1")], "questions": [], "chosen": []}


class RoundTest(RepoTest):
    """A round in which the generator and the first user, once they have replied, are sent what
    comes next by message."""

    def setUp(self):
        super().setUp()
        self.started()
        self.due(self.replied(CLAIM))

    def sent_need(self):
        """The first user finds no Good for an item, and the script tells and sends what the
        receiver would need to the generator by message; the message move."""
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
    def test_a_generator_that_replied_is_sent_what_the_receiver_would_need_by_message(self):
        # Given: a generator that replied, and a first user finding no Good for an item
        # When: the orchestrator goes on
        # Then: the generator is sent, by its agent ID, the item with what the receiver would need,
        # as the first user gave it, with its files as the CCS names them now, and its old reply is
        # removed
        move = self.sent_need()
        self.assertEqual(move["tool"], "SendMessage")
        self.assertEqual(move["input"]["to"], IDS["turn:generator"])
        message = json.loads(move["input"]["message"])
        self.assertEqual(message, dict(self.files("turn:generator"), needs=[NEEDED_B1]))
        self.assertFalse(os.path.exists(self.kept("generator.json")))

    def test_a_message_keeps_letters_beyond_ascii_as_they_are(self):
        # Given: a first user that says in Japanese what the receiver would need
        # When: the generator is sent it
        # Then: the words stand in the message as they are
        need = dict(NEEDED_B1, need="冒頭を読んだ")
        move = self.due(self.replied({"items": [FOUND, need]}))
        self.assertIn("冒頭を読んだ", move["input"]["message"])

    def test_a_reply_is_waited_for_a_second_at_a_time_within_the_shell_s_ten_minutes(self):
        # Given: a generator sent the first user's need, which has it and never replies
        # When: the orchestrator goes on, with the wait as turn has it
        # Then: the script waits a second at a time, nine minutes in all, as one move within the
        # ten minutes the orchestrator's step gives the shell, then says it is waiting
        self.sent_need()
        self.recorded(IDS["turn:generator"], MESSAGE)
        with (
            mock.patch.object(flow, "WAIT", WAITED),
            mock.patch.object(flow.time, "sleep") as sleep,
        ):
            self.assertEqual(self.next(), {"waiting": "turn:generator"})
        self.assertEqual(sleep.call_args_list, [mock.call(1)] * 540)

    def test_the_messaged_generators_reply_is_waited_for_and_the_first_user_sent_it(self):
        # Given: a generator sent the first user's need
        # When: the orchestrator goes on, and the reply comes during the wait
        # Then: the first user, kept started, is sent the work made again by message, with its
        # parts as the remake left them, as a remake may add a section
        self.sent_need()
        self.write("README.md", "# x\n\nx does y.\n\n## Use\n\nRun x.\n")
        move = self.due(self.later(MENDED))
        self.assertEqual(move["input"]["to"], IDS["turn:first-user"])
        files = self.files("turn:first-user")
        expected = {
            "remade": files.pop("work"),
            "parts": [self.here("README.md:1-4"), self.here("README.md:5-7")],
            **files,
        }
        self.assertEqual(json.loads(move["input"]["message"]), expected)

    def test_a_reply_not_come_within_the_wait_leaves_the_run_waiting(self):
        # Given: a generator sent the first user's need, which has it
        # When: the orchestrator goes on and no reply comes within the wait
        # Then: the script says it is still waiting on the generator, and goes on once it comes
        self.sent_need()
        self.recorded(IDS["turn:generator"], MESSAGE)
        with mock.patch.object(flow, "WAIT", 2), mock.patch.object(flow.time, "sleep") as sleep:
            self.assertEqual(self.next(), {"waiting": "turn:generator"})
        self.assertEqual(sleep.call_count, 2)
        self.assertEqual(self.due(self.later(MENDED))["tool"], "SendMessage")

    def test_a_second_next_while_the_first_still_waits_stops(self):
        # Given: a generator sent the first user's need, which has it, and a `turn.py next` of the
        # run still waiting on its end, as one Claude Code moved to the background past its timeout
        self.sent_need()
        self.recorded(IDS["turn:generator"], MESSAGE)
        with open(self.kept("next.lock"), "w", encoding="utf-8") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            # When: the orchestrator runs `turn.py next` again, on z/OS too, a machine with fcntl
            # whose name is "zos"
            with mock.patch.object(flow.sys, "platform", "zos"):
                self.assertIn("another `turn.py next", self.refused())
            out = self.refused()
        # Then: it stops, saying the other still runs and to take the move it prints, and takes no
        # move of the run; once the other has ended, the run goes on
        self.assertIn(
            f"turn: another `turn.py next {RESULT}` still runs, waiting on a role's end; wait for"
            " it to end and take the move it prints",
            out,
        )
        self.assertEqual(self.next(), {"waiting": "turn:generator"})

    def test_a_machine_without_fcntl_holds_the_run_by_msvcrt(self):
        # Given: a generator sent the first user's need, which has it, on a machine with no fcntl,
        # Windows, whose msvcrt locks the file's first byte, already locked by another
        self.sent_need()
        self.recorded(IDS["turn:generator"], MESSAGE)
        msvcrt = mock.Mock(LK_NBLCK=2, **{"locking.side_effect": OSError})
        with (
            mock.patch.object(flow.sys, "platform", "win32"),
            mock.patch.dict(sys.modules, {"msvcrt": msvcrt}),
        ):
            # When: the orchestrator runs `turn.py next`
            out = self.refused()
        # Then: it stops as another still runs, having asked msvcrt for the byte without waiting
        self.assertIn(f"turn: another `turn.py next {RESULT}` still runs", out)
        (fd, mode, size), _ = msvcrt.locking.call_args
        self.assertEqual((type(fd), mode, size), (int, 2, 1))

    def test_anything_handed_on_while_a_messaged_role_runs_stops(self):
        # Given: a generator sent a message, not ended yet
        # When: the orchestrator gives a reading of its own, words that are no JSON, or the end
        # of the generator's agent
        # Then: it stops, saying the run reads the generator's end itself, by its ID, and is to be
        # gone on with with nothing
        self.sent_need()
        for given in (CLAIM, "ended", {"ended": "agen"}):
            with self.subTest(given=given):
                self.assertIn(
                    "turn: the run waits on the end of turn:generator, agent agen, which it reads"
                    " in the agent's record; run `turn.py next .tasks/readme-result.json` with"
                    " nothing",
                    self.refused(given),
                )

    def test_a_reply_written_is_taken_only_once_its_role_has_ended(self):
        # Given: a generator sent the first user's need, which writes its reply and runs on, its
        # record holding the message and no reply after it
        # When: the orchestrator goes on with nothing, then again once the record holds the reply
        # ending its turn
        # Then: the script waits the whole wait, as a role may still change its reply, and takes
        # the reply once the role has ended
        self.sent_need()
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

    def test_a_message_not_come_within_the_wait_is_sent_again(self):
        # Given: a generator whose record ends with the reply ending its first turn, sent the first
        # user's need, which has not reached its record by the end of the wait, as a message
        # printed by a `turn.py next` Claude Code moved to the background reaches no one
        sent = self.sent_need()
        # When: the orchestrator goes on with nothing
        out = self.next()
        # Then: the reply ending the earlier turn is not taken as the end, and the move sending the
        # message is printed again, with no line, as no role starts; once it comes and the
        # generator ends, its reply is taken
        self.assertEqual(out, {"move": sent})
        self.assertEqual(self.due(self.later(MENDED))["input"]["to"], IDS["turn:first-user"])

    def test_a_role_whose_record_is_not_found_stops_the_run_saying_what_it_needs(self):
        # Given: a generator sent the first user's need, and Claude Code's records not where turn
        # reads them
        self.sent_need()
        shutil.rmtree(os.path.join(self.config, "projects"))
        # When: the orchestrator goes on with nothing
        out = self.next()
        # Then: the run stops, as it cannot tell the generator's end, telling the caller what it
        # tried, confirmed and not, and needs; it goes on only by a call again
        projects = os.path.join(self.config, "projects")
        self.assertEqual(
            out["line"],
            f"turn: turn:generator stopped: it needs Claude Code's records under {projects}, the"
            " folder CLAUDE_CONFIG_DIR names or ~/.claude where it names none, holding the record"
            " of each agent the run starts.",
        )
        self.assertEqual(
            out["stopped"]["not_confirmed"],
            "whether turn:generator has ended, as no record of agent agen is there",
        )
        self.assertIn("for 0 seconds", out["stopped"]["tried"])
        self.assertIn(
            "the run stopped, as turn:generator needs Claude Code's records", self.refused()
        )

    def test_a_reply_a_stop_hook_kept_going_is_not_the_end(self):
        # Given: a generator sent the first user's need, which wrote its reply and ended its turn,
        # a stop hook then keeping it going
        # When: the orchestrator goes on with nothing, then again once it ends its turn again
        # Then: the script waits on the generator, then takes its reply
        self.sent_need()
        self.write(self.prompt()["reply"], json.dumps(MENDED))
        self.recorded(IDS["turn:generator"], MESSAGE, END, HOOK)
        self.assertEqual(self.next(), {"waiting": "turn:generator"})
        self.recorded(IDS["turn:generator"], END)
        self.assertEqual(self.due(self.next())["input"]["to"], IDS["turn:first-user"])

    def test_a_role_ended_without_its_reply_is_told_to_write_it(self):
        # Given: a generator sent the first user's need, which ends without writing its reply
        # When: the orchestrator goes on with nothing
        # Then: the generator is sent where to write its reply, and the run waits on its end again,
        # once the message has reached it
        self.sent_need()
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
        self.recorded(IDS["turn:generator"], MESSAGE)
        self.assertEqual(self.next(), {"waiting": "turn:generator"})


class TestFirstUserKept(RoundTest):
    def test_a_first_user_finding_every_good_has_the_run_return(self):
        # Given: a first user finding every item's Good
        # When: the orchestrator goes on
        # Then: the run returns, no role of the round sent more
        out = self.replied({"items": [FOUND, dict(FOUND, item="B-1")]})
        self.assertEqual(self.returned(out), {"returned": RESULT})

    def test_the_first_user_sends_back_three_times_a_round_at_most(self):
        # Given: a first user that finds no Good for an item each time it reads
        # When: the round goes on
        # Then: the generator is sent it three times, and the fourth reading without it ends the
        # round, the item made again in the next
        for _ in range(3):
            self.assertEqual(self.sent_need()["input"]["to"], IDS["turn:generator"])
            self.due(self.later(MENDED))
        out = self.replied({"items": FIRST_READ})
        self.assertIn("round 2", self.line_of(out))

    def test_the_round_s_sending_back_counts_anew_in_the_next_round(self):
        # Given: a first round whose sending back was spent
        # When: the second round's first user finds no Good for an item
        # Then: the generator is sent it again by message
        for _ in range(3):
            self.sent_need()
            self.due(self.later(MENDED))
        self.due(self.replied({"items": FIRST_READ}))
        self.assertEqual(self.due(self.made())["tool"], "Agent")
        self.assertEqual(self.sent_need()["input"]["to"], IDS["turn:generator"])

    def test_a_question_from_the_generator_sent_a_need_is_asked_at_once_then_answered_by_message(
        self,
    ):
        # Given: a generator, sent the first user's need, that replies with a question
        # When: the orchestrator goes on, and the answer is handed on
        # Then: the run asks at once; the generator is sent the answer by message, and its claim
        # sends the first user the work made again
        self.sent_need()
        out = self.later({"items": [WAITS], "questions": [QUESTION], "chosen": []})
        self.assertEqual(self.heard(out), {"asked": RESULT})
        move = self.due(self.answered())
        self.assertEqual(move["input"]["to"], IDS["turn:generator"])
        self.assertIn("answers", json.loads(move["input"]["message"]))
        self.assertEqual(self.due(self.later(MENDED))["input"]["to"], IDS["turn:first-user"])


class TestNeeds(RoundTest):
    """What the receiver would need, as the first user gives it, reaches the generator, which makes
    the work again for it, and the first user reads the work made again."""

    def test_a_remake_claims_the_items_sent_alone(self):
        # Given: a generator sent what the receiver would need at B-1
        self.sent_need()
        # When: it claims every item again
        out = self.later(CLAIM)
        # Then: it is sent what is wrong, F-1 not judged in a remake, as an item not sent back
        # stands as it was
        self.assertEqual(out["move"]["input"]["to"], IDS["turn:generator"])
        self.assertIn(
            "checklists/readme.md F-1 is not an item judged here", out["move"]["input"]["message"]
        )

    def test_a_remake_is_told_as_made_again_for_the_items_sent(self):
        # Given: a generator sent what the receiver would need at B-1
        self.sent_need()
        # When: it claims B-1 made again
        out = self.later(MENDED)
        # Then: a line says it made the work again for one item, and the first user is sent the
        # work made again, with nothing of the generator's claim
        self.assertIn("turn:generator made README.md again for 1 item.", out["line"])
        self.assertNotIn("items", json.loads(out["move"]["input"]["message"]))

    def test_an_item_given_its_good_on_the_remake_lets_the_run_return(self):
        # Given: a generator that made the work again for B-1, the first user sent it
        self.sent_need()
        self.due(self.later(MENDED))
        # When: the first user finds B-1's Good
        out = self.replied({"items": [FOUND, FOUND_B1]})
        # Then: the run returns
        self.assertEqual(self.returned(out), {"returned": RESULT})

    def test_an_item_still_without_good_is_sent_again_while_the_round_may_send(self):
        # Given: a generator that made the work again for B-1, the first user sent it
        self.sent_need()
        self.due(self.later(MENDED))
        # When: the first user still finds no Good for B-1
        out = self.replied({"items": FIRST_READ})
        # Then: the generator is sent what the receiver would need again, no question asked, as
        # the round may still send
        self.assertEqual(out["move"]["input"]["to"], IDS["turn:generator"])
        self.assertEqual(json.loads(out["move"]["input"]["message"])["needs"], [NEEDED_B1])
        self.assertEqual(self.state()["sent"], 2)


if __name__ == "__main__":
    unittest.main()
