"""What each entry of turn's hooks runs: every check of its event on the event Claude Code hands
it, a use stopped or an agent kept going with what they say."""

import json
import os
import sys
from typing import IO

from checks import (
    call_given,
    no_commit,
    read_in_given,
    read_whole,
    role_given,
    role_reply,
    run_returned,
    start_as_called,
    write_work_alone,
)

PRETOOLUSE = (
    call_given,
    start_as_called,
    role_given,
    write_work_alone,
    no_commit,
    read_in_given,
    read_whole,
    role_reply,
    run_returned,
)
SUBAGENTSTOP = (read_whole, role_reply, run_returned)


def main(checks: tuple, stream: IO[str]) -> int:
    event = json.load(stream)
    os.chdir(event["cwd"])
    said = [s for c in checks for s in c.check(event)]
    if said:
        sys.stderr.write("turn: " + "\n".join(said) + "\n")
        return 2
    return 0
