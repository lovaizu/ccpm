"""The Lane that lets a role run only the commands it names, word for word, with the run values
filled in."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from form import Lane, Route
from place import Call, EndAsked, StartCall
from runs import Due

from lanes.kind import Held, Kept, Marking, TypeInfo, Verdict

# Each value that a Lane of this type takes, by the name it lies under in the Lane's `args`, with
# what it is, as lay.py types shows it.
ARGS: dict[str, str] = {
    "commands": ("Each command the role may run, word for word, with `{<name>}` for a run value."),
}


class RunOnly:
    """The lane type, as lanes/ finds it by `TYPE`."""

    def info(self) -> TypeInfo:
        """What lay.py types shows of the type: its name, `run_only`, its sentence, the steps it
        suits, what it allows, and `ARGS`.

        Carries: S1 `L->>T: each type`.
        """
        return TypeInfo(
            name="run_only",
            sentence="Run only `<command>`, with each of `commands` joined by `or`.",
            suits="a Step that runs commands",
            allows="a Bash command that is one of `commands`, word for word",
            args=ARGS,
        )

    def faults(self, lane: Lane, last_step: int, routes: Sequence[Route]) -> tuple[str, ...]:
        """Each fault of a Lane of this type, such as `commands` missing, empty, or not a list of
        strings.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`.
        """
        given = lane.args.get("commands")
        if not isinstance(given, list) or not given or not all(isinstance(x, str) for x in given):
            return ("run_only takes `commands`, a list of one string or more",)
        return ()

    def sentence(self, lane: Lane, routes: Sequence[Route]) -> str:
        """The sentence that the Lane lays on its Step: `Run only` each of `commands`, joined by
        `or`.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`, and the sentence of each
        Broken.
        """
        named = " or ".join(f"`{command}`" for command in lane.args["commands"])
        return f"Run only {named}."

    def allows(self, lane: Lane, call: Call, held: Held) -> bool | None:
        """True for a Bash command that is one of `commands`, its run values filled in from the
        Start, a name that the values don't give standing for any word; False for any other Bash
        command; None for a Call of another tool.

        Carries: the Call checks of S2, S5, and S6.
        """
        if call.tool != "Bash":
            return None
        values = held.start.values if held.start else {}
        command = str(call.input.get("command"))
        return any(re.fullmatch(_pattern(each, values), command) for each in lane.args["commands"])

    def check_start(self, lane: Lane, asked: StartCall, held: Held, due: Sequence[Due]) -> Verdict:
        """Kept: the Lane checks no start.

        Carries: S5 `G->>T: checks the start by the Lane of the skill's Routes, with the moves due`.
        """
        return Kept()

    def check_mark(self, lane: Lane, marking: Marking, held: Held) -> Verdict:
        """Kept: the Lane checks no Mark.

        Carries: S6 `G->>T: checks the Mark by each Lane on Step n`.
        """
        return Kept()

    def check_end(self, lane: Lane, end: EndAsked, held: Held) -> Verdict:
        """Kept: the Lane checks no end.

        Carries: S2 `G->>T: checks the end by each Lane of up`, S5 `G->>T: checks the end by each
        Lane of each Run's skill`, S6 `G->>T: checks the end by each Lane of the role`.
        """
        return Kept()


TYPE = RunOnly()


def _pattern(command: str, values: Mapping[str, str]) -> str:
    """The command as a pattern: each `{<name>}` its run value, or any word where the values give
    none, and every other character as it stands."""
    parts = re.split(r"\{(\w+)\}", command)
    return "".join(
        re.escape(part) if i % 2 == 0 else re.escape(values[part]) if part in values else r"\S+"
        for i, part in enumerate(parts)
    )
