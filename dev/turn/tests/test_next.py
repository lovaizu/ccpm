import json

from helpers import (
    ACCURATE,
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
    MARKED,
    PARTS,
    QUESTION,
    READ_GIVEN,
    READ_SHOWN,
    SECTIONED,
    SENT_BACK,
    STATEMENT,
    UNSOURCED,
    WAITS,
    RepoTest,
)

RESULT = CALL["result"]
RAN = {"command": "printf a", "output": "a"}


def judged(item):
    """An item's finding without the checklist and ID that name it."""
    return {k: v for k, v in item.items() if k not in ("checklist", "item")}


ITEM_F1 = {"checklist": "checklists/readme.md", "item": "F-1"}
ITEM_B1 = {"checklist": "checklists/readme.md", "item": "B-1"}
# A reading finding every item's Good.
EVERY_GOOD = {"items": [GOOD, dict(GOOD, item="B-1")], "questions": []}
# A first user's stop at the item waiting on a question.
WAITS_READ = dict(ITEM_B1, places=["README.md:3-3"])
# The orchestrator's decision keeping its findings: the first item Good, the other waiting.
AGREED = {"items": [GOOD, WAITS], "questions": []}
# A generator's claim on a run whose CCS names the accuracy checklist too, after reading it whole
# with the rest it was given.
CLAIM_ACCURATE = {
    "items": [GOOD, dict(GOOD, item="B-1"), ACCURATE],
    "questions": [],
    "statements": [],
}
READ_ACCURACY = READ_GIVEN + (("Read", {"file_path": "checklists/accuracy.md"}),)


class ReadTest(RepoTest):
    def setUp(self):
        super().setUp()
        self.started()

    def read(self, reading):
        return self.read_text(json.dumps(reading))

    def read_text(self, text):
        return self.turn("next", RESULT, stdin=text)

    def claimed(self, *statements, ran=()):
        """The generator started as the script printed, replying with the statements, after reading
        what it was given and running the commands, each with what it printed."""
        prompt = self.read_json(RESULT)["running"]["next"]["prompt"]
        uses = tuple(("Bash", {"command": c}, o) for c, o in ran)
        reply = {"items": [GOOD, dict(GOOD, item="B-1")], "questions": [], "statements": statements}
        self.assertEqual(self.replied("turn:generator", prompt, reply, *READ_GIVEN, *uses), (0, ""))


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


class TestReading(ReadTest):
    def test_a_reading_that_sends_items_back_gives_the_generator_them(self):
        # Given: a reading that finds one item's Good and sends the other back
        # When: the reading is recorded
        # Then: the generator is to be started again with the item sent back and what the receiver
        # gets once it has its Good
        out = self.next({"items": [GOOD, SENT_BACK], "questions": [], "statements": [MARKED]})
        self.assertEqual(out["agent"], "turn:generator")
        self.assertEqual(self.given()["sent_back"], [SENT_BACK])
        self.assertEqual(self.read_json(RESULT)["running"]["next"]["prompt"], out["prompt"])

    def test_a_reading_that_sends_a_statement_back_gives_the_generator_it(self):
        # Given: a reading finding every item's Good and one statement whose source it does not
        # find
        # When: the reading is recorded
        # Then: the generator is to be started again with the statement and what is wrong with it,
        # and no item sent back
        out = self.next(
            {
                "items": [GOOD, dict(GOOD, item="B-1")],
                "questions": [],
                "statements": [MARKED],
                "unsourced": [UNSOURCED],
            }
        )
        self.assertEqual(out["agent"], "turn:generator")
        self.assertEqual((self.given()["sent_back"], self.given()["unsourced"]), ([], [UNSOURCED]))

    def test_a_statement_marked_how_the_product_behaves_with_no_run_is_sent_back(self):
        # Given: a generator grounding a statement in quotes as a decision, and grounding one in a
        # run at other lines, and a reading marking the first how the product behaves
        # When: the reading is recorded
        # Then: the generator is to be started again with the first, as no run shows it
        run = {"lines": ["README.md:1-1"], "kind": "behavior", "ran": [RAN]}
        self.claimed(STATEMENT, run, ran=[(RAN["command"], RAN["output"])])
        behaves = dict(MARKED, kind="behavior")
        out = self.next(
            {
                "items": [GOOD, dict(GOOD, item="B-1")],
                "questions": [],
                "statements": [behaves, dict(behaves, lines=run["lines"])],
            }
        )
        self.assertEqual(out["agent"], "turn:generator")
        gets = (
            "it tells how the product behaves, and no command run shows it: run one that shows"
            " it, or take it out of the work"
        )
        self.assertEqual(self.given()["unsourced"], [{"lines": ["README.md:3-3"], "gets": gets}])

    def test_a_statement_with_an_empty_list_of_runs_is_not_shown_by_a_run(self):
        # Given: a generator grounding a statement in quotes, with an empty list of runs beside
        # them, and a reading marking it how the product behaves
        # When: the reading is recorded
        # Then: the generator is to be started again with it, as no run shows it
        self.claimed(dict(STATEMENT, ran=[]))
        reading = dict(EVERY_GOOD, statements=[dict(MARKED, kind="behavior")])
        self.assertEqual(self.next(reading)["agent"], "turn:generator")
        self.assertEqual(self.given()["unsourced"][0]["lines"], MARKED["lines"])

    def test_a_statement_the_reading_sends_back_itself_is_sent_back_once(self):
        # Given: a generator grounding a statement in quotes as a decision, and a reading marking
        # it how the product behaves and sending it back itself
        # When: the reading is recorded
        # Then: the generator is given it once, as the reading sent it back
        self.claimed(STATEMENT)
        reading = {
            "items": [GOOD, dict(GOOD, item="B-1")],
            "questions": [],
            "statements": [dict(MARKED, kind="behavior")],
            "unsourced": [UNSOURCED],
        }
        self.next(reading)
        self.assertEqual(self.given()["unsourced"], [UNSOURCED])

    def test_a_statement_marked_how_the_product_behaves_resting_on_a_run_passes(self):
        # Given: a generator grounding a statement over lines 2 to 3 in a run, and a reading
        # marking line 3 how the product behaves
        # When: the reading is recorded
        # Then: the first user is to be started, as a run shows it
        run = {"lines": ["README.md:2-3"], "kind": "behavior", "ran": [RAN]}
        self.claimed(run, ran=[(RAN["command"], RAN["output"])])
        behaves = dict(MARKED, kind="behavior")
        out = self.next(
            {"items": [GOOD, dict(GOOD, item="B-1")], "questions": [], "statements": [behaves]}
        )
        self.assertEqual(out["agent"], "turn:first-user")

    def test_a_reading_with_every_item_good_or_waiting_starts_the_first_user(self):
        # Given: a call naming what the receiver reads the work for and what they have with it, a
        # CCS naming an accuracy checklist too, and a reading that finds one item's Good and has
        # the other wait on a question
        # When: the reading is recorded
        # Then: the first user is to be started with the work, what the receiver has, who the
        # receiver is and what for, and the usability checklists, and not the CCS, the reading or
        # the accuracy checklist
        self.with_accuracy()
        call = dict(CALL, kind=dict(CALL["kind"], use="purpose", has="page"))
        self.turn("start", json.dumps(call))
        can = CAN + [{"checklist": "checklists/accuracy.md", "item": "B-1", "can": "the decisions"}]
        self.next({"items": can, "questions": []})
        prompt = json.dumps({"run": RESULT})
        self.assertEqual(
            self.replied("turn:generator", prompt, CLAIM_ACCURATE, *READ_ACCURACY), (0, "")
        )
        out = self.next(
            {"items": [GOOD, WAITS, ACCURATE], "questions": [QUESTION], "statements": [MARKED]}
        )
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

    def test_the_parts_of_the_work_are_printed_when_asked(self):
        # Given: a run whose work is a README of a title, an opening and one section
        # When: the parts are asked for, and asked for a result no run was started for
        # Then: the parts are printed, each as its lines; and the second stops, naming the path
        self.write("README.md", SECTIONED)
        self.assertEqual(self.turn("parts", RESULT), (0, json.dumps({"parts": PARTS}) + "\n"))
        code, out = self.turn("parts", "elsewhere.json")
        self.assertEqual(code, 1)
        self.assertIn("elsewhere.json", out)

    def test_a_reading_given_after_the_run_returned_stops(self):
        # Given: a run that has returned
        # When: another reading is given
        # Then: it stops, saying the run has returned and how to start one
        self.through(EVALUATED)
        self.learnt(self.next(AGREED))
        code, out = self.read(
            {"items": [GOOD, WAITS], "questions": [QUESTION], "statements": [MARKED]}
        )
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
        reading = json.dumps({"items": [GOOD, SENT_BACK], "questions": [], "statements": [MARKED]})
        code, out = self.read_text(f"```json\n{reading}\n```\n")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.given()["sent_back"], [SENT_BACK])


class TestReaders(ReadTest):
    def test_the_evaluator_is_started_with_the_first_users_reading(self):
        # Given: a run whose first user has replied with the Good it found for one item
        # When: the orchestrator goes on
        # Then: the evaluator is to be started with what the first user was, and its reading
        out = self.next({"items": [GOOD, WAITS], "questions": [QUESTION], "statements": [MARKED]})
        first = self.given()
        self.replied("turn:first-user", out["prompt"], {"items": self.reading(FOUND)})
        out = self.next()
        self.assertEqual(out["agent"], "turn:evaluator")
        self.assertEqual(self.given(), dict(first, reading=[FOUND]))

    def test_going_on_before_the_first_user_replies_stops(self):
        # Given: a run whose first user is to be started
        # When: the orchestrator goes on before it has replied
        # Then: it stops, saying to start the first user with the prompt printed and wait
        self.next({"items": [GOOD, WAITS], "questions": [QUESTION], "statements": [MARKED]})
        self.assertIn("start turn:first-user", self.refused())

    def test_an_evaluator_agreeing_with_the_findings_still_has_every_item_decided(self):
        # Given: findings with one item's Good and the other waiting, and an evaluator giving a
        # Good to the first item alone
        # When: the orchestrator goes on, and then decides as it found
        # Then: both items come to decide, as readers that agree may still carry a doubt inside a
        # Good; after the learner, the result holds where the work is, the orchestrator's Good
        # with its lines, and the question with its recommended answer and the item it settles,
        # and the run has returned
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
        self.started(dict(CALL, result="result.json"))
        reading = {"items": [GOOD, WAITS], "questions": [QUESTION], "statements": [MARKED]}
        _, out = self.turn("next", "result.json", stdin=json.dumps(reading))
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
        # Given: a reading giving an item asked of each part no Good where one part does not give
        # it
        # When: the reading is recorded
        # Then: the generator is to be started again with the item, what the receiver gets and
        # the part where it is not found
        back = dict(SENT_BACK, item="B-2", places=["README.md:5-7"])
        reading = {"items": [GOOD, WAITS, back], "questions": [QUESTION], "statements": [MARKED]}
        self.assertEqual(self.next(reading)["agent"], "turn:generator")
        self.assertEqual(self.given()["sent_back"], [back])

    def test_an_item_given_a_good_for_every_part_is_good_in_the_result(self):
        # Given: findings, a first user and an evaluator each giving an item asked of each part a
        # Good for every part
        # When: the run returns
        # Then: the result holds the item with its Good for every part
        findings = (GOOD, WAITS, EACH_GOOD)
        self.through(EVALUATED, EACH_GOOD, findings=findings, found=(FOUND, EACH_GOOD))
        decision = {"items": list(findings), "questions": []}
        self.assertEqual(self.learnt(self.next(decision)), {"returned": RESULT})
        self.assertEqual(self.read_json(RESULT)["items"], [GOOD, EACH_GOOD])

    def test_an_item_a_reader_gave_no_good_for_every_part_goes_to_decide(self):
        # Given: findings giving an item asked of each part a Good for every part, and an
        # evaluator that leaves it out
        # When: the orchestrator goes on
        # Then: the item comes back to decide with the orchestrator's Good for every part
        findings = (GOOD, WAITS, EACH_GOOD)
        out = self.through(EVALUATED, findings=findings, found=(FOUND, EACH_GOOD))
        decided = [i for i in out["decide"]["items"] if i["item"] == "B-2"]
        self.assertEqual(decided[0]["orchestrator"], judged(EACH_GOOD))
        self.assertEqual(decided[0]["first_user"], judged(EACH_GOOD))
        self.assertIsNone(decided[0]["evaluator"])
        decision = {"items": list(findings), "questions": []}
        self.assertEqual(self.learnt(self.next(decision)), {"returned": RESULT})
        self.assertEqual(self.read_json(RESULT)["items"], [GOOD, EACH_GOOD])

    def test_a_good_for_every_part_no_reader_found_stops(self):
        # Given: an item asked of each part the orchestrator found Good while neither reader gave it
        # When: the decision gives it a Good for every part
        # Then: it stops, asking for what the receiver gets and where it is not found
        findings = (GOOD, WAITS, EACH_GOOD)
        self.through(EVALUATED, findings=findings, found=(FOUND,))
        out = self.refused({"items": list(findings), "questions": []})
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
        # findings' question any more
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
        # Given: both items to decide, with one question asked in the findings
        # When: the orchestrator has the first wait on a new question, numbered after the findings',
        # and the second still wait on the findings' question
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
        # Given: an item the orchestrator found Good while neither the first user nor the
        # evaluator found its Good
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
        for findings, evaluated in (
            ((GOOD, WAITS), dict(EVALUATED, item="B-1")),
            ((dict(WAITS, item="F-1"), dict(GOOD, item="B-1")), EVALUATED),
        ):
            with self.subTest(evaluated=evaluated["item"]):
                super().setUp()
                self.through(evaluated, findings=findings, found=())
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

    def test_a_reading_leaving_an_item_without_good_starts_the_learner(self):
        # Given: a first reading whose decision leaves an item without Good
        # When: the decision is recorded
        # Then: the learner is to be started with every item's finding, the record of every
        # role that replied in the run, and no lesson yet
        self.assertEqual(self.learner["agent"], "turn:learner")
        records = [
            f"{self.repo}/session/subagents/agent-{a}.jsonl" for a in ("first-user", "evaluator")
        ]
        self.assertEqual(
            self.given(),
            {"findings": [GOOD, SENT_BACK], "records": records, "lessons": []},
        )

    def test_a_reading_with_every_item_good_starts_the_learner_too(self):
        # Given: a first reading whose evaluator agrees with the findings
        # When: the orchestrator goes on
        # Then: the learner is to be started, as a run may get its Goods by chance or with waste
        super().setUp()
        self.started()
        self.through(EVALUATED)
        self.assertEqual(self.next(AGREED)["agent"], "turn:learner")

    def test_the_orchestrators_own_record_is_shown_to_the_learner(self):
        # Given: a run whose orchestrator's record is kept
        # When: the learner is started after a reading
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
        out = self.next({"items": [GOOD, WAITS], "questions": [QUESTION], "statements": [MARKED]})
        self.assertEqual(out["agent"], "turn:first-user")
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
        # Given: a reading with every item Good, and a learner that found no lesson on the run
        # When: the orchestrator goes on
        # Then: the run returns, as nothing is offered
        super().setUp()
        self.started()
        self.through(EVALUATED)
        out = self.next(AGREED)
        reply = {"process": [], "checked": CHECKED}
        self.replied("turn:learner", out["prompt"], reply)
        self.assertEqual(self.next(), {"returned": RESULT})

    def test_with_no_lesson_after_a_reading_leaving_an_item_without_good_the_work_is_made_again(
        self,
    ):
        # Given: a first reading leaving an item without Good, and a learner that found no lesson
        # When: the orchestrator goes on
        # Then: the generator makes the work again with the item, as nothing is offered to take
        reply = {"process": [], "checked": CHECKED}
        self.replied("turn:learner", self.learner["prompt"], reply)
        self.assertEqual(self.next()["agent"], "turn:generator")
        self.assertEqual(self.given()["sent_back"], [SENT_BACK])

    def test_an_item_still_without_good_after_the_second_reading_is_returned(self):
        # Given: a work made again with what the learner found, and a lesson taken
        # When: its second reading leaves an item without Good, and the learner after it gives
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
        # Given: a learner's run, whose first user's record holds its prompt and a Read
        # When: the learner asks for the first record's first page
        # Then: it is shown with its number and page among all, the prompt and the tool used
        code, out = self.turn("record", RESULT, "1", "1")
        self.assertEqual(code, 0, out)
        first = out.splitlines()[0]
        self.assertEqual(first, f"record 1 of 2, page 1 of 1: {self.given()['records'][0]}")
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
        # Given: a learner's run of three records
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
                self.assertEqual(out.splitlines()[0], f"record {n} of 3, page 1 of 1: {path}")

    def test_a_record_or_page_out_of_range_stops(self):
        # Given: a learner's run of two records, each of one page
        # When: a record or page outside them, or one not a number, is asked for
        # Then: it is stopped, naming what there is
        for number, page, said in (
            ("3", "1", "record 3 is not one of 1 to 2"),
            ("0", "1", "record 0 is not one of 1 to 2"),
            ("1", "0", "page 0 is not one of 1 to 1"),
            ("1", "2", "page 2 is not one of 1 to 1"),
            ("a", "1", "record a is not one of 1 to 2"),
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

    def test_a_statement_sent_back_out_of_its_form_stops(self):
        # Given: a statement sent back with empty words, or with lines outside the work
        # When: it is recorded
        # Then: it stops, naming the statement
        for statement, said in (
            (dict(UNSOURCED, gets=" "), 'empty "gets"'),
            (dict(UNSOURCED, lines=["docs/start.md:1"]), "is not lines of the work"),
        ):
            with self.subTest(said=said):
                self.stops(
                    {"items": [GOOD, SENT_BACK], "questions": [], "unsourced": [statement]},
                    "statement 1 of unsourced",
                    said,
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


class TestAccuracy(RepoTest):
    """A run whose CCS names an accuracy checklist beside the README's: its item is answered by
    the orchestrator alone, which holds the sources."""

    def setUp(self):
        super().setUp()
        self.with_accuracy()
        self.turn("start", json.dumps(CALL))
        can = CAN + [{"checklist": "checklists/accuracy.md", "item": "B-1", "can": "the decisions"}]
        prompt = self.next({"items": can, "questions": []})["prompt"]
        self.assertEqual(
            self.replied("turn:generator", prompt, CLAIM_ACCURATE, *READ_ACCURACY), (0, "")
        )
        reading = {
            "items": [GOOD, WAITS, ACCURATE],
            "questions": [QUESTION],
            "statements": [MARKED],
        }
        self.prompt = self.next(reading)["prompt"]

    def test_the_first_user_answers_the_usability_items_alone(self):
        # Given: a first user started on the run
        # When: it replies with the accuracy item among its items
        # Then: it is kept going; replying with the README's items alone, the evaluator is started,
        # given the usability checklists alone
        code, err = self.replied(
            "turn:first-user", self.prompt, {"items": [FOUND, WAITS_READ, ACCURATE]}
        )
        self.assertEqual(code, 2, err)
        self.assertIn("checklists/accuracy.md B-1", err)
        reply = {"items": [FOUND, WAITS_READ]}
        self.assertEqual(self.replied("turn:first-user", self.prompt, reply), (0, ""))
        self.assertEqual(self.next()["agent"], "turn:evaluator")
        self.assertEqual(self.given()["checklists"], ["checklists/readme.md"])

    def test_an_accuracy_item_takes_the_orchestrators_good_alone(self):
        # Given: readers that give the README's items alone
        # When: the decision gives the accuracy item the orchestrator's Good
        # Then: it is taken, and the result holds it
        self.replied("turn:first-user", self.prompt, {"items": [FOUND, WAITS_READ]})
        out = self.next()
        self.replied("turn:evaluator", out["prompt"], {"items": [EVALUATED]})
        decide = self.next()["decide"]["items"]
        accuracy = [i for i in decide if i["checklist"] == "checklists/accuracy.md"]
        self.assertEqual(accuracy[0]["first_user"], None)
        self.assertEqual(accuracy[0]["evaluator"], None)
        out = self.next({"items": [GOOD, WAITS, ACCURATE], "questions": []})
        self.assertEqual(self.learnt(out), {"returned": RESULT})
        self.assertEqual(self.read_json(RESULT)["items"], [GOOD, ACCURATE])
