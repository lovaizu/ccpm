"""The generator's claim taken: the first user started on the work made, or the generator's
questions asked at once."""

import json
import os
import unittest

from helpers import (
    ANSWER,
    ASKED,
    CALL,
    GOOD,
    IDS,
    ITEM_B1,
    QUESTION,
    RESULT,
    WAITS,
    ReadTest,
    state,
)


class TestMade(ReadTest):
    def test_the_generator_is_given_what_it_makes_the_work_from_and_where_it_replies(self):
        # Given: a run started
        # When: the generator is to be started
        # Then: its prompt names the work, the checklists, the call's test, nothing sent back
        # yet, no answers, no choice of an earlier claim, the result, and its reply file beside
        # it, beside the files it makes the work from, which the start's tests hold
        prompt = self.prompt()
        del prompt["given"]
        self.assertEqual(
            prompt,
            {
                "work": [self.here("README.md")],
                "checklists": [self.here("checklists/readme.md")],
                "test": "sh tests/readme.sh",
                "sent_back": [],
                "answers": [],
                "chosen": [],
                "result": self.here(RESULT),
                "reply": self.kept("generator.json"),
            },
        )

    def test_the_generators_claim_starts_the_first_user_with_what_the_receiver_has(self):
        # Given: a call naming what the receiver reads the work for and what they have with it,
        # and a generator that replied with every item's Good
        # When: the orchestrator goes on
        # Then: the first user is to be started with the work, what the receiver has, who the
        # receiver is and what for, and the checklists, and not the CCS or the claim
        move = self.due(self.made())
        self.assertEqual(move["input"]["subagent_type"], "turn:first-user")
        self.assertEqual(
            json.loads(move["input"]["prompt"]),
            {
                "given": [
                    self.here("README.md"),
                    self.here("docs/start.md"),
                    self.here("checklists/readme.md"),
                ],
                "work": [self.here("README.md")],
                "checklists": [self.here("checklists/readme.md")],
                "receiver": ["a developer new to it"],
                "use": ["to try it on their own files"],
                "parts": [self.here("README.md:1-3")],
                "reply": self.kept("first-user.json"),
            },
        )
        self.assertNotIn(GOOD["good"], move["input"]["prompt"])

    def test_a_generator_asking_before_making_anything_has_the_question_sent_at_once(self):
        # Given: a generator replying, before making anything, with a question only the user can
        # answer, naming the item that waits on it alone
        # When: the orchestrator goes on
        # Then: the run asks at once, with no first user started, the result not written, and
        # the question is printed with the item it settles
        out = self.replied({"items": [WAITS], "questions": [QUESTION], "chosen": []})
        self.assertEqual(self.heard(out), {"asked": RESULT})
        self.assertNotIn("next", self.state())
        self.assertFalse(os.path.exists(RESULT))
        self.assertEqual(json.loads(self.turn("questions", RESULT)[1]), ASKED)

    def test_questions_are_printed_with_letters_beyond_ascii_as_they_are(self):
        # Given: a question asked in Japanese
        # When: the questions are asked for
        # Then: its words are printed as they are
        asked = dict(QUESTION, question="どのライセンスで公開しますか")
        self.replied({"items": [WAITS], "questions": [asked], "chosen": []})
        self.assertIn("どのライセンスで公開しますか", self.turn("questions", RESULT)[1])

    def asked_first(self):
        """The generator asks before making anything, the run asks the calling AI, and its answer
        is handed on; what the script prints then."""
        self.replied({"items": [WAITS], "questions": [QUESTION], "chosen": []})
        return self.answered()

    def test_going_on_with_no_answer_while_a_question_waits_stops(self):
        # Given: a run whose generator asked a question
        # When: the orchestrator goes on with nothing, or with blanks alone
        # Then: it stops, saying the run waits on the calling AI's answer, and still waits
        self.replied({"items": [WAITS], "questions": [QUESTION], "chosen": []})
        for given in ("", " \n"):
            with self.subTest(given=given):
                out = self.refused(given) if given else self.refused()
                self.assertIn("the run waits on the calling AI's answer", out)
        self.assertEqual(self.state()["stage"], "asked")

    def test_the_questions_when_none_is_asked_stop(self):
        # Given: a run whose generator is due, and no run at all
        # When: the questions are asked for
        # Then: it stops, saying no question is asked now, or that no run is going
        for result, said in ((RESULT, "asks no question now"), ("none.json", "no run is going")):
            with self.subTest(result=result):
                code, out = self.turn("questions", result)
                self.assertEqual(code, 1)
                self.assertIn(said, out)

    def test_the_answer_is_sent_by_message_to_the_generator_that_asked(self):
        # Given: a generator that asked before making anything
        # When: the calling AI's answer is handed on
        # Then: the generator, kept started, is sent the question and the answer as it came
        move = self.due(self.asked_first())
        self.assertEqual(move["input"]["to"], IDS["turn:generator"])
        reply = self.kept("generator.json")
        self.assertEqual(
            json.loads(move["input"]["message"]), {"answers": [ANSWER], "reply": reply}
        )

    def test_an_answer_that_lays_the_work_out_anew_has_the_run_started_again(self):
        # Given: a generator that asked before making anything, and a CCS the calling AI added a
        # file of the work to with the answer
        self.replied({"items": [WAITS], "questions": [QUESTION], "chosen": []})
        self.laid_out_anew()
        # When: the answer is handed on, with nothing again, and the run started again
        # Then: the run is to be started again, and is to be till it is; then the generator is
        # started anew on the work of both files, given the answer
        self.assertEqual(self.answered(), {"anew": RESULT})
        self.assertEqual(self.next(), {"anew": RESULT})
        self.turn("start", json.dumps(CALL))
        prompt = json.loads(self.due(self.next())["input"]["prompt"])
        self.assertEqual(prompt["work"], [self.here("README.md"), self.here("LICENSE")])
        self.assertEqual(prompt["answers"][0]["answer"], "MIT")

    def test_a_generator_asking_again_is_sent_the_new_answer_alone(self):
        # Given: a generator sent the answer to its question, which asks another
        # When: the second answer is handed on
        # Then: the generator is sent the second answer alone, as it holds the first already
        self.due(self.asked_first())
        second = dict(QUESTION, question="Which name?")
        self.replied({"items": [WAITS], "questions": [second], "chosen": []})
        move = self.due(self.answered("csvtidy"))
        sent = json.loads(move["input"]["message"])["answers"]
        self.assertEqual(
            sent, [{"questions": [dict(second, items=[ITEM_B1])], "answer": "csvtidy"}]
        )

    def test_the_generator_sent_the_answer_goes_on_to_the_first_user(self):
        # Given: a generator sent the calling AI's answer to its question
        # When: it replies with every item's Good
        # Then: the first user is started on the work
        self.due(self.asked_first())
        self.assertEqual(self.due(self.made())["input"]["subagent_type"], "turn:first-user")

    def test_a_question_found_while_making_is_sent_at_once(self):
        # Given: a generator whose claim gives one item's Good and has the other wait on a question
        # When: the orchestrator goes on
        # Then: the run asks at once, before the first user reads
        self.assertEqual(self.heard(self.made(GOOD, WAITS)), {"asked": RESULT})
        self.assertEqual(json.loads(self.turn("questions", RESULT)[1]), ASKED)

    def test_a_generator_started_that_ended_without_its_reply_is_told_to_write_it(self):
        # Given: a generator started, whose Agent call returned with no reply written
        # When: the orchestrator goes on with the agent ID, then gives a reading of its own
        # Then: the generator is sent where to write its reply, with no line for the user, as it
        # neither starts nor ends a role, and the reading stops, the run waiting on the generator's
        # end and going on
        reply = self.kept("generator.json")
        out = self.next({"agent_id": IDS["turn:generator"]})
        self.assertNotIn("line", out)
        self.assertEqual(
            out["move"]["input"],
            {
                "to": IDS["turn:generator"],
                "message": f"Write your reply to {reply} in your form; it is not there",
            },
        )
        reading = json.dumps({"items": [GOOD, WAITS], "questions": [QUESTION]})
        self.assertIn("waits on the end of turn:generator", self.refused(reading))
        self.assertTrue(os.path.exists(state.state_path(RESULT)))

    def test_going_on_without_the_agent_id_of_a_role_started_stops(self):
        # Given: a run whose generator was started
        # When: the orchestrator goes on with no agent ID, or one of no words
        # Then: it stops, asking for the agent ID the Agent call gave back
        for given in ("", "x", '{"agent_id": " "}', "[]"):
            with self.subTest(given=given):
                self.assertIn("give the agent ID the Agent call", self.refused(given))

    def test_a_claim_leaving_an_item_out_or_without_its_questions_is_sent_back(self):
        # Given: a generator whose claim leaves an item out, or holds no list of questions
        # When: the orchestrator goes on
        # Then: the generator is sent what is wrong, to write its reply again
        for claim, said in (
            ({"items": [GOOD], "questions": [], "chosen": []}, "B-1 is left out"),
            ({"items": [GOOD, dict(GOOD, item="B-1")], "chosen": []}, '"questions": [...]'),
            ({"items": [GOOD, dict(GOOD, item="B-1")], "questions": []}, '"chosen": [...]'),
        ):
            with self.subTest(said=said):
                out = self.replied(claim)
                self.assertEqual(out["move"]["input"]["to"], IDS["turn:generator"])
                self.assertIn(said, out["move"]["input"]["message"])

    def test_the_parts_of_the_work_are_printed_when_asked(self):
        # Given: a run going
        # When: the parts of its work are asked for
        # Then: each part is printed as its lines
        code, out = self.turn("parts", RESULT)
        self.assertEqual((code, json.loads(out)), (0, {"parts": [self.here("README.md:1-3")]}))

    def test_going_on_for_a_result_never_started_stops(self):
        # Given: no run going at a path
        # When: the orchestrator goes on, asks for the parts or a page there
        # Then: it is stopped, saying how to start one
        for argv in (("next", "none.json"), ("parts", "none.json"), ("next", "none.json", "1")):
            with self.subTest(argv=argv):
                code, out = self.turn(*argv)
                self.assertEqual(code, 1)
                self.assertIn("no run is going with its result at none.json", out)


if __name__ == "__main__":
    unittest.main()
