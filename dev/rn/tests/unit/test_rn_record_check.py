"""The unit cases of record/check.py, what rn's check holds an end to, and of record/command.py,
record.py's command line. An end turns on its role, its record, its result's items, and its
deliverable's template, so the cases take a generator's end that lacks nothing, one whose record
lacks a practice, one whose deliverable leaves its template, the orchestrator's turn that puts no
work up, and a record out of form; and each command of record.py with its input in form, out of
it, and a command line out of form."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
from fault import Wrong
from record import check, form
from record.command import main
from record.form import Entry
from tree import cut, rounds

from dev.rn.tests.unit import rn_data as d

LATER = pytest.mark.xfail(
    strict=True,
    reason="the case's generator records no step, as the generator's part held none when it was"
    " written, and its part now holds steps 1 to 7",
)


def practice_ids(kind: str) -> list[str]:
    """The ID of each practice of rn's best practice of the kind, deciding ones first."""
    with open(
        os.path.join(d.RN, "domain", "best-practices", kind, "best-practice.json"), encoding="utf-8"
    ) as f:
        goal = json.load(f)["goal"]
    found = [
        (item["at"] != "decide", f"{n['id']}.{i}")
        for factor in goal["critical_success_factors"]
        for n in factor["necessary_conditions"]
        for i, item in enumerate(n["items"], 1)
    ]
    return [each for _, each in sorted(found, key=lambda pair: pair[0])]


def generator_ended(
    tmp: Any, data: dict[str, Any] | None = None, leave_out: str = ""
) -> tuple[Any, str]:
    """A run whose generator took the Cut of its first deliverable doing, recorded each practice
    of its best practices but `leave_out`, and wrote its Made, committed; gives the run and the
    record's path from the worktree."""
    run = d.run_of(d.repository(str(tmp)))
    tree = data or d.with_status(d.walkthrough_tree(), "doing", "open")
    d.tree_written(run, tree)
    given = cut.next_start(run, d.design(tree), "generator", [])
    assert given is not None
    record = given.values["record"]
    kinds = (str(given.part["kind"]), os.path.basename(str(given.part["refactor"]).rstrip("/")))
    for kind in kinds:
        for each in practice_ids(kind):
            if each != leave_out:
                form.add(
                    os.path.join(run.worktree, record), Entry(kind, None, each, "Carried out.")
                )
    d.write_json(
        os.path.join(run.worktree, rounds.made_path(run, str(given.part["deliverable"]), True)),
        d.made(),
    )
    d.git(run.worktree, "add", "-A")
    d.git(run.worktree, "commit", "-q", "-m", "The generator's work")
    return run, record


@LATER
@pytest.mark.supports("test_a_generators_done_result_is_kept_in_its_record")
def test_an_end_that_lacks_nothing_passes_and_keeps_its_result(tmp_path: Any) -> None:
    """Given: a generator that recorded each practice, and wrote a Made naming its decision.
    When: its end with done is checked.
    Then: it lacks nothing, and its record keeps done by the generator."""
    run, record = generator_ended(tmp_path)
    assert check.check(d.RN, run.worktree, "generator", "done", record) == ()
    assert form.read(os.path.join(run.worktree, record)).kept == form.Kept("generator", "done")


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
def test_an_end_whose_record_lacks_a_practice_names_it_and_keeps_nothing(tmp_path: Any) -> None:
    """Given: a generator that recorded each practice but code's N4.1.
    When: its end with done is checked.
    Then: it names N4.1, and its record keeps no result."""
    run, record = generator_ended(tmp_path, leave_out="N4.1")
    found = check.check(d.RN, run.worktree, "generator", "done", record)
    assert any("N4.1" in each for each in found)
    assert form.read(os.path.join(run.worktree, record)).kept is None


@pytest.mark.supports("test_a_generators_end_with_its_deliverable_off_its_template_is_held")
def test_an_end_whose_deliverable_leaves_its_template_names_each_place(tmp_path: Any) -> None:
    """Given: a generator of invoicer's README, which recorded each practice and wrote a README.md
    of one heading.
    When: its end with done is checked.
    Then: it names README.md with a line where it leaves the readme template."""
    readme = d.open_deliverable(
        "A newcomer decides from invoicer's README alone", "README.md", "doing", kind="readme"
    )
    readme["necessary_conditions"] = d.conditions(10)
    run, record = generator_ended(
        tmp_path, {"goal": d.walkthrough_tree()["goal"], "deliverables": [readme]}
    )
    with open(os.path.join(run.worktree, "README.md"), "w", encoding="utf-8") as f:
        f.write("# invoicer\n")
    found = check.check(d.RN, run.worktree, "generator", "done", record)
    assert any(each.startswith("README.md:") for each in found)


@pytest.mark.supports("test_the_goal_is_put_to_the_user_once_the_design_tree_holds_it")
def test_the_orchestrators_turn_that_puts_no_work_up_lacks_nothing(tmp_path: Any) -> None:
    """Given: a run whose orchestrator recorded nothing, and no sign-off waiting.
    When: the end of its turn, giving no result, is checked.
    Then: it lacks nothing."""
    run = d.run_of(d.repository(str(tmp_path)))
    d.tree_written(run)
    assert check.check(d.RN, run.worktree, "orchestrator", "", None) == ()


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
def test_an_end_whose_record_is_out_of_form_is_refused(tmp_path: Any) -> None:
    """Given: a generator whose record holds step 0.
    When: its end is checked.
    Then: it's refused."""
    run, record = generator_ended(tmp_path)
    d.write_json(
        os.path.join(run.worktree, record),
        {"entries": [{"of": "generator", "step": 0, "gave": "x"}]},
    )
    with pytest.raises(Wrong):
        check.check(d.RN, run.worktree, "generator", "done", record)


@pytest.mark.supports("test_record_py_refuses_an_entry_out_of_its_form")
def test_add_records_an_entry_and_refuses_one_out_of_form(tmp_path: Any) -> None:
    """Given: no record at the path.
    When: record.py add runs with step 3 of the generator, then with the practice X1.
    Then: the first gives 0 and the record holds the step, and the second gives 1 with what's
    wrong."""
    path = os.path.join(tmp_path, "record.json")
    assert main(["add", path, "generator", "3", "Made it."], str(tmp_path), d.RN)[0] == 0
    assert form.read(path).entries == (Entry("generator", 3, None, "Made it."),)
    code, out, err = main(["add", path, "code", "X1", "x"], str(tmp_path), d.RN)
    assert (code, out) == (1, "") and err


@LATER
@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
def test_check_gives_0_or_1_with_each_thing_lacking_on_a_line(tmp_path: Any) -> None:
    """Given: a generator that recorded each practice, and one that left out code's N4.1.
    When: record.py check generator done runs on each record.
    Then: the first gives 0, and the second 1 with N4.1 on a line of its own."""
    run, record = generator_ended(tmp_path / "whole")
    assert main(["check", "generator", "done", record], run.worktree, d.RN)[0] == 0
    run, record = generator_ended(tmp_path / "short", leave_out="N4.1")
    code, _, err = main(["check", "generator", "done", record], run.worktree, d.RN)
    assert code == 1 and any("N4.1" in line for line in err.splitlines())


@pytest.mark.supports("test_record_py_refuses_an_entry_out_of_its_form")
@pytest.mark.parametrize("argv", [[], ["add", "record.json"], ["keep"]])
def test_a_command_line_out_of_form_gives_2_with_the_usage(tmp_path: Any, argv: list[str]) -> None:
    """Given: a folder.
    When: record.py runs with no command, add lacking its arguments, or a command it doesn't know.
    Then: it gives 2 with the usage."""
    code, out, err = main(argv, str(tmp_path), d.RN)
    assert (code, out) == (2, "") and "usage" in err
