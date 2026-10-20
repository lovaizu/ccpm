import json

from helpers import (
    CALL,
    CAN,
    CHECKED,
    CHECKLIST,
    EACH,
    EACH_GOOD,
    EVALUATED,
    FOUND,
    GOOD,
    LESSON,
    PARTS,
    QUESTION,
    READ_SHOWN,
    SECTIONED,
    SENT_BACK,
    STOPPED,
    WAITS,
    RepoTest,
)

RESULT = CALL["result"]


def judged(item):
    """An item's finding without the checklist and ID that name it."""
    return {k: v for k, v in item.items() if k not in ("checklist", "item")}


ITEM_F1 = {"checklist": "checklists/readme.md", "item": "F-1"}
ITEM_B1 = {"checklist": "checklists/readme.md", "item": "B-1"}
# A first user's stop at the item waiting on a question.
WAITS_READ = dict(STOPPED, places=["README.md:3-3"])
# The orchestrator's decision keeping the claim: the first item Good, the other waiting.
AGREED = {"items": [GOOD, WAITS], "questions": []}


class ReadTest(RepoTest):
    def setUp(self):
        super().setUp()
        self.started()


class TestCheck(RepoTest):
    def setUp(self):
        super().setUp()
        code, out = self.turn("start", json.dumps(CALL))
        self.assertEqual(code, 0, out)

    def test_what_a_role_is_given_before_the_check_stops(self):
        # Given: a run started, whose check is not given yet
        # When: a role asks what it is given
        # Then: it is stopped, as no role is started before the check
        code, out = self.turn("given", RESULT)
        self.assertEqual(code, 1)
        self.assertIn("no role is started", out)

    def test_a_check_in_a_json_fence_is_recorded(self):
        # Given: a check given as JSON inside a ```json fence
        # When: it is recorded
        # Then: it is taken as the check itself, and the generator is to be started
        check = json.dumps({"items": CAN, "questions": []})
        code, out = self.turn("next", RESULT, stdin=f"```json\n{check}\n```\n")
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(out)["agent"], "turn:generator")

    def test_the_items_to_check_are_printed_again_when_asked_with_no_check(self):
        # Given: a run started
        # When: the script is asked to go on with no check given
        # Then: it prints the items to check again
        self.assertEqual(self.next(), {"check": [ITEM_F1, ITEM_B1]})

    def test_a_check_with_an_item_waiting_on_a_question_returns_the_questions_alone(self):
        # Given: a check finding what gives one item its Good and nothing in the CCS for the other
        # When: the check is recorded
        # Then: the run returns with no work made, the result holding the question alone with the
        # item it settles
        out = self.next({"items": [CAN[0], WAITS], "questions": [QUESTION]})
        self.assertEqual(out, {"returned": RESULT})
        self.assertEqual(self.read_json(RESULT), {"questions": [dict(QUESTION, items=[ITEM_B1])]})

    def test_a_check_out_of_its_form_stops(self):
        # Given: a check leaving an item out, giving one empty words, or one a Good
        # When: the check is recorded
        # Then: it is stopped, naming each place to fill, and the run waits on the check still
        for items, said in (
            ([CAN[0]], "B-1 is left out"),
            ([CAN[0], dict(CAN[1], can=" ")], 'empty "can"'),
            ([CAN[0], dict(ITEM_B1, good="x", lines=["README.md:1-1"])], "must hold"),
        ):
            with self.subTest(said=said):
                code, out = self.turn(
                    "next", RESULT, stdin=json.dumps({"items": items, "questions": []})
                )
                self.assertEqual(code, 1)
                self.assertIn("the check is not filled", out)
                self.assertIn(said, out)
        self.assertEqual(self.next(), {"check": [ITEM_F1, ITEM_B1]})


class TestMade(ReadTest):
    def test_the_generators_claim_starts_the_first_user_with_what_the_receiver_has(self):
        # Given: a call naming what the receiver reads the work for and what they have with it,
        # and a generator that replied with one item's Good and the other waiting on a question
        # When: the orchestrator goes on
        # Then: the first user is to be started with the work, what the receiver has, who the
        # receiver is and what for, and the checklists, and not the CCS or the claim, with no
        # reading of the orchestrator between
        self.started()
        out = self.made(GOOD, WAITS)
        self.assertEqual(out["agent"], "turn:first-user")
        self.assertEqual(
            self.given(),
            {
                "work": ["README.md"],
                "has": ["docs/start.md"],
                "receiver": ["a developer new to it"],
                "use": ["to try it on their own files"],
                "checklists": ["checklists/readme.md"],
                "parts": ["README.md:1-3"],
                "lessons": [],
            },
        )

    def test_a_reading_of_the_orchestrator_between_the_roles_stops(self):
        # Given: a run waiting on the generator's reply, and one waiting on the first user's
        # When: the orchestrator gives a reading of its own
        # Then: it stops, saying the run waits on the role's reply, and the run goes on
        reading = json.dumps({"items": [GOOD, WAITS], "questions": [QUESTION]})
        code, out = self.turn("next", RESULT, stdin=reading)
        self.assertEqual(code, 1, out)
        self.assertIn("waits on turn:generator's reply, not on yours", out)
        self.made(GOOD, WAITS)
        code, out = self.turn("next", RESULT, stdin=reading)
        self.assertEqual(code, 1, out)
        self.assertIn("waits on turn:first-user's reply", out)
        self.assertIn("running", self.read_json(RESULT))

    def test_going_on_before_the_generator_replies_stops(self):
        # Given: a run whose generator is to be started
        # When: the orchestrator goes on before it has replied
        # Then: it stops, saying to start the generator with the prompt printed and wait
        self.assertIn("start turn:generator", self.refused())

    def test_the_parts_of_the_work_are_printed_when_asked(self):
        # Given: a run whose work is a README of a title, an opening and one section
        # When: the parts are asked for, and asked for a result no run was started for
        # Then: the parts are printed, each as its lines; and the second stops, naming the path
        self.write("README.md", SECTIONED)
        self.assertEqual(self.turn("parts", RESULT), (0, json.dumps({"parts": PARTS}) + "\n"))
        code, out = self.turn("parts", "elsewhere.json")
        self.assertEqual(code, 1)
        self.assertIn("elsewhere.json", out)

    def test_a_decision_given_after_the_run_returned_stops(self):
        # Given: a run that has returned
        # When: another decision is given
        # Then: it stops, saying the run has returned and how to start one
        self.through(EVALUATED)
        self.learnt(self.next(AGREED))
        code, out = self.turn("next", RESULT, stdin=json.dumps(AGREED))
        self.assertEqual(code, 1)
        self.assertIn("no run is going", out)
        self.assertIn("turn.py start", out)

    def test_going_on_for_a_result_never_started_stops(self):
        # Given: a result path no run was started for
        # When: the orchestrator goes on there
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


class TestReaders(ReadTest):
    def test_the_evaluator_is_started_with_the_first_users_reading(self):
        # Given: a run whose first user has replied with the Good it found for one item
        # When: the orchestrator goes on
        # Then: the evaluator is to be started with what the first user was, and its reading
        out = self.made(GOOD, WAITS)
        first = self.given()
        self.replied("turn:first-user", out["prompt"], {"items": self.reading(FOUND)})
        out = self.next()
        self.assertEqual(out["agent"], "turn:evaluator")
        self.assertEqual(self.given(), dict(first, reading=[FOUND]))

    def test_going_on_before_the_first_user_replies_stops(self):
        # Given: a run whose first user is to be started
        # When: the orchestrator goes on before it has replied
        # Then: it stops, saying to start the first user with the prompt printed and wait
        self.made(GOOD, WAITS)
        self.assertIn("start turn:first-user", self.refused())

    def test_an_evaluator_agreeing_with_the_first_user_still_has_every_item_decided(self):
        # Given: a claim with one item's Good and the other waiting, and an evaluator giving a
        # Good to the first item alone
        # When: the orchestrator goes on, and then decides as claimed
        # Then: both items come to decide, as readers that agree may still carry a doubt inside a
        # Good; after the learner, the result holds where the work is, the Good with its lines,
        # and the question with its recommended answer and the item it settles, and the run has
        # returned
        decide = self.through(EVALUATED)["decide"]["items"]
        self.assertEqual([i["item"] for i in decide], ["F-1", "B-1"])
        self.assertEqual(self.learnt(self.next(AGREED)), {"returned": RESULT})
        self.assertEqual(
            self.read_json(RESULT),
            {
                "work": ["README.md"],
                "items": [GOOD],
                "questions": [dict(QUESTION, items=[ITEM_B1])],
                "not_good": [],
                "lessons": [],
            },
        )

    def test_the_result_is_written_one_key_or_value_to_a_line(self):
        # Given: a run that returns
        # When: its result is written
        # Then: each key and each value of a list stands on a line of its own, indented one space
        # a level, so the calling AI and the user can read it
        self.through(EVALUATED)
        self.learnt(self.next(AGREED))
        with open(RESULT, encoding="utf-8") as f:
            lines = f.read().splitlines()
        self.assertEqual(lines[:4], ["{", ' "work": [', '  "README.md"', " ],"])

    def test_a_result_at_the_top_of_the_repository_is_written(self):
        # Given: a run whose result goes at the top of the repository, in no folder
        # When: it returns
        # Then: the result is written there
        prompt = self.started(dict(CALL, result="result.json"))
        claim = {"items": [GOOD, WAITS], "questions": [QUESTION]}
        self.replied("turn:generator", prompt, claim)
        _, out = self.turn("next", "result.json")
        self.replied("turn:first-user", json.loads(out)["prompt"], {"items": [FOUND, WAITS_READ]})
        _, out = self.turn("next", "result.json")
        self.replied("turn:evaluator", json.loads(out)["prompt"], {"items": [EVALUATED]})
        self.turn("next", "result.json")
        _, out = self.turn("next", "result.json", stdin=json.dumps(AGREED))
        learnt = {"process": [], "checked": CHECKED}
        self.replied("turn:learner", json.loads(out)["prompt"], learnt)
        code, out = self.turn("next", "result.json")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.read_json("result.json")["items"], [GOOD])

    def test_every_item_goes_to_the_orchestrator_to_decide(self):
        # Given: a claim with one item's Good and the other waiting on a question, an evaluator
        # giving no Good to the first and a Good to the second, and a first user that read the
        # work
        # When: the orchestrator goes on
        # Then: both items come back to decide, each with the evaluator's Good and the first
        # user's, the second with the question the generator found it waits on, with the
        # questions, and the run goes on
        good_b1 = dict(EVALUATED, item="B-1")
        out = self.through(good_b1, opened=READ_SHOWN)
        self.assertEqual(
            out,
            {
                "decide": {
                    "items": [
                        dict(ITEM_F1, evaluator=None, first_user=judged(FOUND)),
                        dict(ITEM_B1, evaluator=judged(good_b1), first_user=None, question=1),
                    ],
                    "questions": [QUESTION],
                }
            },
        )
        self.assertIn("running", self.read_json(RESULT))


class TestEachPart(RepoTest):
    """An item asked of each part is given a Good for every part, and has its Good only then."""

    def setUp(self):
        super().setUp()
        self.write("checklists/readme.md", CHECKLIST + EACH)
        self.write("README.md", SECTIONED)
        code, out = self.turn("start", json.dumps(CALL))
        self.assertEqual(code, 0, out)
        can = CAN + [dict(CAN[0], item="B-2")]
        self.next({"items": can, "questions": []})

    def test_an_item_asked_of_each_part_is_sent_back_with_the_parts_without_good(self):
        # Given: a first user giving an item asked of each part no Good where one part does not
        # give it
        # When: the orchestrator goes on
        # Then: the generator is sent the item again, with the part where it stopped, what it did
        # there and what it did not get
        out = self.made(GOOD, WAITS, EACH_GOOD)
        back = dict(STOPPED, item="B-2", places=["README.md:5-7"])
        reply = {"items": [FOUND, WAITS_READ, back]}
        self.assertEqual(self.replied("turn:first-user", out["prompt"], reply), (0, ""))
        self.assertEqual(self.next()["agent"], "turn:generator")
        self.assertEqual(self.given()["sent_back"], [back])

    def test_an_item_given_a_good_for_every_part_is_good_in_the_result(self):
        # Given: findings, a first user and an evaluator each giving an item asked of each part a
        # Good for every part
        # When: the run returns
        # Then: the result holds the item with its Good for every part
        claim = (GOOD, WAITS, EACH_GOOD)
        self.through(EVALUATED, EACH_GOOD, claim=claim, found=(FOUND, EACH_GOOD))
        decision = {"items": list(claim), "questions": []}
        self.assertEqual(self.learnt(self.next(decision)), {"returned": RESULT})
        self.assertEqual(self.read_json(RESULT)["items"], [GOOD, EACH_GOOD])

    def test_an_item_a_reader_gave_no_good_for_every_part_goes_to_decide(self):
        # Given: a first user giving an item asked of each part a Good for every part, and an
        # evaluator that leaves it out
        # When: the orchestrator goes on
        # Then: the item comes back to decide with the first user's Good for every part
        claim = (GOOD, WAITS, EACH_GOOD)
        out = self.through(EVALUATED, claim=claim, found=(FOUND, EACH_GOOD))
        decided = [i for i in out["decide"]["items"] if i["item"] == "B-2"]
        self.assertEqual(decided[0]["first_user"], judged(EACH_GOOD))
        self.assertIsNone(decided[0]["evaluator"])
        decision = {"items": list(claim), "questions": []}
        self.assertEqual(self.learnt(self.next(decision)), {"returned": RESULT})
        self.assertEqual(self.read_json(RESULT)["items"], [GOOD, EACH_GOOD])

    def test_a_good_for_every_part_no_reader_found_stops(self):
        # Given: an item asked of each part the generator claimed Good while neither reader gave it
        # When: the decision gives it a Good for every part
        # Then: it stops, asking for what the receiver gets and where it is not found
        claim = (GOOD, WAITS, EACH_GOOD)
        self.through(EVALUATED, claim=claim, found=(FOUND,))
        out = self.refused({"items": list(claim), "questions": []})
        self.assertIn("checklists/readme.md B-2 has no Good a reader found", out)
        self.assertIn("and where it is not found", out)


class TestDecision(ReadTest):
    def setUp(self):
        super().setUp()
        self.through(dict(EVALUATED, item="B-1"))

    def test_a_decision_with_every_item_good_or_waiting_writes_the_result(self):
        # Given: both items to decide
        # When: the orchestrator gives the first Good and has the second wait on a new question
        # Then: the result holds the Good and the new question alone, as no item waits on the
        # claim's question any more
        new = {"question": "Which name?", "recommended": "csvtidy"}
        out = self.next({"items": [GOOD, dict(WAITS, question=2)], "questions": [new]})
        self.assertEqual(self.learnt(out), {"returned": RESULT})
        self.assertEqual(
            self.read_json(RESULT),
            {
                "work": ["README.md"],
                "items": [GOOD],
                "questions": [dict(new, items=[ITEM_B1])],
                "not_good": [],
                "lessons": [],
            },
        )

    def test_a_decision_may_ask_a_new_question_or_keep_one(self):
        # Given: both items to decide, with one question asked in the claim
        # When: the orchestrator has the first wait on a new question, numbered after the claim's,
        # and the second still wait on the claim's question
        # Then: the result holds both questions, numbered from 1, each with the item it settles
        new = {"question": "Which name?", "recommended": "csvtidy"}
        decision = {"items": [dict(WAITS, item="F-1", question=2), WAITS], "questions": [new]}
        self.assertEqual(self.learnt(self.next(decision)), {"returned": RESULT})
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

    def test_a_good_no_reader_found_stops(self):
        # Given: an item the generator claimed Good while neither the first user nor the evaluator
        # found its Good
        # When: the decision gives it its Good
        # Then: it stops, asking for what the receiver gets once it has it, and the run goes on
        super().setUp()
        self.through(dict(EVALUATED, item="B-1"), found=())
        decision = {"items": [GOOD, WAITS], "questions": []}
        self.assertIn("checklists/readme.md F-1 has no Good", self.refused(decision))
        self.assertIn("running", self.read_json(RESULT))
        unmet = dict(SENT_BACK, item="F-1")
        self.assertIn("learner", self.next({"items": [unmet, WAITS], "questions": []})["agent"])

    def test_a_good_a_reader_found_passes_beside_an_item_none_found(self):
        # Given: two items to decide, one whose Good the evaluator found and one no reader found,
        # either way round
        # When: the decision gives the first its Good and has the other wait on the question
        # Then: the run returns, as the Good given is one a reader found
        for claim, evaluated in (
            ((GOOD, WAITS), dict(EVALUATED, item="B-1")),
            ((dict(WAITS, item="F-1"), dict(GOOD, item="B-1")), EVALUATED),
        ):
            with self.subTest(evaluated=evaluated["item"]):
                super().setUp()
                self.through(evaluated, claim=claim, found=())
                good = dict(GOOD, item=evaluated["item"])
                other = "F-1" if evaluated["item"] == "B-1" else "B-1"
                decision = {"items": [good, dict(WAITS, item=other)], "questions": []}
                self.assertEqual(self.learnt(self.next(decision)), {"returned": RESULT})

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

    def offered(self, *lessons):
        """The learner replied with the lessons, and what is offered to take."""
        reply = {"process": list(lessons), "checked": CHECKED}
        self.assertEqual(self.replied("turn:learner", self.learner["prompt"], reply), (0, ""))
        return self.next()

    def test_a_round_leaving_an_item_without_good_starts_the_learner(self):
        # Given: a first round whose decision leaves an item without Good
        # When: the decision is recorded
        # Then: the learner is to be started with every item's finding, the record of every
        # role that replied in the run, and no lesson yet
        self.assertEqual(self.learner["agent"], "turn:learner")
        records = [
            f"{self.repo}/session/subagents/agent-{a}.jsonl"
            for a in ("generator", "first-user", "evaluator")
        ]
        self.assertEqual(
            self.given(),
            {"findings": [GOOD, SENT_BACK], "records": records, "lessons": []},
        )

    def test_a_round_with_every_item_good_starts_the_learner_too(self):
        # Given: a first round whose evaluator agrees with the first user
        # When: the orchestrator goes on
        # Then: the learner is to be started, as a run may get its Goods by chance or with waste
        super().setUp()
        self.started()
        self.through(EVALUATED)
        self.assertEqual(self.next(AGREED)["agent"], "turn:learner")

    def test_the_orchestrators_own_record_is_shown_to_the_learner(self):
        # Given: a run whose orchestrator's record is kept
        # When: the learner is started after a round
        # Then: it is given the orchestrator's record after every role's
        super().setUp()
        self.started()
        kept = self.read_json(RESULT)
        kept["running"]["orchestrator"] = "orchestrator.jsonl"
        self.write_json(RESULT, kept)
        self.through(EVALUATED)
        self.next(AGREED)
        self.assertEqual(self.given()["records"][-1], "orchestrator.jsonl")

    def test_what_the_learner_found_is_offered_to_the_orchestrator_to_take(self):
        # Given: a learner that replied with a lesson on the run
        # When: the orchestrator goes on, and again with nothing given
        # Then: the lesson is offered to take, with what the learner checked, each time
        offer = {"take": {"process": [LESSON], "checked": CHECKED}}
        self.assertEqual(self.offered(LESSON), offer)
        self.assertEqual(self.next(), offer)

    def test_what_is_taken_goes_to_the_generator_and_to_each_role_of_the_second_round(self):
        # Given: an offer of a lesson for the generator and one for the first user
        # When: the orchestrator takes both lessons
        # Then: the generator makes the work again with the item without Good and its lesson, and
        # the first user of the second round is given its own
        self.offered(LESSON, dict(LESSON, role="first-user", lesson="read the opening first"))
        out = self.next({"process": [1, 2]})
        self.assertEqual(out["agent"], "turn:generator")
        given = self.given()
        self.assertEqual((given["sent_back"], given["lessons"]), ([SENT_BACK], [LESSON["lesson"]]))
        self.assertNotIn("learnt", given)
        out = self.made(GOOD, WAITS)
        self.assertEqual(out["agent"], "turn:first-user")
        self.assertIn("prompt", out)
        self.assertEqual(self.given()["lessons"], ["read the opening first"])

    def test_each_lesson_taken_is_the_one_its_number_names(self):
        # Given: an offer of three lessons, each for another role
        # When: the orchestrator takes the third alone
        # Then: only the third goes on, to its role
        roles = ("first-user", "evaluator", "generator")
        self.offered(*(dict(LESSON, role=r, lesson=f"lesson for {r}") for r in roles))
        self.next({"process": [3]})
        self.assertEqual(self.given()["lessons"], ["lesson for generator"])

    def test_what_is_taken_out_of_its_form_stops(self):
        # Given: an offer of what the learner found
        # When: the orchestrator takes a lesson not offered
        # Then: it stops, naming it, and the offer still waits
        self.offered(LESSON)
        out = self.refused({"process": [2]})
        self.assertIn("what you take is not filled", out)
        self.assertIn("lesson 2 is not one of 1 to 1", out)
        self.assertIn("take", self.read_json(RESULT)["running"])

    def test_with_nothing_to_take_the_run_goes_on_without_asking(self):
        # Given: a round with every item Good, and a learner that found no lesson on the run
        # When: the orchestrator goes on
        # Then: the run returns, as nothing is offered
        super().setUp()
        self.started()
        self.through(EVALUATED)
        out = self.next(AGREED)
        reply = {"process": [], "checked": CHECKED}
        self.replied("turn:learner", out["prompt"], reply)
        self.assertEqual(self.next(), {"returned": RESULT})

    def test_with_no_lesson_after_a_round_leaving_an_item_without_good_the_work_is_made_again(
        self,
    ):
        # Given: a first round leaving an item without Good, and a learner that found no lesson
        # When: the orchestrator goes on
        # Then: the generator makes the work again with the item, as nothing is offered to take
        reply = {"process": [], "checked": CHECKED}
        self.replied("turn:learner", self.learner["prompt"], reply)
        self.assertEqual(self.next()["agent"], "turn:generator")
        self.assertEqual(self.given()["sent_back"], [SENT_BACK])

    def test_an_item_still_without_good_after_the_second_round_is_returned(self):
        # Given: a work made again with what the learner found, and a lesson taken
        # When: its second round leaves an item without Good, and the learner after it gives
        # another lesson, which is taken
        # Then: the run returns with that item, what the receiver gets once it has its Good and
        # where it is not found, and both lessons
        self.offered(LESSON)
        self.next({"process": [1]})
        self.through(dict(EVALUATED, item="B-1"))
        self.learner = self.next({"items": [GOOD, SENT_BACK], "questions": []})
        self.assertEqual(self.given()["lessons"], [])
        second = dict(LESSON, role="learner", lesson="it read each record once")
        self.offered(second)
        self.assertEqual(self.next({"process": [1]}), {"returned": RESULT})
        self.assertEqual(
            self.read_json(RESULT),
            {
                "work": ["README.md"],
                "items": [GOOD],
                "questions": [],
                "not_good": [SENT_BACK],
                "lessons": [LESSON, second],
            },
        )


class TestRecord(ReadTest):
    def setUp(self):
        super().setUp()
        self.through(dict(EVALUATED, item="B-1"))
        self.next({"items": [GOOD, SENT_BACK], "questions": []})

    def test_a_record_is_shown_with_what_the_role_was_given_did_and_replied(self):
        # Given: a learner's run, whose generator's record holds its prompt and a Read
        # When: the learner asks for the first record's first page
        # Then: it is shown with its number and page among all, the prompt and the tool used
        code, out = self.turn("record", RESULT, "1", "1")
        self.assertEqual(code, 0, out)
        first = out.splitlines()[0]
        self.assertEqual(first, f"record 1 of 3, page 1 of 1: {self.given()['records'][0]}")
        self.assertIn('[user] {"run": ".tasks/readme-result.json"}', out)
        self.assertIn('[tool_use Read] {"file_path": "README.md"}', out)

    def test_a_record_too_long_for_one_read_is_shown_page_by_page(self):
        # Given: a record holding a tool result longer than two pages, a text and a file Claude
        # Code showed whole
        # When: the learner asks for each page
        # Then: the pages together show the whole record, each of 20000 characters but the last
        path = self.given()["records"][0]
        parts = [
            {"type": "text", "text": "I read it."},
            {"type": "tool_result", "content": [{"type": "text", "text": "x" * 45000}]},
            {"type": "tool_result", "content": "done"},
        ]
        shown = {"type": "edited_text_file", "filename": "README.md", "snippet": "1\t# csvtidy"}
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"type": "user", "message": {"content": parts}}) + "\n")
            f.write(json.dumps({"type": "attachment", "attachment": shown}) + "\n")
        pages = []
        for page in (1, 2, 3):
            code, out = self.turn("record", RESULT, "1", str(page))
            self.assertEqual(code, 0, out)
            self.assertIn(f"page {page} of 3", out.splitlines()[0])
            # The page, without its head and the line end print adds.
            pages.append(out.split("\n", 1)[1][:-1])
        self.assertEqual([len(p) for p in pages[:2]], [20000, 20000])
        whole = "".join(pages)
        for words in ("I read it.", "x" * 45000, "[tool_result] done", "[shown README.md]"):
            self.assertIn(words, whole)

    def test_a_record_shows_the_role_alone_not_the_requests_claude_code_copies(self):
        # Given: a record holding, among the role's own entries, the copy of a request Claude
        # Code keeps beside them
        # When: the learner asks for its page
        # Then: the copy is not shown, and the entries after it are
        path = self.given()["records"][0]
        copy = {"role": "user", "content": [{"type": "text", "text": "copied request"}]}
        after = {"content": [{"type": "text", "text": "read after the copy"}]}
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"type": "api-request-blob", "message": copy}) + "\n")
            f.write(json.dumps({"type": "assistant", "message": after}) + "\n")
        code, out = self.turn("record", RESULT, "1", "1")
        self.assertEqual(code, 0, out)
        self.assertNotIn("copied request", out)
        self.assertIn("read after the copy", out)

    def test_a_record_shows_each_part_by_its_type_and_no_other_attachment(self):
        # Given: a record holding a part of a type of its own, a tool used with words beyond
        # ASCII, and attachments that are not a file shown whole
        # When: the learner asks for its page
        # Then: the part is shown by its type, the words as they are, and the attachments not
        path = self.given()["records"][0]
        parts = [
            {"type": "web_search_tool_result", "text": "found"},
            {"type": "tool_use", "name": "Read", "input": {"file_path": "読む.md"}},
        ]
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"type": "assistant", "message": {"content": parts}}) + "\n")
            for kind in ("date", "queued_command"):
                attachment = {"type": kind, "filename": kind, "snippet": "x"}
                f.write(json.dumps({"type": "attachment", "attachment": attachment}) + "\n")
        code, out = self.turn("record", RESULT, "1", "1")
        self.assertEqual(code, 0, out)
        self.assertIn("[web_search_tool_result] found", out)
        self.assertIn('[tool_use Read] {"file_path": "読む.md"}', out)
        self.assertNotIn("[shown", out)

    def test_each_record_is_shown_by_its_number(self):
        # Given: a learner's run of four records
        # When: each is asked for
        # Then: each is shown, headed by its number and path
        kept = self.read_json(RESULT)
        records = kept["running"]["next"]["given"]["records"]
        records.append(self.given_record("third", "{}"))
        self.write_json(RESULT, kept)
        for n, path in enumerate(records, 1):
            with self.subTest(n=n):
                code, out = self.turn("record", RESULT, str(n), "1")
                self.assertEqual(code, 0, out)
                self.assertEqual(out.splitlines()[0], f"record {n} of 4, page 1 of 1: {path}")

    def test_a_record_or_page_out_of_range_stops(self):
        # Given: a learner's run of three records, each of one page
        # When: a record or page outside them, or one not a number, is asked for
        # Then: it is stopped, naming what there is
        for number, page, said in (
            ("4", "1", "record 4 is not one of 1 to 3"),
            ("0", "1", "record 0 is not one of 1 to 3"),
            ("1", "0", "page 0 is not one of 1 to 1"),
            ("1", "2", "page 2 is not one of 1 to 1"),
            ("a", "1", "record a is not one of 1 to 3"),
        ):
            with self.subTest(number=number, page=page):
                code, out = self.turn("record", RESULT, number, page)
                self.assertEqual(code, 1)
                self.assertIn(said, out)

    def test_a_record_before_the_learner_is_started_stops(self):
        # Given: a run waiting on the orchestrator's check, where no learner is started
        # When: a record is asked for
        # Then: it is stopped, as there is none to show
        self.started(dict(CALL, result="other.json"))
        code, out = self.turn("record", "other.json", "1", "1")
        self.assertEqual(code, 1)
        self.assertIn("record 1 is not one of 1 to 0", out)
        self.turn("start", json.dumps(dict(CALL, result="checking.json")))
        code, out = self.turn("record", "checking.json", "1", "1")
        self.assertIn("record 1 is not one of 1 to 0", out)

    def test_a_record_of_no_run_going_stops(self):
        # Given: no run going at the path
        # When: a record is asked for
        # Then: it is stopped
        code, out = self.turn("record", "none.json", "1", "1")
        self.assertEqual(code, 1)
        self.assertIn("no run is going", out)


class TestDecisionForm(ReadTest):
    def setUp(self):
        super().setUp()
        self.through(dict(EVALUATED, item="B-1"))

    def stops(self, decision, *said):
        code, out = self.turn(
            "next", RESULT, stdin=decision if isinstance(decision, str) else json.dumps(decision)
        )
        self.assertEqual(code, 1, out)
        for words in said:
            self.assertIn(words, out)
        self.assertIn("decide", self.read_json(RESULT)["running"])

    def test_a_decision_that_is_not_json_stops(self):
        # Given: a decision that is not a JSON object of items and questions
        # When: it is recorded
        # Then: it stops, saying the shape to give
        self.stops("good", '{"items": [...], "questions": [...]}')
        self.stops("[]", '{"items": [...], "questions": [...]}')
        self.stops('{"items": []}', '{"items": [...], "questions": [...]}')

    def test_a_decision_in_a_json_fence_is_recorded(self):
        # Given: a decision given as JSON inside a ```json fence
        # When: it is recorded
        # Then: it is taken as the decision itself, and the learner is to be started
        code, out = self.turn("next", RESULT, stdin=f"```json\n{json.dumps(AGREED)}\n```\n")
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(out)["agent"], "turn:learner")

    def test_an_item_left_out_or_given_twice_stops(self):
        # Given: a decision missing an item, or giving one twice, or naming one no checklist holds
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
                    {"items": [GOOD, item], "questions": []},
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
        self.write("CHANGELOG.md", "# Changelog\n")
        for lines in (
            ["docs/start.md:1"],
            ["CHANGELOG.md:1"],
            ["README.md:2-9"],
            ["README.md:3-1"],
            ["README.md"],
        ):
            with self.subTest(lines=lines):
                self.stops(
                    {"items": [dict(GOOD, lines=lines), SENT_BACK], "questions": []},
                    lines[0],
                    "<path>:<from>-<to>",
                )

    def test_a_question_number_with_no_question_stops(self):
        # Given: an item waiting on question 3 where the claim asked one and the decision one more
        # When: it is recorded
        # Then: it stops, naming the number
        self.stops({"items": [GOOD, dict(WAITS, question=3)], "questions": [QUESTION]}, "3")

    def test_a_question_that_is_not_a_number_stops(self):
        # Given: an item waiting on a question named by its words, not its number
        # When: it is recorded
        # Then: it stops, saying to give the question's number
        waits = dict(WAITS, question="Which license?")
        self.stops({"items": [GOOD, waits], "questions": []}, "not a number")

    def test_a_question_without_a_recommended_answer_stops(self):
        # Given: a new question with no recommended answer
        # When: it is recorded
        # Then: it stops, saying each question has one
        self.stops(
            {"items": [GOOD, dict(WAITS, question=2)], "questions": [{"question": "Which?"}]},
            '"recommended"',
        )

    def test_a_question_no_item_waits_on_stops(self):
        # Given: a new question no item waits on
        # When: it is recorded
        # Then: it stops, naming the question
        self.stops({"items": [GOOD, SENT_BACK], "questions": [QUESTION]}, "question 2")
