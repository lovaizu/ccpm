"""Decides what the main conversation hears within a run of the skill that the routes name, and
which of its moves stop, as the architecture's principle "The guard holds the main conversation
only while its run lasts" says.

A run begins as the skill's command expands or as the Skill call of the skill comes back. Within
the run, the guard checks only the starts of roles, the messages that resume one, a dialog while a
role's point waits, and the end of a turn. It reads the other events only to tell the next start
or to keep the person's words.
"""

from __future__ import annotations

from typing import Any

import called
import command
import exchange
import laid
import lanes
import plugin
import routes
import step

# The first line of the message that resumes a role with the person's answer.
ANSWER = "The person's answer, word for word:"
# How a prompt begins that brings the end of a role run in the background, as a try of Claude
# Code 2.1.319 showed it. It's no prompt of the person's.
NOTIFICATION = "<task-notification>"
# The statuses that the Agent call of a start comes back with, as Claude Code documents them.
STATUSES = ("async_launched", "completed")


class _Context:
    """What the guard reads of the plugin and the record as it answers one event."""

    def __init__(self, name: str, root: str, event: exchange.Event, found: routes.Routes) -> None:
        self.name = name
        self.root = root
        self.event = event
        self.routes = found
        self.record = called.record(event.session, name)

    def run(self) -> called.Run | None:
        return called.run(self.record.entries())

    def typed(self, role: str) -> str:
        return routes.typed(self.name, role)

    def line(self, text: str) -> str:
        return f"{self.name}: {text}"


def answer(name: str, root: str, event: exchange.Event) -> exchange.Answer:
    """The guard's answer to an event of the main conversation."""
    begun = _begun(name, event)
    record = called.record(event.session, name)
    current = called.run(record.entries())
    if begun is None and current is None:
        return exchange.Answer()
    skill = begun or (current.skill if current else "")
    try:
        found = laid.read(root)
    except laid.Unlaid as why:
        return _told(name, event, skill, None, str(why), exchange.LAY_AGAIN.format(plugin=name))
    if found.routes is None:
        return exchange.Answer()
    context = _Context(name, root, event, found.routes)
    try:
        if begun is not None:
            return _begin(context, found, begun, current)
        return _within(context, current or called.Run(skill, [], {}, []))
    except exchange.Fault as fault:
        return _told(name, event, skill, fault.about, fault.what, fault.who)


def _told(
    name: str, event: exchange.Event, skill: str, about: str | None, what: str, who: str
) -> exchange.Answer:
    """What the main conversation and whoever runs the plugin hear of a run that the guard can't
    check."""
    where = about or f"the routes of {skill}"
    told = f"{name}: lane cannot check {where}: {what}. Tell the user: {who}."
    if event.name == "PreToolUse":
        return exchange.Answer(deny=told, tell=told)
    if event.name == "Stop":
        return exchange.Answer(tell=told)
    return exchange.Answer(context=told, tell=told)


def _begun(name: str, event: exchange.Event) -> str | None:
    """The skill of the plugin that the event begins, or None. The expansion of the skill's command
    begins it, and so does the Skill call of it that comes back."""
    if event.name == "UserPromptExpansion":
        given = event.command
    elif event.name == "PostToolUse" and event.tool == "Skill":
        given = event.tool_input.get("skill")
    else:
        return None
    if isinstance(given, str) and given.startswith(name + ":"):
        return given[len(name) + 1 :]
    return None


def _begin(
    context: _Context, found: laid.Laid, skill: str, current: called.Run | None
) -> exchange.Answer:
    """Begins a run of the skill where the routes name it and no run is on but one that waits."""
    given = context.routes
    if skill != given.orchestrator:
        return exchange.Answer()
    if current is not None and routes.due(given, current.groups).kind != "waits":
        return exchange.Answer()
    lines = []
    if given.step is not None:
        _check_skill(context, found)
    else:
        lines.append(context.line(lanes.sentence("follow_routes", [])))
        results = routes.result_commands(found, skill)
        lines.append(context.line(lanes.sentence("end_by", results)))
    context.record.add({"kind": "run", "skill": skill})
    lines.append(context.line(_start_line(context, routes.due(given, []).role)))
    return exchange.Answer(context="\n".join(lines))


def _check_skill(context: _Context, found: laid.Laid) -> None:
    """Checks that the skill's step still says the routes' sentence.

    It raises `exchange.Fault` where the guard can't read the skill's part, where the part holds no
    such step, or where the step no longer says the sentence.
    """
    given = context.routes
    lay_again = exchange.LAY_AGAIN.format(plugin=context.name)
    about = f"follow_routes on step {given.step} of {given.orchestrator}"
    try:
        part = step.part(context.root, plugin.skill(context.root, given.orchestrator))
    except plugin.Fault as why:
        raise exchange.Fault(str(why), lay_again, about) from None
    said = lanes.sentence("follow_routes", [])
    steps = {s.number: s.says for s in part.steps}
    if given.step not in steps:
        raise exchange.Fault(f"the steps hold no step {given.step}", lay_again, about)
    if said not in steps[given.step]:
        raise exchange.Fault(f'step {given.step} no longer says "{said}"', lay_again, about)


def _start_line(context: _Context, role: str) -> str:
    """What the main conversation hears of the start due of the role, with the command that gives
    its text, where the routes name one and the role is the plugin's own."""
    line = f"Start `{context.typed(role)}`."
    if context.routes.command and ":" not in role:
        line += (
            f" Run `{_command(context, role)}` first, and start it with what it prints as its"
            " prompt, word for word."
        )
    return line


def _command(context: _Context, role: str) -> str:
    """The routes' command for the start of the role, as the main conversation runs it."""
    return f"{(context.routes.command or '').replace(command.ROOT, context.root)} {role}"


def _wait_line(context: _Context, role: str) -> str:
    """What the main conversation hears while starts of the role run."""
    if role in context.routes.fan_out:
        return (
            f"Wait for every run of `{context.typed(role)}` to end: you are told the next start"
            " once each has."
        )
    return f"Wait for `{context.typed(role)}` to end: you are told the next start once it has."


def _point_line(context: _Context, role: str) -> str:
    """What the main conversation hears where it would move on while a role's point waits."""
    return (
        f"Put the point of `{context.typed(role)}` to the person as it wrote it, in your reply,"
        " and end your turn: their answer comes back as their next prompt."
    )


def _due_line(context: _Context, due: routes.Due) -> str:
    """What the main conversation hears of the move due, as it stops a move that isn't."""
    if due.kind == "wait":
        return _wait_line(context, due.role)
    if due.kind == "waits":
        return _point_line(context, due.role)
    return _start_line(context, due.role)


def _gave(due: routes.Due) -> str:
    """The result that led to the move due, as the main conversation hears it."""
    if due.count > 1:
        return f"The {due.count} runs of {due.after} gave `{due.result}`."
    return f"{due.after} gave `{due.result}`."


def _next(context: _Context, current: called.Run) -> str:
    """What the main conversation hears of where the run stands. A run whose route ends ends."""
    given = context.routes
    due = routes.due(given, current.groups)
    if due.kind == "unordered":
        raise exchange.Fault(
            f"the runs of {due.role} gave results that precedence doesn't order",
            f"the maker of {context.name} must order each result of {due.role} in precedence",
        )
    if due.kind == "wait":
        return context.line(_wait_line(context, due.role))
    if due.kind == "again":
        return context.line(
            f"{due.role} ended with no result. Start `{context.typed(due.role)}` again."
        )
    if due.kind == "waits":
        return context.line(
            f"{_gave(due)} Put its point to the user as it wrote it, in your reply, and resume"
            f" `{context.typed(due.role)}` with their answer by SendMessage."
        )
    if due.kind == "end":
        context.record.add({"kind": "end"})
        return context.line(f"{_gave(due)} Start no more subagents.")
    if due.result is None:
        return context.line(_start_line(context, due.role))
    return context.line(f"{_gave(due)} {_start_line(context, due.role)}")


def _within(context: _Context, current: called.Run) -> exchange.Answer:
    """The answer to an event of the main conversation within the run."""
    event = context.event
    if event.name == "PreToolUse":
        return _move(context, current)
    if event.name == "PostToolUse":
        return _moved(context, current)
    if event.name == "UserPromptSubmit":
        return _prompted(context, current)
    if event.name == "Stop":
        return _stops(context, current)
    return exchange.Answer()


def _held_type(context: _Context, given: Any) -> str | None:
    """The role that a subagent type names, where it's the plugin's own role that the routes name
    or one of a dependency that they name, or None."""
    for role in routes.named(context.routes):
        if given == context.typed(role):
            return role
    return None


def _move(context: _Context, current: called.Run) -> exchange.Answer:
    """The answer to a tool call of the main conversation within the run."""
    event = context.event
    due = routes.due(context.routes, current.groups)
    follow = context.line(lanes.sentence("follow_routes", []))
    if event.tool == "Agent":
        role = _held_type(context, event.tool_input.get("subagent_type"))
        if role is None:
            return exchange.Answer()
        refused = _start_refused(context, current, due, role)
        return exchange.Answer(deny=f"{follow}\n{refused}") if refused else exchange.Answer()
    if event.tool == "SendMessage":
        refused = _message_refused(context, current, due)
        return exchange.Answer(deny=f"{follow}\n{refused}") if refused else exchange.Answer()
    if event.tool == "AskUserQuestion" and due.kind == "waits":
        return exchange.Answer(deny=f"{follow}\n{_point_line(context, due.role)}")
    return exchange.Answer()


def _start_refused(
    context: _Context, current: called.Run, due: routes.Due, role: str
) -> str | None:
    """Why the start of the role stops, or None where it's the start due."""
    if due.kind in ("start", "again") and due.role == role:
        if not context.routes.command or ":" in role:
            return None
        prompt = context.event.tool_input.get("prompt")
        given = current.given.get(role)
        if isinstance(prompt, str) and given is not None and prompt.strip() == given.strip():
            return None
        return (
            f"Start `{context.typed(role)}` with what `{_command(context, role)}` printed as its"
            " prompt, word for word: run it first where you haven't."
        )
    if due.kind == "wait" and due.role == role and role in context.routes.fan_out:
        return None
    return _due_line(context, due)


def _resume_line(context: _Context, role: str, words: list[str]) -> str:
    """The message by which the main conversation resumes the role with the person's words."""
    return (
        f"Resume `{context.typed(role)}` by SendMessage with this message, word for word:\n"
        f"{ANSWER}\n" + "\n\n".join(words)
    )


def _message_refused(context: _Context, current: called.Run, due: routes.Due) -> str | None:
    """Why the SendMessage call stops, or None where it resumes the role whose point waits with
    the person's words alone. A message to a start outside the run goes on."""
    to = context.event.tool_input.get("to")
    starts = [s for g in current.groups for s in g.starts if s.agent is not None]
    if not any(s.agent == to for s in starts):
        return None
    if due.kind != "waits" or due.agent != to:
        return _due_line(context, due)
    if not current.words:
        return _point_line(context, due.role)
    expected = f"{ANSWER}\n" + "\n\n".join(current.words)
    message = context.event.tool_input.get("message")
    if isinstance(message, str) and message.strip() == expected.strip():
        return None
    return _resume_line(context, due.role, current.words)


def _moved(context: _Context, current: called.Run) -> exchange.Answer:
    """Keeps a move of the main conversation that came back: a start, a message to a start, or
    the text that the routes' command printed."""
    event = context.event
    if event.tool == "Agent":
        role = _held_type(context, event.tool_input.get("subagent_type"))
        if role is None:
            return exchange.Answer()
        back = event.tool_response if isinstance(event.tool_response, dict) else {}
        status, agent = back.get("status"), back.get("agentId")
        if status not in STATUSES or not isinstance(agent, str):
            raise exchange.Fault(
                f"the Agent call came back with the status `{status}`, where Claude Code"
                " documents async_launched or completed",
                exchange.CLAUDE_CODE,
            )
        prompt = event.tool_input.get("prompt", "")
        context.record.add(
            {"kind": "start", "agent": agent, "role": role, "prompt": prompt, "status": status}
        )
        return exchange.Answer(context=_next(context, context.run() or current))
    if event.tool == "SendMessage":
        to, text = event.tool_input.get("to"), event.tool_input.get("message", "")
        if any(s.agent == to for g in current.groups for s in g.starts):
            context.record.add({"kind": "message", "agent": to, "text": text})
        return exchange.Answer()
    if event.tool == "Bash" and context.routes.command:
        return _ran(context)
    return exchange.Answer()


def _ran(context: _Context) -> exchange.Answer:
    """Keeps what the routes' command printed, where the Bash call ran it for a role."""
    run = context.event.tool_input.get("command")
    for role in routes.named(context.routes):
        if (
            ":" in role
            or not isinstance(run, str)
            or not command.matches(run, _command(context, role))
        ):
            continue
        back = context.event.tool_response
        if not isinstance(back, dict) or not isinstance(back.get("stdout"), str):
            raise exchange.Fault("the Bash call came back with no stdout", exchange.CLAUDE_CODE)
        context.record.add({"kind": "given", "role": role, "text": back["stdout"]})
    return exchange.Answer()


def _prompted(context: _Context, current: called.Run) -> exchange.Answer:
    """The answer to a prompt that reaches the main conversation: the person's words to resume a
    role with while its point waits, or where the run stands."""
    due = routes.due(context.routes, current.groups)
    prompt = context.event.prompt or ""
    if due.kind == "waits" and not prompt.startswith(NOTIFICATION):
        if prompt.strip().split(" ")[0] == f"/{context.name}:{context.routes.orchestrator}":
            return exchange.Answer()
        context.record.add({"kind": "words", "text": prompt})
        return exchange.Answer(
            context=context.line(_resume_line(context, due.role, [*current.words, prompt]))
        )
    return exchange.Answer(context=_next(context, current))


def _stops(context: _Context, current: called.Run) -> exchange.Answer:
    """The answer to the end of the main conversation's turn: it goes on once while a start is due
    and no start of the run still runs, and the run ends where it would end again."""
    due = routes.due(context.routes, current.groups)
    if due.kind in ("waits", "wait"):
        return exchange.Answer()
    if not context.event.stop_active:
        follow = lanes.sentence("follow_routes", [])
        return exchange.Answer(block=context.line(f"{follow}\n{_due_line(context, due)}"))
    context.record.add({"kind": "end"})
    left = (
        f"lane let the run of {context.routes.orchestrator} end with"
        f" `{context.typed(due.role)}` still due"
    )
    if due.kind == "again":
        part = step.part(context.root, plugin.subagent(context.root, due.role))
        last = part.steps[-1].number if part.steps else 1
        return exchange.Answer(
            tell=context.line(
                f"{left}, as {due.role} ended with no result: the maker of {context.name} must fix"
                f" step {last} of {due.role} in {part.path}, which gives its result."
            )
        )
    skill = step.part(context.root, plugin.skill(context.root, context.routes.orchestrator))
    return exchange.Answer(
        tell=context.line(
            f"{left}: the maker of {context.name} must fix step {context.routes.step} of"
            f" {context.routes.orchestrator} in {skill.path}, which starts it."
        )
    )
