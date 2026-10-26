"""The tests of the session: found from the branch, started with its draft pull request, each move
kept with `state`, and each part the orchestrator wrote put back into the record."""

from __future__ import annotations

import os
import shutil
import unittest
from unittest import mock

from helpers import (
    CALLS,
    FOLDER,
    HISTORY,
    KIND,
    LEARNINGS,
    NEXT,
    PR,
    RECORD,
    REPOSITORY,
    SHOWN,
    SLUG,
    STEERED,
    STEERING,
    RepoTest,
    call_at,
    options,
    plan,
    rn,
    steered,
    task,
)


class SessionTest(RepoTest):
    def test_no_session_where_the_branch_changed_none(self):
        # Given: a branch that changed nothing under .rn/.
        # When: the orchestrator asks for the session.
        # Then: rn says there is none, and no stage or sign-off.
        self.assertEqual(self.ran("session"), {"session": None, "stage": None, "signoff": None})

    def test_the_session_the_branch_changed_is_found_with_its_stage(self):
        # Given: a session's folder committed on the branch, at the design stage, no sign-off
        # waiting.
        self.session(steered(stage="design"))
        # When: the orchestrator asks for the session.
        # Then: rn gives its folder and its stage, and no sign-off waiting.
        want = {"session": FOLDER, "stage": "design", "signoff": None}
        self.assertEqual(self.ran("session"), want)

    def test_the_signoff_waiting_is_given(self):
        # Given: a session whose steering waits at the plan sign-off.
        self.session(steered(signoff="plan"))
        # When: the orchestrator asks for the session.
        # Then: rn gives the sign-off waiting.
        self.assertEqual(self.ran("session")["signoff"], "plan")

    def test_a_finished_session_is_not_taken_up(self):
        # Given: a session on the branch whose steering is at the finished stage.
        self.session(steered(stage="finished"))
        # When: the orchestrator asks for the session.
        # Then: there is none.
        self.assertIsNone(self.ran("session")["session"])

    def test_a_steering_finished_and_not_yet_kept_is_still_the_session(self):
        # Given: a session whose steering is set finished in the working tree and not committed.
        self.session()
        self.write(STEERING, steered(stage="finished"))
        # When: the orchestrator asks for the session.
        # Then: it is found, as the last commit holds it at the plan stage.
        self.assertEqual(self.ran("session")["session"], FOLDER)

    def test_a_session_on_the_default_branch_is_not_taken_up(self):
        # Given: a session merged into the default branch, which the branch did not change.
        self.git("checkout", "-q", "main")
        self.write(f"{RECORD}/20261001-old/steering.md", STEERED)
        self.commit()
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")
        self.git("checkout", "-q", "-B", "work")
        # When: the orchestrator asks for the session.
        # Then: there is none.
        self.assertIsNone(self.ran("session")["session"])

    def test_a_session_the_branch_removed_is_not_taken_up(self):
        # Given: a session folder on the default branch, which the branch removed.
        old = f"{RECORD}/20261001-old"
        self.git("checkout", "-q", "main")
        self.write(f"{old}/steering.md", STEERED)
        self.commit()
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")
        self.git("checkout", "-q", "-B", "work")
        self.git("rm", "-q", "-r", old)
        self.commit()
        # When: the orchestrator asks for the session.
        # Then: there is none.
        self.assertIsNone(self.ran("session")["session"])

    def test_the_users_checklists_are_not_a_session(self):
        # Given: a branch that changed only the user's checklists under .rn/.
        self.write(f"{RECORD}/checklists/{KIND}.md", "# Code\n")
        self.commit()
        # When: the orchestrator asks for the session.
        # Then: there is none.
        self.assertIsNone(self.ran("session")["session"])

    def test_a_file_straight_under_rn_is_not_a_session(self):
        # Given: a branch that changed a file named as a session, straight under .rn/.
        self.write(f"{RECORD}/20261020-x", "")
        self.commit()
        # When: the orchestrator asks for the session.
        # Then: there is none.
        self.assertIsNone(self.ran("session")["session"])

    def test_a_session_without_a_steering_is_found_with_no_stage(self):
        # Given: a session folder holding no steering.
        self.session(None)
        # When: the orchestrator asks for the session.
        # Then: it is found, with no stage and no sign-off.
        self.assertEqual(self.ran("session"), {"session": FOLDER, "stage": None, "signoff": None})

    def test_a_steering_without_a_readable_front_matter_is_not_finished(self):
        texts = (
            "stage: finished\n---\n",
            "--\nstage: finished\n---\n",
            "",
            "---\nstage: finished\n",
            "---\nnotes\nstage: finished\n---\n",
            "---\n---\nstage: finished\n---\n",
        )
        for text in texts:
            with self.subTest(text=text):
                # Given: a session whose steering says it is finished in no front matter rn reads:
                # one it does not open with, never closes, holds a line that is no `key: value`, or
                # one that is empty with the stage after it.
                self.session(text)
                # When: the orchestrator asks for the session.
                # Then: it is found, as nothing says it is over.
                self.assertEqual(self.ran("session")["session"], FOLDER)

    def test_two_sessions_not_finished_stop(self):
        # Given: a branch that changed two sessions, neither finished.
        other = f"{RECORD}/20261021-other"
        self.session()
        self.session(folder=other)
        # When: the orchestrator asks for the session.
        # Then: rn names both and says to check out the branch of the one to go on with.
        self.assertIn(
            f"more than one session not finished: {FOLDER}, {other}; a branch holds one session,"
            " so check out the branch of the one to go on with",
            self.stopped("session"),
        )

    def test_below_the_top_of_the_repository_stops(self):
        # Given: rn run from a folder below the top of the repository.
        os.makedirs("src")
        os.chdir("src")
        # When: the orchestrator asks for the session.
        # Then: rn says to run it from the top.
        self.assertIn(
            "runs in src/ below the top of the repository; run it from the top, after"
            ' `cd "$(git rev-parse --show-toplevel)"`',
            self.stopped("session"),
        )

    def test_outside_a_repository_stops(self):
        # Given: rn run from a folder no git repository holds.
        os.chdir(self.plugin)
        # When: the orchestrator asks for the session.
        out = self.stopped("session")
        # Then: rn says what git said and to run it inside the user's repository.
        self.assertRegex(
            out, r"rn: git rev-parse --show-prefix failed: fatal: .*; run rn inside the user's"
        )

    def test_an_unknown_default_branch_stops(self):
        # Given: a repository whose remote's default branch git does not know.
        self.git("symbolic-ref", "--delete", "refs/remotes/origin/HEAD")
        # When: the orchestrator asks for the session.
        # Then: rn says how to have git learn it.
        self.assertIn("git remote set-head origin --auto", self.stopped("session"))

    def test_a_branch_unrelated_to_the_default_branch_stops(self):
        # Given: a default branch with no history in common with the checked-out branch.
        self.git("checkout", "-q", "--orphan", "lone")
        self.write("lone.md", "# lone\n")
        self.commit()
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")
        self.git("checkout", "-q", "work")
        # When: the orchestrator asks for the session.
        # Then: rn says the two share no history, and how to fetch it whole.
        self.assertIn(
            "rn: git merge-base origin/main HEAD failed; the checked-out branch shares no history"
            " with origin/main; fetch it whole with `git fetch --unshallow origin`",
            self.stopped("session"),
        )


class StartTest(RepoTest):
    def start(self, slug: str = SLUG, message: str = "Start add-login", **given: str) -> list[str]:
        """The arguments that start a session with the slug and the message, and each other option
        as given or a value it takes."""
        values = {
            "title": "Add login",
            "artifact-language": "English",
            "conversation-language": "Japanese",
            **{key.replace("_", "-"): value for key, value in given.items()},
        }
        return ["start", slug, *options({f"--{k}": v for k, v in values.items()})] + [
            "--message",
            message,
        ]

    def test_start_makes_the_sessions_branch_from_the_remotes_default_branch(self):
        # Given: the branch `work`, holding a commit the default branch does not.
        self.write("work.md", "x\n")
        self.commit()
        # When: the orchestrator starts a session.
        self.ran(*self.start())
        # Then: the branch named by the slug is checked out, made from origin's main alone.
        here = (self.out("branch", "--show-current"), os.path.exists("work.md"))
        self.assertEqual(here, (f"{SLUG}\n", False))

    def test_start_from_a_branch_of_another_name_makes_the_sessions_branch(self):
        # Given: the branch `a` checked out, holding no session.
        self.git("checkout", "-q", "-b", "a")
        # When: the orchestrator starts a session.
        self.ran(*self.start())
        # Then: the branch named by the slug is checked out.
        self.assertEqual(self.out("branch", "--show-current"), f"{SLUG}\n")

    def test_start_writes_the_steering_with_the_title_next_and_the_pull_request(self):
        # Given: a branch with no session.
        # When: the orchestrator starts one.
        self.ran(*self.start())
        # Then: the steering holds rn's version, the pull request, the plan stage, no sign-off,
        # the languages, the title, Next the step that makes the plan and nothing open, as kept
        # on the remote.
        want = steered(part="# Add login", next_step=rn.STARTED)
        self.assertEqual(
            (self.read(STEERING), self.out("show", f"origin/{SLUG}:{STEERING}")), (want, want)
        )

    def test_start_keeps_the_steering_with_the_message_before_the_pull_request(self):
        # Given: a branch with no session.
        # When: the orchestrator starts one with a message.
        self.ran(*self.start(message="Start add-login\n\nFrom the user's words."))
        # Then: the commit before the last holds the steering with no pull request yet, with the
        # message as given; the last keeps the pull request.
        kept = (
            "pr: none\n" in self.out("show", f"origin/{SLUG}~1:{STEERING}"),
            self.out("log", "-1", "--format=%B", f"origin/{SLUG}~1"),
            self.out("log", "-1", "--format=%B", f"origin/{SLUG}"),
        )
        want = (True, "Start add-login\n\nFrom the user's words.\n\n", f"pr: {PR}\n\n")
        self.assertEqual(kept, want)

    def test_start_opens_the_draft_pull_request_linking_the_steering(self):
        # Given: a branch with no session.
        # When: the orchestrator starts one.
        self.ran(*self.start())
        # Then: gh is asked the repository's URL, then opens a draft pull request of the branch
        # into the default branch, with the title and a body linking the steering.
        link = f"[steering.md]({REPOSITORY}/blob/{SLUG}/{STEERING})"
        want = [
            ["repo", "view", "--json", "url", "--jq", ".url"],
            ["pr", "create", "--draft", "--base", "main", "--head", SLUG, "--title", "Add login"]
            + ["--body", link],
        ]
        self.assertEqual(self.asked(), want)

    def test_start_gives_the_session_its_branch_and_the_pull_request(self):
        # Given: a branch with no session.
        # When: the orchestrator starts one.
        # Then: rn gives the session's folder, its branch and its pull request.
        want = {"session": FOLDER, "branch": SLUG, "pr": PR}
        self.assertEqual(self.ran(*self.start()), want)

    def test_a_pull_request_not_opened_stops_and_start_again_opens_it(self):
        # Given: gh failing as it does when not logged in.
        with mock.patch.dict(os.environ, {"GH_FAIL": "To get started, run: gh auth login"}):
            # When: the orchestrator starts a session.
            out = self.stopped(*self.start())
        kept = self.out("show", f"origin/{SLUG}:{STEERING}")
        # Then: rn says what gh said and to run start again, the steering kept with no pull
        # request; and start run again opens it and keeps it.
        again = self.ran(*self.start())
        self.assertEqual(
            (
                "failed: To get started, run: gh auth login; fix it as gh says, such as with"
                " `gh auth login`, then run `rn.py start` again with the same arguments" in out,
                "pr: none\n" in kept,
                again,
                self.read(STEERING),
            ),
            (
                True,
                True,
                {"session": FOLDER, "branch": SLUG, "pr": PR},
                steered(part="# Add login", next_step=rn.STARTED),
            ),
        )

    def test_start_again_on_a_session_with_its_pull_request_stops(self):
        # Given: a session started, with its pull request.
        self.ran(*self.start())
        # When: the orchestrator starts it again.
        # Then: rn says it is started already, and how to go on with it.
        self.assertIn(
            f"rn: the session {FOLDER} is started already, with its pull request {PR}; go on with"
            " it with /rn:up",
            self.stopped(*self.start()),
        )

    def test_start_without_gh_stops_saying_to_install_it(self):
        # Given: a PATH holding git and no gh.
        lone = os.path.join(self.base, "lone")
        os.makedirs(lone)
        os.symlink(shutil.which("git") or "", os.path.join(lone, "git"))
        with mock.patch.dict(os.environ, {"PATH": lone}):
            # When: the orchestrator starts a session.
            out = self.stopped(*self.start())
        # Then: rn says gh could not be run, and to install it.
        self.assertIn("rn: gh could not be run: No such file or directory; install it", out)

    def test_start_without_rns_manifest_stops(self):
        # Given: a plugin folder without its manifest.
        os.remove(os.path.join(self.plugin, ".claude-plugin", "plugin.json"))
        # When: the orchestrator starts a session.
        out = self.stopped(*self.start())
        # Then: rn says its version is not given, to install rn again, and the branch stays.
        said = "plugin.json gives no version of rn; install rn again" in out
        self.assertEqual((said, self.out("branch", "--show-current")), (True, "work\n"))

    def test_start_with_changes_not_committed_stops_and_stays(self):
        # Given: a file changed and not committed.
        self.write("README.md", "# changed\n")
        # When: the orchestrator starts a session.
        out = self.stopped(*self.start())
        # Then: rn names the change and says to commit or stash it, and the branch stays.
        said = "rn: the working tree has changes not committed: README.md; rn leaves them as" in out
        self.assertEqual((said, self.out("branch", "--show-current")), (True, "work\n"))

    def test_start_on_a_folder_the_default_branch_holds_stops_and_stays(self):
        # Given: the default branch holding a session folder of today's date and the slug.
        self.git("checkout", "-q", "main")
        self.write(STEERING, STEERED)
        self.commit()
        self.git("push", "-q")
        self.git("checkout", "-q", "work")
        # When: the orchestrator starts one with that slug.
        out = self.stopped(*self.start())
        # Then: rn says it is there and to give another slug, and the branch stays.
        said = f"{FOLDER} is on origin/main already; give another slug" in out
        self.assertEqual((said, self.out("branch", "--show-current")), (True, "work\n"))

    def test_start_on_a_branch_there_stops(self):
        # Given: a branch named as the slug.
        self.git("branch", SLUG)
        # When: the orchestrator starts a session with that slug.
        # Then: rn says what git said and to give another slug.
        self.assertRegex(
            self.stopped(*self.start()),
            rf"rn: git checkout -q --no-track -b {SLUG} origin/main failed: fatal: .*; give"
            " another slug",
        )

    def test_start_with_the_remote_not_reached_stops(self):
        # Given: a remote that cannot be reached.
        self.git("remote", "set-url", "origin", "../none.git")
        # When: the orchestrator starts a session.
        # Then: rn says what git said and to fix it.
        self.assertRegex(
            self.stopped(*self.start()),
            r"(?s)rn: git fetch -q origin failed: .*; fix it as git says",
        )

    def test_start_below_the_top_stops_and_makes_no_folder(self):
        # Given: rn run from a folder below the top of the repository.
        os.makedirs("src")
        os.chdir("src")
        # When: the orchestrator starts a session.
        out = self.stopped(*self.start())
        # Then: rn says to run it from the top, and makes no session folder.
        said = "below the top of the repository" in out
        self.assertEqual((said, os.path.exists(os.path.join("..", RECORD))), (True, False))

    def test_a_slug_of_other_characters_stops(self):
        # Given: a slug with a character other than lowercase letters, digits and hyphens.
        # When: the orchestrator starts a session with it.
        # Then: rn says what a slug holds.
        self.assertIn(
            "the slug '../x' is not lowercase letters, digits and hyphens alone; give it as such",
            self.stopped(*self.start(slug="../x")),
        )

    def test_start_with_an_empty_value_stops_and_stays(self):
        for option, words in (
            ("message", "message"),
            ("title", "title"),
            ("artifact_language", "artifact-language"),
            ("conversation_language", "conversation-language"),
        ):
            with self.subTest(option=option):
                # Given: a branch with no session.
                # When: the orchestrator starts one with a value of blanks.
                given = {"message": " \n"} if option == "message" else {option: " "}
                out = self.stopped(*self.start(**given))
                # Then: rn says it is empty, and the branch stays.
                said = f"rn: the {words} is empty; give it in words" in out
                self.assertEqual((said, self.out("branch", "--show-current")), (True, "work\n"))

    def test_a_title_the_steering_cannot_hold_stops_and_stays(self):
        # Given: a branch with no session.
        # When: the orchestrator starts one with a title over two lines.
        out = self.stopped(*self.start(title="Add\nlogin"))
        # Then: rn says the steering would be out of its form, and the branch stays.
        said = "rn: the steering would be out of its form: line 11: expected the goal" in out
        self.assertEqual((said, self.out("branch", "--show-current")), (True, "work\n"))


class StateTest(RepoTest):
    """Where the session stands, rewritten at each move, and every change kept."""

    def setUp(self) -> None:
        super().setUp()
        self.session()

    def state(self, *more: str, message: str = "plan: the first point asked") -> list[str]:
        """The arguments that keep a move with Next given and the message, and more."""
        return ["state", "--next", "3. Make the plan.", *more, "--message", message]

    def test_next_and_open_are_replaced_whole_and_kept_on_the_remote(self):
        # Given: a session kept.
        # When: the orchestrator keeps a move with Next and two points open.
        self.ran(*self.state("--open", "Which login?", "--open", "Where to?"))
        # Then: the steering holds them, as the remote's branch does, with the message.
        want = steered(next_step="3. Make the plan.", opened="- Which login?\n- Where to?")
        kept = (
            self.read(STEERING),
            self.out("show", f"origin/work:{STEERING}"),
            self.out("log", "-1", "--format=%B", "origin/work"),
        )
        self.assertEqual(kept, (want, want, "plan: the first point asked\n\n"))

    def test_a_steering_without_blank_lines_before_headings_is_rewritten_in_rns_layout(self):
        # Given: a steering in form whose headings of Next and Open follow a line of words, as a
        # commit by hand left it.
        text = STEERED
        for heading in ("Next", "Open"):
            text = text.replace(f"\n\n## {heading}", f"\n## {heading}")
        self.session(text)
        # When: the orchestrator keeps a decision, a move that leaves the steering as it is.
        self.ran("decide", "t1.1", "--title", "A", "--says", "B", "--message", "m")
        # Then: the steering holds every line, a blank line before each of those headings.
        self.assertEqual(self.read(STEERING), STEERED)

    def test_no_point_open_is_kept_as_none(self):
        # Given: a session with a point open.
        self.ran(*self.state("--open", "Which login?"))
        # When: the orchestrator keeps a move with none open.
        self.ran(*self.state())
        # Then: Open holds `None.`.
        self.assertEqual(self.read(STEERING), steered(next_step="3. Make the plan."))

    def test_every_change_of_the_move_is_kept_and_the_commit_given(self):
        # Given: a file the move made.
        self.write("README.md", "# app, made\n")
        # When: the orchestrator keeps the move.
        out = self.ran(*self.state())
        # Then: the commit given holds the steering and the file, and nothing is left to keep.
        changed = self.out("show", "--name-only", "--format=", "HEAD").split()
        left = self.out("status", "--porcelain")
        self.assertEqual((out, changed, left), ({"kept": self.head()}, [STEERING, "README.md"], ""))

    def test_nothing_changed_pushes_what_is_committed(self):
        # Given: a commit not pushed, and a move that changes nothing more.
        self.write("notes.md", "x\n")
        self.commit()
        self.ran(*self.state())
        before = self.head()
        # When: the orchestrator keeps the same move again.
        out = self.ran(*self.state())
        # Then: no commit is made, and the branch is pushed.
        self.assertEqual((out["kept"], self.head("origin/work")), (before, before))

    def test_an_action_done_is_ticked(self):
        # Given: a task of four actions, none ticked.
        # When: the orchestrator keeps the first action done.
        self.ran(*self.state("--done", "T1.1"))
        # Then: that action alone is ticked.
        want = steered(part=plan(tasks=task(ticks="x   ")), next_step="3. Make the plan.")
        self.assertEqual(self.read(STEERING), want)

    def test_a_task_leaves_the_steering_once_all_its_actions_are_ticked(self):
        tasks = f"{task()}\n\n{task('T2', ticks='xxx ')}\n\n{task('T3', 'AC2')}"
        for done, left in (
            ("T1", f"{task('T2', ticks='xxx ')}\n\n{task('T3', 'AC2')}"),
            ("T2", f"{task()}\n\n{task('T3', 'AC2')}"),
            ("T3", f"{task()}\n\n{task('T2', ticks='xxx ')}"),
        ):
            with self.subTest(done=done):
                # Given: three tasks, T2 with three of its four actions ticked.
                self.session(steered(part=plan(tasks=tasks)))
                # When: the orchestrator keeps every action of one of them done, one again.
                argv = [a for k in (1, 2, 3, 4, 1) for a in ("--done", f"{done}.{k}")]
                self.ran(*self.state(*argv))
                # Then: that task is gone with the blank lines that parted it, the others as
                # they were.
                want = steered(part=plan(tasks=left), next_step="3. Make the plan.")
                self.assertEqual(self.read(STEERING), want)

    def test_the_last_task_done_takes_the_tasks_heading_with_it(self):
        # Given: a task whose first two actions are ticked.
        self.ran(*self.state("--done", "T1.1", "--done", "T1.2"))
        # When: the orchestrator keeps the last two done.
        self.ran(*self.state("--done", "T1.3", "--done", "T1.4"))
        # Then: the steering holds no task and no heading of the tasks.
        want = steered(part=plan(tasks=""), next_step="3. Make the plan.")
        self.assertEqual(self.read(STEERING), want)

    def test_an_action_the_steering_does_not_hold_stops_and_keeps_nothing(self):
        for done in ("T2.1", "T1.5", "T1.0", "T1", "1.1"):
            with self.subTest(done=done):
                # Given: a session whose one task has four actions.
                # When: the orchestrator keeps an action done that it does not hold.
                out = self.stopped(*self.state("--done", done))
                # Then: rn names it and says how an action is given, and keeps nothing.
                said = (
                    f"rn: the steering holds no action {done}; give each action done as"
                    " T<n>.<action>, of a task and an action it holds, such as T1.2"
                )
                self.assertEqual((said in out, self.read(STEERING)), (True, STEERED))

    def test_the_stage_moves_to_deliverable_once_no_task_is_left(self):
        # Given: a session at the build stage whose task has one action left.
        self.session(steered(part=plan(tasks=task(ticks="xxx ")), stage="build"))
        # When: the orchestrator keeps the last action done, moving the stage to deliverable.
        self.ran(*self.state("--done", "T1.4", "--stage", "deliverable"))
        # Then: the task is gone and the stage is deliverable.
        want = steered(part=plan(tasks=""), stage="deliverable", next_step="3. Make the plan.")
        self.assertEqual(self.read(STEERING), want)

    def test_the_stage_moving_to_deliverable_with_a_task_left_stops(self):
        # Given: a session at the build stage, with T2 left.
        tasks = task("T2", ticks="x ")
        self.session(steered(part=plan(tasks=tasks), stage="build"))
        # When: the orchestrator moves the stage to deliverable.
        out = self.stopped(*self.state("--stage", "deliverable"))
        # Then: rn names the task left, and keeps nothing.
        said = (
            "rn: T2 is still in the steering, and the finished work is checked once no task is;"
            " tick each action done with --done T<n>.<action>, then run this again"
        )
        want = steered(part=plan(tasks=tasks), stage="build")
        self.assertEqual((said in out, self.read(STEERING)), (True, want))

    def test_the_stage_moves_to_build_from_design_where_no_document_was_made(self):
        # Given: a session at the design stage, whose calls in it are on the plan and on the
        # learnings of the plan sign-off, and a call on t1.1 made in the plan stage.
        self.session(steered(stage="design"))
        self.call("0001", "t1.1", "plan", result={})
        self.call("0002", "learnings", "design", result={})
        self.call("0003", "plan", "design", result={})
        self.kept()
        # When: the orchestrator moves the stage to build.
        self.ran(*self.state("--stage", "build"))
        # Then: the stage is build, with no sign-off.
        want = steered(stage="build", next_step="3. Make the plan.")
        self.assertEqual(self.read(STEERING), want)

    def test_the_stage_moving_to_build_after_a_document_was_made_stops(self):
        # Given: a session at the design stage with a call on t1.1 and on a checklist made in it.
        self.session(steered(stage="design"))
        self.call("0001", "plan", "design", result={})
        self.call("0002", "t1.1", "design")
        self.call("0003", "checklist-code", "design", result={})
        self.call("0004", "t1.1", "design", result={})
        self.kept()
        # When: the orchestrator moves the stage to build.
        out = self.stopped(*self.state("--stage", "build"))
        # Then: rn names each work made, says they go to the design sign-off, and keeps nothing.
        said = (
            "rn: the design stage made t1.1 and checklist-code, which go to the design sign-off;"
            " show it with `rn.py proposal design`, and the user's approval there moves the"
            " session to build"
        )
        self.assertEqual((said in out, self.read(STEERING)), (True, steered(stage="design")))

    def test_the_stage_moves_to_deliverable_after_a_document_made_in_the_design_stage(self):
        # Given: a session at the build stage, no task left, with a call on t1.1 made in the design
        # stage.
        self.session(steered(part=plan(tasks=""), stage="build"))
        self.call("0001", "t1.1", "design", result={})
        self.kept()
        # When: the orchestrator moves the stage to deliverable.
        self.ran(*self.state("--stage", "deliverable"))
        # Then: the stage is deliverable.
        self.assertIn("stage: deliverable\n", self.read(STEERING))

    def test_the_stage_moves_to_finished_with_a_task_left(self):
        # Given: a session at the learnings stage, holding T1.
        self.session(steered(stage="learnings"))
        # When: the orchestrator moves the stage to finished.
        self.ran(*self.state("--stage", "finished"))
        # Then: the stage is finished.
        self.assertIn("stage: finished\n", self.read(STEERING))

    def test_the_stage_moved_to_finished_marks_the_pull_request_ready_first(self):
        # Given: a session at the learnings stage.
        self.session(steered(stage="learnings"))
        # When: the orchestrator moves the stage to finished.
        self.ran(*self.state("--stage", "finished"))
        # Then: gh marks the pull request ready.
        self.assertEqual(self.asked(), [["pr", "ready", PR]])

    def test_the_pull_request_not_marked_ready_keeps_nothing(self):
        # Given: a session at the learnings stage, and gh failing as it does when not logged in.
        self.session(steered(stage="learnings"))
        with mock.patch.dict(os.environ, {"GH_FAIL": "To get started, run: gh auth login"}):
            # When: the orchestrator moves the stage to finished.
            out = self.stopped(*self.state("--stage", "finished"))
        # Then: rn says what gh said and to run it again, and the session stays at learnings.
        said = (
            "failed: To get started, run: gh auth login; fix it as gh says, such as with"
            " `gh auth login`, then run `rn.py state --stage finished` again"
        )
        self.assertEqual((said in out, self.read(STEERING)), (True, steered(stage="learnings")))

    def test_the_actions_done_are_told_with_what_comes_next(self):
        # Given: a session whose T1 has four actions, none ticked.
        # When: the orchestrator keeps the first two done.
        out = self.ran(*self.state("--done", "T1.1", "--done", "T1.2"))
        # Then: rn gives the line telling the user what is done, and what comes next.
        self.assertEqual(
            out["tell"],
            "Done: T1.1, make part 1 of T1, `src/t1-1.py` as a code work; T1.2, make part 2 of T1,"
            " `src/t1-2.py` as a code work. Next: T1.3, make part 3 of T1, `src/t1-3.py` as a code"
            " work.",
        )

    def test_the_last_action_done_is_told_with_the_task_weighed_next(self):
        # Given: a session whose T1 has its first three actions ticked.
        self.session(steered(part=plan(tasks=task(ticks="xxx "))))
        # When: the orchestrator keeps the last done.
        out = self.ran(*self.state("--done", "T1.4"))
        # Then: rn tells it done, and that what T1 brought is weighed next.
        self.assertEqual(
            out["tell"],
            "Done: T1.4, make part 4 of T1, `src/t1-4.py` as a code work. Next: what T1 brought"
            " is weighed against the plan.",
        )

    def test_a_move_with_no_action_done_tells_nothing_and_marks_nothing_ready(self):
        # Given: a session.
        # When: the orchestrator keeps a move with no action done, and no stage moved.
        # Then: rn gives no line to tell, and asks gh nothing.
        self.assertEqual((self.ran(*self.state()), self.asked()), ({"kept": self.head()}, []))

    def test_what_comes_next_is_of_the_task_whose_action_is_done(self):
        for done, told in (
            ("T1.4", "Next: what T1 brought is weighed against the plan."),
            ("T2.1", "Next: T2.2, make part 2 of T2, `src/t2-2.py` as a code work."),
        ):
            with self.subTest(done=done):
                # Given: a session holding T1, its first three actions ticked, and T2.
                tasks = f"{task(ticks='xxx ')}\n\n{task('T2')}"
                self.session(steered(part=plan(tasks=tasks)))
                # When: the orchestrator keeps an action of one of them done.
                # Then: what comes next is of that task alone.
                self.assertTrue(self.ran(*self.state("--done", done))["tell"].endswith(told))

    def test_the_stage_moves_to_finished_from_learnings_and_ends_the_session(self):
        # Given: a session at the learnings stage, no task left.
        self.session(steered(part=plan(tasks=""), stage="learnings"))
        # When: the orchestrator moves the stage to finished.
        self.ran(*self.state("--stage", "finished"))
        # Then: the stage is finished, and no session is found after it.
        self.assertEqual(
            ("stage: finished\n" in self.read(STEERING), self.ran("session")["session"]),
            (True, None),
        )

    def test_the_stage_moving_from_another_stage_stops(self):
        for stage, to, start in (
            ("plan", "deliverable", "build"),
            ("build", "finished", "learnings"),
            ("plan", "build", "design"),
        ):
            with self.subTest(to=to):
                # Given: a session at a stage the move does not start from.
                self.session(steered(stage=stage))
                # When: the orchestrator moves the stage.
                out = self.stopped(*self.state("--stage", to))
                # Then: rn says where it moves from, and that the others move at the sign-offs.
                self.assertIn(
                    f"rn: the session is at the {stage} stage, and moves to {to} from the {start}"
                    " stage alone; the other stages move at the sign-offs, with `rn.py answer`",
                    out,
                )

    def test_a_stage_rn_does_not_move_to_stops(self):
        # Given: a session.
        # When: the orchestrator moves the stage to design.
        # Then: rn names the stages it moves to.
        self.assertIn(
            "argument --stage: invalid choice: 'design'",
            self.stopped(*self.state("--stage", "design")),
        )

    def test_a_steering_changed_by_hand_stops_and_keeps_nothing(self):
        # Given: a steering changed in the working tree.
        self.write(STEERING, STEERED.replace("Add login", "Add sign-in"))
        # When: the orchestrator keeps a move.
        out = self.stopped(*self.state())
        # Then: rn says it differs from what the last keep left and how to restore it, and keeps
        # nothing.
        said = (
            f"rn: {STEERING} differs from what the last keep left, and rn's scripts alone write"
            f" it; restore it with `git checkout HEAD -- {STEERING}`, then run this again"
        )
        self.assertEqual(
            (said in out, self.out("status", "--porcelain")), (True, f" M {STEERING}\n")
        )

    def test_a_steering_removed_stops(self):
        # Given: a steering removed in the working tree.
        os.remove(STEERING)
        # When: the orchestrator keeps a move.
        # Then: rn says it differs from what the last keep left.
        self.assertIn("differs from what the last keep left", self.stopped(*self.state()))

    def test_a_steering_committed_out_of_form_stops(self):
        # Given: a steering out of form, committed by hand.
        self.session(STEERED.replace("stage: plan", "stage: done"))
        # When: the orchestrator keeps a move.
        # Then: rn names the point and says to restore one rn kept from its history.
        self.assertIn(
            f"rn: {STEERING} as the last commit holds it is out of its form: line 4: expected stage"
            " to be plan, design, build, deliverable, learnings or finished, found done; rn keeps"
            f" none so, so restore the last one rn kept from `git log -p -- {STEERING}`, commit"
            " it, then run this again",
            self.stopped(*self.state()),
        )

    def test_a_session_without_a_steering_stops(self):
        # Given: a session folder holding a call and no steering.
        self.call("0001", "plan")
        os.remove(STEERING)
        self.kept()
        # When: the orchestrator keeps a move.
        # Then: rn says it is out of form, as there is none.
        self.assertIn(
            "out of its form: line 1: expected the front matter",
            self.stopped(*self.state()),
        )

    def test_a_move_the_steering_cannot_hold_stops_and_keeps_nothing(self):
        # A heading with its text, and one of its marks alone, which a property test found.
        for heading in ("## Notes", "#"):
            with self.subTest(heading=heading):
                # Given: a session kept.
                # When: the orchestrator keeps Next holding a heading.
                out = self.stopped("state", "--next", heading, "--message", "m")
                # Then: rn names the point and keeps nothing.
                said = (
                    "rn: the steering would be out of its form: line 34: expected only the headings"
                )
                self.assertEqual((said in out, self.read(STEERING)), (True, STEERED))

    def test_next_not_given_stays_as_it_was(self):
        # Given: a session.
        # When: the orchestrator keeps a move with no Next.
        self.ran("state", "--open", "Which login?", "--message", "m")
        # Then: Next stays as it was.
        self.assertEqual(self.read(STEERING), steered(opened="- Which login?"))

    def test_a_stage_moved_sets_next_to_the_step_it_leads_to(self):
        for stage, to, tasks in (
            ("design", "build", plan()),
            ("build", "deliverable", plan(tasks="")),
            ("learnings", "finished", plan()),
        ):
            with self.subTest(to=to):
                # Given: a session at the stage the move starts from.
                self.session(steered(part=tasks, stage=stage))
                # When: the orchestrator moves the stage, giving no Next.
                self.ran("state", "--stage", to, "--message", "m")
                # Then: Next is the step of /rn:up the stage leads to.
                self.assertIn(f"## Next\n\n{rn.STAGED[to]}\n", self.read(STEERING))

    def test_an_empty_value_stops(self):
        for argv, words in (
            (["state", "--next", "x", "--message", " "], "message"),
            (["state", "--next", " ", "--message", "m"], "next step"),
        ):
            with self.subTest(words=words):
                # Given: a session.
                # When: the orchestrator keeps a move with a value of blanks.
                # Then: rn says it is empty.
                self.assertIn(f"rn: the {words} is empty; give it in words", self.stopped(*argv))

    def test_keeping_without_a_session_stops(self):
        # Given: a branch holding no session.
        self.git("checkout", "-q", "-b", "other", "main")
        # When: the orchestrator keeps a move.
        # Then: rn says there is none, and how to start one.
        self.assertIn(
            "rn: the checked-out branch holds no session; start one with `rn.py start <slug>`",
            self.stopped(*self.state()),
        )

    def test_a_push_that_fails_stops_saying_how_to_push_again(self):
        # Given: a remote that cannot be reached.
        self.git("remote", "set-url", "origin", "../none.git")
        # When: the orchestrator keeps a move.
        # Then: rn says what git said and how to push once it is fixed.
        self.assertRegex(
            self.stopped(*self.state()),
            r"(?s)rn: git push -q -u origin HEAD failed: .*; fix it as git says, then push with"
            r" `git push -u origin HEAD`",
        )


class PutTest(RepoTest):
    """A part the orchestrator wrote, put back by `state --put`: the plan's into the steering, the
    learnings' after those kept."""

    def put(self, number: str = "0001") -> list[str]:
        """The arguments that put back the part of the call of the number."""
        return ["state", "--next", NEXT, "--put", number, "--message", "plan: made"]

    def test_the_plan_written_is_put_back_with_its_actions_ticked_as_they_were(self):
        # Given: a steering whose T1 has two actions ticked, and a call on the plan whose part, as
        # the orchestrator wrote it, changed T1's line, added an action, ticked the third, and
        # added T2.
        self.session(steered(part=plan(tasks=task(ticks="xx  "))))
        made = f"{task(ticks='  x  ').replace('part T1', 'page T1')}\n\n{task('T2', 'AC2')}"
        self.call("0001", "plan", part=plan(tasks=made) + "\n\n")
        # When: the orchestrator puts it back.
        self.ran(*self.put())
        # Then: the steering holds the part written, T1's first two actions ticked as they were
        # and the rest not.
        want = f"{task(ticks='xx   ').replace('part T1', 'page T1')}\n\n{task('T2', 'AC2')}"
        self.assertEqual(self.read(STEERING), steered(part=plan(tasks=want)))

    def test_a_part_whose_task_has_every_action_ticked_stops_and_keeps_nothing(self):
        # Given: a steering whose T1 has three of its four actions ticked, and a part leaving the
        # fourth out.
        before = steered(part=plan(tasks=task(ticks="xxx ")))
        self.session(before)
        self.call("0001", "plan", part=plan(tasks=task(ticks="   ")))
        # When: the orchestrator puts it back.
        out = self.stopped(*self.put())
        # Then: rn says a done task is in no steering, and keeps nothing.
        said = "its form: line 23: expected only tasks with an action not ticked" in out
        self.assertEqual((said, self.read(STEERING)), (True, before))

    def test_the_first_tasks_are_taken_from_t1(self):
        # Given: a steering that never held a task, and a call on the plan whose part holds T1.
        self.session(steered(part=plan(tasks="")))
        self.call("0001", "plan", part=plan())
        # When: the orchestrator puts it back.
        self.ran(*self.put())
        # Then: the steering holds it.
        self.assertEqual(self.read(STEERING), STEERED)

    def test_a_first_task_numbered_0_stops(self):
        # Given: a steering that never held a task, and a call on the plan whose part holds T0.
        before = steered(part=plan(tasks=""))
        self.session(before)
        self.call("0001", "plan", part=plan(tasks=task("T0")))
        # When: the orchestrator puts it back.
        out = self.stopped(*self.put())
        # Then: rn says to number each new task from T1, and keeps nothing.
        said = "each new task numbered from T1, then run this again" in out
        self.assertEqual((said, self.read(STEERING)), (True, before))

    def test_a_task_numbered_0_after_a_lower_heading_indented_under_a_task_stops(self):
        # Given: a steering that never held a task, and a call on the plan whose part holds T1,
        # a heading `### Later` indented under it, and T0.
        before = steered(part=plan(tasks=""))
        self.session(before)
        tasks = f"{task()}\n  ### Later\n\n{task('T0')}"
        self.call("0001", "plan", part=plan(tasks=tasks))
        # When: the orchestrator puts it back.
        out = self.stopped(*self.put())
        # Then: rn says to number each new task from T1, as the heading is a line of T1 and T0 a
        # task of the part, and keeps nothing.
        said = "each new task numbered from T1, then run this again" in out
        self.assertEqual((said, self.read(STEERING)), (True, before))

    def test_a_part_may_hold_the_tasks_held_and_any_above_every_task_held_before(self):
        # Given: a steering that held T1, T2 and T3, and now holds T2 alone, the others done, and a
        # call on the plan whose part holds T2 and T4.
        self.session(steered(part=plan(tasks="\n\n".join(task(t) for t in ("T1", "T2", "T3")))))
        self.session(steered(part=plan(tasks=task("T2"))))
        made = f"{task('T2')}\n\n{task('T4')}"
        self.call("0001", "plan", part=plan(tasks=made))
        # When: the orchestrator puts it back.
        self.ran(*self.put())
        # Then: the steering holds the part.
        self.assertEqual(self.read(STEERING), steered(part=plan(tasks=made)))

    def test_a_part_reusing_the_id_of_a_task_done_stops_and_keeps_nothing(self):
        for reused in ("T1", "T3"):
            with self.subTest(reused=reused):
                # Given: a steering that held T1, T2 and T3, and now holds T2 alone, the others
                # done, and a call on the plan whose part holds T2 and one of the IDs done.
                tasks = "\n\n".join(task(t) for t in ("T1", "T2", "T3"))
                self.session(steered(part=plan(tasks=tasks)))
                before = steered(part=plan(tasks=task("T2")))
                self.session(before)
                made = f"{task('T2')}\n\n{task(reused)}"
                self.call("0001", "plan", part=plan(tasks=made))
                self.kept()
                # When: the orchestrator puts it back.
                out = self.stopped(*self.put())
                # Then: rn names the ID, says to number each new task above those used, and
                # keeps nothing.
                said = (
                    f"rn: the part of the call 0001 holds {reused}, neither a task the steering"
                    " holds nor numbered above every task it has held, and an ID names one task"
                    " alone; nothing is kept: write the part again, each new task"
                    " numbered from T4, then run this again"
                )
                self.assertEqual((said in out, self.read(STEERING)), (True, before))

    def test_the_learnings_written_follow_those_kept_and_the_records_go(self):
        # Given: a learning kept, records shown in the git folder, and a call on the learnings
        # whose part holds two learnings.
        self.session()
        self.write(LEARNINGS, "- L1: Kept.\n")
        self.write(HISTORY, "x")
        made = "- L1: First.\n  Its words.\n- L2: Second.\n"
        self.call("0001", "learnings", part=made)
        self.kept()
        # When: the orchestrator puts it back.
        self.ran(*self.put())
        # Then: they follow the one kept in the session's learnings, numbered on from it, kept on
        # the remote; the steering holds none of them, and the records are removed.
        want = "- L1: Kept.\n- L2: First.\n  Its words.\n- L3: Second.\n"
        kept = (
            self.read(LEARNINGS),
            self.out("show", f"origin/work:{LEARNINGS}"),
            self.read(STEERING),
            os.path.exists(SHOWN),
        )
        self.assertEqual(kept, (want, want, STEERED, False))

    def test_the_first_learnings_are_numbered_from_one(self):
        # Given: a session with no learnings, and a call on the learnings whose part holds one
        # numbered otherwise.
        self.session()
        self.call("0001", "learnings", part="- L4: First.\n")
        # When: the orchestrator puts it back.
        self.ran(*self.put())
        # Then: the session's learnings are made, holding it as L1.
        self.assertEqual(self.read(LEARNINGS), "- L1: First.\n")

    def test_no_learning_made_leaves_no_learnings(self):
        # Given: a call on the learnings whose part the orchestrator left empty.
        self.session()
        self.call("0001", "learnings", part="")
        # When: the orchestrator puts it back.
        self.ran(*self.put())
        # Then: the session has no learnings, and the steering is as it was.
        self.assertEqual((os.path.exists(LEARNINGS), self.read(STEERING)), (False, STEERED))

    def test_learnings_put_with_a_move_the_steering_cannot_hold_stop_and_keep_nothing(self):
        # Given: a call on the learnings whose part holds one.
        self.session()
        self.call("0001", "learnings", part="- L1: First.\n")
        # When: the orchestrator puts it back with Next holding a heading.
        out = self.stopped("state", "--next", "## Notes", "--put", "0001", "--message", "m")
        # Then: rn names the point, and writes no learnings.
        said = "rn: the steering would be out of its form" in out
        self.assertEqual((said, os.path.exists(LEARNINGS)), (True, False))

    def test_learnings_out_of_form_stop_and_keep_nothing(self):
        # Given: records shown in the git folder, and a call on the learnings whose part holds one
        # with no ID.
        self.session()
        self.write(HISTORY, "x")
        self.call("0001", "learnings", part="- A slip.\n")
        self.kept()
        before = self.head()
        # When: the orchestrator puts it back.
        out = self.stopped(*self.put())
        # Then: rn names the point and says to write it again, keeping nothing and the records
        # left.
        said = (
            f"rn: {LEARNINGS} would be out of its form: line 1: expected a learning as `- L<n>:"
            " <what happened, with the words it rests on, and where it would make later work"
            " better>`, found `- A slip.`; nothing is kept: write the part it puts back again"
        )
        kept = (os.path.exists(LEARNINGS), self.head(), os.path.exists(SHOWN))
        self.assertEqual((said in out, kept), (True, (False, before, True)))

    def test_learnings_under_a_heading_stop(self):
        for heading in ("## Learnings", "# Learnings"):
            with self.subTest(heading=heading):
                # Given: a call on the learnings whose part holds one under a heading, which the
                # form of rn's learnings checklist has none of.
                self.session()
                self.call("0001", "learnings", part=f"{heading}\n- L1: First.\n")
                # When: the orchestrator puts it back.
                out = self.stopped(*self.put())
                # Then: rn names the heading as out of the learnings' form, and writes none.
                said = f"rn: {LEARNINGS} would be out of its form: line 1: expected a learning"
                self.assertEqual(
                    (said in out, f"found `{heading}`" in out, os.path.exists(LEARNINGS)),
                    (True, True, False),
                )

    def test_the_plan_put_back_leaves_the_records(self):
        # Given: records shown in the git folder, and a call on the plan.
        self.session()
        self.write(HISTORY, "x")
        self.call("0001", "plan", part=plan())
        # When: the orchestrator puts it back.
        self.ran(*self.put())
        # Then: the records are there.
        self.assertTrue(os.path.exists(HISTORY))

    def test_a_part_out_of_form_stops_and_keeps_nothing(self):
        # Given: a call on the plan whose part holds a heading of its own.
        self.session()
        self.call("0001", "plan", part=plan() + "\n\n## Notes\n")
        # When: the orchestrator puts it back.
        out = self.stopped(*self.put())
        # Then: rn names the point, says to write it again, and keeps nothing.
        said = "rn: the steering would be out of its form: line 32: expected only the headings"
        kept = (
            "nothing is kept: give what this move writes again so it holds, or write the part it"
            " puts back again"
        )
        self.assertEqual((said in out, kept in out, self.read(STEERING)), (True, True, STEERED))

    def test_a_part_with_an_action_out_of_form_stops_and_keeps_nothing(self):
        # Given: a call on the plan whose part holds an action out of its form.
        self.session()
        self.call("0001", "plan", part=plan(tasks=task().replace("[ ] 3.", "[ ] three.")))
        # When: the orchestrator puts it back.
        out = self.stopped(*self.put())
        # Then: rn names the action, and keeps nothing.
        said = "its form: line 29: expected action 3 of T1 in one of the forms" in out
        self.assertEqual((said, self.read(STEERING)), (True, STEERED))

    def test_a_call_not_there_stops(self):
        for number in ("0000", "0002"):
            with self.subTest(number=number):
                # Given: a session with the call 0001.
                self.session()
                self.call("0001", "plan", part=plan())
                # When: the orchestrator puts back the part of a call not there.
                # Then: rn says there is none, and what to give.
                self.assertIn(
                    f"rn: {CALLS} holds no call {number}; give the number of a call on plan or"
                    " learnings, such as 0001",
                    self.stopped(*self.put(number)),
                )

    def test_a_call_on_another_work_stops(self):
        # Given: a call on a task's work.
        self.session()
        self.call("0001", "t1.1", result={})
        # When: the orchestrator puts back its part.
        # Then: rn says it makes no part rn puts back.
        self.assertIn(
            "rn: the call 0001 is on t1.1, which makes no part rn puts back; give a call on plan or"
            " learnings",
            self.stopped(*self.put()),
        )

    def test_a_part_not_there_stops(self):
        for work, name in (("plan", "steering.md"), ("learnings", "learnings.md")):
            with self.subTest(work=work):
                # Given: a call on the work holding its decisions alone, its part not cut.
                self.session()
                self.call("0001", work, decisions=("Scope: the cart",))
                # When: the orchestrator puts back its part.
                # Then: rn says it is not there and how to have it made again.
                self.assertIn(
                    f"rn: {call_at('0001', name)}, the part the call 0001 makes, is not there;"
                    f" cut it with `rn.py ccs {work}`, write it, then run this again",
                    self.stopped(*self.put()),
                )


class CheckTest(RepoTest):
    """A part the orchestrator writes, checked by `check` as `state --put` holds it, before it is
    put back."""

    def test_a_part_in_form_holds_and_nothing_is_kept(self):
        for work, part in (("plan", plan()), ("learnings", "- L1: First.\n")):
            with self.subTest(work=work):
                # Given: a call on the work, its part in its form.
                self.session()
                self.call("0001", work, part=part)
                self.kept()
                before = self.head()
                # When: the orchestrator runs the check on it.
                held = self.ran("check", "0001")
                # Then: rn says it holds, and keeps nothing.
                self.assertEqual(
                    (held, self.head(), self.read(STEERING)), ({"held": "0001"}, before, STEERED)
                )

    def test_a_plan_out_of_form_stops_at_the_parts_own_line(self):
        # Given: a call on the plan whose part holds an action out of its form on its line 20.
        self.session()
        made = plan(tasks=task().replace("[ ] 3.", "[ ] three."))
        self.call("0001", "plan", part=made)
        self.kept()
        # When: the orchestrator runs the check on it.
        out = self.stopped("check", "0001")
        # Then: rn names the part, the point at that line, and what to do.
        said = (
            f"rn: {call_at('0001', 'steering.md')} would be out of its form: line 20: expected"
            " action 3 of T1 in one of the forms of rn's plan checklist's F-1"
        )
        found = "found `  - [ ] three. Make part 3 of T1"
        self.assertEqual(
            (
                said in out,
                found in out,
                out.rstrip().endswith("change it so it holds, then run this again"),
            ),
            (True, True, True),
        )

    def test_a_plan_whose_task_is_written_ticked_holds_as_put_keeps_the_ticks(self):
        # Given: a call on the plan whose part has every action of T1 ticked, as put keeps each
        # action ticked as the steering had it, none.
        self.session()
        self.call("0001", "plan", part=plan(tasks=task(ticks="xxxx")))
        self.kept()
        # When: the orchestrator runs the check on it.
        # Then: it holds.
        self.assertEqual(self.ran("check", "0001"), {"held": "0001"})

    def test_a_plan_reusing_the_id_of_a_task_done_stops(self):
        # Given: a steering that held T1 and T2, and now holds T2 alone, and a call on the plan
        # whose part holds T1.
        self.session(steered(part=plan(tasks=f"{task('T1')}\n\n{task('T2')}")))
        self.session(steered(part=plan(tasks=task("T2"))))
        self.call("0001", "plan", part=plan(tasks=task("T1")))
        self.kept()
        # When: the orchestrator runs the check on it.
        # Then: rn names the ID, as put does.
        self.assertIn(
            "rn: the part of the call 0001 holds T1, neither a task the steering holds nor"
            " numbered above every task it has held",
            self.stopped("check", "0001"),
        )

    def test_learnings_out_of_form_stop_at_the_parts_own_line(self):
        # Given: three learnings kept, and a call on the learnings whose part holds one with a
        # line under it, then a line with no ID on its line 3.
        self.session()
        self.write(LEARNINGS, "- L1: Kept.\n- L2: Kept too.\n- L3: Kept last.\n")
        self.call("0001", "learnings", part="- L1: First.\n  Its words.\n- A slip.\n")
        self.kept()
        # When: the orchestrator runs the check on it.
        out = self.stopped("check", "0001")
        # Then: rn names the part and the point at that line.
        self.assertIn(
            f"rn: {call_at('0001', 'learnings.md')} would be out of its form: line 3: expected a"
            " learning as `- L<n>: <what happened, with the words it rests on, and where it would"
            " make later work better>`, found `- A slip.`; change it so it holds, then run this"
            " again",
            out,
        )


if __name__ == "__main__":
    unittest.main()
