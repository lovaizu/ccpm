"""The Lane that holds a Step's Mark until the role has read each line of each path it names by Read
since the Step began, each path read from the top of its worktree with the run values filled in."""

from __future__ import annotations

from collections.abc import Sequence

from form import Lane, Route
from place import Call, EndAsked, StartCall
from runs import Due

from lanes.kind import Held, Marking, TypeInfo, Verdict

# Each value that a Lane of this type takes, by the name it lies under in the Lane's `args`, with
# what it is, as lay.py types shows it.
ARGS: dict[str, str] = {
    "paths": (
        "Each path the Step reads whole, from the top of its worktree, with `{<name>}` for a run"
        " value."
    ),
}


class ReadsWhole:
    """The lane type, as lanes/ finds it by `TYPE`."""

    def info(self) -> TypeInfo:
        """What lay.py types shows of the type: its name, `reads_whole`, its sentence, the steps it
        suits, what it allows, and `ARGS`.

        Carries: S1 `L->>T: each type`.
        """
        return TypeInfo(
            name="reads_whole",
            sentence="Read `<path>` whole, with each of `paths` joined by `and`.",
            suits="a Step that reads files whole",
            allows="nothing: it holds the Step's Mark until each line of each of `paths` is read by"
            " Read since the Step began",
            args=ARGS,
        )

    def faults(self, lane: Lane, last_step: int, routes: Sequence[Route]) -> tuple[str, ...]:
        """Each fault of a Lane of this type, such as `paths` missing, empty, or not a list of
        strings.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`.
        """
        raise NotImplementedError("reads_whole.faults")

    def sentence(self, lane: Lane, routes: Sequence[Route]) -> str:
        """The sentence that the Lane lays on its Step, naming each of `paths` to read whole by
        Read.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`, and the sentence of each
        Broken.
        """
        raise NotImplementedError("reads_whole.sentence")

    def allows(self, lane: Lane, call: Call, held: Held) -> bool | None:
        """None: the Lane judges no Call, and holds the Step's Mark.

        Carries: the Call checks of S2, S5, and S6.
        """
        raise NotImplementedError("reads_whole.allows")

    def check_start(self, lane: Lane, asked: StartCall, held: Held, due: Sequence[Due]) -> Verdict:
        """Kept: the Lane checks no start.

        Carries: S5 `G->>T: checks the start by the Lane of the skill's Routes, with the moves due`.
        """
        raise NotImplementedError("reads_whole.check_start")

    def check_mark(self, lane: Lane, marking: Marking, held: Held) -> Verdict:
        """Kept where, for each of `paths` with the Start's run values filled in, the Reads since
        the Step began cover each line that the file holds now; Broken, with the Lane's sentence
        and each path with the lines not read, where they don't; CantCheck, with why and the
        plugin's developer to fix it, where a path can't be read.

        Carries: S6 `G->>T: checks the Mark by each Lane on Step n, with the Reads and Marks since
        the Step began`, and `else a path a Lane of reads_whole names wasn't read whole`.
        """
        raise NotImplementedError("reads_whole.check_mark")

    def check_end(self, lane: Lane, end: EndAsked, held: Held) -> Verdict:
        """Kept: the Lane checks no end, as keeps_steps holds the end until the Step is marked.

        Carries: S6 `G->>T: checks the end by each Lane of the role`.
        """
        raise NotImplementedError("reads_whole.check_end")


TYPE = ReadsWhole()


def named(lane: Lane, call: Call, held: Held) -> str | None:
    """The path, as the Lane names it, that a Read reads.

    Takes: a Lane of this type, the Call, and what it's held to, the Start's run values among it.
    Gives: the one of `paths`, with the run values filled in, that the Read's `file_path` names
    from `call.top`; None for a Call of another tool, or a Read of another path.
    Changes: nothing.
    Refuses: nothing.
    Carries: S6 `opt a Read of a path that a Lane of reads_whole names`, through
    `lanes.read_kept`.
    """
    raise NotImplementedError("reads_whole.named")
