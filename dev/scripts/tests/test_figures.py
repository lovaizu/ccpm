"""The tests of dev/scripts/figures.py: every figure, its Japanese copy in .review/ja included,
takes its whole look from dev/images/figures.css, and check fails on a figure that looks any other
way."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from helpers import GIT_ENV, TOP, ran_in

SCRIPT = os.path.join(TOP, "dev", "scripts", "figures.py")
STYLE = "svg { font-family: sans-serif; }\n.box { fill: #f6f8fa; }\n"
FIGURE = (
    '<svg xmlns="http://www.w3.org/2000/svg">\n  <style>\n    .old { fill: #000000; }\n  </style>\n'
    '  <rect class="box"/>\n</svg>\n'
)


class FiguresTest(unittest.TestCase):
    def setUp(self):
        self.repo = tempfile.mkdtemp(prefix="figures-")
        self.addCleanup(shutil.rmtree, self.repo)
        self.env = dict(os.environ, **GIT_ENV)
        subprocess.run(["git", "init", "-q", self.repo], env=self.env, check=True)
        self.put("dev/images/figures.css", STYLE)

    def put(self, path, text, held=True):
        full = os.path.join(self.repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as file:
            file.write(text)
        if held:
            subprocess.run(["git", "add", path], cwd=self.repo, env=self.env, check=True)

    def read(self, path):
        with open(os.path.join(self.repo, path), encoding="utf-8") as file:
            return file.read()

    def figures(self, command):
        return ran_in(self.repo, self.env, sys.executable, SCRIPT, command)

    def test_write_gives_each_figure_the_style_and_check_then_passes(self):
        self.put("a.svg", FIGURE)
        self.assertEqual(self.figures("check").returncode, 1)
        self.assertEqual(self.figures("write").returncode, 0)
        self.assertIn("    .box { fill: #f6f8fa; }\n", self.read("a.svg"))
        self.assertEqual(self.figures("check").returncode, 0)

    def test_check_fails_on_a_figure_that_sets_its_own_font_or_color(self):
        for attribute in ('font-family="serif"', 'fill="#000000"', 'style="stroke: red"'):
            with self.subTest(attribute=attribute):
                self.put("a.svg", FIGURE.replace('class="box"', f'class="box" {attribute}'))
                self.figures("write")
                result = self.figures("check")
                self.assertEqual(result.returncode, 1)
                self.assertIn("a.svg:6: sets its own", result.stderr)
                self.assertIn(attribute.split("=")[0], result.stderr)

    def test_write_and_check_reach_a_japanese_copy_that_git_does_not_hold(self):
        self.put("a.svg", FIGURE)
        self.put(".review/ja/a.svg", FIGURE, held=False)
        self.figures("write")
        self.assertIn(".box { fill: #f6f8fa; }", self.read(".review/ja/a.svg"))
        own = FIGURE.replace('class="box"', 'class="box" fill="red"')
        self.put(".review/ja/a.svg", own, held=False)
        result = self.figures("check")
        self.assertEqual(result.returncode, 1)
        self.assertIn(".review/ja/a.svg:5: sets its own fill", result.stderr)

    def test_check_fails_on_a_figure_with_no_style_to_hold_the_copy(self):
        # Given: a figure with no <style>.
        self.put(
            "a.svg", '<svg xmlns="http://www.w3.org/2000/svg">\n  <rect class="box"/>\n</svg>\n'
        )
        # When: the check runs.
        result = self.figures("check")
        # Then: it fails, and names the figure and the file whose copy it can't hold.
        self.assertEqual(result.returncode, 1)
        self.assertIn("a.svg: no <style> to hold dev/images/figures.css", result.stderr)

    def test_a_command_it_does_not_take_gives_2_with_its_usage(self):
        result = self.figures("fix")
        self.assertEqual((result.returncode, result.stderr), (2, "usage: figures.py write|check\n"))


if __name__ == "__main__":
    unittest.main()
