"""Lane's E2E cases: the walkthrough of Lane's README at its real size, run 3 times on the real
Claude Code on Opus by dev/scripts/e2e.py, with an AI in the user's place that holds an intent Lane
never sees, which builds a plugin the size of changelog, approves its proposal once by a person's
reply and once by its own act, changes the steps between two runs of `/lane:up`, and runs the
plugin. The developer runs them once every unit and integration test passes, with their login as
CLAUDE_CODE_OAUTH_TOKEN."""

from __future__ import annotations

import pytest
from walkthrough_records import judge, known_answers, kr1_1, kr1_2, last, walkthroughs

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)


@pytest.fixture(scope="module")
def records() -> list[str]:
    """The records of 3 runs of the walkthrough."""
    return walkthroughs()


@pytest.mark.supports("KR1.1")
def test_kr1_1_the_share_of_the_plugins_runs_that_go_wrong_is_no_larger_than_in_the_last_runs(
    records: list[str],
):
    """Given Lane as it now stands, and the KR1.1 of the last runs kept
    When an AI in the user's place runs the walkthrough 3 times
    Then the share of the plugin's runs that went wrong in one of the product vision's ways is no
    larger than the last runs'"""
    before = last("KR1.1")
    now = kr1_1(records)
    assert before is None or now <= before, f"KR1.1 rose from {before} to {now}"


@pytest.mark.supports("KR1.2")
def test_kr1_2_the_time_to_the_first_held_run_is_no_longer_where_kr1_1_holds(records: list[str]):
    """Given Lane as it now stands, and the KR1.1 and KR1.2 of the last runs kept
    When an AI in the user's place runs the walkthrough 3 times
    Then, where KR1.1 is the last runs', the time from the first step to the first run of the
    plugin that keeps them is no longer than the last runs'"""
    before, held = last("KR1.2"), last("KR1.1")
    now = kr1_2(records)
    assert before is None or kr1_1(records) != held or now <= before, (
        f"KR1.2 rose from {before} to {now}"
    )


@pytest.mark.supports("KR1.1")
def test_the_judge_is_right_on_each_kept_record_whose_answer_is_known():
    """Given each kept record of a run of the plugin whose answer on a way of KR1.1 is known
    When the judge gives its verdict on that way
    Then its verdict is the known answer on every one"""
    known = known_answers()
    wrong = [(r, run, way) for r, run, way, answer in known if judge(r, run, way).wrong != answer]
    assert known and not wrong, wrong
