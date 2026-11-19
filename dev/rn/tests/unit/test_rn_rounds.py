"""The unit cases of the Rounds, the course, and the Cut: tree/'s rounds.each and rounds.path, one
for each class of what they read, course.due, one for each transition of a deliverable's rounds
that the use brings about, from the starts of its Rounds and those that run, and cut.write, one for
each class of start due."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
from fault import Wrong
from repo_files import write_files
from rn_bench import COMMAND, GUIDE, RUN, plan
from tree import course, cut, rounds
from tree.course import Due
from tree.rounds import Start

CODE_GROUPS = {"C1": ["N1", "N2", "N3"], "C2": ["N4", "N5", "N6", "N7"], "C3": ["N8"]}


def decisions(tree: dict[str, Any]) -> list[dict[str, Any]]:
    """Each decision of the command, as the generator's Cut holds it."""
    return [
        {"path": COMMAND, "condition": c["id"], **d}
        for c in tree["deliverables"][0]["necessary_conditions"]
        for d in c["decisions"]
    ]


def generator(number: int, practice: str, result: Any, tree: dict[str, Any] | None = None) -> Start:
    """The generator's start of the command's round, by the best practice, with its result."""
    held = {"role": "generator", "best_practice": practice, "decisions": decisions(tree or plan())}
    return Start(number, "generator", "", held, result)


def evaluators(number: int, more: dict[str, str], groups: Any = CODE_GROUPS) -> list[Start]:
    """One evaluator's start of the round for each group, more on each condition named."""
    return [
        Start(
            number,
            "evaluator",
            group,
            {"role": "evaluator", "group": group, "conditions": conditions},
            {
                "good": [{"condition": c, "lines": ["x:1"]} for c in conditions if c not in more],
                "more": [{"condition": c, "good_when": more[c]} for c in conditions if c in more],
            },
        )
        for group, conditions in groups.items()
    ]


MADE = {"result": "made", "carried_out": []}
SHORT = {"N2": "The team sees a wrong line named"}


def changed() -> dict[str, Any]:
    """The plan with a decision under the command's N2, from a finding."""
    tree = plan()
    tree["deliverables"][0]["necessary_conditions"][1]["decisions"].append(
        {"about": "A wrong line", "decided": "named by its number", "by": "reasoning"}
    )
    return tree


def roles(due: Any) -> list[tuple[str, str, str, int]]:
    """Each start due by its role, group, best practice, and round."""
    return [(d.role, d.group, d.best_practice, d.round) for d in due]


@pytest.mark.supports("test_the_first_deliverable_of_the_work_gets_a_generator_with_its_cut")
def test_no_round_yet_gives_the_first_deliverables_generator_by_its_kind():
    """Given the plan and no Round
    When course.due gives the starts due
    Then the command's generator of round 1 by code is due"""
    assert roles(course.due(plan(), [], [])) == [("generator", "", "code", 1)]


@pytest.mark.supports("test_one_generator_runs_for_each_deliverable")
def test_a_generator_running_gives_none():
    """Given the command's generator of round 1 running, with no result
    When course.due gives the starts due
    Then none is due"""
    running = [Due(COMMAND, "generator", "", "code", 1)]
    assert roles(course.due(plan(), [generator(1, "code", None)], running)) == []


@pytest.mark.supports("test_a_generators_point_starts_no_evaluator")
def test_a_generators_point_gives_none():
    """Given the command's generator ended with a point
    When course.due gives the starts due
    Then none is due"""
    point = {"result": "point", "point": "EUR alone?"}
    assert roles(course.due(plan(), [generator(1, "code", point)], [])) == []


@pytest.mark.supports("test_a_deliverable_made_gets_one_evaluator_for_each_group_of_its_conditions")
def test_a_generator_made_gives_one_evaluator_for_each_group():
    """Given the command's generator of round 1 made
    When course.due gives the starts due
    Then one evaluator of round 1 by code is due for each group of code"""
    due = course.due(plan(), [generator(1, "code", MADE)], [])
    assert roles(due) == [("evaluator", g, "code", 1) for g in CODE_GROUPS]


@pytest.mark.supports("test_a_deliverable_made_gets_one_evaluator_for_each_group_of_its_conditions")
def test_evaluators_running_leave_only_the_groups_none_runs():
    """Given the command made, and the evaluator of C1 running
    When course.due gives the starts due
    Then the evaluators of C2 and C3 are due"""
    running = [Due(COMMAND, "evaluator", "C1", "code", 1)]
    due = course.due(plan(), [generator(1, "code", MADE)], running)
    assert [d.group for d in due] == ["C2", "C3"]


@pytest.mark.supports("test_a_finding_taken_into_its_decision_gets_the_next_round_of_content")
def test_findings_with_their_decision_changed_give_the_next_round_of_content():
    """Given round 1 judged with more on N2, and a decision under N2 added since its Cut
    When course.due gives the starts due
    Then the generator of round 2 by code is due"""
    starts = [generator(1, "code", MADE), *evaluators(1, SHORT)]
    assert roles(course.due(changed(), starts, [])) == [("generator", "", "code", 2)]


@pytest.mark.supports("test_a_finding_taken_into_its_decision_gets_the_next_round_of_content")
def test_findings_with_no_decision_changed_give_none():
    """Given round 1 judged with more on N2, and no decision changed since its Cut
    When course.due gives the starts due
    Then none is due, as the findings wait for the orchestrator"""
    starts = [generator(1, "code", MADE), *evaluators(1, SHORT)]
    assert roles(course.due(plan(), starts, [])) == []


@pytest.mark.supports("test_a_later_round_judges_only_the_groups_whose_decisions_changed")
def test_a_later_round_of_content_gives_evaluators_of_the_changed_groups_alone():
    """Given round 2's generator made, after a decision under N2 changed
    When course.due gives the starts due
    Then only the evaluator of C1 is due"""
    tree = changed()
    starts = [generator(1, "code", MADE), *evaluators(1, SHORT), generator(2, "code", MADE, tree)]
    assert roles(course.due(tree, starts, [])) == [("evaluator", "C1", "code", 2)]


@pytest.mark.supports("test_content_judged_good_gets_a_round_of_refactoring")
def test_content_judged_good_gives_a_round_of_refactoring():
    """Given round 1 judged good on each condition
    When course.due gives the starts due
    Then the generator of round 2 by refactor-code is due"""
    starts = [generator(1, "code", MADE), *evaluators(1, {})]
    assert roles(course.due(plan(), starts, [])) == [("generator", "", "refactor-code", 2)]


@pytest.mark.supports("test_content_judged_good_gets_a_round_of_refactoring")
def test_a_guide_judged_good_gives_a_round_of_refactor_doc():
    """Given the command done, and the guide's round 1 judged good
    When course.due gives the starts due
    Then the guide's generator of round 2 by refactor-doc is due"""
    tree = plan()
    tree["deliverables"][0] = {"name": "c", "path": COMMAND, "kind": "code", "status": "done"}
    tree["work"] = tree["work"][1:]
    groups = {
        "C1": ["N1", "N2", "N3", "N4", "N5"],
        "C2": ["N6"],
        "C3": ["N7", "N8"],
        "C4": ["N9", "N10"],
    }
    held = {"role": "generator", "best_practice": "readme", "decisions": []}
    starts = [Start(1, "generator", "", held, MADE), *evaluators(1, {}, groups)]
    assert roles(course.due(tree, starts, [])) == [("generator", "", "refactor-doc", 2)]


@pytest.mark.supports("test_content_judged_good_gets_a_round_of_refactoring")
def test_a_round_of_refactoring_made_gives_each_group_of_the_refactor_best_practice():
    """Given round 2 by refactor-code made
    When course.due gives the starts due
    Then one evaluator by refactor-code is due for each group of refactor-code"""
    starts = [generator(1, "code", MADE), *evaluators(1, {}), generator(2, "refactor-code", MADE)]
    due = course.due(plan(), starts, [])
    assert roles(due) == [("evaluator", g, "refactor-code", 2) for g in ("C1", "C2", "C3")]


@pytest.mark.supports("test_findings_past_two_rounds_of_content_start_no_third")
def test_two_rounds_of_content_short_give_none():
    """Given two rounds of content, each judged with more on N2, a decision changed after each
    When course.due gives the starts due
    Then none is due, as the limit leaves each finding to the orchestrator"""
    tree = changed()
    tree["deliverables"][0]["necessary_conditions"][1]["decisions"].append(
        {"about": "The row", "decided": "counted from 1", "by": "reasoning"}
    )
    starts = [
        generator(1, "code", MADE),
        *evaluators(1, SHORT),
        generator(2, "code", MADE, changed()),
        *evaluators(2, SHORT, {"C1": CODE_GROUPS["C1"]}),
    ]
    assert roles(course.due(tree, starts, [])) == []


@pytest.mark.supports("test_findings_past_two_rounds_of_content_start_no_third")
def test_two_rounds_of_refactoring_short_give_none():
    """Given content judged good, and two rounds of refactoring, each judged with more on N2
    When course.due gives the starts due
    Then none is due"""
    refactoring = {"C1": ["N1"], "C2": ["N2", "N3", "N4", "N5", "N6"], "C3": ["N7", "N8"]}
    starts = [
        generator(1, "code", MADE),
        *evaluators(1, {}),
        generator(2, "refactor-code", MADE),
        *evaluators(2, SHORT, refactoring),
        generator(3, "refactor-code", MADE, changed()),
        *evaluators(3, SHORT, {"C2": refactoring["C2"]}),
    ]
    assert roles(course.due(changed(), starts, [])) == []


@pytest.mark.supports("test_the_first_deliverable_of_the_work_gets_a_generator_with_its_cut")
def test_the_guide_waits_while_the_command_isnt_done():
    """Given the plan with the command's rounds left past the limit
    When course.due gives the starts due
    Then no start of the guide is due, as its input isn't done"""
    starts = [generator(1, "code", MADE), *evaluators(1, {}), generator(2, "refactor-code", MADE)]
    starts += evaluators(
        2, {}, {"C1": ["N1"], "C2": ["N2", "N3", "N4", "N5", "N6"], "C3": ["N7", "N8"]}
    )
    assert all(d.deliverable == COMMAND for d in course.due(plan(), starts, []))


def run_folder(tmp: str, files: dict[str, Any]) -> str:
    """The run's folder with each file of its Rounds, as JSON."""
    run = os.path.join(tmp, RUN)
    write_files(run, {p: v if isinstance(v, str) else json.dumps(v) for p, v in files.items()})
    return run


@pytest.mark.supports("test_a_pick_up_in_a_new_conversation_gets_the_results_kept_in_their_order")
def test_each_gives_none_for_a_run_with_no_round(tmp_path: Any):
    """Given the run's folder with no rounds/
    When rounds.each reads it
    Then it gives no start"""
    assert rounds.each(run_folder(str(tmp_path), {"design-tree.json": plan()})) == []


@pytest.mark.supports("test_a_pick_up_in_a_new_conversation_gets_the_results_kept_in_their_order")
def test_each_gives_each_start_in_the_order_of_its_rounds(tmp_path: Any):
    """Given round 1's generator and evaluator of C1 with their results, and round 2's generator
    with none, and round 10's generator
    When rounds.each reads them
    Then it gives round 1's generator, its evaluator, round 2's generator with no result, and round
    10's, in that order"""
    cut_ = {"role": "generator"}
    run = run_folder(
        str(tmp_path),
        {
            "rounds/1/generator.cut.json": cut_,
            "rounds/1/generator.json": MADE,
            "rounds/1/evaluator-C1.cut.json": {"role": "evaluator"},
            "rounds/1/evaluator-C1.json": {"good": [], "more": []},
            "rounds/2/generator.cut.json": cut_,
            "rounds/10/generator.cut.json": cut_,
        },
    )
    got = [(s.round, s.role, s.group, s.result is None) for s in rounds.each(run)]
    assert got == [
        (1, "generator", "", False),
        (1, "evaluator", "C1", False),
        (2, "generator", "", True),
        (10, "generator", "", True),
    ]


@pytest.mark.supports("test_a_pick_up_in_a_new_conversation_gets_the_results_kept_in_their_order")
def test_each_refuses_a_cut_that_isnt_json_naming_it(tmp_path: Any):
    """Given round 1's generator's Cut that isn't JSON
    When rounds.each reads it
    Then it refuses with Wrong, naming the file"""
    run = run_folder(str(tmp_path), {"rounds/1/generator.cut.json": "{"})
    with pytest.raises(Wrong) as refused:
        rounds.each(run)
    assert "rounds/1/generator.cut.json" in str(refused.value)


@pytest.mark.supports("test_a_role_stopped_starts_again_from_its_kept_cut")
@pytest.mark.parametrize(
    ("role", "group", "name"),
    [("generator", "", "generator.cut.json"), ("evaluator", "C2", "evaluator-C2.cut.json")],
)
def test_path_names_the_cut_of_a_start(role: str, group: str, name: str):
    """Given a start of round 3, the generator's or the evaluator's of C2
    When rounds.path names its Cut
    Then it gives rounds/3/ and the file of its role and group"""
    start = Start(3, role, group, {}, None)
    assert rounds.path(RUN, start) == f"{RUN}/rounds/3/{name}"


@pytest.mark.supports("test_each_cut_holds_its_role_deliverable_best_practice_and_goal")
def test_write_gives_the_generator_its_deliverable_best_practice_goal_and_decisions(tmp_path: Any):
    """Given the plan, and the command's generator of round 1 due
    When cut.write writes its Cut
    Then the Cut at rounds/1/generator.cut.json names the generator, the command, code, the goal,
    and each decision of the command"""
    run = run_folder(str(tmp_path), {"design-tree.json": plan()})
    path = cut.write(run, plan(), Due(COMMAND, "generator", "", "code", 1))
    with open(path, encoding="utf-8") as f:
        written = json.load(f)
    assert path.endswith(f"{RUN}/rounds/1/generator.cut.json")
    assert (written["role"], written["deliverable"]["path"]) == ("generator", COMMAND)
    assert (written["best_practice"], written["goal"]) == ("code", plan()["goal"]["decided"])
    assert written["decisions"] == decisions(plan())


@pytest.mark.supports("test_a_generator_starts_with_only_the_decisions_of_its_deliverable")
def test_write_gives_the_generator_the_decisions_of_an_input_node_with_no_file(tmp_path: Any):
    """Given the plan with a node of the product vision with no file, a decision under it, as the
    guide's input, and a decision under the guide
    When cut.write writes the guide's generator's Cut, the command done
    Then the Cut holds the guide's decisions and the node's, and none of another node"""
    tree = plan()
    vision = {
        "name": "The accounting team's aim",
        "path": "docs/team-vision.md",
        "kind": "product-vision",
        "status": "done",
        "necessary_conditions": [
            {
                "id": "N1",
                "good": True,
                "decisions": [{"about": "Who", "decided": "the team", "by": "user"}],
            }
        ],
    }
    tree["deliverables"][0] = {"name": "c", "path": COMMAND, "kind": "code", "status": "done"}
    tree["deliverables"].append(vision)
    tree["deliverables"][1]["inputs"] = ["docs/team-vision.md", COMMAND]
    tree["deliverables"][1]["necessary_conditions"][0]["decisions"].append(
        {"about": "The steps", "decided": "five", "by": "reasoning"}
    )
    tree["work"] = tree["work"][1:]
    run = run_folder(str(tmp_path), {"design-tree.json": tree})
    path = cut.write(run, tree, Due(GUIDE, "generator", "", "readme", 1))
    with open(path, encoding="utf-8") as f:
        held = {(d["path"], d["about"]) for d in json.load(f)["decisions"]}
    assert held == {(GUIDE, "The steps"), ("docs/team-vision.md", "Who")}


@pytest.mark.supports("test_an_evaluator_starts_with_only_what_the_deliverables_people_have")
def test_write_gives_an_evaluator_its_group_and_the_conditions_due_and_no_decision(tmp_path: Any):
    """Given the plan, and the command's evaluator of C2 of round 1 due
    When cut.write writes its Cut
    Then the Cut at rounds/1/evaluator-C2.cut.json names C2 and N4 to N7, and no decision"""
    run = run_folder(str(tmp_path), {"design-tree.json": plan()})
    path = cut.write(run, plan(), Due(COMMAND, "evaluator", "C2", "code", 1))
    with open(path, encoding="utf-8") as f:
        written = json.load(f)
    assert path.endswith(f"{RUN}/rounds/1/evaluator-C2.cut.json")
    assert (written["group"], written["conditions"]) == ("C2", CODE_GROUPS["C2"])
    assert "decisions" not in written


@pytest.mark.supports("test_each_cut_holds_its_role_deliverable_best_practice_and_goal")
@pytest.mark.parametrize(
    "due",
    [Due("docs/faq.md", "generator", "", "code", 1), Due(COMMAND, "evaluator", "C9", "code", 1)],
    ids=["no such deliverable", "no such group"],
)
def test_write_refuses_a_start_that_the_tree_doesnt_hold(tmp_path: Any, due: Due):
    """Given the plan, and a start of a deliverable or a group that it doesn't hold
    When cut.write writes its Cut
    Then it refuses with Wrong, naming it"""
    run = run_folder(str(tmp_path), {"design-tree.json": plan()})
    with pytest.raises(Wrong) as refused:
        cut.write(run, plan(), due)
    assert (due.group or due.deliverable) in str(refused.value)
