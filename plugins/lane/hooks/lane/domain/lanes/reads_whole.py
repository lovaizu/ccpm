"""The Lane that holds a Step's Mark until the role has read each line of each path it names by Read
since the Step began, each path read from the top of its worktree with the run values filled in."""

from __future__ import annotations

import os
from collections.abc import Sequence

from form import Lane, Route
from place import Call, EndAsked, StartCall, top
from run_record import Read, Report
from runs import Due

from lanes import paths
from lanes.kind import Broken, CantCheck, Held, Kept, Marking, TypeInfo, Verdict

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
        return paths.fault(lane)

    def sentence(self, lane: Lane, routes: Sequence[Route]) -> str:
        """The sentence that the Lane lays on its Step, naming each of `paths` to read whole by
        Read.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`, and the sentence of each
        Broken.
        """
        named = " and ".join(f"`{path}`" for path in lane.args["paths"])
        return f"Read {named} whole."

    def allows(self, lane: Lane, call: Call, held: Held) -> bool | None:
        """None: the Lane judges no Call, and holds the Step's Mark.

        Carries: the Call checks of S2, S5, and S6.
        """
        return None

    def check_start(self, lane: Lane, asked: StartCall, held: Held, due: Sequence[Due]) -> Verdict:
        """Kept: the Lane checks no start.

        Carries: S5 `G->>T: checks the start by the Lane of the skill's Routes, with the moves due`.
        """
        return Kept()

    def check_mark(self, lane: Lane, marking: Marking, held: Held) -> Verdict:
        """Kept where, for each of `paths` with the Start's run values filled in, the Reads since
        the Step began cover each line that the file holds now, counted as Read counts them, the
        empty line after a last newline among them; Broken, with the Lane's sentence and each path
        with the lines not read, where they don't; CantCheck, with why and the plugin's developer
        to fix it, where a path can't be read.

        Carries: S6 `G->>T: checks the Mark by each Lane on Step n, with the Reads and Marks since
        the Step began`, and `else a path a Lane of reads_whole names wasn't read whole`.
        """
        values = held.start.values if held.start else {}
        unread = []
        for path in paths.filled(lane, values):
            try:
                with open(os.path.join(top(held.cwd), path), encoding="utf-8") as f:
                    count = len(f.read().split("\n"))
            except OSError as e:
                why = f"`{path}`, which a Lane of reads_whole names, can't be read: {e.strerror}"
                return CantCheck(why, f"The developer of the plugin must fix {lane.file}")
            unread += [f"`{path}`, {span}" for span in _unread(path, count, marking.since)]
        if unread:
            said, left = self.sentence(lane, held.routes), ", ".join(unread)
            return Broken(lane, said, f"Not read by Read since the step began: {left}.")
        return Kept()

    def check_end(self, lane: Lane, end: EndAsked, held: Held) -> Verdict:
        """Kept: the Lane checks no end, as keeps_steps holds the end until the Step is marked.

        Carries: S6 `G->>T: checks the end by each Lane of the role`.
        """
        return Kept()


TYPE = ReadsWhole()


def _unread(path: str, count: int, since: Sequence[Report]) -> list[str]:
    """Each run of the file's lines, of the count it holds, that no Read of the path since the
    Step began read, such as `lines 4 to 7` or `line 1`."""
    read = {
        n
        for r in since
        if isinstance(r, Read) and r.path == path
        for n in range(r.first, r.last + 1)
    }
    runs: list[list[int]] = []
    for n in (n for n in range(1, count + 1) if n not in read):
        if runs and runs[-1][-1] == n - 1:
            runs[-1].append(n)
        else:
            runs.append([n])
    return [f"line {r[0]}" if len(r) == 1 else f"lines {r[0]} to {r[-1]}" for r in runs]


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
    if call.tool != "Read":
        return None
    path = paths.named(call, str(call.input.get("file_path")))
    values = held.start.values if held.start else {}
    return path if path in paths.filled(lane, values) else None
