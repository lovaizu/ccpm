"""Every ID referred to exists, and once tasks are planned, every acceptance criterion is served by a
task."""
import os
import re

from record import criteria, front_matter, section, steering
from checks.steering_form import TASK

ID = re.compile(r"\b([AM]\d+)\b")


def check(top, sdir):
    problems = []
    text = steering(sdir)
    front = front_matter(text) or {}
    defined = set(criteria(text))
    tasks = section(text, "# Tasks", 1)
    served = set(ID.findall("\n".join(tasks)))
    for i in sorted(served - defined):
        problems.append(f"steering.md: task refers to {i}, which no acceptance criterion has")
    vpath = os.path.join(top, front.get("verification", "docs/verification.md"))
    if os.path.isfile(vpath):
        for i in sorted(set(ID.findall(open(vpath).read())) - defined):
            problems.append(f"verification: refers to {i}, which steering.md does not define")
    if any(TASK.match(l) and "sign-off" not in l.lower() for l in tasks):
        for i in sorted(defined - served):
            problems.append(f"steering.md: criterion {i} is served by no task")
    return problems
