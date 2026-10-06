"""The README's links reach their files, and the names it teaches are the ones pith uses."""

import os
import re
import unittest

PLUGIN_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "pith")


def read(*parts):
    with open(os.path.join(PLUGIN_ROOT, *parts), encoding="utf-8") as handle:
        return handle.read()


class ReadmeTest(unittest.TestCase):
    def test_every_relative_link_reaches_a_file(self):
        # Given
        links = re.findall(r"\]\(([^)#]+)\)", read("README.md"))
        # When
        relative = [link for link in links if "://" not in link]
        # Then
        self.assertTrue(relative)
        for link in relative:
            self.assertTrue(os.path.exists(os.path.join(PLUGIN_ROOT, link)), link)

    def test_the_commands_taught_are_exactly_the_skills(self):
        # Given
        skills = [name for name in os.listdir(os.path.join(PLUGIN_ROOT, "skills"))
                  if "user-invocable: false" not in read("skills", name, "SKILL.md")]
        # When
        readme = read("README.md")
        # Then
        for skill in skills:
            self.assertIn("/pith:{}".format(skill), readme)
            self.assertIn("name: {}\n".format(skill), read("skills", skill, "SKILL.md"))
        self.assertEqual(set(re.findall(r"/pith:(\w+)", readme)), set(skills))

    def test_every_essentials_file_is_named(self):
        # Given
        names = os.listdir(os.path.join(PLUGIN_ROOT, "references", "essentials"))
        # When
        readme = read("README.md")
        # Then
        for name in names:
            self.assertIn(name, readme)


if __name__ == "__main__":
    unittest.main()
