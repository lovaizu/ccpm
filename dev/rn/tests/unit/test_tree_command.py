"""The unit cases of tree/command.py, tree.py's command line, through `main`: the exit code, what
it prints, and what it does for each command, on a repository of the test's own with the double
of gh. The commands' own decisions lie in the modules each case of theirs names; these cases try
what the command line adds: its arguments, its output, and its exit codes."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
from rn_example import HINTS, HINTS_NAME, LESSON, TYPED, TYPED_NAME, WORDS, git, write
from rn_parts import environ, repository, schema_tree
from tree.command import USAGE, main

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")


class Repo:
    """A repository of the test's own, its environment, and the run that `begin` made in it."""

    def __init__(self, base: str):
        self.root, self.remote = repository(base)
        self.env = environ(base)
        self.base = base
        self.worktree = ""

    def run(self, *argv: str, cwd: str = "") -> tuple[int, str, str]:
        """tree.py with the arguments, in the run's worktree once begun, else at the root."""
        return main(list(argv), self.env, cwd or self.worktree or self.root)

    def begin(self) -> str:
        code, out, err = self.run("begin", WORDS)
        assert code == 0, err
        self.worktree = out.strip()
        return os.path.join(".rn", os.path.basename(self.worktree).removeprefix("rn-"))


@pytest.fixture
def repo(tmp_path: Any) -> Repo:
    return Repo(str(tmp_path))


@pytest.mark.parametrize(
    "argv", [[], ["start"], ["begin"], ["cut", "x"], ["record", "r", "generator", "1", "Read."]]
)
@pytest.mark.supports(
    "test_up_with_a_request_makes_the_runs_worktree_on_its_branch_with_its_folder"
)
def test_arguments_of_no_command_give_2_with_the_usage(repo: Repo, argv: list[str]):
    """Given no argument, an unknown command, or a command short of its arguments
    When tree.py runs
    Then it gives 2 with the usage"""
    assert repo.run(*argv) == (2, "", USAGE)


@pytest.mark.supports(
    "test_up_with_a_request_makes_the_runs_worktree_on_its_branch_with_its_folder"
)
def test_begin_gives_0_and_prints_the_worktree(repo: Repo):
    """Given the repository
    When `tree.py begin type hints for invoicer` runs
    Then it gives 0 and prints the worktree's path, which git lists"""
    code, out, _ = repo.run("begin", WORDS)
    assert code == 0 and out.strip() in git(repo.root, "worktree", "list")


@pytest.mark.supports("test_begin_refuses_a_run_that_already_has_its_worktree")
def test_begin_of_a_run_there_is_gives_1(repo: Repo):
    """Given the walkthrough's run begun
    When it's begun again
    Then tree.py gives 1, naming the worktree"""
    repo.begin()
    code, _, err = repo.run("begin", WORDS, cwd=repo.root)
    assert code == 1 and repo.worktree in err


@pytest.mark.supports("test_runs_with_no_run_left_lists_none")
def test_runs_prints_the_runs_as_json(repo: Repo):
    """Given the repository with no run
    When `tree.py runs` runs
    Then it gives 0 and prints `{"runs": []}`"""
    code, out, _ = repo.run("runs")
    assert code == 0 and json.loads(out) == {"runs": []}


@pytest.mark.supports("test_the_tree_keeper_starts_with_its_cut_of_the_run_alone")
def test_cut_prints_the_run_values_as_one_json_line(repo: Repo):
    """Given the walkthrough's run
    When `tree.py cut <run> tree-keeper` runs
    Then it gives 0 and prints one JSON line of run values naming the run"""
    run = repo.begin()
    code, out, _ = repo.run("cut", run, "tree-keeper")
    assert code == 0 and len(out.strip().splitlines()) == 1 and json.loads(out)["run"] == run


@pytest.mark.supports(
    "test_the_goal_and_the_plan_written_commit_the_design_tree_with_the_point_open"
)
def test_write_prints_changed_touched_and_doing_and_commits_with_the_ground(repo: Repo):
    """Given the walkthrough's run, and a design tree written by the tree-keeper
    When `tree.py write` runs on it with a ground
    Then it gives 0 and prints `changed`, `touched`, and `doing`, and the last commit's message is
    the ground"""
    run = repo.begin()
    path = write(repo.base, "design-tree.json", json.dumps(schema_tree()))
    code, out, _ = repo.run("write", run, path, "The user answered each file.")
    assert code == 0 and set(json.loads(out)) == {"changed", "touched", "doing"}
    assert git(repo.worktree, "log", "-1", "--format=%B").strip() == "The user answered each file."


@pytest.mark.supports("test_write_refuses_a_tree_out_of_the_schemas_form_naming_the_field")
def test_write_of_a_tree_out_of_form_gives_1_and_commits_nothing(repo: Repo):
    """Given the walkthrough's run, and a design tree whose goal has no `by`
    When `tree.py write` runs on it
    Then it gives 1 naming `by`, and the worktree's HEAD is as it was"""
    run = repo.begin()
    head = git(repo.worktree, "rev-parse", "HEAD")
    path = write(repo.base, "design-tree.json", json.dumps(schema_tree(goal={"decided": "x"})))
    code, _, err = repo.run("write", run, path, "Ground.")
    assert code == 1 and "by" in err and git(repo.worktree, "rev-parse", "HEAD") == head


@pytest.mark.supports("test_a_lesson_without_its_words_cant_be_put_up")
def test_sign_off_of_a_file_that_isnt_json_gives_1_naming_it(repo: Repo):
    """Given the walkthrough's run, and a sign-off file holding `{`
    When `tree.py sign-off` runs on it
    Then it gives 1, naming the file"""
    run = repo.begin()
    path = write(repo.base, "sign-off.json", "{")
    code, _, err = repo.run("sign-off", run, path)
    assert code == 1 and "sign-off.json" in err


@pytest.mark.supports("test_ty_with_nothing_waiting_doesnt_load")
def test_approve_with_nothing_waiting_gives_1(repo: Repo):
    """Given the walkthrough's run with nothing put up
    When `tree.py approve` runs in its worktree
    Then it gives 1, saying nothing waits"""
    repo.begin()
    code, _, err = repo.run("approve")
    assert code == 1 and "nothing waits" in err


@pytest.mark.supports("test_a_lesson_signed_off_by_the_users_ty_opens_its_issue_on_rns_repository")
def test_approve_of_a_lesson_prints_the_url_of_its_issue(repo: Repo):
    """Given the walkthrough's run with a lesson put up
    When `tree.py approve` runs in its worktree
    Then it gives 0 and prints the issue's URL"""
    run = repo.begin()
    path = write(
        repo.base,
        "lesson.json",
        json.dumps({"of": "lesson", "can_do": "", "decisions": [], "words": LESSON}),
    )
    repo.run("sign-off", run, path)
    code, out, _ = repo.run("approve")
    assert code == 0 and out.strip().endswith("/issues/1")


@pytest.mark.supports("test_push_without_gh_logged_in_says_whats_missing_and_pushes_nothing")
def test_push_without_a_login_gives_1_with_whats_missing(repo: Repo):
    """Given the walkthrough's run, and gh logged in nowhere
    When `tree.py push` runs
    Then it gives 1 naming `gh auth login`"""
    run = repo.begin()
    write(repo.base, "github.json", json.dumps({"logged_in": False, "pulls": {}, "issues": []}))
    code, _, err = repo.run("push", run)
    assert code == 1 and "gh auth login" in err


@pytest.mark.supports("test_pause_without_gh_logged_in_commits_and_says_its_not_pushed")
def test_pause_that_cant_push_gives_1_saying_committed_but_not_pushed(repo: Repo):
    """Given the walkthrough's run with invoicer/tax.py written, and gh logged in nowhere
    When `tree.py pause` runs
    Then it gives 1 with `committed but not pushed`"""
    run = repo.begin()
    write(repo.worktree, "invoicer/tax.py", "def tax() -> None: ...\n")
    write(repo.base, "github.json", json.dumps({"logged_in": False, "pulls": {}, "issues": []}))
    code, _, err = repo.run("pause", run)
    assert code == 1 and "committed but not pushed" in err


@pytest.mark.supports(
    "test_the_orchestrator_gets_the_round_and_puts_up_the_points_the_generator_settled"
)
def test_round_of_a_deliverable_with_no_round_gives_1(repo: Repo):
    """Given the walkthrough's run, its tree holding the hints with no round yet
    When `tree.py round` runs on the hints
    Then it gives 1 naming the hints"""
    run = repo.begin()
    path = write(repo.base, "design-tree.json", json.dumps(schema_tree()))
    repo.run("write", run, path, "The plan.")
    code, _, err = repo.run("round", run, HINTS)
    assert code == 1 and HINTS in err


@pytest.mark.supports("test_gm_after_done_sends_the_pull_request_handed_over_back_to_a_draft")
def test_send_back_after_ready_marks_the_pull_request_a_draft_again(repo: Repo):
    """Given the walkthrough's run with both deliverables done and signed off, and the pull request
    marked ready by `tree.py ready`
    When `tree.py send-back` runs in its worktree
    Then it gives 0, and GitHub holds the pull request a draft again"""
    run = repo.begin()
    done = [
        {"name": HINTS_NAME, "path": HINTS, "kind": "code", "status": "done"},
        {"name": TYPED_NAME, "path": TYPED, "kind": "code", "status": "done"},
    ]
    path = write(repo.base, "design-tree.json", json.dumps(schema_tree(deliverables=done)))
    repo.run("write", run, path, "Both done.")
    for of in ("plan", HINTS, TYPED):
        sign_off = {"of": of, "can_do": "", "decisions": [], "words": ""}
        repo.run("sign-off", run, write(repo.base, "sign-off.json", json.dumps(sign_off)))
        repo.run("approve")
    repo.run("push", run)
    repo.run("ready", run)
    code, _, _ = repo.run("send-back")
    with open(os.path.join(repo.base, "github.json"), encoding="utf-8") as f:
        (pull,) = json.load(f)["pulls"].values()
    assert code == 0 and pull["draft"]


@pytest.mark.supports(
    "test_ty_after_done_signs_off_the_pull_request_handed_over_and_leaves_it_ready"
)
def test_approve_after_ready_leaves_the_pull_request_ready_and_unmerged(repo: Repo):
    """Given the walkthrough's run with both deliverables done and signed off, and the pull request
    marked ready by `tree.py ready`
    When `tree.py approve` runs in its worktree
    Then it gives 0, and GitHub holds the pull request ready and unmerged"""
    run = repo.begin()
    done = [
        {"name": HINTS_NAME, "path": HINTS, "kind": "code", "status": "done"},
        {"name": TYPED_NAME, "path": TYPED, "kind": "code", "status": "done"},
    ]
    path = write(repo.base, "design-tree.json", json.dumps(schema_tree(deliverables=done)))
    repo.run("write", run, path, "Both done.")
    for of in ("plan", HINTS, TYPED):
        sign_off = {"of": of, "can_do": "", "decisions": [], "words": ""}
        repo.run("sign-off", run, write(repo.base, "sign-off.json", json.dumps(sign_off)))
        repo.run("approve")
    repo.run("push", run)
    repo.run("ready", run)
    code, _, _ = repo.run("approve")
    with open(os.path.join(repo.base, "github.json"), encoding="utf-8") as f:
        (pull,) = json.load(f)["pulls"].values()
    assert code == 0 and set(pull) == {"number", "draft", "comments"} and not pull["draft"]


@pytest.mark.supports("test_ready_refuses_while_a_deliverable_isnt_done")
def test_ready_with_a_deliverable_open_gives_1_naming_it(repo: Repo):
    """Given the walkthrough's run, its tree holding the hints open
    When `tree.py ready` runs
    Then it gives 1 naming the hints"""
    run = repo.begin()
    path = write(repo.base, "design-tree.json", json.dumps(schema_tree()))
    repo.run("write", run, path, "The plan.")
    code, _, err = repo.run("ready", run)
    assert code == 1 and HINTS in err
