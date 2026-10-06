"""Each trial fixture in the current form passes the form checks, so a trial starts from a state the
rn under test can read."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.join(HERE, "..", "..", "..", "rn")
FIXTURES = os.path.join(HERE, "..", "trials", "fixtures")
sys.path.insert(0, os.path.join(PLUGIN, "hooks"))
import form  # noqa: E402


class FixturesTest(unittest.TestCase):
    def test_current_form_fixtures_pass_the_form_checks(self):
        # Given every trial fixture whose steering.md is in the current form
        current = []
        for name in sorted(os.listdir(FIXTURES)):
            tree = os.path.join(FIXTURES, name, "tree")
            for sdir in (os.path.join(tree, ".rn", s) for s in os.listdir(os.path.join(tree, ".rn"))):
                if open(os.path.join(sdir, "steering.md")).read().startswith("---"):
                    current.append((name, tree, sdir))
        self.assertGreater(len(current), 0)
        for name, tree, sdir in current:
            with self.subTest(fixture=name):
                # When the form checks run on it
                problems = form.check(tree, sdir)
                # Then they find nothing
                self.assertEqual(problems, [])

if __name__ == "__main__":
    unittest.main()
