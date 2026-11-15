"""The Lane that lets a role run only the commands it names, word for word, with the run values
filled in."""

from __future__ import annotations

from collections.abc import Sequence

from form import Lane, Route
from place import Call, EndAsked, StartCall
from runs import Due

from lanes.kind import Held, TypeInfo, Verdict

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
        raise NotImplementedError("run_only.RunOnly.info")

    def faults(self, lane: Lane, last_step: int, routes: Sequence[Route]) -> tuple[str, ...]:
        """Each fault of a Lane of this type, such as `commands` missing, empty, or not a list of
        strings.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`.
        """
        raise NotImplementedError("run_only.RunOnly.faults")

    def sentence(self, lane: Lane, routes: Sequence[Route]) -> str:
        """The sentence that the Lane lays on its Step: `Run only` each of `commands`, joined by
        `or`.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`, and the sentence of each
        Broken.
        """
        raise NotImplementedError("run_only.RunOnly.sentence")

    def allows(self, lane: Lane, call: Call, held: Held) -> bool | None:
        """True for a Bash command that is one of `commands`, its run values filled in from the
        Start, a name that the values don't give standing for any word; False for any other Bash
        command; None for a Call of another tool.

        Carries: the Call checks of S2, S5, and S6.
        """
        raise NotImplementedError("run_only.RunOnly.allows")

    def check_start(self, lane: Lane, asked: StartCall, held: Held, due: Sequence[Due]) -> Verdict:
        """Kept: the Lane checks no start.

        Carries: S5 `G->>T: checks the start by the Lane of the skill's Routes, with the moves due`.
        """
        raise NotImplementedError("run_only.RunOnly.check_start")

    def check_end(self, lane: Lane, end: EndAsked, held: Held) -> Verdict:
        """Kept: the Lane checks no end.

        Carries: S2 `G->>T: checks the end by each Lane of up`, S5 `G->>T: checks the end by each
        Lane of each Run's skill`, S6 `G->>T: checks the end by each Lane of the role`.
        """
        raise NotImplementedError("run_only.RunOnly.check_end")


TYPE = RunOnly()
