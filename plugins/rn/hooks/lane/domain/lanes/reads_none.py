"""The Lane that stops each call of a role that reaches a path it names, by Read, Grep, Glob, or a
Bash command, each path read from the top of its worktree with the run values filled in."""

from __future__ import annotations

import os
import re
from collections.abc import Sequence

from form import Lane, Route
from place import Call, EndAsked, StartCall
from runs import Due

from lanes import paths
from lanes.kind import Held, Kept, Marking, TypeInfo, Verdict

# Each value that a Lane of this type takes, by the name it lies under in the Lane's `args`, with
# what it is, as lay.py types shows it.
ARGS: dict[str, str] = {
    "paths": (
        "Each path the role never reads, from the top of its worktree, with `{<name>}` for a run"
        " value."
    ),
}


# What parts a Bash command into the words that may name a path: spaces, quotes, the shell's
# operators, and the `=` of an option, so that `cat 'tally.py'` and `--file=tally.py` name it.
WORDS = re.compile(r"[\s'\"=;|&<>()`]+")


class ReadsNone:
    """The lane type, as lanes/ finds it by `TYPE`."""

    def info(self) -> TypeInfo:
        """What lay.py types shows of the type: its name, `reads_none`, its sentence, the steps it
        suits, what it allows, and `ARGS`.

        Carries: S1 `L->>T: each type`.
        """
        return TypeInfo(
            name="reads_none",
            sentence="Never read `<path>`, with each of `paths` joined by `or`.",
            suits="a Step that says never to read a path",
            allows="any call but a Read, Grep, Glob, or Bash command that reaches one of `paths`,"
            " from the top of the worktree",
            args=ARGS,
        )

    def faults(self, lane: Lane, last_step: int, routes: Sequence[Route]) -> tuple[str, ...]:
        """Each fault of a Lane of this type, such as `paths` missing, empty, or not a list of
        strings.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`.
        """
        return paths.fault(lane)

    def sentence(self, lane: Lane, routes: Sequence[Route]) -> str:
        """The sentence that the Lane lays on its Step, naming each of `paths` never to read.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`, and the sentence of each
        Broken.
        """
        named = " or ".join(f"`{path}`" for path in lane.args["paths"])
        return f"Never read {named}."

    def allows(self, lane: Lane, call: Call, held: Held) -> bool | None:
        """False for a call that reaches one of `paths`, read from `call.top` with the Start's run
        values filled in: a Read of it, a Grep of it or of a folder that holds it, as a Grep reads
        each file's contents, a Glob whose pattern names it, and a Bash command that names it; None
        for any other Call, a Glob of its folder by another pattern among them, as a Glob reads no
        file, so that a Lane of this type that names another path never outweighs it.

        Carries: the Call checks of S4 and S5, as a Lane of reads_none stops the call at its
        PreToolUse.
        """
        never = paths.filled(lane, held.start.values if held.start else {})
        return False if any(path in never for path in _reached(call, never)) else None

    def check_start(self, lane: Lane, asked: StartCall, held: Held, due: Sequence[Due]) -> Verdict:
        """Kept: the Lane checks no start.

        Carries: S4 `G->>T: checks the start by the Lane of the skill's Routes, with the moves due`.
        """
        return Kept()

    def check_mark(self, lane: Lane, marking: Marking, held: Held) -> Verdict:
        """Kept: the Lane checks no Mark, as it stops the read itself.

        Carries: S5 `G->>T: checks the Mark by each Lane on Step n`.
        """
        return Kept()

    def check_end(self, lane: Lane, end: EndAsked, held: Held) -> Verdict:
        """Kept: the Lane checks no end.

        Carries: S5 `G->>T: checks the end by each Lane of the role`.
        """
        return Kept()


TYPE = ReadsNone()


def _reached(call: Call, never: Sequence[str]) -> tuple[str, ...]:
    """Each path, from the top of the worktree, that the Call reaches: a Read's file; for a Grep of
    a folder, each of `never` that the folder holds, as a Grep reads each file's contents; the
    path that a Glob's pattern names in its folder; and each word of a Bash command, read as a
    path, its words parted by `WORDS`; none for any other Call."""
    given = call.input
    if call.tool == "Read":
        return (paths.named(call, str(given.get("file_path"))),)
    if call.tool == "Grep":
        folder = paths.named(call, str(given.get("path") or os.curdir))
        inside = [p for p in never if folder == os.curdir or p.startswith(folder + os.sep)]
        return (folder, *inside)
    if call.tool == "Glob":
        pattern = os.path.join(str(given.get("path") or os.curdir), str(given.get("pattern")))
        return (paths.named(call, pattern),)
    if call.tool == "Bash":
        words = WORDS.split(str(given.get("command")))
        return tuple(paths.named(call, word) for word in words if word)
    return ()
