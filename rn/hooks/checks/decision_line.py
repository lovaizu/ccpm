"""Check 4: every conductor commit ends with a decision line `● … ── … → …`, followed by nothing but
trailers such as Co-Authored-By."""

import re

from record import last_line

DECISION = re.compile(r"^● .+ ── .+ → .+$")


def check(msg):
    if not DECISION.match(last_line(msg)):
        return [
            (
                "on a commit: the message's last line is not a decision line `● … ── … → …`, "
                "so a later conversation cannot read what was decided and what comes next"
            )
        ]
    return []
