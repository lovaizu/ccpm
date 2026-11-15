"""The rule that a role ends by the result script, laid on its last Step: the sentence that names
the script with each Result the role may give, and the checks that hold the role to it, the
script's run let through, a subagent's start of a role stopped, and an end with no Result
stopped."""

from __future__ import annotations

from collections.abc import Sequence

from form import Lane, Route
from place import Call, EndAsked, StartCall
from runs import Due

from lanes.kind import Held, TypeInfo, Verdict

# Each value that a Lane of this type takes, by the name it lies under in the Lane's `args`, with
# what it is, as lay.py types shows it. It takes none, as the Routes name each Result that its
# sentence gives.
ARGS: dict[str, str] = {}


class EndsByResult:
    """The lane type, as lanes/ finds it by `TYPE`."""

    def info(self) -> TypeInfo:
        """What lay.py types shows of the type: its name, `ends_by_result`, its sentence, the
        steps it suits, what it allows, and `ARGS`.

        Carries: S1 `L->>T: each type`.
        """
        raise NotImplementedError("ends_by_result.EndsByResult.info")

    def faults(self, lane: Lane, last_step: int, routes: Sequence[Route]) -> tuple[str, ...]:
        """Each fault of a Lane of this type, such as a Step that isn't its role's last, or a role
        that the Routes give no Result.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`.
        """
        raise NotImplementedError("ends_by_result.EndsByResult.faults")

    def sentence(self, lane: Lane, routes: Sequence[Route]) -> str:
        """The sentence that the Lane lays on the role's last Step: `End by running` the result
        script with each Result that the Routes name for the role, a Route's `after` for a
        subagent and a move's `no_more` for the skill, joined by `or`.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`, and the sentence of each
        Broken.
        """
        raise NotImplementedError("ends_by_result.EndsByResult.sentence")

    def allows(self, lane: Lane, call: Call, held: Held) -> bool | None:
        """True for a Bash run of the result script for the Lane's role, as
        `script_calls.result_args` reads it, whatever the Result, as result.py refuses one the
        role may not give; None for any other Call. lanes/ keeps a Call that this allows,
        whatever the other types say.

        Carries: the Call checks of S2, S5, and S6.
        """
        raise NotImplementedError("ends_by_result.EndsByResult.allows")

    def check_start(self, lane: Lane, asked: StartCall, held: Held, due: Sequence[Due]) -> Verdict:
        """Broken, with the Lane's sentence, where a subagent starts or resumes a role of the plugin
        (`asked.ours`), as only the main conversation starts the roles; else Kept.

        Carries: S6 `else it starts a role of the plugin` and `G-->>SA: stops it, with the
        sentence of the Lane on its last Step`.
        """
        raise NotImplementedError("ends_by_result.EndsByResult.check_start")

    def check_end(self, lane: Lane, end: EndAsked, held: Held) -> Verdict:
        """Broken, with the Lane's sentence, where the subagent's Start holds no Result; Kept for
        the main conversation's end, which the moves due hold, and for a Start with a Result.

        Carries: S6 `alt the Lane on its last Step finds no Result since its Start` and `G-->>SA:
        stops the end, with that Lane's sentence`.
        """
        raise NotImplementedError("ends_by_result.EndsByResult.check_end")


TYPE = EndsByResult()
