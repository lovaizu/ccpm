"""A round's end and the rounds after it: an item has its Good where the first user gives one, the
items without it are made again, and an item two rounds leave becomes a question."""

import json
import unittest

from helpers import (
    ANSWER,
    ASKED,
    FOUND,
    FOUND_B1,
    QUESTION,
    RESULT,
    STOPPED_B1,
    STOPPED_F1,
    WAITS,
    ReadTest,
)


class TestRoundEnd(ReadTest):
    """Once the first user's reading ends, an item has its Good where the first user gave one."""

    def test_every_good_found_has_the_learner_start(self):
        # Given: a first user finding every item's Good
        # When: the orchestrator goes on
        # Then: a line says what the first user found and that the learner learns next, with no
        # second round
        out = self.first_read(FOUND, FOUND_B1)
        self.assertTrue(
            str(out["line"]).startswith(
                "turn: turn:first-user found the Good of 2 of 2 items. Next, turn:learner will"
            ),
            out,
        )
        self.assertEqual(self.due(out)["input"]["subagent_type"], "turn:learner")

    def test_an_item_the_first_user_found_no_good_for_is_made_again_as_it_gave_it(self):
        # Given: a first user giving one item's Good and stopping at the other
        # When: the orchestrator goes on
        # Then: a line says what the first user found and that the second round's generator makes
        # the work, which is given the stop as the first user gave it
        out = self.first_read(FOUND)
        self.assertEqual(
            out["line"],
            "turn: turn:first-user found the Good of 1 of 2 items. Next, turn:generator will make"
            " the work to give every item its Good, and run what it gives as the receiver would,"
            " of README.md, for 2 items, round 2.",
        )
        self.due(out)
        self.assertEqual(self.prompt()["sent_back"], [STOPPED_B1])

    def test_a_reading_with_no_good_goes_to_the_next_round_with_every_item(self):
        # Given: a first user finding no item's Good
        # When: the orchestrator goes on
        # Then: the second round's generator is due, given every item as the first user stopped
        out = self.first_read()
        self.assertIn("round 2", out["line"])
        self.assertEqual(self.prompt()["sent_back"], [STOPPED_F1, STOPPED_B1])


class TestRounds(ReadTest):
    """Only the items without Good are made again in the next round, and an item two rounds leave
    without Good becomes a question."""

    def second(self):
        """The first round taken to its end with F-1 Good and B-1 without Good; the move starting
        the second round's generator."""
        return self.due(self.first_read(FOUND))

    def left(self, *stops):
        """Both rounds taken to their end with B-1 without Good, the second's reading giving the
        stops, the question to word told; what is shown."""
        self.second()
        out = self.first_read(FOUND, *stops)
        self.assertEqual(
            out["line"],
            "turn: turn:first-user found the Good of 1 of 2 items. Next, turn:up will word a"
            " question for each item two rounds left without Good, of README.md, for 2 items,"
            " round 2.",
        )
        return self.next()

    def test_the_next_round_starts_its_generator_anew(self):
        # Given: a first round leaving B-1 without Good
        # When: the orchestrator goes on after the line
        # Then: a line says the second round's generator makes the work, and it is started anew,
        # not sent a message
        out = self.first_read(FOUND)
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
        # When: the second round's first user finds both Goods
        # Then: the run returns with both Goods of the second round
        self.second()
        self.assertEqual(self.learnt(self.first_read(FOUND, FOUND_B1)), {"returned": RESULT})
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
        out = self.first_read(FOUND)
        self.assertIn("round 4", out["line"])
        self.due(out)
        self.assertEqual(self.heard(self.first_read(FOUND)), {"left": [STOPPED_B1]})

    def test_each_answer_lets_two_rounds_more_run(self):
        # Given: an item left without Good after the fourth round, once answered after the second
        # When: it is answered again, and the fifth and the sixth round leave it without Good
        # Then: the fifth goes on to the sixth, and the sixth's end shows it for a question
        self.due(self.answered_left())
        self.due(self.first_read(FOUND))
        self.heard(self.first_read(FOUND))
        self.heard(self.next({"items": [WAITS], "questions": [QUESTION]}))
        out = self.answered()
        self.assertIn("round 5", out["line"])
        self.due(out)
        out = self.first_read(FOUND)
        self.assertIn("round 6", out["line"])
        self.due(out)
        self.assertEqual(self.heard(self.first_read(FOUND)), {"left": [STOPPED_B1]})

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

    def test_items_left_too_long_for_one_read_are_shown_page_by_page(self):
        # Given: a run waiting on the question for an item left whose stop runs past two pages
        # When: the orchestrator runs the script with no input, then asks for each page after
        # Then: each page is headed by its number among all and how to see the others, the pages
        # together are the items left, and a page past the last stops
        self.left(dict(STOPPED_B1, lacking="x" * 45000))
        left = self.state()["left"]
        pages = []
        for asked in ((), ("2",), ("3",)):
            code, out = self.turn("next", RESULT, *asked)
            self.assertEqual(code, 0, out)
            head, page = out.split("\n", 1)
            self.assertTrue(head.startswith(f"left, page {len(pages) + 1} of 3: "), head)
            self.assertIn(f"turn.py next {RESULT} <page>", head)
            pages.append(page[:-1])
        self.assertEqual(json.loads("".join(pages)), {"left": left})
        self.assertEqual([len(p) for p in pages[:2]], [20000, 20000])
        for page in ("0", "4", "a"):
            self.assertIn(f"page {page} is not one of 1 to 3", self.turn("next", RESULT, page)[1])

    def test_items_left_of_two_pages_are_shown_page_by_page(self):
        # Given: a run waiting on the question for an item left whose stop runs to two pages
        # When: the orchestrator runs the script with no input
        # Then: the first page is headed by its number of two
        self.left(dict(STOPPED_B1, lacking="x" * 25000))
        out = self.turn("next", RESULT)[1]
        self.assertTrue(out.startswith("left, page 1 of 2: "), out[:80])

    def test_items_left_short_enough_for_one_read_are_printed_as_they_are(self):
        # Given: a run waiting on the question for an item left that fits in one page
        # When: the orchestrator asks for the first page
        # Then: the items left are printed with no head, as with no page asked
        self.left()
        code, out = self.turn("next", RESULT, "1")
        self.assertEqual((code, json.loads(out)), (0, self.next()))

    def test_a_page_asked_while_the_run_waits_on_a_role_stops(self):
        # Given: a run waiting on the generator's reply
        # When: the orchestrator asks for a page
        # Then: it stops, saying to go on with no page
        code, out = self.turn("next", RESULT, "2")
        self.assertEqual(code, 1, out)
        self.assertIn(f"run `turn.py next {RESULT}`", out)


if __name__ == "__main__":
    unittest.main()
