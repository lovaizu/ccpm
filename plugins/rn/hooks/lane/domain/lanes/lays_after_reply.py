"""up's Lane that holds lay.py write to the caller's own act: the sentence, and the check that a
call of lay.py write comes after a person's reply to the Run that showed its ID, or in a Run that an
AI called."""

from __future__ import annotations

from form import Lane
from place import Call, EndAsked
from runs import Approval
from script_calls import write_call

from lanes.kind import Held, Kept, TypeInfo, Verdict
from lanes.up_only import ARGS, UpOnly


class LaysAfterReply(UpOnly):
    """The lane type, as lanes/ finds it by `TYPE`."""

    SENTENCE = (
        "Run lay.py write only after the person's reply to the Proposal it lays, or"
        " in a run an AI called."
    )

    def info(self) -> TypeInfo:
        """What lay.py types shows of the type: its name, `lays_after_reply`, its sentence, the
        steps it suits, what it allows, and `ARGS`.

        Carries: S1 `L->>T: each type`.
        """
        return TypeInfo(
            name="lays_after_reply",
            sentence=self.SENTENCE,
            suits="up's Step that lays the Proposal",
            allows="lay.py write once a person replied to the Proposal it shows, or in an AI's run",
            args=ARGS,
        )

    def allows(self, lane: Lane, call: Call, held: Held) -> bool | None:
        """False for a call of lay.py write, as `script_calls.write_call` reads it, in a person's
        Run with no Approval of its ID; True for one with it, or in an AI's Run; None for any other
        Call.

        Carries: the Call checks of S2, S5, and S6.
        """
        found = write_call(str(call.input.get("command", "")))
        if found is None:
            return None
        return held.run.by == "ai" or Approval(found[1], "person") in held.run.approvals

    def check_end(self, lane: Lane, end: EndAsked, held: Held) -> Verdict:
        """Kept: the Lane checks no end.

        Carries: S2 `G->>T: checks the end by each Lane of up`, S5 `G->>T: checks the end by each
        Lane of each Run's skill`, S6 `G->>T: checks the end by each Lane of the role`.
        """
        return Kept()


TYPE = LaysAfterReply()
