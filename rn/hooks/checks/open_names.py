"""Each item of open/ is named `{NN}-{kind}-{about}.md`, as step 3 of rn's references/record.md
says, with the kind `report`, `feedback` or `notes`."""

import re

from checks import Record, stop

NAME = re.compile(r"\d{2,}-(report|feedback|notes)-[^/]+\.md")
# A misnamed item may still tell what it holds, and so which step wrote it; one that tells
# nothing is met where the conductor takes the items of open/ up by their names.
STEPS = (
    ("question", "Asking the user"),
    ("proposal", "Stopping for the user"),
    ("report", "Making a work through turn"),
    ("feedback", "Feedback"),
)
TAKING_UP = "Taking up the session"


def check(record: Record) -> list[str]:
    problems = []
    for name in sorted(record.open):
        if not NAME.fullmatch(name):
            step = next((step for word, step in STEPS if word in name), TAKING_UP)
            problems.append(
                stop(
                    step,
                    f"{record.folder}/open/{name}",
                    "is not named `{NN}-{kind}-{about}.md` with the kind `report`, `feedback`"
                    " or `notes`",
                    "rename it as step 3 of rn's references/record.md says",
                    "rn's commands and checks find each item of open/ by its name",
                )
            )
    return problems
