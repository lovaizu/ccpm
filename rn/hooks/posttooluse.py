"""PostToolUse on Write and Edit: a write to a session's plan, an item of its open/ or the
verification document its plan names is checked against the record's form where it happens, so the
conductor mends the record before building on it; those three are all the record holds, so a write
elsewhere is not the record's and goes through unread."""

import os
import sys
from typing import IO

from checks import FORM, older, run
from record import open_sessions, read_event, report, verification_file

CHECKS = FORM


def main(stream: IO[str]) -> None:
    event = read_event(stream)
    if event is None:
        return
    written = os.path.realpath(event["tool_input"]["file_path"])
    for top, folder, record in open_sessions(event):
        record_file = os.path.dirname(written) == os.path.join(top, folder, "open") or (
            written == verification_file(top, record.plan)
        )
        # An older session's plan written without its front matter or its rn key looks the same
        # as the older session itself, so a write to a plan is checked whichever rn started it.
        if written == os.path.join(top, folder, "steering.md") or (
            record_file and not older(record)
        ):
            report(run(CHECKS, record))


if __name__ == "__main__":
    main(sys.stdin)
