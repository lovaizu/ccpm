"""Decides how a run's worktree comes to be, is found again, and goes: made with its branch from
the default branch that origin's HEAD names, with its design tree; found from the runs' branches
whose committed design tree holds work left, its worktree made again where none lies; and removed
with its local branch where the user cancels the run, leaving to the user what GitHub holds, as
GitHub itself answers; and, inside herdr, made, opened, and removed through herdr, so that the run
shows as a herdr workspace while it lies here."""

from __future__ import annotations

import json
import os
from typing import NamedTuple

from fault import CantRun, Missing, Wrong
from practice import Practice
from tree import form

from repository.host import Host, checked
from repository.place import RunPlace

# The line of info/exclude that keeps the runs' worktrees out of the user's untracked files.
_EXCLUDED = "/.claude/worktrees/"
# The branches of the runs: the local ones, and origin's as the repository last fetched them.
_REFS = ("refs/heads/rn-*", "refs/remotes/origin/rn-*")


def new(
    run: RunPlace, context: form.Context, goal: str, practice: Practice, host: Host
) -> RunPlace:
    """Makes a run's worktree and its design tree with the goal as put.

    Takes: the run to make, named by `place.named` from the day and the user's words in reply
    to `/rn:on`; the run's context, as `tree.form.context` gives it; the goal as the orchestrator
    puts it; the design tree best practice; and the host.
    Gives: the run, made.
    Changes: adds the branch `rn-<name>` from the head of the default branch that
    `git symbolic-ref refs/remotes/origin/HEAD` names, tracking none, checks
    it out in the run's worktree, and writes there the design tree that `tree.form.started` gives
    for the context and the goal, uncommitted; the user's own worktree and branch stay as they
    were. Inside herdr, herdr makes the branch and the worktree and opens its workspace, leaving
    the focus where it is.
    Refuses: Missing where the run's repository isn't the top of a git repository with a commit, or
    `refs/remotes/origin/HEAD` names no default branch; Wrong where the goal is empty, or a run of
    the name already lies there; CantRun where git or herdr fails, with what it said.
    """
    if not goal.strip():
        raise Wrong("the goal is empty; give the goal as one sentence with the user as its subject")
    top = host(["git", "rev-parse", "--show-toplevel"], run.repository)
    if top.code != 0 or os.path.realpath(top.out.strip()) != os.path.realpath(run.repository):
        raise Missing(f"{run.repository} isn't the top of a git repository; run /rn:on at its top")
    if os.path.exists(run.worktree):
        raise Wrong(f"a run {run.name} already lies at {run.worktree}; pick it up with /rn:up")
    default = host(["git", "symbolic-ref", "refs/remotes/origin/HEAD"], run.repository)
    if default.code != 0:
        raise Missing(
            "origin's HEAD names no default branch to start the run from; push the default branch"
            " to origin, and run git remote set-head origin --auto"
        )
    start = default.out.strip()
    if _inside_herdr():
        _made_by_herdr(run, start, host)
    else:
        checked(
            host,
            ["git", "worktree", "add", "-q", "--no-track", "-b", run.branch, run.worktree, start],
            run.repository,
            CantRun,
            "git can't make the run's worktree",
        )
    _exclude(run, host)
    plan = os.path.relpath(run.tree, run.worktree)
    os.makedirs(run.folder)
    form.write(run.tree, form.started(context, goal, plan, practice))
    return run


def _inside_herdr() -> bool:
    """Whether rn runs in a pane of herdr, by the variable that herdr sets in each pane's
    environment, tested as herdr 0.9.5's `herdr --skill` tests it."""
    return os.environ.get("HERDR_ENV") == "1"


def _made_by_herdr(run: RunPlace, start: str, host: Host) -> None:
    """Has herdr make the run's branch from the start and its worktree, and open its workspace.
    herdr gives the branch the base as its upstream where the base is a remote's branch, so herdr
    takes the start's commit, from which the branch tracks none, as git's `--no-track` makes it."""
    commit = ["git", "rev-parse", "--verify", f"{start}^{{commit}}"]
    base = checked(host, commit, run.repository, CantRun, "git can't read the default branch")
    create = ["herdr", "worktree", "create", "--cwd", run.repository, "--branch", run.branch]
    where = ["--base", base.out.strip(), "--path", run.worktree, "--no-focus"]
    checked(host, [*create, *where], run.repository, CantRun, "herdr can't make the run's worktree")


def _exclude(run: RunPlace, host: Host) -> None:
    """Keeps the runs' worktrees out of what git shows untracked in the user's own worktree, by
    the repository's info/exclude, which no commit holds, where its line isn't there yet."""
    found = host(["git", "rev-parse", "--git-path", "info/exclude"], run.repository)
    path = os.path.join(run.repository, found.out.strip())
    with open(path, "a+", encoding="utf-8") as file:
        file.seek(0)
        if _EXCLUDED not in file.read().splitlines():
            file.write(f"\n{_EXCLUDED}\n")


def newest(repository: str, host: Host) -> RunPlace | None:
    """The run to pick up, from the runs' commits.

    Takes: the top of the user's repository, and the host.
    Gives: the run of the newest branch by its last commit, among the local branches `rn-*` and
    origin's, as the repository last fetched them, whose committed design tree,
    `.rn/<name>/design-tree.json` on the branch, holds a deliverable that isn't done; a run whose
    newest branch holds no such deliverable, or no design tree, is none to pick up. None where
    there's no such run, or the folder isn't a git repository.
    Changes: nothing.
    Refuses: Wrong where a branch's design tree isn't JSON, naming the branch and the path.
    """
    listed = host(
        ["git", "for-each-ref", "--sort=-committerdate", "--format=%(refname)", *_REFS], repository
    )
    seen: set[str] = set()
    for ref in listed.out.split() if listed.code == 0 else []:
        name = ref.rpartition("/")[2][len("rn-") :]
        if name in seen:
            continue
        seen.add(name)
        path = f".rn/{name}/design-tree.json"
        shown = host(["git", "show", f"{ref}:{path}"], repository)
        if shown.code != 0:
            continue
        try:
            tree = json.loads(shown.out)
        except ValueError as error:
            raise Wrong(f"{ref}:{path}: isn't JSON: {error}") from None
        if any(each["status"] != "done" for each in tree["deliverables"]):
            return RunPlace(repository, name)
    return None


def found(repository: str, host: Host) -> RunPlace | None:
    """The run to pick up, its worktree made again where none lies.

    Takes: the top of the user's repository, and the host.
    Gives: the run that `newest` gives, or None where it gives none.
    Changes: where the run's worktree is gone, prunes git's record of gone worktrees and adds the
    worktree again: on the local branch `rn-<name>` where it lies, else on a new local branch
    `rn-<name>` from origin's, so that a pick-up works in a fresh clone or on another machine;
    keeps the runs' worktrees out of the user's untracked files, as `new` does. Inside herdr, then
    has herdr open the worktree's workspace, leaving the focus where it is, as herdr opens only a
    worktree that lies there.
    Refuses: Wrong as `newest` refuses; CantRun where git can't make the worktree, or herdr can't
    open it, with what it said.
    """
    run = newest(repository, host)
    if run is None or os.path.isdir(run.worktree):
        return run
    host(["git", "worktree", "prune"], repository)
    # git takes a branch that only origin holds as a new local branch from origin's, tracking it.
    add = ["git", "worktree", "add", "-q", run.worktree, run.branch]
    checked(host, add, repository, CantRun, "git can't make the run's worktree again")
    _exclude(run, host)
    if _inside_herdr():
        opened = ["herdr", "worktree", "open", "--cwd", repository, "--path", run.worktree]
        what = "herdr can't open the run's worktree"
        checked(host, [*opened, "--no-focus"], repository, CantRun, what)
    return run


class Left(NamedTuple):
    """What of a cancelled run GitHub holds, as GitHub answered: `held`, each thing it holds, and
    `unchecked`, each thing that rn couldn't ask GitHub of, with why."""

    held: list[str]
    unchecked: list[str]


def removed(run: RunPlace, host: Host) -> Left:
    """Removes a run that the user cancels from this machine, and asks GitHub what it holds of it.

    Takes: the run, and the host.
    Gives: what of the run GitHub holds, which only the user removes, as GitHub itself answers, as
    a ref here may outlive the branch it records: in `held`, `origin/rn-<name>` where
    `git ls-remote` finds origin holding the branch, then the URL of the open pull request where
    `gh pr view rn-<name>` gives one; in `unchecked`, for each of the two that git or gh couldn't
    ask, such as with no network or no login, `the branch rn-<name> on GitHub, as git can't ask
    origin: <what git said>` or `the pull request of rn-<name> on GitHub, as gh can't ask GitHub:
    <what gh said>`, each one line. A pull request that gh gives closed or merged, such as an
    earlier run's of the same branch's name, isn't held.
    Changes: removes the run's worktree, with each change in it that isn't committed, and then its
    local branch `rn-<name>`; then, where origin holds no branch `rn-<name>`, deletes the
    repository's ref of origin's branch, so that no later read meets it; the user's own worktree
    and branch stay as they were. Inside herdr, has herdr open the worktree's workspace, leaving
    the focus where it is, and remove the worktree of the workspace it gives, as herdr removes a
    worktree by its workspace, which it closes.
    Refuses: CantRun where git or herdr fails to remove the worktree or the branch, with what it
    said, the branch then kept where the worktree stays.
    """
    top = run.repository
    if _inside_herdr():
        opened = ["herdr", "worktree", "open", "--cwd", top, "--path", run.worktree, "--no-focus"]
        given = checked(host, opened, top, CantRun, "herdr can't open the run's worktree")
        workspace = json.loads(given.out)["result"]["workspace"]["workspace_id"]
        remove = ["herdr", "worktree", "remove", "--workspace", workspace, "--force"]
        checked(host, remove, top, CantRun, "herdr can't remove the run's worktree")
    else:
        remove = ["git", "worktree", "remove", "--force", run.worktree]
        checked(host, remove, top, CantRun, "git can't remove the run's worktree")
    checked(host, ["git", "branch", "-D", run.branch], top, CantRun, "git can't delete the branch")
    left = Left([], [])
    _branch_left(run, host, left)
    _pull_request_left(run, host, left)
    return left


def _branch_left(run: RunPlace, host: Host, left: Left) -> None:
    """Adds to what's left whether origin holds the run's branch, as `git ls-remote` asks it, and
    deletes the repository's ref of origin's branch where origin holds none."""
    head = f"refs/heads/{run.branch}"
    asked = host(["git", "ls-remote", "--heads", "origin", head], run.repository)
    if asked.code != 0:
        said = _line(asked.out + asked.err)
        left.unchecked.append(f"the branch {run.branch} on GitHub, as git can't ask origin: {said}")
    elif head in [each.partition("\t")[2] for each in asked.out.splitlines()]:
        left.held.append(f"origin/{run.branch}")
    else:
        host(["git", "update-ref", "-d", f"refs/remotes/origin/{run.branch}"], run.repository)


def _pull_request_left(run: RunPlace, host: Host, left: Left) -> None:
    """Adds to what's left the run's branch's open pull request, as `gh pr view` gives it, where
    there's one; gh takes an open one of the branch before any closed or merged one."""
    asked = host(["gh", "pr", "view", run.branch, "--json", "state,url"], run.repository)
    if asked.code == 0:
        shown = json.loads(asked.out)
        if shown["state"] == "OPEN":
            left.held.append(shown["url"])
    elif not asked.err.startswith("no pull requests found"):
        said = _line(asked.out + asked.err)
        what = f"the pull request of {run.branch} on GitHub, as gh can't ask GitHub: {said}"
        left.unchecked.append(what)


def _line(said: str) -> str:
    """What a program said, as one line."""
    return " ".join(said.split())
