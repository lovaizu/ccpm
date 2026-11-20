"""The integration cases of S6, a step's checklist: a reporter's mark of the step done before each
item that the step's rule of the checklist names is done stopped with each item not yet done, and
let through once each is, the items named in the rule or given at the mark by the plugin's command,
which runs in the folder that the conversation works in and whose failure stops the mark. Each runs
`log` and Lane through the double of Claude Code."""

from __future__ import annotations

import copy
import os

import pytest
from claude_code import Agent
from lane_bench import RULES, Bench, items, opened, started


@pytest.mark.supports("S6", "rule types")
def test_a_step_marked_before_its_items_names_each_item_not_done(b: Bench):
    """Given the writer running, NOTES.md read whole, no item done
    When it reports the step `write` done
    Then it reads the step's sentence naming each item, `dated` and `linked`"""
    writer = started(opened(b))
    writer.read(b.at("NOTES.md"))
    said = writer.bash("lane-step write").said
    assert "dated" in said
    assert "linked" in said


@pytest.mark.supports("S6")
def test_a_step_marked_with_one_item_done_names_only_the_other(b: Bench):
    """Given the writer running, NOTES.md read whole, and the item `dated` done
    When it reports the step `write` done
    Then it reads the step's sentence naming `linked` and not `dated`"""
    writer = started(opened(b))
    writer.read(b.at("NOTES.md"))
    writer.bash("lane-item write dated")
    said = writer.bash("lane-step write").said
    assert "linked" in said
    assert "dated" not in said


@pytest.mark.supports("S6")
def test_a_step_marked_once_each_item_is_done_holds(b: Bench):
    """Given the writer running, NOTES.md read whole, and each item done
    When it reports the step `write` done
    Then it reads no sentence naming an item"""
    writer = started(opened(b))
    writer.read(b.at("NOTES.md"))
    items(writer)
    said = writer.bash("lane-step write").said
    assert "dated" not in said
    assert "linked" not in said


# A checklist whose items the plugin's command gives at the mark: each file that the writer wrote
# under docs/changes/, and, where it wrote none, an exit 1 saying so.
NO_CHANGES = "no changes written yet"
LISTED = f"test -d docs/changes || {{ echo '{NO_CHANGES}'; exit 1; }}; ls docs/changes"


def listed_by_command(b: Bench) -> None:
    """Writes the rules of `log` with the writer's checklist of `write` given by LISTED in place
    of its items."""
    rules = copy.deepcopy(RULES)
    write = rules["roles"]["log:writer"]["steps"][0]
    write["rules"] = [r for r in write["rules"] if r["type"] != "checklist"]
    write["rules"].append({"type": "checklist", "command": LISTED})
    b.rules(rules)


def wrote(writer: Agent, *names: str) -> None:
    """The writer writes each part under docs/changes/, and reads NOTES.md whole."""
    for name in names:
        writer.write(os.path.join(writer.conversation.cwd, "docs", "changes", name), "x\n")
    writer.read(os.path.join(writer.conversation.cwd, "NOTES.md"))


COMMANDED = pytest.mark.xfail(strict=True, reason="checklist.items gives no command's items yet")


@COMMANDED
@pytest.mark.supports("S6", "Rules")
def test_a_step_marked_before_the_items_its_command_gives_names_each_not_done(b: Bench):
    """Given `log` whose writer's checklist of `write` is each file under docs/changes/, as its
    command lists them, and the writer running, which wrote a.md and b.md there
    When it marks the item a.md done, and reports the step `write` done
    Then the mark is stopped with the step's sentence naming b.md and not a.md"""
    listed_by_command(b)
    writer = started(opened(b))
    wrote(writer, "a.md", "b.md")
    writer.bash("lane-item write a.md")
    said = writer.bash("lane-step write").said
    assert "b.md" in said
    assert "a.md" not in said


@COMMANDED
@pytest.mark.supports("S6")
def test_a_checklist_given_by_a_command_takes_the_items_at_the_mark(b: Bench):
    """Given `log` whose writer's checklist of `write` is each file under docs/changes/, and the
    writer running, which wrote a.md there and marked it done
    When it writes b.md there, and reports the step `write` done, and then marks b.md done and
    reports `write` done again
    Then the first mark is stopped with the step's sentence naming b.md, and the second reads no
    sentence naming it"""
    listed_by_command(b)
    writer = started(opened(b))
    wrote(writer, "a.md")
    writer.bash("lane-item write a.md")
    wrote(writer, "b.md")
    assert "b.md" in writer.bash("lane-step write").said
    writer.bash("lane-item write b.md")
    assert "b.md" not in writer.bash("lane-step write").said


@COMMANDED
@pytest.mark.supports("S6", "guard")
def test_a_checklist_command_that_exits_other_than_0_stops_the_mark_with_what_it_printed(
    b: Bench,
):
    """Given `log` whose writer's checklist of `write` is given by a command that exits 1 saying no
    changes are written yet, where docs/changes/ isn't there, and the writer running, NOTES.md read
    whole
    When it reports the step `write` done
    Then the mark is stopped with the step `write` and what the command printed"""
    listed_by_command(b)
    writer = started(opened(b))
    wrote(writer)
    said = writer.bash("lane-step write").said
    assert "`write`" in said
    assert NO_CHANGES in said


@COMMANDED
@pytest.mark.supports("S6", "guard")
def test_a_checklist_command_runs_in_the_worktree_the_conversation_works_in(b: Bench):
    """Given `log` whose writer's checklist of `write` is each file under docs/changes/, and the
    main conversation in a worktree, where the writer wrote a.md under docs/changes/, which the
    repository's top doesn't hold
    When the writer reports the step `write` done
    Then the mark is stopped naming a.md, as the command lists the worktree's files"""
    listed_by_command(b)
    c = opened(b)
    c.enter_worktree("entry")
    writer = started(c)
    wrote(writer, "a.md")
    said = writer.bash("lane-step write").said
    assert "a.md" in said
    assert NO_CHANGES not in said
