"""The tests of dev/scripts/ci-fix.sh: for each branch named, it has Claude Code mend the failed
runs of Test quality and Nightly not yet handled, at once, on a branch `ci-fix/<branch>-<head>` of
a worktree of its own, from the oldest commit that those pushes started from, and waits to mend a
branch again until its last fix is merged into it. Each test runs one round of the watch in a
repository of its own, with stand-ins for gh, claude, uv, and npm, and a `sleep` that ends the
watch, so that it checks what the script decides and not the tools it runs."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest

from helpers import GIT_ENV, TOP, executable, git_in, ran_in

# gh gives the failed runs of a workflow from runs-<workflow>, and a run's log from log-<run>.
GH = """#!/bin/sh
if [ "$1 $2" = "run list" ]; then
  cat "$GH_DIR/runs-$(echo "$4" | tr ' ' -)" 2>/dev/null
elif [ "$1 $2 $4" = "run view --log" ]; then
  cat "$GH_DIR/log-$3" 2>/dev/null
elif [ "$1 $2 $4" = "run view --log-failed" ]; then
  echo "the failure of $3"
fi
"""
# claude keeps its brief, its arguments, and the folder it ran in, and reports in one line.
CLAUDE = """#!/bin/sh
n=$(ls "$CLAUDE_DIR" | wc -l)
cat > "$CLAUDE_DIR/$n.brief"
printf '%s\\n' "$PWD" "$@" > "$CLAUDE_DIR/$n.args"
echo "fixed the runs"
"""
NOTHING = "#!/bin/sh\n"
# sleep ends the watch after its first round.
SLEEP = "#!/bin/sh\nexit 3\n"


class CiFixTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="ci-fix-")
        self.addCleanup(shutil.rmtree, self.dir)
        self.gh = os.path.join(self.dir, "gh")
        self.claude = os.path.join(self.dir, "claude")
        bin_ = os.path.join(self.dir, "bin")
        for folder in (self.gh, self.claude, bin_):
            os.makedirs(folder)
        tools = {"gh": GH, "claude": CLAUDE, "uv": NOTHING, "npm": NOTHING, "sleep": SLEEP}
        for name, text in tools.items():
            executable(os.path.join(bin_, name), text)
        self.env = dict(os.environ, **GIT_ENV, GH_DIR=self.gh, CLAUDE_DIR=self.claude)
        self.env["PATH"] = bin_ + os.pathsep + self.env["PATH"]
        origin = os.path.join(self.dir, "origin.git")
        self.repo = os.path.join(self.dir, "repo")
        git_in(self.dir, self.env, "init", "-q", "--bare", "-b", "main", origin)
        git_in(self.dir, self.env, "clone", "-q", origin, self.repo)
        os.makedirs(os.path.join(self.repo, "dev", "scripts"))
        for script in ("ci-fix.sh", "ci-fix.md"):
            shutil.copy(
                os.path.join(TOP, "dev", "scripts", script),
                os.path.join(self.repo, "dev", "scripts"),
            )
        git_in(self.repo, self.env, "add", "-A")
        git_in(self.repo, self.env, "commit", "-q", "-m", "the checks")
        self.first = git_in(self.repo, self.env, "rev-parse", "HEAD")
        git_in(self.repo, self.env, "commit", "-q", "--allow-empty", "-m", "a change")
        git_in(self.repo, self.env, "push", "-q", "origin", "HEAD:work")
        self.head = git_in(self.repo, self.env, "rev-parse", "--short=8", "HEAD")

    def failed(self, workflow, run, base=None):
        """gh gives the run as a failed run of the workflow, whose log names the base."""
        with open(os.path.join(self.gh, f"runs-{workflow.replace(' ', '-')}"), "a") as file:
            file.write(f"{run}\n")
        if base:
            with open(os.path.join(self.gh, f"log-{run}"), "w") as file:
                file.write(f"x quality.sh: the lines changed since {base}\n")

    def watch(self, *branches):
        return ran_in(self.repo, self.env, "sh", "dev/scripts/ci-fix.sh", *branches)

    def briefs(self):
        """The run values that each start of claude was given, after its brief."""
        names = sorted(n for n in os.listdir(self.claude) if n.endswith(".brief"))
        values = []
        for name in names:
            with open(os.path.join(self.claude, name)) as file:
                values.append(json.loads(file.read().strip().splitlines()[-1]))
        return values

    def args(self, n=0):
        with open(os.path.join(self.claude, f"{n}.args")) as file:
            return file.read().splitlines()

    def test_no_branch_gives_2_with_its_usage(self):
        done = self.watch()
        self.assertEqual(done.returncode, 2)
        self.assertIn("usage: sh dev/scripts/ci-fix.sh <branch>...", done.stderr)

    def test_a_failed_run_is_mended_on_a_fix_branch_of_the_branchs_head(self):
        # Given: a failed run of Test quality on work, whose push started from the first commit.
        self.failed("Test quality", "11", self.first)
        # When: the watch runs a round.
        done = self.watch("work")
        # Then: claude mends it from the base, on ci-fix/work-<head>, and its report's first line
        # is printed.
        (values,) = self.briefs()
        self.assertEqual(
            (values["runs"], values["branch"], values["fix_branch"], values["base"]),
            ("11", "work", f"ci-fix/work-{self.head}", self.first),
        )
        self.assertIn("ci-fix: runs 11 on work: fixed the runs", done.stdout)

    def test_claude_works_in_a_worktree_of_its_own_that_goes_once_it_ends(self):
        self.failed("Test quality", "11", self.first)
        self.watch("work")
        folder = self.args()[0]
        self.assertEqual(
            os.path.dirname(folder), os.path.join(self.repo, ".claude", "worktrees"), folder
        )
        self.assertFalse(os.path.exists(folder), "the worktree is removed")

    def test_claude_may_push_only_its_own_branch(self):
        self.failed("Test quality", "11", self.first)
        self.watch("work")
        pushes = [a for a in self.args() if a.startswith("Bash(git push")]
        fix = f"ci-fix/work-{self.head}"
        self.assertEqual(
            pushes, [f"Bash(git push origin {fix})", f"Bash(git push -u origin {fix})"]
        )

    def test_a_run_handled_is_not_mended_again(self):
        # Given: a failed run that a round of the watch handled.
        self.failed("Test quality", "11", self.first)
        self.watch("work")
        # When: the watch runs again.
        self.watch("work")
        # Then: claude was started once.
        self.assertEqual(len(self.briefs()), 1)

    def test_runs_failed_together_are_mended_at_once_from_the_oldest_base(self):
        # Given: two failed runs of Test quality, one from the first commit and one from the head.
        head = git_in(self.repo, self.env, "rev-parse", "HEAD")
        self.failed("Test quality", "11", head)
        self.failed("Test quality", "12", self.first)
        # When: the watch runs a round.
        self.watch("work")
        # Then: one start of claude mends both, from the older commit.
        (values,) = self.briefs()
        self.assertEqual((values["runs"], values["base"]), ("11 12", self.first))

    def test_a_nightly_failure_is_mended_with_no_base(self):
        # Given: a failed nightly run beside a failed run of Test quality.
        self.failed("Test quality", "11", self.first)
        self.failed("Nightly", "21")
        # When: the watch runs a round.
        self.watch("work")
        # Then: the fix covers both, with no base, as a nightly run checks the whole.
        (values,) = self.briefs()
        self.assertEqual((values["runs"], values["base"]), ("11 21", ""))

    def test_a_branch_whose_last_fix_is_not_merged_waits(self):
        # Given: a fix of work pushed and not merged into it, and a failed run.
        git_in(self.repo, self.env, "commit", "-q", "--allow-empty", "-m", "a fix")
        git_in(self.repo, self.env, "push", "-q", "origin", "HEAD:refs/heads/ci-fix/work-0000000")
        self.failed("Test quality", "11", self.first)
        # When: the watch runs a round.
        self.watch("work")
        # Then: claude isn't started.
        self.assertEqual(self.briefs(), [])

    def test_a_branch_whose_last_fix_is_merged_is_mended_again(self):
        # Given: a fix of work pushed and merged into it, and a failed run.
        git_in(self.repo, self.env, "commit", "-q", "--allow-empty", "-m", "a fix")
        git_in(
            self.repo,
            self.env,
            "push",
            "-q",
            "origin",
            "HEAD:refs/heads/ci-fix/work-0000000",
            "HEAD:work",
        )
        self.failed("Test quality", "11", self.first)
        # When: the watch runs a round.
        self.watch("work")
        # Then: claude mends the run.
        self.assertEqual([v["runs"] for v in self.briefs()], ["11"])


if __name__ == "__main__":
    unittest.main()
