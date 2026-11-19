"""The unit cases of hooks/lane/report.py: report, one for each kind of reporter and each count of
words that fits or doesn't fit it, and read_report, one for each class of a Bash call's output."""

from __future__ import annotations

import pytest
from report import read_report, report

pytestmark = pytest.mark.xfail(strict=True, reason="Lane's parts have no bodies yet")


def printed(capsys: pytest.CaptureFixture[str], kind: str, words: list[str]) -> tuple[int, str]:
    """What report gives for the kind and the words, and the line it prints."""
    code = report(kind, words)
    return code, capsys.readouterr().out


@pytest.mark.supports("test_a_step_marked_before_the_step_before_it_is_stopped_with_the_step_due")
def test_a_step_with_its_name_prints_its_report(capsys: pytest.CaptureFixture[str]):
    """Given the reporter of a step
    When it reports `write`
    Then it gives 0, and the line it printed reads back as the step `write` done"""
    code, out = printed(capsys, "step", ["write"])
    assert code == 0
    assert out.endswith("\n") and out.count("\n") == 1
    assert read_report(out) == {"kind": "step", "step": "write"}


@pytest.mark.supports("test_a_step_marked_with_one_item_done_names_only_the_other")
def test_an_item_with_its_step_and_name_prints_its_report(capsys: pytest.CaptureFixture[str]):
    """Given the reporter of an item
    When it reports `dated` of the step `write`
    Then it gives 0, and its line reads back as that item done"""
    code, out = printed(capsys, "item", ["write", "dated"])
    assert code == 0
    assert read_report(out) == {"kind": "item", "step": "write", "item": "dated"}


@pytest.mark.supports("test_the_reviewers_more_makes_the_writer_due_again")
def test_a_result_prints_its_report(capsys: pytest.CaptureFixture[str]):
    """Given the reporter of a result
    When it reports `more`
    Then it gives 0, and its line reads back as the result `more`"""
    code, out = printed(capsys, "result", ["more"])
    assert code == 0
    assert read_report(out) == {"kind": "result", "result": "more"}


@pytest.mark.supports(
    "test_a_reporter_given_words_that_dont_fit_its_kind_exits_2_with_what_it_takes"
)
@pytest.mark.parametrize(
    "kind, words",
    [
        ("step", []),
        ("step", ["write", "report"]),
        ("item", ["write"]),
        ("item", ["write", "dated", "linked"]),
        ("result", []),
        ("result", ["good", "more"]),
    ],
)
def test_words_that_dont_fit_the_kind_give_2_with_what_it_takes(
    capsys: pytest.CaptureFixture[str], kind: str, words: list[str]
):
    """Given a reporter of the kind
    When it's given one word fewer or more than its kind takes
    Then it gives 2, prints nothing on standard output, and says on standard error what it takes"""
    code = report(kind, words)
    out, err = capsys.readouterr()
    assert code == 2
    assert out == ""
    assert f"lane-{kind}" in err


@pytest.mark.supports("test_a_reporters_result_counts_for_the_subagent_that_ran_it")
@pytest.mark.parametrize(
    "output",
    ["", "bf742e7 first\n", '{"kind": "step"}\n', '{"kind": "size", "step": "write"}\n'],
)
def test_output_that_no_reporter_printed_reads_as_no_report(output: str):
    """Given the output of a Bash call that ran no reporter, or JSON not of a report
    When the guard reads it
    Then it reads no report"""
    assert read_report(output) is None


@pytest.mark.supports("test_a_reporters_result_counts_for_the_subagent_that_ran_it")
def test_a_report_beside_other_output_reads_as_no_report(capsys: pytest.CaptureFixture[str]):
    """Given a reporter's line after a line that another command printed
    When the guard reads the output
    Then it reads no report, as only the reporter's one line is a report"""
    report("result", ["written"])
    out = capsys.readouterr().out
    assert read_report("done\n" + out) is None
