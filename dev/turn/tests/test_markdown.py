"""How a best practice is made Markdown a person reads: markdown.py writes it beside the JSON, and
its check names a Markdown not as its JSON makes it."""

import json
import os
import tempfile
import unittest

import helpers  # noqa: F401  (puts turn's scripts on the path)
import markdown

G = {"title": "T", "url": "https://x.example/t", "by": "X, 2020", "quote": "y"}
DATA = {
    "standard": {
        "goal": "The reader gets it.",
        "format": {"parts": [{"id": "a", "what": "A.", "parts": [{"id": "b", "what": "B."}]}]},
        "checklist": [{"id": "Q1", "about": "a", "what": "Does it?"}],
    },
    "practice": {
        "methods": [
            {"question": "Q1", "thinking": "Think.", "steps": ["Do."], "grounds": [G]}
        ]
    },
}


class Markdown(unittest.TestCase):
    def test_holds_each_part_question_and_method_under_its_question(self):
        # Given a best practice, When it is made Markdown, Then each item is there in order.
        text = markdown.markdown("kind", DATA)
        expected = ["# kind", "The reader gets it.", "- **a**: A.", "  - **b**: B."]
        expected += ["- **Q1** (a): Does it?", "### Q1: Does it?", "**Thinking**: Think."]
        expected += ["1. Do.", '- [T](https://x.example/t), X, 2020: "y"']
        for line in expected:
            self.assertIn(line, text)
        self.assertLess(text.index("## Standard"), text.index("## Practice"))

    def test_leaves_out_what_a_best_practice_has_none_of(self):
        # Given no format and a method with no steps or grounds, Then neither heading is written.
        data = json.loads(json.dumps(DATA))
        del data["standard"]["format"]
        data["practice"]["methods"][0].update(steps=[], grounds=[])
        text = markdown.markdown("kind", data)
        for absent in ("### Format", "**Steps**", "**Grounds**"):
            self.assertNotIn(absent, text)

    def test_check_fails_until_write_makes_the_markdown(self):
        # Given a JSON with no Markdown, When checked, then written, then checked again.
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "kind.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(DATA, f)
            self.assertEqual(markdown.main(["check", path]), 1)
            self.assertEqual(markdown.main(["write", path]), 0)
            self.assertEqual(markdown.main(["check", path]), 0)

    def test_refuses_an_unknown_command(self):
        self.assertEqual(markdown.main(["print"]), 2)


if __name__ == "__main__":
    unittest.main()
