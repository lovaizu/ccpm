"""Check 3: every ID referred to exists; the verification document keeps the form the verification
checklist gives; every acceptance criterion has a scene or a machine check, and a task once tasks
are planned; a question item names on its `Serves:` line the criteria it rests on, or `goal`."""

import os
import re

from record import criteria, front_matter, open_items, read, section, steering

from checks.steering_form import TASK

ID = re.compile(r"\b([AM]\d+)\b")


def verification(vtext, defined, old_record):
    """The problems with the verification document; a record from rn 0.9.0 is taken up as it
    stands, so its document needs no front matter."""
    problems = []
    front = front_matter(vtext)
    if not old_record and (
        front is None or front.get("name") != "verification" or "version" not in front
    ):
        problems.append(
            "verification: open it with front matter giving `name: verification` and its "
            "`version`, since turn uses the deliverable against it as a checklist"
        )
    heads = re.findall(r"^### ([AM]\d+):", vtext, re.MULTILINE)
    named = set(ID.findall(vtext))
    for i in sorted(named - defined):
        problems.append(f"verification: refers to {i}, which steering.md does not define")
    lines = vtext.splitlines()
    for heading in ("## Scenes", "## Machine checks"):
        if heading not in lines:
            problems.append(
                f"verification: `{heading}` is missing, so the checks cannot be run again after "
                "a change"
            )
    for i in sorted(d for d in defined if d.startswith("A") and d not in heads):
        problems.append(
            f"verification: attractive criterion {i} has no `### {i}:` scene, so nothing shows "
            "the user getting it"
        )
    for i in sorted(d for d in defined if d.startswith("M") and d not in named):
        problems.append(
            f"verification: must-be criterion {i} is named in no scene or check, so it breaks "
            "unseen"
        )
    return problems


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
        problems += verification(read(vpath), defined, front.get("rn", "").startswith("0.9."))
    for name in open_items(sdir):
        if "-notes-question" not in name:
            continue
        first = (read(os.path.join(sdir, "open", name)).strip().splitlines() or [""])[0]
        m = re.match(r"^Serves: (.+)$", first)
        named = set(ID.findall(m.group(1))) if m else set()
        if not m or (m.group(1).strip() != "goal" and not named):
            problems.append(
                f"open/{name}: the first line must be `Serves:` with the criterion IDs "
                "the question rests on, or `goal`"
            )
        for i in sorted(named - defined):
            problems.append(
                f"open/{name}: serves {i}, which steering.md does not define; ask what "
                "the result must do and write it as a criterion before offering ways"
            )
    planned = any(
        TASK.match(l) and "sign-off" not in l.lower() for l in section(text, "# Tasks", 1)
    )
    if planned:
        served = set(ID.findall(tasks_text))
        for i in sorted(defined - served):
            problems.append(
                f"steering.md: criterion {i} is served by no task, so it is never built"
            )
    return problems
