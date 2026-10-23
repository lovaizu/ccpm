import json
import os

from helpers import (
    CALL,
    CAN,
    CHECKED,
    CHECKLIST,
    DID,
    EACH,
    EACH_GOOD,
    FOUND,
    GOOD,
    HOLDS,
    IDS,
    LACKING,
    LESSON,
    QUESTION,
    RESULT,
    SECTIONED,
    STOPPED,
    UNTRUE,
    WAITS,
    RepoTest,
    run,
)

ITEM_F1 = {"checklist": "checklists/readme.md", "item": "F-1"}
ITEM_B1 = {"checklist": "checklists/readme.md", "item": "B-1"}
# The first user's Good for each item.
FOUND_B1 = dict(FOUND, item="B-1")
# The first user's stop at an item, as RepoTest.reading gives it.
STOPPED_F1 = dict(ITEM_F1, places=["README.md:1-1"], did=DID, lacking=LACKING)
STOPPED_B1 = dict(ITEM_B1, places=["README.md:1-1"], did=DID, lacking=LACKING)
# The question an item waits on, as the calling AI is sent it, and the answer kept for it.
ASKED = {"questions": [dict(QUESTION, items=[ITEM_B1])]}
ANSWER = dict(ASKED, answer="MIT")


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
        self.assertEqual(self.next(), {"check": [ITEM_F1, ITEM_B1]})

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
        # Given: a run that asked a question, and a CCS the calling AI added the answer to
        # When: the orchestrator goes on with the answer
        # Then: the items are checked again, on the CCS as it is now
        self.asked()
        ccs = self.read_json(CALL["ccs"])
        ccs["retrieved_artifacts"].append({"checklist": "checklists/more.md"})
        self.write_json(CALL["ccs"], ccs)
        self.write("checklists/more.md", CHECKLIST.replace("B-1", "B-3"))
        check = self.heard(self.answered())["check"]
        self.assertEqual([i["item"] for i in check], ["F-1", "B-1", "F-1", "B-3"])
        self.assertNotIn("asked", self.state())

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
        self.assertIn("asked", self.state())

    def test_the_questions_when_none_is_asked_stop(self):
        # Given: a run waiting on the check, and no run at all
        # When: the questions are asked for
        # Then: it stops, saying no question is asked now, or that no run is going
        for result, said in ((RESULT, "asks no question now"), ("none.json", "no run is going")):
            with self.subTest(result=result):
                code, out = self.turn("questions", result)
                self.assertEqual(code, 1)
                self.assertIn(said, out)

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
        # Then: its prompt names the work, the checklists, nothing sent back yet, no answers, and
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
                "answers": [],
                "reply": self.here(RESULT + ".generator.json"),
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
                "parts": ["README.md:1-3"],
                "reply": self.here(RESULT + ".first-user.json"),
            },
        )
        self.assertNotIn(GOOD["good"], move["input"]["prompt"])

    def test_a_generator_asking_before_making_anything_has_the_question_sent_at_once(self):
        # Given: a generator replying, before making anything, with a question only the user can
        # answer, naming the item that waits on it alone
        # When: the orchestrator goes on
        # Then: a line says the generator found the item waiting, the run asks at once, with no
        # first user started, and the question is printed with the item it settles
        out = self.replied({"items": [WAITS], "questions": [QUESTION]})
        self.assertTrue(
            str(out["line"]).startswith(
                "turn: turn:generator found 1 of 2 items waiting on the user's answer. Next,"
                " turn:up will ask what only the user can decide"
            ),
            out,
        )
        self.assertEqual(self.next(), {"asked": RESULT})
        self.assertNotIn("next", self.state())
        self.assertEqual(json.loads(self.turn("questions", RESULT)[1]), ASKED)

    def asked_first(self):
        """The generator asks before making anything, the run asks the calling AI, and its answer
        is handed on; what the script prints then."""
        self.replied({"items": [WAITS], "questions": [QUESTION]})
        self.next()
        return self.answered()

    def test_the_answer_handed_on_is_told_before_it_is_sent_to_the_generator(self):
        # Given: a generator that asked before making anything
        # When: the calling AI's answer is handed on
        # Then: a line says the calling AI answered and that the generator goes on with it
        out = self.asked_first()
        self.assertTrue(
            str(out["line"]).startswith(
                "turn: The calling AI answered. Next, turn:generator will go on with the calling"
                " AI's answer"
            ),
            out,
        )

    def test_the_answer_is_sent_by_message_to_the_generator_that_asked(self):
        # Given: a generator that asked before making anything
        # When: the calling AI's answer is handed on, and the orchestrator goes on after the line
        # Then: the generator, kept started, is sent the question and the answer as it came
        move = self.due(self.asked_first())
        self.assertEqual(move["input"]["to"], IDS["turn:generator"])
        reply = self.here(RESULT + ".generator.json")
        self.assertEqual(
            json.loads(move["input"]["message"]), {"answers": [ANSWER], "reply": reply}
        )

    def test_a_generator_asking_again_is_sent_the_new_answer_alone(self):
        # Given: a generator sent the answer to its question, which asks another
        # When: the second answer is handed on
        # Then: the generator is sent the second answer alone, as it holds the first already
        self.due(self.asked_first())
        second = dict(QUESTION, question="Which name?")
        self.heard(self.replied({"items": [WAITS], "questions": [second]}))
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


class TestGoodCheck(ReadTest):
    """Once the first user's reading ends, the orchestrator checks each Good it gave, and an item
    has its Good only where the first user gave one and the check says it holds."""

    def test_only_the_goods_the_first_user_gave_are_shown_to_check_after_a_line(self):
        # Given: a first user giving one item's Good and stopping at the other, with the round's
        # sending back spent
        # When: the orchestrator goes on, and once more
        # Then: a line says what the first user found and that the orchestrator checks next, and
        # then the first user's Good alone is shown to check
        out = self.first_read(FOUND)
        self.assertEqual(
            out["line"],
            "turn: turn:first-user found the Good of 1 of 2 items. Next, turn:up will check that"
            " each Good the first user found holds, running what it says, of README.md, for 2"
            " items, round 1.",
        )
        self.assertEqual(self.next(), {"goods": [FOUND]})
        self.assertEqual(self.next(), {"goods": [FOUND]})

    def test_every_good_found_and_held_has_the_learner_start(self):
        # Given: a first user finding every item's Good
        # When: the orchestrator's check says each holds
        # Then: a line says how many hold, and the learner is to start, with no second round
        self.first_read(FOUND, FOUND_B1)
        out = self.held()
        self.assertTrue(str(out["line"]).startswith("turn: turn:up found 2 of 2 Goods hold. Next,"))
        self.assertEqual(self.due(out)["input"]["subagent_type"], "turn:learner")

    def test_a_good_the_check_finds_untrue_is_made_again_with_what_it_found(self):
        # Given: a first user finding every item's Good
        # When: the orchestrator's check finds the first untrue, with where and what is lacking
        # Then: the second round's generator is started anew with that item alone, as the check
        # gave it
        self.first_read(FOUND, FOUND_B1)
        move = self.due(self.held(UNTRUE, dict(HOLDS, item="B-1")))
        self.assertEqual(move["tool"], "Agent")
        self.assertEqual(json.loads(move["input"]["prompt"])["sent_back"], [UNTRUE])

    def test_an_item_the_first_user_found_no_good_for_is_made_again_as_it_gave_it(self):
        # Given: a first user giving one item's Good and stopping at the other
        # When: the orchestrator's check says the Good holds
        # Then: the second round's generator is given the stop as the first user gave it
        self.first_read(FOUND)
        self.due(self.held())
        self.assertEqual(self.prompt()["sent_back"], [STOPPED_B1])

    def test_a_reading_with_no_good_goes_to_the_next_round_with_no_check(self):
        # Given: a first user finding no item's Good
        # When: the orchestrator goes on
        # Then: a line says so, and the second round's generator is due, with nothing to check
        out = self.first_read()
        self.assertTrue(
            str(out["line"]).startswith(
                "turn: turn:first-user found the Good of 0 of 2 items. Next, turn:generator will"
            ),
            out,
        )
        self.assertIn("round 2", out["line"])
        self.assertEqual(self.prompt()["sent_back"], [STOPPED_F1, STOPPED_B1])

    def test_a_check_out_of_its_form_stops_and_the_goods_wait(self):
        # Given: a first user giving one item's Good
        # When: the check leaves it out, gives an item not shown, or says it holds as false
        # Then: it stops, naming what is wrong, and the Goods still wait on the check
        self.first_read(FOUND)
        self.next()
        for items, said in (
            ([], "F-1 is left out"),
            ([HOLDS, dict(HOLDS, item="B-1")], "B-1 is not an item judged here"),
            ([dict(HOLDS, holds=False)], '"holds" is not true'),
        ):
            with self.subTest(said=said):
                out = self.refused({"items": items})
                self.assertIn("the check of the Goods is not filled", out)
                self.assertIn(said, out)
        self.assertEqual(self.next(), {"goods": [FOUND]})

    def test_a_check_in_a_json_fence_is_recorded(self):
        # Given: a first user giving one item's Good
        # When: the check is given inside a ```json fence
        # Then: it is taken as the check itself
        self.first_read(FOUND)
        self.next()
        code, out = self.turn(
            "next", RESULT, stdin=f"```json\n{json.dumps({'items': [HOLDS]})}\n```"
        )
        self.assertEqual(code, 0, out)
        self.assertEqual(self.state()["next"]["agent"], "turn:generator")

    def test_goods_too_long_for_one_read_are_shown_page_by_page(self):
        # Given: a run waiting on the check of a Good whose words run past two pages
        # When: the orchestrator runs the script with no input, then asks for each page after
        # Then: each page is headed by its number among all and how to see the others, the pages
        # together are the Goods to check, and a page past the last stops
        self.first_read(dict(FOUND, good="x" * 45000))
        self.next()
        goods = self.state()["goods"]
        pages = []
        for asked in ((), ("2",), ("3",)):
            code, out = self.turn("next", RESULT, *asked)
            self.assertEqual(code, 0, out)
            head, page = out.split("\n", 1)
            self.assertTrue(head.startswith(f"goods, page {len(pages) + 1} of 3: "), head)
            self.assertIn(f"turn.py next {RESULT} <page>", head)
            pages.append(page[:-1])
        self.assertEqual(json.loads("".join(pages)), {"goods": goods})
        self.assertEqual([len(p) for p in pages[:2]], [20000, 20000])
        for page in ("0", "4", "a"):
            self.assertIn(f"page {page} is not one of 1 to 3", self.turn("next", RESULT, page)[1])

    def test_goods_of_two_pages_are_shown_page_by_page(self):
        # Given: a run waiting on the check of Goods that run to two pages
        # When: the orchestrator runs the script with no input
        # Then: the first page is headed by its number of two
        self.first_read(dict(FOUND, good="x" * 25000))
        self.next()
        out = self.turn("next", RESULT)[1]
        self.assertTrue(out.startswith("goods, page 1 of 2: "), out[:80])

    def test_goods_short_enough_for_one_read_are_printed_as_they_are(self):
        # Given: a run waiting on the check of Goods that fit in one page
        # When: the orchestrator asks for the first page
        # Then: the Goods are printed with no head, as with no page asked
        self.first_read(FOUND)
        self.next()
        code, out = self.turn("next", RESULT, "1")
        self.assertEqual((code, json.loads(out)), (0, self.next()))

    def test_a_page_asked_while_the_run_waits_on_a_role_stops(self):
        # Given: a run waiting on the generator's reply
        # When: the orchestrator asks for a page
        # Then: it stops, saying to go on with no page
        code, out = self.turn("next", RESULT, "2")
        self.assertEqual(code, 1, out)
        self.assertIn(f"run `turn.py next {RESULT}`", out)


class TestRounds(ReadTest):
    """Only the items without Good are made again in the next round, and an item two rounds leave
    without Good becomes a question."""

    def second(self):
        """The first round taken to its end with F-1 held and B-1 without Good; the move starting
        the second round's generator."""
        self.first_read(FOUND)
        return self.due(self.held())

    def left(self):
        """Both rounds taken to their end with B-1 without Good, the check told; what is shown."""
        self.second()
        self.first_read(FOUND)
        out = self.held()
        self.assertEqual(
            out["line"],
            "turn: turn:up found 1 of 1 Goods hold. Next, turn:up will word a question for each"
            " item two rounds left without Good, of README.md, for 2 items, round 2.",
        )
        return self.next()

    def test_the_next_round_starts_its_generator_anew(self):
        # Given: a first round leaving B-1 without Good
        # When: the orchestrator goes on after the line
        # Then: a line says the second round's generator makes the work, and it is started anew,
        # not sent a message
        self.first_read(FOUND)
        out = self.held()
        self.assertIn("round 2", out["line"])
        move = self.due(out)
        self.assertEqual(
            (move["tool"], move["input"]["subagent_type"]), ("Agent", "turn:generator")
        )

    def test_the_next_round_starts_its_first_user_anew(self):
        # Given: a second round whose generator replied with every item's Good
        # When: the orchestrator goes on after the line
        # Then: the first user is started anew, not sent a message
        self.second()
        first = self.due(self.made())
        self.assertEqual(
            (first["tool"], first["input"]["subagent_type"]), ("Agent", "turn:first-user")
        )

    def test_the_next_round_s_first_user_reads_every_item_again(self):
        # Given: a second round's first user, B-1 alone made again
        # When: it replies with F-1's Good alone
        # Then: it is sent what is wrong, B-1 left out, as a remake may break an item that held
        self.second()
        self.due(self.made())
        said = self.replied({"items": [FOUND]})
        self.assertIn("B-1 is left out", said["move"]["input"]["message"])

    def test_a_second_round_giving_every_good_returns_its_goods(self):
        # Given: a first round leaving B-1 without Good
        # When: the second round's first user finds both Goods and the check says they hold
        # Then: the run returns with both Goods of the second round
        self.second()
        self.first_read(FOUND, FOUND_B1)
        self.assertEqual(self.learnt(self.held()), {"returned": RESULT})
        self.assertEqual(self.read_json(RESULT)["items"], [FOUND, FOUND_B1])

    def test_an_item_two_rounds_leave_without_good_is_shown_for_a_question(self):
        # Given: two rounds leaving B-1 without Good
        # When: the orchestrator goes on after the line
        # Then: B-1 is shown as the first user last gave it, with no learner started
        self.assertEqual(self.left(), {"left": [STOPPED_B1]})
        self.assertNotIn("next", self.state())
        self.assertEqual(self.next(), {"left": [STOPPED_B1]})

    def test_the_question_for_an_item_left_is_sent_at_once(self):
        # Given: an item two rounds left without Good
        # When: the orchestrator gives its question for it
        # Then: a line says the item waits on the user's answer, and the run asks it
        self.left()
        out = self.next({"items": [WAITS], "questions": [QUESTION]})
        self.assertTrue(
            str(out["line"]).startswith(
                "turn: turn:up found 1 of 2 items waiting on the user's answer."
            ),
            out,
        )
        self.assertEqual(self.next(), {"asked": RESULT})
        self.assertEqual(json.loads(self.turn("questions", RESULT)[1]), ASKED)

    def answered_left(self):
        """Both rounds leaving B-1 without Good, its question asked, and the calling AI's answer
        handed on; what the script prints then."""
        self.left()
        self.heard(self.next({"items": [WAITS], "questions": [QUESTION]}))
        return self.answered()

    def test_once_answered_the_item_left_is_made_again_with_the_answer(self):
        # Given: an item two rounds left without Good, asked of the calling AI
        # When: the answer is handed on
        # Then: a third round starts its generator anew with the item as last found and the
        # answer
        out = self.answered_left()
        self.assertIn("round 3", out["line"])
        move = self.due(out)
        prompt = json.loads(move["input"]["prompt"])
        self.assertEqual((move["tool"], prompt["sent_back"]), ("Agent", [STOPPED_B1]))
        self.assertEqual(prompt["answers"], [ANSWER])

    def test_once_answered_two_rounds_more_run_before_the_item_is_asked_again(self):
        # Given: an item two rounds left without Good, answered
        # When: the third and the fourth round leave it without Good too
        # Then: the third goes on to the fourth, and the fourth's end shows it for a question
        self.due(self.answered_left())
        self.first_read(FOUND)
        self.assertIn("round 4", self.held()["line"])
        self.next()
        self.first_read(FOUND)
        self.assertEqual(self.heard(self.held()), {"left": [STOPPED_B1]})

    def test_each_answer_lets_two_rounds_more_run(self):
        # Given: an item left without Good after the fourth round, once answered after the second
        # When: it is answered again, and the fifth and the sixth round leave it without Good
        # Then: the fifth goes on to the sixth, and the sixth's end shows it for a question
        self.due(self.answered_left())
        self.first_read(FOUND)
        self.due(self.held())
        self.first_read(FOUND)
        self.heard(self.held())
        self.heard(self.next({"items": [WAITS], "questions": [QUESTION]}))
        out = self.answered()
        self.assertIn("round 5", out["line"])
        self.due(out)
        self.first_read(FOUND)
        self.assertIn("round 6", self.held()["line"])
        self.next()
        self.first_read(FOUND)
        self.assertEqual(self.heard(self.held()), {"left": [STOPPED_B1]})

    def test_questions_for_the_items_left_out_of_their_form_stop(self):
        # Given: an item two rounds left without Good
        # When: the orchestrator gives it a Good, or leaves it out
        # Then: it stops, naming what is wrong, and the item is still shown
        self.left()
        for items, said in (
            ([dict(FOUND_B1)], 'must hold "question"'),
            ([], "B-1 is left out"),
        ):
            with self.subTest(said=said):
                out = self.refused({"items": items, "questions": []})
                self.assertIn("the questions are not filled", out)
                self.assertIn(said, out)
        self.assertEqual(self.next(), {"left": [STOPPED_B1]})


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
        self.due(self.made(GOOD, dict(GOOD, item="B-1"), EACH_GOOD))
        back = dict(STOPPED, item="B-2", places=["README.md:5-7"])
        move = self.due(self.replied({"items": [FOUND, FOUND_B1, back]}))
        self.assertEqual(move["input"]["to"], IDS["turn:generator"])
        self.assertEqual(json.loads(move["input"]["message"])["sent_back"], [back])

    def test_an_item_given_a_good_for_every_part_is_good_in_the_result(self):
        # Given: a first user giving an item asked of each part a Good for every part, and a check
        # saying it holds
        # When: the run returns
        # Then: the result holds the item with its Good for every part
        claim = (GOOD, dict(GOOD, item="B-1"), EACH_GOOD)
        self.first_read(FOUND, FOUND_B1, EACH_GOOD, claim=claim)
        self.assertEqual(self.learnt(self.held()), {"returned": RESULT})
        self.assertEqual(self.read_json(RESULT)["items"], [FOUND, FOUND_B1, EACH_GOOD])

    def test_a_reply_giving_an_each_part_item_without_every_part_is_sent_back_to_its_role(self):
        # Given: a generator replying with an item asked of each part given one part alone
        # When: the orchestrator goes on
        # Then: the generator is sent what is wrong, to write its reply again, and the reply file
        # is removed until it does
        one = dict(EACH_GOOD, parts=EACH_GOOD["parts"][:1])
        out = self.made(GOOD, dict(GOOD, item="B-1"), one)
        self.assertEqual(out["move"]["tool"], "SendMessage")
        self.assertEqual(out["move"]["input"]["to"], IDS["turn:generator"])
        self.assertIn("in your form, filled:", out["move"]["input"]["message"])
        self.assertFalse(os.path.exists(RESULT + ".generator.json"))
        move = self.due(self.made(GOOD, dict(GOOD, item="B-1"), EACH_GOOD))
        self.assertEqual(move["tool"], "Agent")


class TestLearner(ReadTest):
    def setUp(self):
        super().setUp()
        for agent, agent_id in IDS.items():
            self.given_record(agent_id, "{}", agent)
        self.orchestrator = self.given_record("aup", json.dumps(CALL), "turn:up")
        self.first_read(FOUND, FOUND_B1)
        self.learner = self.held()

    def test_the_learner_starts_once_on_every_record_of_the_run_shown_as_text(self):
        # Given: a run whose every item has its Good
        # When: the check is recorded
        # Then: the learner is to be started with the record of every role that replied and the
        # orchestrator's, each shown as text beside the result, and where it replies
        move = self.due(self.learner)
        self.assertEqual(move["input"]["subagent_type"], "turn:learner")
        texts = [self.here(f"{RESULT}.records/{n}.txt") for n in (1, 2, 3)]
        self.assertEqual(
            json.loads(move["input"]["prompt"]),
            {"given": texts, "reply": self.here(RESULT + ".learner.json")},
        )
        self.assertIn("[user] {}", self.read(texts[0]))
        self.assertIn('"result": ".tasks/readme-result.json"', self.read(texts[2]))

    def test_a_record_not_kept_is_left_out(self):
        # Given: a run whose records are not where Claude Code keeps them
        # When: the learner is started
        # Then: it is given none
        RepoTest.setUp(self)
        self.started()
        self.first_read(FOUND, FOUND_B1)
        self.due(self.held())
        self.assertEqual(self.prompt()["given"], [])

    def test_the_lessons_go_into_the_result_with_every_good_and_the_run_returns(self):
        # Given: a learner replying with a general lesson and one of the project's own
        # When: the orchestrator goes on
        # Then: the result holds where the work is, each item's Good as the first user gave it,
        # the lessons and what the learner checked, and the run returns
        own = dict(LESSON, whose="own", lesson="the checklist names no license item")
        self.due(self.learner)
        out = self.replied({"lessons": [LESSON, own], "checked": CHECKED})
        self.assertEqual(
            self.read_json(RESULT),
            {
                "work": ["README.md"],
                "items": [FOUND, FOUND_B1],
                "lessons": [LESSON, own],
                "checked": CHECKED,
            },
        )
        self.assertEqual(self.heard(out), {"returned": RESULT})

    def test_once_returned_what_the_run_kept_beside_the_result_is_removed(self):
        # Given: a run whose learner replied
        # When: the run returns
        # Then: the result and the CCS alone stay beside it
        self.learnt(self.learner)
        self.assertEqual(sorted(os.listdir(".tasks")), ["readme-result.json", "readme.json"])

    def test_the_result_is_written_one_key_or_value_to_a_line(self):
        # Given: a run that returns
        # When: its result is written
        # Then: each key and each value of a list stands on a line of its own
        self.learnt(self.learner)
        with open(RESULT, encoding="utf-8") as f:
            lines = f.read().splitlines()
        self.assertEqual(lines[:4], ["{", ' "work": [', '  "README.md"', " ],"])

    def test_a_lesson_quoting_words_no_record_holds_is_sent_back_to_the_learner(self):
        # Given: a learner whose lesson quotes words its record does not hold
        # When: the orchestrator goes on
        # Then: the learner is sent what is wrong
        self.due(self.learner)
        lesson = dict(LESSON, grounds=[{"record": 1, "quote": "never said"}])
        out = self.replied({"lessons": [lesson], "checked": CHECKED})
        self.assertEqual(out["move"]["input"]["to"], IDS["turn:learner"])
        self.assertIn("is not in record 1 as written", out["move"]["input"]["message"])

    def test_the_result_holds_every_good_in_the_checklists_order(self):
        # Given: a first user giving the Goods out of the checklist's order
        # When: the run returns
        # Then: the result holds them in the checklist's order
        RepoTest.setUp(self)
        self.started()
        self.due(self.made())
        self.write_json(run.state_path(RESULT), dict(self.state(), sent=run.SENDS))
        self.replied({"items": [FOUND_B1, FOUND]})
        self.learnt(self.held())
        self.assertEqual(self.read_json(RESULT)["items"], [FOUND, FOUND_B1])


class TestRecordsShown(ReadTest):
    """Each record is shown to the learner as what the role was given, said, used and was shown."""

    def setUp(self):
        super().setUp()
        self.path = self.given_record(IDS["turn:generator"], '{"given": []}', "turn:generator")

    def shown(self):
        """The generator's record as the learner is shown it after the run."""
        self.first_read(FOUND, FOUND_B1)
        self.due(self.held())
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
