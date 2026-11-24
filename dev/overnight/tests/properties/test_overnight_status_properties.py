"""The property-based tests of what status shows, as overnight's Test strategy names them: the
invariant that the README's walkthrough and the architecture state of the table of a night, which
the user reads in a later session to learn how each piece went.

- How the night went, seen at a glance (P5.1, P5.3, S2): for any night of pieces in any states,
  with any last words of one line, the table gives one row of each piece, in the order of their
  numbers, with its branch and its last words where it ended, and its last line the share stopped,
  else the user misreads which piece holds which work, or how many the night stopped."""

from __future__ import annotations

import os
import tempfile
from datetime import timedelta

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from overnight_bench import rows_of
from overnight_files import SHARE, handed, running_process, shut_down
from overnight_stand_ins import STOP
from pieces.command import main
from pieces.record import begin, end, wait

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's bodies aren't built yet")

# Last words of one line, as Claude Code ends a run: any letters, marks, and quotes, but no break
# of a line, and no space at either end, which a table's cell doesn't show.
LAST_WORDS = (
    st.text(st.characters(blacklist_categories=("Cs", "Cc", "Zl", "Zp")), min_size=1, max_size=60)
    .map(str.strip)
    .filter(bool)
)
STATES = st.sampled_from(["running", "waiting", "done", "failed"])


@pytest.mark.supports(
    "test_the_walkthroughs_three_pieces_go_on_through_the_limit_and_show_done_in_a_later_session"
)
@settings(max_examples=30)
@given(
    st.dictionaries(
        st.integers(1, 120), st.tuples(STATES, st.booleans(), LAST_WORDS), min_size=1, max_size=5
    )
)
def test_the_table_shows_each_piece_in_order_and_the_share_stopped(
    night: dict[int, tuple[str, bool, str]],
):
    """Given any night of one to five pieces of any numbers, each running, waiting, done, or
    failed with any last words of one line, each carried by a runner that runs or by one that has
    ended
    When status runs
    Then it gives 0, with a row of each piece in the order of their numbers, each on its branch,
    each done or failed showing its last words, and the last line the share of the pieces left
    running or waiting by a runner that ended
    (Model-based, resting on P5.1, P5.3, and S2.)"""
    child = running_process()
    try:
        with tempfile.TemporaryDirectory() as repo:
            for number, (state, runs, words) in night.items():
                begin(repo, handed(number, ("Read",)), os.getpid() if runs else child.pid)
                if state == "waiting":
                    wait(repo, number, STOP, STOP + timedelta(hours=3))
                elif state in ("done", "failed"):
                    end(repo, number, state, words)
            shut_down(child)
            code, out, err = main(["report"], repo)
            rows = rows_of(out)
            assert (code, err) == (0, "")
            assert [(row["Piece"], row["Branch"]) for row in rows] == [
                (str(n), f"overnight/{n}") for n in sorted(night)
            ]
            for row in rows:
                state, _, words = night[int(row["Piece"])]
                if state in ("done", "failed"):
                    assert (row["State"], row["Last words"]) == (state, words)
            stopped = sum(
                state in ("running", "waiting") and not runs for state, runs, _ in night.values()
            )
            assert out.splitlines()[-1] == SHARE.format(stopped, len(night))
    finally:
        shut_down(child)
