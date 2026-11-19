"""The integration cases of S6, a step's checklist: a reporter's mark of the step done before each
item that the plugin's checklist adapter gives is done stopped with each item not yet done, and let
through once each is. Each runs `log` and Lane through the double of Claude Code."""

from __future__ import annotations

import pytest
from lane_bench import UNREPORTED, Bench, items, opened, started

pytestmark = UNREPORTED


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


@pytest.mark.supports("S6")
def test_a_checklist_rule_with_no_checklist_adapter_says_what_to_mend(b: Bench):
    """Given `log` with no checklist adapter, and the writer running with NOTES.md read whole
    When it reports the step `write` done
    Then it reads that `log` gives no checklist adapter, naming lane/adapters/checklist.py"""
    b.adapter("checklist.py", None)
    writer = started(opened(b))
    writer.read(b.at("NOTES.md"))
    assert "checklist.py" in writer.bash("lane-step write").said
