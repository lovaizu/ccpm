"""Check 8: every commit is pushed."""
from record import git


def check(top):
    if not git("rev-parse", "--abbrev-ref", "@{u}", cwd=top).strip():
        return ["the branch has no remote branch; push it"]
    ahead = git("rev-list", "--count", "@{u}..HEAD", cwd=top).strip()
    if ahead and ahead != "0":
        return [f"{ahead} commit(s) not pushed; push them"]
    return []
