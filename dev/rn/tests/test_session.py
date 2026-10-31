"""The tests of the session: found from the branch, started with its draft pull request, each move
kept with `state`, the steering written with its Markdown, each task taken out once turn returned
it, and each part the orchestrator wrote put back into the record."""

from __future__ import annotations

import json
import os
import shutil
import unittest
from unittest import mock

from helpers import (
    CALLS,
    FOLDER,
    KIND,
    LEARNINGS,
    MARKDOWN,
    NEXT,
    PR,
    RECORD,
    REPOSITORY,
    SLUG,
    STEERED,
    STEERING,
    RepoTest,
    call_at,
    json_text,
    plan,
    session,
    steered,
    task,
)

# A plan with no task left.
NO_TASK = plan(tasks=())


class SessionTest(RepoTest):
    def test_no_session_where_the_branch_changed_none(self):
        # Given: a branch that changed nothing under .rn/.
        # When: the orchestrator asks for the session.
        # Then: rn says there is none, and no stage or sign-off.
        self.assertEqual(self.ran("session"), {"session": None, "stage": None, "signoff": None})

    def test_the_session_the_branch_changed_is_found_with_its_stage(self):
        # Given: a session's folder committed on the branch, at the architecture stage, no sign-off
        # waiting.
        self.session(steered(stage="architecture"))
        # When: the orchestrator asks for the session.
        # Then: rn gives its folder and its stage, and no sign-off waiting.
        want = {"session": FOLDER, "stage": "architecture", "signoff": None}
        self.assertEqual(self.ran("session"), want)

    def test_the_signoff_waiting_is_the_one_of_the_stage(self):
        # Given: a session whose steering waits at the sign-off of its stage, the ux.
        self.session(steered(stage="ux", waiting=True))
        # When: the orchestrator asks for the session.
        # Then: rn gives the ux sign-off waiting.
        self.assertEqual(self.ran("session")["signoff"], "ux")

    def test_a_finished_session_is_not_taken_up(self):
        # Given: a session on the branch whose steering is at the finished stage.
        self.session(steered(stage="finished"))
        # When: the orchestrator asks for the session.
        # Then: there is none.
        self.assertIsNone(self.ran("session")["session"])

    def test_a_steering_finished_and_not_yet_kept_is_still_the_session(self):
        # Given: a session whose steering is set finished in the working tree and not committed.
        self.session()
        self.write(STEERING, json_text(steered(stage="finished")))
        # When: the orchestrator asks for the session.
        # Then: it is found, as the last commit holds it at the goal stage.
        self.assertEqual(self.ran("session")["session"], FOLDER)

    def test_a_session_on_the_default_branch_is_not_taken_up(self):
        # Given: a session merged into the default branch, which the branch did not change.
        self.git("checkout", "-q", "main")
        self.write(f"{RECORD}/20261001-old/steering.json", json_text(STEERED))
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
        self.write(f"{old}/steering.json", json_text(STEERED))
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

    def test_a_steering_rn_cannot_read_is_not_finished(self):
        texts = ("", '{"status": "finished"', '["finished"]', '{"stage": "finished"}')
        for text in texts:
            with self.subTest(text=text):
                # Given: a session whose steering says it is finished nowhere rn reads it: no JSON,
                # or JSON holding no stage in the status.
                self.write(STEERING, text)
                self.kept()
                # When: the orchestrator asks for the session.
                # Then: it is found, with no stage, as nothing says it is over.
                want = {"session": FOLDER, "stage": None, "signoff": None}
                self.assertEqual(self.ran("session"), want)

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


# The steering a session starts with.
STARTED = steered(part=plan(goals=(), criteria=(), tasks=()), next_step=session.STARTED)


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
        options = [part for key, value in values.items() for part in (f"--{key}", value)]
        return ["start", slug, *options, "--message", message]

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
        # Then: the steering holds rn's version, the pull request, the title, the languages, no
        # plan yet, the goal stage, no sign-off waiting, Next the step that makes the plan and
        # nothing open, as kept on the remote, one key or value to a line.
        want = json_text(STARTED)
        self.assertEqual(
            (self.read(STEERING), self.out("show", f"origin/{SLUG}:{STEERING}")), (want, want)
        )

    def test_start_writes_the_steerings_markdown_for_the_user(self):
        # Given: a branch with no session.
        # When: the orchestrator starts one.
        self.ran(*self.start())
        # Then: the steering's Markdown is there beside it, as kept on the remote, with the title
        # and where the session stands.
        want = (
            "# Add login\n\n## Where it stands\n\nStage: goal.\n\n"
            f"Next: {session.STARTED}\n\nOpen:\n\nNone.\n"
        )
        self.assertEqual(
            (self.read(MARKDOWN), self.out("show", f"origin/{SLUG}:{MARKDOWN}")), (want, want)
        )

    def test_start_keeps_the_steering_with_the_message_before_the_pull_request(self):
        # Given: a branch with no session.
        # When: the orchestrator starts one with a message.
        self.ran(*self.start(message="Start add-login\n\nFrom the user's words."))
        # Then: the commit before the last holds the steering with no pull request yet, with the
        # message as given; the last keeps the pull request.
        kept = (
            json.loads(self.out("show", f"origin/{SLUG}~1:{STEERING}"))["session"]["pr"],
            self.out("log", "-1", "--format=%B", f"origin/{SLUG}~1"),
            self.out("log", "-1", "--format=%B", f"origin/{SLUG}"),
        )
        want = (None, "Start add-login\n\nFrom the user's words.\n\n", f"pr: {PR}\n\n")
        self.assertEqual(kept, want)

    def test_start_opens_the_draft_pull_request_linking_the_steerings_markdown(self):
        # Given: a branch with no session.
        # When: the orchestrator starts one.
        self.ran(*self.start())
        # Then: gh is asked the repository's URL, then opens a draft pull request of the branch
        # into the default branch, with the title and a body linking the steering's Markdown.
        link = f"[steering.md]({REPOSITORY}/blob/{SLUG}/{MARKDOWN})"
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
        kept = json.loads(self.out("show", f"origin/{SLUG}:{STEERING}"))
        # Then: rn says what gh said and to run start again, the steering kept with no pull
        # request; and start run again opens it and keeps it.
        again = self.ran(*self.start())
        self.assertEqual(
            (
                "failed: To get started, run: gh auth login; fix it as gh says, such as with"
                " `gh auth login`, then run `rn.py start` again with the same arguments" in out,
                kept["session"]["pr"],
                again,
                self.read(STEERING),
            ),
            (True, None, {"session": FOLDER, "branch": SLUG, "pr": PR}, json_text(STARTED)),
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
        self.write(STEERING, json_text(STEERED))
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

    def test_start_sets_each_language_as_given(self):
        # Given: a branch with no session.
        # When: the orchestrator starts one with Japanese written and English said.
        self.ran(*self.start(artifact_language="Japanese", conversation_language="English"))
        # Then: the steering holds each language as given.
        self.assertEqual(
            self.read_json(STEERING)["session"]["languages"],
            {"artifact": "Japanese", "conversation": "English"},
        )


class StateTest(RepoTest):
    """Where the session stands, rewritten at each move, and every change kept."""

    def setUp(self) -> None:
        super().setUp()
        self.session()

    def state(self, *more: str, message: str = "plan: the first point asked") -> list[str]:
        """The arguments that keep a move with Next given and the message, and more."""
        return ["state", "--next", "3. Make the plan.", *more, "--message", message]

    def returned(self, number: str = "0001", work: str = "t1") -> None:
        """A call on the work that turn returned, kept."""
        self.call(number, work, result={})
        self.kept()

    def test_next_and_open_are_replaced_whole_and_kept_on_the_remote(self):
        # Given: a session kept.
        # When: the orchestrator keeps a move with Next and two points open.
        self.ran(*self.state("--open", "Which login?", "--open", "Where to?"))
        # Then: the steering holds them, as the remote's branch does, with the message.
        want = json_text(
            steered(next_step="3. Make the plan.", opened=("Which login?", "Where to?"))
        )
        kept = (
            self.read(STEERING),
            self.out("show", f"origin/work:{STEERING}"),
            self.out("log", "-1", "--format=%B", "origin/work"),
        )
        self.assertEqual(kept, (want, want, "plan: the first point asked\n\n"))

    def test_the_steerings_markdown_is_written_with_it_at_each_move(self):
        # Given: a session kept.
        # When: the orchestrator keeps a move with a point open.
        self.ran(*self.state("--open", "Which login?"))
        # Then: the Markdown on the remote says the point open, and Next.
        found = self.out("show", f"origin/work:{MARKDOWN}")
        self.assertTrue(found.endswith("Next: 3. Make the plan.\n\nOpen:\n\n- Which login?\n"))

    def test_a_move_within_a_step_is_written_and_committed_as_the_step_ends(self):
        # Given: a session kept, and a decision written.
        self.ran("decide", "t1", "--title", "A", "--says", "B", "--message", "The decision")
        before = self.head()
        # When: the orchestrator keeps a move the step goes on after, then the move the step ends
        # with.
        out = self.ran(*self.state("--goes-on", "--open", "Which login?", message="Asked"))
        written = (out, self.read(STEERING), self.head())
        self.ran(*self.state(message="The step ends"))
        # Then: the first writes the steering and commits nothing, and the last commits the
        # step's every change on the remote, its message first, then each move's in the order
        # written.
        want = json_text(steered(next_step="3. Make the plan.", opened=("Which login?",)))
        self.assertEqual(
            (written, self.out("log", "-1", "--format=%B", "origin/work")),
            (
                ({"written": STEERING}, want, before),
                "The step ends\n\nThe decision\n\nAsked\n\n",
            ),
        )

    def test_a_steering_written_within_a_step_is_the_one_the_next_move_goes_on_from(self):
        # Given: a move within a step written, not committed.
        self.ran(*self.state("--goes-on", "--open", "Which login?"))
        # When: the orchestrator keeps the next move, giving no Next.
        self.ran("state", "--goes-on", "--message", "m")
        # Then: it goes on from the steering written, Next as it was written.
        self.assertEqual(self.read_json(STEERING)["status"]["next_step"], "3. Make the plan.")

    def test_a_move_within_a_step_putting_taking_out_or_moving_the_stage_stops(self):
        for more in (["--put", "0001"], ["--done", "T1"], ["--stage", "build"]):
            with self.subTest(more=more):
                # Given: a session kept.
                # When: the orchestrator keeps a move within a step that puts a part back, takes a
                # task out or moves the stage.
                out = self.stopped(*self.state("--goes-on", *more))
                # Then: rn says such a move ends its step, and writes nothing.
                said = (
                    "rn: a move within a step puts no part back, takes no task out and moves no"
                    " stage, as each ends the step; keep it without --goes-on"
                )
                self.assertEqual((said in out, self.read(STEERING)), (True, json_text(STEERED)))

    def test_a_steering_kept_in_another_layout_is_written_in_rns(self):
        # Given: a steering in form kept on one line, as a commit by hand left it.
        self.write(STEERING, json.dumps(STEERED))
        self.kept()
        # When: the orchestrator keeps a decision, a move that leaves the steering as it is.
        self.ran("decide", "t1", "--title", "A", "--says", "B", "--message", "m")
        # Then: the steering holds the same, one key or value to a line.
        self.assertEqual(self.read(STEERING), json_text(STEERED))

    def test_text_beyond_ascii_is_kept_as_it_is(self):
        # Given: a session kept.
        # When: the orchestrator keeps a point open in Japanese.
        self.ran(*self.state("--open", "どのログイン?"))
        # Then: the steering holds it as it is, as the user reads it on the pull request.
        self.assertIn('"どのログイン?"', self.read(STEERING))

    def test_no_point_open_is_kept_as_none(self):
        # Given: a session with a point open.
        self.ran(*self.state("--open", "Which login?"))
        # When: the orchestrator keeps a move with none open.
        self.ran(*self.state())
        # Then: no point is open.
        self.assertEqual(self.read_json(STEERING), steered(next_step="3. Make the plan."))

    def test_every_change_of_the_move_is_kept_and_the_commit_given(self):
        # Given: a file the move made.
        self.write("README.md", "# app, made\n")
        # When: the orchestrator keeps the move.
        out = self.ran(*self.state())
        # Then: the commit given holds the steering, its Markdown and the file, and nothing is
        # left to keep.
        changed = sorted(self.out("show", "--name-only", "--format=", "HEAD").split())
        left = self.out("status", "--porcelain")
        self.assertEqual(
            (out, changed, left),
            ({"kept": self.head()}, sorted([STEERING, MARKDOWN, "README.md"]), ""),
        )

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

    def test_a_task_turn_returned_leaves_the_plan(self):
        for done, left in (
            ("T1", ("T2", "T3")),
            ("T2", ("T1", "T3")),
            ("T3", ("T1", "T2")),
        ):
            with self.subTest(done=done):
                # Given: three tasks, the latest call on the one done returned by turn.
                self.session(steered(part=plan(tasks=[task(), task("T2"), task("T3", ("AC2",))])))
                self.returned(work=done.lower())
                # When: the orchestrator keeps it done.
                self.ran(*self.state("--done", done))
                # Then: that task is gone, the others as they were.
                kept = [t for t in (task(), task("T2"), task("T3", ("AC2",))) if t["id"] in left]
                want = steered(part=plan(tasks=kept), next_step="3. Make the plan.")
                self.assertEqual(self.read_json(STEERING), want)

    def test_the_last_task_done_leaves_no_task(self):
        # Given: a task turn returned.
        self.returned()
        # When: the orchestrator keeps it done.
        self.ran(*self.state("--done", "T1"))
        # Then: the plan holds no task, and the Markdown no heading of the tasks.
        self.assertEqual(
            (self.read_json(STEERING)["plan"]["tasks"], "## Tasks" in self.read(MARKDOWN)),
            ([], False),
        )

    def test_a_task_done_before_turn_returned_it_stops_and_keeps_nothing(self):
        cases = {
            "no call": (),
            "a call not returned": (("0001", None),),
            "returned, then called again": (("0001", {}), ("0002", None)),
        }
        for name, made in cases.items():
            with self.subTest(name=name):
                # Given: T1, whose latest call turn has not returned, or that has no call.
                self.session()
                for number, result in made:
                    self.call(number, "t1", result=result)
                self.kept()
                # When: the orchestrator keeps it done.
                out = self.stopped(*self.state("--done", "T1"))
                # Then: rn says turn has not returned its result, how to have it made, and keeps
                # nothing.
                said = (
                    "rn: turn has not returned T1's result, and a task leaves the plan only once"
                    " it has; have turn make it with the call `rn.py ccs t1` prints, read it at"
                    " each item's lines, then run this again; nothing is kept"
                )
                self.assertEqual((said in out, self.read(STEERING)), (True, json_text(STEERED)))

    def test_a_task_the_plan_does_not_hold_stops_and_keeps_nothing(self):
        for done in ("T2", "T0", "T1.1", "1", "t1"):
            with self.subTest(done=done):
                # Given: a session whose plan holds T1, returned by turn.
                self.returned()
                # When: the orchestrator keeps a task done that the plan does not hold.
                out = self.stopped(*self.state("--done", done))
                # Then: rn names it and says how a task is given, and keeps nothing.
                said = (
                    f"rn: the plan holds no task {done}; give each task done as T<n>, of a task"
                    " the plan holds, such as T1"
                )
                self.assertEqual((said in out, self.read(STEERING)), (True, json_text(STEERED)))

    def test_a_task_building_on_one_done_holds_once_it_is(self):
        # Given: T2 building on T1, and T1 returned by turn.
        self.session(steered(part=plan(tasks=[task(), task("T2", builds_on=("T1",))])))
        self.returned()
        # When: the orchestrator keeps T1 done.
        self.ran(*self.state("--done", "T1"))
        # Then: the plan holds T2 alone, still building on T1.
        self.assertEqual(self.read_json(STEERING)["plan"]["tasks"], [task("T2", builds_on=("T1",))])

    def test_the_stage_moves_to_deliverable_once_no_task_is_left(self):
        # Given: a session at the build stage whose task turn returned.
        self.session(steered(stage="build"))
        self.returned()
        # When: the orchestrator keeps it done, moving the stage to deliverable.
        self.ran(*self.state("--done", "T1", "--stage", "deliverable"))
        # Then: the task is gone and the stage is deliverable.
        want = steered(part=NO_TASK, stage="deliverable", next_step="3. Make the plan.")
        self.assertEqual(self.read_json(STEERING), want)

    def test_the_stage_moving_to_deliverable_with_a_task_left_stops(self):
        # Given: a session at the build stage, with T2 left.
        before = steered(part=plan(tasks=[task("T2")]), stage="build")
        self.session(before)
        # When: the orchestrator moves the stage to deliverable.
        out = self.stopped(*self.state("--stage", "deliverable"))
        # Then: rn names the task left, and keeps nothing.
        said = (
            "rn: T2 is still in the plan, and the finished work is checked once no task is; take"
            " each out with --done T<n> once turn has returned it, then run this again"
        )
        self.assertEqual((said in out, self.read(STEERING)), (True, json_text(before)))

    def test_the_stage_moves_on_from_ux_or_architecture_where_it_made_no_document(self):
        for stage, to, before in (("ux", "architecture", "goal"), ("architecture", "build", "ux")):
            with self.subTest(to=to):
                # Given: a session at the ux or the architecture stage, whose calls in it are on
                # the plan and on the learnings, with a call on t1 made in the stage before it.
                self.session(steered(stage=stage))
                self.call("0001", "t1", before, result={})
                self.call("0002", "learnings", stage, result={})
                self.call("0003", "plan", stage, result={})
                self.kept()
                # When: the orchestrator moves the stage on.
                self.ran(*self.state("--stage", to))
                # Then: the stage is the next one, with no sign-off.
                want = steered(stage=to, next_step="3. Make the plan.")
                self.assertEqual(self.read_json(STEERING), want)

    def test_the_stage_moving_on_after_a_document_was_made_in_it_stops(self):
        for stage, to in (("ux", "architecture"), ("architecture", "build")):
            with self.subTest(to=to):
                # Given: a session at the ux or the architecture stage with a call on t1 and on a
                # checklist made in it.
                self.session(steered(stage=stage))
                self.call("0001", "plan", stage, result={})
                self.call("0002", "t1", stage)
                self.call("0003", "checklist-code", stage, result={})
                self.call("0004", "t1", stage, result={})
                self.kept()
                # When: the orchestrator moves the stage on.
                out = self.stopped(*self.state("--stage", to))
                # Then: rn names each work made, says they go to the stage's sign-off, and keeps
                # nothing.
                said = (
                    f"rn: the {stage} stage made t1 and checklist-code, which go to the {stage}"
                    f" sign-off; show it with `rn.py proposal {stage}`, and the user's approval"
                    f" there moves the session to {to}"
                )
                self.assertEqual(
                    (said in out, self.read(STEERING)), (True, json_text(steered(stage=stage)))
                )

    def test_the_stage_moves_to_deliverable_after_a_document_made_before_the_build(self):
        # Given: a session at the build stage, no task left, with a call on t1 made in the
        # architecture stage.
        self.session(steered(part=NO_TASK, stage="build"))
        self.call("0001", "t1", "architecture", result={})
        self.kept()
        # When: the orchestrator moves the stage to deliverable.
        self.ran(*self.state("--stage", "deliverable"))
        # Then: the stage is deliverable.
        self.assertEqual(self.read_json(STEERING)["status"]["stage"], "deliverable")

    def test_the_stage_moves_to_finished_with_a_task_left(self):
        # Given: a session at the learnings stage, holding T1.
        self.session(steered(stage="learnings"))
        # When: the orchestrator moves the stage to finished.
        self.ran(*self.state("--stage", "finished"))
        # Then: the stage is finished.
        self.assertEqual(self.read_json(STEERING)["status"]["stage"], "finished")

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
        self.assertEqual(
            (said in out, self.read(STEERING)), (True, json_text(steered(stage="learnings")))
        )

    def test_the_tasks_done_are_told_with_what_comes_next(self):
        # Given: a session holding T1 and T2, both returned by turn.
        self.session(steered(part=plan(tasks=[task(), task("T2")])))
        self.call("0001", "t1", result={})
        self.returned("0002", "t2")
        # When: the orchestrator keeps both done.
        out = self.ran(*self.state("--done", "T1", "--done", "T2"))
        # Then: rn gives the line telling the user what is done, and what comes next.
        self.assertEqual(
            out["tell"],
            "Done: T1, the part T1; T2, the part T2. Next: what T2 brought is weighed against the"
            " plan.",
        )

    def test_a_move_with_no_task_done_tells_nothing_and_marks_nothing_ready(self):
        # Given: a session.
        # When: the orchestrator keeps a move with no task done, and no stage moved.
        # Then: rn gives no line to tell, and asks gh nothing.
        self.assertEqual((self.ran(*self.state()), self.asked()), ({"kept": self.head()}, []))

    def test_the_stage_moves_to_finished_from_learnings_and_ends_the_session(self):
        # Given: a session at the learnings stage, no task left.
        self.session(steered(part=NO_TASK, stage="learnings"))
        # When: the orchestrator moves the stage to finished.
        self.ran(*self.state("--stage", "finished"))
        # Then: the stage is finished, and no session is found after it.
        self.assertEqual(
            (self.read_json(STEERING)["status"]["stage"], self.ran("session")["session"]),
            ("finished", None),
        )

    def test_the_stage_moving_from_another_stage_stops(self):
        for stage, to, start in (
            ("goal", "deliverable", "build"),
            ("build", "finished", "learnings"),
            ("goal", "build", "architecture"),
            ("goal", "architecture", "ux"),
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
        # When: the orchestrator moves the stage to ux, which the goal sign-off moves it to.
        # Then: rn names the stages it moves to.
        self.assertIn(
            "argument --stage: invalid choice: 'ux'",
            self.stopped(*self.state("--stage", "ux")),
        )

    def test_a_steering_changed_by_hand_stops_and_keeps_nothing(self):
        # Given: a steering changed in the working tree.
        self.write(STEERING, json_text(steered(next_step="Elsewhere.")))
        # When: the orchestrator keeps a move.
        out = self.stopped(*self.state())
        # Then: rn says it differs from what the last keep left and how to restore it, and keeps
        # nothing.
        said = (
            f"rn: {STEERING} differs from what the last keep left, and rn's scripts alone write"
            f" it; restore it with `git checkout -- {STEERING}`, then run this again"
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
        self.session(steered(stage="done"))
        # When: the orchestrator keeps a move.
        # Then: rn names the point and says to restore one rn kept from its history.
        self.assertIn(
            f"rn: {STEERING} as the last keep left it is out of its form: $.status.stage: expected"
            ' one of "goal", "ux", "architecture", "build", "deliverable", "learnings",'
            ' "finished", found "done"; rn keeps none so, so restore the last one rn kept with'
            f" `git checkout <commit> -- {STEERING}`, the commit found with `git log --"
            f" {STEERING}`, then run this again, which keeps it",
            self.stopped(*self.state()),
        )

    def test_a_steering_committed_building_on_a_task_not_done_stops(self):
        # Given: a steering committed by hand whose T2 builds on T1, which the plan no longer
        # holds and turn never returned.
        self.session(steered(part=plan(tasks=[task("T2", builds_on=("T1",))])))
        # When: the orchestrator keeps a move.
        # Then: rn names the point, as T1 is no task done.
        self.assertIn(
            "out of its form: $.plan.tasks[0].builds_on: expected only tasks or tasks done the"
            " plan holds, found T1",
            self.stopped(*self.state()),
        )

    def test_a_steering_committed_that_is_no_json_stops(self):
        for text in ("", "{", '["status"]'):
            with self.subTest(text=text):
                # Given: a steering committed by hand that is no JSON, or none rn reads.
                self.write(STEERING, text)
                self.kept()
                # When: the orchestrator keeps a move.
                # Then: rn says it is out of its form.
                self.assertIn(
                    f"{STEERING} as the last keep left it is out of its form: $:",
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
            "out of its form: $: expected the steering as JSON, found none",
            self.stopped(*self.state()),
        )

    def test_a_move_the_steering_cannot_hold_stops_and_keeps_nothing(self):
        for argv, point in (
            (["--open", " "], '$.status.open_questions[0]: expected some words, found " "'),
            (["--open", "a", "--open", ""], "$.status.open_questions[1]: expected some words"),
        ):
            with self.subTest(argv=argv):
                # Given: a session kept.
                # When: the orchestrator keeps a move with a point open of no words.
                out = self.stopped(*self.state(*argv))
                # Then: rn names the point and keeps nothing.
                said = f"rn: the steering would be out of its form: {point}"
                self.assertEqual((said in out, self.read(STEERING)), (True, json_text(STEERED)))

    def test_next_not_given_stays_as_it_was(self):
        # Given: a session.
        # When: the orchestrator keeps a move with no Next.
        self.ran("state", "--open", "Which login?", "--message", "m")
        # Then: Next stays as it was.
        self.assertEqual(self.read_json(STEERING), steered(opened=("Which login?",)))

    def test_a_stage_moved_sets_next_to_the_step_it_leads_to(self):
        for stage, to, part in (
            ("ux", "architecture", plan()),
            ("architecture", "build", plan()),
            ("build", "deliverable", NO_TASK),
            ("learnings", "finished", plan()),
        ):
            with self.subTest(to=to):
                # Given: a session at the stage the move starts from.
                self.session(steered(part=part, stage=stage))
                # When: the orchestrator moves the stage, giving no Next.
                self.ran("state", "--stage", to, "--message", "m")
                # Then: Next is the step of /rn:up the stage leads to.
                self.assertEqual(
                    self.read_json(STEERING)["status"]["next_step"], session.STAGED[to]
                )

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
            r"(?s)rn: git push -q -u origin HEAD failed: .*; what is committed is not pushed:"
            r" fix it as git says, then run this again, which pushes it",
        )


class PutTest(RepoTest):
    """A part the orchestrator wrote, put back by `state --put`: the plan's into the steering, the
    learnings' as the session's learnings."""

    def put(self, number: str = "0001") -> list[str]:
        """The arguments that put back the part of the call of the number."""
        return ["state", "--next", NEXT, "--put", number, "--message", "plan: made"]

    def test_the_plan_written_is_put_back_as_the_steerings_plan(self):
        # Given: a steering holding T1, and a call on the plan whose part changes T1 and adds T2.
        self.session()
        changed = {**task(), "what": "The page T1."}
        made = plan(tasks=[changed, task("T2", ("AC2",))])
        self.call("0001", "plan", part=made)
        # When: the orchestrator puts it back.
        self.ran(*self.put())
        # Then: the steering's plan is the part written.
        self.assertEqual(self.read_json(STEERING), steered(part=made))

    def test_the_first_tasks_are_taken_from_t1(self):
        # Given: a steering that never held a task, and a call on the plan whose part holds T1.
        self.session(steered(part=NO_TASK))
        self.call("0001", "plan", part=plan())
        # When: the orchestrator puts it back.
        self.ran(*self.put())
        # Then: the steering holds it.
        self.assertEqual(self.read_json(STEERING), STEERED)

    def test_a_part_may_hold_the_tasks_held_and_any_above_every_task_held_before(self):
        # Given: a steering that held T1, T2 and T3, and now holds T2 alone, the others done, and a
        # call on the plan whose part holds T2 and T4.
        self.session(steered(part=plan(tasks=[task(t) for t in ("T1", "T2", "T3")])))
        self.session(steered(part=plan(tasks=[task("T2")])))
        made = plan(tasks=[task("T2"), task("T4")])
        self.call("0001", "plan", part=made)
        # When: the orchestrator puts it back.
        self.ran(*self.put())
        # Then: the steering holds the part.
        self.assertEqual(self.read_json(STEERING), steered(part=made))

    def test_a_part_may_put_back_a_task_done_to_make_its_result_again(self):
        # Given: a steering that held T1 and T2, and now holds T2 alone, T1 done as turn returned
        # its result, and a call on the plan whose part puts T1 back.
        self.session(steered(part=plan(tasks=[task("T1"), task("T2")])))
        self.session(steered(part=plan(tasks=[task("T2")])))
        self.call("0001", "t1", "build", result={})
        made = plan(tasks=[task("T1"), task("T2")])
        self.call("0002", "plan", "build", part=made)
        # When: the orchestrator puts it back.
        self.ran(*self.put("0002"))
        # Then: the steering holds the part, so T1's result is made again on its own calls.
        self.assertEqual(self.read_json(STEERING), steered(part=made))

    def test_a_part_reusing_the_id_of_a_task_left_unmade_stops_and_keeps_nothing(self):
        for reused in ("T1", "T3"):
            with self.subTest(reused=reused):
                # Given: a steering that held T1, T2 and T3, and now holds T2 alone, the others
                # left with no call, and a call on the plan whose part holds T2 and one of them.
                self.session(steered(part=plan(tasks=[task(t) for t in ("T1", "T2", "T3")])))
                before = steered(part=plan(tasks=[task("T2")]))
                self.session(before)
                self.call("0001", "plan", part=plan(tasks=[task("T2"), task(reused)]))
                self.kept()
                # When: the orchestrator puts it back.
                out = self.stopped(*self.put())
                # Then: rn names the ID, says to number each new task above those used, and
                # keeps nothing.
                said = (
                    f"rn: the part of the call 0001 holds {reused}, neither a task the steering"
                    " holds, nor one done, nor numbered above every task it has held, and an ID"
                    " names one task alone; nothing is kept: write the part again, each new task"
                    " numbered from T4, then run this again"
                )
                self.assertEqual((said in out, self.read(STEERING)), (True, json_text(before)))

    def test_a_part_holding_a_new_task_numbered_below_one_held_stops_and_keeps_nothing(self):
        # Given: a steering that held T1 and T3 and never T2, and now holds T3 alone, T1 left with
        # no call, and a call on the plan whose part holds T3 and T2.
        self.session(steered(part=plan(tasks=[task("T1"), task("T3")])))
        before = steered(part=plan(tasks=[task("T3")]))
        self.session(before)
        self.call("0001", "plan", part=plan(tasks=[task("T3"), task("T2")]))
        self.kept()
        # When: the orchestrator puts it back.
        out = self.stopped(*self.put())
        # Then: rn names T2, as it is numbered below T3, not above every task held, says to number
        # each new task from T4, and keeps nothing.
        said = (
            "rn: the part of the call 0001 holds T2, neither a task the steering holds, nor one"
            " done, nor numbered above every task it has held, and an ID names one task alone;"
            " nothing is kept: write the part again, each new task numbered from T4, then run"
            " this again"
        )
        self.assertEqual((said in out, self.read(STEERING)), (True, json_text(before)))

    def test_a_part_leaving_out_a_task_turn_has_not_returned_stops_and_keeps_nothing(self):
        # Given: T1, whose latest call turn has not returned, and a part on the plan leaving it
        # out.
        self.session()
        self.call("0001", "t1")
        self.call("0002", "plan", part=NO_TASK)
        self.kept()
        # When: the orchestrator puts it back.
        out = self.stopped(*self.put("0002"))
        # Then: rn says T1 is left out before turn returned it, and keeps nothing.
        said = (
            "rn: the part of the call 0002 leaves out T1, and turn has not returned its result:"
            f" {call_at('0001', 'result.json')} is not there; keep T1 in the part until turn"
            " returns the call `rn.py ccs t1` prints, then run this again; nothing is kept"
        )
        self.assertEqual((said in out, self.read(STEERING)), (True, json_text(STEERED)))

    def test_a_part_leaving_out_a_task_never_called_or_returned_is_put_back(self):
        for name, made in (("never called", ()), ("returned", (("0002", {}),))):
            with self.subTest(name=name):
                # Given: T1, never called or returned by turn, and a part on the plan leaving it
                # out, as no longer needed or done.
                self.session()
                self.call("0001", "plan", part=NO_TASK)
                for number, result in made:
                    self.call(number, "t1", result=result)
                self.kept()
                # When: the orchestrator puts it back.
                self.ran(*self.put())
                # Then: the plan holds no task.
                self.assertEqual(self.read_json(STEERING)["plan"], NO_TASK)

    def test_the_learnings_written_are_the_sessions_learnings(self):
        # Given: a call on the learnings whose part holds two learnings.
        self.session()
        made = "- L1: First.\n  Its words.\n- L2: Second.\n"
        self.call("0001", "learnings", part=made)
        self.kept()
        # When: the orchestrator puts it back.
        self.ran(*self.put())
        # Then: they are the session's learnings as written, kept on the remote; the steering
        # holds none of them.
        kept = (
            self.read(LEARNINGS),
            self.out("show", f"origin/work:{LEARNINGS}"),
            self.read(STEERING),
        )
        self.assertEqual(kept, (made, made, json_text(STEERED)))

    def test_no_learning_made_leaves_no_learnings(self):
        # Given: a call on the learnings whose part the orchestrator left empty.
        self.session()
        self.call("0001", "learnings", part="")
        # When: the orchestrator puts it back.
        self.ran(*self.put())
        # Then: the session has no learnings, and the steering is as it was.
        self.assertEqual(
            (os.path.exists(LEARNINGS), self.read(STEERING)), (False, json_text(STEERED))
        )

    def test_learnings_put_with_a_move_the_steering_cannot_hold_stop_and_keep_nothing(self):
        # Given: a call on the learnings whose part holds one.
        self.session()
        self.call("0001", "learnings", part="- L1: First.\n")
        # When: the orchestrator puts it back with a point open of no words.
        argv = ["state", "--open", " ", "--put", "0001", "--message", "m"]
        out = self.stopped(*argv)
        # Then: rn names the point, and writes no learnings.
        said = "rn: the steering would be out of its form" in out
        self.assertEqual((said, os.path.exists(LEARNINGS)), (True, False))

    def test_learnings_out_of_form_stop_and_keep_nothing(self):
        # Given: a call on the learnings whose part holds one with no ID.
        self.session()
        self.call("0001", "learnings", part="- A slip.\n")
        self.kept()
        before = self.head()
        # When: the orchestrator puts it back.
        out = self.stopped(*self.put())
        # Then: rn names the point and says to write it again, keeping nothing.
        said = (
            f"rn: {LEARNINGS} would be out of its form: line 1: expected a learning as `- L<n>:"
            " <what happened, with the words it rests on, and where it would make later work"
            " better>`, found `- A slip.`; nothing is kept: write the part it puts back again"
        )
        kept = (os.path.exists(LEARNINGS), self.head())
        self.assertEqual((said in out, kept), (True, (False, before)))

    def test_learnings_holding_an_id_twice_stop(self):
        # Given: a call on the learnings whose part holds L1, then L1 again on its line 3.
        self.session()
        self.call("0001", "learnings", part="- L1: First.\n\n- L1: Again.\n")
        # When: the orchestrator puts it back.
        # Then: rn names the ID given again, at its line.
        self.assertIn(
            f"rn: {LEARNINGS} would be out of its form: line 3: expected each ID once, found L1"
            " again",
            self.stopped(*self.put()),
        )

    def test_learnings_end_with_their_last_line_of_words(self):
        # Given: a call on the learnings whose part ends with blank lines.
        self.session()
        self.call("0001", "learnings", part="- L1: First.\n\n\n")
        # When: the orchestrator puts it back.
        self.ran(*self.put())
        # Then: the learnings end with the learning.
        self.assertEqual(self.read(LEARNINGS), "- L1: First.\n")

    def test_a_line_indented_before_any_learning_stops(self):
        # Given: a call on the learnings whose part opens with a line indented, under no learning.
        self.session()
        self.call("0001", "learnings", part="  Its words.\n- L1: First.\n")
        # When: the orchestrator puts it back.
        # Then: rn names the line as under no learning.
        self.assertIn(
            f"rn: {LEARNINGS} would be out of its form: line 1: expected a learning as",
            self.stopped(*self.put()),
        )

    def test_learnings_after_a_blank_line_are_taken(self):
        # Given: a call on the learnings whose part opens with a blank line, then holds two.
        self.session()
        self.call("0001", "learnings", part="\n- L1: First.\n- L2: Second.\n")
        self.kept()
        # When: the orchestrator puts it back, then asks for the learnings.
        self.ran(*self.put())
        # Then: both are the session's learnings, the blank line gone.
        self.assertEqual(
            (self.read(LEARNINGS), self.ran("learnings")),
            ("- L1: First.\n- L2: Second.\n", {"learnings": {"L1": "First.", "L2": "Second."}}),
        )

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

    def test_a_part_out_of_form_stops_at_its_place_in_the_part_and_keeps_nothing(self):
        # Given: a call on the plan whose task serves a criterion the plan does not hold.
        self.session()
        self.call("0001", "plan", part=plan(tasks=[task(serves=("AC3",))]))
        # When: the orchestrator puts it back.
        out = self.stopped(*self.put())
        # Then: rn names the part and the point at its place in it, and keeps nothing.
        said = (
            f"rn: {call_at('0001', 'plan.json')} would be out of its form:"
            " $.tasks[0].completion_criteria[0].contributes_to: expected only acceptance criteria"
            " the plan holds, found AC3; change it so it holds, then run this again"
        )
        self.assertEqual((said in out, self.read(STEERING)), (True, json_text(STEERED)))

    def test_a_part_that_is_no_json_stops(self):
        # Given: a call on the plan whose part is written as Markdown.
        self.session()
        self.call("0001", "plan")
        self.write(call_at("0001", "plan.json"), "# Add login\n")
        # When: the orchestrator puts it back.
        # Then: rn says it is no JSON and to write the plan there as JSON.
        self.assertIn(
            f"rn: {call_at('0001', 'plan.json')} is no JSON; write the plan there as JSON in the"
            " steering's form, as rn.py cut it, then run this again",
            self.stopped(*self.put()),
        )

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
        # Given: a call on a task's result.
        self.session()
        self.call("0001", "t1", result={})
        # When: the orchestrator puts back its part.
        # Then: rn says it makes no part rn puts back.
        self.assertIn(
            "rn: the call 0001 is on t1, which makes no part rn puts back; give a call on plan or"
            " learnings",
            self.stopped(*self.put()),
        )

    def test_a_part_not_there_stops(self):
        for work, name in (("plan", "plan.json"), ("learnings", "learnings.md")):
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

    def test_a_plan_in_form_gives_its_markdown_and_nothing_is_kept(self):
        # Given: a call on the plan, its part in its form, changing T1's words.
        self.session()
        self.call("0001", "plan", part=plan(tasks=[{**task(), "what": "The page T1."}]))
        self.kept()
        before = self.head()
        # When: the orchestrator runs the check on it.
        shown = self.printed("check", "0001")
        # Then: rn prints the Markdown the steering would show with it, and keeps nothing.
        self.assertEqual(
            (
                shown.startswith("# Add login\n\n## Goals\n\n- G1: Users sign in\n"),
                "- T1: The page T1. Builds on none.\n" in shown,
                self.head(),
                self.read(STEERING),
            ),
            (True, True, before, json_text(STEERED)),
        )

    def test_learnings_in_form_hold_and_nothing_is_kept(self):
        # Given: a call on the learnings, its part in its form.
        self.session()
        self.call("0001", "learnings", part="- L1: First.\n")
        self.kept()
        before = self.head()
        # When: the orchestrator runs the check on it.
        held = self.ran("check", "0001")
        # Then: rn says it holds, and keeps nothing.
        self.assertEqual(
            (held, self.head(), self.read(STEERING)),
            ({"held": "0001"}, before, json_text(STEERED)),
        )

    def test_a_plan_out_of_form_stops_at_its_place_in_the_part(self):
        # Given: a call on the plan whose second task's ID is out of its form.
        self.session()
        self.call("0001", "plan", part=plan(tasks=[task(), task("Two")]))
        self.kept()
        # When: the orchestrator runs the check on it.
        # Then: rn names the part, the point at its place, and what to do.
        self.assertIn(
            f"rn: {call_at('0001', 'plan.json')} would be out of its form: $.tasks[1].id:"
            " expected T<n>, n from 1, found Two; change it so it holds, then run this again",
            self.stopped("check", "0001"),
        )

    def test_a_plan_reusing_the_id_of_a_task_left_unmade_stops(self):
        # Given: a steering that held T1 and T2, and now holds T2 alone, T1 with no call, and a
        # call on the plan whose part holds T1.
        self.session(steered(part=plan(tasks=[task("T1"), task("T2")])))
        self.session(steered(part=plan(tasks=[task("T2")])))
        self.call("0001", "plan", part=plan(tasks=[task("T1")]))
        self.kept()
        # When: the orchestrator runs the check on it.
        # Then: rn names the ID, as put does.
        self.assertIn(
            "rn: the part of the call 0001 holds T1, neither a task the steering holds, nor one"
            " done, nor numbered above every task it has held",
            self.stopped("check", "0001"),
        )

    def test_learnings_out_of_form_stop_at_the_parts_own_line(self):
        # Given: a call on the learnings whose part holds one with a line under it, then a line
        # with no ID on its line 3.
        self.session()
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


class LearningsTest(RepoTest):
    def test_learnings_gives_the_sessions_by_id_each_as_one_line(self):
        # Given: the session's learnings, the first over two lines.
        self.session()
        self.write(LEARNINGS, "- L1: A slip.\n  Its words.\n- L2: Another.\n  Its own.\n")
        self.kept()
        # When: the orchestrator asks for the learnings.
        # Then: rn gives the session's by ID, each as one line, and nothing else.
        self.assertEqual(
            self.ran("learnings"),
            {"learnings": {"L1": "A slip. Its words.", "L2": "Another. Its own."}},
        )

    def test_learnings_are_printed_with_text_beyond_ascii_as_it_is(self):
        # Given: the session's learnings, one in Japanese.
        self.session()
        self.write(LEARNINGS, "- L1: 遅い。\n")
        self.kept()
        # When: the orchestrator asks for the learnings.
        # Then: rn prints it as it is, for the orchestrator to read.
        self.assertIn('"L1": "遅い。"', self.printed("learnings"))

    def test_learnings_without_a_session_stop(self):
        # Given: a branch holding no session.
        # When: the orchestrator asks for the learnings.
        # Then: rn says there is none.
        self.assertIn("holds no session", self.stopped("learnings"))


if __name__ == "__main__":
    unittest.main()
