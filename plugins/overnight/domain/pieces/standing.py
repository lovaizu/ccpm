"""How each piece stands once its record is read against its runner's process, the count of the
pieces stopped included."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pieces.record import Record

# What stopped a piece that nothing carries any more: the usage limit where it was waiting, and the
# session closing where it was running.
Stop = Literal["usage limit", "session closing"]


@dataclass(frozen=True)
class Standing:
    """A piece's record, and what stopped it where its runner ended before its conversation did."""

    record: Record
    stopped: Stop | None


@dataclass(frozen=True)
class Night:
    """How each piece stands, by its number, and how many of them were stopped."""

    standings: tuple[Standing, ...]

    @property
    def stopped(self) -> int:
        """How many of the pieces were stopped.

        Takes: nothing.
        Gives: the count of the standings that name what stopped them.
        Changes: nothing.
        Refuses: nothing.
        """
        raise NotImplementedError("pieces.standing.Night.stopped")


def stand(records: list[Record]) -> Night:
    """How each piece stands.

    Takes: each piece's record, as `record.read` gives them.
    Gives: each record with what stopped it: the usage limit where it's recorded as waiting and
    its runner's process no longer runs, the session closing where it's recorded as running and
    its runner's process no longer runs, and nothing otherwise. A piece done or failed counts by
    how its conversation ended, never by a call refused on the way.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("pieces.standing.stand")
