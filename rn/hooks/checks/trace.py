"""Every criterion the record refers to is one the plan has, and each criterion is where rn's
steps look for it: a scene or machine check in the verification document, and, once tasks are
planned, a task serving it."""

import re

from checks import TASK, Record, criteria, field, front_matter, section, stop, task_blocks

ID = re.compile(r"[AM]\d+")
PLAN_STEP = "Planning the tasks"
DESIGN_STEP = "Working out the design"
# rn 0.9.x wrote the verification document without front matter.
WITHOUT_FRONT_MATTER = re.compile(r"0\.9\.\d+")


def tasks(record: Record, ids: set[str]) -> list[str]:
    where = f"{record.folder}/steering.md"
    problems = []
    served = set()
    beyond_sign_offs = False
    for block in task_blocks(record.plan):
        task = TASK.match(block)
        if task is None:
            continue
        beyond_sign_offs = beyond_sign_offs or not task.group(2).endswith("sign-off")
        serves = re.search(r"^Serves:(.*)$", block, re.MULTILINE)
        for criterion in ID.findall(serves.group(1) if serves else ""):
            served.add(criterion)
            if criterion not in ids:
                problems.append(
                    stop(
                        PLAN_STEP,
                        where,
                        f"has #{task.group(1)} serve {criterion}, which no criterion of the plan"
                        " has",
                        "serve only criteria the plan lists under `# Acceptance criteria`",
                        "each task is judged by the criteria it serves",
                    )
                )
    for criterion in criteria(record.plan) if beyond_sign_offs else []:
        if criterion not in served:
            problems.append(
                stop(
                    PLAN_STEP,
                    where,
                    f"has no task serving {criterion}",
                    f"add {criterion} to the `Serves:` line of the task that brings it to hold,"
                    " or plan one",
                    "a criterion no task serves is never built",
                )
            )
    return problems


def questions(record: Record, ids: set[str]) -> list[str]:
    problems = []
    fix = "open it with `Serves:` and the IDs of the criteria the question rests on, or `goal`"
    why = "the question is judged by what it serves"
    for name in sorted(record.open):
        if not name.endswith("-notes-question.md"):
            continue
        where = f"{record.folder}/open/{name}"
        first = re.fullmatch(r"Serves:(.*)", record.open[name].split("\n", 1)[0])
        served = re.findall(r"[^,\s]+", first.group(1)) if first else []
        if not served:
            broken = "does not open with `Serves:` and what it serves"
            problems.append(stop("Asking the user", where, broken, fix, why))
        for token in served:
            if token not in ids and token != "goal":
                broken = f"serves {token}, which is neither a criterion of the plan nor `goal`"
                problems.append(stop("Asking the user", where, broken, fix, why))
    return problems


def verification(record: Record, where: str, text: str) -> list[str]:
    problems = []
    fields = front_matter(text)
    if fields is None and not WITHOUT_FRONT_MATTER.fullmatch(record.rn or ""):
        fields = {}
    if fields is not None and (fields.get("name") != "verification" or "version" not in fields):
        problems.append(
            stop(
                DESIGN_STEP,
                where,
                "does not open with front matter giving `name: verification` and its `version`",
                "put back the front matter of the template in rn's checklists/verification.md",
                "turn uses the deliverable against the document as a checklist only by that"
                " front matter",
            )
        )
    lines = text.splitlines()
    for heading in ("## Scenes", "## Machine checks"):
        if heading not in lines:
            problems.append(
                stop(
                    DESIGN_STEP,
                    where,
                    f"has no `{heading}` heading",
                    "put it back as the template in rn's checklists/verification.md gives it",
                    "rn's checks find each criterion's scene and machine check under it",
                )
            )
    scenes = section(text, "## Scenes")
    headed = re.findall(r"^### ([AM]\d+):", scenes, re.MULTILINE)
    for criterion in headed:
        if criterion not in criteria(record.plan):
            problems.append(
                stop(
                    DESIGN_STEP,
                    where,
                    f"has a scene for {criterion}, which no criterion of the plan has",
                    "head each scene with the ID of an attractive criterion of the plan",
                    "rn's checks find each criterion's scene by its ID",
                )
            )
    for criterion in criteria(record.plan, "## Attractive quality"):
        if criterion not in headed:
            problems.append(
                stop(
                    DESIGN_STEP,
                    where,
                    f"has no scene for {criterion}",
                    f"add `### {criterion}:` under `## Scenes` with what is put in and what must"
                    " happen",
                    "each attractive criterion is checked by the scenes the user approved",
                )
            )
    checked = scenes + "\n" + section(text, "## Machine checks")
    for criterion in criteria(record.plan, "## Must-be quality"):
        if not re.search(rf"{criterion}\b", checked):
            problems.append(
                stop(
                    DESIGN_STEP,
                    where,
                    f"names {criterion} in no scene's pass and no machine check's criteria",
                    f"name {criterion} in the machine check that judges it, or in the pass of a"
                    " scene where no machine can",
                    "a must-be criterion no check covers breaks unseen",
                )
            )
    return problems


def check(record: Record) -> list[str]:
    ids = set(criteria(record.plan))
    problems = tasks(record, ids) + questions(record, ids)
    where = field(record.plan, "verification")
    if where is not None and record.verification is not None:
        problems += verification(record, where, record.verification)
    return problems
