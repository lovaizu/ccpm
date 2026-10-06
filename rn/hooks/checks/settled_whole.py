"""A settled open/ item is whole in the commit message that clears it."""
import os

from record import git


def norm(s):
    return " ".join(s.split())


def check(top, rel_sdir, msg):
    problems = []
    gone = git("diff", "--name-only", "--diff-filter=D", "HEAD~1", "HEAD", "--",
               rel_sdir + "/open", cwd=top).split()
    for path in gone:
        if norm(git("show", "HEAD~1:" + path, cwd=top)) not in norm(msg):
            problems.append(f"commit message: {os.path.basename(path)} left open/ but is not whole "
                            "in the message")
    return problems
