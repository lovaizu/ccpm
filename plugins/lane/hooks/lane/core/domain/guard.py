"""The guard: decides, of a tool call of a subagent with lanes laid, whether it goes through or
which sentences stop it, from the call's input alone, as Claude Code documents it; and, where it
cannot decide, the error that says what is wrong and who must fix it.

A subagent with lanes runs a command only where a lane names it, whole: a call of Bash is judged by
the run lanes of the subagent together, as lane does not know which step the subagent is on. A
write is judged by its write lanes together, and goes through where it has none. Any other tool
goes through."""

from __future__ import annotations

from typing import Any, NamedTuple

import lanes
import rules
import schema
import step
from lanes import run_only

# Each tool a lane judges, with the action its call is and the field of its input the lane judges.
WATCHED = {
    "Bash": ("run", "command"),
    "Write": ("write", "file_path"),
    "Edit": ("write", "file_path"),
    "NotebookEdit": ("write", "notebook_path"),
}
# What a subagent is told, after its run lanes' sentences, of the commands it may run.
MAY_RUN = "The commands you may run, each word for word: {listed}."
RUN_NONE = "You may run no command."
# What a subagent is told to do where lane cannot check a lane, given who must fix it: a role asks
# the main conversation for what lies outside its work and goes on with the rest, as
# dev/architecture.md's Asking for what lies outside the work says.
ASK = "Ask the main conversation for the fix: {fix}. Go on with the rest of your work meanwhile."
LAY_AGAIN = (
    "the maker of {plugin} must lay its lanes again with `lay.py write`, so they match its steps"
)
CLAUDE_CODE = (
    "Claude Code must be updated with `claude update`, and where this goes on, it must be reported"
    " at https://github.com/lovaizu/ccpm/issues"
)


class Said(NamedTuple):
    """What the guard says of a call: a break, told the subagent; or an error, told the subagent
    and the user alike, as only the user can have it fixed."""

    text: str
    error: bool = False


def cannot(on: str, wrong: str, fix: str) -> Said:
    """The error where lane cannot check what `on` names, such as `the lanes of <subagent>` or
    `<lane> on step <n> of <subagent>`, in the form docs/lanes.md gives."""
    return Said(f"lane cannot check {on}: {wrong}. {ASK.format(fix=fix)}", True)


def unshaped(name: str, wrong: str) -> Said:
    """The error where the event of the subagent of the name is not as Claude Code hands it, by the
    point given, which Claude Code must fix."""
    said = f"the hook was handed no event as Claude Code hands it, {wrong}"
    return cannot(f"the lanes of {name}", said, CLAUDE_CODE)


def check(root: str, plugin: str, name: str, event: dict[str, Any], wrong: str) -> list[Said]:
    """What the guard says of the PreToolUse event of the subagent of the name, of the plugin at
    root of the name given: nothing where no lane is laid in the subagent or its call goes through;
    a break where a lane stops it; an error where the plugin's hooks/lanes.json cannot be read,
    the event is not as Claude Code hands it, as `wrong` says or its tool's field shows, or a step
    no longer says the sentence of a lane that judges the call."""
    try:
        laid = rules.of(rules.read(root), name)
    except ValueError as why:
        return [cannot(f"the lanes of {name}", str(why), LAY_AGAIN.format(plugin=plugin))]
    if laid is None:
        return []
    if wrong:
        return [unshaped(name, wrong)]
    tool, given = event["tool_name"], event["tool_input"]
    if tool not in WATCHED:
        return []
    action, field = WATCHED[tool]
    out = schema.held({"type": "string"}, given.get(field))
    if out is not None:
        return [unshaped(name, f"$.tool_input.{field}{out.told()[1:]}")]
    judging = [g for g in laid if lanes.LANES[g.lane].ACTION == action]
    writing = action == "write"  # pragma: no mutate
    if writing and not judging:
        return []
    for g in judging:
        said = lanes.sentence(g.lane, g.takes)
        if not step.holds(root, name, g.step, said):
            on = f"{g.lane} on step {g.step} of {name}"
            gone = f"step {g.step} no longer says: {said}".rstrip(".")
            return [cannot(on, gone, LAY_AGAIN.format(plugin=plugin))]
    value = given[field]
    if any(lanes.LANES[g.lane].allows(value, g.takes, root, event["cwd"]) for g in judging):
        return []
    told = [lanes.sentence(g.lane, g.takes) for g in judging]
    if not writing:
        commands = [c for g in judging for c in run_only.named(g.takes, root)]
        listed = ", ".join(f"`{c}`" for c in dict.fromkeys(commands))
        told.append(MAY_RUN.format(listed=listed) if commands else RUN_NONE)
    return [Said("\n".join(told))]
