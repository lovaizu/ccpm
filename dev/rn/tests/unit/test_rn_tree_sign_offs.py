"""The unit cases of tree/sign_offs.py, which decides the run's sign-offs and how each moves. A
sign-off moves by what is put up, of each kind, and by whether one waits as the user decides, so
the cases take none put up, each kind put up, one approved and one sent back, a decision with none
waiting, a deliverable the tree doesn't hold, and a file out of its form."""

from __future__ import annotations

import datetime
import os
from typing import Any

import pytest
from fault import Wrong
from tree import sign_offs
from tree.sign_offs import Kind, State

from dev.rn.tests.unit import rn_data as d


def a_run(tmp: Any) -> Any:
    run = d.run_of(d.repository(str(tmp)))
    d.tree_written(run)
    return run


@pytest.mark.supports("test_a_sign_off_pushes_the_work_and_keeps_a_draft_pull_request")
def test_a_run_with_none_put_up_has_no_sign_off(tmp_path: Any) -> None:
    """Given: a run with no sign-off put up.
    When: its sign-offs are read.
    Then: they're none."""
    assert sign_offs.read(a_run(tmp_path)).each == ()


@pytest.mark.supports("test_a_sign_off_pushes_the_work_and_keeps_a_draft_pull_request")
@pytest.mark.parametrize(
    ("kind", "what"),
    [
        (Kind.PLAN, ""),
        (Kind.DELIVERABLE, "invoicer"),
        (Kind.LESSON, "The code best practice says nothing of py.typed."),
        (Kind.PULL_REQUEST, "http://github.com/owner/repo/pull/1"),
    ],
)
def test_each_kind_put_up_waits_with_when_it_was_put_up(
    tmp_path: Any, kind: Kind, what: str
) -> None:
    """Given: a run with no sign-off put up.
    When: the plan, a deliverable, a lesson, or the pull request is put up.
    Then: it waits, with what it puts up word for word and when, in ISO 8601, and the run's
    sign-offs read it back."""
    run = a_run(tmp_path)
    given = sign_offs.put_up(run, kind, what)
    assert (given.kind, given.what, given.state) == (kind, what, State.WAITING)
    datetime.datetime.fromisoformat(given.at.replace("Z", "+00:00"))
    assert sign_offs.read(run).each == (given,)
    assert os.path.isfile(os.path.join(run.folder, "sign-offs.json"))


@pytest.mark.supports("test_ty_approves_the_plan_and_starts_the_work_resting_on_it")
@pytest.mark.parametrize(
    ("approved", "state"), [(True, State.SIGNED_OFF), (False, State.SENT_BACK)]
)
def test_the_sign_off_waiting_is_decided_by_ty_or_gm(
    tmp_path: Any, approved: bool, state: State
) -> None:
    """Given: a run with the plan signed off, and a deliverable waiting.
    When: the sign-off waiting is approved, or sent back.
    Then: the deliverable's is signed off, or sent back, and the plan's stays as it was, in the
    order put up."""
    run = a_run(tmp_path)
    sign_offs.put_up(run, Kind.PLAN, "")
    sign_offs.decide(run, True)
    sign_offs.put_up(run, Kind.DELIVERABLE, "invoicer")
    decided = sign_offs.decide(run, approved)
    assert (decided.kind, decided.state) == (Kind.DELIVERABLE, state)
    assert [s.state for s in sign_offs.read(run).each] == [State.SIGNED_OFF, state]


@pytest.mark.supports("test_only_the_users_own_ty_decides_a_sign_off")
def test_a_decision_with_no_sign_off_waiting_is_refused(tmp_path: Any) -> None:
    """Given: a run whose plan is signed off, and nothing waiting.
    When: a sign-off is approved.
    Then: it's refused."""
    run = a_run(tmp_path)
    sign_offs.put_up(run, Kind.PLAN, "")
    sign_offs.decide(run, True)
    with pytest.raises(Wrong):
        sign_offs.decide(run, True)


@pytest.mark.supports("test_a_deliverable_put_up_and_approved_is_marked_done")
def test_a_deliverable_the_tree_doesnt_hold_is_refused(tmp_path: Any) -> None:
    """Given: a run with the walkthrough's tree.
    When: README.md is put up as a deliverable.
    Then: it's refused, naming README.md."""
    with pytest.raises(Wrong, match="README.md"):
        sign_offs.put_up(a_run(tmp_path), Kind.DELIVERABLE, "README.md")


@pytest.mark.supports("test_only_the_users_own_ty_decides_a_sign_off")
@pytest.mark.parametrize(
    "held",
    [{"sign_offs": [{"kind": "plan", "what": "", "state": "approved", "at": "x"}]}, {"each": []}],
)
def test_sign_offs_out_of_their_form_are_refused(tmp_path: Any, held: Any) -> None:
    """Given: a run whose sign-offs.json holds a state its form doesn't name, or no sign_offs.
    When: its sign-offs are read.
    Then: they're refused."""
    run = a_run(tmp_path)
    d.write_json(os.path.join(run.folder, "sign-offs.json"), held)
    with pytest.raises(Wrong):
        sign_offs.read(run)
