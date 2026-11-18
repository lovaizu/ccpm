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
from tree import cut, records, rounds, sign_offs
from tree.sign_offs import Kind

from dev.rn.tests.rn_walkthrough import steps_of
from dev.rn.tests.unit import rn_data as d


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


def four_lines(tmp: Any) -> None:
    """a.py of 4 lines in the folder."""
    with open(os.path.join(tmp, "a.py"), "w", encoding="utf-8") as f:
        f.write("1\n2\n3\n4\n")


def generator_ended(
    tmp: Any, data: dict[str, Any] | None = None, leave_out: str = ""
) -> tuple[Any, str]:
    """A run whose generator took the Cut of its first deliverable doing, recorded the first step
    of its part, each practice of its best practices but `leave_out`, and each other step, as its
    part says, and wrote its Made, committed; gives the run and the record's path from the
    worktree."""
    run = d.run_of(d.repository(str(tmp)))
    tree = data or d.with_status(d.walkthrough_tree(), "doing", "open")
    d.tree_written(run, tree)
    given = cut.next_start(run, d.design(tree), "generator", [])
    assert given is not None
    record = given.values["record"]
    kinds = (str(given.part["kind"]), os.path.basename(str(given.part["refactor"]).rstrip("/")))
    first, *others = steps_of(d.RN, "domain/generator.md")
    entries = [Entry("generator", first, None, "a.py:1")]
    entries += [Entry(k, None, p, "a.py:1") for k in kinds for p in practice_ids(k)]
    entries += [Entry("generator", step, None, "a.py:1") for step in others]
    for entry in entries:
        if entry.practice != leave_out:
            form.add(os.path.join(run.worktree, record), entry)
    d.write_json(
        os.path.join(run.worktree, rounds.made_path(run, str(given.part["deliverable"]), True)),
        d.made(),
    )
    d.git(run.worktree, "add", "-A")
    d.git(run.worktree, "commit", "-q", "-m", "The generator's work")
    return run, record


@pytest.mark.supports("test_a_generators_done_result_is_kept_in_its_record")
def test_an_end_that_lacks_nothing_passes_and_keeps_its_result(tmp_path: Any) -> None:
    """Given: a generator that recorded each step and practice, and wrote a Made naming its
    decision.
    When: its end with done is checked.
    Then: it lacks nothing, and its record keeps done by the generator."""
    run, record = generator_ended(tmp_path)
    assert check.check(d.RN, run.worktree, "generator", "done", record) == ()
    assert form.read(os.path.join(run.worktree, record)).kept == form.Kept("generator", "done")


def making_ids(kind: str) -> list[str]:
    """The ID of each practice of rn's best practice of the kind marked make."""
    with open(
        os.path.join(d.RN, "domain", "best-practices", kind, "best-practice.json"), encoding="utf-8"
    ) as f:
        goal = json.load(f)["goal"]
    return [
        f"{n['id']}.{i}"
        for factor in goal["critical_success_factors"]
        for n in factor["necessary_conditions"]
        for i, item in enumerate(n["items"], 1)
        if item["at"] == "make"
    ]


@pytest.mark.supports("test_the_goal_and_the_plan_reach_the_design_tree_through_the_tree_keeper")
def test_a_tree_keeper_resumed_with_a_change_is_held_to_the_making_practices_alone(
    tmp_path: Any,
) -> None:
    """Given: a tree-keeper resumed with a change, which recorded its steps and each practice of
    the design tree best practice marked make, and none marked decide, as the orchestrator
    decides each change and the tree-keeper writes it.
    When: its end with done is checked.
    Then: it lacks nothing."""
    run = d.run_of(d.repository(str(tmp_path)))
    d.tree_written(run)
    given = cut.next_start(run, d.design(d.walkthrough_tree()), "tree-keeper", [])
    assert given is not None
    record = os.path.join(run.worktree, given.values["record"])
    first, *others = steps_of(d.RN, "domain/tree-keeper.md")
    entries = [Entry("tree-keeper", first, None, "a.py:1")]
    entries += [Entry("tree-keeper", step, None, "a.py:1") for step in others]
    entries += [Entry("tree-keeper", first, None, "a.py:1")]
    entries += [Entry("design-tree", None, p, "a.py:1") for p in making_ids("design-tree")]
    entries += [Entry("tree-keeper", step, None, "a.py:1") for step in others]
    for entry in entries:
        form.add(record, entry)
    assert check.check(d.RN, run.worktree, "tree-keeper", "done", given.values["record"]) == ()


@pytest.mark.supports("test_the_goal_and_the_plan_reach_the_design_tree_through_the_tree_keeper")
def test_a_tree_keepers_first_pass_with_its_first_step_at_two_places_lacks_no_practice(
    tmp_path: Any,
) -> None:
    """Given: a tree-keeper at its start, which recorded its first step at two places in one run,
    the best practice and the tree, then each other step, and no practice, as its first pass only
    reads the tree.
    When: its end with done is checked.
    Then: it lacks nothing, as one pass holds each run of its first step's entries."""
    run = d.run_of(d.repository(str(tmp_path)))
    d.tree_written(run)
    given = cut.next_start(run, d.design(d.walkthrough_tree()), "tree-keeper", [])
    assert given is not None
    record = os.path.join(run.worktree, given.values["record"])
    first, *others = steps_of(d.RN, "domain/tree-keeper.md")
    form.add(
        record,
        Entry("tree-keeper", first, None, "a.py:1"),
        Entry("tree-keeper", first, None, "b.py:1"),
    )
    form.add(record, *(Entry("tree-keeper", step, None, "a.py:1") for step in others))
    assert check.check(d.RN, run.worktree, "tree-keeper", "done", given.values["record"]) == ()


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
def test_an_end_whose_record_lacks_a_practice_names_it_and_keeps_nothing(tmp_path: Any) -> None:
    """Given: a generator that recorded each step and practice but code's N4.1.
    When: its end with done is checked.
    Then: it names N4.1, and its record keeps no result."""
    run, record = generator_ended(tmp_path, leave_out="N4.1")
    found = check.check(d.RN, run.worktree, "generator", "done", record)
    assert any("N4.1" in each for each in found)
    assert form.read(os.path.join(run.worktree, record)).kept is None


@pytest.mark.supports("test_a_generators_end_with_its_deliverable_off_its_template_is_held")
def test_an_end_whose_deliverable_leaves_its_template_names_each_place(tmp_path: Any) -> None:
    """Given: a generator of invoicer's README, which recorded each step and practice and wrote a
    README.md of one heading.
    When: its end with done is checked.
    Then: it names README.md with a line where it leaves the readme template."""
    readme = d.open_deliverable(
        "A newcomer decides from invoicer's README alone", "README.md", "doing", kind="readme"
    )
    readme["necessary_conditions"] = d.conditions(10)
    run, record = generator_ended(
        tmp_path,
        {
            "goal": d.walkthrough_tree()["goal"],
            "deliverables": [readme],
            "work": [{"do": "make", "path": "README.md"}],
        },
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


# The orchestrator's record at the end of its turn: no sign-off waits, or one waits; and what the
# turn recorded: every step of up and of its part, a step of its part missing, a command typed whose
# steps it left out, or its part's last step left out, which has work only where no run is left.


def orchestrator_turn(tmp: Any, *entries: tuple[str, int]) -> Any:
    """A run whose plan waits for the user's sign-off, and whose orchestrator recorded the entries,
    each a step of a prompt; gives the run."""
    run = d.run_of(d.repository(str(tmp)))
    d.tree_written(run)
    sign_offs.put_up(run, Kind.PLAN, "")
    path = os.path.join(run.worktree, records.orchestrator_record(run))
    form.add(path, *(Entry(of, n, None, "a.py:1") for of, n in entries))
    return run


def every_step(of: str, file: str) -> list[tuple[str, int]]:
    return [(of, n) for n in steps_of(d.RN, file)]


UP = every_step("up", "skills/up/SKILL.md")
PART = every_step("orchestrator", "domain/orchestrator.md")


@pytest.mark.supports("test_the_goal_is_put_to_the_user_once_the_design_tree_holds_it")
def test_a_sign_off_waiting_and_every_step_of_up_and_the_part_recorded_lacks_nothing(
    tmp_path: Any,
) -> None:
    """Given: a run whose plan waits, and whose orchestrator recorded each step of up and of its
    part in order.
    When: the end of its turn is checked.
    Then: it lacks nothing."""
    run = orchestrator_turn(tmp_path, *UP, *PART)
    assert check.check(d.RN, run.worktree, "orchestrator", "", None) == ()


@pytest.mark.supports("test_the_goal_is_put_to_the_user_once_the_design_tree_holds_it")
def test_a_sign_off_waiting_and_a_step_of_the_part_missing_names_it(tmp_path: Any) -> None:
    """Given: a run whose plan waits, and whose orchestrator recorded each step of up and each of
    its part but step 2.
    When: the end of its turn is checked.
    Then: it names step 3 recorded before step 2, and each step of the part after it."""
    run = orchestrator_turn(tmp_path, *UP, *[e for e in PART if e[1] != 2])
    found = check.check(d.RN, run.worktree, "orchestrator", "", None)
    assert found[0] == "orchestrator step 3 is recorded before step 2"


@pytest.mark.supports("test_ty_approves_the_plan_and_starts_the_work_resting_on_it")
def test_a_sign_off_waiting_and_a_typed_commands_steps_left_out_names_them(tmp_path: Any) -> None:
    """Given: a run whose plan waits, and whose orchestrator recorded each step of up, step 1 of
    ty alone, and each step of its part.
    When: the end of its turn is checked.
    Then: it names step 2 of ty."""
    run = orchestrator_turn(tmp_path, *UP, ("ty", 1), *PART)
    assert check.check(d.RN, run.worktree, "orchestrator", "", None) == (
        "ty step 2 isn't recorded after step 1",
    )


@pytest.mark.supports("test_the_goal_is_put_to_the_user_once_the_design_tree_holds_it")
def test_a_sign_off_waiting_and_the_parts_last_step_left_out_names_it(tmp_path: Any) -> None:
    """Given: a run whose plan waits, and whose orchestrator recorded each step of up and each step
    of its part but its last, which has work only where /rn:up alone finds no run left.
    When: the end of its turn is checked.
    Then: it names the last step, as each turn records a step with no work at the place that
    shows none."""
    run = orchestrator_turn(tmp_path, *UP, *PART[:-1])
    last = PART[-1][1]
    assert check.check(d.RN, run.worktree, "orchestrator", "", None) == (
        f"orchestrator step {last} isn't recorded after step {last - 1}",
    )


# The orchestrator's turns after one: a turn passed, or a turn whose check failed; and the next
# turn, or the same turn again, taking its part from step 1, as each turn of a run does.


def ended(run: Any) -> tuple[str, ...]:
    """What rn's check finds the end of the orchestrator's turn lacks."""
    return check.check(d.RN, run.worktree, "orchestrator", "", None)


def recorded(run: Any, *entries: tuple[str, int]) -> None:
    """The orchestrator records the entries, each a step of a prompt, after what it recorded, or
    records nothing where none is given."""
    if not entries:
        return
    form.add(
        os.path.join(run.worktree, records.orchestrator_record(run)),
        *(Entry(of, n, None, "a.py:1") for of, n in entries),
    )


@pytest.mark.supports("test_the_goal_is_put_to_the_user_once_the_design_tree_holds_it")
def test_a_turn_passed_and_the_next_taking_its_part_from_step_1_lacks_nothing(
    tmp_path: Any,
) -> None:
    """Given: a run whose plan waits, and whose orchestrator's turn of up, each step of up and of
    its part recorded, rn's check passed.
    When: the next turn, which typed no command, records each step of the part from step 1, and
    its end is checked.
    Then: it lacks nothing, as a turn is held to the latest pass from step 1 of its part."""
    run = orchestrator_turn(tmp_path, *UP, *PART)
    assert ended(run) == ()
    recorded(run, *PART)
    assert ended(run) == ()


@pytest.mark.supports("test_a_turn_putting_the_plan_up_with_a_step_of_the_part_left_out_is_held")
def test_a_turn_whose_check_failed_and_that_takes_its_part_again_from_step_1_lacks_nothing(
    tmp_path: Any,
) -> None:
    """Given: a run whose plan waits, and whose orchestrator's turn of up, each step of up and of
    its part but step 2 recorded, rn's check held.
    When: the same turn records each step of the part again from step 1, and its end is checked
    again.
    Then: it lacks nothing, as the latest pass of the part from step 1 holds each step."""
    run = orchestrator_turn(tmp_path, *UP, *[e for e in PART if e[1] != 2])
    assert ended(run) != ()
    recorded(run, *PART)
    assert ended(run) == ()


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
def test_an_end_whose_record_is_out_of_form_is_refused(tmp_path: Any) -> None:
    """Given: a generator whose record holds step 0.
    When: its end is checked.
    Then: it's refused."""
    run, record = generator_ended(tmp_path)
    d.write_json(
        os.path.join(run.worktree, record),
        {"entries": [{"of": "generator", "step": 0, "where": "a.py:1"}]},
    )
    with pytest.raises(Wrong):
        check.check(d.RN, run.worktree, "generator", "done", record)


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
@pytest.mark.parametrize("where", ["with no record", "outside a run's worktree"])
def test_a_roles_end_with_no_record_or_outside_a_run_is_refused(tmp_path: Any, where: str) -> None:
    """Given: a generator that recorded each step and practice, and wrote its Made.
    When: its end is checked with no record, or from the repository's root, which lies in no run's
    worktree.
    Then: it's refused."""
    run, record = generator_ended(tmp_path)
    root = os.path.dirname(os.path.dirname(os.path.dirname(run.worktree)))
    cwd, named = (run.worktree, None) if where == "with no record" else (root, record)
    with pytest.raises(Wrong):
        check.check(d.RN, cwd, "generator", "done", named)


@pytest.mark.supports("test_record_py_refuses_an_entry_out_of_its_form")
def test_add_records_an_entry_and_refuses_one_out_of_form(tmp_path: Any) -> None:
    """Given: no record at the path.
    When: record.py add runs with steps 3 and 4 of the generator at lines of a.py, then with the
    practice X1.
    Then: the first gives 0 and the record holds both steps, and the second gives 1 with what's
    wrong."""
    path = os.path.join(tmp_path, "record.json")
    four_lines(tmp_path)
    given = "3=a.py:1 4=a.py:2-4"
    assert main(["add", path, "generator", given], str(tmp_path), d.RN)[0] == 0
    entries = (Entry("generator", 3, None, "a.py:1"), Entry("generator", 4, None, "a.py:2-4"))
    assert form.read(path).entries == entries
    code, out, err = main(["add", path, "code", "X1=a.py:1"], str(tmp_path), d.RN)
    assert (code, out) == (1, "") and err


@pytest.mark.supports("test_record_py_refuses_an_entry_out_of_its_form")
@pytest.mark.parametrize("where", ["gone.py:1", "a.py:5", "a.py:2-5", ".:1"])
def test_add_refuses_a_place_with_no_file_or_past_its_end(tmp_path: Any, where: str) -> None:
    """Given: a.py of 4 lines, and no record at the path.
    When: record.py add runs with step 1 at a file that isn't there, past a.py's end, through it,
    or at a folder.
    Then: it gives 1 with what's wrong, and makes no record."""
    path = os.path.join(tmp_path, "record.json")
    four_lines(tmp_path)
    code, out, err = main(["add", path, "generator", f"1={where}"], str(tmp_path), d.RN)
    assert (code, out) == (1, "") and err
    assert not os.path.exists(path)


@pytest.mark.supports("test_an_end_whose_record_lacks_a_practice_is_held_with_it")
def test_check_gives_0_or_1_with_each_thing_lacking_on_a_line(tmp_path: Any) -> None:
    """Given: a generator that recorded each step and practice, and one that left out code's
    N4.1.
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
