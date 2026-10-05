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
    def test_given_the_readme_when_its_relative_links_are_followed_then_each_file_exists(self):
        # Given
        links = re.findall(r"\]\(([^)#]+)\)", read("README.md"))
        # When
        relative = [link for link in links if "://" not in link]
        # Then
        self.assertTrue(relative)
        for link in relative:
            self.assertTrue(os.path.exists(os.path.join(PLUGIN_ROOT, link)), link)

    def test_given_the_essentials_files_when_the_readme_is_read_then_each_is_linked(self):
        # Given
        names = os.listdir(ESSENTIALS)
        # When
        readme = read("README.md")
        # Then
        for name in names:
            self.assertIn("(references/essentials/{})".format(name), readme)

    def test_given_the_skills_when_the_readme_is_read_then_its_commands_are_exactly_them(self):
        # Given
        skills = os.listdir(os.path.join(PLUGIN_ROOT, "skills"))
        # When
        readme = read("README.md")
        # Then
        for skill in skills:
            self.assertIn("/writ:{}".format(skill), readme)
            self.assertIn("name: {}\n".format(skill), read("skills", skill, "SKILL.md"))
        self.assertEqual(set(re.findall(r"/writ:(\w+)", readme)), set(skills))


if __name__ == "__main__":
    unittest.main()
