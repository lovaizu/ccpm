import json

from helpers import CALL, GOOD, QUESTION, SENT_BACK, WAITS, RepoTest

RESULT = CALL["result"]


class ReadTest(RepoTest):
    def setUp(self):
        super().setUp()
        self.started()

    def read(self, reading):
        return self.turn("read", RESULT, stdin=json.dumps(reading))


class TestRead(ReadTest):
    def test_a_reading_that_sends_items_back_gives_the_generator_them(self):
        # Given: a reading that finds one item's Good and sends the other back
        # When: the reading is recorded
        # Then: the generator is to be started again with the item sent back and what the receiver
        # gets once it has its Good
        code, out = self.read({"items": [GOOD, SENT_BACK], "questions": []})
        self.assertEqual(code, 0, out)
        prompt = json.loads(json.loads(out)["prompt"])
        self.assertEqual(prompt["sent_back"], [SENT_BACK])
        self.assertEqual(self.read_json(RESULT)["running"]["prompt"], json.loads(out)["prompt"])

    def test_a_reading_with_every_item_good_or_waiting_writes_the_result(self):
        # Given: a reading that finds one item's Good and has the other wait on a question
        # When: the reading is recorded
        # Then: the result holds where the work is, the Good with its lines, and the question with
        # its recommended answer and the item it settles, and the run has returned
        code, out = self.read({"items": [GOOD, WAITS], "questions": [QUESTION]})
        self.assertEqual((code, json.loads(out)), (0, {"returned": RESULT}))
        self.assertEqual(
            self.read_json(RESULT),
            {
                "work": ["README.md"],
                "items": [GOOD],
                "questions": [
                    dict(QUESTION, items=[{"checklist": "checklists/readme.md", "item": "B-1"}])
                ],
                "not_good": [],
            },
        )

    def test_a_result_at_the_top_of_the_repository_is_written(self):
        # Given: a run whose result goes at the top of the repository, in no folder
        # When: a reading with every item Good or waiting is recorded
        # Then: the result is written there
        self.started(dict(CALL, result="result.json"))
        reading = {"items": [GOOD, WAITS], "questions": [QUESTION]}
        code, out = self.turn("read", "result.json", stdin=json.dumps(reading))
        self.assertEqual(code, 0, out)
        self.assertEqual(self.read_json("result.json")["items"], [GOOD])

    def test_a_reading_given_after_the_run_returned_stops(self):
        # Given: a run that has returned
        # When: another reading is given
        # Then: it stops, saying the run has returned and how to start one
        self.read({"items": [GOOD, WAITS], "questions": [QUESTION]})
        code, out = self.read({"items": [GOOD, WAITS], "questions": [QUESTION]})
        self.assertEqual(code, 1)
        self.assertIn("no run is going", out)
        self.assertIn("turn.py start", out)

    def test_a_reading_for_a_result_never_started_stops(self):
        # Given: a result path no run was started for
        # When: a reading is given for it
        # Then: it stops, naming the path
        code, out = self.turn("read", "elsewhere.json", stdin="{}")
        self.assertEqual(code, 1)
        self.assertIn("elsewhere.json", out)


class TestReadingForm(ReadTest):
    def stops(self, reading, *said):
        code, out = self.turn(
            "read", RESULT, stdin=reading if isinstance(reading, str) else json.dumps(reading)
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
            "no checklist",
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
