"""How practices.py checks a best practice's form and makes the Markdown a person reads: the check
names each fault and each Markdown not as its JSON makes it, and write puts the Markdown beside
the JSON."""

import copy
import json
import os
import tempfile
import unittest

import helpers  # noqa: F401  (puts turn's scripts on the path)
import practices

G = {"title": "T", "url": "https://x.example/t", "by": "X, 2020", "quote": "y"}
DATA = {
    "standard": {
        "goal": "The reader gets it.",
        "parts": [{"id": "a", "what": "A.", "parts": [{"id": "b", "what": "B."}]}],
        "checklist": [
            {"id": "Q1", "about": "a", "what": "Does it?"},
            {"id": "Q2", "about": "b, the whole", "what": "After Q1, does all?"},
        ],
    },
    "practice": {
        "methods": [
            {"question": "Q1", "thinking": "Think.", "steps": ["Do."], "grounds": [G]},
            {"question": "Q2", "thinking": "Then.", "steps": [], "grounds": []},
        ]
    },
}


def changed(change):
    data = copy.deepcopy(DATA)
    change(data)
    return practices.faults(data)


class Faults(unittest.TestCase):
    def test_a_sound_best_practice_has_none(self):
        self.assertEqual(practices.faults(DATA), [])

    def test_questions_out_of_number_order(self):
        def swap(d):
            d["standard"]["checklist"].reverse()
            d["practice"]["methods"].reverse()

        self.assertIn("questions are Q2, Q1, not numbered in order from Q1", changed(swap))

    def test_methods_not_in_the_questions_order(self):
        def swap(d):
            d["practice"]["methods"].reverse()

        expected = "methods meet Q2, Q1, not each question once in its order"
        self.assertEqual(changed(swap), [expected])

    def test_a_question_with_no_method(self):
        def drop(d):
            d["practice"]["methods"].pop()

        self.assertEqual(changed(drop), ["methods meet Q1, not each question once in its order"])

    def test_about_a_part_that_is_not_there(self):
        def wrong(d):
            d["standard"]["checklist"][0]["about"] = "c"

        self.assertEqual(changed(wrong), ["Q1 is about c, which is no part"])

    def test_a_part_named_twice(self):
        def twice(d):
            d["standard"]["parts"].append({"id": "a", "what": "Again."})

        self.assertEqual(changed(twice), ["part a is named more than once"])

    def test_a_ground_missing_a_field_or_with_no_https_link(self):
        def missing(d):
            d["practice"]["methods"][0]["grounds"] = [dict(G, title=""), dict(G, url="x.example")]

        self.assertEqual(
            changed(missing),
            ["Q1 ground 1 has no title", "Q1 ground 2 links no https page"],
        )

    def test_a_question_named_in_the_text_that_is_not_there(self):
        def name(d):
            d["practice"]["methods"][1]["thinking"] = "As Q3 says."

        self.assertEqual(changed(name), ["Q3 is named, but there is no such question"])

    def test_a_ground_naming_a_question_is_its_source_s_words(self):
        def quote(d):
            d["practice"]["methods"][0]["grounds"] = [dict(G, quote="see Q9")]

        self.assertEqual(changed(quote), [])


class Markdown(unittest.TestCase):
    def test_holds_each_part_question_and_method_under_its_question(self):
        text = practices.markdown("kind", DATA)
        expected = ["# kind", "The reader gets it.", "### Parts", "- **a**: A.", "  - **b**: B."]
        expected += ["- **Q1** (a): Does it?", "### Q1: Does it?", "**Thinking**: Think."]
        expected += ["1. Do.", '- [T](https://x.example/t), X, 2020: "y"']
        for line in expected:
            self.assertIn(line, text)
        self.assertLess(text.index("## Standard"), text.index("## Practice"))

    def test_leaves_out_what_a_best_practice_has_none_of(self):
        data = copy.deepcopy(DATA)
        del data["standard"]["parts"]
        text = practices.markdown("kind", data)
        self.assertNotIn("### Parts", text)
        self.assertEqual(text.count("**Steps**"), 1)
        self.assertEqual(text.count("**Grounds**"), 1)


class Main(unittest.TestCase):
    def test_check_fails_until_write_makes_the_markdown(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "kind.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(DATA, f)
            self.assertEqual(practices.main(["check", path]), 1)
            self.assertEqual(practices.main(["write", path]), 0)
            self.assertEqual(practices.main(["check", path]), 0)

    def test_check_fails_on_a_fault_of_the_form(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "kind.json")
            data = copy.deepcopy(DATA)
            data["practice"]["methods"].pop()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            practices.main(["write", path])
            self.assertEqual(practices.main(["check", path]), 1)

    def test_refuses_an_unknown_command(self):
        self.assertEqual(practices.main(["print"]), 2)


if __name__ == "__main__":
    unittest.main()
