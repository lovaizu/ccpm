"""pith checks a plugin by the same questions the repository's plugin rules hold, word for word."""

import os
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")


def questions(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        text = handle.read()
    first = next(line for line in text.splitlines() if line.startswith("- ") and line.endswith("?"))
    return text[text.index(first):].split("\n## ")[0].strip()


class PluginEssentialsTest(unittest.TestCase):
    def test_pith_plugin_essentials_are_the_rules_questions_word_for_word(self):
        # Given
        rules = questions(".claude/rules/plugin.md")
        # When
        pith = questions("pith/references/essentials/plugin.md")
        # Then
        self.assertEqual(rules, pith)


if __name__ == "__main__":
    unittest.main()
