"""Decides how the run's work reaches GitHub: what each commit holds and says, the push of the
work's branch, and the run's one pull request."""

from __future__ import annotations

from collections.abc import Sequence

from repository.host import Host
from repository.place import RunPlace


def commit(run: RunPlace, paths: Sequence[str], message: str, host: Host) -> str:
    """Commits the paths in the run's worktree.

    Takes: the run, each path from the worktree's top to commit, the commit message, and the host.
    Gives: the new commit's hash.
    Changes: stages and commits the paths on the work's branch, and nothing else of the index.
    Refuses: Wrong where a path lies outside the worktree or none of them has a change, naming
    them; CantRun where git fails, such as a commit check of the repository refusing, with what it
    said.
    """
    raise NotImplementedError("repository.push.commit")


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
    raise NotImplementedError("repository.push.pause")


def put_up(run: RunPlace, deliverable: str, host: Host) -> str:
    """Puts a deliverable up for the user's sign-off, in the run's one pull request.

    Takes: the run, the path of the deliverable in the design tree, and the host.
    Gives: the URL of the pull request's changes, `<pull request>/files`.
    Changes: runs `gh auth status` first; then commits each change in the run's worktree as
    `rn: <deliverable's name>`, pushes the work's branch to `origin`, and opens the pull request
    into the default branch, titled by the first sentence of the design tree's goal, as
    `template.markdown.sentences` splits it, where the
    branch has none open.
    Refuses: Missing, before any commit or push, where `gh auth status` finds no login, with what
    it said; Wrong where the design tree holds no deliverable of the path; Missing where the
    repository has no remote `origin`, or gh may not open a pull request, with what gh said;
    CantRun where git or gh fails otherwise.
    """
    raise NotImplementedError("repository.push.put_up")
