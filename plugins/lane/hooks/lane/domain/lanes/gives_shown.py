"""up's Lane that holds up's end to what lay.py print showed: the sentence, and the check that up's
last message gives the words of the Run's latest Shown, word for word."""

from __future__ import annotations

from form import Lane
from place import Call, EndAsked
from runs import Approval

from lanes.kind import Broken, Held, Kept, TypeInfo, Verdict
from lanes.up_only import ARGS, UpOnly


class GivesShown(UpOnly):
    """The lane type, as lanes/ finds it by `TYPE`."""

    SENTENCE = "Give the caller what lay.py print showed, word for word."

    def info(self) -> TypeInfo:
        """What lay.py types shows of the type: its name, `gives_shown`, its sentence, the steps it
        suits, what it allows, and `ARGS`.

        Carries: S1 `L->>T: each type`.
        """
        return TypeInfo(
            name="gives_shown",
            sentence=self.SENTENCE,
            suits="up's Step that shows the Proposal",
            allows="nothing: it holds up's end to the words lay.py print showed",
            args=ARGS,
        )

    def allows(self, lane: Lane, call: Call, held: Held) -> bool | None:
        """None: the Lane judges no Call.

        Carries: the Call checks of S2, S5, and S6.
        """
        return None

    def check_end(self, lane: Lane, end: EndAsked, held: Held) -> Verdict:
        """Broken, with the words of the Run's latest Shown as what up may do, where the person
        hasn't replied to it and the last message doesn't hold them word for word; else Kept, as
        for a Run that showed nothing.

        Carries: S2 `G->>T: checks the end by each Lane of up` and `alt up didn't give what lay.py
        print showed, word for word`.
        """
        for shown in held.run.shown[-1:]:
            words = shown.words.strip()
            replied = Approval(shown.proposal_id, "person") in held.run.approvals
            if not replied and words not in end.last_message:
                return Broken(lane, self.sentence(lane, held.routes), words)
        return Kept()


TYPE = GivesShown()
