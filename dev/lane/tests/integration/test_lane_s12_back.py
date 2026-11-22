"""The integration cases of S12, going back to an earlier step: a reporter's step gone back to, a
step marked done, undoing the marks of it and of each step after it, the items of their checklists
among them, so that the step is at hand again, a later step marked before it is stopped with it as
the step due, and an end is stopped while it is undone; the reads kept, as the file was read; each
step taken again in order letting the end through; a step gone back to that isn't marked done
stopped with its sentence, undoing nothing; and going back let through at a step whose rule of
commands doesn't name it. Each runs `log` and Lane through the double of Claude Code."""

from __future__ import annotations

import copy
import os

import pytest
from claude_code import Agent
from lane_bench import RULES, Bench, items, opened, reached, started, written


def gone_back(b: Bench) -> Agent:
    """The writer that kept each step and gave `written`, then went back to its step `write`."""
    writer = started(opened(b))
    written(writer)
    back = writer.bash("lane-back write")
    assert (back.exit_code, back.said) == (0, ""), back.output
    return writer


@pytest.mark.supports("S12", "reporters")
def test_a_later_step_marked_after_going_back_is_stopped_with_the_step_gone_back_to(b: Bench):
    """Given the writer that kept each step, then went back to `write`
    When it reports the step `report` done
    Then the mark is stopped with the sentence of `report` naming `write` as the step due"""
    assert gone_back(b).bash("lane-step report").said == (
        "You're at the step `write` of log:writer, which comes before `report`.\n"
        "Do `write` and mark it done with lane-step write first."
    )


@pytest.mark.supports("S12")
def test_a_step_gone_back_to_asks_its_items_again_and_keeps_its_reads(b: Bench):
    """Given the writer that kept each step, NOTES.md read whole, then went back to `write`
    When it reports the step `write` done again
    Then the mark is stopped with the checklist's sentence naming `dated` and `linked`, not with the
    sentence of NOTES.md, as the read stays counted"""
    assert gone_back(b).bash("lane-step write").said == (
        "You're at the step `write` of log:writer, whose checklist isn't done: dated and linked.\n"
        "Do each and mark it done with lane-item write <item> first."
    )


@pytest.mark.supports("S12", "S5")
def test_an_end_after_going_back_is_stopped_with_the_step_gone_back_to(b: Bench):
    """Given the writer that kept each step and gave `written`, then went back to `write`
    When it ends
    Then the end is stopped with the sentence of `write`"""
    answer = gone_back(b).end("Done.")[0]
    assert answer.blocked
    assert answer.said == (
        "You end before the step `write` of log:writer is done.\n"
        "Do it and mark it done with lane-step write."
    )


@pytest.mark.supports("S12")
def test_each_step_taken_again_in_order_after_going_back_lets_the_end_through(b: Bench):
    """Given the writer that kept each step, then went back to `write`
    When it marks each item and `write` again, reads CHANGELOG.md again, marks `report`, and ends
    Then each mark holds, and its end reaches the main conversation with `written`"""
    writer = gone_back(b)
    items(writer)
    assert writer.bash("lane-step write").said == ""
    writer.read(os.path.join(writer.conversation.cwd, "CHANGELOG.md"))
    assert writer.bash("lane-step report").said == ""
    assert "written" in reached(writer).said


@pytest.mark.supports("S12", "reporters")
def test_a_step_gone_back_to_that_isnt_marked_done_is_stopped_with_its_sentence(b: Bench):
    """Given the writer that marked `write` done, at its step `report`
    When it goes back to `report`, which isn't marked done
    Then it's stopped with the sentence naming `report` as the step at hand, and `write` stays
    done, so that a mark of `report` names no step before it"""
    writer = started(opened(b))
    written(writer, result=None, report=False)
    assert writer.bash("lane-back report").said == (
        "You're at the step `report` of log:writer, and `report` isn't marked done.\n"
        "Go back only to a step marked done, with lane-back <step>."
    )
    assert writer.bash("lane-step report").said == ""


@pytest.mark.supports("S12", "reporters")
def test_going_back_goes_through_at_a_step_whose_rule_of_commands_doesnt_name_it(b: Bench):
    """Given `log` whose writer's step `report` runs only `git log`, and the writer that marked
    `write` done, at its step `report`
    When it runs `lane-back write`
    Then the call goes through, and a mark of `report` is stopped naming `write` as the step due"""
    rules = copy.deepcopy(RULES)
    rules["roles"]["log:writer"]["steps"][1]["rules"].append(
        {"type": "commands", "commands": ["git log"]}
    )
    b.rules(rules)
    writer = started(opened(b))
    written(writer, result=None, report=False)
    back = writer.bash("lane-back write")
    assert (back.blocked, back.exit_code, back.said) == (False, 0, ""), back.output
    assert writer.bash("lane-step report").said == (
        "You're at the step `write` of log:writer, which comes before `report`.\n"
        "Do `write` and mark it done with lane-step write first."
    )
