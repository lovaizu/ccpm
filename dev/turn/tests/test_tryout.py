"""Tests for the copy the first user tries the deliverable in, run as turn runs it."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

PLUGIN_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "turn")
ENTRY = os.path.join(PLUGIN_ROOT, "scripts", "tryout.py")


def copies():
    return {n for n in os.listdir(tempfile.gettempdir()) if n.startswith("turn-try-")}


class TryoutTest(unittest.TestCase):

    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp())
        self.repo = os.path.join(self.root, "repo")
        os.makedirs(self.repo)
        self.git("init", "-q")
        self.write("package.json", "{}\n")
        self.git("add", "package.json")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "start")
        self.write("notes.txt", "only in the working repository\n")

    def tearDown(self):
        shutil.rmtree(self.root)

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, check=True)

    def write(self, path, text):
        full = os.path.join(self.repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(text)

    def run_tryout(self, *args, cwd=None):
        return subprocess.run([sys.executable, ENTRY, *args], cwd=cwd or self.repo,
                              capture_output=True, text=True)

    def test_the_copy_is_a_fresh_clone_with_only_the_deliverable_added(self):
        # Given
        self.write("docs/SETUP.md", "# Setup\n")
        # When
        result = self.run_tryout("make", "docs/SETUP.md")
        folder = result.stdout.strip()
        self.addCleanup(shutil.rmtree, folder, True)
        # Then
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(os.path.isfile(os.path.join(folder, "package.json")))
        self.assertTrue(os.path.isfile(os.path.join(folder, "docs", "SETUP.md")))
        self.assertFalse(os.path.exists(os.path.join(folder, "notes.txt")))

    def test_a_deliverable_folder_is_copied_whole(self):
        # Given
        self.write("guide/a.md", "a\n")
        self.write("guide/b/c.md", "c\n")
        # When
        result = self.run_tryout("make", "guide")
        folder = result.stdout.strip()
        self.addCleanup(shutil.rmtree, folder, True)
        # Then
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(os.path.isfile(os.path.join(folder, "guide", "b", "c.md")))

    def test_a_deliverable_not_made_yet_makes_no_copy(self):
        # Given
        before = copies()
        # When
        result = self.run_tryout("make", "SETUP.md")
        # Then
        self.assertEqual((result.returncode, result.stdout.strip()), (1, "deliverable SETUP.md does not exist"))
        self.assertEqual(copies(), before)

    def test_outside_a_git_repository_no_copy_is_made(self):
        # Given
        outside = self.root
        # When
        result = self.run_tryout("make", "SETUP.md", cwd=outside)
        # Then
        self.assertEqual((result.returncode, result.stdout.strip()), (1, "not inside a git repository"))

    def test_drop_deletes_a_copy_it_made(self):
        # Given
        self.write("SETUP.md", "# Setup\n")
        folder = self.run_tryout("make", "SETUP.md").stdout.strip()
        self.assertTrue(folder and os.path.isdir(folder), folder)
        # When
        result = self.run_tryout("drop", folder)
        # Then
        self.assertEqual((result.returncode, result.stdout), (0, ""))
        self.assertFalse(os.path.exists(folder))

    def test_drop_deletes_nothing_it_did_not_make(self):
        # Given
        other = tempfile.mkdtemp(prefix="other-")
        self.addCleanup(shutil.rmtree, other, True)
        # When
        results = [self.run_tryout("drop", path) for path in (other, self.repo)]
        # Then
        for result in results:
            self.assertEqual(result.returncode, 1)
            self.assertIn("nothing deleted", result.stdout)
        self.assertTrue(os.path.isdir(other))
        self.assertTrue(os.path.isdir(self.repo))

    def test_work_makes_the_session_s_empty_folder_that_drop_deletes(self):
        # Given
        made = self.run_tryout("work", "s1")
        folder = made.stdout.strip()
        self.assertEqual(made.returncode, 0, made.stdout + made.stderr)
        self.assertEqual(folder, os.path.join(tempfile.gettempdir(), "turn-try-s1"))
        self.assertEqual(os.listdir(folder), [])
        # When
        result = self.run_tryout("drop", folder)
        # Then
        self.assertEqual((result.returncode, result.stdout), (0, ""))
        self.assertFalse(os.path.exists(folder))

    def test_work_empties_what_a_turn_cut_off_in_the_session_left(self):
        # Given
        folder = self.run_tryout("work", "s2").stdout.strip()
        self.addCleanup(shutil.rmtree, folder, True)
        with open(os.path.join(folder, "turn.json"), "w", encoding="utf-8") as f:
            f.write("{}")
        # When
        again = self.run_tryout("work", "s2").stdout.strip()
        # Then
        self.assertEqual((again, os.listdir(folder)), (folder, []))

    def test_a_call_without_make_or_drop_shows_how_to_call_it(self):
        # Given
        args = ["work"]
        # When
        result = self.run_tryout(*args)
        # Then
        self.assertEqual(result.returncode, 2)
        self.assertIn("tryout.py make <deliverable>", result.stdout)


if __name__ == "__main__":
    unittest.main()
