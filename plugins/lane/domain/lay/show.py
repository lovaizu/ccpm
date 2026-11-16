"""How lay.py print shows a Proposal, as the person reads it before they approve: the Routes of each
skill, each Lane of each role with the Step it's laid on, each Step as it will read, and the
Proposal's ID with what to reply."""

from __future__ import annotations

from collections.abc import Sequence

from form import After, Lane, Move, Proposal, Route
from lanes import ends_by_result, sentence
from script_calls import id_line

from lay.steps import Step

# The word that names each lane type in the table of a role's Lanes.
LABELS = {
    "run_only": "run",
    "write_only": "write",
    "ends_checked": "check",
    "ends_by_result": "end",
    "reads_whole": "read",
    "reads_none": "never",
    "keeps_items": "items",
    "keeps_steps": "steps",
}


def render(proposal: Proposal, steps: Sequence[Step], proposal_id: str, plugin: str) -> str:
    """What lay.py print shows.

    Takes: the Proposal, each Step as it will read once laid, the ID it's kept by, and the
    plugin's name, which the line that asks for yes or a change names.
    Gives: the words, ending with `script_calls.id_line` and the line that asks for yes or a
    change, as the README's walkthrough shows.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `L-->>UP: the Routes, each Step as it'll read, and the ID`.
    """
    roles = list(dict.fromkeys(lane.role for lane in proposal.lanes))
    blocks = [_role(proposal, steps, role) for role in roles]
    asked = f"Reply yes to lay these into {plugin}, or say what to change."
    return "\n\n".join([*blocks, f"{id_line(proposal_id)}\n{asked}"]) + "\n"


def _role(proposal: Proposal, steps: Sequence[Step], role: str) -> str:
    """One role's block: the Routes of a skill, or the table of a subagent's Lanes, and then each
    of its Steps that a Lane lies on, as it will read."""
    lanes = [lane for lane in proposal.lanes if lane.role == role]
    on = {(lane.file, lane.step) for lane in lanes}
    shown = "\n".join(f"{s.number}. {s.text}" for s in steps if (s.file, s.number) in on)
    routed = [lane for lane in lanes if lane.type == "routes"]
    head = _routes(proposal.routes, routed[0]) if routed else _lanes(proposal, lanes, role)
    return f"{head}\n\n{shown}"


def _routes(routes: Sequence[Route], lane: Lane) -> str:
    """The Routes of the skill, after what each goes after and its moves."""
    rows = [
        (_after(r.after), ", ".join(_move(m) for m in r.moves))
        for r in routes
        if r.skill == lane.role
    ]
    width = max(len(after) for after, _ in rows) + 2
    table = "\n".join(f"  {after.ljust(width)}{moves}" for after, moves in rows)
    return f"Routes of {lane.role}, laid on its step {lane.step}:\n{table}"


def _after(after: After) -> str:
    """What a Route goes after, in the words of Lane's page of steps, routes, and adapters: `first`,
    such as ``writer `written` `` for a Result, `the person types pause` for a command, and `the
    call of lint:check` for another plugin's run that hands its work back."""
    if after.kind == "command":
        return f"the person types {after.command}"
    if after.kind == "returned":
        return f"the call of {after.skill}"
    return "first" if after.kind == "first" else f"{after.role} `{after.result}`"


def _move(move: Move) -> str:
    """A move as the table of Routes names it, such as `start writer` or `start no more`."""
    if move.kind == "no_more":
        return "start no more"
    named = move.role or move.command or move.skill or ""
    return f"{move.kind} {named}".rstrip()


def _lanes(proposal: Proposal, lanes: Sequence[Lane], role: str) -> str:
    """The table of a subagent's Lanes, each with its Step, its kind, its sentence, and, but for
    the end's, its type; and the commands it may run, where a Lane lets it run only some."""
    said = [(lane, sentence(lane, lane.step, proposal.routes)) for lane in lanes]
    label = max(len(LABELS[lane.type]) for lane in lanes) + 2
    typed = [len(s) for lane, s in said if lane.type != "ends_by_result"]
    width = max(typed, default=0) + 2
    rows = []
    for lane, text in said:
        kind = f"{LABELS[lane.type]}:".ljust(label)
        row = f"  step {lane.step}  {kind}{text}"
        if lane.type != "ends_by_result":
            row = f"  step {lane.step}  {kind}{text.ljust(width)}type {lane.type}"
        rows.append(row)
    commands = [c for lane in lanes if lane.type == "run_only" for c in lane.args["commands"]]
    if commands:
        commands += ends_by_result.commands(role, proposal.routes)
        named = " or ".join(f"`{c}`" for c in commands)
        rows.append(f"  commands: {role} may run only {named}")
    return f"Lanes of {role}, each checked only in {role}:\n" + "\n".join(rows)
