"""The unit cases of repository/command.py's `main`, repository.py's command line: each subcommand
with what it prints and its exit code, `find` of no run, and of the newest of several, its worktree
made again, `pause`, `cancel` of a run that GitHub holds nothing of, of one whose branch and pull
request it removes there, of one where gh can't ask GitHub, and of a worktree that can't be removed,
`put-up` printing a link of each of the deliverable's paths and none for the plan, marking the
deliverable's last Round, and making done one at a step that the user doesn't check, `diff`,
`ci` by what the checks found, `checks` with findings and with none, and each fault by its exit
code: 2 with the usage for arguments of another form, 1 with `repository.py: ` for an input that
is Wrong and for something Missing, origin's HEAD naming no branch and gh with no login among
them, and 2 for what CantRun."""

from __future__ import annotations

import os
from datetime import date
from typing import Any

import pytest
import rn_files
from gh import gh_double
from repo_files import git
from repository.command import USAGE, main
from repository.place import RunPlace
from rn_runs import NAME, branch_run, changed, head, hook, made_run

RUN = f".claude/worktrees/rn-{NAME}/.rn/{NAME}"
PR = "http://github.com/owner/repo/pull/1"


def command_link(run: RunPlace, ref: str = "HEAD") -> str:
    """The line that put-up prints of the command's file at the commit of the run's worktree that
    the ref names."""
    worktree = rn_files.worktree_of(run.repository, NAME)
    return f"http://github.com/owner/repo/blob/{head(worktree, ref)}/{rn_files.COMMAND}\n"


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_open"
)
def test_new_prints_the_new_runs_folder_from_the_repositorys_top(tmp_path: Any, host: Any):
    """Given invoicer's repository with a remote
    When repository.py new is given the walkthrough's slug and its languages
    Then it gives 0 printing the run's folder, named by today and the slug, from the top, as a
    line, and the run's design tree holds the goal open, for the pruner to write"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    rn_files.with_origin(repo, str(tmp_path / "origin.git"))
    name = f"{date.today():%Y%m%d}-{rn_files.NAMED}"
    folder = f".claude/worktrees/rn-{name}/.rn/{name}"
    argv = ["new", rn_files.NAMED, *rn_files.LANGUAGES]
    given = main(argv, repo, rn_files.RN, host)
    assert given == (0, folder + "\n", "")
    tree = rn_files.read_json(os.path.join(repo, folder, "design-tree.json"))
    assert tree["goal"] == {"decided": None}


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_open"
)
def test_new_writes_rns_version_and_the_languages_in_the_trees_context(tmp_path: Any, host: Any):
    """Given invoicer's repository with a remote
    When repository.py new is given the walkthrough's slug, English, and Japanese
    Then the run's design tree's context holds rn's version as its plugin.json gives it, English
    as the deliverables' language and Japanese as the conversation's, no issues, and no pull
    request"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    rn_files.with_origin(repo, str(tmp_path / "origin.git"))
    argv = ["new", rn_files.NAMED, "English", "Japanese"]
    code, out, _ = main(argv, repo, rn_files.RN, host)
    assert code == 0
    tree = rn_files.read_json(os.path.join(repo, out.strip(), "design-tree.json"))
    plugin = rn_files.read_json(os.path.join(rn_files.RN, ".claude-plugin", "plugin.json"))
    assert tree["context"] == {
        "rn": plugin["version"],
        "languages": {"deliverables": "English", "conversation": "Japanese"},
        "issues": {"closes": [], "refs": []},
        "pr": None,
    }


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_open"
)
def test_new_of_an_empty_language_says_which_to_give(tmp_path: Any, host: Any):
    """Given invoicer's repository with a remote
    When repository.py new is given the walkthrough's slug, an empty deliverables'
    language, and Japanese
    Then it gives 1 with `repository.py: ` and which language is empty on stderr, and makes no
    worktree"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    rn_files.with_origin(repo, str(tmp_path / "origin.git"))
    argv = ["new", rn_files.NAMED, "", "Japanese"]
    code, out, err = main(argv, repo, rn_files.RN, host)
    assert (code, out) == (1, "")
    assert err.startswith("repository.py: the deliverables language is empty")
    assert not os.path.exists(os.path.join(repo, ".claude", "worktrees"))


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_open"
)
@pytest.mark.parametrize("given", ["?!", rn_files.WORDS], ids=["no-letter", "the-users-words"])
def test_new_of_other_than_a_slug_says_the_form_it_takes(tmp_path: Any, host: Any, given: str):
    """Given invoicer's repository with a remote
    When repository.py new is given words with no letter or digit, or the user's words as typed,
    in place of the slug
    Then it gives 1 with `repository.py: ` and the form that a slug takes on stderr, and makes no
    worktree"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    rn_files.with_origin(repo, str(tmp_path / "origin.git"))
    code, out, err = main(["new", given, *rn_files.LANGUAGES], repo, rn_files.RN, host)
    assert (code, out) == (1, "")
    assert err.startswith("repository.py: ") and "lower-case English words joined by -" in err
    assert not os.path.exists(os.path.join(repo, ".claude", "worktrees"))


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_open"
)
def test_new_with_no_default_branch_on_origin_says_what_is_missing(tmp_path: Any, host: Any):
    """Given invoicer's repository with no remote, so that origin's HEAD names no branch
    When repository.py new is given the walkthrough's slug and its languages
    Then it gives 1 with `repository.py: ` and what's missing on stderr, and makes no worktree"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    argv = ["new", rn_files.NAMED, *rn_files.LANGUAGES]
    code, out, err = main(argv, repo, rn_files.RN, host)
    assert (code, out) == (1, "")
    assert err.startswith("repository.py: ")
    assert not os.path.exists(os.path.join(repo, ".claude", "worktrees"))


@pytest.mark.supports("test_a_pick_up_with_no_run_finds_none_and_makes_no_worktree")
def test_find_of_no_run_prints_nothing(tmp_path: Any, host: Any):
    """Given invoicer's repository with a remote and no run
    When repository.py find is run
    Then it gives 0 printing nothing"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    rn_files.with_origin(repo, str(tmp_path / "origin.git"))
    assert main(["find"], repo, rn_files.RN, host) == (0, "", "")


@pytest.mark.supports("test_a_pick_up_with_no_run_finds_none_and_makes_no_worktree")
def test_find_with_github_out_of_reach_says_so_on_stderr(tmp_path: Any, host: Any):
    """Given invoicer's repository with one run with work left, whose origin git can't reach
    When repository.py find is run
    Then it gives 0 printing the run's folder as a line, and on stderr `repository.py: can't
    check the runs on GitHub, as git can't ask origin: ` with what git said, as one line"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    git(repo, "remote", "add", "origin", str(tmp_path / "gone.git"))
    branch_run(repo, NAME, rn_files.walkthrough_tree(NAME))
    code, out, err = main(["find"], repo, rn_files.RN, host)
    assert (code, out) == (0, f"{RUN}\n")
    prefix = "repository.py: can't check the runs on GitHub, as git can't ask origin: fatal: "
    assert err.startswith(prefix) and err.endswith("exists.\n") and err.count("\n") == 1


@pytest.mark.supports("test_a_pick_up_in_a_repository_whose_worktree_is_gone_makes_it_again")
def test_find_prints_the_newest_run_and_makes_its_worktree_again(tmp_path: Any, host: Any):
    """Given a repository with two runs with work left, the newer by its last commit with its
    worktree removed, and one newer still whose every deliverable is done
    When repository.py find is run
    Then it gives 0 printing the newer run with work left, its folder from the top, as one line,
    and that run's worktree lies there again"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    rn_files.with_origin(repo, str(tmp_path / "origin.git"))
    for name, when in (
        ("20261120-a", "2026-11-15T09:00:00"),
        ("20261101-z", "2026-11-20T09:00:00"),
    ):
        branch_run(repo, name, rn_files.walkthrough_tree(name), when, worktree=name != "20261101-z")
    done = rn_files.tree(
        [rn_files.done_node(rn_files.GOAL, rn_files.plan_path("x"), "design-tree")]
    )
    branch_run(repo, "20261121-done", done, "2026-11-21T09:00:00")
    printed = ".claude/worktrees/rn-20261101-z/.rn/20261101-z\n"
    assert main(["find"], repo, rn_files.RN, host) == (0, printed, "")
    assert os.path.isfile(os.path.join(repo, printed.strip(), "design-tree.json"))


@pytest.mark.supports("test_a_pause_pushes_the_runs_work_so_far")
def test_pause_prints_the_hash_the_remote_holds(tmp_path: Any, host: Any):
    """Given a run whose design tree is changed
    When repository.py pause is given the run's folder
    Then it gives 0 printing the hash of origin's rn-<name> as a line"""
    run = made_run(str(tmp_path))
    changed(run, {f".rn/{NAME}/design-tree.json": "{}\n"})
    code, out, err = main(["pause", RUN], run.repository, rn_files.RN, host)
    assert (code, out, err) == (0, head(str(tmp_path / "origin.git"), f"rn-{NAME}") + "\n", "")


@pytest.mark.supports("test_a_pause_pushes_the_runs_work_so_far")
def test_pause_with_no_origin_says_what_is_missing(tmp_path: Any, host: Any):
    """Given a run whose repository has no remote
    When repository.py pause is given the run's folder
    Then it gives 1 with `repository.py: ` and what's missing on stderr"""
    run = made_run(str(tmp_path), origin=False)
    code, out, err = main(["pause", RUN], run.repository, rn_files.RN, host)
    assert (code, out) == (1, "")
    assert err.startswith("repository.py: ")


@pytest.mark.supports("test_a_cancel_removes_the_worktree_its_branch_and_its_pull_request")
@pytest.mark.parametrize("pushed", [False, True], ids=["local-only", "pushed"])
def test_cancel_removes_the_run_and_prints_what_it_removed_on_github(
    tmp_path: Any, host: Any, gh_state: str, pushed: bool
):
    """Given a run whose branch is on this machine alone, or pushed to origin with its pull
    request open
    When repository.py cancel is given the run's folder
    Then it gives 0 printing nothing, or the pull request and origin/rn-<name>, a line each, with
    nothing on stderr; the run's worktree and its local branch are gone; and origin holds no
    branch rn-<name>"""
    run = made_run(str(tmp_path))
    if pushed:
        git(run.worktree, "push", "-q", "-u", "origin", f"rn-{NAME}")
        gh_double.opened(gh_state, PR)
    printed = f"{PR}\norigin/rn-{NAME}\n" if pushed else ""
    assert main(["cancel", RUN], run.repository, rn_files.RN, host) == (0, printed, "")
    assert not os.path.exists(run.worktree)
    assert git(run.repository, "branch", "--list", f"rn-{NAME}").strip() == ""
    assert git(run.repository, "ls-remote", "--heads", "origin", f"rn-{NAME}") == ""


@pytest.mark.supports("test_a_cancel_removes_the_worktree_its_branch_and_its_pull_request")
def test_cancel_that_cant_remove_on_github_says_so_on_stderr_and_still_gives_0(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given a run whose branch is pushed to origin, and gh that can't reach GitHub
    When repository.py cancel is given the run's folder
    Then it gives 0 printing origin/rn-<name> as a line, and on stderr `repository.py: can't
    remove ` with what it couldn't remove and what gh said, as a line; and the run's worktree and
    its local branch are gone"""
    run = made_run(str(tmp_path))
    git(run.worktree, "push", "-q", "-u", "origin", f"rn-{NAME}")
    gh_double.unreached(gh_state)
    said = gh_double.line(gh_double.PR_VIEW, "gh pr view can't reach GitHub")["stderr"].strip()
    unchecked = (
        f"repository.py: can't remove the pull request of rn-{NAME} on GitHub, as gh can't ask"
        f" GitHub: {said}\n"
    )
    assert main(["cancel", RUN], run.repository, rn_files.RN, host) == (
        0,
        f"origin/rn-{NAME}\n",
        unchecked,
    )
    assert not os.path.exists(run.worktree)
    assert git(run.repository, "branch", "--list", f"rn-{NAME}").strip() == ""


@pytest.mark.supports("test_a_cancel_whose_worktree_cant_be_removed_gives_2_and_keeps_the_run")
def test_cancel_of_a_worktree_git_cant_remove_gives_2(tmp_path: Any, host: Any):
    """Given a run whose worktree is locked
    When repository.py cancel is given the run's folder
    Then it gives 2 with `repository.py: ` and what git said on stderr, and the worktree stays"""
    run = made_run(str(tmp_path))
    git(run.repository, "worktree", "lock", run.worktree)
    code, out, err = main(["cancel", RUN], run.repository, rn_files.RN, host)
    assert (code, out) == (2, "")
    assert err.startswith("repository.py: ") and "locked" in err
    assert os.path.isdir(run.worktree)


@pytest.mark.supports(
    "test_the_first_deliverable_whose_rounds_are_over_is_put_up_in_the_runs_pull_request"
)
def test_put_up_of_the_plan_prints_nothing(tmp_path: Any, host: Any):
    """Given a run whose plan is open
    When repository.py put-up is given the run's folder and the plan's path
    Then it gives 0 printing nothing, as the plan is the message that shows it"""
    run = made_run(str(tmp_path), design_tree=rn_files.walkthrough_tree(NAME, plan_done=False))
    given = main(["put-up", RUN, rn_files.plan_path(NAME)], run.repository, rn_files.RN, host)
    assert given == (0, "", "")


@pytest.mark.supports(
    "test_the_first_deliverable_whose_rounds_are_over_is_put_up_in_the_runs_pull_request"
)
def test_put_up_prints_a_link_of_each_path_of_the_deliverable_a_line_each(tmp_path: Any, host: Any):
    """Given a run whose command lies at invoicer/__main__.py and at the more path docs/
    When repository.py put-up is given the run's folder and the command's path
    Then it gives 0 printing the link of the command's file, then of the folder docs, at the
    commit pushed, each as a line"""
    design_tree = rn_files.walkthrough_tree(NAME)
    design_tree["deliverables"][1]["more_paths"] = ["docs/"]
    run = made_run(str(tmp_path), design_tree=design_tree)
    changed(run, {rn_files.COMMAND: "print()\n"})
    given = main(["put-up", RUN, rn_files.COMMAND], run.repository, rn_files.RN, host)
    commit = head(rn_files.worktree_of(run.repository, NAME))
    docs = f"http://github.com/owner/repo/tree/{commit}/docs\n"
    assert given == (0, command_link(run) + docs, "")


@pytest.mark.supports("test_a_send_back_past_the_contents_limit_is_remade_in_rounds_of_its_own")
def test_put_up_marks_the_deliverables_last_round_as_put_up(tmp_path: Any, host: Any):
    """Given a run whose command has Rounds content-1 and content-2, its node holding N1 not good
    with an open decision of N1, the rest good
    When repository.py put-up is given the run's folder and the command's path
    Then it gives 0 printing the command's link, and content-2 alone holds put-up.json with N1
    not good and its open decision"""
    left = {"N1": [rn_files.decision("a comma in a line", None)]}
    design_tree = rn_files.walkthrough_tree(NAME, command_good=["N2", "N3"], command_decisions=left)
    run = made_run(str(tmp_path), design_tree=design_tree)
    changed(run, {rn_files.COMMAND: "print()\n"})
    folder = rn_files.folder_of(run.repository, NAME)
    first, second = (rn_files.a_round(folder, rn_files.COMMAND, "content", n) for n in (1, 2))
    given = main(["put-up", RUN, rn_files.COMMAND], run.repository, rn_files.RN, host)
    assert given == (0, command_link(run), "")
    assert not os.path.exists(os.path.join(first, "put-up.json"))
    assert rn_files.read_json(os.path.join(second, "put-up.json")) == {
        "short": ["N1"],
        "open": [{"condition": "N1", "about": "a comma in a line"}],
    }


ONE_STEP = (
    "test_a_deliverable_at_a_step_the_user_doesnt_check_is_done_once_put_up_and_the_next_starts"
)


def stepped(command: bool) -> dict:
    """The walkthrough's tree whose command is open with each condition good, at a step whose
    sign-off is as given, and whose guide's step the user checks."""
    design_tree = rn_files.walkthrough_tree(NAME, command_good=True)
    design_tree["steps"] = [
        rn_files.step("what it does", [rn_files.COMMAND], command),
        rn_files.step("how it's used", [rn_files.GUIDE], True),
    ]
    return design_tree


@pytest.mark.supports(
    "test_a_deliverable_at_a_step_the_user_doesnt_check_is_done_once_put_up_and_the_next_starts"
)
def test_put_up_at_a_step_the_user_doesnt_check_makes_it_done_marks_its_round_and_pushes(
    tmp_path: Any, host: Any
):
    """Given a run whose command, open with each condition good after Round content-1, lies at a
    step that the user doesn't check
    When repository.py put-up is given the run's folder and the command's path
    Then it gives 0 printing the command's link at the commit before it's done; the tree holds the
    command done in its one line, its item of the work gone; content-1 holds put-up.json; the
    tree, put-up.json among it, is committed as
    `rn: <command's name>, done at a step that the user doesn't check`; and origin's rn-<name>
    holds that commit"""
    run = made_run(str(tmp_path), design_tree=stepped(False))
    changed(run, {rn_files.COMMAND: "print()\n"})
    folder = rn_files.folder_of(run.repository, NAME)
    first = rn_files.a_round(folder, rn_files.COMMAND, "content", 1)
    given = main(["put-up", RUN, rn_files.COMMAND], run.repository, rn_files.RN, host)
    assert given == (0, command_link(run, "HEAD~1"), "")
    design_tree = rn_files.read_json(os.path.join(folder, "design-tree.json"))
    done = rn_files.done_node(rn_files.COMMAND_NAME, rn_files.COMMAND, "light")
    assert design_tree["deliverables"][1] == done
    assert design_tree["work"] == [rn_files.work("make", rn_files.GUIDE)]
    assert os.path.isfile(os.path.join(first, "put-up.json"))
    worktree = rn_files.worktree_of(run.repository, NAME)
    assert git(worktree, "status", "--porcelain") == ""
    assert git(worktree, "log", "-1", "--format=%s").strip() == (
        f"rn: {rn_files.COMMAND_NAME}, done at a step that the user doesn't check"
    )
    assert head(str(tmp_path / "origin.git"), f"rn-{NAME}") == head(worktree)


@pytest.mark.supports(
    "test_a_deliverable_at_a_step_the_user_doesnt_check_is_done_once_put_up_and_the_next_starts"
)
def test_put_up_at_a_step_the_user_checks_leaves_it_open_for_the_signoff(tmp_path: Any, host: Any):
    """Given a run whose command, open with each condition good after Round content-1, lies at a
    step that the user checks
    When repository.py put-up is given the run's folder and the command's path
    Then it gives 0, and the tree holds the command open"""
    run = made_run(str(tmp_path), design_tree=stepped(True))
    changed(run, {rn_files.COMMAND: "print()\n"})
    folder = rn_files.folder_of(run.repository, NAME)
    rn_files.a_round(folder, rn_files.COMMAND, "content", 1)
    assert main(["put-up", RUN, rn_files.COMMAND], run.repository, rn_files.RN, host)[0] == 0
    design_tree = rn_files.read_json(os.path.join(folder, "design-tree.json"))
    assert design_tree["deliverables"][1]["status"] == "open"


@pytest.mark.supports("test_the_final_check_pushes_the_work_and_reads_its_whole_diff_and_ci")
def test_diff_prints_the_pull_requests_whole_diff(tmp_path: Any, host: Any):
    """Given a run whose guide is written but not committed
    When repository.py diff is given the run's folder
    Then it gives 0 printing a diff that holds the guide"""
    run = made_run(str(tmp_path))
    changed(run, {rn_files.GUIDE: "# Guide\n"})
    code, out, err = main(["diff", RUN], run.repository, rn_files.RN, host)
    assert (code, err) == (0, "")
    assert f"+++ b/{rn_files.GUIDE}" in out


@pytest.mark.supports("test_the_final_check_pushes_the_work_and_reads_its_whole_diff_and_ci")
@pytest.mark.parametrize(
    ("found", "expected"),
    [
        ("passed", (0, "tests\tpassed")),
        ("cancelled", (0, "cancels\tcancelled")),
        ("failed", (1, "repository.py: the pull request's CI fails at tests")),
        ("none", (0, "no CI started within 120 seconds of the push")),
    ],
    ids=["passed", "cancelled", "failed", "no-ci"],
)
def test_ci_gives_0_or_1_by_what_the_checks_found(
    tmp_path: Any, host: Any, gh_state: str, found: str, expected: tuple[int, str]
):
    """Given a run whose plan was put up, and whose CI's checks each passed, one was cancelled,
    one failed, or are none
    When repository.py ci is given the run's folder
    Then it gives 0 printing each check with how it ended, 1 naming the one that failed, or 0
    saying that no CI started within 120 seconds of the push"""
    run = made_run(str(tmp_path), design_tree=rn_files.walkthrough_tree(NAME, plan_done=False))
    main(["put-up", RUN, rn_files.plan_path(NAME)], run.repository, rn_files.RN, host)
    gh_double.checks(gh_state, found)
    code, out, err = main(["ci", RUN], run.repository, rn_files.RN, host)
    assert code == expected[0]
    assert expected[1] in out + err


@pytest.mark.supports(
    "test_the_first_deliverable_whose_rounds_are_over_is_put_up_in_the_runs_pull_request"
)
def test_put_up_with_gh_logged_out_says_what_is_missing_and_commits_nothing(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given a run whose command is changed, and gh with no login
    When repository.py put-up is given the run's folder and the command's path
    Then it gives 1 with `repository.py: ` and gh's words that no GitHub host is logged into on
    stderr, and the branch's head is as it was"""
    run = made_run(str(tmp_path))
    changed(run, {rn_files.COMMAND: "print()\n"})
    worktree = rn_files.worktree_of(run.repository, NAME)
    before = head(worktree)
    gh_double.logged_out(gh_state)
    code, out, err = main(["put-up", RUN, rn_files.COMMAND], run.repository, rn_files.RN, host)
    assert (code, out) == (1, "")
    assert err.startswith("repository.py: ") and "not logged into any GitHub hosts" in err
    assert head(worktree) == before


@pytest.mark.supports("test_the_generators_checks_give_the_repositorys_commit_check_findings")
def test_checks_with_no_finding_prints_nothing(tmp_path: Any, host: Any):
    """Given a run whose repository sets no check, and the command written
    When repository.py checks is given the run's folder and the command
    Then it gives 0 printing nothing"""
    run = made_run(str(tmp_path))
    changed(run, {rn_files.COMMAND: "print()\n"})
    assert main(["checks", RUN, rn_files.COMMAND], run.repository, rn_files.RN, host) == (
        0,
        "",
        "",
    )


@pytest.mark.supports("test_the_generators_checks_give_the_repositorys_commit_check_findings")
def test_checks_with_findings_gives_1_with_each_a_line(tmp_path: Any, host: Any):
    """Given a run whose repository's check fails saying two lines, and the command and the guide
    written
    When repository.py checks is given the run's folder, the command, and the guide
    Then it gives 1 with the two lines, each a line"""
    run = made_run(str(tmp_path))
    hook(run.repository, "echo first\necho second\nexit 1\n")
    changed(run, {rn_files.COMMAND: "print()\n", rn_files.GUIDE: "# Guide\n"})
    code, out, err = main(
        ["checks", RUN, rn_files.COMMAND, rn_files.GUIDE], run.repository, rn_files.RN, host
    )
    assert code == 1
    assert out + err == "first\nsecond\n"


@pytest.mark.supports("test_the_people_start_from_the_branch_without_rns_folder")
def test_trial_prints_the_folder_of_the_peoples_starting_state(tmp_path: Any, host: Any, temp: str):
    """Given a run with the command's Round content-1
    When repository.py trial is given the run's folder and the Round's folder from the top
    Then it gives 0 printing the folder it made, under the system's temporary folder, as a line,
    and the folder holds invoicer's lines"""
    run = made_run(str(tmp_path))
    round_ = rn_files.round_of(RUN, rn_files.COMMAND, "content", 1)
    os.makedirs(os.path.join(run.repository, round_))
    code, out, err = main(["trial", RUN, round_], run.repository, rn_files.RN, host)
    assert (code, err) == (0, "")
    folder = out.removesuffix("\n")
    assert out == folder + "\n"
    expected = os.path.join(temp, f"rn-trial-{NAME}-invoicer%2F__main__.py-content-1")
    assert os.path.normpath(folder) == expected
    assert os.path.isfile(os.path.join(folder, "invoicer", "lines.py"))


@pytest.mark.supports("test_the_people_start_from_the_branch_without_rns_folder")
def test_trial_where_the_folder_cant_be_made_gives_2(tmp_path: Any, host: Any, temp: str):
    """Given a run with the command's Round content-1, and a system's temporary folder that may
    not be written
    When repository.py trial is given the run's folder and the Round's folder
    Then it gives 2 with what stopped it on stderr"""
    run = made_run(str(tmp_path))
    round_ = rn_files.round_of(RUN, rn_files.COMMAND, "content", 1)
    os.makedirs(os.path.join(run.repository, round_))
    os.chmod(temp, 0o555)
    try:
        code, out, err = main(["trial", RUN, round_], run.repository, rn_files.RN, host)
    finally:
        os.chmod(temp, 0o755)
    assert (code, out) == (2, "")
    assert err


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
@pytest.mark.parametrize("sub", ["pause", "cancel", "put-up", "checks", "trial", "diff", "ci"])
def test_a_folder_that_isnt_a_runs_is_wrong(tmp_path: Any, host: Any, sub: str):
    """Given invoicer's repository with no run
    When the subcommand is given a folder that isn't a run's, with what else it takes
    Then it gives 1 with `repository.py: ` naming the folder on stderr"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    rest = {"pause": [], "put-up": [rn_files.COMMAND], "checks": [rn_files.COMMAND], "diff": []}
    rest.update(ci=[], cancel=[])
    argv = [sub, "docs", *rest.get(sub, ["docs"])]
    code, out, err = main(argv, repo, rn_files.RN, host)
    assert (code, out) == (1, "")
    assert err.startswith("repository.py: ") and "docs" in err


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_open"
)
@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["start"],
        ["new", rn_files.NAMED, "English"],
        ["new", rn_files.NAMED, *rn_files.LANGUAGES, "more"],
        ["find", "more"],
        ["pause"],
        ["cancel"],
        ["cancel", RUN, "more"],
        ["put-up", RUN],
        ["checks"],
        ["trial", RUN],
        ["trial", RUN, "a", "b"],
        ["diff"],
        ["diff", RUN, "more"],
        ["ci"],
        ["ci", RUN, "more"],
    ],
)
def test_arguments_of_another_form_give_the_usage(tmp_path: Any, host: Any, argv: list[str]):
    """Given invoicer's repository
    When repository.py is given arguments other than a subcommand's: none, an unknown one, or one
    too few or too many
    Then it gives 2 with the usage on stderr, and runs nothing"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    assert main(argv, repo, rn_files.RN, host) == (2, "", USAGE)
    assert host.ran == []
    assert git(repo, "branch", "--list").split() == ["*", "main"]
