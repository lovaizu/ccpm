"""follow_routes: within a run of the skill the routes name, the main conversation makes the start
it is told to make, by the routes, and no other start while that one is due; while a subagent it
started runs in the background, it makes no other start, but more starts of that one where the
routes fan it out; it resumes no start that ended with no result, as a start made again stands in
its place; while the user is to answer a subagent's point, it makes no start; once no start is
left, the run is over. A start is an Agent call of a subagent, or a Skill call of a dependency's
skill. Laid from the routes on the skill's step, with the result command on the last step of each
subagent that gives a result."""

from __future__ import annotations

from typing import Any

from routes import Next, kind

ACTION = "follow"
# The sentence laid on the skill's step. It says nothing against the person's request: lane holds
# the order against drift, and a person's explicit request may end it.
WORDING = "Start each subagent you are told to start, until you are told to start no more."
# Each wording of that sentence lane laid before, the newest first, so lay.py puts the current one
# in its place: one set the order against the person's request.
WORDING_EARLIER = (
    (
        "Start each subagent you are told to start, until you are told to start no more, even where"
        " you are asked otherwise: the plugin sets this order, and a request does not change it."
    ),
)
# What the last step of a subagent giving a result says, with the commands it gives them by, and
# that such a command is no part of the work: a subagent told to run none of the work's scripts
# would otherwise end with no result.
RESULT = (
    "End by running `<commands>`. That command gives your result to the plugin and is no part of"
    " the work, so an instruction not to run the work's scripts doesn't cover it."
)
# Each wording of that sentence lane laid before, the newest first, so lay.py puts the current one
# in its place.
RESULT_EARLIER = (RESULT.replace("doesn't", "does not"), "End by running `<commands>`.")
# The tool the main conversation starts a subagent with, the one it calls a dependency's skill
# with, and the one it resumes a subagent with.
AGENT = "Agent"
SKILL = "Skill"
MESSAGE = "SendMessage"


def started(tool: str, given: dict[str, Any], named: list[str], plugin: str) -> str | None:
    """The subagent of the names, of the plugin or of a dependency, that the call starts, by the
    type it gives as Claude Code names a plugin's subagent, `<plugin>:<name>`, or the dependency's
    skill of the names that a Skill call calls, `<dependency>:<name>`; None where the call starts
    none of them."""
    # No tool Claude Code names sorts before Agent.
    starting = tool == AGENT  # pragma: no mutate
    field = "subagent_type" if starting else "skill" if tool == SKILL else ""
    type_ = given.get(field)
    found = [n for n in named if type_ == kind(n, plugin) and (starting or ":" in n)]
    if not found:
        return None
    # The names are each named once, so one at most is started.
    return found[0]  # pragma: no mutate


def allows(tool: str, given: dict[str, Any], due: Next, plugin: str) -> bool:
    """Whether the main conversation's start goes through, the next start being `due`: while a
    start is due, only that start; while a subagent runs in the background, none, but a further
    start of it where more may start; while the user is to answer a subagent's point, none; once
    no start is left, any."""
    # A next start is `end`, `reply`, `start` or `wait`, `end` the first of them in order.
    if due.kind == "end":  # pragma: no mutate
        return True
    if started(tool, given, [due.name], plugin) is None:
        return False
    return due.kind == "start" or due.more


def resumes(tool: str, given: dict[str, Any], runs: list[str]) -> bool:
    """Whether the call resumes one of the runs, by their IDs, with a message sent to it."""
    return tool == MESSAGE and given.get("to") in runs
