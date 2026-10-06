"""rn's agents are defined so the first user and the generator keep to their roles."""
import os
import unittest

from harness import PLUGIN


class Agents(unittest.TestCase):
    def front(self, name):
        text = open(os.path.join(PLUGIN, "agents", name)).read()
        return text.split("---")[1]

    def test_first_user_starts_without_claude_md(self):
        # Given the first user's definition
        # When its front matter is read
        front = self.front("first-user.md")
        # Then it skips CLAUDE.md
        self.assertRegex(front, r"(?m)^omitClaudeMd: true$")

    def test_generator_cannot_start_an_agent(self):
        # Given the generator's definition
        # When its front matter is read
        front = self.front("generator.md")
        # Then the Agent tool is disallowed
        self.assertRegex(front, r"(?m)^disallowedTools: .*\bAgent\b")


if __name__ == "__main__":
    unittest.main()
