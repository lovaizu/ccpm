"""Check 9: only the conductor commits or pushes on the session's repository."""

from shell import on_repo


def check(agent, runs, top):
    if agent and on_repo(runs, ("commit", "push"), top):
        return [
            (
                "only the conductor uses git, so every commit records a decision someone made; "
                f"{agent} may not commit or push"
            )
        ]
    return []
