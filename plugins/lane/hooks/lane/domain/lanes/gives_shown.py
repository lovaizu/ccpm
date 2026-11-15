"""up's Lane that holds up's end to what lay.py print showed: the sentence, and the check that up's
last message gives the words of the Run's latest Shown, word for word."""

from __future__ import annotations

from collections.abc import Sequence

from form import Lane, Route
from place import Call, EndAsked, StartCall
from runs import Due

from lanes.kind import Held, TypeInfo, Verdict

# Each value that a Lane of this type takes, by the name it lies under in the Lane's `args`, with
# what it is, as lay.py types shows it. It takes none.
ARGS: dict[str, str] = {}


class GivesShown:
    """The lane type, as lanes/ finds it by `TYPE`."""

    def info(self) -> TypeInfo:
        """What lay.py types shows of the type: its name, `gives_shown`, its sentence, the steps it
        suits, what it allows, and `ARGS`.

        Carries: S1 `L->>T: each type`.
        """
        raise NotImplementedError

    def faults(self, lane: Lane) -> tuple[str, ...]:
        """Each fault of a Lane of this type, such as a Step of a role other than up.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`.
        """
        raise NotImplementedError

    def sentence(self, lane: Lane, routes: Sequence[Route]) -> str:
        """The sentence that the Lane lays on up's Step, which names no value.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`, and the sentence of each
        Broken.
        """
        raise NotImplementedError

    def allows(self, lane: Lane, call: Call, held: Held) -> bool | None:
        """None: the Lane judges no Call.

        Carries: the Call checks of S2, S5, and S6.
        """
        raise NotImplementedError

    def check_start(self, lane: Lane, asked: StartCall, held: Held, due: Sequence[Due]) -> Verdict:
        """Kept: the Lane checks no start.

        Carries: S5 `G->>T: checks the start by the Lane of the skill's Routes, with the moves due`.
        """
        raise NotImplementedError

    def check_end(self, lane: Lane, end: EndAsked, held: Held) -> Verdict:
        """Broken, with the words that lay.py print showed, where the last message doesn't hold them
        word for word after the Run's latest Shown; else Kept.

        Carries: S2 `G->>T: checks the end by each Lane of up` and `alt up didn't give what lay.py
        print showed, word for word`.
        """
        raise NotImplementedError


TYPE = GivesShown()
