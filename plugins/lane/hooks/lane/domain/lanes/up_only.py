"""What the lane types that hold only up share: their Lane lies only on up's Steps, takes no value,
lays the sentence that lay.py types shows of its type as it stands, and checks no start."""

from __future__ import annotations

from collections.abc import Sequence

from form import Lane, Route
from place import StartCall
from runs import Due

from lanes.kind import Held, Kept, Verdict

# Each value that a Lane of these types takes, by the name it lies under in the Lane's `args`, with
# what it is, as lay.py types shows it. They take none.
ARGS: dict[str, str] = {}


class UpOnly:
    """The part of a lane type that holds only up; the type gives `SENTENCE`, `info`, `allows`,
    and `check_end`."""

    # The sentence that a Lane of the type lays, which names no value, and which its `info` shows.
    SENTENCE: str

    def faults(self, lane: Lane, last_step: int, routes: Sequence[Route]) -> tuple[str, ...]:
        """One fault where the Lane lies on a Step of a role other than up; else none.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`.
        """
        if lane.role != "up":
            return (f"{lane.type} holds only up's Step, not {lane.role}'s",)
        return ()

    def sentence(self, lane: Lane, routes: Sequence[Route]) -> str:
        """The sentence that the Lane lays on up's Step: the type's `SENTENCE`, as it names no
        value.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`, and the sentence of each
        Broken.
        """
        return self.SENTENCE

    def check_start(self, lane: Lane, asked: StartCall, held: Held, due: Sequence[Due]) -> Verdict:
        """Kept: the Lane checks no start.

        Carries: S5 `G->>T: checks the start by the Lane of the skill's Routes, with the moves due`.
        """
        return Kept()
