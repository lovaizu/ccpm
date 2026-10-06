"""The steering.md has its front matter and headings, and task and criterion IDs are unique."""
import re

from record import criteria, front_matter

FRONT_KEYS = ("rn", "pr", "status", "artifact-language", "conversation-language", "readme", "design",
              "verification")
HEADINGS = ("# Goal", "# Acceptance criteria", "## Attractive quality", "## Must-be quality",
            "# Assumptions", "# Rules", "# Tasks")
TASK = re.compile(r"^### \[( |x)\] #(\d+): \S")


def check(text):
    problems = []
    front = front_matter(text) or {}
    for k in FRONT_KEYS:
        if k not in front:
            problems.append(f"steering.md: front matter has no `{k}`")
    if front.get("status") not in ("running", "finished"):
        problems.append("steering.md: `status` is neither running nor finished")
    lines = text.splitlines()
    for h in HEADINGS:
        if h not in lines:
            problems.append(f"steering.md: heading `{h}` is missing")
    ids = []
    for line in lines:
        if line.startswith("### "):
            m = TASK.match(line)
            if not m:
                problems.append(f"steering.md: task heading `{line}` is not `### [ ] #N: name`")
            else:
                ids.append(m.group(2))
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        problems.append("steering.md: task ids repeat: " + ", ".join("#" + i for i in dup))
    crit = criteria(text)
    dupc = sorted({i for i in crit if crit.count(i) > 1})
    if dupc:
        problems.append("steering.md: criterion ids repeat: " + ", ".join(dupc))
    return problems
