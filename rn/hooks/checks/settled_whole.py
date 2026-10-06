"""Check 5: a settled open/ item is whole in the commit message."""
import os

from record import git


def norm(s):
    return " ".join(s.split())


def check(top, rel_sdir, msg):
    problems = []
    gone = git("diff", "--name-only", "--diff-filter=D", "HEAD~1", "HEAD", "--",
               rel_sdir + "/open", cwd=top).split()
    flat = norm(msg)
    for path in gone:
        body = git("show", "HEAD~1:" + path, cwd=top)
        if norm(body) not in flat:
            problems.append(f"commit message: {os.path.basename(path)} left open/ but is not whole "
                            "in the message")
    return problems
