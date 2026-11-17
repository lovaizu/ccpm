"""The Lane that holds an end to a command of the plugin's: the sentence, and the check that the
command, run in the hook event's cwd with the run values and the Result filled in, gives 0."""

from __future__ import annotations

import subprocess
from collections.abc import Sequence

from form import Lane, Route
from place import Call, EndAsked, StartCall
from runs import Due

from lanes.kind import Broken, CantCheck, Held, Kept, Marking, TypeInfo, Verdict

# The exit codes by which the shell says a command couldn't run: found but not executable, and not
# found, as POSIX's Shell Command Language gives them.
CANT_RUN = (126, 127)
# Each value that a Lane of this type takes, by the name it lies under in the Lane's `args`, with
# what it is, as lay.py types shows it.
ARGS: dict[str, str] = {
    "command": (
        "The command of the plugin's that the end must pass, word for word, with `{result}` for"
        " the Result given and `{<name>}` for a run value."
    ),
}


class EndsChecked:
    """The lane type, as lanes/ finds it by `TYPE`."""

    def info(self) -> TypeInfo:
        """What lay.py types shows of the type: its name, `ends_checked`, its sentence, the steps it
        suits, what it allows, and `ARGS`.

        Carries: S1 `L->>T: each type`.
        """
        return TypeInfo(
            name="ends_checked",
            sentence="End once `<command>` gives 0.",
            suits="a Step whose end a command of the plugin's checks",
            allows="nothing: it holds the end, as Lane runs `command` with the Result filled in",
            args=ARGS,
        )

    def faults(self, lane: Lane, last_step: int, routes: Sequence[Route]) -> tuple[str, ...]:
        """Each fault of a Lane of this type, such as `command` missing or not a string.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`.
        """
        if not isinstance(lane.args.get("command"), str):
            return ("ends_checked takes `command`, the command as one string",)
        return ()

    def sentence(self, lane: Lane, routes: Sequence[Route]) -> str:
        """The sentence that the Lane lays on its Step, with `command` in it.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`, and the sentence of each
        Broken.
        """
        return f"End once `{lane.args['command']}` gives 0."

    def allows(self, lane: Lane, call: Call, held: Held) -> bool | None:
        """None: Lane runs the command at the end, and the Lane judges no Call.

        Carries: the Call checks of S4 and S5.
        """
        return None

    def check_start(self, lane: Lane, asked: StartCall, held: Held, due: Sequence[Due]) -> Verdict:
        """Kept: the Lane checks no start.

        Carries: S4 `G->>T: checks the start by the Lane of the skill's Routes, with the moves due`.
        """
        return Kept()

    def check_mark(self, lane: Lane, marking: Marking, held: Held) -> Verdict:
        """Kept: the Lane checks no Mark.

        Carries: S5 `G->>T: checks the Mark by each Lane on Step n`.
        """
        return Kept()

    def check_end(self, lane: Lane, end: EndAsked, held: Held) -> Verdict:
        """Kept where `command` gives 0, run by the shell in the hook event's cwd with each run
        value of the Start filled in and `{result}` as the Start's last Result, or the skill's own
        for the main conversation; Broken, with the Lane's sentence, where it gives another code;
        CantCheck, with why and the plugin's developer to fix it, where the shell can't run it.

        Carries: S4 and S5 `opt a Lane holds the end to a command of the plugin's`, and `alt a Lane
        is broken`.
        """
        start = held.start
        values = dict(start.values) if start else {}
        skills = tuple(r.result for r in held.run.results if r.role == held.run.skill)
        results = start.results if start else skills
        values["result"] = results[-1] if results else ""
        command = str(lane.args["command"])
        for name, value in values.items():
            command = command.replace(f"{{{name}}}", value)
        code = run(["sh", "-c", command], held.cwd)
        if code in CANT_RUN:
            why = f"`{command}` couldn't run, as the shell gave {code}"
            return CantCheck(why, f"The developer of the plugin must fix {lane.file}")
        if code != 0:
            said = self.sentence(lane, held.routes).replace("${CLAUDE_PLUGIN_ROOT}", held.root)
            return Broken(lane, said, "")
        return Kept()


TYPE = EndsChecked()


def run(command: Sequence[str], cwd: str) -> int:
    """Runs a command of the plugin's, as an ends_checked Lane names it with its values filled in.

    Takes: the command's words, and the hook event's cwd.
    Gives: its exit code.
    Changes: whatever the command changes.
    Refuses: OSError, where the command can't start, which the Lane gives as CantCheck.
    Carries: S4 and S5 `T->>PC: runs it` and `PC-->>T: its exit code`.
    """
    return subprocess.run(list(command), cwd=cwd, check=False).returncode
