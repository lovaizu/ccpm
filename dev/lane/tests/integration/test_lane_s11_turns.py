"""The integration cases of S11, the steps given at each turn: a main conversation whose role
`log`'s rules name with no steps takes, at each turn's first call or end, the steps that the
plugin's adapter of the rules gives for the turn's prompt, empty for the run's first turn, for the
role of the run's latest command then, and for each earlier turn of the run; each call and mark of
the turn is held to them, and its end is stopped while a step is undone. Each transition of a turn
that Claude Code's states bring about has its case: a turn's end let through, then a person's
prompt, a subagent's end, a command typed, or two subagents' ends one after the other, each
beginning a turn; a turn whose steps rest on the earlier turns that the adapter is given; a turn's
end that Lane stops, then a subagent's end, going on in the same turn; a subagent's end reaching the
main conversation within its turn; a turn whose first move is its end; a command that the Skill
tool calls within a turn, which gives the turn its steps afresh; and the command that each turn
called, which the adapter is given. Each runs `log` and Lane through the double of Claude Code."""

from __future__ import annotations

import pytest
from claude_code import Agent, Conversation
from lane_bench import (
    TAG_WRITES,
    UP_UNDONE,
    Bench,
    opened,
    reached,
    started,
    steps_by_turn,
    written,
)

# The note that TURN_ADAPTER gives the run's first turn to write, from the run's words.
FIRST_NOTE = ".log/1.2.0.md"


def writes(paths: str, file: str) -> str:
    """The sentence of the main conversation's write of the file at the step `up` of log:up, which
    writes only the paths."""
    return (
        f"You're at the step `up` of log:up, which writes only {paths}.\n"
        f"Write there instead of {file}."
    )


# What the writer replies as it ends, which its task-notification carries to the main conversation.
WROTE = "Wrote docs/changes/1.2.0.md."

# An adapter of the starts due that makes the writer due twice at once until two starts of it are
# made, and then none, never ending the run.
TWO_WRITERS = """\
import json, sys

moves = json.load(sys.stdin)["run"]["moves"]
made = len([m for m in moves if m["kind"] == "start"])
print(json.dumps({"starts": [{"role": "log:writer", "count": 2 - made}] if made < 2 else []}))
"""

# An adapter of the rules that gives each turn the step named by its role's skill, writing each
# Markdown file that the turn's prompt names, or, where it names none, those that the latest
# earlier turn's prompt names, as the answer to a question rests on the turn that asked it.
EARLIER_TURNS = """\
import json, re, sys

given = json.load(sys.stdin)
prompts = [turn["prompt"] for turn in given["turns"]] + [given["prompt"]]
named = [re.findall(r"[\\w./-]+\\.md", prompt) for prompt in prompts]
paths = ([each for each in named if each] or [[]])[-1]
rules = [{"type": "order"}, {"type": "writes", "paths": paths}]
print(json.dumps({"steps": [{"name": given["role"].partition(":")[2], "rules": rules}]}))
"""

# An adapter of the rules that gives each turn one step, writing nothing, named by the command that
# each earlier turn called and that this turn called, oldest first, `none` for a turn that called
# none, so that a write's sentence shows what the adapter was given.
COMMANDS = """\
import json, sys

given = json.load(sys.stdin)
called = [turn["command"] for turn in given["turns"]] + [given["command"]]
name = "-".join((each or ":none").partition(":")[2] for each in called)
rules = [{"type": "order"}, {"type": "writes", "paths": []}]
print(json.dumps({"steps": [{"name": name, "rules": rules}]}))
"""


def writes_nothing(step: str, role: str) -> str:
    """The sentence of the main conversation's write of notes.txt at the step of the role, which
    writes nothing."""
    return (
        f"You're at the step `{step}` of {role}, which writes nothing.\nLeave notes.txt unwritten."
    )


def first_turn_ended(b: Bench) -> tuple[Conversation, Agent]:
    """A conversation of `log` taking its steps at each turn, whose first turn started the writer,
    marked its step `up` done, and ended, its end let through; gives it with the writer."""
    steps_by_turn(b)
    c = opened(b)
    writer = started(c)
    c.bash("lane-step up")
    stopped = c.stop("The writer runs.")
    assert not stopped.blocked, stopped.said
    return c, writer


@pytest.mark.supports("S11", "Rules")
def test_the_runs_first_turn_takes_its_steps_from_the_adapter_with_the_runs_words(b: Bench):
    """Given `log` whose rules name log:up with no steps, and whose adapter of the rules gives a
    turn with no prompt the step `up`, which writes the note of the run's words
    When the person types /log:up 1.2.0, and the main conversation writes notes.txt, and then
    .log/1.2.0.md
    Then the first write, the run's first event after the skill's call, is stopped with the
    writer due and the sentence of the step `up` of log:up naming .log/1.2.0.md, and the second
    goes through"""
    steps_by_turn(b)
    c = opened(b)
    answer = c.write(None, b.at("notes.txt"), "x\n")
    assert answer.blocked
    assert answer.said == "Due: log:writer.\n" + writes(FIRST_NOTE, "notes.txt")
    assert not c.write(None, b.at(FIRST_NOTE), "x\n").blocked


@pytest.mark.supports("S11", "S5")
def test_the_turns_end_before_its_step_is_marked_is_stopped_and_goes_through_once_it_is(b: Bench):
    """Given the person's /log:up 1.2.0 in `log` taking its steps at each turn, and the writer
    started
    When the main conversation ends its turn, and then marks `up` done and ends it again
    Then the first end is stopped with the sentence of the step `up`, and the second goes
    through"""
    steps_by_turn(b)
    c = opened(b)
    started(c)
    answer = c.stop("The writer runs.")
    assert answer.blocked
    assert answer.said == UP_UNDONE
    c.bash("lane-step up")
    assert not c.stop("The writer runs.").blocked


@pytest.mark.supports("S11", "Run")
def test_a_subagents_end_after_the_turns_end_begins_a_turn_held_to_steps_from_its_notification(
    b: Bench,
):
    """Given `log` taking its steps at each turn, whose first turn ended, its end let through
    When the writer keeps each step and ends replying that it wrote docs/changes/1.2.0.md, and the
    main conversation writes .log/1.2.0.md, and then docs/changes/1.2.0.md
    Then the first write is stopped naming docs/changes/1.2.0.md, as the new turn's steps come from
    the task-notification, and the second goes through"""
    c, writer = first_turn_ended(b)
    written(writer)
    reached(writer, WROTE)
    answer = c.write(None, b.at(FIRST_NOTE), "x\n")
    assert answer.blocked
    assert answer.said == writes("docs/changes/1.2.0.md", FIRST_NOTE)
    assert not c.write(None, b.at("docs/changes/1.2.0.md"), "x\n").blocked


@pytest.mark.supports("S11", "S5")
def test_a_turn_whose_first_move_is_its_end_is_held_to_its_own_steps_afresh(b: Bench):
    """Given `log` taking its steps at each turn, whose first turn marked `up` done and ended, its
    end let through
    When the writer keeps each step and ends, and the main conversation ends the turn that its end
    begins at once
    Then the end is stopped with the sentence of the step `up`, as the first turn's mark counts
    for that turn alone"""
    c, writer = first_turn_ended(b)
    written(writer)
    reached(writer, WROTE)
    answer = c.stop("The reviewer is due.")
    assert answer.blocked
    assert answer.said == UP_UNDONE


@pytest.mark.supports("S11")
def test_a_persons_prompt_after_the_turns_end_begins_a_turn_held_to_steps_from_it(b: Bench):
    """Given `log` taking its steps at each turn, whose first turn ended, its end let through
    When the person types `Write docs/notes.md.`, and the main conversation writes .log/1.2.0.md,
    and then docs/notes.md
    Then the first write is stopped naming docs/notes.md, and the second goes through"""
    c, _ = first_turn_ended(b)
    c.type("Write docs/notes.md.")
    answer = c.write(None, b.at(FIRST_NOTE), "x\n")
    assert answer.blocked
    assert answer.said == writes("docs/notes.md", FIRST_NOTE)
    assert not c.write(None, b.at("docs/notes.md"), "x\n").blocked


@pytest.mark.supports("S11")
def test_a_turns_adapter_of_the_rules_is_given_each_earlier_turn_with_its_role_and_prompt(
    b: Bench,
):
    """Given `log` taking its steps at each turn from an adapter of the rules that, for a prompt
    naming no Markdown file, writes those that the latest earlier turn's prompt names, and whose
    first turn ended, its end let through
    When the person types `Write docs/notes.md.`, the main conversation marks `up` done and ends
    its turn, the person types `Again.`, and the main conversation writes .log/1.2.0.md, and then
    docs/notes.md
    Then the end goes through, the first write is stopped naming docs/notes.md, from the earlier
    turn, and the second goes through"""
    c, _ = first_turn_ended(b)
    b.adapter("rules.py", EARLIER_TURNS)
    c.type("Write docs/notes.md.")
    c.bash("lane-step up")
    assert not c.stop("Noted.").blocked
    c.type("Again.")
    answer = c.write(None, b.at(FIRST_NOTE), "x\n")
    assert answer.blocked
    assert answer.said == writes("docs/notes.md", FIRST_NOTE)
    assert not c.write(None, b.at("docs/notes.md"), "x\n").blocked


@pytest.mark.supports("S11", "S9")
def test_a_command_typed_after_the_turns_end_begins_a_turn_in_its_skills_role(b: Bench):
    """Given `log` taking its steps at each turn for log:up and log:tag, whose first turn ended,
    its end let through
    When the person types /log:tag, and the main conversation writes notes.txt
    Then the write is stopped with the sentence of the step `tag` of log:tag, the step that the
    adapter gives that role"""
    c, _ = first_turn_ended(b)
    c.type("/log:tag")
    answer = c.write(None, b.at("notes.txt"), "x\n")
    assert answer.blocked
    assert answer.said == TAG_WRITES


@pytest.mark.supports("S11", "S9")
def test_a_skill_called_within_a_turn_gives_the_turn_its_skills_steps_afresh(b: Bench):
    """Given the person's /log:up 1.2.0 in `log` taking its steps at each turn for log:up and
    log:tag, and the writer started
    When the main conversation calls log:tag by the Skill tool, writes notes.txt, starts the
    tagger, marks `tag` done, and ends its turn
    Then the write is stopped with the sentence of the step `tag` of log:tag, which the adapter
    gives that role, writing the run's first turn's note, and the end goes through"""
    steps_by_turn(b)
    c = opened(b)
    started(c)
    c.skill("log:tag", "")
    answer = c.write(None, b.at("notes.txt"), "x\n")
    assert answer.blocked
    assert answer.said == (
        f"You're at the step `tag` of log:tag, which writes only {FIRST_NOTE}.\n"
        "Write there instead of notes.txt."
    )
    started(c, "log:tagger")
    c.bash("lane-step tag")
    assert not c.stop("Tagged.").blocked


@pytest.mark.supports("S11", "S9")
def test_a_turns_adapter_of_the_rules_is_given_the_command_that_each_turn_called(b: Bench):
    """Given `log` taking its steps at each turn from an adapter of the rules that names the step
    by the command that each earlier turn and this turn called, and whose first turn, of /log:up,
    started the writer
    When the main conversation writes notes.txt in that turn, in a turn of the person's `Go on.`,
    in a turn of `Tag it.` before and after it calls log:tag by the Skill tool, starting the
    tagger, and in a turn of a typed /log:tag, marking each turn's step done and ending it
    Then each write is stopped at the step `up`, `up-none`, `up-none-none`, `up-none-tag`, and
    `up-none-tag-tag`, of log:up until the Skill call and of log:tag after it"""
    steps_by_turn(b)
    b.adapter("rules.py", COMMANDS)
    c = opened(b)
    started(c)
    seen = []

    def wrote(role: str) -> str:
        answer = c.write(None, b.at("notes.txt"), "x\n")
        assert answer.blocked
        step = answer.said.split("`")[1]
        assert answer.said == writes_nothing(step, role)
        seen.append(step)
        return step

    def ended() -> None:
        c.bash(f"lane-step {seen[-1]}")
        assert not c.stop("Done.").blocked

    wrote("log:up")
    ended()
    c.type("Go on.")
    wrote("log:up")
    ended()
    c.type("Tag it.")
    wrote("log:up")
    c.skill("log:tag", "")
    wrote("log:tag")
    started(c, "log:tagger")
    ended()
    c.type("/log:tag")
    wrote("log:tag")
    assert seen == ["up", "up-none", "up-none-none", "up-none-tag", "up-none-tag-tag"]


@pytest.mark.supports("S11", "S9")
def test_two_subagents_ends_one_after_the_other_each_begin_a_turn_of_their_own(b: Bench):
    """Given `log` taking its steps at each turn, whose order makes the writer due twice at once,
    and whose first turn started both writers, marked `up` done, and ended, its end let through
    When the first writer ends replying that it wrote docs/changes/one.md, the main conversation
    writes that file, marks `up` done, and ends its turn, and then the second writer ends replying
    that it wrote docs/changes/two.md, and the main conversation writes docs/changes/three.md
    Then the first write and the turn's end go through, and the last write is stopped naming
    docs/changes/two.md"""
    steps_by_turn(b)
    b.adapter("starts_due.py", TWO_WRITERS)
    c = opened(b)
    one, two = started(c), started(c)
    c.bash("lane-step up")
    assert not c.stop("Both writers run.").blocked
    written(one)
    reached(one, "Wrote docs/changes/one.md.")
    assert not c.write(None, b.at("docs/changes/one.md"), "x\n").blocked
    c.bash("lane-step up")
    assert not c.stop("One writer is done.").blocked
    written(two, path="docs/changes/1.2.0/two.md")
    reached(two, "Wrote docs/changes/two.md.")
    answer = c.write(None, b.at("docs/changes/three.md"), "x\n")
    assert answer.blocked
    assert answer.said == writes("docs/changes/two.md", "docs/changes/three.md")


@pytest.mark.supports("S11")
def test_a_subagents_end_after_a_turns_end_that_lane_stopped_goes_on_in_the_same_turn(b: Bench):
    """Given the person's /log:up 1.2.0 in `log` taking its steps at each turn, the writer started,
    and the main conversation's end of its turn stopped, as `up` is undone
    When the writer keeps each step and ends replying that it wrote docs/changes/1.2.0.md, and the
    main conversation writes docs/changes/1.2.0.md, and then .log/1.2.0.md
    Then the first write is stopped naming .log/1.2.0.md, and the second goes through, as the
    turn goes on with its own steps"""
    steps_by_turn(b)
    c = opened(b)
    writer = started(c)
    assert c.stop("The writer runs.").blocked
    written(writer)
    reached(writer, WROTE)
    answer = c.write(None, b.at("docs/changes/1.2.0.md"), "x\n")
    assert answer.blocked
    assert answer.said == writes(FIRST_NOTE, "docs/changes/1.2.0.md")
    assert not c.write(None, b.at(FIRST_NOTE), "x\n").blocked


@pytest.mark.supports("S11", "S9")
def test_a_subagents_end_that_reaches_the_main_conversation_within_its_turn_leaves_the_turn(
    b: Bench,
):
    """Given the person's /log:up 1.2.0 in `log` taking its steps at each turn, the writer started,
    and `up` marked done
    When the main conversation stops the writer by TaskStop, whose notification reaches it within
    the turn, starts the writer due again, and ends its turn
    Then the end goes through, as the mark of `up` counts for the same turn"""
    steps_by_turn(b)
    c = opened(b)
    writer = started(c)
    c.bash("lane-step up")
    c.task_stop(writer)
    started(c)
    assert not c.stop("The writer runs again.").blocked
