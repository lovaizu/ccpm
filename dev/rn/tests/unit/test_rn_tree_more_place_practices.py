"""The unit cases of tree/more.py, which decides which more is kept, of tree/place.py, which decides
a Place's form, and of tree/practices.py, which decides where a kind's best practice lies for a run.
A more is kept by whether a decision under its necessary condition changed, so the cases take one
changed, one added, none changed, one changed under another condition, and a deliverable that isn't
the tree's. A Place takes its step from 1 up, so the cases take step 1, a Place read back, and
files out of its form or missing. A best practice lies in the run, in rn, or in neither."""

from __future__ import annotations

import copy
import os
import shutil
from typing import Any

import pytest
from fault import CantRun, Wrong
from tree import more, place, practices
from tree.more import More
from tree.place import Place

from dev.rn.tests.unit import rn_data as d

pytestmark = pytest.mark.xfail(
    strict=True, reason="tree/more.py, place.py, and practices.py have empty bodies"
)

GOOD_WHEN = "A caller's editor shows the type of each argument as they type the call."
N1 = More("invoicer", "N1", GOOD_WHEN)


def changed_under(index: int, decided: str = "some files") -> Any:
    """The walkthrough's tree with a decision under the necessary condition of the index changed
    or added."""
    data = copy.deepcopy(d.walkthrough_tree())
    decisions = data["deliverables"][0]["necessary_conditions"][index]["decisions"]
    if decisions:
        decisions[0]["decided"] = decided
    else:
        decisions.append({"about": "what the hints name", "decided": decided, "by": "reasoning"})
    return d.design(data)


@pytest.mark.supports("test_a_more_the_people_fall_short_by_reaches_the_next_rounds_generator")
@pytest.mark.parametrize("now", [changed_under(0), changed_under(0, "only callers' functions")])
def test_a_more_whose_condition_has_a_decision_changed_may_be_kept(now: Any) -> None:
    """Given: the tree as the round's cut took it, and the tree with a decision under N1 changed.
    When: whether the more of N1 may be kept is asked.
    Then: it may."""
    assert more.keepable(d.design(), now, N1) is None


@pytest.mark.supports("test_a_more_the_people_fall_short_by_reaches_the_next_rounds_generator")
def test_a_more_whose_condition_has_a_decision_added_may_be_kept() -> None:
    """Given: the tree as the round's cut took it, and the tree with a decision added under N2.
    When: whether the more of N2 may be kept is asked.
    Then: it may."""
    assert more.keepable(d.design(), changed_under(1), More("invoicer", "N2", GOOD_WHEN)) is None


@pytest.mark.supports("test_a_more_kept_with_no_decision_changed_is_refused")
@pytest.mark.parametrize("now", [d.design(), changed_under(1)])
def test_a_more_with_no_decision_changed_under_its_condition_is_refused(now: Any) -> None:
    """Given: the tree as the round's cut took it, and a tree with nothing changed or a decision
    changed only under N2.
    When: whether the more of N1 may be kept is asked.
    Then: it's refused, naming N1."""
    with pytest.raises(Wrong, match="N1"):
        more.keepable(d.design(), now, N1)


@pytest.mark.supports("test_a_more_kept_with_no_decision_changed_is_refused")
def test_a_more_of_a_deliverable_the_tree_doesnt_hold_is_refused() -> None:
    """Given: the walkthrough's tree before and after a change under N1.
    When: whether a more of README.md may be kept is asked.
    Then: it's refused."""
    with pytest.raises(Wrong):
        more.keepable(d.design(), changed_under(0), More("README.md", "N1", GOOD_WHEN))


@pytest.mark.supports("test_each_steps_end_commits_the_work_with_its_place")
@pytest.mark.parametrize("work", [(), ("invoicer/totals.py", "invoicer/tax.py")])
def test_a_place_written_is_read_back_alike(tmp_path: Any, work: tuple[str, ...]) -> None:
    """Given: the Place of a generator at step 1, with no file of its work and with two.
    When: it's written and read back.
    Then: it reads alike."""
    path = os.path.join(tmp_path, "place.json")
    given = Place(".rn/x/records/1-generator.json", 1, work)
    place.write(path, given)
    assert place.read(path) == given


@pytest.mark.supports("test_up_alone_in_the_runs_worktree_picks_up_where_it_stopped")
@pytest.mark.parametrize("held", [{"record": "r", "step": 0, "work": []}, {"step": 1}, []])
def test_a_place_out_of_its_form_is_refused(tmp_path: Any, held: Any) -> None:
    """Given: a Place file whose step is 0, which lacks its record, or which isn't an object.
    When: it's read.
    Then: it's refused."""
    path = d.write_json(os.path.join(tmp_path, "place.json"), held)
    with pytest.raises(Wrong):
        place.read(path)


@pytest.mark.supports("test_up_alone_in_the_runs_worktree_picks_up_where_it_stopped")
def test_a_place_missing_cant_be_read(tmp_path: Any) -> None:
    """Given: no Place file.
    When: it's read.
    Then: it couldn't run."""
    with pytest.raises(CantRun):
        place.read(os.path.join(tmp_path, "place.json"))


@pytest.mark.supports("test_a_best_practice_made_on_the_run_is_taken_over_rns_own")
def test_a_best_practice_made_on_the_run_is_taken_over_rns_own(tmp_path: Any) -> None:
    """Given: a run whose worktree holds a code best practice in .rn/best-practices/code/.
    When: the folder of the code best practice is asked.
    Then: it gives the run's."""
    run = d.run_of(d.repository(str(tmp_path)))
    made = os.path.join(run.worktree, ".rn", "best-practices", "code")
    shutil.copytree(os.path.join(d.RN, "domain", "best-practices", "code"), made)
    assert os.path.realpath(practices.folder(run, d.RN, "code")) == os.path.realpath(made)


@pytest.mark.supports("test_the_generator_starts_with_its_cut_of_the_first_deliverable_doing")
def test_rns_own_best_practice_is_taken_where_the_run_has_none(tmp_path: Any) -> None:
    """Given: a run with no best practice of its own.
    When: the folder of the code best practice is asked.
    Then: it gives rn's own."""
    run = d.run_of(d.repository(str(tmp_path)))
    own = os.path.join(d.RN, "domain", "best-practices", "code")
    assert os.path.realpath(practices.folder(run, d.RN, "code")) == os.path.realpath(own)


@pytest.mark.supports("test_the_generator_starts_with_its_cut_of_the_first_deliverable_doing")
def test_a_kind_with_no_best_practice_is_refused_naming_the_kinds(tmp_path: Any) -> None:
    """Given: a run with no best practice of its own.
    When: the folder of the kind poem is asked.
    Then: it's refused, naming the kinds there are, readme among them."""
    run = d.run_of(d.repository(str(tmp_path)))
    with pytest.raises(Wrong, match="readme"):
        practices.folder(run, d.RN, "poem")
