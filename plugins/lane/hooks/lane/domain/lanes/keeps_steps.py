"""The rule that a role marks each Step done in order by step.py, laid on its last Step: the
sentence that names the script, and the check that holds the role's end until each Step is marked
in its latest pass."""

from __future__ import annotations

from collections.abc import Sequence

from form import Lane, Route
from place import Call, EndAsked, StartCall
from runs import Due

from lanes.kind import Held, Marking, TypeInfo, Verdict

# Each value that a Lane of this type takes, by the name it lies under in the Lane's `args`, with
# what it is, as lay.py types shows it. It takes none, as its Step is the role's last.
ARGS: dict[str, str] = {}


class KeepsSteps:
    """The lane type, as lanes/ finds it by `TYPE`."""

    def info(self) -> TypeInfo:
        """What lay.py types shows of the type: its name, `keeps_steps`, its sentence, the steps it
        suits, what it allows, and `ARGS`.

        Carries: S1 `L->>T: each type`.
        """
        return TypeInfo(
            name="keeps_steps",
            sentence="As each step ends, run"
            " `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/step.py <role> <n>`, with the step's"
            " number.",
            suits="the last Step of a role whose Steps are done in order",
            allows="nothing: it holds the role's end until each Step is marked since its last"
            " Mark of Step 1",
            args=ARGS,
        )

    def faults(self, lane: Lane, last_step: int, routes: Sequence[Route]) -> tuple[str, ...]:
        """Each fault of a Lane of this type, such as a Step that isn't its role's last.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`.
        """
        raise NotImplementedError("keeps_steps.faults")

    def sentence(self, lane: Lane, routes: Sequence[Route]) -> str:
        """The sentence that the Lane lays on the role's last Step: to run
        `script_calls.step_command` for the role as each Step ends, with its number.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`, and the sentence of each
        Broken.
        """
        raise NotImplementedError("keeps_steps.sentence")

    def allows(self, lane: Lane, call: Call, held: Held) -> bool | None:
        """None: the guard checks a run of step.py by the Lanes on its Step, and the Lane judges no
        Call.

        Carries: the Call checks of S2, S5, and S6.
        """
        raise NotImplementedError("keeps_steps.allows")

    def check_start(self, lane: Lane, asked: StartCall, held: Held, due: Sequence[Due]) -> Verdict:
        """Kept: the Lane checks no start.

        Carries: S5 `G->>T: checks the start by the Lane of the skill's Routes, with the moves due`.
        """
        raise NotImplementedError("keeps_steps.check_start")

    def check_mark(self, lane: Lane, marking: Marking, held: Held) -> Verdict:
        """Kept: the guard takes a Mark only for the Step due, as `marks.may_mark` gives, before
        it asks the Lanes on the Step, and the Lane checks no Mark.

        Carries: S6 `G->>T: checks the Mark by each Lane on Step n`.
        """
        raise NotImplementedError("keeps_steps.check_mark")

    def check_end(self, lane: Lane, end: EndAsked, held: Held) -> Verdict:
        """Broken, with the Lane's sentence and the Step due, where `marks.step_due` gives a Step
        for the Start's Marks, or the skill's Run's for the main conversation, with the Lane's
        Step as the last; else Kept.

        Carries: S6 `else a Lane of keeps_steps finds a Step unmarked in the latest pass` and
        `G-->>SA: stops the end, with that Lane's sentence and the Step due`; S5 `G->>T: checks the
        end by each Lane of each Run's skill`.
        """
        raise NotImplementedError("keeps_steps.check_end")


TYPE = KeepsSteps()


def last_step(lanes: Sequence[Lane], role: str) -> int | None:
    """The role's last Step, as its Lane of keeps_steps lies on it.

    Takes: the Lanes of lanes.json, and the role or skill.
    Gives: the Step of the role's Lane of keeps_steps; None where the role has none, as it keeps
    no Steps.
    Changes: nothing.
    Refuses: nothing.
    Carries: S6 `alt Step n isn't due in the latest pass of its Start` and `G->>A: asks for the
    Items of the Step due, with the role and the Start's run values`, for the Step that ends a
    pass.
    """
    raise NotImplementedError("keeps_steps.last_step")
