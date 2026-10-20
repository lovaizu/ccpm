"""What each entry of a plugin's hooks runs: every check of its event on the event Claude Code hands
it, a use stopped or an agent kept going with what they say."""

import json
import os
from collections.abc import Sequence
from typing import IO, Any

# Claude Code stops the tool's use, or keeps the agent going, on this exit, showing the AI what was
# written to stderr.
STOPPED = 2


def run(plugin: str, checks: Sequence[Any], stream: IO[str], err: IO[str]) -> int:
    """Runs each check on the event in the stream, from the folder the event comes from; gives
    STOPPED with what they say on err, headed by the plugin's name, where any says something, and 0
    where none does."""
    event = json.load(stream)
    os.chdir(event["cwd"])
    said = [s for c in checks for s in c.check(event)]
    if said:
        err.write(f"{plugin}: " + "\n".join(said) + "\n")
        return STOPPED
    return 0
