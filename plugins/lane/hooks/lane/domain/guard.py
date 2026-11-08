"""Decides which checks run on a hook event, and what the role, the main conversation, and whoever
runs the plugin hear from them.

The guard holds each role of the plugin that has lanes or that the routes name, and hands the main
conversation's events to conversation.py, which holds a run of the skill. A check that can't run
stops the call it's about, and says why and who must fix it, as the architecture's principle "A
call that the guard can't check stops" says.
"""

from __future__ import annotations

from typing import Any, NamedTuple

import called
import command
import conversation
import laid
import lanes
import plugin
import routes
import step
from exchange import CLAUDE_CODE, LAY_AGAIN, Answer, Event, Fault

# What the record keeps of a call's input: what the lanes read of it, and not what it writes.
KEPT = ("file_path", "notebook_path", "path", "command", "offset", "limit")
# What a role hears as it starts a role of the plugin, which only the main conversation starts.
NO_START = (
    "Start no subagent of this plugin: only the main conversation starts one, with what the plugin"
    " gives it. Reply with what you would pass on, and end."
)


class _Held(NamedTuple):
    """A role that the guard holds, with what its checks read."""

    plugin: str
    root: str
    project: str | None
    laid: laid.Laid
    name: str
    part: step.Part
    record: called.Record


def answer(name: str, root: str, project: str | None, event: Event) -> Answer:
    """The guard's answer to the event of the plugin of the name, which lies at the root, in the
    project at the folder given, or None where Claude Code gave no project folder."""
    if event.agent_type is None:
        return conversation.answer(name, root, event)
    if not event.agent_type.startswith(name + ":"):
        return Answer()
    role = event.agent_type[len(name) + 1 :]
    try:
        held = _held(name, root, project, role, event.session)
        if held is None:
            return Answer()
        return _ON[event.name](held, event) if event.name in _ON else Answer()
    except Fault as fault:
        where = (
            f"the lanes of {role}"
            if fault.about is None
            else f"{fault.about.lane} on step {fault.about.step} of {role}"
        )
        told = (
            f"{name}: lane cannot check {where}: {fault.what}. Ask the main conversation for"
            f" the fix: {fault.who}. Go on with the rest of your work meanwhile."
        )
        if event.name == "PreToolUse":
            return Answer(deny=told, tell=told)
        if event.name == "SubagentStop" and not event.stop_active:
            return Answer(block=told, tell=told)
        return Answer(tell=told)


def _held(name: str, root: str, project: str | None, role: str, session: str) -> _Held | None:
    """The role as the guard holds it, or None where it has no lanes and the routes don't name it.

    It raises Fault where the guard can't read the lanes laid, the role's entry, or its part.
    """
    lay_again = LAY_AGAIN.format(plugin=name)
    try:
        found = laid.read(root)
        named = routes.named(found.routes) if found.routes is not None else []
        if found.role(role) is None and role not in named:
            return None
        entry = plugin.subagent(root, role)
        part = step.part(root, entry)
    except (laid.Unlaid, plugin.Fault) as why:
        raise Fault(str(why), lay_again) from None
    if not entry.background:
        raise Fault(
            f"{entry.path} no longer sets `background: true`",
            f"the maker of {name} must set `background: true` in {entry.path}",
        )
    _check_steps(found, role, part, lay_again)
    return _Held(name, root, project, found, role, part, called.record(session, name))


def _check_steps(found: laid.Laid, role: str, part: step.Part, lay_again: str) -> None:
    """Checks that each step that the lanes and routes lay a sentence in still says it.

    It raises Fault where the part no longer holds such a step, or where the step no longer says
    the sentence.
    """
    steps = {s.number: s for s in part.steps}
    for said in laid.sentences(found, role, part.steps):
        if said.step is None:
            continue
        sentence = lanes.sentence(said.lane, said.takes)
        if said.step not in steps:
            raise Fault(f"the steps hold no step {said.step}", lay_again, said)
        if sentence not in steps[said.step].says:
            raise Fault(f'step {said.step} no longer says "{sentence}"', lay_again, said)


def _start(held: _Held, event: Event) -> Answer:
    """The answer to the start of the role: its part, where it's a file of its own, and each
    sentence that no step says, as context that Claude Code adds as the role starts."""
    told = [
        lanes.sentence(s.lane, s.takes)
        for s in laid.sentences(held.laid, held.name, held.part.steps)
        if s.step is None
    ]
    given = []
    if held.part.own:
        given.append(held.part.text.replace(command.ROOT, held.root).rstrip("\n"))
    given += [f"{held.plugin}: {s}" for s in told]
    return Answer(context="\n\n".join(given)) if given else Answer()


def _call(held: _Held, event: Event) -> Answer:
    """The answer to a tool call of the role: a deny with the sentence that the call breaks, or
    nothing."""
    if held.project is None:
        raise Fault(
            "Claude Code gave the hook no CLAUDE_PROJECT_DIR",
            f"whoever runs {held.plugin} must run it in a Claude Code that gives each hook"
            " CLAUDE_PROJECT_DIR",
        )
    if _starts_one(held, event):
        return Answer(deny=f"{held.plugin}: {NO_START}")
    results = routes.result_commands(held.laid, held.name)
    run = event.tool_input.get("command") if event.tool == "Bash" else None
    if isinstance(run, str) and _result_of(held, run) is not None:
        expanded = [c.replace(command.ROOT, held.root) for c in results]
        if _result_of(held, run) in routes.allowed(held.laid, held.name):
            role = held.laid.role(held.name)
            found = role.lanes if role else ()
            given = {lane: _given(held, held.project, lane) for lane in found}
            return _ending(held, event, given, _context(held, given))
        joined = " and ".join(f"`{c}`" for c in expanded)
        return Answer(
            deny=f"{held.plugin}: {lanes.sentence('end_by', results)}\nThe commands you may end"
            f" by: {joined}."
        )
    role = held.laid.role(held.name)
    found = role.lanes if role else ()
    call = lanes.Call(event.tool or "", event.tool_input, event.cwd)
    given = {lane: _given(held, held.project, lane) for lane in found}
    context = _context(held, given)
    for lane in found:
        kind = lanes.TYPES[lane.lane]
        if given[lane] is None or not hasattr(kind, "check"):
            continue
        line = _checked(held, lane, kind.check, call, given[lane], context)
        if line:
            return Answer(deny=f"{held.plugin}: {_sentence(lane)}\n{line}")
    kept = _kept(held, event.agent_id)
    due = _due(held, given, kept)
    if due is not None and any(
        lanes.TYPES[lane.lane].traced(call, given[lane])
        for lane in found
        if lanes.traced(lane.lane) and given[lane] is not None and lane.step > due[0]
    ):
        return Answer(deny=f"{held.plugin}: {due[1]}\n{due[2]}")
    for lane in found:
        if (
            lane.lane == "hold"
            and given[lane] is not None
            and lanes.TYPES["hold"].held(call, given[lane])
        ):
            return Answer(ask=f"{held.plugin}: {_sentence(lane)}")
    return Answer()


def _sentence(lane: laid.Lane) -> str:
    return lanes.sentence(lane.lane, list(lane.takes))


def _checked(held: _Held, lane: laid.Lane, check: Any, *given: Any) -> Any:
    """What the lane's check gives, called with what's given.

    It raises Fault where the check can't run: about the role where the hook input is out of its
    documented form, and about the lane where what the lane takes is wrong.
    """
    try:
        return check(*given)
    except lanes.Malformed as why:
        raise Fault(str(why), CLAUDE_CODE) from None
    except lanes.Unchecked as why:
        said = laid.Said(lane.step, lane.lane, list(lane.takes))
        raise Fault(str(why), LAY_AGAIN.format(plugin=held.plugin), said) from None


def _kept(held: _Held, agent: str | None) -> list[lanes.Call]:
    """Each call of the agent that came back, in its order."""
    return [
        lanes.Call(e["tool"], e["input"], e["cwd"])
        for e in held.record.entries()
        if e["kind"] == "call" and e.get("agent") == agent
    ]


def _due(
    held: _Held, given: dict[laid.Lane, dict[str, list[str]] | None], kept: list[lanes.Call]
) -> tuple[int, str, str] | None:
    """The first step whose traces haven't all come back, with what the step says and what's
    missing of its traces, or None where every trace came back."""
    role = held.laid.role(held.name)
    traces = [
        l for l in (role.lanes if role else ()) if lanes.traced(l.lane) and given[l] is not None
    ]
    says = {s.number: s.says for s in held.part.steps}
    for number in sorted({l.step for l in traces}):
        for lane in [l for l in traces if l.step == number]:
            missing = lanes.TYPES[lane.lane].done(given[lane], kept)
            if missing:
                return number, says.get(number, _sentence(lane)), missing
    return None


def _ending(
    held: _Held,
    event: Event,
    given: dict[laid.Lane, dict[str, list[str]] | None],
    context: lanes.Context,
) -> Answer:
    """The answer to the role's run of the result script with a result it may give: a deny where a
    step's trace hasn't come back or a lane checked at the end isn't kept, or nothing."""
    kept = _kept(held, event.agent_id)
    due = _due(held, given, kept)
    if due is not None:
        return Answer(deny=f"{held.plugin}: {due[1]}\n{due[2]}")
    role = held.laid.role(held.name)
    told = []
    for lane in role.lanes if role else ():
        kind = lanes.TYPES[lane.lane]
        if given[lane] is None or not hasattr(kind, "end"):
            continue
        missing = _checked(held, lane, kind.end, given[lane], kept, context)
        if missing:
            told.append(f"{held.plugin}: {_sentence(lane)}\n{missing}")
    return Answer(deny="\n".join(told)) if told else Answer()


def _starts_one(held: _Held, event: Event) -> bool:
    """Whether the call starts a role of the plugin that the guard holds, or a role or a skill of
    a dependency that the routes name."""
    named = routes.named(held.laid.routes) if held.laid.routes is not None else []
    names = [r.name for r in held.laid.roles] + named
    started = {routes.typed(held.plugin, n) for n in names}
    if event.tool == "Agent":
        return event.tool_input.get("subagent_type") in started
    return event.tool == "Skill" and event.tool_input.get("skill") in started


def _result_of(held: _Held, run: str) -> str | None:
    """The result that the command gives, where it runs this plugin's result script for the role
    with one word after it, or None."""
    script = f"python3 {held.root}/hooks/lane/result.py {held.name} "
    word = run.strip()[len(script) :] if run.strip().startswith(script) else ""
    return word if word and " " not in word else None


def _came_back(held: _Held, event: Event) -> Answer:
    """Keeps the call of the role that came back, and its result where it ran the result script."""
    kept = {k: v for k, v in event.tool_input.items() if k in KEPT}
    if event.tool == "Read":
        kept["lines"] = _lines(lanes.Call("Read", event.tool_input, event.cwd))
    held.record.add(
        {
            "kind": "call",
            "agent": event.agent_id,
            "tool": event.tool,
            "input": kept,
            "cwd": event.cwd,
        }
    )
    run = event.tool_input.get("command") if event.tool == "Bash" else None
    given = _result_of(held, run) if isinstance(run, str) else None
    if given is not None and given in routes.allowed(held.laid, held.name):
        held.record.add(
            {"kind": "result", "agent": event.agent_id, "role": held.name, "result": given}
        )
    return Answer()


def _ends(held: _Held, event: Event) -> Answer:
    """Keeps the role going once where it ends with no result that it gives, and keeps its end
    otherwise."""
    results = routes.result_commands(held.laid, held.name)
    if results and not _gave(held.record.entries(), event.agent_id) and not event.stop_active:
        return Answer(block=f"{held.plugin}: {lanes.sentence('end_by', results)}")
    held.record.add({"kind": "ended", "agent": event.agent_id})
    return Answer()


def _lines(call: lanes.Call) -> int | None:
    """The lines of the file that the Read call read, as it stood then, or None where it's gone."""
    try:
        with open(lanes.called_path(call) or "", encoding="utf-8", errors="replace") as f:
            return len(f.read().splitlines())
    except OSError:
        return None


def _gave(entries: list[dict[str, Any]], agent: str | None) -> bool:
    """Whether the agent gave a result since it started or a message resumed it."""
    gave = False
    for entry in entries:
        if entry.get("agent") != agent:
            continue
        if entry["kind"] == "message":
            gave = False
        elif entry["kind"] == "result":
            gave = True
    return gave


# What the guard does on each event of a role it holds.
_ON = {
    "PreToolUse": _call,
    "PostToolUse": _came_back,
    "SubagentStart": _start,
    "SubagentStop": _ends,
}


def _given(held: _Held, project: str, lane: laid.Lane) -> dict[str, list[str]] | None:
    """What the lane takes on this call, as lanes.given puts it."""
    try:
        return lanes.given(lane.lane, list(lane.takes), {}, held.root, project)
    except lanes.Unchecked as why:
        said = laid.Said(lane.step, lane.lane, list(lane.takes))
        raise Fault(str(why), LAY_AGAIN.format(plugin=held.plugin), said) from None


def _context(held: _Held, given: dict[laid.Lane, dict[str, list[str]] | None]) -> lanes.Context:
    """What the role's lanes allow beside each lane's own takes: each command that any of its
    lanes names, its result commands, and the forms of its in_form lanes and its own part to
    read."""
    commands: list[str] = []
    for lane, places in given.items():
        where = lanes.commands_place(lane.lane)
        if where and places is not None:
            commands += places[where]
    results = routes.result_commands(held.laid, held.name)
    commands += [c.replace(command.ROOT, held.root) for c in results]
    forms = [
        f
        for lane, places in given.items()
        if lane.lane == "in_form" and places
        for f in places["form"]
    ]
    return lanes.Context(tuple(dict.fromkeys(commands)), (*forms, held.part.path))
