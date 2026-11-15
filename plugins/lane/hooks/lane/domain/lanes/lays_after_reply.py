"""up's Lane that holds lay.py write to the caller's own act: the sentence, and the check that a
call of lay.py write comes after a person's reply to the Run that showed its ID, or in a Run that an
AI called."""

from __future__ import annotations

from collections.abc import Sequence

from form import Lane, Route
from place import Call, EndAsked, StartCall
from runs import Due

from lanes.kind import Held, Kept, TypeInfo, Verdict

# Each value that a Lane of this type takes, by the name it lies under in the Lane's `args`, with
# what it is, as lay.py types shows it. It takes none.
ARGS: dict[str, str] = {}


class LaysAfterReply:
    """The lane type, as lanes/ finds it by `TYPE`."""

    def info(self) -> TypeInfo:
        """What lay.py types shows of the type: its name, `lays_after_reply`, its sentence, the
        steps it suits, what it allows, and `ARGS`.

        Carries: S1 `L->>T: each type`.
        """
        return TypeInfo(
            name="lays_after_reply",
            sentence="Run lay.py write only once the caller approved by their own act.",
            suits="up's Step that lays the Proposal",
            allows="lay.py write once a person replied to the Proposal it shows, or in an AI's run",
            args=ARGS,
        )

    def faults(self, lane: Lane, last_step: int, routes: Sequence[Route]) -> tuple[str, ...]:
        """Each fault of a Lane of this type, such as a Step of a role other than up.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`.
        """
        if lane.role != "up":
            return (f"{lane.type} holds only up's Step, not {lane.role}'s",)
        return ()

    def sentence(self, lane: Lane, routes: Sequence[Route]) -> str:
        """The sentence that the Lane lays on up's Step, which names no value.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`, and the sentence of each
        Broken.
        """
        raise NotImplementedError("lays_after_reply.LaysAfterReply.sentence")

    def allows(self, lane: Lane, call: Call, held: Held) -> bool | None:
        """False for a call of lay.py write in a person's Run with no Approval of its ID since the
        Run showed it; True for one with it, or in an AI's Run; None for any other Call.

        Carries: the Call checks of S2, S5, and S6.
        """
        raise NotImplementedError("lays_after_reply.LaysAfterReply.allows")

    def check_start(self, lane: Lane, asked: StartCall, held: Held, due: Sequence[Due]) -> Verdict:
        """Kept: the Lane checks no start.

        Carries: S5 `G->>T: checks the start by the Lane of the skill's Routes, with the moves due`.
        """
        return Kept()

    def check_end(self, lane: Lane, end: EndAsked, held: Held) -> Verdict:
        """Kept: the Lane checks no end.

        Carries: S2 `G->>T: checks the end by each Lane of up`, S5 `G->>T: checks the end by each
        Lane of each Run's skill`, S6 `G->>T: checks the end by each Lane of the role`.
        """
        return Kept()


TYPE = LaysAfterReply()
