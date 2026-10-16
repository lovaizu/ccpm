"""The plan keeps the front matter, headings and task headings of the template in rn's
checklists/session/plan.md, with each task and criterion ID given once."""

from checks import TASK, Record, criteria, front_matter, stop, task_blocks

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
STEP = "Working out the plan"
WHY = (
    "rn's commands and checks read the plan by that form, and a later conversation goes on from"
    " it only when the form holds"
)
TEMPLATE = "the template in rn's checklists/session/plan.md"


def twice(values: list[str]) -> list[str]:
    return sorted({value for value in values if values.count(value) > 1})


def check(record: Record) -> list[str]:
    where = f"{record.folder}/steering.md"
    fields = front_matter(record.plan)
    if fields is None:
        broken = "opens with no front matter between two `---` lines"
        return [stop(STEP, where, broken, f"put back the front matter of {TEMPLATE}", WHY)]
    problems = []
    for key in KEYS:
        if key not in fields:
            broken = f"has no `{key}` key in its front matter"
            problems.append(stop(STEP, where, broken, f"add `{key}` as {TEMPLATE} gives it", WHY))
    status = fields.get("status", "running")
    if status not in ("running", "finished"):
        fix = "set it to `running`, or to `finished` once the Deliverable sign-off is approved"
        problems.append(stop(STEP, where, f"has `status: {status}`", fix, WHY))
    lines = record.plan.splitlines()
    for heading in HEADINGS:
        if heading not in lines:
            fix = f"put it back where {TEMPLATE} has it"
            problems.append(stop(STEP, where, f"has no `{heading}` heading", fix, WHY))
    numbers = []
    for block in task_blocks(record.plan):
        heading = block.splitlines()[0]
        task = TASK.fullmatch(heading)
        if task is None:
            fix = "write it as `### [ ] #N: name`, or `### [x] #N: name` once the task is done"
            problems.append(stop(STEP, where, f"has the task heading `{heading}`", fix, WHY))
        else:
            numbers.append(task.group(1))
    for number in twice(numbers):
        broken = f"gives #{number} to more than one task"
        problems.append(stop(STEP, where, broken, "give the later task the next unused id", WHY))
    for criterion in twice(criteria(record.plan)):
        broken = f"gives {criterion} to more than one criterion"
        fix = "give the later criterion the next unused ID"
        problems.append(stop(STEP, where, broken, fix, WHY))
    return problems
