"""The unit cases of tree/more.py, which decides which more is kept, of tree/place.py, which decides
a Place's form, and of tree/practices.py, which decides where a kind's best practice lies for a run
and which groups of necessary conditions judge a kind. A more is kept by whether the decision it
names lies under its deliverable and changed, so the cases take that decision changed, added, the
same, under another deliverable, missing from the tree, a deliverable that isn't the tree's, and a
more of the refactor best practice whose condition ID the kind's best practice shares. A Place
takes its step from 1 up, so the cases take step 1, a Place read back, and files out of its form or
missing. A best practice lies in the run, in rn, or in neither."""

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

GOOD_WHEN = "A caller's editor shows the type of each argument as they type the call."
N1_DECISION = "deliverables/0/necessary_conditions/0/decisions/0"
N2_DECISION = "deliverables/0/necessary_conditions/1/decisions/0"


def a_more(
    decision: str = N1_DECISION,
    deliverable: str = "invoicer",
    best_practice: str = "code",
    condition: str = "N1",
) -> More:
    """A more of the walkthrough's first deliverable, of N1 of the code best practice by default."""
    return More(deliverable, best_practice, condition, decision, GOOD_WHEN)


def changed_under(index: int, decided: str = "some files", deliverable: int = 0) -> Any:
    """The walkthrough's tree with the first decision under the necessary condition of the index,
    of the deliverable of the index, changed or added."""
    data = copy.deepcopy(d.walkthrough_tree())
    decisions = data["deliverables"][deliverable]["necessary_conditions"][index]["decisions"]
    if decisions:
        decisions[0]["decided"] = decided
    else:
        decisions.append({"about": "what the hints name", "decided": decided, "by": "reasoning"})
    return d.design(data)


@pytest.mark.supports("test_a_more_the_people_fall_short_by_reaches_the_next_rounds_generator")
@pytest.mark.parametrize("now", [changed_under(0), changed_under(0, "only callers' functions")])
def test_a_more_whose_decision_changed_may_be_kept(now: Any) -> None:
    """Given: the tree as the round's cut took it, and the tree with the decision under N1 of
    invoicer changed.
    When: whether a more of N1 naming that decision may be kept is asked.
    Then: it may."""
    assert more.keepable(d.design(), now, a_more()) is None


@pytest.mark.supports("test_a_more_the_people_fall_short_by_reaches_the_next_rounds_generator")
def test_a_more_whose_decision_the_cut_didnt_hold_may_be_kept() -> None:
    """Given: the tree as the round's cut took it, and the tree with a decision added under N2.
    When: whether a more of N2 naming the added decision may be kept is asked.
    Then: it may."""
    assert more.keepable(d.design(), changed_under(1), a_more(N2_DECISION, condition="N2")) is None


@pytest.mark.supports("test_a_more_the_people_fall_short_by_reaches_the_next_rounds_generator")
def test_a_more_of_the_refactor_practice_goes_by_its_decision_not_its_condition_id() -> None:
    """Given: the tree as the round's cut took it, and the tree with the decision under N1 changed
    and none under N2.
    When: whether a more of N2 of the refactor best practice naming the decision under N1 may be
    kept is asked.
    Then: it may, as the kind's N2 isn't the refactor one's."""
    kept = a_more(best_practice="refactor-code", condition="N2")
    assert more.keepable(d.design(), changed_under(0), kept) is None


@pytest.mark.supports("test_a_more_kept_with_no_decision_changed_is_refused")
@pytest.mark.parametrize("now", [d.design(), changed_under(1)])
def test_a_more_whose_decision_didnt_change_is_refused(now: Any) -> None:
    """Given: the tree as the round's cut took it, and a tree with nothing changed or only a
    decision under N2 changed.
    When: whether a more of N1 naming the decision under N1 may be kept is asked.
    Then: it's refused, naming the code best practice and N1."""
    with pytest.raises(Wrong, match="code") as refused:
        more.keepable(d.design(), now, a_more())
    assert "N1" in str(refused.value)


@pytest.mark.supports("test_a_more_kept_with_no_decision_changed_is_refused")
def test_a_more_whose_decision_moved_in_the_list_but_didnt_change_is_refused() -> None:
    """Given: the tree as the round's cut took it, and the tree with a deliverable added before
    invoicer, which moves invoicer to deliverables/1, its decisions unchanged.
    When: whether a more of invoicer naming its decision under N1 at its new path may be kept is
    asked.
    Then: it's refused, naming the code best practice and N1, as that decision didn't change."""
    data = copy.deepcopy(d.walkthrough_tree())
    data["deliverables"].insert(0, d.open_deliverable("invoicer's README", "README.md"))
    moved = "deliverables/1/necessary_conditions/0/decisions/0"
    with pytest.raises(Wrong, match="code") as refused:
        more.keepable(d.design(), d.design(data), a_more(moved))
    assert "N1" in str(refused.value)


@pytest.mark.supports("test_a_more_kept_with_no_decision_changed_is_refused")
def test_a_more_whose_decision_lies_under_another_deliverable_is_refused() -> None:
    """Given: the tree as the round's cut took it, and the tree with a decision added under N1 of
    "invoicer marked as typed".
    When: whether a more of invoicer naming that decision may be kept is asked.
    Then: it's refused, naming the code best practice and N1, as only a decision under invoicer
    starts its next round."""
    other = "deliverables/1/necessary_conditions/0/decisions/0"
    with pytest.raises(Wrong, match="code") as refused:
        more.keepable(d.design(), changed_under(0, deliverable=1), a_more(other))
    assert "N1" in str(refused.value)


@pytest.mark.supports("test_a_more_kept_with_no_decision_changed_is_refused")
def test_a_more_naming_no_decision_of_the_tree_is_refused_naming_the_path() -> None:
    """Given: the tree as the round's cut took it, and the tree with the decision under N1 changed.
    When: whether a more naming a decision that the tree doesn't hold may be kept is asked.
    Then: it's refused, naming the path."""
    missing = "deliverables/0/necessary_conditions/0/decisions/5"
    with pytest.raises(Wrong, match=missing):
        more.keepable(d.design(), changed_under(0), a_more(missing))


@pytest.mark.supports("test_a_more_kept_with_no_decision_changed_is_refused")
def test_a_more_of_a_deliverable_the_tree_doesnt_hold_is_refused() -> None:
    """Given: the walkthrough's tree before and after a change under N1.
    When: whether a more of README.md may be kept is asked.
    Then: it's refused."""
    with pytest.raises(Wrong):
        more.keepable(d.design(), changed_under(0), a_more(deliverable="README.md"))


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


@pytest.mark.supports("test_the_round_gives_each_evaluators_answers_and_what_the_generator_made")
def test_a_kind_is_judged_by_its_groups_then_the_refactor_ones(tmp_path: Any) -> None:
    """Given: a run with no best practice of its own.
    When: the groups that judge a deliverable of code are asked.
    Then: each group of the code best practice comes first, then each of refactor-code, each
    naming its kind and folder, and the two share condition IDs."""
    run = d.run_of(d.repository(str(tmp_path)))
    judged = practices.judged_by(run, d.RN, "code")
    kinds = [g.kind for g in judged]
    first = kinds.index("refactor-code")
    assert set(kinds[:first]) == {"code"} and set(kinds[first:]) == {"refactor-code"}
    for group in judged:
        assert os.path.realpath(group.folder) == os.path.realpath(
            practices.folder(run, d.RN, group.kind)
        )
    code = {c for g in judged if g.kind == "code" for c in g.conditions}
    refactor = {c for g in judged if g.kind == "refactor-code" for c in g.conditions}
    assert code & refactor


@pytest.mark.supports("test_the_generator_starts_with_its_cut_of_the_first_deliverable_doing")
def test_a_kind_with_no_best_practice_is_judged_by_no_group(tmp_path: Any) -> None:
    """Given: a run with no best practice of its own.
    When: the groups that judge a deliverable of the kind poem are asked.
    Then: it's refused, naming the kinds there are."""
    run = d.run_of(d.repository(str(tmp_path)))
    with pytest.raises(Wrong, match="readme"):
        practices.judged_by(run, d.RN, "poem")
