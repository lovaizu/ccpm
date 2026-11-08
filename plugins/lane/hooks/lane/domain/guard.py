"""Decides which checks run on a hook event, and what the role, the main conversation, and whoever
runs the plugin hear from them.

The guard holds each role of the plugin that has lanes or that the routes name, and hands the main
conversation's events to conversation.py, which holds a run of the skill. A check that can't run
stops the call it's about, and says why and who must fix it, as the architecture's principle "A
call that the guard can't check stops" says.
"""

from __future__ import annotations

import time
from typing import Any, NamedTuple

import called
import command
import conversation
import laid
import lanes
import plugin
import ports
import routes
import step
from exchange import CLAUDE_CODE, LAY_AGAIN, Answer, Event, Fault

# What the record keeps of a call's input: what the lanes read of it, and not what it writes.
KEPT = ("file_path", "notebook_path", "path", "command", "offset", "limit")
# The most seconds that a role's call waits for the Agent call that started the role to come back,
# as the role starts a moment before.
WAIT = 3.0
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
        return _dependency(name, root, event)
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
    """The answer to the start of the role, as context that Claude Code adds as the role starts:
    its part, where it's a file of its own, each sentence that no step says, and each step list
    that its steps adapter gives, where the Agent call that started it came back already."""
    told = [
        lanes.sentence(s.lane, s.takes)
        for s in laid.sentences(held.laid, held.name, held.part.steps)
        if s.step is None
    ]
    given = []
    if held.part.own:
        given.append(held.part.text.replace(command.ROOT, held.root).rstrip("\n"))
    given += [f"{held.plugin}: {s}" for s in told]
    role = held.laid.role(held.name)
    values = _values(held, event.agent_id, wait=False)
    if role is not None and role.steps_adapter and values is not None:
        for each in _adapted(held, role.steps_adapter, values):
            numbered = [f"{n}. {s.says}" for n, s in enumerate(each.steps, 1)]
            given.append(
                f"{held.plugin}: The steps of {each.name}, in their order:\n" + "\n".join(numbered)
            )
    return Answer(context="\n\n".join(given)) if given else Answer()


class _Step(NamedTuple):
    """A step of a step list: what it says, and the type and takes of each lane of its trace."""

    says: str
    traces: tuple[tuple[str, dict[str, list[str]]], ...]


class _List(NamedTuple):
    """A step list: the numbered list of the role's part, or a list that its steps adapter gives."""

    name: str
    steps: tuple[_Step, ...]


class _Checks(NamedTuple):
    """What the checks of one call of the role read: what each lane takes, the step lists, what
    the lanes allow beside their own takes, and the calls kept of the start."""

    given: dict[laid.Lane, dict[str, list[str]] | None]
    lists: list[_List]
    context: lanes.Context
    kept: list[lanes.Call]


def _call(held: _Held, event: Event) -> Answer:
    """The answer to a tool call of the role: a deny with the sentence that the call breaks, an
    ask with the sentence of a command held for the person, or nothing."""
    if held.project is None:
        raise Fault(
            "Claude Code gave the hook no CLAUDE_PROJECT_DIR",
            f"whoever runs {held.plugin} must run it in a Claude Code that gives each hook"
            " CLAUDE_PROJECT_DIR",
        )
    if _starts_one(held.plugin, held.laid, event):
        return Answer(deny=f"{held.plugin}: {NO_START}")
    run = event.tool_input.get("command") if event.tool == "Bash" else None
    if isinstance(run, str) and _result_of(held, run) is not None:
        results = routes.result_commands(held.laid, held.name)
        if _result_of(held, run) in routes.allowed(held.laid, held.name):
            return _ending(held, _checks(held, event, held.project))
        joined = " and ".join(f"`{c.replace(command.ROOT, held.root)}`" for c in results)
        return Answer(
            deny=f"{held.plugin}: {lanes.sentence('end_by', results)}\nThe commands you may end"
            f" by: {joined}."
        )
    checks = _checks(held, event, held.project)
    call = lanes.Call(event.tool or "", event.tool_input, event.cwd)
    for lane, given in checks.given.items():
        kind = lanes.TYPES[lane.lane]
        if given is None or not hasattr(kind, "check"):
            continue
        line = _checked(held, lane, kind.check, call, given, checks.context)
        if line:
            return Answer(deny=f"{held.plugin}: {_sentence(lane)}\n{line}")
    for each in checks.lists:
        due = _due(each, checks.kept)
        if due is None:
            continue
        later = each.steps[due[0] + 1 :]
        if any(lanes.TYPES[t].traced(call, g) for s in later for t, g in s.traces):
            return Answer(deny=f"{held.plugin}: {due[1]}\n{due[2]}")
    for lane, given in checks.given.items():
        if lane.lane == "hold" and given is not None and lanes.TYPES["hold"].held(call, given):
            return Answer(ask=f"{held.plugin}: {_sentence(lane)}")
    return Answer()


def _checks(held: _Held, event: Event, project: str) -> _Checks:
    """What the checks of the call read, the start's values among them where a lane or an adapter
    needs them."""
    role = held.laid.role(held.name)
    found = role.lanes if role else ()
    values: dict[str, Any] = {}
    if role is not None and (
        role.adapter or role.steps_adapter or any(command.values(t) for l in found for t in l.takes)
    ):
        values = _values(held, event.agent_id, wait=True) or {}
    given = {lane: _given(held, project, lane, values) for lane in found}
    lists = [_laid_list(held, found, given)]
    if role is not None and role.steps_adapter:
        lists += _adapted(held, role.steps_adapter, values)
    return _Checks(given, lists, _context(held, given, lists, values), _kept(held, event.agent_id))


def _values(held: _Held, agent: str | None, wait: bool) -> dict[str, Any] | None:
    """The values of the start of the agent, read at the values port from the texts that the start
    holds. A role starts a moment before its Agent call comes back, so where wait holds, this
    waits a few seconds for the call. It gives None where the call hasn't come back.

    It raises Fault where the call doesn't come back in time, or the values adapter fails.
    """
    deadline = time.monotonic() + WAIT
    texts = called.texts(held.record.entries(), agent or "")
    while texts is None and wait and time.monotonic() < deadline:
        time.sleep(0.05)
        texts = called.texts(held.record.entries(), agent or "")
    if texts is None:
        if not wait:
            return None
        raise Fault(
            f"the Agent call that started {held.name} didn't come back within {WAIT} seconds",
            f"the main conversation must start {held.name} again",
        )
    role = held.laid.role(held.name)
    adapter = role.adapter if role else None
    try:
        return ports.values(texts, held.root, adapter)
    except ports.Unported as why:
        raise Fault(str(why), f"the maker of {held.plugin} must fix {adapter}") from None


def _laid_list(
    held: _Held, found: tuple[laid.Lane, ...], given: dict[laid.Lane, dict[str, list[str]] | None]
) -> _List:
    """The step list of the role's lanes of the trace kind, by their steps' numbers."""
    says = {s.number: s.says for s in held.part.steps}
    traces = [l for l in found if lanes.traced(l.lane) and given[l] is not None]
    steps = []
    for number in sorted({l.step for l in traces}):
        on = [l for l in traces if l.step == number]
        text = says.get(number, " ".join(_sentence(l) for l in on))
        steps.append(_Step(text, tuple((l.lane, given[l] or {}) for l in on)))
    return _List("steps", tuple(steps))


def _adapted(held: _Held, adapter: str, values: dict[str, Any]) -> list[_List]:
    """The step lists that the role's steps adapter gives for the start's values, each step saying
    the sentence of each lane of its trace too.

    It raises Fault where the adapter fails or gives a lane that can't stand.
    """
    who = f"the maker of {held.plugin} must fix {adapter}"
    try:
        given = ports.steps(values, held.root, adapter)
    except ports.Unported as why:
        raise Fault(str(why), who) from None
    found = []
    for each in given:
        steps = []
        for item in each["steps"]:
            traces = []
            said = [item["says"]]
            for lane in item["lanes"]:
                faults = lanes.stands(lane["lane"], lane["takes"])
                if faults:
                    raise Fault(f"{adapter} gives a lane that can't stand: {faults[0]}", who)
                said.append(lanes.sentence(lane["lane"], lane["takes"]))
                try:
                    takes = lanes.given(
                        lane["lane"], lane["takes"], values, held.root, held.project or ""
                    )
                except lanes.Unchecked as why:
                    raise Fault(str(why), who) from None
                if takes is not None:
                    traces.append((lane["lane"], takes))
            steps.append(_Step(" ".join(said), tuple(traces)))
        found.append(_List(each["list"], tuple(steps)))
    return found


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


def _due(each: _List, kept: list[lanes.Call]) -> tuple[int, str, str] | None:
    """The index of the first step of the list whose traces haven't all come back, with what the
    step says and what's missing of its traces, or None where every trace came back."""
    for index, item in enumerate(each.steps):
        for lane, given in item.traces:
            missing = lanes.TYPES[lane].done(given, kept)
            if missing:
                return index, item.says, missing
    return None


def _ending(held: _Held, checks: _Checks) -> Answer:
    """The answer to the role's run of the result script with a result it may give: a deny where a
    step's trace hasn't come back or a lane checked at the end isn't kept, or nothing."""
    for each in checks.lists:
        due = _due(each, checks.kept)
        if due is not None:
            return Answer(deny=f"{held.plugin}: {due[1]}\n{due[2]}")
    told = []
    for lane, given in checks.given.items():
        kind = lanes.TYPES[lane.lane]
        if given is None or not hasattr(kind, "end"):
            continue
        context = checks.context
        if lane.adapter is not None:
            context = context._replace(items=_items(held, lane.adapter, dict(context.values)))
        missing = _checked(held, lane, kind.end, given, checks.kept, context)
        if missing:
            told.append(f"{held.plugin}: {_sentence(lane)}\n{missing}")
    return Answer(deny="\n".join(told)) if told else Answer()


def _items(held: _Held, adapter: str, values: dict[str, Any]) -> Any:
    """What reads the items of an input through the adapter, for every_item."""

    def read(path: str, text: str) -> list[str]:
        try:
            return ports.items(path, text, values, held.root, adapter)
        except ports.Unported as why:
            raise lanes.Unchecked(str(why)) from None

    return read


def _dependency(name: str, root: str, event: Event) -> Answer:
    """The answer to an event of a dependency's role that the routes name. Its start of a role of
    the plugin stops, the guard keeps its result by the dependency's result script, and it goes on
    once where it would end with no result. The dependency's own guard holds its other calls."""
    try:
        found = laid.read(root)
    except laid.Unlaid:
        return Answer()
    role = event.agent_type or ""
    if found.routes is None or role not in routes.named(found.routes):
        return Answer()
    record = called.record(event.session, name)
    written = _dependency_results(found, role)
    if event.name == "PreToolUse" and _starts_one(name, found, event):
        return Answer(deny=f"{name}: {NO_START}")
    run = event.tool_input.get("command") if event.tool == "Bash" else None
    if event.name == "PostToolUse" and isinstance(run, str):
        for result, written_command in written.items():
            if command.matches(run, written_command):
                record.add(
                    {"kind": "result", "agent": event.agent_id, "role": role, "result": result}
                )
    if event.name != "SubagentStop":
        return Answer()
    if not _gave(record.entries(), event.agent_id) and not event.stop_active:
        dependency = role.split(":")[0]
        return Answer(
            block=f"{name}: {lanes.sentence('end_by', list(written.values()))}\n"
            f"`${{dependency:{dependency}}}` stands for the folder that holds the plugin"
            f" {dependency}."
        )
    record.add({"kind": "ended", "agent": event.agent_id})
    return Answer()


def _dependency_results(found: laid.Laid, role: str) -> dict[str, str]:
    """The command by which the dependency's role or skill gives each result of a route from it, by
    the result. Each runs the result script of the dependency, in the dependency's folder."""
    dependency, _, short = role.partition(":")
    given = routes.results(found.routes, role) if found.routes is not None else None
    script = f"python3 ${{dependency:{dependency}}}/hooks/lane/result.py {short}"
    return {r: f"{script} {r}" for r in given or []}


def _starts_one(name: str, found: laid.Laid, event: Event) -> bool:
    """Whether the call starts a role of the plugin that the guard holds, or a role or a skill of
    a dependency that the routes name."""
    named = routes.named(found.routes) if found.routes is not None else []
    started = {routes.typed(name, n) for n in [r.name for r in found.roles] + named}
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


def _given(
    held: _Held, project: str, lane: laid.Lane, values: dict[str, Any]
) -> dict[str, list[str]] | None:
    """What the lane takes on this call, as lanes.given puts it."""
    try:
        return lanes.given(lane.lane, list(lane.takes), values, held.root, project)
    except lanes.Unchecked as why:
        said = laid.Said(lane.step, lane.lane, list(lane.takes))
        raise Fault(str(why), LAY_AGAIN.format(plugin=held.plugin), said) from None


def _context(
    held: _Held,
    given: dict[laid.Lane, dict[str, list[str]] | None],
    lists: list[_List],
    values: dict[str, Any],
) -> lanes.Context:
    """What the role's lanes allow beside each lane's own takes: each command that any of its
    lanes or its step lists names, its result commands, and the forms of its in_form lanes and its
    own part to read."""
    commands: list[str] = []
    for lane, places in given.items():
        where = lanes.commands_place(lane.lane)
        if where and places is not None:
            commands += places[where]
    commands += [
        c for each in lists for s in each.steps for t, g in s.traces for c in g.get("commands", [])
    ]
    results = routes.result_commands(held.laid, held.name)
    commands += [c.replace(command.ROOT, held.root) for c in results]
    forms = [
        f
        for lane, places in given.items()
        if lane.lane == "in_form" and places
        for f in places["form"]
    ]
    return lanes.Context(tuple(dict.fromkeys(commands)), (*forms, held.part.path), values)
