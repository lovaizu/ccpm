"""Check 2: open/ files are named {NN}-{kind}-{about}.md, the kind report, feedback, or notes."""
import re

from record import open_items

KINDS = ("report", "feedback", "notes")


def check(sdir):
    problems = []
    for name in open_items(sdir):
        m = re.match(r"^(\d{2})-([a-z]+)-[a-z0-9][a-z0-9-]*\.md$", name)
        if not m or m.group(2) not in KINDS:
            problems.append(f"open/{name}: not named {{NN}}-{{kind}}-{{about}}.md with kind "
                            + " | ".join(KINDS))
    return problems
