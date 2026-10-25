"""The orchestrator's check of the CCS before any work is made, the questions it asks the calling AI
and the run going on with the answer."""

import json
import os
import unittest

from helpers import (
    ASKED,
    CALL,
    CAN,
    CHECKLIST,
    ITEM_B1,
    ITEM_F1,
    QUESTION,
    RESULT,
    WAITS,
    RepoTest,
)


class TestCheck(RepoTest):
    def setUp(self):
        super().setUp()
        code, out = self.turn("start", json.dumps(CALL))
        self.assertEqual(code, 0, out)
        self.heard(self.next())

    def asked(self):
        """The check finding one item waiting on a question, told, and the run asking it."""
        return self.heard(self.next({"items": [CAN[0], WAITS], "questions": [QUESTION]}))

    def test_a_check_in_a_json_fence_is_recorded(self):
        # Given: a check given as JSON inside a ```json fence
        # When: it is recorded
        # Then: it is taken as the check itself, and the generator is to be told and started
        check = json.dumps({"items": CAN, "questions": []})
        code, out = self.turn("next", RESULT, stdin=f"```json\n{check}\n```\n")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.state()["next"]["agent"], "turn:generator")

    def test_the_items_to_check_are_printed_again_when_asked_with_no_check(self):
        # Given: a run started
        # When: the script is asked to go on with no check given
        # Then: it prints the items to check again
        self.assertEqual(self.next()["check"], [ITEM_F1, ITEM_B1])

    def test_a_check_with_an_item_waiting_on_a_question_asks_it_before_any_work(self):
        # Given: a check finding what gives one item its Good and nothing in the CCS for the other
        # When: the check is recorded, and the questions are asked for
        # Then: the run asks at once, with no role started, and the question is printed with the
        # item it settles; the result is not written, as the question is not kept in it
        self.assertEqual(self.asked(), {"asked": RESULT})
        self.assertNotIn("next", self.state())
        code, out = self.turn("questions", RESULT)
        self.assertEqual((code, json.loads(out)), (0, ASKED))
        self.assertFalse(os.path.exists(RESULT))

    def test_questions_are_printed_with_letters_beyond_ascii_as_they_are(self):
        # Given: a question asked in Japanese
        # When: the questions are asked for
        # Then: its words are printed as they are
        asked = dict(QUESTION, question="どのライセンスで公開しますか")
        self.heard(self.next({"items": [CAN[0], WAITS], "questions": [asked]}))
        self.assertIn("どのライセンスで公開しますか", self.turn("questions", RESULT)[1])

    def test_once_answered_the_check_is_made_again_on_the_ccs(self):
        # Given: a run that asked a question, and a CCS the calling AI added the answer to, in a
        # file the CCS named before
        self.asked()
        self.write("notes/readme.decisions.md", "# Decisions\n\nMIT\n")
        # When: the orchestrator goes on with the answer
        out = self.answered()
        # Then: a line says the calling AI answered and that the check is made again, and the
        # items are checked again
        self.assertTrue(
            str(out["line"]).startswith("turn: The calling AI answered. Next, turn:up will check"),
            out,
        )
        self.assertEqual(self.next()["check"], [ITEM_F1, ITEM_B1])

    def test_an_answer_laying_the_run_out_anew_has_the_run_started_again(self):
        # Given: a run that asked a question, and a CCS the calling AI added a checklist to with
        # the answer
        self.asked()
        ccs = self.read_json(CALL["ccs"])
        ccs["retrieved_artifacts"].append({"checklist": "checklists/more.md"})
        self.write_json(CALL["ccs"], ccs)
        self.write("checklists/more.md", CHECKLIST.replace("B-1", "B-3"))
        # When: the orchestrator goes on with the answer, and with nothing again
        # Then: the run is to be started again, and is to be till it is
        self.assertEqual(self.answered(), {"anew": RESULT})
        self.assertEqual(self.next(), {"anew": RESULT})

    def test_the_run_started_again_checks_every_item_as_the_ccs_now_names_them(self):
        # Given: a run whose answer added a checklist to the CCS
        self.asked()
        ccs = self.read_json(CALL["ccs"])
        ccs["retrieved_artifacts"].append({"checklist": "checklists/more.md"})
        self.write_json(CALL["ccs"], ccs)
        self.write("checklists/more.md", CHECKLIST.replace("B-1", "B-3"))
        self.answered()
        # When: the run is started again with the same call
        code, out = self.turn("start", json.dumps(CALL))
        # Then: it gives the checklist added to read, and the check, told with the answer, holds
        # the items of both checklists
        self.assertEqual(code, 0, out)
        self.assertIn(self.here("checklists/more.md"), json.loads(out)["given"])
        line = str(self.next()["line"])
        self.assertTrue(line.startswith("turn: The calling AI answered. Next, turn:up will"), line)
        check = self.next()["check"]
        self.assertEqual([i["item"] for i in check], ["F-1", "B-1", "F-1", "B-3"])

    def test_a_ccs_laid_out_as_before_by_the_time_the_run_goes_on_is_checked_again(self):
        # Given: a run whose answer added a file of notes to the CCS, taken out again before the
        # orchestrator goes on
        self.asked()
        ccs = self.read_json(CALL["ccs"])
        self.write_json(CALL["ccs"], dict(ccs, more=[{"decisions": "notes/answer.md"}]))
        self.write("notes/answer.md", "MIT\n")
        self.assertEqual(self.answered(), {"anew": RESULT})
        self.write_json(CALL["ccs"], ccs)
        # When: the orchestrator goes on with nothing
        # Then: the run goes on to the check made again
        self.assertEqual(self.heard(self.next())["check"], [ITEM_F1, ITEM_B1])

    def test_the_answer_is_given_to_the_generator_where_it_is_started_next(self):
        # Given: a run whose check asked a question
        # When: the calling AI's answer is handed on, and the check made again finds every Good
        # Then: the generator is started with the question and the answer as it came
        self.asked()
        self.heard(self.answered("MIT, as the user chose\n"))
        self.due(self.next({"items": CAN, "questions": []}))
        self.assertEqual(self.prompt()["answers"], [dict(ASKED, answer="MIT, as the user chose")])

    def test_going_on_with_no_answer_while_a_question_waits_stops(self):
        # Given: a run that asked a question
        # When: the orchestrator goes on with nothing, or with blanks alone
        # Then: it stops, saying the run waits on the calling AI's answer, and still waits
        self.asked()
        for given in ("", " \n"):
            with self.subTest(given=given):
                out = self.refused(given) if given else self.refused()
                self.assertIn("the run waits on the calling AI's answer", out)
        self.assertEqual(self.state()["stage"], "asked")

    def test_the_questions_when_none_is_asked_stop(self):
        # Given: a run waiting on the check, and no run at all
        # When: the questions are asked for
        # Then: it stops, saying no question is asked now, or that no run is going
        for result, said in ((RESULT, "asks no question now"), ("none.json", "no run is going")):
            with self.subTest(result=result):
                code, out = self.turn("questions", result)
                self.assertEqual(code, 1)
                self.assertIn(said, out)

    def test_the_questions_before_the_run_asks_them_stop(self):
        # Given: a check finding an item waiting on a question, the asking told and not yet done
        self.next({"items": [CAN[0], WAITS], "questions": [QUESTION]})
        # When: the questions are asked for
        code, out = self.turn("questions", RESULT)
        # Then: it stops, saying no question is asked now
        self.assertEqual(code, 1)
        self.assertIn("asks no question now", out)

    def test_a_check_out_of_its_form_stops(self):
        # Given: a check leaving an item out, giving one empty words, or one a Good
        # When: the check is recorded
        # Then: it is stopped, naming each place to fill and the command to run again, and the run
        # waits on the check still
        for items, said in (
            ([CAN[0]], "B-1 is left out"),
            ([CAN[0], dict(CAN[1], can=" ")], 'empty "can"'),
            ([CAN[0], dict(ITEM_B1, good="x", lines=["README.md:1-1"])], "must hold"),
        ):
            with self.subTest(said=said):
                out = self.refused({"items": items, "questions": []})
                self.assertIn("the check is not filled", out)
                self.assertIn(said, out)
                self.assertIn("again with the check filled", out)
        self.assertEqual(self.next()["check"], [ITEM_F1, ITEM_B1])


if __name__ == "__main__":
    unittest.main()
