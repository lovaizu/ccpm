"""The tests of dev/scripts/pre-push.sh: it checks the commits each push sends, given on its
standard input as git gives them, and stops the push where the check fails. Each test runs the
script in a repository of its own, with stand-ins for check.sh, changed.sh, uv and npm, so that it
checks what the script decides and not the checks it runs."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest

from helpers import GIT_ENV, TOP, without

ZERO = "0" * 40

# The stand-in for check.sh fails where the commit checked holds a file named bad, and writes
# where it ran and what it got.
CHECK = """#!/bin/sh
echo "$PWD $*" >> "$LOG/check"
[ ! -e bad ]
"""
# The stand-in for changed.sh names the plugins in the file plugins of the commit it gets.
CHANGED = """#!/bin/sh
echo "$*" >> "$LOG/changed"
git show "$2:plugins" 2>/dev/null || true
"""
# The stand-in for uv runs, for `uv run --no-sync`, the command after it, and does nothing else.
UV = """#!/bin/sh
if [ "$1" = run ]; then shift 2; exec "$@"; fi
"""
NPM = "#!/bin/sh\n"


class PrePushTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="pre-push-")
        self.addCleanup(shutil.rmtree, self.dir)
        self.repo = os.path.join(self.dir, "repo")
        self.log = os.path.join(self.dir, "log")
        self.bin = os.path.join(self.dir, "bin")
        os.makedirs(self.log)
        os.makedirs(self.bin)
        self.env = dict(os.environ, **GIT_ENV, LOG=self.log)
        self.env["PATH"] = self.bin + os.pathsep + self.env["PATH"]
        for name, text in (("uv", UV), ("npm", NPM)):
            self.write(os.path.join(self.bin, name), text)
        self.git("init", "-q", "-b", "main", self.repo, cwd=self.dir)
        scripts = os.path.join(self.repo, "dev", "scripts")
        os.makedirs(scripts)
        shutil.copy(os.path.join(TOP, "dev", "scripts", "pre-push.sh"), scripts)
        self.write(os.path.join(scripts, "check.sh"), CHECK)
        self.write(os.path.join(scripts, "changed.sh"), CHANGED)
        self.main = self.commit("plugins", "rn\n")
        self.git("update-ref", "refs/remotes/origin/main", self.main)

    def write(self, path, text):
        with open(path, "w") as file:
            file.write(text)
        os.chmod(path, 0o755)

    def git(self, *args, cwd=None):
        return subprocess.run(
            ["git", *args],
            cwd=cwd or self.repo,
            env=self.env,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def commit(self, name, text):
        self.write(os.path.join(self.repo, name), text)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", name)
        return self.git("rev-parse", "HEAD")

    def push(self, *lines, env=None):
        given = "".join(f"refs/heads/b {local} refs/heads/b {remote}\n" for local, remote in lines)
        return subprocess.run(
            ["sh", "dev/scripts/pre-push.sh"],
            cwd=self.repo,
            env=env or self.env,
            input=given,
            capture_output=True,
            text=True,
            check=False,
        )

    def read(self, name):
        path = os.path.join(self.log, name)
        if not os.path.exists(path):
            return []
        with open(path) as file:
            return file.read().splitlines()

    def worktrees(self):
        return self.git("worktree", "list").splitlines()

    def test_a_push_whose_commits_fail_the_check_stops(self):
        # Given: a commit that the check fails.
        local = self.commit("bad", "")
        # When: git pushes it.
        done = self.push((local, self.main))
        # Then: the push stops, and no worktree stays.
        self.assertNotEqual(done.returncode, 0)
        self.assertEqual(len(self.worktrees()), 1)

    def test_a_push_whose_commits_pass_the_check_goes_on(self):
        # Given: a commit that the check passes.
        local = self.commit("good", "")
        # When: git pushes it.
        done = self.push((local, self.main))
        # Then: the push goes on, the check got --reached and the plugins changed.sh named, and no
        # worktree stays.
        self.assertEqual(done.returncode, 0, done.stderr)
        [checked] = self.read("check")
        self.assertTrue(checked.endswith(" --reached rn"), checked)
        self.assertEqual(len(self.worktrees()), 1)

    def test_the_check_reads_the_commits_pushed_not_the_working_tree(self):
        # Given: a commit that the check passes, and a file the check fails beside it, uncommitted.
        local = self.commit("good", "")
        self.write(os.path.join(self.repo, "bad"), "")
        # When: git pushes the commit.
        done = self.push((local, self.main))
        # Then: the push goes on, as the check ran in a folder other than the working tree.
        self.assertEqual(done.returncode, 0, done.stderr)
        [checked] = self.read("check")
        self.assertNotEqual(checked.split()[0], self.repo)

    def test_a_branch_on_the_remote_is_counted_from_where_the_remote_has_it(self):
        # Given: two commits, the remote having the first.
        first = self.commit("one", "")
        second = self.commit("two", "")
        # When: git pushes the second.
        self.push((second, first))
        # Then: changed.sh got the change from the first to the second.
        self.assertEqual(self.read("changed"), [f"{first} {second}"])

    def test_a_branch_new_on_the_remote_is_counted_from_where_it_left_main(self):
        # Given: a commit after main.
        local = self.commit("one", "")
        # When: git pushes it as a branch new to the remote.
        self.push((local, ZERO))
        # Then: changed.sh got the change from main to the commit.
        self.assertEqual(self.read("changed"), [f"{self.main} {local}"])

    def test_a_branch_deleted_is_not_checked(self):
        # When: a push deletes a branch.
        done = self.push((ZERO, self.main))
        # Then: the push goes on, with nothing checked.
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(self.read("changed"), [])
        self.assertEqual(self.read("check"), [])

    def test_a_push_that_changes_no_plugin_is_not_checked(self):
        # Given: a commit with a file the check fails, for which changed.sh names no plugin.
        self.commit("bad", "")
        local = self.commit("plugins", "")
        # When: git pushes it.
        done = self.push((local, self.main))
        # Then: the push goes on, with nothing checked.
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(self.read("check"), [])

    def test_each_branch_of_a_push_is_checked(self):
        # Given: a commit that the check passes and one that it fails.
        good = self.commit("good", "")
        bad = self.commit("bad", "")
        # When: git pushes both at once, the good one first.
        done = self.push((good, self.main), (bad, self.main))
        # Then: the push stops, as the second fails.
        self.assertNotEqual(done.returncode, 0)
        self.assertEqual(len(self.read("check")), 2)

    def test_a_tool_missing_stops_the_push_and_says_which(self):
        local = self.commit("good", "")
        for tool in ("uv", "npm"):
            with self.subTest(tool=tool):
                # Given: every command on PATH but the tool.
                env = dict(
                    self.env, PATH=without(self.env["PATH"], tool, os.path.join(self.dir, tool))
                )
                # When: git pushes a commit.
                done = self.push((local, self.main), env=env)
                # Then: the push stops before it checks anything, and says the tool isn't on
                # PATH.
                self.assertNotEqual(done.returncode, 0)
                self.assertIn(f"{tool} isn't on PATH", done.stderr)
                self.assertEqual(self.read("changed"), [])


if __name__ == "__main__":
    unittest.main()
