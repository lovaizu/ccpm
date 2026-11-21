"""The integration cases of S8, the plugin's own check: an end that the check of its role doesn't
pass stopped with the step's sentence and what the check said, an end that it passes let through,
and the check run only once the result and each step hold. Each runs `log` and Lane through the
double of Claude Code."""

from __future__ import annotations

import pytest
from lane_bench import CHECK_SAYS, Bench, opened, reached, started, written

# An entry of another version, which the check of `log` doesn't pass.
OLD_ENTRY = "# Changelog\n\n## 1.1.0\n\n- Invoices render.\n"


@pytest.mark.supports("S8", "rule types")
def test_an_end_that_the_plugins_check_doesnt_pass_is_stopped_with_what_it_said(b: Bench):
    """Given the writer that kept each step, its CHANGELOG.md holding no entry of 1.2.0
    When it ends
    Then the end is stopped with the sentence of `report` and what the check said"""
    writer = started(opened(b))
    written(writer, entry=OLD_ENTRY)
    answer = writer.end("Done.")[0]
    assert answer.blocked
    assert "report" in answer.said
    assert CHECK_SAYS in answer.said


@pytest.mark.supports("S8")
def test_an_end_that_the_plugins_check_passes_goes_through(b: Bench):
    """Given the writer that kept each step, its CHANGELOG.md holding the entry of 1.2.0
    When it ends
    Then its end reaches the main conversation"""
    writer = started(opened(b))
    written(writer)
    assert reached(writer) is not None


@pytest.mark.supports("S8", "rule types")
def test_an_end_with_no_result_names_the_result_before_the_check(b: Bench):
    """Given the writer that kept each step but reported no result, its CHANGELOG.md holding no
    entry of 1.2.0
    When it ends
    Then the end is stopped naming `written`, and not what the check would say"""
    writer = started(opened(b))
    written(writer, result=None, entry=OLD_ENTRY)
    answer = writer.end("Done.")[0]
    assert "written" in answer.said
    assert CHECK_SAYS not in answer.said


@pytest.mark.supports("S8", "rule types")
def test_an_end_with_a_step_undone_names_the_step_before_the_check(b: Bench):
    """Given the writer that reported `written` but not its step `report`, its CHANGELOG.md
    holding no entry of 1.2.0
    When it ends
    Then the end is stopped naming `report`, and not what the check would say"""
    writer = started(opened(b))
    written(writer, entry=OLD_ENTRY, report=False)
    answer = writer.end("Done.")[0]
    assert "report" in answer.said
    assert CHECK_SAYS not in answer.said
