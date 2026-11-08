"""Decides which checks run on a hook event, and what the role, the main conversation, and whoever
runs the plugin hear from them.

The guard holds a role of the plugin that has lanes to its steps. A check that can't run stops the
call it's about, and says why and who must fix it, as the architecture's principle "A call that
the guard can't check stops" says.
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any, NamedTuple

import laid
import lanes
import plugin
import step

# Who fixes the lanes laid, as `lay.py write` lays them again from a proposal.
LAY_AGAIN = "the maker of {plugin} must lay its lanes again with Lane's lay.py write"
# Who fixes a hook input that Claude Code gave out of its documented form.
CLAUDE_CODE = "Anthropic must fix Claude Code, whose hook input isn't as its documentation gives it"


class Event(NamedTuple):
    """A hook event, as hook.py reads it from Claude Code's hook input."""

    # The event's name, such as PreToolUse.
    name: str
    # The session's ID.
    session: str
    # The folder that the session works in.
    cwd: str
    # The ID of the subagent that the event comes from, or None for the main conversation.
    agent_id: str | None = None
    # The type of that subagent, such as `changelog:writer`, or None.
    agent_type: str | None = None
    # The tool of a tool event, or None.
    tool: str | None = None
    # The tool's input of a tool event.
    tool_input: Mapping[str, Any] = MappingProxyType({})
    # What the tool gave back, in PostToolUse.
    tool_response: Any = None
    # The prompt of UserPromptSubmit.
    prompt: str | None = None
    # The command of UserPromptExpansion, such as `changelog:write`.
    command: str | None = None
    # Whether a stop hook kept the conversation or the role going before, in Stop and SubagentStop.
    stop_active: bool = False


class Answer(NamedTuple):
    """What the guard answers Claude Code. Each field left None says nothing."""

    # Why a tool call stops, which the role or the main conversation reads.
    deny: str | None = None
    # Why a tool call goes to the person to approve.
    ask: str | None = None
    # What Claude Code adds beside the event for the role or the main conversation.
    context: str | None = None
    # Why the role or the main conversation goes on, where it would end.
    block: str | None = None
    # What whoever runs the plugin reads.
    tell: str | None = None


class _Fault(Exception):
    """A check that can't run, with what's wrong, who must fix it, and the lane it's about, or
    None where it's about every lane of the role."""

    def __init__(self, what: str, who: str, lane: laid.Lane | None = None) -> None:
        super().__init__(what)
        self.what = what
        self.who = who
        self.lane = lane


class _Held(NamedTuple):
    """A role that the guard holds, with what its checks read."""

    plugin: str
    root: str
    project: str | None
    role: laid.Role
    part: step.Part


def answer(name: str, root: str, project: str | None, event: Event) -> Answer:
    """The guard's answer to the event of the plugin of the name, which lies at the root, in the
    project at the folder given, or None where Claude Code gave no project folder."""
    if event.agent_type is None or not event.agent_type.startswith(name + ":"):
        return Answer()
    role = event.agent_type[len(name) + 1 :]
    try:
        held = _held(name, root, project, role)
        if held is None or event.name != "PreToolUse":
            return Answer()
        return _call(held, event)
    except _Fault as fault:
        where = (
            f"the lanes of {role}"
            if fault.lane is None
            else f"{fault.lane.lane} on step {fault.lane.step} of {role}"
        )
        told = (
            f"{name}: lane cannot check {where}: {fault.what}. Ask the main conversation for"
            f" the fix: {fault.who}. Go on with the rest of your work meanwhile."
        )
        return Answer(deny=told, tell=told)


def _held(name: str, root: str, project: str | None, role: str) -> _Held | None:
    """The role as the guard holds it, or None where it has no lanes.

    It raises _Fault where the guard can't read the lanes laid, the role's entry, or its part.
    """
    lay_again = LAY_AGAIN.format(plugin=name)
    try:
        found = laid.read(root).role(role)
        if found is None:
            return None
        entry = plugin.subagent(root, role)
        part = step.part(root, entry)
    except (laid.Unlaid, plugin.Fault) as why:
        raise _Fault(str(why), lay_again) from None
    if not entry.background:
        raise _Fault(
            f"{entry.path} no longer sets `background: true`",
            f"the maker of {name} must set `background: true` in {entry.path}",
        )
    if part.steps:
        _check_steps(found, part, lay_again)
    return _Held(name, root, project, found, part)


def _check_steps(role: laid.Role, part: step.Part, lay_again: str) -> None:
    """Checks that each step that a lane is on still says the lane's sentence.

    It raises _Fault where the part no longer holds a step that a lane is on, or where the step no
    longer says the lane's sentence.
    """
    steps = {s.number: s for s in part.steps}
    for lane in role.lanes:
        said = lanes.sentence(lane.lane, list(lane.takes))
        if lane.step not in steps:
            raise _Fault(f"the steps hold no step {lane.step}", lay_again, lane)
        if said not in steps[lane.step].says:
            raise _Fault(f'step {lane.step} no longer says "{said}"', lay_again, lane)


def _call(held: _Held, event: Event) -> Answer:
    """The answer to a tool call of the role: a deny with the sentence of the first lane it
    breaks, or nothing."""
    if held.project is None:
        raise _Fault(
            "Claude Code gave the hook no CLAUDE_PROJECT_DIR",
            f"whoever runs {held.plugin} must run it in a Claude Code that gives each hook"
            " CLAUDE_PROJECT_DIR",
        )
    call = lanes.Call(event.tool or "", event.tool_input, event.cwd)
    given = {lane: _given(held, held.project, lane) for lane in held.role.lanes}
    context = _context(given)
    for lane in held.role.lanes:
        kind = lanes.TYPES[lane.lane]
        if given[lane] is None or not hasattr(kind, "check"):
            continue
        try:
            line = kind.check(call, given[lane], context)
        except lanes.Unchecked as why:
            raise _Fault(str(why), CLAUDE_CODE) from None
        if line:
            return Answer(
                deny=f"{held.plugin}: {lanes.sentence(lane.lane, list(lane.takes))}\n{line}"
            )
    return Answer()


def _given(held: _Held, project: str, lane: laid.Lane) -> dict[str, list[str]] | None:
    """What the lane takes on this call, as lanes.given puts it."""
    try:
        return lanes.given(lane.lane, list(lane.takes), {}, held.root, project)
    except lanes.Unchecked as why:
        raise _Fault(str(why), LAY_AGAIN.format(plugin=held.plugin), lane) from None


def _context(given: dict[laid.Lane, dict[str, list[str]] | None]) -> lanes.Context:
    """What the role's lanes allow beside each lane's own takes: each command any of its lanes
    names."""
    commands: list[str] = []
    for lane, places in given.items():
        where = lanes.commands_place(lane.lane)
        if where and places is not None:
            commands += places[where]
    return lanes.Context(tuple(dict.fromkeys(commands)), ())
