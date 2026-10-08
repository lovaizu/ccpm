"""rn's generator is defined so it cannot call another agent, such as a first user."""
import os
import unittest

PLUGIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "rn")


class Agents(unittest.TestCase):
    def front(self, name):
        text = open(os.path.join(PLUGIN, "agents", name)).read()
        return text.split("---")[1]

    def test_generator_cannot_start_an_agent(self):
        # Given the generator's definition
        # When its front matter is read
        front = self.front("generator.md")
        # Then the Agent tool is disallowed
        self.assertRegex(front, r"(?m)^disallowedTools: .*\bAgent\b")


if __name__ == "__main__":
    unittest.main()
