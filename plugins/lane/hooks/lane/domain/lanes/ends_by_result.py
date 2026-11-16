"""The rule that a role ends by the result script, laid on its last Step: the sentence that names
the script with each Result the role may give, and the checks that hold the role to it, the
script's run let through, a subagent's start of a role stopped, and an end with no Result
stopped."""

from __future__ import annotations

from collections.abc import Sequence

from form import Lane, Route
from place import Call, EndAsked, StartCall
from runs import Due
from script_calls import result_args, result_command

from lanes.kind import Broken, Held, Kept, Marking, TypeInfo, Verdict

# Each value that a Lane of this type takes, by the name it lies under in the Lane's `args`, with
# what it is, as lay.py types shows it. It takes none, as the Routes name each Result that its
# sentence gives.
ARGS: dict[str, str] = {}
# What a role may do where its end holds no Result: the guard takes a Result only from a command
# that runs the result script alone, as only its exit tells that the script gave 0, and the run
# record keeps no Call to tell a role that ran it inside a longer command from one that never ran
# it, so every such stop says it.
ALONE = "Run it as a command of its own: result.py run inside a longer command gives no Result."


class EndsByResult:
    """The lane type, as lanes/ finds it by `TYPE`."""

    def info(self) -> TypeInfo:
        """What lay.py types shows of the type: its name, `ends_by_result`, its sentence, the
        steps it suits, what it allows, and `ARGS`.

        Carries: S1 `L->>T: each type`.
        """
        return TypeInfo(
            name="ends_by_result",
            sentence="End by running `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py <role>"
            " <result>`, with each Result the Routes name for the role, joined by `or`.",
            suits="the last Step of the skill and of each subagent, which Lane lays it on",
            allows="the role's run of the result script, whatever the other Lanes of the role say",
            args=ARGS,
        )

    def faults(self, lane: Lane, last_step: int, routes: Sequence[Route]) -> tuple[str, ...]:
        """Each fault of a Lane of this type, such as a Step that isn't its role's last, or a role
        that the Routes give no Result.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`.
        """
        found = []
        if lane.step != last_step:
            found.append(f"ends_by_result lies on {lane.role}'s last Step, {last_step}")
        if not commands(lane.role, routes):
            found.append(f"ends_by_result needs a Result that the Routes name for {lane.role}")
        return tuple(found)

    def sentence(self, lane: Lane, routes: Sequence[Route]) -> str:
        """The sentence that the Lane lays on the role's last Step: `End by running` the result
        script with each Result that the Routes name for the role, a Route's `after` for a
        subagent and a move's `no_more` for the skill, joined by `or`.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`, and the sentence of each
        Broken.
        """
        named = " or ".join(f"`{command}`" for command in commands(lane.role, routes))
        return f"End by running {named}."

    def allows(self, lane: Lane, call: Call, held: Held) -> bool | None:
        """True for a Bash run of the result script for the Lane's role, as
        `script_calls.result_args` reads it, whatever the Result, as result.py refuses one the
        role may not give; None for any other Call. lanes/ keeps a Call that this allows,
        whatever the other types say.

        Carries: the Call checks of S2, S5, and S6.
        """
        command = call.input.get("command") if call.tool == "Bash" else None
        given = result_args(command, held.root) if isinstance(command, str) else None
        return True if given and given[0] == lane.role else None

    def check_start(self, lane: Lane, asked: StartCall, held: Held, due: Sequence[Due]) -> Verdict:
        """Broken, with the Lane's sentence, where a subagent starts or resumes a role of the plugin
        (`asked.ours`), as only the main conversation starts the roles; else Kept.

        Carries: S6 `else it starts a role of the plugin` and `G-->>SA: stops it, with the
        sentence of the Lane on its last Step`.
        """
        if held.start is not None and asked.ours:
            return self._broken(lane, held)
        return Kept()

    def check_mark(self, lane: Lane, marking: Marking, held: Held) -> Verdict:
        """Kept: the Lane checks no Mark.

        Carries: S6 `G->>T: checks the Mark by each Lane on Step n`.
        """
        raise NotImplementedError("ends_by_result.check_mark")

    def check_end(self, lane: Lane, end: EndAsked, held: Held) -> Verdict:
        """Broken, with the Lane's sentence and `ALONE`, where the subagent's Start holds no
        Result; Kept for the main conversation's end, which the moves due hold, and for a Start
        with a Result.

        Carries: S6 `alt the Lane on its last Step finds no Result since its Start` and `G-->>SA:
        stops the end, with that Lane's sentence`.
        """
        if held.start is not None and not held.start.results:
            return self._broken(lane, held, ALONE)
        return Kept()

    def _broken(self, lane: Lane, held: Held, may: str = "") -> Broken:
        """The Lane broken, its sentence naming the result script by the plugin's folder, with what
        the role may do."""
        said = self.sentence(lane, held.routes).replace("${CLAUDE_PLUGIN_ROOT}", held.root)
        return Broken(lane, said, may)


TYPE = EndsByResult()


def commands(role: str, routes: Sequence[Route]) -> tuple[str, ...]:
    """The commands by which the role gives each Result it may give.

    Takes: a role or skill, and the Routes.
    Gives: the result script's run with each Result, in the order the Routes name them: those a
    Route goes after for a subagent, and those a move starts no more by for the skill; none where
    the Routes name none.
    Changes: nothing.
    Refuses: nothing.
    Carries: the sentence of the Lane on a role's last Step, and what a stop says the role may run.
    """
    given = [r.after.result for r in routes if r.after.kind == "result" and r.after.role == role]
    given += [m.result for r in routes if r.skill == role for m in r.moves if m.kind == "no_more"]
    return tuple(result_command(role, str(result)) for result in dict.fromkeys(given))
