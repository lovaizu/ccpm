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
        # Given: a repository with a committed file, a file not committed, and a deliverable made in a subfolder
        self.write("docs/SETUP.md", "# Setup\n")
        # When: the copy for the first user is made
        result = self.run_tryout("make", "docs/SETUP.md")
        folder = result.stdout.strip()
        self.addCleanup(shutil.rmtree, folder, True)
        # Then: the copy holds the committed file and the deliverable, and not the file left uncommitted
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(os.path.isfile(os.path.join(folder, "package.json")))
        self.assertTrue(os.path.isfile(os.path.join(folder, "docs", "SETUP.md")))
        self.assertFalse(os.path.exists(os.path.join(folder, "notes.txt")))

    def test_a_deliverable_folder_is_copied_whole(self):
        # Given: a deliverable that is a folder with a folder inside it
        self.write("guide/a.md", "a\n")
        self.write("guide/b/c.md", "c\n")
        # When: the copy for the first user is made
        result = self.run_tryout("make", "guide")
        folder = result.stdout.strip()
        self.addCleanup(shutil.rmtree, folder, True)
        # Then: the copy holds the file in the inner folder
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(os.path.isfile(os.path.join(folder, "guide", "b", "c.md")))

    def test_a_deliverable_not_made_yet_makes_no_copy(self):
        # Given: a deliverable never made
        before = copies()
        # When: the copy for the first user is made
        result = self.run_tryout("make", "SETUP.md")
        # Then: it fails, says the deliverable does not exist, and no copy is made
        self.assertEqual((result.returncode, result.stdout.strip()), (1, "deliverable SETUP.md does not exist"))
        self.assertEqual(copies(), before)

    def test_outside_a_git_repository_no_copy_is_made(self):
        # Given: a folder that is not in a git repository
        outside = self.root
        # When: the copy for the first user is made from there
        result = self.run_tryout("make", "SETUP.md", cwd=outside)
        # Then: it fails and says it is not inside a git repository
        self.assertEqual((result.returncode, result.stdout.strip()), (1, "not inside a git repository"))

    def test_drop_deletes_a_copy_it_made(self):
        # Given: a copy made for the first user
        self.write("SETUP.md", "# Setup\n")
        folder = self.run_tryout("make", "SETUP.md").stdout.strip()
        self.assertTrue(folder and os.path.isdir(folder), folder)
        # When: it is deleted
        result = self.run_tryout("drop", folder)
        # Then: it prints nothing and the copy is gone
        self.assertEqual((result.returncode, result.stdout), (0, ""))
        self.assertFalse(os.path.exists(folder))

    def test_drop_deletes_nothing_it_did_not_make(self):
        # Given: a temporary folder not made by turn, and the repository itself
        other = tempfile.mkdtemp(prefix="other-")
        self.addCleanup(shutil.rmtree, other, True)
        # When: each is deleted
        results = [self.run_tryout("drop", path) for path in (other, self.repo)]
        # Then: each fails, says nothing was deleted, and both folders are still there
        for result in results:
            self.assertEqual(result.returncode, 1)
            self.assertIn("nothing deleted", result.stdout)
        self.assertTrue(os.path.isdir(other))
        self.assertTrue(os.path.isdir(self.repo))

    def test_work_makes_the_session_s_empty_folder_that_drop_deletes(self):
        # Given: an empty work folder made and named for a session
        made = self.run_tryout("work", "s1")
        folder = made.stdout.strip()
        self.assertEqual(made.returncode, 0, made.stdout + made.stderr)
        self.assertEqual(folder, os.path.join(tempfile.gettempdir(), "turn-try-s1"))
        self.assertEqual(os.listdir(folder), [])
        # When: it is deleted
        result = self.run_tryout("drop", folder)
        # Then: it prints nothing and the work folder is gone
        self.assertEqual((result.returncode, result.stdout), (0, ""))
        self.assertFalse(os.path.exists(folder))

    def test_work_empties_what_a_turn_cut_off_in_the_session_left(self):
        # Given: a session's work folder that a cut-off turn left a file in
        folder = self.run_tryout("work", "s2").stdout.strip()
        self.addCleanup(shutil.rmtree, folder, True)
        with open(os.path.join(folder, "turn.json"), "w", encoding="utf-8") as f:
            f.write("{}")
        # When: the work folder is made again for the same session
        again = self.run_tryout("work", "s2").stdout.strip()
        # Then: it is the same folder, now empty
        self.assertEqual((again, os.listdir(folder)), (folder, []))

    def test_a_call_without_make_or_drop_shows_how_to_call_it(self):
        # Given: a call to make a work folder with no session
        args = ["work"]
        # When: it is made
        result = self.run_tryout(*args)
        # Then: it fails and shows how to call it
        self.assertEqual(result.returncode, 2)
        self.assertIn("tryout.py make <deliverable>", result.stdout)


if __name__ == "__main__":
    unittest.main()
