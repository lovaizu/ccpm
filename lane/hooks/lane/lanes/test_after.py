"""test_after: the subagent, once it has changed an output its step names, passes a test before it
ends, such as the unit tests after changing the code they test. It is held as the subagent is about
to end: its last change to the output with no passing run of a test taken after it is a drift. A
run passes where its Bash call gave back no error, as a command that exits other than 0 does, and
the call's exit is the test's: each command after the test is joined to it by `&&`, so a failing
test ends the call, where `; echo exit=$?` or a pipe to `tail` would end it with 0 whatever the
test gave. A call that changes the output and runs the test passes it, as the AI writes a change
and its test in one call in that order."""

from __future__ import annotations

import os

import shell
from call import Call, End, changed, starts

ACTION = "test"
WORDING = "After changing `<output>`, pass `<test>`."
EVENTS = ("SubagentStop",)


def drifts(end: End, takes: list[str], root: str) -> bool:
    """Whether the subagent changed the output taken first, named from the folder it ends in, where
    the guard stands, and ran none of the tests taken after it with no error since its last change;
    a test is run by a command that `starts` holds to run it."""
    output = shell.path(os.getcwd(), takes[0])
    made = end.made or []
    changes = [at for at, c in enumerate(made) if output and changed(c, output)]
    return bool(changes) and not any(passes(c, takes[1:]) for c in made[changes[-1] :])


def passes(made: Call, tests: list[str]) -> bool:
    """Whether the call ran one of the tests, each command after it joined by `&&`, and gave
    back no error."""
    return not made.failed and any(
        starts(words, t) and all(e == "&&" for e in made.ends[at:-1])
        for at, words in enumerate(made.what)
        for t in tests
    )
