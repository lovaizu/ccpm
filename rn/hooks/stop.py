"""Stop: at each end of the conductor's turn, every open session's record is checked against its
form, so a breach made by a shell command, which PostToolUse on Write and Edit does not see, is
still stopped within the turn it was made in."""

from __future__ import annotations

import sys
from typing import IO

from checks import FORM, Record, older, run
from record import open_sessions, read_event, report

CHECKS = FORM


def at_turn_end(record: Record) -> list[str]:
    """An older session waits for `/rn:up` to bring it to the current form, so it is passed by."""
    return [] if older(record) else run(CHECKS, record)


def main(stream: IO[str]) -> None:
    event = read_event(stream)
    if event is None:
        return
    report(
        [sentence for session in open_sessions(event) for sentence in at_turn_end(session.record)]
    )


if __name__ == "__main__":
    main(sys.stdin)
