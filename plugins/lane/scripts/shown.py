"""Decides how `lay.py print` shows a Proposal to the caller: the Routes laid on the skill's step,
each Step as it'll read once laid, each Lane with its sentence and type, the commands each role may
run, the notes beside a step, and the ID, in the form that Lane's README shows."""

from __future__ import annotations

from collections.abc import Sequence

from domain.laid_set import CALL, RESUME, START, WAIT, Lane, Move, Route
from domain.lanes import may_run
from proposal import Proposal, role_order
from steps import Role, Step

# How each lane reads in the list of a role's lanes, by its type.
_LABELS = {"run_only": "run", "write_only": "write", "gives_result": "end"}


def reads(step: Step, sentences: Sequence[str]) -> str:
    """The Step as it'll read once laid: its words, then each sentence that its own words don't
    already say, each after one space."""
    words = step.words
    for sentence in sentences:
        if sentence not in words:
            words += f" {sentence}"
    return words


def notes(proposal: Proposal, found: Sequence[Role]) -> list[str]:
    """Each note beside the Proposal: each step that names in backticks a command its subagent may
    not run, each role whose Steps name no command, so that Lane holds only how it ends, and each
    laid sentence that the user changed, which Lane keeps as their own words."""
    raise NotImplementedError("shown.notes")


def text(proposal: Proposal, found: Sequence[Role]) -> str:
    """What `lay.py print` prints for the Proposal, ending with its ID and the line that asks for
    `yes` or what to change."""
    by_name = {role.name: role for role in found}
    blocks = []
    for role in role_order(proposal):
        lanes = sorted((lane for lane in proposal.lanes if lane.role == role), key=_number)
        if role in proposal.skills:
            blocks.append(_routes(proposal, role, lanes))
        else:
            blocks.append(_lanes(role, lanes))
        blocks.append(_laid_steps(by_name[role], lanes))
    asked = f"Reply yes to lay these into {proposal.plugin}, or say what to change."
    blocks.append(f"ID: {proposal.id}\n{asked}")
    return "\n\n".join(blocks) + "\n"


def _number(lane: Lane) -> int:
    return lane.step


def _routes(proposal: Proposal, skill: str, lanes: Sequence[Lane]) -> str:
    step = next((lane.step for lane in lanes if lane.type == "gives_result"), 1)
    rows = [(_after(r), _moves(r.moves)) for r in proposal.routes if r.skill == skill]
    width = max(len(after) for after, _ in rows)
    lines = [f"  {after.ljust(width)}  {moves}" for after, moves in rows]
    return "\n".join([f"Routes of {skill}, laid on its step {step}:", *lines])


def _after(route: Route) -> str:
    words = route.after.split()
    if len(words) == 2 and not route.after.startswith("/") and ":" not in route.after:
        return f"{words[0]} `{words[1]}`"
    return route.after


def _moves(moves: Sequence[Move]) -> str:
    return " or ".join(_move(move) for move in moves)


def _move(move: Move) -> str:
    if move.kind == START and move.waits_for:
        return f"start {move.role} once the person types {move.waits_for}"
    if move.kind in (START, RESUME, CALL):
        return f"{move.kind} {move.role}"
    if move.kind == WAIT:
        return "wait for the person's reply"
    return "start no more"


def _lanes(role: str, lanes: Sequence[Lane]) -> str:
    labels = [f"{_LABELS[lane.type]}:" for lane in lanes]
    label_width = max(len(label) for label in labels)
    typed = [lane.sentence for lane in lanes if _LABELS[lane.type] != "end"]
    sentence_width = max((len(sentence) for sentence in typed), default=0)
    lines = [f"Lanes of {role}, each checked only in {role}:"]
    for lane, label in zip(lanes, labels):
        line = f"  step {lane.step}  {label.ljust(label_width)} {lane.sentence}"
        if label != "end:":
            line = (
                f"{line.ljust(len(line) - len(lane.sentence) + sentence_width)}  type {lane.type}"
            )
        lines.append(line)
    if any(lane.type == "run_only" for lane in lanes):
        commands = " or ".join(f"`{each}`" for each in may_run(lanes, "${CLAUDE_PLUGIN_ROOT}"))
        lines.append(f"  commands: {role} may run only {commands}")
    return "\n".join(lines)


def _laid_steps(role: Role, lanes: Sequence[Lane]) -> str:
    steps = [step for step in role.steps if any(lane.step == step.number for lane in lanes)]
    return "\n".join(
        reads(step, [lane.sentence for lane in lanes if lane.step == step.number]) for step in steps
    )
