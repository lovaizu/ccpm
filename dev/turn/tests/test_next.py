import json
import os

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
    IDS,
    LESSON,
    QUESTION,
    RESULT,
    SECTIONED,
    SENT_BACK,
    STOPPED,
    WAITS,
    RepoTest,
    run,
)


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
        self.heard(self.next())

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
        self.assertEqual(self.next(), {"check": [ITEM_F1, ITEM_B1]})

    def test_a_check_with_an_item_waiting_on_a_question_asks_it_before_any_work(self):
        # Given: a check finding what gives one item its Good and nothing in the CCS for the other
        # When: the check is recorded, and the questions are asked for
        # Then: the run asks, with no work made, the result holding the question alone with the
        # item it settles, printed as it holds it
        out = self.heard(self.next({"items": [CAN[0], WAITS], "questions": [QUESTION]}))
        self.assertEqual(out, {"asked": RESULT})
        asked = {"questions": [dict(QUESTION, items=[ITEM_B1])]}
        self.assertEqual(self.read_json(RESULT), asked)
        code, out = self.turn("questions", RESULT)
        self.assertEqual((code, json.loads(out)), (0, asked))

    def test_questions_are_printed_with_letters_beyond_ascii_as_they_are(self):
        # Given: a question asked in Japanese
        # When: the questions are asked for
        # Then: its words are printed as they are
        asked = dict(QUESTION, question="どのライセンスで公開しますか")
        self.next({"items": [CAN[0], WAITS], "questions": [asked]})
        self.assertIn("どのライセンスで公開しますか", self.turn("questions", RESULT)[1])

    def test_once_answered_the_check_is_made_again_on_the_ccs(self):
        # Given: a run that asked a question, and a CCS the calling AI added the answer to
        # When: the orchestrator goes on
        # Then: the items are checked again, on the CCS as it is now
        self.heard(self.next({"items": [CAN[0], WAITS], "questions": [QUESTION]}))
        ccs = self.read_json(CALL["ccs"])
        ccs["retrieved_artifacts"].append({"license": "MIT"})
        self.write_json(CALL["ccs"], ccs)
        self.assertEqual(self.heard(self.next()), {"check": [ITEM_F1, ITEM_B1]})
        self.assertNotIn("asked", self.state())
        self.assertEqual(self.due(self.next({"items": CAN, "questions": []}))["tool"], "Agent")

    def test_the_questions_of_a_result_holding_none_stop(self):
        # Given: no result, and a result that holds no questions
        # When: the questions are asked for
        # Then: it stops, saying to go on with the run
        for text in (None, "{}", "[]", "x"):
            with self.subTest(text=text):
                if text is not None:
                    self.write(RESULT, text)
                code, out = self.turn("questions", RESULT)
                self.assertEqual(code, 1)
                self.assertIn("holds no questions", out)

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
                out = self.refused({"items": items, "questions": []})
                self.assertIn("the check is not filled", out)
                self.assertIn(said, out)
        self.assertEqual(self.next(), {"check": [ITEM_F1, ITEM_B1]})


class TestMade(ReadTest):
    def test_the_generator_is_given_what_it_makes_the_work_from_and_where_it_replies(self):
        # Given: a run checked to give every item its Good
        # When: the generator is to be started
        # Then: its prompt names the work, the checklists, nothing sent back yet, no lessons, and
        # its reply file beside the result, beside the files it makes the work from, which the
        # start's tests hold
        prompt = self.prompt()
        del prompt["given"]
        self.assertEqual(
            prompt,
            {
                "work": [self.here("README.md")],
                "checklists": [self.here("checklists/readme.md")],
                "sent_back": [],
                "lessons": [],
                "reply": self.here(RESULT + ".generator.json"),
            },
        )

    def test_the_generators_claim_starts_the_first_user_with_what_the_receiver_has(self):
        # Given: a call naming what the receiver reads the work for and what they have with it,
        # and a generator that replied with one item's Good and the other waiting on a question
        # When: the orchestrator goes on
        # Then: the first user is to be started with the work, what the receiver has, who the
        # receiver is and what for, and the checklists, and not the CCS or the claim
        move = self.due(self.made(GOOD, WAITS))
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
                "parts": ["README.md:1-3"],
                "lessons": [],
                "reply": self.here(RESULT + ".first-user.json"),
            },
        )

    def test_a_reading_of_the_orchestrator_between_the_roles_stops(self):
        # Given: a run waiting on the generator's reply, kept started
        # When: the orchestrator gives a reading of its own once the agent ID is given
        # Then: it stops, saying the run waits on the role's reply, and the run goes on
        reading = json.dumps({"items": [GOOD, WAITS], "questions": [QUESTION]})
        self.next({"agent_id": IDS["turn:generator"]})
        self.assertIn("waits on turn:generator's reply, not on yours", self.refused(reading))
        self.assertTrue(os.path.exists(run.state_path(RESULT)))

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
            ({"items": [GOOD], "questions": []}, "B-1 is left out"),
            ({"items": [GOOD, dict(GOOD, item="B-1")]}, '"questions": [...]'),
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
        self.assertEqual((code, json.loads(out)), (0, {"parts": ["README.md:1-3"]}))

    def test_going_on_for_a_result_never_started_stops(self):
        # Given: no run going at a path
        # When: the orchestrator goes on, asks for the parts or a page there
        # Then: it is stopped, saying how to start one
        for argv in (("next", "none.json"), ("parts", "none.json"), ("next", "none.json", "1")):
            with self.subTest(argv=argv):
                code, out = self.turn(*argv)
                self.assertEqual(code, 1)
                self.assertIn("no run is going with its result at none.json", out)


class TestReaders(ReadTest):
    def test_the_evaluator_is_started_with_the_first_users_reading(self):
        # Given: a run whose first user has replied with the Good it found for one item
        # When: the orchestrator goes on
        # Then: the evaluator is to be started with what the first user was, its own reply file,
        # and the reading
        self.due(self.made(GOOD, WAITS))
        first = self.prompt()
        move = self.due(self.replied({"items": self.reading(FOUND)}))
        self.assertEqual(move["input"]["subagent_type"], "turn:evaluator")
        expected = dict(first, reading=[FOUND], reply=self.here(RESULT + ".evaluator.json"))
        self.assertEqual(json.loads(move["input"]["prompt"]), expected)

    def test_an_evaluator_agreeing_with_the_first_user_still_has_every_item_decided(self):
        # Given: a claim with one item's Good and the other waiting, and an evaluator giving a
        # Good to the first item alone
        # When: the orchestrator goes on, and then decides as claimed
        # Then: both items come to decide; after the learner, the result holds where the work is,
        # the Good with its lines, and the question with the item it settles; the run has
        # returned, and what it kept beside the result is removed
        decide = self.heard(self.through(EVALUATED))["decide"]["items"]
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
        self.assertEqual(sorted(os.listdir(".tasks")), ["readme-result.json", "readme.json"])

    def test_the_result_is_written_one_key_or_value_to_a_line(self):
        # Given: a run that returns
        # When: its result is written
        # Then: each key and each value of a list stands on a line of its own
        self.through(EVALUATED)
        self.learnt(self.next(AGREED))
        with open(RESULT, encoding="utf-8") as f:
            lines = f.read().splitlines()
        self.assertEqual(lines[:4], ["{", ' "work": [', '  "README.md"', " ],"])

    def test_every_item_goes_to_the_orchestrator_to_decide(self):
        # Given: a claim with one item's Good and the other waiting on a question, an evaluator
        # giving no Good to the first and a Good to the second
        # When: the orchestrator goes on
        # Then: both items come back to decide, each with the evaluator's Good and the first
        # user's, the second with the question the generator found it waits on
        good_b1 = dict(EVALUATED, item="B-1")
        self.assertEqual(
            self.heard(self.through(good_b1)),
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


class TestEachPart(RepoTest):
    """An item asked of each part is given a Good for every part, and has its Good only then."""

    def setUp(self):
        super().setUp()
        self.write("checklists/readme.md", CHECKLIST + EACH)
        self.write("README.md", SECTIONED)
        code, out = self.turn("start", json.dumps(CALL))
        self.assertEqual(code, 0, out)
        can = CAN + [dict(CAN[0], item="B-2")]
        self.due(self.next({"items": can, "questions": []}))

    def test_an_item_asked_of_each_part_is_sent_back_with_the_parts_without_good(self):
        # Given: a first user giving an item asked of each part no Good where one part does not
        # give it
        # When: the orchestrator goes on
        # Then: the generator is sent the item again, with the part where it stopped
        self.due(self.made(GOOD, WAITS, EACH_GOOD))
        back = dict(STOPPED, item="B-2", places=["README.md:5-7"])
        move = self.due(self.replied({"items": [FOUND, WAITS_READ, back]}))
        self.assertEqual(move["input"]["to"], IDS["turn:generator"])
        self.assertEqual(json.loads(move["input"]["message"])["sent_back"], [back])

    def test_an_item_given_a_good_for_every_part_is_good_in_the_result(self):
        # Given: a first user and an evaluator each giving an item asked of each part a Good for
        # every part
        # When: the run returns
        # Then: the result holds the item with its Good for every part
        claim = (GOOD, WAITS, EACH_GOOD)
        self.through(EVALUATED, EACH_GOOD, claim=claim, found=(FOUND, EACH_GOOD))
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

    def test_a_reply_giving_an_each_part_item_without_every_part_is_sent_back_to_its_role(self):
        # Given: a generator replying with an item asked of each part given one part alone
        # When: the orchestrator goes on
        # Then: the generator is sent what is wrong, to write its reply again, and the reply file
        # is removed until it does
        one = dict(EACH_GOOD, parts=EACH_GOOD["parts"][:1])
        out = self.made(GOOD, WAITS, one)
        self.assertEqual(out["move"]["tool"], "SendMessage")
        self.assertEqual(out["move"]["input"]["to"], IDS["turn:generator"])
        self.assertIn("in your form, filled:", out["move"]["input"]["message"])
        self.assertFalse(os.path.exists(RESULT + ".generator.json"))
        self.assertEqual(self.due(self.made(GOOD, WAITS, EACH_GOOD))["tool"], "Agent")


class TestDecision(ReadTest):
    def setUp(self):
        super().setUp()
        self.through(dict(EVALUATED, item="B-1"))

    def test_a_decision_with_every_item_good_or_waiting_writes_the_result(self):
        # Given: both items to decide
        # When: the orchestrator gives the first Good and has the second wait on a new question
        # Then: the result holds the Good and the new question alone
        new = {"question": "Which name?", "recommended": "csvtidy"}
        out = self.next({"items": [GOOD, dict(WAITS, question=2)], "questions": [new]})
        self.assertEqual(self.learnt(out), {"returned": RESULT})
        self.assertEqual(self.read_json(RESULT)["questions"], [dict(new, items=[ITEM_B1])])

    def test_a_decision_may_ask_a_new_question_or_keep_one(self):
        # Given: both items to decide, with one question asked in the claim
        # When: the orchestrator has the first wait on a new question and the second on the
        # claim's
        # Then: the result holds both questions, numbered from 1, each with the item it settles
        new = {"question": "Which name?", "recommended": "csvtidy"}
        decision = {"items": [dict(WAITS, item="F-1", question=2), WAITS], "questions": [new]}
        self.assertEqual(self.learnt(self.next(decision)), {"returned": RESULT})
        self.assertEqual(
            self.read_json(RESULT)["questions"],
            [dict(QUESTION, items=[ITEM_B1]), dict(new, items=[ITEM_F1])],
        )

    def test_the_items_to_decide_are_printed_again_when_asked_with_no_decision(self):
        # Given: a run waiting on the orchestrator's decision
        # When: the orchestrator runs the script with no input
        # Then: it is shown the items to decide again, and the run still waits on its decision
        first = self.state()["decide"]
        self.assertEqual(self.next(), {"decide": first})
        self.assertIn("decide", self.state())

    def test_items_to_decide_too_long_for_one_read_are_shown_page_by_page(self):
        # Given: a run waiting on a decision whose items run past two pages
        # When: the orchestrator runs the script with no input, then asks for each page after
        # Then: each page is headed by its number among all and how to see the others, the pages
        # together are the items to decide, and a page past the last stops
        super().setUp()
        self.through(dict(EVALUATED, item="B-1", good="x" * 45000))
        decide = self.state()["decide"]
        pages = []
        for asked in ((), ("2",), ("3",)):
            code, out = self.turn("next", RESULT, *asked)
            self.assertEqual(code, 0, out)
            head, page = out.split("\n", 1)
            self.assertTrue(head.startswith(f"decide, page {len(pages) + 1} of 3: "), head)
            self.assertIn(f"turn.py next {RESULT} <page>", head)
            pages.append(page[:-1])
        self.assertEqual(json.loads("".join(pages)), {"decide": decide})
        self.assertEqual([len(p) for p in pages[:2]], [20000, 20000])
        for page in ("0", "4", "a"):
            self.assertIn(f"page {page} is not one of 1 to 3", self.turn("next", RESULT, page)[1])

    def test_items_to_decide_of_two_pages_are_shown_page_by_page(self):
        # Given: a run waiting on a decision whose items run to two pages
        # When: the orchestrator runs the script with no input
        # Then: the first page is headed by its number of two
        super().setUp()
        self.through(dict(EVALUATED, item="B-1", good="x" * 25000))
        out = self.turn("next", RESULT)[1]
        self.assertTrue(out.startswith("decide, page 1 of 2: "), out[:80])

    def test_items_to_decide_short_enough_for_one_read_are_printed_as_they_are(self):
        # Given: a run waiting on a decision whose items fit in one page
        # When: the orchestrator asks for the first page
        # Then: the items to decide are printed with no head, as with no page asked
        code, out = self.turn("next", RESULT, "1")
        self.assertEqual((code, json.loads(out)), (0, self.next()))

    def test_a_page_asked_while_the_run_waits_on_a_role_stops(self):
        # Given: a run waiting on the generator's reply
        # When: the orchestrator asks for a page
        # Then: it stops, saying to go on with no page
        super().setUp()
        code, out = self.turn("next", RESULT, "2")
        self.assertEqual(code, 1, out)
        self.assertIn(f"run `turn.py next {RESULT}`", out)

    def test_a_good_no_reader_found_stops(self):
        # Given: an item the generator claimed Good while neither reader found its Good
        # When: the decision gives it its Good
        # Then: it stops, asking for what the receiver gets once it has it, and the run goes on
        super().setUp()
        self.through(dict(EVALUATED, item="B-1"), found=())
        decision = {"items": [GOOD, WAITS], "questions": []}
        self.assertIn("checklists/readme.md F-1 has no Good", self.refused(decision))
        unmet = dict(SENT_BACK, item="F-1")
        self.next({"items": [unmet, WAITS], "questions": []})
        self.assertEqual(self.state()["next"]["agent"], "turn:learner")

    def test_a_good_a_reader_found_passes_beside_an_item_none_found(self):
        # Given: two items to decide, one whose Good the evaluator found and one no reader found,
        # either way round
        # When: the decision gives the first its Good and has the other wait on the question
        # Then: the run returns
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
                self.assertIn("decide", self.state())


class TestLearner(ReadTest):
    def setUp(self):
        super().setUp()
        for agent, agent_id in IDS.items():
            self.given_record(agent_id, "{}", agent)
        self.orchestrator = self.given_record("aup", json.dumps(CALL), "turn:up")
        self.through(dict(EVALUATED, item="B-1"))
        self.learner = self.next({"items": [GOOD, SENT_BACK], "questions": []})

    def offered(self, *lessons):
        """The learner replied with the lessons, and what is offered to take."""
        self.due(self.learner)
        return self.replied({"process": list(lessons), "checked": CHECKED})

    def test_a_round_starts_the_learner_on_every_record_of_the_run_shown_as_text(self):
        # Given: a first round whose decision leaves an item without Good
        # When: the decision is recorded
        # Then: the learner is to be started with every item's finding, the record of every role
        # that replied and the orchestrator's, each shown as text beside the result, and no lesson
        move = self.due(self.learner)
        self.assertEqual(move["input"]["subagent_type"], "turn:learner")
        texts = [self.here(f"{RESULT}.records/{n}.txt") for n in (1, 2, 3, 4)]
        self.assertEqual(
            json.loads(move["input"]["prompt"]),
            {
                "given": texts,
                "findings": [GOOD, SENT_BACK],
                "lessons": [],
                "reply": self.here(RESULT + ".learner.json"),
            },
        )
        self.assertIn("[user] {}", self.read(texts[0]))
        self.assertIn('"result": ".tasks/readme-result.json"', self.read(texts[3]))

    def test_a_record_not_kept_is_left_out(self):
        # Given: a run whose records are not where Claude Code keeps them
        # When: the learner is started
        # Then: it is given none
        super().setUp()
        self.through(EVALUATED)
        self.due(self.next(AGREED))
        self.assertEqual(self.prompt()["given"], [])

    def test_what_the_learner_found_is_offered_to_the_orchestrator_to_take(self):
        # Given: a learner that replied with a lesson resting on its record's words
        # When: the orchestrator goes on, and again with nothing given
        # Then: the lesson is offered to take, with what the learner checked, each time
        offer = {"take": {"process": [LESSON], "checked": CHECKED}}
        self.assertEqual(self.heard(self.offered(LESSON)), offer)
        self.assertEqual(self.next(), offer)

    def test_what_is_taken_goes_to_the_generator_and_to_each_role_of_the_second_round(self):
        # Given: an offer of a lesson for the generator and one for the first user
        # When: the orchestrator takes both lessons
        # Then: the generator is started anew with the item without Good and its lesson, and the
        # first user of the second round is started anew with its own
        self.offered(LESSON, dict(LESSON, role="first-user", lesson="read the opening first"))
        out = self.next({"process": [1, 2]})
        self.assertIn("round 2", out["line"])
        self.assertEqual(self.due(out)["tool"], "Agent")
        given = self.prompt()
        self.assertEqual((given["sent_back"], given["lessons"]), ([SENT_BACK], [LESSON["lesson"]]))
        self.assertEqual(self.due(self.made(GOOD, WAITS))["tool"], "Agent")
        self.assertEqual(self.prompt()["lessons"], ["read the opening first"])

    def test_the_lessons_found_and_those_taken_are_told(self):
        # Given: a learner that replied with two lessons
        # When: the orchestrator goes on, and takes one
        # Then: a line says how many lessons the learner gave before they are shown, and a line
        # says how many were taken before the next round
        out = self.offered(LESSON, dict(LESSON, lesson="it read the work once"))
        self.assertTrue(
            str(out["line"]).startswith(
                "turn: turn:learner gave 2 lessons on how the round went. Next, turn:up will take"
                " the learner's lessons that hold, of README.md, for 2 items, round 1."
            ),
            out,
        )
        out = self.next({"process": [2]})
        self.assertTrue(
            str(out["line"]).startswith("turn: turn:up took 1 of 2 lessons. Next, turn:generator"),
            out,
        )

    def test_each_lesson_taken_is_the_one_its_number_names(self):
        # Given: an offer of three lessons, each for another role
        # When: the orchestrator takes the third alone
        # Then: only the third goes on, to its role
        roles = ("first-user", "evaluator", "generator")
        self.offered(*(dict(LESSON, role=r, lesson=f"lesson for {r}") for r in roles))
        self.next({"process": [3]})
        self.assertEqual(self.prompt()["lessons"], ["lesson for generator"])

    def test_what_is_taken_out_of_its_form_stops(self):
        # Given: an offer of what the learner found
        # When: the orchestrator takes a lesson not offered
        # Then: it stops, naming it, and the offer still waits
        self.offered(LESSON)
        out = self.refused({"process": [2]})
        self.assertIn("lesson 2 is not one of 1 to 1", out)
        self.assertIn("take", self.state())

    def test_a_lesson_quoting_words_no_record_holds_is_sent_back_to_the_learner(self):
        # Given: a learner whose lesson quotes words its record does not hold
        # When: the orchestrator goes on
        # Then: the learner is sent what is wrong
        out = self.offered(dict(LESSON, grounds=[{"record": 1, "quote": "never said"}]))
        self.assertEqual(out["move"]["input"]["to"], IDS["turn:learner"])
        self.assertIn("is not in record 1 as written", out["move"]["input"]["message"])

    def test_with_nothing_to_take_after_a_round_with_every_item_good_the_run_returns(self):
        # Given: a round with every item Good, and a learner that found no lesson on the run
        # When: the orchestrator goes on
        # Then: the run returns, as nothing is offered
        super().setUp()
        self.through(EVALUATED)
        self.assertEqual(self.learnt(self.next(AGREED)), {"returned": RESULT})

    def test_with_no_lesson_after_a_round_leaving_an_item_without_good_the_work_is_made_again(
        self,
    ):
        # Given: a first round leaving an item without Good, and a learner that found no lesson
        # When: the orchestrator goes on
        # Then: the generator makes the work again with the item
        self.assertEqual(self.due(self.offered())["tool"], "Agent")
        self.assertEqual(self.prompt()["sent_back"], [SENT_BACK])

    def test_an_item_still_without_good_after_the_second_round_is_returned(self):
        # Given: a work made again with what the learner found, and a lesson taken
        # When: its second round leaves an item without Good, and the learner after it gives
        # another lesson, which is taken
        # Then: the run returns with that item and both lessons
        self.offered(LESSON)
        self.due(self.next({"process": [1]}))
        self.through(dict(EVALUATED, item="B-1"))
        self.learner = self.next({"items": [GOOD, SENT_BACK], "questions": []})
        self.assertEqual(self.prompt()["lessons"], [])
        second = dict(LESSON, role="learner", lesson="it read each record once")
        self.offered(second)
        self.assertEqual(self.heard(self.next({"process": [1]})), {"returned": RESULT})
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
        self.assertFalse(os.path.exists(RESULT + ".records"))


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
        self.assertIn("decide", self.state())

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
        self.assertEqual(self.state()["next"]["agent"], "turn:learner")

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


class TestRecordsShown(ReadTest):
    """Each record is shown to the learner as what the role was given, said, used and was shown."""

    def setUp(self):
        super().setUp()
        self.path = self.given_record(IDS["turn:generator"], '{"given": []}', "turn:generator")

    def shown(self):
        """The generator's record as the learner is shown it after the round."""
        self.through(EVALUATED)
        self.due(self.next(AGREED))
        return self.read(self.prompt()["given"][0])

    def test_a_record_shows_each_part_by_its_type_and_the_files_shown_whole(self):
        # Given: a record holding a tool used with words beyond ASCII, a tool result as a list
        # and as text, a part of a type of its own, a file Claude Code showed whole, an attachment
        # of another kind, and the copy of a request Claude Code keeps beside them
        # When: the learner is started
        # Then: each part is shown by its type, the file shown whole by its name, and neither the
        # other attachment nor the copy
        parts = [
            {"type": "tool_use", "name": "Read", "input": {"file_path": "読む.md"}},
            {"type": "tool_result", "content": [{"type": "text", "text": "x" * 2500}]},
            {"type": "tool_result", "content": "done"},
            {"type": "web_search_tool_result", "text": "found"},
        ]
        entries = [
            {"type": "assistant", "message": {"content": parts}},
            {
                "type": "attachment",
                "attachment": {
                    "type": "edited_text_file",
                    "filename": "R.md",
                    "snippet": "1\t# csvtidy",
                },
            },
            {"type": "attachment", "attachment": {"type": "date", "filename": "d"}},
            {"type": "api-request-blob", "message": {"content": "copied request"}},
        ]
        with open(self.path, "a", encoding="utf-8") as f:
            f.writelines(json.dumps(e) + "\n" for e in entries)
        shown = self.shown()
        self.assertIn('[user] {"given": []}', shown)
        self.assertIn('[tool_use Read] {"file_path": "読む.md"}', shown)
        # A word longer than a read shows stands on a line of its own.
        self.assertIn("[tool_result]\n" + "x" * 2500 + "\n", shown)
        self.assertIn("[tool_result] done", shown)
        self.assertIn("[web_search_tool_result] found", shown)
        self.assertIn("[shown R.md] 1\t# csvtidy", shown)
        self.assertNotIn("copied request", shown)
        self.assertEqual(shown.count("[shown"), 1)

    def test_a_line_longer_than_a_read_shows_is_cut_at_its_blanks(self):
        # Given: a record holding a line of many words, longer than a read shows
        # When: the learner is started
        # Then: the line is cut at its blanks, every word kept
        said = {"content": [{"type": "text", "text": " ".join(["word"] * 400)}]}
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"type": "assistant", "message": said}) + "\n")
        shown = self.shown()
        self.assertTrue(all(len(line) <= 1000 for line in shown.splitlines()))
        self.assertEqual(shown.count("word"), 400)

    def test_a_line_as_long_as_a_read_shows_is_kept_as_it_is(self):
        # Given: a line of a thousand characters, the last a blank, and one a character longer
        # When: they are wrapped for the learner
        # Then: the first is kept as it is, and the second cut at its blank
        self.assertEqual(run.records.wrapped("a" * 999 + " "), "a" * 999 + " \n")
        self.assertEqual(run.records.wrapped("a" * 999 + " b"), "a" * 999 + "\nb\n")

    def test_the_orchestrator_s_record_is_the_latest_naming_the_result(self):
        # Given: beside the roles' records, agents of another type, a meta file not JSON or not an
        # object, an orchestrator whose prompt is no call or names another result, and two
        # orchestrators naming the result
        # When: the learner is started
        # Then: it is shown the latest orchestrator naming the result, after the roles'
        self.write(os.path.join(self.session, "agent-abad.meta.json"), "x")
        self.write(os.path.join(self.session, "agent-alist.meta.json"), "[]")
        self.write(os.path.join(self.session, "agent-alist.jsonl"), "")
        self.write(os.path.join(self.session, "agent-agone.meta.json"), '{"agentType": "turn:up"}')
        decoys = [
            self.given_record("aother", json.dumps(CALL), "turn:generator"),
            self.given_record("azz", json.dumps(CALL), "turn:zz"),
            self.given_record("anotjson", "not a call", "turn:up"),
            self.given_record("aelse", json.dumps(dict(CALL, result="else.json")), "turn:up"),
        ]
        older = self.given_record("aold", json.dumps(CALL), "turn:up")
        newer = self.given_record("anew", json.dumps(CALL), "turn:up")
        os.utime(older, (1, 1))
        # Each record the orchestrator's is not is the latest of all.
        for decoy in decoys:
            os.utime(decoy, (4e9, 4e9))
        shown = self.shown()
        self.assertIn("I open it.", shown)
        texts = self.prompt()["given"]
        self.assertEqual(len(texts), 2)
        self.assertIn(json.dumps(CALL)[:20], self.read(texts[1]))
        self.assertEqual(run.records.orchestrator([self.path], RESULT), newer)
