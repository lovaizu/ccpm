"""Decides how the run's work reaches GitHub: what each commit holds and says, the push of the
work's branch, and the run's one pull request."""

from __future__ import annotations

import json
from collections.abc import Sequence

from fault import CantRun, Missing, Wrong
from template.markdown import sentences
from tree import form

from repository.host import Host, Ran, checked
from repository.place import RunPlace

# What git says where origin refuses a push for want of a login or a permission, in lower case:
# a remote that rejects the refs, as a folder that may not be written does, among them.
_REFUSED = ("permission", "could not read username", "authentication failed", "remote rejected")


def commit(run: RunPlace, paths: Sequence[str], message: str, host: Host) -> str:
    """Commits the paths in the run's worktree.

    Takes: the run, each path from the worktree's top to commit, the commit message, and the host.
    Gives: the new commit's hash.
    Changes: stages and commits the paths on the work's branch, and nothing else of the index.
    Refuses: Wrong where a path lies outside the worktree or none of them has a change, naming
    them; CantRun where git fails, such as a commit check of the repository refusing, with what it
    said.
    """
    outside = [each for each in paths if not run.holds(each)]
    if outside:
        raise Wrong(f"{', '.join(outside)}: lies outside the run's worktree; commit only its paths")
    _git(host, run, "add", "--", *paths)
    if host(["git", "diff", "--cached", "--quiet", "--", *paths], run.worktree).code == 0:
        raise Wrong(f"{', '.join(paths)}: holds no change to commit")
    _git(host, run, "commit", "-q", "-m", message, "--", *paths)
    return _git(host, run, "rev-parse", "HEAD").out.strip()


def pause(run: RunPlace, host: Host) -> str:
    """Keeps the run's work where any conversation picks it up.

    Takes: the run, and the host.
    Gives: the hash of the commit that the branch's remote now holds.
    Changes: commits each change in the run's worktree, the run's folder and the deliverables'
    files, as `rn: paused <name>`, where there's one, and pushes the work's branch to `origin`,
    setting it upstream.
    Refuses: Missing where the repository has no remote `origin`, or the push is refused for want
    of a login or a permission, with what git said; CantRun where git fails otherwise.
    """
    _commit_all(run, f"rn: paused {run.name}", host)
    return _push(run, host)


def put_up(run: RunPlace, deliverable: str, host: Host) -> str:
    """Puts a deliverable up for the user's sign-off, in the run's one pull request.

    Takes: the run, the path of the deliverable in the design tree, and the host.
    Gives: the URL of the pull request's changes, `<pull request>/files`.
    Changes: runs `gh auth status` first; then commits each change in the run's worktree as
    `rn: <deliverable's name>`, pushes the work's branch to `origin`, and opens the pull request
    into the default branch, where the branch has none open: titled by the first sentence of the
    design tree's goal, as `template.markdown.sentences` splits it, its body the goal, then a
    line `Closes #N` for each issue of the tree's `context.issues.closes` and a line `Refs #N` for
    each of its `refs`, in their order. Where the tree's `context.pr` is null, it then writes the
    pull request's URL there, commits it as `rn: the pull request of <name>`, and pushes it.
    Refuses: Missing, before any commit or push, where `gh auth status` finds no login, with what
    it said; Wrong where the design tree holds no deliverable of the path; Missing where the
    repository has no remote `origin`, or gh may not open a pull request, with what gh said;
    CantRun where git or gh fails otherwise.
    """
    checked(
        host,
        ["gh", "auth", "status"],
        run.worktree,
        Missing,
        "gh has no login to open the pull request",
    )
    tree = form.read(run.tree)
    node = form.deliverable(tree, deliverable)
    _commit_all(run, f"rn: {node['name']}", host)
    _push(run, host)
    shown = host(["gh", "pr", "view", run.branch, "--json", "url"], run.worktree)
    if shown.code == 0:
        url = json.loads(shown.out)["url"]
    else:
        goal = tree["goal"]["decided"]
        made = checked(
            host,
            [
                "gh",
                "pr",
                "create",
                "--head",
                run.branch,
                "--title",
                sentences(goal)[0],
                "--body",
                _body(goal, tree["context"]["issues"]),
            ],
            run.worktree,
            Missing,
            "gh may not open the pull request",
        )
        url = made.out.strip()
    if tree["context"]["pr"] is None:
        tree["context"]["pr"] = url
        form.write(run.tree, tree)
        _commit_all(run, f"rn: the pull request of {run.name}", host)
        _push(run, host)
    return f"{url}/files"


def _body(goal: str, issues: dict[str, list[int]]) -> str:
    """The pull request's body: the goal, then a line naming each issue that the run closes and
    each that it refers to."""
    lines = [f"Closes #{each}" for each in issues["closes"]]
    lines += [f"Refs #{each}" for each in issues["refs"]]
    return "\n\n".join([goal, "\n".join(lines)]) if lines else goal


def _commit_all(run: RunPlace, message: str, host: Host) -> None:
    """Commits each change in the run's worktree with the message, where there's one."""
    _git(host, run, "add", "-A")
    if host(["git", "diff", "--cached", "--quiet"], run.worktree).code != 0:
        _git(host, run, "commit", "-q", "-m", message)


def _push(run: RunPlace, host: Host) -> str:
    """Pushes the work's branch to origin, setting it upstream, and gives the hash it holds."""
    if host(["git", "remote", "get-url", "origin"], run.worktree).code != 0:
        raise Missing("the repository has no remote origin to push the run's work to; add one")
    pushed = host(["git", "push", "-q", "-u", "origin", run.branch], run.worktree)
    if pushed.code != 0 and any(each in pushed.err.lower() for each in _REFUSED):
        raise Missing(
            "origin refuses the push of the run's work, for want of a login or a permission:"
            f" {pushed.err.strip()}"
        )
    if pushed.code != 0:
        raise CantRun(f"git can't push the run's work: {pushed.err.strip()}")
    return _git(host, run, "rev-parse", "HEAD").out.strip()


def _git(host: Host, run: RunPlace, *words: str) -> Ran:
    """Runs git in the run's worktree, raising CantRun with what it said where it fails."""
    return checked(host, ["git", *words], run.worktree, CantRun, f"git {words[0]} fails")
