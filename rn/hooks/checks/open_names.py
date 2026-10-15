"""Each item of open/ is named `{NN}-{kind}-{about}.md`, as references/record.md gives."""

from __future__ import annotations

import re

from checks import Record

NAME = re.compile(r"\d{2}-(report|feedback|notes)-.+\.md")


def check(record: Record) -> list[str]:
    return [
        f"rn: {record.session}/open/{name} is not named `{{NN}}-{{kind}}-{{about}}.md` with the kind "
        f"`report`, `feedback` or `notes`; rename it so, since rn's commands and checks find each "
        f"item of open/ by its number, kind and name, as references/record.md gives."
        for name in sorted(record.items)
        if not NAME.fullmatch(name)
    ]
