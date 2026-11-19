"""The integration cases of S10, a run picked up: after /compact, the run that the run record holds,
not ended, going on where it stands; in a new conversation, a run added with the words typed after
the command, whose starts due the plugin's order gives from where the plugin's own files say the run
stands; and each state of Claude Code that bears on them, as dev/lane/claude-code-states.md lists
it. Each runs `log` and Lane through the double of Claude Code."""

from __future__ import annotations

import pytest
from lane_bench import (
    ENTRY,
    ORDER,
    UNBUILT,
    WORDS,
    Bench,
    opened,
    reached,
    started,
    to_review,
    written,
)
from repo_files import git, write_files


def entry_kept(b: Bench) -> None:
    """`log` decides its order by ORDER, and the repository keeps the entry of 1.2.0 that an earlier
    conversation's writer wrote."""
    b.adapter("starts_due.py", ORDER)
    write_files(b.repo, {"CHANGELOG.md": ENTRY})
    git(b.repo, "add", "-A")
    git(b.repo, "commit", "-q", "-m", "The entry of 1.2.0")


@pytest.mark.supports("S10", "Run")
@UNBUILT
def test_after_compact_the_run_goes_on_with_its_starts_due(b: Bench):
    """Given the writer due
    When the person types /compact, and the main conversation ends its turn
    Then the compaction goes through, its summary's end lying outside the run, and the end is
    stopped with the writer due"""
    c = opened(b)
    assert not c.compact().blocked
    answer = c.stop("Compacted.")
    assert answer.blocked
    assert "log:writer" in answer.said


@pytest.mark.supports("S10", "Run")
@UNBUILT
def test_the_command_typed_after_compact_gives_where_the_run_stands(b: Bench):
    """Given the writer ended with `written`, so the reviewer is due, and the person typed /compact
    When the person types /log:up 1.2.0 again, and the main conversation starts the reviewer
    Then the main conversation reads, at the command, the reviewer due, and the start goes
    through, as the run goes on where it stands"""
    c = to_review(b)
    c.compact()
    assert "log:reviewer" in c.type(f"/log:up {WORDS}").said
    assert started(c, "log:reviewer") is not None


@pytest.mark.supports("S10", "Run")
def test_a_subagent_running_through_compact_stays_on_its_start(b: Bench):
    """Given the writer running, and the person typed /compact
    When the writer keeps each step and ends
    Then its end reaches the main conversation with the reviewer due"""
    c = opened(b)
    writer = started(c)
    c.compact()
    written(writer)
    assert "log:reviewer" in reached(writer).said


@pytest.mark.supports("S10", "Starts due")
@UNBUILT
def test_a_new_conversation_goes_on_where_the_plugins_own_files_say(b: Bench):
    """Given `log` deciding its order from CHANGELOG.md, which holds the entry of 1.2.0 that an
    earlier conversation wrote
    When the person types /log:up 1.2.0 in a new conversation, and the main conversation ends its
    turn
    Then the end is stopped with the reviewer due"""
    entry_kept(b)
    answer = opened(b).stop("Picked up.")
    assert answer.blocked
    assert "log:reviewer" in answer.said


@pytest.mark.supports("S10")
@UNBUILT
def test_the_order_of_a_new_conversation_takes_the_words_typed_after_the_command(b: Bench):
    """Given `log` deciding its order from CHANGELOG.md, which holds the entry of 1.2.0 alone
    When the person types /log:up 1.3.0 in a new conversation, and the main conversation ends its
    turn
    Then the end is stopped with the writer due, as nothing is written for 1.3.0"""
    entry_kept(b)
    answer = opened(b, "1.3.0").stop("Started.")
    assert answer.blocked
    assert "log:writer" in answer.said


@pytest.mark.supports("S10")
@UNBUILT
def test_a_run_added_by_the_skill_tool_takes_its_arguments_as_the_words(b: Bench):
    """Given `log` deciding its order from CHANGELOG.md, which holds the entry of 1.2.0
    When the main conversation calls log:up by the Skill tool with 1.2.0 in a new conversation, and
    ends its turn
    Then the end is stopped with the reviewer due"""
    entry_kept(b)
    c = b.converse()
    c.skill("log:up", WORDS)
    assert "log:reviewer" in c.stop("Picked up.").said


@pytest.mark.supports("S10", "route adapter")
@UNBUILT
def test_a_new_conversation_of_a_plugin_that_fixes_its_order_starts_from_its_command(b: Bench):
    """Given `log` fixing its order by routes alone, and the repository keeping the entry of 1.2.0
    When the person types /log:up 1.2.0 in a new conversation, and the main conversation ends its
    turn
    Then the end is stopped with the writer due, as the route after the command makes it and no
    file of the plugin's is read"""
    write_files(b.repo, {"CHANGELOG.md": ENTRY})
    answer = opened(b).stop("Started.")
    assert answer.blocked
    assert "log:writer" in answer.said
