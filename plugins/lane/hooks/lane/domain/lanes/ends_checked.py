"""The Lane that holds an end to a command of the plugin's: the sentence, and the check that the
command, run in the hook event's cwd with the run values and the Result filled in, gives 0."""

from __future__ import annotations

from collections.abc import Sequence

from form import Lane, Route
from place import Call, EndAsked, StartCall
from runs import Due

from lanes.kind import Held, TypeInfo, Verdict

# Each value that a Lane of this type takes, by the name it lies under in the Lane's `args`, with
# what it is, as lay.py types shows it.
ARGS: dict[str, str] = {
    "command": (
        "The command of the plugin's that the end must pass, word for word, with `{result}` for"
        " the Result given and `{<name>}` for a run value."
    ),
}


class EndsChecked:
    """The lane type, as lanes/ finds it by `TYPE`."""

    def info(self) -> TypeInfo:
        """What lay.py types shows of the type: its name, `ends_checked`, its sentence, the steps it
        suits, what it allows, and `ARGS`.

        Carries: S1 `L->>T: each type`.
        """
        raise NotImplementedError

    def faults(self, lane: Lane) -> tuple[str, ...]:
        """Each fault of a Lane of this type, such as `command` missing or not a string.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`.
        """
        raise NotImplementedError

    def sentence(self, lane: Lane, routes: Sequence[Route]) -> str:
        """The sentence that the Lane lays on its Step, with `command` in it.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`, and the sentence of each
        Broken.
        """
        raise NotImplementedError

    def allows(self, lane: Lane, call: Call, held: Held) -> bool | None:
        """None: Lane runs the command at the end, and the Lane judges no Call.

        Carries: the Call checks of S2, S5, and S6.
        """
        raise NotImplementedError

    def check_start(self, lane: Lane, asked: StartCall, held: Held, due: Sequence[Due]) -> Verdict:
        """Kept: the Lane checks no start.

        Carries: S5 `G->>T: checks the start by the Lane of the skill's Routes, with the moves due`.
        """
        raise NotImplementedError

    def check_end(self, lane: Lane, end: EndAsked, held: Held) -> Verdict:
        """Kept where `command`, its values filled in, gives 0; Broken, with the Lane's sentence,
        where it gives another code; CantCheck, with why and the plugin's developer to fix it,
        where it can't run.

        Carries: S5 and S6 `opt a Lane holds the end to a command of the plugin's`, and `alt a Lane
        is broken`.
        """
        raise NotImplementedError


TYPE = EndsChecked()


def run(command: Sequence[str], cwd: str) -> int:
    """Runs a command of the plugin's, as an ends_checked Lane names it with its values filled in.

    Takes: the command's words, and the hook event's cwd.
    Gives: its exit code.
    Changes: whatever the command changes.
    Refuses: OSError, where the command can't start, which the Lane gives as CantCheck.
    Carries: S5 and S6 `T->>PC: runs it` and `PC-->>T: its exit code`.
    """
    raise NotImplementedError
