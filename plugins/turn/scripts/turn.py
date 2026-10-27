"""What turn:up and each role run for what must come out the same on every run: the call started or
gone on with, what each role is given, each role's reply checked, and the result written. Python
looks first in this file's folder, so turn's own modules are found before any of the same name."""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Callable

import call
import folder
import prompts
import result
from prompts import FIRST_USER, GENERATOR

USAGE = (
    "usage: turn.py start '<call JSON>'\n"
    "       turn.py generator <result>\n"
    "       turn.py first-user <result>\n"
    "       turn.py parts <result>\n"
    "       turn.py claim <result>\n"
    "       turn.py reading <result>\n"
    "       turn.py end <result>"
)


def start(text: str) -> dict[str, str]:
    """Starts the run the call asks for, keeping the call and the folder it is made from in the
    run's folder; or, called again with the same call, goes on with the run its result names,
    keeping what its folder holds. Gives where the result goes, as a whole path, which each later
    command names. Stops where the call or its CCS is not one turn can take, or another call's run
    is kept for the same result."""
    asked = call.checked(call.parse(text))
    kept = folder.kept(asked["result"])
    if kept is None:
        call.laid_out(asked)
        folder.keep(asked, os.getcwd())
    elif kept["call"] != asked:
        raise call.Stop(
            f"turn: a run of another call is kept for the result {asked['result']}, in"
            f" {folder.folder(asked['result'])}; call turn with that call to go on with it, or with"
            " another result"
        )
    else:
        # The call's paths mean the folder the first call was made from.
        os.chdir(kept["root"])
        call.laid_out(asked)
    return {"result": os.path.abspath(asked["result"])}


def checked(role: str) -> Callable[[dict[str, Any]], dict[str, str]]:
    """The check of the role's last reply: gives where it is, once it is filled; stops, saying where
    to write it or each thing to fix, where it is not."""

    def check(run: dict[str, Any]) -> dict[str, str]:
        path = folder.reply(run["result"], role)
        text = prompts.last(run, role)
        if text is None:
            raise call.Stop(
                f"turn: {path} is not there; write your reply there with the Write tool, in the"
                f" form of {prompts.CHECKS[role]}.json"
            )
        said = prompts.problems(run, role, text)
        if said:
            raise call.Stop("\n".join([f"turn: {path} is not filled; fix each of these:", *said]))
        return {"filled": path}

    return check


# What each command but start gives, from the run of the result it names, laid out from its CCS as
# it is now.
COMMANDS: dict[str, Callable[[dict[str, Any]], Any]] = {
    "generator": prompts.generator,
    "first-user": prompts.first_user,
    "parts": lambda run: {"parts": prompts.parts(run)},
    "claim": checked(GENERATOR),
    "reading": checked(FIRST_USER),
    "end": result.ended,
}


def main(argv: list[str]) -> int:
    """What turn.py runs: the command given on its argument. Prints what it gives as JSON and gives
    0, or prints what was wrong and gives 1."""
    try:
        if argv[:1] == ["start"] and len(argv) == 2:
            out = start(argv[1])
        elif len(argv) == 2 and argv[0] in COMMANDS:
            out = COMMANDS[argv[0]](prompts.laid_out(argv[1]))
        else:
            print(USAGE)
            return 1
    except call.Stop as stop:
        print(stop)
        return 1
    print(json.dumps(out, ensure_ascii=False))
    return 0


if (
    __name__ == "__main__"  # pragma: no mutate
):
    sys.exit(main(sys.argv[1:]))
