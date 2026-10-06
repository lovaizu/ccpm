"""Check 6: a stop commit leaves in open/ only what its kind allows; at a sign-off the latest
default branch is merged, and every Good and More in the proposal names an acceptance criterion by
its ID."""
import re
import subprocess

from record import criteria, git, last_line, open_items, steering
from checks.trace import ID

PROPOSAL_POINT = re.compile(r"^- (Good|More)\b(.*?):")


def check(top, sdir, msg):
    problems = []
    last = last_line(msg)
    names = open_items(sdir)
    kinds = [n.split("-")[1] for n in names if n.count("-") >= 2]
    if "waiting for #" in last or "── approved →" in last:
        bad = [n for n, k in zip(names, kinds) if k != "notes" or "proposal" in n]
        if bad:
            problems.append("stop at a sign-off: open/ must hold only notes of design points, not "
                            + ", ".join(bad))
        if "waiting for #" in last:
            defined = set(criteria(steering(sdir)))
            for line in msg.splitlines():
                m = PROPOSAL_POINT.match(line)
                if m and not (set(ID.findall(m.group(2))) & defined):
                    problems.append(f"proposal: `{line.strip()[:60]}` names no acceptance criterion "
                                    "by its ID")
            head = git("rev-parse", "--abbrev-ref", "origin/HEAD", cwd=top).strip()
            if head and subprocess.run(["git", "merge-base", "--is-ancestor", head, "HEAD"],
                                       cwd=top).returncode != 0:
                problems.append(f"stop at a sign-off: {head} is not merged into the branch")
    if "── feedback in " in last and "feedback" not in kinds:
        problems.append("stop after /rn:gm: open/ holds no feedback item")
    return problems
