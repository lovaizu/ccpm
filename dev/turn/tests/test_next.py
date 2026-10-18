import json

from helpers import (
    CALL,
    EVALUATED,
    FOUND,
    GOOD,
    LEARNT,
    QUESTION,
    READ_SHOWN,
    SENT_BACK,
    WAITS,
    RepoTest,
)

RESULT = CALL["result"]


def judged(item):
    """An item's finding without the checklist and ID that name it."""
    return {k: v for k, v in item.items() if k not in ("checklist", "item")}


ITEM_B1 = {"checklist": "checklists/readme.md", "item": "B-1"}


class ReadTest(RepoTest):
    def setUp(self):
        super().setUp()
        self.started()

    def read(self, reading):
        return self.read_text(json.dumps(reading))

    def read_text(self, text):
        return self.turn("next", RESULT, stdin=text)


class TestReading(ReadTest):
    def test_a_reading_that_sends_items_back_gives_the_generator_them(self):
        # Given: a reading that finds one item's Good and sends the other back
        # When: the reading is recorded
        # Then: the generator is to be started again with the item sent back and what the receiver
        # gets once it has its Good
        out = self.next({"items": [GOOD, SENT_BACK], "questions": []})
        self.assertEqual(out["agent"], "turn:generator")
        self.assertEqual(self.given()["sent_back"], [SENT_BACK])
        self.assertEqual(self.read_json(RESULT)["running"]["next"]["prompt"], out["prompt"])

    def test_a_reading_with_every_item_good_or_waiting_starts_the_first_user(self):
        # Given: a call naming what the receiver reads the work for and what they open with it, and
        # a reading that finds one item's Good and has the other wait on a question
        # When: the reading is recorded
        # Then: the first user is to be started with the work, what the receiver opens, who the
        # receiver is and what for, and the checklists, and not the CCS or the reading
        call = dict(CALL, kind=dict(CALL["kind"], use="purpose", opens="page"))
        self.started(call)
        out = self.next({"items": [GOOD, WAITS], "questions": [QUESTION]})
        self.assertEqual(out["agent"], "turn:first-user")
        self.assertEqual(
            self.given(),
            {
                "work": ["README.md"],
                "opens": ["docs/start.md"],
                "receiver": ["a developer new to it"],
                "use": ["to try it on their own files"],
                "checklists": ["checklists/readme.md"],
            },
        )

    def test_a_reading_given_after_the_run_returned_stops(self):
        # Given: a run that has returned
        # When: another reading is given
        # Then: it stops, saying the run has returned and how to start one
        self.through(EVALUATED)
        code, out = self.read({"items": [GOOD, WAITS], "questions": [QUESTION]})
        self.assertEqual(code, 1)
        self.assertIn("no run is going", out)
        self.assertIn("turn.py start", out)

    def test_a_reading_for_a_result_never_started_stops(self):
        # Given: a result path no run was started for
        # When: a reading is given for it
        # Then: it stops, naming the path
        code, out = self.turn("next", "elsewhere.json", stdin="{}")
        self.assertEqual(code, 1)
        self.assertIn("elsewhere.json", out)

    def test_what_a_role_is_given_for_a_result_never_started_stops(self):
        # Given: a result path no run was started for
        # When: a role asks what it is given there
        # Then: it stops, naming the path
        code, out = self.turn("given", "elsewhere.json")
        self.assertEqual(code, 1)
        self.assertIn("elsewhere.json", out)

    def test_a_reading_in_a_json_fence_is_recorded(self):
        # Given: a reading given as JSON inside a ```json fence
        # When: it is recorded
        # Then: it is taken as the reading itself
        reading = json.dumps({"items": [GOOD, SENT_BACK], "questions": []})
        code, out = self.read_text(f"```json\n{reading}\n```\n")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.given()["sent_back"], [SENT_BACK])


class TestReaders(ReadTest):
    def test_the_evaluator_is_started_with_the_first_users_reading(self):
        # Given: a run whose first user has replied with the Good it found for one item
        # When: the orchestrator goes on
        # Then: the evaluator is to be started with what the first user was, and its reading
        out = self.next({"items": [GOOD, WAITS], "questions": [QUESTION]})
        first = self.given()
        self.replied("turn:first-user", out["prompt"], {"items": [FOUND]})
        out = self.next()
        self.assertEqual(out["agent"], "turn:evaluator")
        self.assertEqual(self.given(), dict(first, reading=[FOUND]))

    def test_going_on_before_the_first_user_replies_stops(self):
        # Given: a run whose first user is to be started
        # When: the orchestrator goes on before it has replied
        # Then: it stops, saying to start the first user with the prompt printed and wait
        self.next({"items": [GOOD, WAITS], "questions": [QUESTION]})
        self.assertIn("start turn:first-user", self.refused())

    def test_an_evaluator_agreeing_with_the_findings_writes_the_result(self):
        # Given: findings with one item's Good and the other waiting, and an evaluator giving a
        # Good to the first item alone
        # When: the orchestrator goes on
        # Then: the result holds where the work is, the orchestrator's Good with its lines, and the
        # question with its recommended answer and the item it settles, and the run has returned
        self.assertEqual(self.through(EVALUATED), {"returned": RESULT})
        self.assertEqual(
            self.read_json(RESULT),
            {
                "work": ["README.md"],
                "items": [GOOD],
                "questions": [dict(QUESTION, items=[ITEM_B1])],
                "not_good": [],
            },
        )

    def test_a_result_at_the_top_of_the_repository_is_written(self):
        # Given: a run whose result goes at the top of the repository, in no folder
        # When: it returns
        # Then: the result is written there
        self.started(dict(CALL, result="result.json"))
        reading = {"items": [GOOD, WAITS], "questions": [QUESTION]}
        _, out = self.turn("next", "result.json", stdin=json.dumps(reading))
        self.replied("turn:first-user", json.loads(out)["prompt"], {"items": []})
        _, out = self.turn("next", "result.json")
        self.replied("turn:evaluator", json.loads(out)["prompt"], {"items": [EVALUATED]})
        code, out = self.turn("next", "result.json")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.read_json("result.json")["items"], [GOOD])

    def test_items_judged_apart_go_to_the_orchestrator_to_decide(self):
        # Given: findings with one item's Good and the other waiting on a question, an evaluator
        # giving no Good to the first and a Good to the second, and a first user that read the
        # work
        # When: the orchestrator goes on
        # Then: both items come back to decide, each with the orchestrator's finding, the
        # evaluator's Good and the first user's, with the questions, and the run goes on
        good_b1 = dict(EVALUATED, item="B-1")
        out = self.through(good_b1, opened=READ_SHOWN)
        self.assertEqual(
            out,
            {
                "decide": {
                    "items": [
                        dict(
                            ITEM_B1,
                            item="F-1",
                            orchestrator=judged(GOOD),
                            evaluator=None,
                            first_user=judged(FOUND),
                        ),
                        dict(
                            ITEM_B1,
                            orchestrator=judged(WAITS),
                            evaluator=judged(good_b1),
                            first_user=None,
                        ),
                    ],
                    "questions": [QUESTION],
                }
            },
        )
        self.assertIn("running", self.read_json(RESULT))


class TestDecision(ReadTest):
    def setUp(self):
        super().setUp()
        self.through(dict(EVALUATED, item="B-1"))

    def test_a_decision_with_every_item_good_or_waiting_writes_the_result(self):
        # Given: both items to decide
        # When: the orchestrator gives the first Good and has the second wait on a new question
        # Then: the result holds the Good and the new question alone, as no item waits on the
        # findings' question any more
        new = {"question": "Which name?", "recommended": "csvtidy"}
        out = self.next({"items": [GOOD, dict(WAITS, question=2)], "questions": [new]})
        self.assertEqual(out, {"returned": RESULT})
        self.assertEqual(
            self.read_json(RESULT),
            {
                "work": ["README.md"],
                "items": [GOOD],
                "questions": [dict(new, items=[ITEM_B1])],
                "not_good": [],
            },
        )

    def test_a_decision_may_ask_a_new_question_or_keep_one(self):
        # Given: both items to decide, with one question asked in the findings
        # When: the orchestrator has the first wait on a new question, numbered after the findings',
        # and the second still wait on the findings' question
        # Then: the result holds both questions, numbered from 1, each with the item it settles
        new = {"question": "Which name?", "recommended": "csvtidy"}
        decision = {"items": [dict(WAITS, item="F-1", question=2), WAITS], "questions": [new]}
        self.assertEqual(self.next(decision), {"returned": RESULT})
        self.assertEqual(
            self.read_json(RESULT)["questions"],
            [dict(QUESTION, items=[ITEM_B1]), dict(new, items=[dict(ITEM_B1, item="F-1")])],
        )

    def test_the_items_to_decide_are_printed_again_when_asked_with_no_decision(self):
        # Given: a run waiting on the orchestrator's decision
        # When: the orchestrator runs the script with no input
        # Then: it is shown the items to decide again, and the run still waits on its decision
        first = self.read_json(RESULT)["running"]["decide"]
        self.assertEqual(self.next(), {"decide": first})
        self.assertIn("decide", self.read_json(RESULT)["running"])

    def test_a_decision_out_of_its_form_stops(self):
        # Given: both items to decide
        # When: the decision leaves one out, waits on a question not asked, or asks one no item
        # waits on
        # Then: it stops, naming what is wrong, and the run goes on
        new = {"question": "Which name?", "recommended": "csvtidy"}
        for decision, said in (
            ({"items": [GOOD], "questions": []}, "left out"),
            ({"items": [GOOD, dict(WAITS, question=3)], "questions": [new]}, "question 3"),
            ({"items": [GOOD, WAITS], "questions": [new]}, "question 2"),
        ):
            with self.subTest(decision=decision):
                self.assertIn(said, self.refused(decision))
                self.assertIn("running", self.read_json(RESULT))


class TestLearner(ReadTest):
    def setUp(self):
        super().setUp()
        self.through(dict(EVALUATED, item="B-1"))
        self.learner = self.next({"items": [GOOD, SENT_BACK], "questions": []})

    def test_an_item_left_without_good_starts_the_learner(self):
        # Given: a first reading whose decision leaves an item without Good
        # When: the decision is recorded
        # Then: the learner is to be started with every item's finding and the record of every
        # role that replied in the run
        self.assertEqual(self.learner["agent"], "turn:learner")
        records = [
            f"{self.repo}/session/subagents/agent-{a}.jsonl" for a in ("first-user", "evaluator")
        ]
        self.assertEqual(
            self.given(),
            {"findings": [GOOD, SENT_BACK], "records": records},
        )

    def test_what_the_learner_found_goes_to_the_generator_with_what_was_sent_back(self):
        # Given: a learner that replied with what makes each item's Good
        # When: the orchestrator goes on
        # Then: the generator is to make the work again with the item without Good and what the
        # learner found
        self.replied("turn:learner", self.learner["prompt"], {"items": LEARNT})
        out = self.next()
        self.assertEqual(out["agent"], "turn:generator")
        prompt = self.given()
        self.assertEqual((prompt["sent_back"], prompt["learnt"]), ([SENT_BACK], LEARNT))

    def test_an_item_still_without_good_after_the_second_reading_is_returned(self):
        # Given: a work made again with what the learner found
        # When: its second reading leaves an item without Good
        # Then: the run returns with that item and what the receiver gets once it has its Good,
        # and no learner is started again
        self.replied("turn:learner", self.learner["prompt"], {"items": LEARNT})
        self.next()
        self.through(dict(EVALUATED, item="B-1"))
        out = self.next({"items": [GOOD, SENT_BACK], "questions": []})
        self.assertEqual(out, {"returned": RESULT})
        self.assertEqual(
            self.read_json(RESULT),
            {"work": ["README.md"], "items": [GOOD], "questions": [], "not_good": [SENT_BACK]},
        )


class TestReadingForm(ReadTest):
    def stops(self, reading, *said):
        code, out = self.turn(
            "next", RESULT, stdin=reading if isinstance(reading, str) else json.dumps(reading)
        )
        self.assertEqual(code, 1, out)
        for words in said:
            self.assertIn(words, out)
        self.assertIn("running", self.read_json(RESULT))

    def test_a_reading_that_is_not_json_stops(self):
        # Given: a reading that is not a JSON object of items and questions
        # When: it is recorded
        # Then: it stops, saying the shape to give
        self.stops("good", '{"items": [...], "questions": [...]}')
        self.stops("[]", '{"items": [...], "questions": [...]}')
        self.stops('{"items": []}', '{"items": [...], "questions": [...]}')

    def test_an_item_left_out_or_given_twice_stops(self):
        # Given: a reading missing an item, or giving one twice, or naming one no checklist holds
        # When: it is recorded
        # Then: it stops, naming the item
        self.stops({"items": [GOOD], "questions": []}, "B-1", "left out")
        self.stops({"items": [GOOD, GOOD, SENT_BACK], "questions": []}, "F-1", "twice")
        self.stops(
            {"items": [GOOD, SENT_BACK, dict(SENT_BACK, item="B-9")], "questions": []},
            "B-9",
            "not an item judged here",
        )

    def test_an_item_with_none_or_two_of_good_question_and_gets_stops(self):
        # Given: an item with neither a Good, a question nor what the receiver gets, or with two
        # When: it is recorded
        # Then: it stops, naming the item and the three shapes it may take
        bare = {"checklist": "checklists/readme.md", "item": "B-1"}
        both = dict(SENT_BACK, question=1)
        for item in (bare, both):
            with self.subTest(item=item):
                self.stops(
                    {"items": [GOOD, item], "questions": [QUESTION]},
                    "B-1",
                    '"good" with "lines", "question" or "gets"',
                )

    def test_a_good_without_lines_or_with_empty_words_stops(self):
        # Given: a Good with no lines, or with no words
        # When: it is recorded
        # Then: it stops, naming the item
        for good in (dict(GOOD, lines=[]), dict(GOOD, good=" ")):
            with self.subTest(good=good):
                self.stops({"items": [good, SENT_BACK], "questions": []}, "F-1")

    def test_lines_outside_the_work_stop(self):
        # Given: a Good whose lines name a file that is not the work, lines past its end, or lines
        # not in the form path:from-to
        # When: it is recorded
        # Then: it stops, naming the lines and the form they take
        for lines in (["docs/start.md:1"], ["README.md:2-9"], ["README.md:3-1"], ["README.md"]):
            with self.subTest(lines=lines):
                self.stops(
                    {"items": [dict(GOOD, lines=lines), SENT_BACK], "questions": []},
                    lines[0],
                    "<path>:<from>-<to>",
                )

    def test_a_question_number_with_no_question_stops(self):
        # Given: an item waiting on question 2 where one question is given
        # When: it is recorded
        # Then: it stops, naming the number
        self.stops({"items": [GOOD, dict(WAITS, question=2)], "questions": [QUESTION]}, "2")

    def test_a_question_that_is_not_a_number_stops(self):
        # Given: an item waiting on a question named by its words, not its number
        # When: it is recorded
        # Then: it stops, saying to give the question's number
        waits = dict(WAITS, question="Which license?")
        self.stops({"items": [GOOD, waits], "questions": [QUESTION]}, "not a number")

    def test_a_question_without_a_recommended_answer_stops(self):
        # Given: a question with no recommended answer
        # When: it is recorded
        # Then: it stops, saying each question has one
        self.stops(
            {"items": [GOOD, WAITS], "questions": [{"question": "Which license?"}]},
            '"recommended"',
        )

    def test_a_question_no_item_waits_on_stops(self):
        # Given: a question no item waits on
        # When: it is recorded
        # Then: it stops, naming the question
        self.stops({"items": [GOOD, SENT_BACK], "questions": [QUESTION]}, "question 1")
