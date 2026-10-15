"""The plan keeps the form of the template in checklists/plan.md: its front matter, its headings,
its task headings, and IDs given once."""

from __future__ import annotations

import re

from checks import Record, criteria, front_matter, section, tasks

KEYS = (
    "rn",
    "pr",
    "status",
    "artifact-language",
    "conversation-language",
    "readme",
    "design",
    "verification",
)
HEADINGS = (
    "# Goal",
    "# Acceptance criteria",
    "## Attractive quality",
    "## Must-be quality",
    "# Assumptions",
    "# Rules",
    "# Tasks",
    "# Not yet specified",
)
TASK = re.compile(r"### \[[ x]\] #(\d+): \S")
WHY = "since rn's commands and checks read the plan by the template of checklists/plan.md"


def check(record: Record) -> list[str]:
    plan = f"{record.session}/steering.md"
    fields = front_matter(record.plan)
    if fields is None:
        problems = [
            (
                f"rn: {plan} has no front matter between `---` lines at its top; "
                f"write it as the template gives, {WHY}."
            )
        ]
    else:
        problems = [
            f"rn: {plan} has no `{key}` key in its front matter; add it, {WHY}."
            for key in KEYS
            if key not in fields
        ]
        if fields.get("status", "running") not in ("running", "finished"):
            problems.append(
                f"rn: {plan} has the status `{fields['status']}`; "
                f"make it `running`, or `finished` once the Deliverable sign-off is approved, {WHY}."
            )
    lines = record.plan.split("\n")
    problems += [
        f"rn: {plan} has no `{heading}` heading; add it where the template puts it, {WHY}."
        for heading in HEADINGS
        if heading not in lines
    ]
    ids = []
    for heading, _ in tasks(record.plan):
        task = TASK.match(heading)
        if task:
            ids.append(f"#{task[1]}")
        else:
            problems.append(
                f"rn: {plan} has the task heading `{heading}`; "
                f"write it as `### [ ] #N: name`, or `### [x] #N: name` once done, {WHY}."
            )
    ids += criteria(section(record.plan, "# Acceptance criteria"))
    problems += [
        f"rn: {plan} gives the ID {given} more than once; give each task and criterion an ID "
        f"of its own, never reused, {WHY}."
        for given in sorted(set(ids))
        if ids.count(given) > 1
    ]
    return problems
