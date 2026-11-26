"""The unit cases of repository/push.py: `stop`, which commits each change and pushes with its
upstream set, and each refusal: no origin, a push refused for want of a permission, and a remote
that isn't there; `put_up`, which asks gh's login first, its first time opening the pull request as
a draft titled by the picked need, its body the outcome and the issues, or the outcome alone, an
open pull request used as it is, its own opened beside an earlier one closed, the link of a file
and of a folder, and each refusal: gh with no login, no need picked, a deliverable that no step
names, each before any commit or push, gh that may not open the pull request, and a path that the
commit doesn't hold; `diff`, which commits and pushes each change and gives the whole diff; and
`ci`, which waits for the checks to start, each passed, one cancelled or timed out, one failed alone
or beside cancelled ones, gh that can't give the pull request or its checks, and no check started
within 120 seconds."""

from __future__ import annotations

import json
import os
import stat
from collections.abc import Mapping, Sequence
from typing import Any

import pytest
import rn_files
from fault import CantRun, Missing, Wrong
from gh import gh_double
from host import Ran
from place import RunPlace
from repo_files import git, write_files
from repository.push import ci, diff, put_up, stop
from repository.worktree import new

NAME = "20261126-invoice-from-statement"
URL = "http://github.com/owner/repo/pull/1"
# The repository's page on GitHub, as the pull request's URL gives it.
REPOSITORY = "http://github.com/owner/repo"
STEERING = rn_files.steering()


def made(tmp_path: Any, origin: bool = True) -> RunPlace:
    """The user's repository with origin, unless not, and a run made in it, its steering
    committed."""
    repo = rn_files.repository(str(tmp_path / "accounting"))
    if origin:
        rn_files.with_origin(repo, str(tmp_path / "origin.git"))
    else:
        git(repo, "update-ref", "refs/remotes/origin/HEAD", "HEAD")
        git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
        git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    run_ = new(RunPlace(repo, NAME), gh_double.host(str(tmp_path / "unused")))
    rn_files.committed_steering(run_.worktree, NAME, STEERING)
    return run_


def with_command(run_: RunPlace) -> RunPlace:
    """The run, with the command written in its worktree, as its generator leaves it."""
    write_files(run_.worktree, {rn_files.COMMAND: "print('invoice')\n"})
    return run_


def head(folder: str, ref: str = "HEAD") -> str:
    return git(folder, "rev-parse", ref).strip()


def subject(folder: str) -> str:
    return git(folder, "log", "-1", "--format=%s").strip()


def asked(gh_state: str, *words: str) -> list[list[str]]:
    """Each gh command that the double was asked whose words after `gh` begin with those given."""
    return [
        each
        for each in gh_double.state(gh_state)["asked"]
        if each[1 : 1 + len(words)] == list(words)
    ]


def flag(argv: list[str], name: str) -> str:
    """The value that a command names after the flag."""
    return argv[argv.index(name) + 1]


# stop


def test_a_stop_commits_each_change_and_pushes_the_branch_with_its_upstream(
    tmp_path: Any, host: Any
) -> None:
    """Given a run whose command is new, not committed.
    When stop is given the run.
    Then it gives the hash that origin's branch now holds, a commit `rn: stopped <name>`, whose
    upstream is origin's, with nothing left uncommitted."""
    run_ = with_command(made(tmp_path))
    given = stop(run_, host)
    assert given == head(str(tmp_path / "origin.git"), run_.branch) == head(run_.worktree)
    assert subject(run_.worktree) == f"rn: stopped {NAME}"
    upstream = git(
        run_.worktree, "rev-parse", "--abbrev-ref", f"{run_.branch}@{{upstream}}"
    ).strip()
    assert (upstream, git(run_.worktree, "status", "--porcelain")) == (f"origin/{run_.branch}", "")


def test_a_stop_with_no_origin_is_missing_one(tmp_path: Any, host: Any) -> None:
    """Given a run whose repository has no remote.
    When stop is given the run.
    Then Missing is raised."""
    with pytest.raises(Missing, match="no remote origin"):
        stop(made(tmp_path, origin=False), host)


def test_a_stop_whose_push_is_refused_for_want_of_a_permission_is_missing_one(
    tmp_path: Any, host: Any
) -> None:
    """Given a run whose remote's files may not be written.
    When stop is given the run.
    Then Missing is raised, with what git said of the permission."""
    run_ = with_command(made(tmp_path))
    origin = str(tmp_path / "origin.git")
    for folder, _, files in os.walk(origin):
        for each in [folder, *(os.path.join(folder, f) for f in files)]:
            os.chmod(each, os.stat(each).st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
    try:
        with pytest.raises(Missing, match=r"(?s)a permission: .*\[remote rejected\]"):
            stop(run_, host)
    finally:
        for folder, _, _ in os.walk(origin):
            os.chmod(folder, os.stat(folder).st_mode | stat.S_IWUSR)


def test_a_stop_to_a_remote_that_isnt_there_cant_run(tmp_path: Any, host: Any) -> None:
    """Given a run whose remote origin names a folder that doesn't exist.
    When stop is given the run.
    Then CantRun is raised, with what git said."""
    run_ = made(tmp_path, origin=False)
    git(run_.repository, "remote", "add", "origin", str(tmp_path / "gone.git"))
    with pytest.raises(CantRun, match="push the run's work: .*does not appear to be a git repo"):
        stop(run_, host)


# put_up


def test_a_first_put_up_opens_the_pull_request_as_a_draft_titled_by_the_picked_need(
    tmp_path: Any, host: Any, gh_state: str
) -> None:
    """Given a run whose command is made, with no pull request.
    When put_up is given the command.
    Then gh's login is asked first, the command is committed as `rn: <path>` and pushed, a draft
    pull request is opened of the branch titled by the picked need, its body the outcome and
    `Closes #38`, and the command's link at the pushed commit is given."""
    run_ = with_command(made(tmp_path))
    links = put_up(run_, STEERING, rn_files.COMMAND, host)
    assert gh_double.state(gh_state)["asked"][0][:3] == ["gh", "auth", "status"]
    assert subject(run_.worktree) == f"rn: {rn_files.COMMAND}"
    pushed = head(str(tmp_path / "origin.git"), run_.branch)
    assert links == [f"{REPOSITORY}/blob/{pushed}/invoice/__main__.py"]
    [create] = asked(gh_state, "pr", "create")
    assert ("--draft" in create, flag(create, "--head"), flag(create, "--title")) == (
        True,
        run_.branch,
        rn_files.PRINT,
    )
    assert flag(create, "--body") == f"{rn_files.OUTCOME}\n\nCloses #38"


def test_a_put_up_names_each_issue_it_closes_then_each_it_refers_to_or_none(
    tmp_path: Any, host: Any, gh_state: str
) -> None:
    """Given a run that closes #38 and #40 and refers to #12, and another that names none.
    When each puts its command up first.
    Then the first body names `Closes #38`, `Closes #40`, then `Refs #12`, and the second is the
    outcome alone."""
    run_ = with_command(made(tmp_path))
    issues = rn_files.steering()
    issues["state"]["issues"] = {"closes": [38, 40], "refs": [12]}
    put_up(run_, issues, rn_files.COMMAND, host)
    none = rn_files.steering()
    none["state"]["issues"] = {"closes": [], "refs": []}
    gh_double.keep(gh_state, {**gh_double.state(gh_state), "pull_request": None})
    put_up(run_, none, rn_files.COMMAND, host)
    bodies = [flag(each, "--body") for each in asked(gh_state, "pr", "create")]
    assert bodies == [f"{rn_files.OUTCOME}\n\nCloses #38\nCloses #40\nRefs #12", rn_files.OUTCOME]


def test_a_put_up_whose_pull_request_is_open_opens_none(
    tmp_path: Any, host: Any, gh_state: str
) -> None:
    """Given a run whose branch has its pull request open.
    When put_up is given the command.
    Then it opens no pull request, and gives the link on the open one's repository."""
    run_ = with_command(made(tmp_path))
    gh_double.opened(gh_state, URL)
    assert put_up(run_, STEERING, rn_files.COMMAND, host)[0].startswith(f"{REPOSITORY}/blob/")
    assert asked(gh_state, "pr", "create") == []


def test_a_put_up_beside_an_earlier_pull_request_not_open_opens_its_own(
    tmp_path: Any, host: Any, gh_state: str
) -> None:
    """Given a run whose branch's name had a pull request that's closed.
    When put_up is given the command.
    Then it opens a pull request of its own."""
    run_ = with_command(made(tmp_path))
    gh_double.earlier(gh_state, "http://github.com/owner/repo/pull/0", "CLOSED")
    put_up(run_, STEERING, rn_files.COMMAND, host)
    assert len(asked(gh_state, "pr", "create")) == 1


def test_a_put_up_of_a_folder_gives_its_link_as_a_tree(tmp_path: Any, host: Any) -> None:
    """Given a run whose step names the folder invoice/, made.
    When put_up is given invoice/.
    Then the link names the folder as a tree, with no `/` closing it."""
    run_ = with_command(made(tmp_path))
    folder = rn_files.steering()
    folder["state"]["steps"][0]["deliverables"][0]["path"] = "invoice/"
    [link] = put_up(run_, folder, "invoice/", host)
    assert link == f"{REPOSITORY}/tree/{head(run_.worktree)}/invoice"


@pytest.mark.parametrize(
    "case",
    [
        (rn_files.steering(target=None), rn_files.COMMAND, "no need is picked"),
        (STEERING, "docs/other.md", "no step names the deliverable"),
    ],
    ids=["no-need-picked", "no-step-names-it"],
)
def test_a_put_up_that_can_not_be_is_wrong_before_any_commit_or_push(
    tmp_path: Any, host: Any, gh_state: str, case: tuple[Any, str, str]
) -> None:
    """Given a run with no need picked, or a deliverable that no step names.
    When put_up is given it.
    Then Wrong is raised, and nothing is committed or pushed, and gh is asked its login alone."""
    steering, deliverable, says = case
    run_ = with_command(made(tmp_path))
    before = head(run_.worktree)
    with pytest.raises(Wrong, match=says):
        put_up(run_, steering, deliverable, host)
    assert head(run_.worktree) == before
    assert [each[:3] for each in gh_double.state(gh_state)["asked"]] == [["gh", "auth", "status"]]


def test_a_put_up_with_gh_logged_out_is_missing_its_login(
    tmp_path: Any, host: Any, gh_state: str
) -> None:
    """Given gh with no login.
    When put_up is given the command.
    Then Missing is raised, and nothing is committed."""
    run_ = with_command(made(tmp_path))
    gh_double.logged_out(gh_state)
    before = head(run_.worktree)
    with pytest.raises(Missing, match="no login"):
        put_up(run_, STEERING, rn_files.COMMAND, host)
    assert head(run_.worktree) == before


def test_a_put_up_that_gh_may_not_open_is_missing_the_right(tmp_path: Any, host: Any) -> None:
    """Given gh that refuses to open the pull request.
    When put_up is given the command.
    Then Missing is raised, with what gh said."""
    run_ = with_command(made(tmp_path))

    def refusing(argv: Sequence[str], cwd: str, env: Mapping[str, str] | None = None) -> Ran:
        return (
            Ran(1, "", "must be a collaborator\n")
            if argv[1:3] == ["pr", "create"]
            else host(argv, cwd, env)
        )

    with pytest.raises(Missing, match="may not open the pull request: must be a collaborator"):
        put_up(run_, STEERING, rn_files.COMMAND, refusing)


def test_a_put_up_of_a_path_the_commit_doesnt_hold_is_refused_naming_it(
    tmp_path: Any, host: Any
) -> None:
    """Given a run whose guide its step names but no one made.
    When put_up is given the guide.
    Then Wrong is raised, naming the path."""
    run_ = with_command(made(tmp_path))
    with pytest.raises(Wrong, match="docs/guide.md: the work's pushed commit holds nothing there"):
        put_up(run_, STEERING, rn_files.GUIDE, host)


def test_a_put_up_whose_gh_cant_reach_github_opens_no_second_pull_request(
    tmp_path: Any, host: Any, gh_state: str
) -> None:
    """Given a run whose branch has its pull request open, and gh that can't reach GitHub to view
    it.
    When put_up is given the command.
    Then CantRun is raised with what gh said, and no pull request is opened."""
    run_ = with_command(made(tmp_path))
    gh_double.opened(gh_state, URL)
    gh_double.unreached(gh_state)
    with pytest.raises(CantRun, match="can't tell whether the branch has a pull request"):
        put_up(run_, STEERING, rn_files.COMMAND, host)
    assert asked(gh_state, "pr", "create") == []


# diff


def test_diff_commits_each_change_pushes_it_and_gives_the_whole_diff(
    tmp_path: Any, host: Any
) -> None:
    """Given a run whose command is written, not committed.
    When diff is given the run.
    Then it gives a diff that holds the command and the steering, commits as `rn: the final check
    of <name>`, and origin's branch holds that commit."""
    run_ = with_command(made(tmp_path))
    given = diff(run_, host)
    assert f"+++ b/{rn_files.COMMAND}" in given and f"+++ b/.rn/{NAME}/steering.json" in given
    assert subject(run_.worktree) == f"rn: the final check of {NAME}"
    assert head(str(tmp_path / "origin.git"), run_.branch) == head(run_.worktree)


# ci


def checks_asked(gh_state: str) -> list[list[str]]:
    """Each `gh pr checks` that the double of gh was asked."""
    return [each for each in gh_double.state(gh_state)["asked"] if each[1:3] == ["pr", "checks"]]


# What ci says of the checks that failed, and of three that the CI cancelled.
MEND = "; mend each in the deliverable whose file it concerns"
AGAIN = (
    "; these ended neither passing nor failing, for the user to run again: times-out cancelled,"
    " cancels cancelled, cancelled cancelled"
)


def ended(found: str) -> list[dict[str, str]]:
    """Each check of the record that the double of gh gives for what the CI's checks found, as
    `gh pr checks --json name,state,bucket,link` gives them."""
    return json.loads(gh_double._ends(found)["stdout"])


def lines(checks: list[tuple[str, str]]) -> str:
    """The lines that ci gives of the checks, each by its name and how it ended."""
    return "".join(f"{name}\t{end}\n" for name, end in checks)


def test_ci_where_each_check_passed_gives_them_having_waited_for_the_works_branch(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given a run whose command was put up, and whose CI's checks each passed
    When ci is given the run
    Then it gives each check by its name, once each, in gh's order, as passed; and gh was asked,
    in the run's worktree, to wait for rn-<name>'s checks, then to give each check's end"""
    run = with_command(made(tmp_path))
    put_up(run, STEERING, rn_files.COMMAND, host)
    names = list(dict.fromkeys(each["name"] for each in ended("passed")))
    assert ci(run, host) == lines([(name, "passed") for name in names])
    branch = run.branch
    assert checks_asked(gh_state) == [
        ["gh", "pr", "checks", branch, "--watch"],
        ["gh", "pr", "checks", branch, "--json", "name,state,bucket,link"],
    ]
    assert host.ran[-1][1] == run.worktree


@pytest.mark.parametrize(
    "case",
    [("cancelled", "cancels", "cancelled"), ("timed-out", "deploy", "timed out")],
    ids=["cancelled", "timed-out"],
)
def test_ci_where_a_check_ended_neither_passing_nor_failing_names_how_it_ended(
    tmp_path: Any, host: Any, gh_state: str, case: tuple[str, str, str]
):
    """Given a run whose command was put up, and whose CI's check was cancelled, as GitHub Actions
    ends a job past its time limit too, or timed out, as another check's app may end it, each other
    check passed, and gh's watch ending 0 or 1
    When ci is given the run
    Then it gives each check by its name in gh's order, that one as cancelled or timed out and
    each other as passed, as neither passing nor failing, for the user to run again"""
    found, other, end = case
    run = with_command(made(tmp_path))
    put_up(run, STEERING, rn_files.COMMAND, host)
    gh_double.checks(gh_state, found)
    names = list(dict.fromkeys(each["name"] for each in ended(found)))
    assert other in names
    assert ci(run, host) == lines([(name, end if name == other else "passed") for name in names])


@pytest.mark.parametrize(
    ("found", "expected"),
    [
        ("failed", f"the pull request's CI fails at tests{MEND}"),
        ("ended", f"the pull request's CI fails at fails{MEND}{AGAIN}"),
    ],
    ids=["failed", "failed-and-cancelled"],
)
def test_ci_where_a_check_failed_cant_run_naming_it_once(
    tmp_path: Any, host: Any, gh_state: str, found: str, expected: str
):
    """Given a run whose command was put up, and whose CI's check `tests` failed, which gh's lines
    show twice as it waits, or whose check `fails` failed while three others were cancelled
    When ci is given the run
    Then CantRun is raised, as a problem with the deliverable that no rerun mends, naming each
    check that failed once, and no check that passed, then each that was cancelled, for the user
    to run again"""
    run = with_command(made(tmp_path))
    put_up(run, STEERING, rn_files.COMMAND, host)
    gh_double.checks(gh_state, found)
    with pytest.raises(CantRun) as refused:
        ci(run, host)
    assert str(refused.value) == expected


def test_ci_that_gh_cant_give_cant_run_with_what_gh_said(tmp_path: Any, host: Any, clock: Any):
    """Given a run that has no pull request
    When ci is given the run
    Then CantRun is raised, saying gh can't give the pull request's CI, with what gh said, with no
    wait"""
    run = with_command(made(tmp_path))
    with pytest.raises(CantRun) as refused:
        ci(run, host)
    assert str(refused.value).startswith("gh can't give the pull request's CI: ")
    assert 'no pull requests found for branch "rn-' in str(refused.value)
    assert clock.slept == []


def test_ci_whose_checks_gh_cant_read_once_they_started_cant_run_with_what_gh_said(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given a run whose command was put up, whose pushed head's checks started, and whose gh then
    can't reach GitHub
    When ci is given the run
    Then CantRun is raised, saying gh can't give the pull request's CI, with what gh said"""
    run = with_command(made(tmp_path))
    put_up(run, STEERING, rn_files.COMMAND, host)
    gh_double.checks_unreached(gh_state)
    said = gh_double.line(gh_double.PR_CHECKS, "gh pr checks --json can't reach GitHub")["stderr"]
    with pytest.raises(CantRun) as refused:
        ci(run, host)
    assert str(refused.value) == f"gh can't give the pull request's CI: {said.strip()}"


def views(gh_state: str) -> int:
    """How many times the double of gh was asked for the pull request's head and its checks."""
    asked = gh_double.state(gh_state)["asked"]
    return sum(1 for each in asked if each[1:3] == ["pr", "view"] and "headRefOid" in each[-1])


def test_ci_waits_until_the_pushed_heads_checks_start_then_reads_their_ends(
    tmp_path: Any, host: Any, gh_state: str, clock: Any
):
    """Given a run whose command was put up, whose CI's checks each passed, and whose pull request
    gives the head before the push for one view, then the pushed head with no check started for
    23 views, its checks starting 120 seconds after the first view, the most
    When ci is given the run
    Then it views the head every 5 seconds until the pushed head's checks show, then gives each
    check as passed, as it gives with no wait"""
    run = with_command(made(tmp_path))
    put_up(run, STEERING, rn_files.COMMAND, host)
    gh_double.started(gh_state, 1, 23)
    names = list(dict.fromkeys(each["name"] for each in ended("passed")))
    assert ci(run, host) == lines([(name, "passed") for name in names])
    assert clock.slept == [5] * 24
    assert views(gh_state) == 25


def test_ci_whose_checks_dont_start_within_120_seconds_says_no_ci_started(
    tmp_path: Any, host: Any, gh_state: str, clock: Any
):
    """Given a run whose command was put up, and whose pushed head's checks start only past 120
    seconds after the first view
    When ci is given the run
    Then it gives that no CI started within 120 seconds of the push, having viewed the head at
    each 5 seconds up to 120, and asked gh for no check"""
    run = with_command(made(tmp_path))
    put_up(run, STEERING, rn_files.COMMAND, host)
    gh_double.started(gh_state, 0, 25)
    assert ci(run, host) == "no CI started within 120 seconds of the push\n"
    assert clock.slept == [5] * 24
    assert views(gh_state) == 25
    assert checks_asked(gh_state) == []
