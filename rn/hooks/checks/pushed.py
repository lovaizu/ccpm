"""Check 8: every commit is pushed."""

from record import git


def check(top):
    if not git("rev-parse", "--abbrev-ref", "@{u}", cwd=top).strip():
        return [
            (
                "at the end of the turn: the branch has no remote branch; push it, so a fresh "
                "conversation on another machine goes on from it"
            )
        ]
    ahead = git("rev-list", "--count", "@{u}..HEAD", cwd=top).strip()
    if ahead and ahead != "0":
        return [
            (
                f"at the end of the turn: {ahead} commit(s) not pushed; push them, so nothing decided "
                "lives only on this machine"
            )
        ]
    return []
