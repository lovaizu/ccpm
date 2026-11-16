"""The Lane that lets a role write only the paths it names, each read from the top of its worktree
with the run values filled in."""

from __future__ import annotations

import os
from collections.abc import Sequence

from form import Lane, Route
from place import Call, EndAsked, StartCall
from runs import Due

from lanes.kind import Held, Kept, Marking, TypeInfo, Verdict

# Each value that a Lane of this type takes, by the name it lies under in the Lane's `args`, with
# what it is, as lay.py types shows it.
ARGS: dict[str, str] = {
    "paths": (
        "Each path the role may write, from the top of its worktree, with `{<name>}` for a run"
        " value."
    ),
}


class WriteOnly:
    """The lane type, as lanes/ finds it by `TYPE`."""

    def info(self) -> TypeInfo:
        """What lay.py types shows of the type: its name, `write_only`, its sentence, the steps it
        suits, what it allows, and `ARGS`.

        Carries: S1 `L->>T: each type`.
        """
        return TypeInfo(
            name="write_only",
            sentence="Write only `<path>`, with each of `paths` joined by `or`.",
            suits="a Step that writes files",
            allows="a Write or Edit of a path that is one of `paths`, from the top of the worktree",
            args=ARGS,
        )

    def faults(self, lane: Lane, last_step: int, routes: Sequence[Route]) -> tuple[str, ...]:
        """Each fault of a Lane of this type, such as `paths` missing, empty, or not a list of
        strings.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`.
        """
        given = lane.args.get("paths")
        if not isinstance(given, list) or not given or not all(isinstance(x, str) for x in given):
            return ("write_only takes `paths`, a list of one string or more",)
        return ()

    def sentence(self, lane: Lane, routes: Sequence[Route]) -> str:
        """The sentence that the Lane lays on its Step: `Write only` each of `paths`, joined by
        `or`.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`, and the sentence of each
        Broken.
        """
        named = " or ".join(f"`{path}`" for path in lane.args["paths"])
        return f"Write only {named}."

    def allows(self, lane: Lane, call: Call, held: Held) -> bool | None:
        """True for a Write or Edit of a path that is one of `paths`, read from `call.top`, its run
        values filled in from the Start; False for one of any other path; None for a Call of
        another tool.

        Carries: the Call checks of S2, S5, and S6.
        """
        if call.tool not in ("Write", "Edit"):
            return None
        path = os.path.relpath(os.path.join(call.cwd, str(call.input.get("file_path"))), call.top)
        return path in lane.args["paths"]

    def check_start(self, lane: Lane, asked: StartCall, held: Held, due: Sequence[Due]) -> Verdict:
        """Kept: the Lane checks no start.

        Carries: S5 `G->>T: checks the start by the Lane of the skill's Routes, with the moves due`.
        """
        return Kept()

    def check_mark(self, lane: Lane, marking: Marking, held: Held) -> Verdict:
        """Kept: the Lane checks no Mark.

        Carries: S6 `G->>T: checks the Mark by each Lane on Step n`.
        """
        raise NotImplementedError("write_only.check_mark")

    def check_end(self, lane: Lane, end: EndAsked, held: Held) -> Verdict:
        """Kept: the Lane checks no end.

        Carries: S2 `G->>T: checks the end by each Lane of up`, S5 `G->>T: checks the end by each
        Lane of each Run's skill`, S6 `G->>T: checks the end by each Lane of the role`.
        """
        return Kept()


TYPE = WriteOnly()
