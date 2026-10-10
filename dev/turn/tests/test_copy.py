import os
import shutil
import subprocess
import unittest

import harness


def git(cwd, *args):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args], cwd=cwd,
                   check=True, capture_output=True)


class Copy(unittest.TestCase):
    def setUp(self):
        self.repo = harness.Repo()
        for name in ("app.py", "gone.py", "kept.py"):
            self.repo.write(name, name)
        self.repo.write(".gitignore", "var/\n")
        git(self.repo.work, "add", "-A")
        git(self.repo.work, "commit", "-qm", "app")

    def tearDown(self):
        self.repo.close()

    def test_the_copy_is_what_the_receiver_starts_from_with_the_work_not_yet_committed(self):
        # Given
        self.repo.write("app.py", "changed")
        self.repo.write("docs/SETUP.md", "new")
        self.repo.write("var/app.log", "only here")
        os.remove(os.path.join(self.repo.work, "gone.py"))
        # When
        r = self.repo.script("copy.py")
        # Then
        copy = r.stdout.strip()
        self.addCleanup(shutil.rmtree, os.path.dirname(copy))
        self.assertEqual(open(os.path.join(copy, "app.py")).read(), "changed")
        self.assertEqual(open(os.path.join(copy, "docs", "SETUP.md")).read(), "new")
        self.assertTrue(os.path.isfile(os.path.join(copy, "kept.py")))
        self.assertFalse(os.path.exists(os.path.join(copy, "var")))
        self.assertFalse(os.path.exists(os.path.join(copy, "gone.py")))

    def test_the_copy_is_removed_and_nothing_else_is(self):
        # Given
        copy = self.repo.script("copy.py").stdout.strip()
        # When
        refused = self.repo.script("copy.py", "--remove", self.repo.work)
        removed = self.repo.script("copy.py", "--remove", copy)
        # Then
        self.assertEqual(refused.returncode, 2)
        self.assertTrue(os.path.isdir(self.repo.work))
        self.assertEqual(removed.returncode, 0)
        self.assertFalse(os.path.exists(os.path.dirname(copy)))

    def test_a_wrong_call_is_refused(self):
        # Given / When
        r = self.repo.script("copy.py", "x")
        # Then
        self.assertEqual(r.returncode, 2)
        self.assertIn("usage", r.stderr)


if __name__ == "__main__":
    unittest.main()
