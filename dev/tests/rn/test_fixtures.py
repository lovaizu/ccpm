"""Each trial fixture in the current form passes the form checks, so a trial starts from a state the
rn under test can read."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.join(HERE, "..", "..", "..", "rn")
FIXTURES = os.path.join(HERE, "..", "..", "trials", "rn", "fixtures")
sys.path.insert(0, os.path.join(PLUGIN, "hooks"))
import check  # noqa: E402


class FixturesTest(unittest.TestCase):
    def test_current_form_fixtures_pass_the_form_checks(self):
        seen = 0
        for name in sorted(os.listdir(FIXTURES)):
            tree = os.path.join(FIXTURES, name, "tree")
            for sdir in (os.path.join(tree, ".rn", s) for s in os.listdir(os.path.join(tree, ".rn"))):
                if not open(os.path.join(sdir, "steering.md")).read().startswith("---"):
                    continue
                seen += 1
                with self.subTest(fixture=name):
                    self.assertEqual(check.form_checks(tree, sdir), [])
        self.assertGreater(seen, 0)


if __name__ == "__main__":
    unittest.main()
