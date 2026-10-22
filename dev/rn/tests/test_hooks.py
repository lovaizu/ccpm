"""The tests of rn's hooks: each check stops what rn's design and the decisions for the hooks say it
must, saying what to do instead and why, and lets through everything else. Each test hands the
PreToolUse entry an event in the shape Claude Code hands it, for a tool call in a git repository of
its own, made in a temporary folder, standing for the user's repository."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import re
import runpy
import subprocess
import sys
import unittest
from unittest import mock

PLUGIN = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "rn")
)
HOOKS = os.path.join(PLUGIN, "hooks")
# hooks.json puts rn's scripts on PYTHONPATH, and Python puts the entry's own folder first.
sys.path[:0] = [HOOKS, os.path.join(PLUGIN, "scripts")]
# What every plugin's tests stand on.
sys.path.insert(0, os.path.join(PLUGIN, "..", "dev", "lane"))

import events
import helpers
import hook
import testing
from checks import default_branch

# The session's folder, made on the day rn's tests take as today, and another of an older session.
FOLDER = ".rn/20261020-add-login"
OLD = ".rn/20261001-old"
# Why each stop of the guard of the session's own branch is there.
WHY = (
    "rn keeps every change on the session's own branch, so that it reaches main only when the user"
    " merges the pull request"
)
# The stop of a commit, and of a push, while the default branch is checked out.
ON_MAIN = (
    "rn: `git {}` runs on main, the default branch, which is checked out; switch to the session's"
    " branch with `git switch <branch>`, or make one with `git switch -c <slug>`, and run it there: "
    + WHY
    + "\n"
)
# The stop of a push to the default branch from the session's branch.
TO_MAIN = (
    "rn: `git push` sends to main, the default branch; push the session's branch to its own name"
    " instead, as `git push origin {}`: " + WHY + "\n"
)
# The command rn's /rn:up skill runs to keep the session's folder.
KEEP = f"git add {FOLDER}\ngit commit -F - <<'EOF'\nKeep the plan\nEOF\ngit push"


class HookTest(helpers.MainAndWork):
    """A git repository whose remote's default branch is `main`, with the session's folder committed
    on the branch `work`, checked out; git reads no setting of the machine it runs on."""

    def setUp(self) -> None:
        super().setUp()
        self.repo = self.copied("session", self.kept_on_work)

    def kept_on_work(self) -> None:
        """Makes where the test stands the repository, the session's folder committed on `work`."""
        self.main_and_work()
        self.write(f"{FOLDER}/state.json", '{"stage": "asking"}')
        self.commit()

    def on_main(self) -> None:
        """The default branch checked out, with the session's folder made on it, as `rn.py start`
        makes it before the conductor switches to the session's branch."""
        self.git("checkout", "-q", "main")
        self.write(f"{FOLDER}/state.json", '{"stage": "asking"}')

    def event(self, command: str, cwd: str | None = None, tool: str = "Bash") -> str:
        """The PreToolUse event Claude Code hands the hook for the tool's call with the command, in
        the folder, the repository where none is given."""
        return json.dumps(
            {
                "session_id": "abc123",
                "transcript_path": os.path.join(self.base, "abc123.jsonl"),
                "cwd": cwd or self.repo,
                "permission_mode": "default",
                "hook_event_name": "PreToolUse",
                "tool_name": tool,
                "tool_input": {"command": command, "description": "Run it"},
                "tool_use_id": "toolu_01",
            }
        )

    def handed(self, stream: str) -> tuple[int, str]:
        """The exit code and what the entry wrote on stderr, handed the text on stdin."""
        err = io.StringIO()
        code = hook.run("rn", events.PRETOOLUSE, io.StringIO(stream), err)
        return code, err.getvalue()

    def hook(self, command: str, cwd: str | None = None, tool: str = "Bash") -> tuple[int, str]:
        """The exit code and what the entry wrote on stderr for the tool's call with the command."""
        return self.handed(self.event(command, cwd, tool))


class DefaultBranchTest(HookTest):
    """The default branch checked out in a repository holding a session's folder."""

    def setUp(self) -> None:
        super().setUp()
        self.on_main()

    def test_a_commit_on_the_default_branch_is_stopped(self):
        # Given: the default branch checked out, with a session's folder.
        # When: the conductor commits.
        # Then: the hook stops the call.
        self.assertEqual(self.hook("git commit -m 'Keep the plan'")[0], 2)

    def test_a_push_on_the_default_branch_is_stopped(self):
        # Given: the default branch checked out, with a session's folder.
        # When: the conductor pushes another branch.
        # Then: the hook stops the call.
        self.assertEqual(self.hook("git push origin work")[0], 2)

    def test_the_commit_stop_says_to_commit_on_the_sessions_branch_and_why(self):
        # Given: the default branch checked out, with a session's folder.
        # When: the conductor commits.
        # Then: the hook says to switch to the session's branch and commit there, and why.
        self.assertEqual(self.hook("git commit -m m")[1], ON_MAIN.format("commit"))

    def test_the_push_stop_names_the_push(self):
        # Given: the default branch checked out, with a session's folder.
        # When: the conductor pushes.
        # Then: the hook's stop names the push.
        self.assertEqual(self.hook("git push")[1], ON_MAIN.format("push"))

    def test_a_merged_sessions_folder_makes_the_default_branch_rns(self):
        # Given: the default branch checked out, holding the folder of a session merged into it.
        self.write(f"{OLD}/state.json", "{}")
        os.remove(f"{FOLDER}/state.json")
        os.rmdir(FOLDER)
        self.commit()
        # When: the conductor commits.
        # Then: the hook stops the call.
        self.assertEqual(self.hook("git commit -m m")[0], 2)

    def test_a_commit_after_other_statements_is_stopped(self):
        # Given: the default branch checked out, with a session's folder.
        # When: the conductor commits after other statements of the same command.
        # Then: the hook stops the call.
        self.assertEqual(self.hook("ls; git add -A && git commit -m m")[0], 2)

    def test_the_keep_of_rns_skill_is_stopped_at_its_commit(self):
        # Given: the default branch checked out, with a session's folder.
        # When: the conductor keeps the session's folder as rn's /rn:up skill says.
        # Then: the hook stops the call, naming its commit.
        self.assertEqual(self.hook(KEEP)[1], ON_MAIN.format("commit"))

    def test_a_commit_from_a_folder_below_the_top_is_stopped(self):
        # Given: the default branch checked out, with a session's folder, and the call made in a
        # folder below the top of the repository.
        os.makedirs("src")
        # When: the conductor commits there.
        # Then: the hook stops the call.
        self.assertEqual(self.hook("git commit -m m", cwd=os.path.join(self.repo, "src"))[0], 2)

    def test_the_hook_ends_in_the_folder_of_the_call(self):
        # Given: the default branch checked out, with a session's folder, and the call made in a
        # folder below the top of the repository.
        src = os.path.join(self.repo, "src")
        os.makedirs(src)
        # When: the conductor commits there.
        self.hook("git commit -m m", cwd=src)
        # Then: the hook is back in that folder after the check.
        self.assertEqual(os.getcwd(), src)

    def test_a_command_with_no_commit_or_push_goes_on(self):
        # Given: the default branch checked out, with a session's folder.
        # When: the conductor runs git commands that neither commit nor push.
        # Then: the hook lets the call go on, saying nothing.
        self.assertEqual(self.hook("git status && git log -1 | cat"), (0, ""))

    def test_a_commit_in_quotes_goes_on(self):
        # Given: the default branch checked out, with a session's folder.
        # When: the conductor prints the words of a commit.
        # Then: the hook lets the call go on.
        self.assertEqual(self.hook("echo 'git commit'; echo git push")[0], 0)

    def test_a_commit_in_a_heredocs_text_goes_on(self):
        # Given: the default branch checked out, with a session's folder.
        # When: the conductor writes a file whose text holds a commit.
        # Then: the hook lets the call go on.
        self.assertEqual(self.hook("cat > notes.md <<'EOF'\ngit commit -m m\nEOF")[0], 0)

    def test_another_tool_goes_on(self):
        # Given: the default branch checked out, with a session's folder.
        # When: the conductor calls a tool other than Bash, its input holding a commit.
        # Then: the hook lets the call go on.
        self.assertEqual(self.hook("git commit -m m", tool="Write")[0], 0)

    def test_an_unknown_default_branch_stops_with_how_to_have_git_learn_it(self):
        # Given: a session's folder in a repository whose remote's default branch git does not
        # know.
        self.git("symbolic-ref", "--delete", "refs/remotes/origin/HEAD")
        # When: the conductor commits.
        err = self.hook("git commit -m m")[1]
        # Then: the hook says what git said and how to have git learn the default branch, once
        # led by `rn: `.
        self.assertRegex(
            err,
            r"^rn: git symbolic-ref --short refs/remotes/origin/HEAD failed: .*; run `git remote"
            r" set-head origin --auto` so git knows the default branch, then run this again\n$",
        )


class NotRnsTest(HookTest):
    """A commit on the default branch where the work is not rn's."""

    def setUp(self) -> None:
        super().setUp()
        self.git("checkout", "-q", "main")

    def test_the_default_branch_without_a_session_goes_on(self):
        # Given: the default branch checked out, with no folder under .rn/.
        # When: a commit is made.
        # Then: the hook lets the call go on.
        self.assertEqual(self.hook("git commit -m m"), (0, ""))

    def test_the_users_checklists_alone_are_no_session(self):
        # Given: the default branch checked out, holding the user's checklists under .rn/ alone.
        self.write(".rn/checklists/code.md", "# Code\n")
        # When: a commit is made.
        # Then: the hook lets the call go on.
        self.assertEqual(self.hook("git commit -m m")[0], 0)

    def test_a_file_named_as_a_session_is_no_session(self):
        # Given: the default branch checked out, holding a file named as a session's folder.
        self.write(".rn/20261020-x", "")
        # When: a commit is made.
        # Then: the hook lets the call go on.
        self.assertEqual(self.hook("git commit -m m")[0], 0)

    def test_outside_a_repository_every_command_goes_on(self):
        # Given: a folder no git repository holds, named as rn's record.
        outside = os.path.join(self.base, "outside")
        os.makedirs(os.path.join(outside, FOLDER))
        # When: a commit is tried there.
        # Then: the hook lets the call go on.
        self.assertEqual(self.hook("git commit -m m", cwd=outside), (0, ""))


class PushToDefaultTest(HookTest):
    """The session's branch checked out."""

    def test_a_commit_on_the_sessions_branch_goes_on(self):
        # Given: the session's branch checked out.
        # When: the conductor keeps the session's folder as rn's /rn:up skill says.
        # Then: the hook lets the call go on.
        self.assertEqual(self.hook(KEEP), (0, ""))

    def test_a_push_of_the_sessions_branch_goes_on(self):
        # Given: the session's branch checked out.
        # When: the conductor pushes it to its own name, setting its upstream.
        # Then: the hook lets the call go on.
        self.assertEqual(self.hook("git push -u origin work")[0], 0)

    def test_a_push_to_the_default_branch_is_stopped(self):
        refspecs = ("work:main", "HEAD:main", "+work:main", "work:refs/heads/main", "main", ":main")
        for refspec in refspecs:
            with self.subTest(refspec=refspec):
                # Given: the session's branch checked out.
                # When: the conductor pushes with a refspec whose destination is the default
                # branch.
                # Then: the hook stops the call.
                self.assertEqual(self.hook(f"git push origin {refspec}")[0], 2)

    def test_the_push_stop_says_to_push_to_the_branchs_own_name_and_why(self):
        # Given: the session's branch checked out.
        # When: the conductor pushes it to the default branch.
        # Then: the hook says to push it to its own name instead, and why.
        self.assertEqual(self.hook("git push origin work:main")[1], TO_MAIN.format("work"))

    def test_a_push_from_a_detached_head_says_to_name_the_sessions_branch(self):
        # Given: the session's last commit checked out, on no branch.
        self.git("checkout", "-q", "--detach")
        # When: the conductor pushes it to the default branch.
        # Then: the hook says to push it to the session's branch by name.
        want = TO_MAIN.format("HEAD:<the session's branch>")
        self.assertEqual(self.hook("git push origin HEAD:main")[1], want)

    def test_a_push_valued_option_is_no_refspec(self):
        # Given: the session's branch checked out.
        # When: the conductor pushes it with a push option whose value is the default branch's
        # name.
        # Then: the hook lets the call go on.
        self.assertEqual(self.hook("git push -o main origin work")[0], 0)

    def test_a_push_to_the_default_branch_after_a_valued_option_is_stopped(self):
        # Given: the session's branch checked out.
        # When: the conductor pushes to the default branch after an option and its value.
        # Then: the hook stops the call.
        self.assertEqual(self.hook("git push --push-option ci.skip origin work:main")[0], 2)

    def test_a_repository_named_as_the_default_branch_is_no_destination(self):
        # Given: the session's branch checked out.
        # When: the conductor pushes it to a remote named as the default branch.
        # Then: the hook lets the call go on.
        self.assertEqual(self.hook("git push main work")[0], 0)

    def test_a_push_to_another_branch_goes_on(self):
        # Given: the session's branch checked out.
        # When: the conductor pushes it to a branch other than the default branch.
        # Then: the hook lets the call go on.
        self.assertEqual(self.hook("git push origin work:feature")[0], 0)

    def upstream_on_main(self) -> None:
        """git pushing the session's branch to its upstream, the default branch."""
        self.git("remote", "add", "origin", os.path.join(self.base, "remote"))
        self.git("config", "push.default", "upstream")
        self.git("branch", "-q", "--set-upstream-to", "origin/main")

    def test_a_plain_push_to_an_upstream_on_the_default_branch_is_stopped(self):
        # Given: the session's branch checked out, git pushing it to its upstream, the default
        # branch.
        self.upstream_on_main()
        # When: the conductor pushes with no refspec.
        # Then: the hook stops the call.
        self.assertEqual(self.hook("git push")[0], 2)

    def test_a_commit_on_a_branch_pushed_to_the_default_branch_goes_on(self):
        # Given: the session's branch checked out, git pushing it to its upstream, the default
        # branch.
        self.upstream_on_main()
        # When: the conductor commits, with a message holding no option.
        # Then: the hook lets the call go on, as a commit sends nothing.
        self.assertEqual(self.hook("git commit -m main"), (0, ""))

    def test_a_push_naming_the_remote_alone_goes_where_git_pushes_the_branch(self):
        # Given: the session's branch checked out, git pushing it to its upstream, the default
        # branch.
        self.upstream_on_main()
        # When: the conductor pushes naming the remote and no refspec.
        # Then: the hook stops the call.
        self.assertEqual(self.hook("git push origin")[0], 2)

    def test_a_plain_push_without_an_upstream_goes_on(self):
        # Given: the session's branch checked out, with no upstream.
        # When: the conductor pushes with no refspec, which git refuses on its own.
        # Then: the hook lets the call go on.
        self.assertEqual(self.hook("git push")[0], 0)

    def test_a_push_to_the_default_branch_from_below_the_top_is_stopped(self):
        # Given: the session's branch checked out, and the call made in a folder below the top of
        # the repository.
        os.makedirs("src")
        # When: the conductor pushes to the default branch there.
        # Then: the hook stops the call for the push.
        err = self.hook("git push origin work:main", cwd=os.path.join(self.repo, "src"))[1]
        self.assertEqual(err, TO_MAIN.format("work"))

    def test_a_push_to_the_default_branch_from_a_branch_without_a_session_goes_on(self):
        # Given: a branch that changed no session, made from a default branch holding a merged
        # session's folder.
        self.git("checkout", "-q", "main")
        self.write(f"{OLD}/state.json", "{}")
        self.commit()
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")
        self.git("checkout", "-q", "-b", "other")
        # When: it is pushed to the default branch.
        # Then: the hook lets the call go on, as the work is not rn's.
        self.assertEqual(self.hook("git push origin other:main"), (0, ""))

    def test_two_sessions_not_finished_stop_with_what_rn_says(self):
        # Given: the session's branch, which changed two sessions not finished.
        self.write(f"{OLD}/state.json", "{}")
        self.commit()
        # When: the conductor pushes to the default branch.
        err = self.hook("git push origin work:main")[1]
        # Then: the hook says what rn.py says of it, once led by `rn: `.
        self.assertTrue(
            err.startswith("rn: this branch changed more than one session not finished")
        )


class DestinationTest(unittest.TestCase):
    """Where a refspec of `git push` sends to."""

    def test_head_sends_to_the_checked_out_branch(self):
        # Given: the refspec `HEAD`, with the branch `work` checked out.
        # When: its destination is read.
        # Then: it is `work`.
        self.assertEqual(default_branch.destination("HEAD", "work"), "work")

    def test_head_on_a_detached_head_sends_to_no_branch(self):
        # Given: the refspec `HEAD`, on no branch.
        # When: its destination is read.
        # Then: it is no branch.
        self.assertIsNone(default_branch.destination("HEAD", None))


class EntryTest(HookTest):
    """The PreToolUse entry, as Claude Code runs it."""

    def test_an_event_in_claude_codes_shape_goes_on_where_no_check_stops_it(self):
        # Given: the session's branch checked out.
        # When: the entry is handed a commit's event.
        # Then: it exits 0, saying nothing.
        self.assertEqual(self.hook("git commit -m m"), (0, ""))

    def test_the_entry_run_as_a_script_exits_2_on_a_stop(self):
        # Given: the default branch checked out, with a session's folder, and the entry run as a
        # script, in this process so that the coverage of the test run counts it.
        self.on_main()
        script = os.path.join(HOOKS, "pretooluse.py")
        stdin = mock.patch.object(sys, "stdin", io.StringIO(self.event("git commit -m m")))
        err = io.StringIO()
        # When: Claude Code hands it a commit's event.
        with stdin, contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as done:
            runpy.run_path(script, run_name="__main__")
        # Then: it exits 2, with the stop on stderr.
        self.assertEqual((done.exception.code, err.getvalue()), (2, ON_MAIN.format("commit")))


class HooksJsonTest(HookTest):
    """The hook's command in hooks.json, run by a shell as Claude Code runs it."""

    def entry(self) -> dict:
        """The PreToolUse entry of hooks.json."""
        with open(os.path.join(HOOKS, "hooks.json"), encoding="utf-8") as f:
            return json.load(f)["hooks"]["PreToolUse"][0]

    def run_hook(self, path: str) -> subprocess.CompletedProcess:
        """The hook's command run by sh with the PATH, handed a commit's event on the default
        branch with a session's folder."""
        self.on_main()
        env = dict(os.environ, PATH=path, CLAUDE_PLUGIN_ROOT=PLUGIN)
        env.pop("PYTHONPATH", None)
        command = self.entry()["hooks"][0]["command"]
        return subprocess.run(
            ["/bin/sh", "-c", command],
            input=self.event("git commit -m m"),
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )

    def test_the_hook_is_run_for_each_bash_call(self):
        # Given: hooks.json.
        # When: Claude Code matches its PreToolUse entry against the Bash tool.
        # Then: the entry matches.
        self.assertTrue(re.fullmatch(self.entry()["matcher"], "Bash"))

    def test_the_hook_runs_the_checks_with_rns_scripts(self):
        # Given: python3 and git on PATH.
        path = os.pathsep.join([os.path.dirname(sys.executable), os.environ["PATH"]])
        # When: the hook's command is run for a commit on the default branch.
        done = self.run_hook(path)
        # Then: it stops the call, saying why.
        self.assertEqual((done.returncode, done.stderr), (2, ON_MAIN.format("commit")))

    def test_the_hook_without_python3_lets_every_command_through(self):
        # Given: a PATH holding no python3.
        empty = os.path.join(self.base, "bin")
        os.makedirs(empty)
        # When: the hook's command is run for a commit on the default branch.
        done = self.run_hook(empty)
        # Then: it lets the call go on, saying nothing.
        self.assertEqual((done.returncode, done.stderr), (0, ""))


# .claude/rules/plugin.md has CI run Hypothesis on the newest Python alone, so where it is not
# installed, as on 3.9, the property tests are not defined, and the examples alone run.
if importlib.util.find_spec("hypothesis") is not None:
    import hypothesis  # pyrefly: ignore[missing-import]
    from hypothesis import strategies as st  # pyrefly: ignore[missing-import]

    testing.load_hypothesis_profile()
    # Any character a branch name may hold: git refuses a name holding a control character, a
    # blank or one of ~^:?*[\.
    NAME = st.text(
        st.characters(blacklist_categories=("Cs", "Cc"), blacklist_characters=" ~^:?*[\\"),
        min_size=1,
    )

    class PropertyTest(unittest.TestCase):
        @hypothesis.given(NAME, NAME, NAME)
        def test_any_refspec_sends_to_what_follows_its_colon(self, remote, source, target):
            # Given: a push of any branch to any other, to any remote. Left out, as the user
            # decided, since git refuses such a branch name: a name beginning with `-`, which
            # git push reads as an option (code.md B-16). A `+` before a refspec marks it forced,
            # `HEAD` names the checked-out branch, and `refs/heads/` begins the full name of a
            # branch, so none of them is part of a branch's name.
            hypothesis.assume(not remote.startswith("-") and not source.startswith(("-", "+")))
            hypothesis.assume(target != "HEAD" and not target.startswith("refs/heads/"))
            # When: its destination is read.
            found = default_branch.destinations([remote, f"{source}:{target}"], "work")
            # Then: it is the branch after the colon.
            self.assertEqual(found, [target])

        @hypothesis.given(NAME, NAME)
        def test_any_branch_pushed_by_name_is_its_destination(self, remote, branch):
            # Given: a push of any branch by its name alone, to any remote; names beginning with
            # `-` left out, and `+`, `HEAD` and `refs/heads/` set apart, as above.
            hypothesis.assume(not remote.startswith("-") and not branch.startswith(("-", "+")))
            hypothesis.assume(branch != "HEAD" and not branch.startswith("refs/heads/"))
            # When: its destination is read.
            # Then: it is the branch of that name.
            self.assertEqual(default_branch.destinations([remote, branch], "work"), [branch])


if __name__ == "__main__":
    unittest.main()
