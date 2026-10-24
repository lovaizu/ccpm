import json
import os
from unittest import mock

from helpers import (
    CALL,
    CAN,
    CHECKED,
    FIRST_READ,
    FOUND,
    GOOD,
    HOLDS,
    IDS,
    QUESTION,
    RESULT,
    STOPPED,
    UNTRUE,
    WAITS,
    RepoTest,
    run,
)

# The generator's claim of every item's Good.
CLAIM = {"items": [GOOD, dict(GOOD, item="B-1")], "questions": []}


class RoundTest(RepoTest):
    """A round in which the generator and the first user, once they have replied, are sent what
    comes next by message."""

    def setUp(self):
        super().setUp()
        self.started()
        self.first = self.due(self.replied(CLAIM))

    def stopped(self):
        """The first user stops at an item, and the script tells and sends it back to the
        generator by message; the message move."""
        return self.due(self.replied({"items": FIRST_READ}))

    def later(self, reply):
        """What the script prints asked with nothing, while the first pause of its wait has the
        role sent a message write its reply."""
        path = self.prompt()["reply"]

        def pause(seconds):
            self.write(path, json.dumps(reply))

        with mock.patch.object(run, "WAIT", 3), mock.patch.object(run.time, "sleep", pause):
            return self.next()


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
        reply = self.here(RESULT + ".generator.json")
        self.assertEqual(message, {"sent_back": [STOPPED], "reply": reply})
        self.assertFalse(os.path.exists(RESULT + ".generator.json"))

    def test_a_message_keeps_letters_beyond_ascii_as_they_are(self):
        # Given: a first user that says in Japanese what it did where it stopped
        # When: the generator is sent the stop
        # Then: the words stand in the message as they are
        stop = dict(STOPPED, did="冒頭を読んだ")
        move = self.due(self.replied({"items": [FOUND, stop]}))
        self.assertIn("冒頭を読んだ", move["input"]["message"])

    def test_a_reply_is_waited_for_a_second_at_a_time_within_the_shell_s_two_minutes(self):
        # Given: a generator sent the first user's stop, which never replies
        # When: the orchestrator goes on, with the wait as turn has it
        # Then: the script waits a second at a time, a hundred times, then says it is waiting
        self.stopped()
        self.waiting.stop()
        with mock.patch.object(run.time, "sleep") as sleep:
            self.assertEqual(self.next(), {"waiting": "turn:generator"})
        self.assertEqual(sleep.call_args_list, [mock.call(1)] * 100)
        self.waiting.start()

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
            "parts": ["README.md:1-4", "README.md:5-7"],
            "reply": self.here(RESULT + ".first-user.json"),
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
        # Given: a generator sent a message, not replied yet
        # When: the orchestrator gives a reading of its own
        # Then: it stops, saying the run waits on the generator
        self.stopped()
        self.assertIn("waits on turn:generator's reply", self.refused(CLAIM))


class TestFirstUserKept(RoundTest):
    def test_a_first_user_finding_every_good_has_the_orchestrator_check_them(self):
        # Given: a first user finding every item's Good
        # When: the orchestrator goes on
        # Then: no role is started; the orchestrator is shown the Goods to check
        out = self.replied({"items": [FOUND, dict(FOUND, item="B-1")]})
        self.assertNotIn("next", self.state())
        self.assertEqual(self.heard(out), {"goods": [FOUND, dict(FOUND, item="B-1")]})

    def test_the_first_user_sends_back_three_times_a_round_at_most(self):
        # Given: a first user that stops at an item each time it reads
        # When: the round goes on
        # Then: the generator is sent it three times, and the fourth stop goes to the check of the
        # Good the first user found
        for _ in range(3):
            self.assertEqual(self.stopped()["input"]["to"], IDS["turn:generator"])
            self.due(self.later(CLAIM))
        out = self.replied({"items": FIRST_READ})
        self.assertEqual(self.heard(out), {"goods": [FOUND]})

    def test_the_round_s_sending_back_counts_anew_in_the_next_round(self):
        # Given: a first round whose sending back was spent, and its Good checked to hold
        # When: the second round's first user stops at an item
        # Then: the generator is sent it again by message
        for _ in range(3):
            self.stopped()
            self.due(self.later(CLAIM))
        self.replied({"items": FIRST_READ})
        self.next()
        self.due(self.next({"items": [HOLDS]}))
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
        out = self.later({"items": [GOOD, WAITS], "questions": [QUESTION]})
        self.assertEqual(self.heard(out), {"asked": RESULT})
        move = self.due(self.answered())
        self.assertEqual(move["input"]["to"], IDS["turn:generator"])
        self.assertIn("answers", json.loads(move["input"]["message"]))
        self.assertEqual(self.due(self.later(CLAIM))["input"]["to"], IDS["turn:first-user"])


class TestTold(RepoTest):
    def test_each_move_is_told_first_by_a_line_the_flow_makes(self):
        # Given: a run checked to give every item its Good
        # When: the orchestrator goes on, and once more
        # Then: the line telling the calling AI what comes next, how far and how is sent to
        # `main` first, then the move itself; the line the flow prints is the message
        self.turn("start", json.dumps(CALL))
        out = self.next({"items": CAN, "questions": []})
        line = (
            "turn: turn:up found in the CCS what gives the Good of 2 items. Next, turn:generator"
            " will make the work to give every item its Good, and run what it gives as the"
            " receiver would, of README.md, for 2 items, round 1."
        )
        self.assertEqual(out["line"], line)
        self.assertEqual(
            out["move"], {"tool": "SendMessage", "input": {"to": "main", "message": line}}
        )
        move = self.next()["move"]
        self.assertEqual(move["tool"], "Agent")
        self.assertEqual(move["input"]["description"], "turn turn:generator")
        out = self.replied(CLAIM)
        self.assertTrue(
            str(out["line"]).startswith("turn: turn:generator made README.md. Next,"), out
        )

    def test_the_orchestrators_check_is_told_first_and_its_outcome_after(self):
        # Given: a run started
        # When: the orchestrator goes on, then gives its check
        # Then: a line telling the check is sent to `main` before the check is shown, and the
        # line after it says what the check found
        self.turn("start", json.dumps(CALL))
        out = self.next()
        line = (
            "turn: Next, turn:up will check that the CCS gives every item its Good, of README.md,"
            " for 2 items, round 1."
        )
        self.assertEqual(
            out,
            {
                "line": line,
                "move": {"tool": "SendMessage", "input": {"to": "main", "message": line}},
            },
        )
        self.assertEqual(self.next()["check"][0]["item"], "F-1")
        out = self.next({"items": CAN, "questions": []})
        self.assertTrue(
            str(out["line"]).startswith(
                "turn: turn:up found in the CCS what gives the Good of 2 items. Next,"
                " turn:generator will"
            ),
            out,
        )

    def test_a_question_is_told_before_it_is_asked_and_the_answer_before_the_check(self):
        # Given: a run started and told its check
        # When: the check finds an item waiting on the user's answer, and the run goes on, and
        # on once answered
        # Then: a line says what the check found and that the question is asked, before the run
        # asks; once answered, a line says so before the check is shown again
        self.turn("start", json.dumps(CALL))
        self.next()
        out = self.next({"items": [CAN[0], WAITS], "questions": [QUESTION]})
        self.assertEqual(
            out["line"],
            "turn: turn:up found 1 of 2 items waiting on the user's answer. Next, turn:up will ask"
            " what only the user can decide, of README.md, for 2 items, round 1.",
        )
        self.assertEqual(self.next(), {"asked": RESULT})
        out = self.answered()
        self.assertTrue(
            str(out["line"]).startswith("turn: The calling AI answered. Next, turn:up will check"),
            out,
        )
        self.assertEqual(self.next()["check"][1]["item"], "B-1")

    def test_the_good_check_s_outcome_is_told_before_the_next_round(self):
        # Given: a first user finding one item's Good, with the round's sending back spent
        # When: the orchestrator's check says the Good does not hold
        # Then: a line says how many Goods hold and that the second round's generator makes the
        # work next
        self.started()
        self.first_read(FOUND)
        out = self.held(UNTRUE)
        self.assertEqual(
            out["line"],
            "turn: turn:up found 0 of 1 Goods hold. Next, turn:generator will make the work to give"
            " every item its Good, and run what it gives as the receiver would, of README.md, for"
            " 2 items, round 2.",
        )

    def test_a_learner_giving_no_lesson_is_told_before_the_run_returns(self):
        # Given: every item's Good found and held, and a learner giving no lesson
        # When: the orchestrator goes on
        # Then: a line says the learner gave none before the run returns, with the result
        # written by then
        self.started()
        self.first_read(FOUND, dict(FOUND, item="B-1"))
        self.due(self.held())
        out = self.replied({"lessons": [], "checked": CHECKED})
        self.assertEqual(
            out["line"],
            "turn: turn:learner gave 0 lessons from the run. Next, turn:up will return the result,"
            " of README.md, for 2 items, round 1.",
        )
        self.assertEqual(self.read_json(RESULT)["items"], [FOUND, dict(FOUND, item="B-1")])
        self.assertEqual(self.next(), {"returned": RESULT})
        self.assertFalse(os.path.exists(run.state_path(RESULT)))

    def test_a_judgment_due_is_told_again_on_a_call_again(self):
        # Given: a run whose check was told
        # When: the same call is made again
        # Then: the check is told again before it is shown
        self.turn("start", json.dumps(CALL))
        self.next()
        self.turn("start", json.dumps(CALL))
        self.assertEqual(self.next()["move"]["input"]["to"], "main")

    def test_a_move_is_printed_with_letters_beyond_ascii_as_they_are(self):
        # Given: a work named in letters beyond ASCII
        # When: its move is printed
        # Then: the letters stand as they are
        ccs = self.read_json(CALL["ccs"])
        ccs["focal_entities"][0] = {"deliverable": "読む.md"}
        self.write_json(CALL["ccs"], ccs)
        self.write("読む.md", "# x\n")
        self.turn("start", json.dumps(CALL))
        self.turn("next", RESULT, stdin=json.dumps({"items": CAN, "questions": []}))
        self.assertIn("読む.md", self.turn("next", RESULT)[1])


class TestResumed(RepoTest):
    def test_a_call_again_on_a_run_kept_goes_on_from_its_move(self):
        # Given: a run whose first user is due, and a run waiting on the check
        # When: the same call is made again
        # Then: it goes on from that move, told again, and the check is shown again
        self.started()
        self.due(self.replied(CLAIM))
        code, out = self.turn("start", json.dumps(CALL))
        self.assertEqual((code, json.loads(out)["result"]), (0, self.here(RESULT)))
        move = self.due(self.next())
        self.assertEqual(move["input"]["subagent_type"], "turn:first-user")
        self.turn("start", json.dumps(dict(CALL, result="other.json")))
        self.turn("start", json.dumps(dict(CALL, result="other.json")))
        self.result = "other.json"
        self.assertEqual(self.heard(self.next())["check"][0]["item"], "F-1")

    def test_a_call_again_on_a_ccs_laid_out_anew_checks_it_again(self):
        # Given: a run whose first user is due, and a CCS that now names another file of the work
        self.started()
        self.due(self.replied(CLAIM))
        self.laid_out_anew()
        # When: the same call is made again
        code, out = self.turn("start", json.dumps(CALL))
        self.assertEqual(code, 0, out)
        # Then: the items are checked again on the CCS as it is now, no role due
        self.assertEqual(self.heard(self.next())["check"], self.state()["items"])
        self.assertEqual(self.state()["work"], ["README.md", "LICENSE"])
        self.assertNotIn("next", self.state())

    def test_a_kept_role_due_a_message_is_started_anew_with_what_was_sent_to_it_since(self):
        # Given: a run whose generator, kept started, was sent two items back in turn, and is due
        # the next
        # When: the same call is made again
        # Then: the generator is started anew with what it was given first and every message
        # since, the one due among them, and no role is kept started any more
        self.started()
        self.due(self.replied(CLAIM))
        sent = self.due(self.replied({"items": FIRST_READ}))
        first = json.loads(sent["input"]["message"])
        self.turn("start", json.dumps(CALL))
        self.assertNotIn("started", self.state())
        move = self.due(self.next())
        self.assertEqual(move["tool"], "Agent")
        prompt = json.loads(move["input"]["prompt"])
        self.assertEqual(prompt["since"], [first])
        self.assertEqual(prompt["sent_back"], [])
        # The same, called again before the message due was moved.
        super().setUp()
        self.started()
        self.due(self.replied(CLAIM))
        self.replied({"items": FIRST_READ})
        self.turn("start", json.dumps(CALL))
        prompt = json.loads(self.due(self.next())["input"]["prompt"])
        self.assertEqual(
            prompt["since"], [dict(first, reply=self.here(RESULT + ".generator.json"))]
        )

    def test_a_run_waiting_on_an_answer_asks_again_on_a_call_again(self):
        # Given: a run whose generator asked before making anything, the question sent
        # When: the same call is made again, and the answer is handed on
        # Then: the question is told and asked again; the generator, its conversation gone, is
        # started anew with the answer in what it is given
        self.started()
        self.heard(self.made(WAITS))
        self.turn("start", json.dumps(CALL))
        self.assertEqual(self.heard(self.next()), {"asked": RESULT})
        self.assertEqual(len(json.loads(self.turn("questions", RESULT)[1])["questions"]), 1)
        move = self.due(self.answered())
        self.assertEqual(move["tool"], "Agent")
        prompt = json.loads(move["input"]["prompt"])
        self.assertEqual((prompt["sent_back"], len(prompt["answers"])), ([], 1))

    def test_a_run_stopped_after_the_first_user_s_reading_goes_on_from_the_check(self):
        # Given: a run whose first user's reading ended, the Goods waiting on the check
        # When: the same call is made again
        # Then: the check is told again and the same Goods are shown, with no role started anew
        self.started()
        self.first_read(FOUND)
        self.turn("start", json.dumps(CALL))
        self.assertEqual(self.heard(self.next()), {"goods": [FOUND]})
        self.assertNotIn("next", self.state())

    def test_a_call_again_with_another_call_on_the_same_result_stops(self):
        # Given: a run kept for a result
        # When: another call names the same result
        # Then: it stops, saying a run of another call is kept there
        self.started()
        other = dict(CALL, kind=dict(CALL["kind"], has="decisions"))
        code, out = self.turn("start", json.dumps(other))
        self.assertEqual(code, 1)
        self.assertIn("a run of another call is kept at", out)

    def test_a_call_again_on_a_ccs_gone_wrong_stops(self):
        # Given: a run kept, whose CCS was taken away
        # When: the same call is made again
        # Then: it stops, as turn cannot take it
        self.started()
        os.remove(CALL["ccs"])
        code, out = self.turn("start", json.dumps(CALL))
        self.assertEqual(code, 1)
        self.assertIn("is not there", out)


class TestFolderMoved(RepoTest):
    """The session's working folder moves when the calling AI runs `cd`, and every agent's commands
    and hooks then run from there; the run's paths still mean where the call was made."""

    def test_the_start_gives_the_result_where_the_call_was_made(self):
        # Given: a call naming its result relative to the folder it is made from
        # When: the run starts
        # Then: the result is given as a whole path, so the orchestrator reaches it from anywhere
        code, out = self.turn("start", json.dumps(CALL))
        self.assertEqual((code, json.loads(out)["result"]), (0, os.path.join(self.repo, RESULT)))

    def test_the_start_gives_what_the_orchestrator_reads_where_the_call_was_made(self):
        # Given: a call naming its CCS relative to the folder it is made from
        # When: the run starts
        # Then: what the orchestrator reads is given as whole paths
        code, out = self.turn("start", json.dumps(CALL))
        self.assertEqual((code, json.loads(out)["given"][0]), (0, self.here(CALL["ccs"])))

    def test_each_role_is_given_whole_paths_of_where_the_call_was_made(self):
        # Given: a run started, and the session's working folder moved to notes/
        # When: the orchestrator goes on with the result the start gave
        # Then: the generator's prompt names each file as a whole path in the folder the call was
        # made from, as its hooks and its commands run from notes/
        self.turn("start", json.dumps(CALL))
        os.chdir("notes")
        self.result = os.path.join(self.repo, RESULT)
        move = json.loads(self.due(self.next({"items": CAN, "questions": []}))["input"]["prompt"])
        here = os.path.join(self.repo, "{}").format
        self.assertEqual(move["work"], [here("README.md")])
        self.assertEqual(move["checklists"], [here("checklists/readme.md")])
        self.assertEqual(move["reply"], here(RESULT + ".generator.json"))
        self.assertIn(here(CALL["ccs"]), move["given"])

    def test_a_round_goes_on_from_another_folder_with_lines_named_by_whole_paths(self):
        # Given: a run started, and the session's working folder moved to notes/
        # When: the generator replies at the whole path it was given, with lines named by whole
        # paths, and the first user is due
        # Then: the reply is taken, and the first user is given the work's parts as the run names
        # them and whole paths for its files
        self.started()
        os.chdir("notes")
        self.result = os.path.join(self.repo, RESULT)
        lines = [os.path.join(self.repo, "README.md:1-3")]
        out = self.made(dict(GOOD, lines=lines), dict(GOOD, item="B-1", lines=lines))
        prompt = json.loads(self.due(out)["input"]["prompt"])
        self.assertEqual(prompt["parts"], ["README.md:1-3"])
        self.assertEqual(prompt["given"][0], os.path.join(self.repo, "README.md"))
        code, out = self.turn("parts", self.result)
        self.assertEqual((code, json.loads(out)), (0, {"parts": ["README.md:1-3"]}))
