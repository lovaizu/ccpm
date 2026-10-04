"""The README's links reach their files, and the names it teaches are the ones writ uses."""

import os
import re
import unittest

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESSENTIALS = os.path.join(PLUGIN_ROOT, "references", "essentials")


def read(*parts):
    with open(os.path.join(PLUGIN_ROOT, *parts), encoding="utf-8") as handle:
        return handle.read()


class ReadmeTest(unittest.TestCase):
    def test_every_relative_link_exists(self):
        links = re.findall(r"\]\(([^)#]+)\)", read("README.md"))
        relative = [link for link in links if "://" not in link]
        self.assertTrue(relative)
        for link in relative:
            self.assertTrue(os.path.exists(os.path.join(PLUGIN_ROOT, link)), link)

    def test_every_essentials_file_is_linked(self):
        readme = read("README.md")
        for name in os.listdir(ESSENTIALS):
            self.assertIn("(references/essentials/{})".format(name), readme)

    def test_commands_match_the_skills(self):
        readme = read("README.md")
        for skill in os.listdir(os.path.join(PLUGIN_ROOT, "skills")):
            self.assertIn("/writ:{}".format(skill), readme)
            self.assertIn("name: {}\n".format(skill), read("skills", skill, "SKILL.md"))
        self.assertEqual(set(re.findall(r"/writ:(\w+)", readme)),
                         set(os.listdir(os.path.join(PLUGIN_ROOT, "skills"))))


if __name__ == "__main__":
    unittest.main()
