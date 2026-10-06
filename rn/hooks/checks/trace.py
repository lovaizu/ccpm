"""Check 3: every ID referred to exists; the verification document keeps its form; every acceptance
criterion has a scene or a machine check, and a task once tasks are planned; a question item names
on its `Serves:` line the criteria it rests on, or `goal`."""
import os
import re

from record import criteria, front_matter, open_items, section, steering
from checks.steering_form import TASK

ID = re.compile(r"\b([AM]\d+)\b")


def check(top, sdir):
    problems = []
    text = steering(sdir)
    front = front_matter(text) or {}
    defined = set(criteria(text))
    tasks_text = "\n".join(section(text, "# Tasks", 1))
    for i in sorted(set(ID.findall(tasks_text)) - defined):
        problems.append(f"steering.md: task refers to {i}, which no acceptance criterion has")
    vpath = os.path.join(top, front.get("verification", "docs/verification.md"))
    if os.path.isfile(vpath):
        vtext = open(vpath).read()
        heads = re.findall(r"^### ([AM]\d+):", vtext, re.M)
        named = set(ID.findall(vtext))
        for i in sorted(named - defined):
            problems.append(f"verification: refers to {i}, which steering.md does not define")
        if "## Scenes" not in vtext.splitlines():
            problems.append("verification: `## Scenes` is missing")
        if "## Machine checks" not in vtext.splitlines():
            problems.append("verification: `## Machine checks` is missing")
        for i in sorted(d for d in defined if d.startswith("A") and d not in heads):
            problems.append(f"verification: attractive criterion {i} has no `### {i}:` scene")
        for i in sorted(d for d in defined if d.startswith("M") and d not in named):
            problems.append(f"verification: must-be criterion {i} is named in no scene or check")
    for name in open_items(sdir):
        if "-notes-question" not in name:
            continue
        first = (open(os.path.join(sdir, "open", name)).read().strip().splitlines() or [""])[0]
        m = re.match(r"^Serves: (.+)$", first)
        named = set(ID.findall(m.group(1))) if m else set()
        if not m or (m.group(1).strip() != "goal" and not named):
            problems.append(f"open/{name}: the first line must be `Serves:` with the criterion IDs "
                            "the question rests on, or `goal`")
        for i in sorted(named - defined):
            problems.append(f"open/{name}: serves {i}, which steering.md does not define; ask what "
                            "the result must do and write it as a criterion before offering ways")
    planned = any(TASK.match(l) and "sign-off" not in l.lower()
                  for l in section(text, "# Tasks", 1))
    if planned:
        served = set(ID.findall(tasks_text))
        for i in sorted(defined - served):
            problems.append(f"steering.md: criterion {i} is served by no task")
    return problems
