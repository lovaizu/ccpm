"""domain/records.py, a round's records checked before their role gives its result: the Making
record and an evaluator's Answers."""

from __future__ import annotations

import os
import time

import helpers
from helpers import RUN, records, runs, starts

from unit.domain.test_starts import answered, good, made

CONTENT = os.path.join(RUN, "turns", "01-readme-md", "01")
READING = os.path.join(RUN, "turns", "01-readme-md-reading", "01")
GROUP = ["Q1", "Q2", "Q3", "Q4", "Q6"]


class Base(helpers.RunTest):
    def setUp(self) -> None:
        super().setUp()
        self.lays(helpers.walkthrough())
        os.makedirs(CONTENT)

    def stopped(self, path):
        with self.assertRaises(starts.Stop) as stop:
            records.record(path)
        return str(stop.exception)


class Made(Base):
    def test_a_record_that_holds_gives_made_or_open(self):
        path = os.path.join(CONTENT, runs.MADE)
        self.write_json(path, made())
        self.assertEqual(
            records.record(path),
            "rn: the Making record holds. Give `made` by its command, and end with this message:"
            f" {path} holds.",
        )
        self.write_json(
            path, made(open_=[{"intent": "Q6", "about": "the list", "what": "a count?"}])
        )
        self.assertIn("Give `open`", records.record(path))

    def test_a_file_not_made_an_intent_of_no_kind_or_no_try_after_it(self):
        path = os.path.join(CONTENT, runs.MADE)
        record = {
            **made(made=["README.md", "gone.md"], commands=["tidy --dry-run"]),
            "decided": [{"intent": "Q99", "about": "a", "decided": "d", "grounds": "g"}],
        }
        self.write_json(path, record)
        self.assertEqual(
            self.stopped(path),
            "gone.md, which it names as made, isn't there\nQ99 is no intent of the best practice\n"
            f"no try record follows it: run throwaway.py {RUN}",
        )
        self.write(os.path.join(CONTENT, runs.TRY), "old")
        later = time.time() + 10
        os.utime(path, (later, later))
        self.assertIn("no try record follows it", self.stopped(path))
        os.utime(os.path.join(CONTENT, runs.TRY), (later + 1, later + 1))
        self.assertNotIn("no try record", self.stopped(path))

    def test_a_record_out_of_form(self):
        path = os.path.join(CONTENT, runs.MADE)
        self.write_json(path, {"made": []})
        with self.assertRaises(helpers.files.Unreadable):
            records.record(path)


class Judged(Base):
    def setUp(self) -> None:
        super().setUp()
        self.write_json(os.path.join(CONTENT, runs.MADE), made())
        self.write(os.path.join(CONTENT, runs.TRY), "$ tidy --dry-run\na.jpg -> Images\n")
        self.path = os.path.join(CONTENT, "evaluator-G1.json")

    def test_answers_that_hold_give_good_more_or_open(self):
        self.write_json(self.path, answered(GROUP))
        self.assertIn("Give `good`", records.record(self.path))
        self.write_json(self.path, answered(GROUP, lacks=["Q2"]))
        self.assertIn("Give `more`", records.record(self.path))
        self.write_json(self.path, answered(GROUP, open_=["Q3"]))
        self.assertIn("Give `open`", records.record(self.path))

    def test_a_line_quoted_from_the_try_record_or_an_input_wrapped_otherwise(self):
        self.write_json(os.path.join(CONTENT, runs.MADE), made(made=["README.md", "gone.md"]))
        data = answered(GROUP)
        data["met"][0]["lines"] = ["a.jpg  ->\n Images", "Someone sorts"]
        self.write_json(self.path, data)
        self.assertIn("Give `good`", records.record(self.path))

    def test_answers_twice_outside_the_group_missing_or_quoting_what_isnt_there(self):
        data = answered(["Q1", "Q1", "Q5"], open_=["Q7"])
        data["met"][0]["lines"] = ["nowhere"]
        self.write_json(self.path, data)
        self.assertEqual(
            self.stopped(self.path),
            "Q1 is answered more than once\nQ5 is no intent of G1\nQ7 is no intent of G1\n"
            "Q2 has no answer\nQ3 has no answer\nQ4 has no answer\nQ6 has no answer\n"
            "Q1 quotes a line that stands in none of what you read: nowhere",
        )

    def test_a_group_the_best_practice_hasnt(self):
        path = os.path.join(CONTENT, "evaluator-G9.json")
        self.write_json(path, answered([]))
        self.assertEqual(self.stopped(path), "the best practice has no group G9")


class Where(Base):
    def test_a_record_outside_the_round_of_the_turn_at_hand(self):
        self.write_json(os.path.join(CONTENT, runs.MADE), made())
        os.makedirs(os.path.join(RUN, "turns", "01-readme-md", "02"))
        self.assertIn(
            "lies in no round of the turn at hand", self.stopped(os.path.join(CONTENT, runs.MADE))
        )
        self.assertIn(
            "is neither generator.json nor",
            self.stopped(os.path.join(RUN, "turns", "01-readme-md", "02", "x.json")),
        )
        self.assertIn("lies in no round", self.stopped(os.path.join(READING, runs.MADE)))
        self.lays(good(helpers.walkthrough()))
        self.assertIn("lies in no round", self.stopped(os.path.join(CONTENT, runs.MADE)))
        self.lays({"goal": helpers.walkthrough()["goal"], "deliverables": []})
        self.assertIn("lies in no round", self.stopped(os.path.join(CONTENT, runs.MADE)))
        empty = os.path.join(RUN, "turns", "03-readme-md", "01")
        self.lays(helpers.walkthrough())
        self.assertIn("lies in no round", self.stopped(os.path.join(empty, runs.MADE)))
