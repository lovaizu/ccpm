"""The integration cases of S10, a run picked up: after /compact, the run that the run record holds,
not ended, giving where it stands; in a new conversation, the run added from the results that the
plugin's kept adapter gives for the words typed after the command; and each state of Claude Code
that bears on them, as dev/lane/claude-code-states.md lists it. Each runs `log` and Lane through the
double of Claude Code."""

from __future__ import annotations

import pytest
from lane_bench import (
    UNREPORTED,
    WORDS,
    Bench,
    opened,
    reached,
    started,
    text,
    to_review,
    written,
)

pytestmark = UNREPORTED

WRITTEN = [{"role": "log:writer", "result": "written"}]


@pytest.mark.supports("S10", "Run")
def test_after_compact_the_run_goes_on_with_its_starts_due(b: Bench):
    """Given the writer due
    When the person types /compact, and the main conversation ends its turn
    Then the compaction goes through, its summary's end lying outside the run, and the end is
    stopped with the writer due"""
    c = opened(b)
    assert not c.compact().blocked
    answer = c.stop("Compacted.")
    assert answer.blocked
    assert text("log:writer") in answer.said


@pytest.mark.supports("S10", "Run")
def test_the_command_typed_after_compact_gives_where_the_run_picks_up(b: Bench):
    """Given the writer ended with `written`, so the reviewer is due, and the person typed /compact
    When the person types /log:up 1.2.0 again
    Then the main conversation reads, at the command, the reviewer due with its text"""
    c = to_review(b)
    c.compact()
    answer = c.type(f"/log:up {WORDS}")
    assert text("log:reviewer") in answer.said
    assert text("log:writer") not in answer.said


@pytest.mark.supports("S10", "Run")
def test_a_subagent_running_through_compact_stays_on_its_start(b: Bench):
    """Given the writer running, and the person typed /compact
    When the writer keeps each step and ends
    Then its end reaches the main conversation with the reviewer due"""
    c = opened(b)
    writer = started(c)
    c.compact()
    written(writer)
    assert text("log:reviewer") in reached(writer).said


@pytest.mark.supports("S10", "Kept results")
def test_a_new_conversation_picks_the_run_up_from_the_kept_results(b: Bench):
    """Given `log` keeping the writer's `written` for 1.2.0, and a new conversation
    When the person types /log:up 1.2.0, and the main conversation ends its turn
    Then the end is stopped with the reviewer due, not the writer"""
    b.kept(WORDS, WRITTEN)
    answer = opened(b).stop("Picked up.")
    assert answer.blocked
    assert text("log:reviewer") in answer.said
    assert text("log:writer") not in answer.said


@pytest.mark.supports("S10", "Kept results")
def test_the_kept_adapter_is_asked_with_the_words_typed_after_the_command(b: Bench):
    """Given `log` keeping the writer's `written` for 1.2.0 alone, and a new conversation
    When the person types /log:up 1.3.0, and the main conversation ends its turn
    Then the end is stopped with the writer due for 1.3.0, as nothing is kept for it"""
    b.kept(WORDS, WRITTEN)
    answer = opened(b, "1.3.0").stop("Started.")
    assert text("log:writer", "1.3.0") in answer.said


@pytest.mark.supports("S10", "Kept results")
def test_a_run_picked_up_by_the_skill_tool_takes_its_arguments_as_the_words(b: Bench):
    """Given `log` keeping the writer's `written` for 1.2.0, and a new conversation
    When the main conversation calls log:up by the Skill tool with 1.2.0, and ends its turn
    Then the end is stopped with the reviewer due"""
    b.kept(WORDS, WRITTEN)
    c = b.converse()
    c.skill("log:up", WORDS)
    assert text("log:reviewer") in c.stop("Picked up.").said


@pytest.mark.supports("S10", "Kept results", "Route")
def test_kept_results_after_which_the_routes_start_no_more_leave_none_due(b: Bench):
    """Given `log` keeping the writer's `written` and the reviewer's `good` for 1.2.0
    When the person types /log:up 1.2.0 in a new conversation, and the main conversation ends its
    turn
    Then the end goes through, as the run ended"""
    b.kept(WORDS, [*WRITTEN, {"role": "log:reviewer", "result": "good"}])
    assert not opened(b).stop("Nothing left.").blocked


@pytest.mark.supports("S10")
def test_a_plugin_without_a_kept_adapter_starts_the_run_from_its_command(b: Bench):
    """Given `log` with no kept adapter, its kept file holding the writer's `written`
    When the person types /log:up 1.2.0 in a new conversation, and the main conversation ends its
    turn
    Then the end is stopped with the writer due, as the command's route makes it"""
    b.adapter("kept.py", None)
    b.kept(WORDS, WRITTEN)
    assert text("log:writer") in opened(b).stop("Started.").said


@pytest.mark.supports("S10", "Kept results")
def test_a_kept_adapter_that_fails_stops_with_the_adapter_and_what_it_said(b: Bench):
    """Given `log` whose kept adapter exits 1 saying the kept file is broken
    When the person types /log:up 1.2.0 in a new conversation, and the main conversation ends its
    turn
    Then the end is stopped, naming the adapter and what it said, for the plugin's author to mend"""
    b.adapter("kept.py", "import sys\n\nsys.exit('the kept file is broken')\n")
    answer = opened(b).stop("Started.")
    assert answer.blocked
    assert "kept.py" in answer.said
    assert "the kept file is broken" in answer.said
