"""The Lane that holds a Step's Mark until the role has marked each Item of the Step's checklist by
item.py since the Step began, the Items being those the plugin's adapter of a step's items gives."""

from __future__ import annotations

from collections.abc import Sequence

from form import Lane, Route
from place import Call, EndAsked, StartCall
from runs import Due

from lanes.kind import Held, Marking, TypeInfo, Verdict

# Each value that a Lane of this type takes, by the name it lies under in the Lane's `args`, with
# what it is, as lay.py types shows it. It takes none, as the adapter gives the Items.
ARGS: dict[str, str] = {}


class KeepsItems:
    """The lane type, as lanes/ finds it by `TYPE`."""

    def info(self) -> TypeInfo:
        """What lay.py types shows of the type: its name, `keeps_items`, its sentence, the steps it
        suits, what it allows, and `ARGS`.

        Carries: S1 `L->>T: each type`.
        """
        return TypeInfo(
            name="keeps_items",
            sentence="As each item of this step's checklist is done, run"
            " `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/item.py <role> <id>`, with the item's ID.",
            suits="a Step that keeps a checklist of the plugin's, laid with keeps_steps",
            allows="nothing: it holds the Step's Mark until each Item the adapter gives is marked",
            args=ARGS,
        )

    def faults(self, lane: Lane, last_step: int, routes: Sequence[Route]) -> tuple[str, ...]:
        """Each fault of a Lane of this type alone; none, as it takes no value.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`.
        """
        raise NotImplementedError("keeps_items.faults")

    def sentence(self, lane: Lane, routes: Sequence[Route]) -> str:
        """The sentence that the Lane lays on its Step: to run `script_calls.item_command` for the
        role as each Item is done, with its ID.

        Carries: S1 `L->>T: checks each Lane, and makes its sentence`, and the sentence of each
        Broken.
        """
        raise NotImplementedError("keeps_items.sentence")

    def allows(self, lane: Lane, call: Call, held: Held) -> bool | None:
        """None: the guard checks a run of item.py by the Items that the adapter gives for the
        Step due, and the Lane judges no Call.

        Carries: the Call checks of S2, S5, and S6.
        """
        raise NotImplementedError("keeps_items.allows")

    def check_start(self, lane: Lane, asked: StartCall, held: Held, due: Sequence[Due]) -> Verdict:
        """Kept: the Lane checks no start.

        Carries: S5 `G->>T: checks the start by the Lane of the skill's Routes, with the moves due`.
        """
        raise NotImplementedError("keeps_items.check_start")

    def check_mark(self, lane: Lane, marking: Marking, held: Held) -> Verdict:
        """Kept where `marks.items_left` gives none of `marking.items` since the Step began;
        Broken, with the Lane's sentence and the Items left, where it gives some.

        Carries: S6 `G->>T: checks the Mark by each Lane on Step n, with the Reads and Marks since
        the Step began`, and `else ... an Item isn't marked`.
        """
        raise NotImplementedError("keeps_items.check_mark")

    def check_end(self, lane: Lane, end: EndAsked, held: Held) -> Verdict:
        """Kept: the Lane checks no end, as keeps_steps holds the end until the Step is marked.

        Carries: S6 `G->>T: checks the end by each Lane of the role`.
        """
        raise NotImplementedError("keeps_items.check_end")


TYPE = KeepsItems()
