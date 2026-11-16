"""The Lane of a skill's Routes: the sentence that tells the main conversation to start each
subagent it's told to start until it's told to start no more, and the check of the main
conversation's start against the moves due."""

from __future__ import annotations

from collections.abc import Sequence

import answers
from form import Lane, Route
from manifest import plugin_name
from place import Call, EndAsked, StartCall
from runs import Due

from lanes.kind import Broken, Held, Kept, Marking, TypeInfo, Verdict

# Each value that a Lane of this type takes, by the name it lies under in the Lane's `args`, with
# what it is, as lay.py types shows it. A Lane of Routes takes none, as the Proposal's Routes hold
# its moves.
ARGS: dict[str, str] = {}


class Routes:
    """The lane type, as lanes/ finds it by `TYPE`."""

    def info(self) -> TypeInfo:
        """What lay.py types shows of the type: its name, `routes`, its sentence, the steps it
        suits, what it allows, and `ARGS`.

        Carries: S1 `L->>T: each type`.
        """
        return TypeInfo(
            name="routes",
            sentence="Start each subagent you are told to start, until you are told to start no"
            " more.",
            suits="the skill's Step that starts its subagents",
            allows="the main conversation's start of each subagent that a Route makes due, with"
            " its text",
            args=ARGS,
        )

    def faults(self, lane: Lane, last_step: int, routes: Sequence[Route]) -> tuple[str, ...]:
        """Each fault of a Lane of this type, such as a Step of a subagent, as the Lane holds only a
        skill's Step.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`.
        """
        return ()

    def sentence(self, lane: Lane, routes: Sequence[Route]) -> str:
        """The sentence that the Lane lays on the skill's Step: `Start each subagent you are told to
        start, until you are told to start no more.`

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`, and the sentence of each
        Broken.
        """
        return "Start each subagent you are told to start, until you are told to start no more."

    def allows(self, lane: Lane, call: Call, held: Held) -> bool | None:
        """None: the Lane judges no Call, as the skill's result script is the Lane on its last
        Step's.

        Carries: the Call checks of S2, S5, and S6.
        """
        return None

    def check_start(self, lane: Lane, asked: StartCall, held: Held, due: Sequence[Due]) -> Verdict:
        """The check of the main conversation's start or resume against the moves due.

        Takes: the Lane of the skill's Routes, the start, the Run, and the moves due with their
        texts.
        Gives: Kept for a start due with its text, or a resume where the Routes open none; Broken,
        with the starts due as `answers.due` says them, as what the main conversation may do, for
        any other start; Kept for a
        subagent's start, which the Lane on the role's last Step checks.
        Changes: nothing.
        Refuses: nothing.
        Carries: S5 `G->>T: checks the start by the Lane of the skill's Routes, with the moves due`,
        and its `alt a start due`, `else a resume`, and `else any other start`.
        """
        starts = [d for d in due if d.move.kind == "start"]
        if held.start is not None or asked.resume:
            return Kept()
        if any(d.move.role == asked.role and d.text == asked.text for d in starts):
            return Kept()
        moves_due = answers.due(plugin_name(held.root), starts)
        return Broken(lane, self.sentence(lane, held.routes), moves_due)

    def check_mark(self, lane: Lane, marking: Marking, held: Held) -> Verdict:
        """Kept: the Lane checks no Mark.

        Carries: S6 `G->>T: checks the Mark by each Lane on Step n`.
        """
        raise NotImplementedError("routes.check_mark")

    def check_end(self, lane: Lane, end: EndAsked, held: Held) -> Verdict:
        """Kept: the main conversation's end is held by the moves due, which the guard checks.

        Carries: S5 `G->>T: checks the end by each Lane of each Run's skill`.
        """
        return Kept()


TYPE = Routes()
