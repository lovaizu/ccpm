"""Decides how the run's work reaches GitHub: what each commit holds and says, the push of the
work's branch, the run's one pull request, a draft until the user marks it ready, what the final
check reads of it, its whole diff and its CI, and the run's work kept on a stop."""

from __future__ import annotations

import json
import time
from typing import Any
from urllib.parse import quote

from fault import CantRun, Missing, Wrong
from host import Host, Ran, checked
from place import RunPlace

# How long ci waits for the pushed head's checks to start, and how often it looks, in seconds.
_WAIT = 120
_EVERY = 5
# What git says where origin refuses a push for want of a login or a permission, in lower case:
# a remote that rejects the refs, as a folder that may not be written does, among them.
_REFUSED = ("permission", "could not read username", "authentication failed", "remote rejected")


def stop(run: RunPlace, host: Host) -> str:
    """Keeps the run's work where any conversation picks it up.

    Takes: the run, and the host.
    Gives: the hash of the commit that the branch's remote now holds.
    Changes: commits each change in the run's worktree, the run's folder and the deliverables'
    files, as `rn: stopped <name>`, where there's one, and pushes the work's branch, as `push`
    does.
    Refuses: as `push` refuses; CantRun where git fails otherwise.
    """
    _commit_all(run, f"rn: stopped {run.name}", host)
    return push(run, host)


def put_up(run: RunPlace, steering: dict[str, Any], deliverable: str, host: Host) -> list[str]:
    """Puts a deliverable up in the run's one pull request.

    Takes: the run, its steering, the deliverable's path as its step names it, and the host.
    Gives: the link of the deliverable on GitHub at the commit it pushed:
    `<repository>/tree/<commit>/<path>` for a folder and `<repository>/blob/<commit>/<path>` for a
    file, as that commit holds it, its path percent-encoded, with no `/` closing it, the
    repository's page being the pull request's URL up to `/pull/`.
    Changes: runs `gh auth status` first; then commits each change in the run's worktree as `rn:
    <path>`, pushes the work's branch to `origin`, and opens the pull request into the default
    branch as a draft, where the branch has none open, as `gh pr view` gives a closed or merged
    one of an earlier run of the same branch's name too: titled by the words of the need that the
    user picked, its body the run's outcome, then a line `Closes #N` for each issue that the run
    closes and a line `Refs #N` for each it refers to, in their order.
    Refuses: Missing, before any commit or push, where `gh auth status` finds no login, with what
    it said; Wrong, before any commit or push, where no need is picked, or no step names the
    deliverable; Missing where the repository has no remote `origin`, or gh may not open a pull
    request, with what gh said; Wrong where the commit pushed holds nothing at the deliverable's
    path; CantRun where gh can't tell whether the branch has a pull request, so that it never
    opens a second, or where git or gh fails otherwise.
    """
    what = "gh has no login to open the pull request"
    checked(host, ["gh", "auth", "status"], run.worktree, Missing, what)
    title = _picked(steering["ost"])
    named = [each["path"] for step in steering["state"]["steps"] for each in step["deliverables"]]
    if deliverable not in named:
        raise Wrong(
            f"no step names the deliverable {deliverable!r}; give its path as its step names it"
        )
    _commit_all(run, f"rn: {deliverable}", host)
    pushed = push(run, host)
    shown = host(["gh", "pr", "view", run.branch, "--json", "url,state"], run.worktree)
    if shown.code != 0 and not shown.err.startswith("no pull requests found"):
        said = (shown.out + shown.err).strip()
        raise CantRun(f"gh can't tell whether the branch has a pull request: {said}")
    held = json.loads(shown.out) if shown.code == 0 else {"state": None}
    url = held["url"] if held["state"] == "OPEN" else _opened(run, steering, title, host)
    repository = url.rsplit("/pull/", 1)[0]
    return [_link(run, repository, pushed, deliverable.rstrip("/"), host)]


def _picked(ost: dict[str, Any]) -> str:
    """The words of the need that the user picked, refusing Wrong where none is picked."""
    stack = list(ost["opportunities"])
    while stack:
        each = stack.pop()
        if each["id"] == ost["target"]:
            return each["opportunity"]
        stack += each["opportunities"]
    raise Wrong("no need is picked yet; put a deliverable up once the user picks one")


def _opened(run: RunPlace, steering: dict[str, Any], title: str, host: Host) -> str:
    """Opens the run's pull request as a draft, and gives its URL."""
    body = _body(steering["ost"]["outcome"], steering["state"]["issues"])
    create = ["gh", "pr", "create", "--draft", "--head", run.branch, "--title", title]
    made = checked(
        host, [*create, "--body", body], run.worktree, Missing, "gh may not open the pull request"
    )
    return made.out.strip()


def _link(run: RunPlace, repository: str, commit: str, path: str, host: Host) -> str:
    """The link on GitHub of the file or folder at the path in the commit, refusing Wrong where the
    commit holds nothing there."""
    listed = _git(host, run, "ls-tree", commit, "--", path).out.split()
    if not listed:
        raise Wrong(
            f"{path}: the work's pushed commit holds nothing there; make the deliverable there, or"
            " mend its path in its step"
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
    """The pull request's body: the run's outcome, then a line naming each issue that the run
    closes and each that it refers to."""
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
