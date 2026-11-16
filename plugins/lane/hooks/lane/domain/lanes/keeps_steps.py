"""The rule that a role marks each Step done in order by step.py, laid on its last Step: the
sentence that names the script, and the check that holds the role's end until each Step is marked
in its latest pass."""

from __future__ import annotations

from collections.abc import Sequence

from form import Lane, Route
from marks import step_due
from place import Call, EndAsked, StartCall
from runs import Due
from script_calls import step_command

from lanes.kind import Broken, Held, Kept, Marking, TypeInfo, Verdict

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
            " `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/step.py <role> <n>` as a command of its"
            " own, with the step's number.",
            suits="the last Step of a role whose Steps are done in order",
            allows="nothing: it holds the role's end until each Step is marked since its last"
            " Mark of Step 1",
            args=ARGS,
        )

    def faults(self, lane: Lane, last_step: int, routes: Sequence[Route]) -> tuple[str, ...]:
        """Each fault of a Lane of this type, such as a Step that isn't its role's last.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`.
        """
        if lane.step != last_step:
            return (f"keeps_steps lies on {lane.role}'s last Step, {last_step}",)
        return ()

    def sentence(self, lane: Lane, routes: Sequence[Route]) -> str:
        """The sentence that the Lane lays on the role's last Step: to run
        `script_calls.step_command` for the role as each Step ends, as a command of its own, with
        its number, as the guard takes a Mark only from such a run.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`, and the sentence of each
        Broken.
        """
        return (
            f"As each step ends, run `{step_command(lane.role)}` as a command of its own, with the"
            " step's number."
        )

    def allows(self, lane: Lane, call: Call, held: Held) -> bool | None:
        """None: the guard checks a run of step.py by the Lanes on its Step, and the Lane judges no
        Call.

        Carries: the Call checks of S2, S5, and S6.
        """
        return None

    def check_start(self, lane: Lane, asked: StartCall, held: Held, due: Sequence[Due]) -> Verdict:
        """Kept: the Lane checks no start.

        Carries: S5 `G->>T: checks the start by the Lane of the skill's Routes, with the moves due`.
        """
        return Kept()

    def check_mark(self, lane: Lane, marking: Marking, held: Held) -> Verdict:
        """Kept: the guard takes a Mark only for the Step due, as `marks.may_mark` gives, before
        it asks the Lanes on the Step, and the Lane checks no Mark.

        Carries: S6 `G->>T: checks the Mark by each Lane on Step n`.
        """
        return Kept()

    def check_end(self, lane: Lane, end: EndAsked, held: Held) -> Verdict:
        """Broken, with the Lane's sentence and the Step due, where `marks.step_due` gives a Step
        for the Start's Marks, or the skill's Run's for the main conversation, with the Lane's
        Step as the last; else Kept.

        Carries: S6 `else a Lane of keeps_steps finds a Step unmarked in the latest pass` and
        `G-->>SA: stops the end, with that Lane's sentence and the Step due`; S5 `G->>T: checks the
        end by each Lane of each Run's skill`.
        """
        reports = held.start.reports if held.start else held.run.reports
        due = step_due(reports, lane.step)
        if due is None:
            return Kept()
        return broken(lane, held, due)


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
    return next((x.step for x in lanes if x.role == role and x.type == "keeps_steps"), None)


def broken(lane: Lane, held: Held, due: int | None) -> Broken:
    """The Lane broken, as a stop gives it: its sentence, with the plugin's folder in place of
    `${CLAUDE_PLUGIN_ROOT}`, and the Step due.

    Takes: a Lane of this type; what it's held to; and the Step due in the latest pass, None where
    that pass has marked each Step.
    Gives: the Broken, whose `may` names the Step due, or, with none, that a new pass begins at
    Step 1.
    Changes: nothing.
    Refuses: nothing.
    Carries: S6 `G-->>SA: stops it, with the Step due` and `G-->>SA: stops the end, with that
    Lane's sentence and the Step due`.
    """
    said = TYPE.sentence(lane, held.routes).replace("${CLAUDE_PLUGIN_ROOT}", held.root)
    may = f"Step {due} is due." if due else "Each step is marked; a new pass begins at step 1."
    return Broken(lane, said, may)
