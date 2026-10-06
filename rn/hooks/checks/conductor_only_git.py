"""Only the conductor commits or pushes on the session's repository."""
from shell import on_repo


def check(agent, runs, top):
    if agent and on_repo(runs, ("commit", "push"), top):
        return [f"only the conductor uses git; {agent} may not commit or push"]
    return []
