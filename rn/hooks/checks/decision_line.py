"""Check 4: every conductor commit ends with a decision line `● … ── … → …`, followed by nothing but
trailers such as Co-Authored-By."""
import re

from record import last_line

DECISION = re.compile(r"^● .+ ── .+ → .+$")


def check(msg):
    if not DECISION.match(last_line(msg)):
        return ["commit message: the last line is not a decision line `● … ── … → …`"]
    return []
