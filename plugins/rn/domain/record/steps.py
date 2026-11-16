"""Decides how rn's check reads the steps of a prompt: the numbered list under `## Steps` of a
role's part in `domain/`, or of a command's `skills/<command>/SKILL.md`."""

from __future__ import annotations

import os
import re

from fault import Wrong

# A step: a line that opens with its number, as a numbered list in Markdown.
_STEP = re.compile(r"^(\d+)\. ")


def numbers(plugin_root: str, of: str) -> tuple[int, ...]:
    """The number of each step of a prompt.

    Takes: rn's folder, and the prompt, by its role, such as generator, or by its command, such as
    up.
    Gives: each step's number, in order, from the numbered list under `## Steps` up to the next
    heading; none where the list is empty.
    Changes: nothing.
    Refuses: fault.Wrong, where no prompt of rn's has that name. A prompt rn ships is never the
    caller's to mend, so a fault in reading it stops with its trace.
    Carries: S1 `GD->>R: checks its record`, against the steps of the role's prompt.
    """
    files = (
        os.path.join(plugin_root, "skills", of, "SKILL.md"),
        os.path.join(plugin_root, "domain", f"{of}.md"),
    )
    found = [path for path in files if os.path.isfile(path) and "/" not in of]
    if not found:
        raise Wrong(f"rn has no prompt named {of!r}, a role's part or a command")
    with open(found[0], encoding="utf-8") as f:
        lines = f.read().split("\n")
    steps, within = [], False
    for line in lines:
        found = _STEP.match(line)
        if line.startswith("#"):
            within = line.strip() == "## Steps"
        elif within and found:
            steps.append(int(found[1]))
    return tuple(steps)
