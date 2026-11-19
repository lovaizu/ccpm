"""The integration cases of S3, the files a step reads whole: a reporter's mark of the step done
before each file that the step names is read whole by the start's own Reads stopped with the step's
sentence and the lines not read, and let through once Reads of the start cover each line. Each runs
`log` and Lane through the double of Claude Code."""

from __future__ import annotations

import pytest
from lane_bench import UNBUILT, Bench, items, opened, started

pytestmark = UNBUILT


@pytest.mark.supports("S3", "rule types")
def test_a_step_marked_done_with_a_file_unread_is_stopped_with_the_file(b: Bench):
    """Given the writer running, each item of its step `write` done, and NOTES.md never read
    When it reports the step `write` done
    Then the main conversation's view of the writer reads the step's sentence naming NOTES.md, and
    the step stays undone, so reporting `report` done is stopped naming `write`"""
    writer = started(opened(b))
    items(writer)
    assert "NOTES.md" in writer.bash("lane-step write").said
    assert "write" in writer.bash("lane-step report").said


@pytest.mark.supports("S3")
def test_a_step_marked_done_after_a_read_in_part_names_the_lines_not_read(b: Bench):
    """Given the writer running, each item done, and lines 1 and 2 of NOTES.md read
    When it reports the step `write` done
    Then it reads the step's sentence naming NOTES.md and its line 3, the first not read"""
    writer = started(opened(b))
    items(writer)
    writer.read(b.at("NOTES.md"), offset=1, limit=2)
    said = writer.bash("lane-step write").said
    assert "NOTES.md" in said
    assert "3" in said


@pytest.mark.supports("S3")
def test_reads_in_parts_that_cover_each_line_read_the_file_whole(b: Bench):
    """Given the writer running, each item done, and NOTES.md read in two parts, lines 1 to 3 and
    4 to 6
    When it reports the step `write` done
    Then the mark holds, and no sentence names NOTES.md"""
    writer = started(opened(b))
    items(writer)
    writer.read(b.at("NOTES.md"), offset=1, limit=3)
    writer.read(b.at("NOTES.md"), offset=4, limit=3)
    assert "NOTES.md" not in writer.bash("lane-step write").said


@pytest.mark.supports("S3")
def test_a_read_whole_holds_the_mark(b: Bench):
    """Given the writer running, each item done, and NOTES.md read with no limit
    When it reports the step `write` done
    Then no sentence names NOTES.md"""
    writer = started(opened(b))
    items(writer)
    writer.read(b.at("NOTES.md"))
    assert "NOTES.md" not in writer.bash("lane-step write").said


@pytest.mark.supports("S3")
def test_a_read_of_the_main_conversation_counts_for_no_subagent(b: Bench):
    """Given the writer running, each item done, and NOTES.md read whole by the main conversation
    When the writer reports the step `write` done
    Then it reads the step's sentence naming NOTES.md, as only its own Read counts"""
    c = opened(b)
    writer = started(c)
    items(writer)
    c.read(None, b.at("NOTES.md"))
    assert "NOTES.md" in writer.bash("lane-step write").said
