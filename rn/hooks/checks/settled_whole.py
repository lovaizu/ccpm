"""Check 5: a settled open/ item is whole in the commit message, and a settled report on a question
lets no More go."""
import os
import re

from record import git

ITEM = re.compile(r"^\d{2}-[a-z]+-[a-z0-9-]*\.md:$")


def norm(s):
    return " ".join(s.split())


def check(top, rel_sdir, msg):
    problems = []
    gone = git("diff", "--name-only", "--diff-filter=D", "HEAD~1", "HEAD", "--",
               rel_sdir + "/open", cwd=top).split()
    flat = norm(msg)
    lines = msg.splitlines()
    for path in gone:
        name = os.path.basename(path)
        body = git("show", "HEAD~1:" + path, cwd=top)
        if norm(body) not in flat:
            problems.append(f"commit message: {name} left open/ but is not whole in the message")
        elif "-report-question" in name and name + ":" in lines:
            for line in lines[lines.index(name + ":") + 1:]:
                if ITEM.match(line) or line.startswith("● "):
                    break
                if "→ let go" in line:
                    problems.append(f"commit message: a More on {name} is let go; fix the question "
                                    "or ask the user what the result must do, since the user meets "
                                    "what it leaves")
                    break
    return problems
