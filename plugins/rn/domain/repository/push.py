"""Decides how the run's work reaches GitHub: what each commit holds and says, the push of the
work's branch, the run's one pull request, a draft until the user marks it ready, and what the
final check reads of it: its whole diff and its CI."""

from __future__ import annotations

import json
import time
from collections.abc import Sequence
from urllib.parse import quote

from fault import CantRun, Missing, Wrong
from template.markdown import sentences
from tree import form

from repository.host import Host, Ran, checked
from repository.place import RunPlace

# How long ci waits for the pushed head's checks to start, and how often it looks, in seconds.
_WAIT = 120
_EVERY = 5
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
    files, as `rn: paused <name>`, where there's one, and pushes the work's branch, as `push`
    does.
    Refuses: as `push` refuses; CantRun where git fails otherwise.
    """
    _commit_all(run, f"rn: paused {run.name}", host)
    return push(run, host)


def put_up(run: RunPlace, deliverable: str, host: Host) -> list[str]:
    """Puts a deliverable up for the user's sign-off, in the run's one pull request.

    Takes: the run, the path of the deliverable in the design tree, and the host.
    Gives: the link of each file or folder that the deliverable is, its path and then each of its
    `more_paths`, on GitHub at the commit it pushed last: `<repository>/tree/<commit>/<path>` for
    a folder and `<repository>/blob/<commit>/<path>` for a file, as that commit holds each, its
    path percent-encoded, with no `/` closing it, and the repository's page being the pull
    request's URL up to `/pull/`. It gives none for the plan, of the kind `design-tree`, as the
    plan's message shows the plan and its file is rn's own, nor for a node of no file.
    Changes: runs `gh auth status` first; then commits each change in the run's worktree as `rn:
    <deliverable's name>`, pushes the work's branch to `origin`, and opens the pull request into the
    default branch as a draft, where the branch has none open, as `gh pr view` gives a closed or
    merged one of an earlier run of the same branch's name too: titled by the first sentence of the
    design tree's goal, as `template.markdown.sentences` splits it, its body the goal, then a line
    `Closes #N` for each issue of the tree's `context.issues.closes` and a line `Refs #N` for each
    of its `refs`, in their order. Where the tree's `context.pr` isn't the open pull request's URL,
    such as null, it then writes that URL there, commits it as `rn: the pull request of <name>`, and
    pushes it.
    Refuses: Missing, before any commit or push, where `gh auth status` finds no login, with what
    it said; Wrong, before any commit or push, where the design tree's goal is open, as
    `tree.form.goal` refuses it, or the tree holds no deliverable of the path; Missing where the
    repository has no remote `origin`, or gh may not open a pull request, with what gh said;
    Wrong where the commit pushed holds nothing at a path of the deliverable, naming it; CantRun
    where git or gh fails otherwise.
    """
    checked(
        host,
        ["gh", "auth", "status"],
        run.worktree,
        Missing,
        "gh has no login to open the pull request",
    )
    tree = form.read(run.tree)
    goal = form.goal(tree)
    node = form.deliverable(tree, deliverable)
    _commit_all(run, f"rn: {node['name']}", host)
    pushed = push(run, host)
    shown = host(["gh", "pr", "view", run.branch, "--json", "url,state"], run.worktree)
    held = json.loads(shown.out) if shown.code == 0 else {"state": None}
    if held["state"] == "OPEN":
        url = held["url"]
    else:
        made = checked(
            host,
            [
                "gh",
                "pr",
                "create",
                "--draft",
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
    if tree["context"]["pr"] != url:
        tree["context"]["pr"] = url
        form.write(run.tree, tree)
        _commit_all(run, f"rn: the pull request of {run.name}", host)
        pushed = push(run, host)
    if node["kind"] == "design-tree" or node.get("file") is False:
        return []
    repository = url.rsplit("/pull/", 1)[0]
    return [_link(run, repository, pushed, each, host) for each in _paths(node)]


def _paths(node: form.Deliverable) -> list[str]:
    """Each path that the deliverable lies at, with no `/` closing a folder."""
    return [each.rstrip("/") for each in [node["path"], *node.get("more_paths", [])]]


def _link(run: RunPlace, repository: str, commit: str, path: str, host: Host) -> str:
    """The link on GitHub of the file or folder at the path in the commit, refusing Wrong where the
    commit holds nothing there."""
    listed = _git(host, run, "ls-tree", commit, "--", path).out.split()
    if not listed:
        raise Wrong(
            f"{path}: the work's pushed commit holds nothing there; make the deliverable there, or"
            " mend its path in the design tree"
        )
    shown = "tree" if listed[1] == "tree" else "blob"
    return f"{repository}/{shown}/{commit}/{quote(path)}"


def diff(run: RunPlace, host: Host) -> str:
    """The pull request's whole diff, as the final check reads it.

    Takes: the run, and the host.
    Gives: the diff of the work's branch from where it parts from the default branch that origin's
    HEAD names, as the pull request shows it.
    Changes: commits each change in the run's worktree as `rn: the final check of <name>`, where
    there's one, such as a stray file removed, and pushes the work's branch, as `push` does.
    Refuses: as `push` refuses; CantRun where git fails otherwise.
    """
    _commit_all(run, f"rn: the final check of {run.name}", host)
    push(run, host)
    return _git(host, run, "diff", "refs/remotes/origin/HEAD...HEAD").out


def ci(run: RunPlace, host: Host) -> str:
    """What the pull request's CI found, once it's done.

    Takes: the run, and the host.
    Gives: `no CI started within 120 seconds of the push` as a line, where the pushed head's
    checks don't start within it, as with no CI; else each check of the pull request's head, by
    its name, once each, in gh's order, with how it ended: `passed`, `skipped`, `cancelled`, as
    GitHub Actions ends a job past its time limit too, `timed out`, or `still running`, where gh's
    watch stopped before it ended, each a line `<name>\t<end>`, where none failed. A check
    cancelled, timed out, or still running neither passed nor failed, and only the user runs it
    again.
    Changes: views `gh pr view <the work's branch> --json headRefOid,statusCheckRollup` in the
    run's worktree every 5 seconds until the pull request's head is the run's HEAD, as pushed, and
    holds a check, at most 120 seconds, as GitHub takes a moment after a push to move the head and
    to start its checks, while gh's watch reads the head before the push or finds no check; then
    runs `gh pr checks <the work's branch> --watch`, which waits until each check is done, then
    reads each check's end by
    `gh pr checks <the work's branch> --json name,state,bucket,link`, as gh's watch prints a
    cancelled check as `fail` and ends 0 where no other failed.
    Refuses: Wrong where a check failed, naming each once, then each that ended neither passing
    nor failing, with how; CantRun where gh can't give the pull request or its checks, such as
    where the branch has no pull request, or gh has no login or can't reach GitHub, with what gh
    said.
    """
    if not _started(run, host):
        return f"no CI started within {_WAIT} seconds of the push\n"
    host(["gh", "pr", "checks", run.branch, "--watch"], run.worktree)
    read = ["gh", "pr", "checks", run.branch, "--json", "name,state,bucket,link"]
    given = host(read, run.worktree)
    if given.code != 0:
        raise CantRun(f"gh can't give the pull request's CI: {(given.out + given.err).strip()}")
    ends = {each["name"]: _end(each) for each in json.loads(given.out)}
    failed = [name for name, end in ends.items() if end == "failed"]
    others = [f"{name} {end}" for name, end in ends.items() if end not in _SETTLED]
    if failed:
        what = f"the pull request's CI fails at {', '.join(failed)}; mend each in the deliverable"
        what += " whose file it concerns"
        if others:
            what += "; these ended neither passing nor failing, for the user to run again: "
            what += ", ".join(others)
        raise Wrong(what)
    return "".join(f"{name}\t{end}\n" for name, end in ends.items())


def _started(run: RunPlace, host: Host) -> bool:
    """Whether the pull request's head is the run's HEAD with a check, within the wait, looking
    again at each interval."""
    pushed = _git(host, run, "rev-parse", "HEAD").out.strip()
    view = ["gh", "pr", "view", run.branch, "--json", "headRefOid,statusCheckRollup"]
    until = time.monotonic() + _WAIT
    while True:
        shown = host(view, run.worktree)
        if shown.code != 0:
            raise CantRun(f"gh can't give the pull request's CI: {(shown.out + shown.err).strip()}")
        head = json.loads(shown.out)
        if head["headRefOid"] == pushed and head["statusCheckRollup"]:
            return True
        if time.monotonic() + _EVERY > until:
            return False
        time.sleep(_EVERY)


# The ends of a check that settle it, as passing or failing, with no one to run it again.
_SETTLED = ("passed", "skipped", "failed")
# How a check ended, by gh's bucket of it, but for one that timed out, which gh buckets as failed.
_ENDS = {
    "pass": "passed",
    "skipping": "skipped",
    "fail": "failed",
    "cancel": "cancelled",
    "pending": "still running",
}


def _end(check: dict[str, str]) -> str:
    """How a check ended, from its `state` and gh's `bucket` of it: `passed`, `skipped`,
    `failed`, `cancelled`, `timed out`, or `still running`, where gh's watch stopped before it
    ended."""
    return "timed out" if check["state"] == "TIMED_OUT" else _ENDS[check["bucket"]]


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


def push(run: RunPlace, host: Host) -> str:
    """Pushes the work's branch to origin.

    Takes: the run, and the host.
    Gives: the hash of the commit that the branch's remote now holds.
    Changes: pushes the work's branch to `origin`, setting it upstream.
    Refuses: Missing where the repository has no remote `origin`, or the push is refused for want
    of a login or a permission, with what git said; CantRun where git fails otherwise.
    """
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
