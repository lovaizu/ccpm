"""The integration cases of S2, how each piece went: status with no piece recorded, with a piece
still recorded as waiting whose runner no longer runs, and with a record left out of its layout,
each as status runs pieces.py."""

from __future__ import annotations

import os

import overnight_files
import pytest
from overnight_bench import Bench
from overnight_files import SHARE

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's bodies aren't built yet")


@pytest.mark.supports("S2", "status")
def test_status_with_no_piece_handed_over_shows_no_pieces_yet(b: Bench):
    """Given the walkthrough's repository, where no piece was handed over
    When status runs in a later session
    Then pieces.py gives 0 with `No pieces yet`"""
    assert b.status() == (0, "No pieces yet\n", "")


@pytest.mark.supports("S2", "pieces", "Wait")
def test_a_piece_whose_runner_ended_while_it_waited_is_counted_stopped_by_the_usage_limit(
    b: Bench,
):
    """Given piece 1 stopped by the session limit and waiting for its reset, and piece 2 done
    When the runner of piece 1 ends while it waits, as the OS shuts it down, and status runs
    Then status shows piece 1 no longer waiting, and 1 of 2 pieces stopped"""
    b.plays(
        {
            "1": [{"kind": "session limit"}, {"kind": "ends"}],
            "2": [{"kind": "ends", "last_words": "Done."}],
        }
    )
    b.hold_waits()
    b.hand()
    b.until(lambda: b.rows()[0]["State"] == "waiting", what="piece 1 to wait")
    (runner,) = b.runners()
    overnight_files.kill(runner)
    b.release_waits()
    b.hand()
    rows = b.settle(2)
    assert rows[0]["State"] != "waiting"
    assert rows[1]["State"] == "done"
    assert b.status().out.splitlines()[-1] == SHARE.format(1, 2)


@pytest.mark.supports("pieces", "Record")
def test_a_record_left_out_of_its_layout_is_refused_naming_its_file(b: Bench):
    """Given piece 1 done, whose record a person then overwrote with text that isn't JSON
    When status runs
    Then pieces.py gives 2, printing nothing, with words that name the record's file"""
    b.plays({"1": [{"kind": "ends"}]})
    b.hand()
    b.settle(1)
    (folder,) = os.listdir(b.at(".overnight"))
    (name,) = os.listdir(b.at(f".overnight/{folder}"))
    with open(b.at(f".overnight/{folder}/{name}"), "w", encoding="utf-8") as f:
        f.write("{not json")
    refused = b.status()
    assert (refused.code, refused.out) == (2, "")
    assert name in refused.err
