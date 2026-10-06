"""Checks 4 to 7 run once the commit is made; a conductor command that also pushes would carry a
breach to the pull request before they could stop it."""
from shell import on_repo


def check(agent, runs, top):
    if not agent and on_repo(runs, ("commit",), top) and on_repo(runs, ("push",), top):
        return ["commit and push in separate commands, so rn's checks run on the commit before "
                "it is pushed"]
    return []
