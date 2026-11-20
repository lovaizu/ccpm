"""The unit cases of the Rounds, the course, and the Cut: tree/'s rounds.each, rounds.folder,
rounds.path, and rounds.fresh, one for each class of what they read; course.groups and
course.decisions, one for each class of the best practice and the design tree they read;
course.due, one for each transition of a deliverable's rounds that the use brings about, from the
starts of its Rounds and those that run, with several deliverables, several evaluators, and several
Rounds among them, as rn's use runs one generator and several evaluators a Round over several
Rounds and deliverables; and cut.write, one for each class of start due. Each Then names the whole
of what the interface gives: each start due whole, each Start whole, and each Cut whole."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
from fault import Wrong
from repo_files import write_files
from rn_bench import COMMAND, GUIDE, RUN, conditions, plan, vision
from tree import course, cut, rounds
from tree.course import Due
from tree.rounds import Start

# The groups of each best practice's conditions that the cases' Rounds work by.
CODE_GROUPS = {"C1": ["N1", "N2", "N3"], "C2": ["N4", "N5", "N6", "N7"], "C3": ["N8"]}
README_GROUPS = {
    "C1": ["N1", "N2", "N3", "N4", "N5"],
    "C2": ["N6"],
    "C3": ["N7", "N8"],
    "C4": ["N9", "N10"],
}
REFACTORING = {"C1": ["N1"], "C2": ["N2", "N3", "N4", "N5", "N6"], "C3": ["N7", "N8"]}
LIGHT_GROUPS = {"C1": ["N1", "N2", "N3", "N4"]}
GOAL = plan()["goal"]["decided"]


def decisions(tree: dict[str, Any]) -> list[dict[str, Any]]:
    """Each decision of the command, as the generator's Cut holds it."""
    return [
        {"path": COMMAND, "condition": c["id"], **d}
        for c in tree["deliverables"][0]["necessary_conditions"]
        for d in c["decisions"]
    ]


def generator(number: int, practice: str, result: Any, tree: dict[str, Any] | None = None) -> Start:
    """The generator's start of the command's round, by the best practice, with its result."""
    held = {
        "role": "generator",
        "deliverable": {"path": COMMAND},
        "best_practice": practice,
        "decisions": decisions(tree or plan()),
    }
    return Start(number, "generator", "", held, result)


def guide_generator(number: int, practice: str, result: Any, tree: dict[str, Any]) -> Start:
    """The guide's generator's start of the round, by the best practice, with its result."""
    held = {
        "role": "generator",
        "deliverable": {"path": GUIDE},
        "best_practice": practice,
        "decisions": course.decisions(tree, GUIDE),
    }
    return Start(number, "generator", "", held, result)


def evaluators(
    number: int,
    more: dict[str, str],
    groups: Any = CODE_GROUPS,
    path: str = COMMAND,
    practice: str = "code",
) -> list[Start]:
    """One evaluator's start of the round for each group, more on each condition named."""
    return [
        Start(
            number,
            "evaluator",
            group,
            {
                "role": "evaluator",
                "deliverable": {"path": path},
                "best_practice": practice,
                "group": group,
                "conditions": conditions,
            },
            {
                "good": [{"condition": c, "lines": ["x:1"]} for c in conditions if c not in more],
                "more": [{"condition": c, "good_when": more[c]} for c in conditions if c in more],
            },
        )
        for group, conditions in groups.items()
    ]


def gen(number: int, practice: str = "code", path: str = COMMAND) -> Due:
    """The generator due of the deliverable's round, by the best practice."""
    return Due(path, "generator", "", practice, number)


def evs(number: int, groups: Any = CODE_GROUPS, practice: str = "code", path: str = COMMAND):
    """One evaluator due of the deliverable's round for each group, in the groups' order."""
    return [Due(path, "evaluator", g, practice, number) for g in groups]


MADE = {"result": "made", "carried_out": []}
SHORT = {"N2": "The team sees a wrong line named"}
POINT = {"result": "point", "point": "EUR alone?"}


def changed(
    tree: dict[str, Any] | None = None, about: str = "A wrong line", by: str = "reasoning"
) -> dict[str, Any]:
    """The plan, or the tree given, with a decision about the point under the command's N2, from a
    finding, settled by whoever is given."""
    tree = tree or plan()
    tree["deliverables"][0]["necessary_conditions"][1]["decisions"].append(
        {"about": about, "decided": "named by its number", "by": by}
    )
    return tree


def light(done: bool = False) -> dict[str, Any]:
    """The plan with the command of the kind light, with that kind's conditions, its check decided
    under N1, and no input, or, where `done`, signed off and out of the work."""
    tree = plan()
    command = tree["deliverables"][0]
    command.update(kind="light", inputs=[], necessary_conditions=conditions("light"))
    check = {"about": "The check", "decided": "python3 -m invoicer runs", "by": "user"}
    command["necessary_conditions"][0]["decisions"] = [check]
    if done:
        command["status"] = "done"
        tree["work"] = tree["work"][1:]
    return tree


def side_by_side() -> dict[str, Any]:
    """The plan in which the guide rests on the product vision alone, so that both deliverables
    can be made at once."""
    tree = plan()
    tree["deliverables"][1]["inputs"] = ["docs/product-vision.md"]
    return tree


def due(tree: dict[str, Any], starts: list[Start], running: list[Due] | None = None) -> list[Due]:
    """Each start that course.due gives, as a list."""
    return list(course.due(tree, starts, running or []))


@pytest.mark.supports("test_a_deliverable_made_gets_one_evaluator_for_each_group_of_its_conditions")
def test_groups_give_each_group_of_a_best_practice_with_its_conditions_in_order():
    """Given rn's best practices of code and of refactor-code
    When course.groups reads each
    Then it gives each group by its ID, with each condition it bundles, both in the best
    practice's order"""
    assert [(g, list(c)) for g, c in course.groups("code").items()] == list(CODE_GROUPS.items())
    got = [(g, list(c)) for g, c in course.groups("refactor-code").items()]
    assert got == list(REFACTORING.items())


@pytest.mark.supports("test_a_deliverable_made_gets_one_evaluator_for_each_group_of_its_conditions")
def test_groups_of_no_best_practice_of_rns_refuse_with_os_error():
    """Given a name that no best practice of rn's has, such as code's near match cod
    When course.groups reads it
    Then it refuses with OSError"""
    with pytest.raises(OSError):
        course.groups("cod")


@pytest.mark.supports("test_a_generator_starts_with_only_the_decisions_of_its_deliverable")
def test_decisions_give_none_for_a_node_with_no_decision_and_no_input_node():
    """Given the plan with each decision of the command taken out, and its inputs files alone
    When course.decisions gives the command's
    Then it gives none"""
    tree = plan()
    for condition in tree["deliverables"][0]["necessary_conditions"]:
        condition["decisions"] = []
    assert course.decisions(tree, COMMAND) == []


@pytest.mark.supports("test_a_generator_starts_with_only_the_decisions_of_its_deliverable")
def test_decisions_give_the_nodes_own_then_each_input_nodes_by_path_and_condition_in_order():
    """Given the plan with a decision under the command's N2 beside the two under its N1, a node
    of the product vision with no file holding a decision, and the guide resting on that node and
    the command, with a decision of its own under N3, and an input that is a file
    When course.decisions gives the guide's
    Then it gives the guide's decision, then each of the command's in the order of its
    conditions, then the vision's, each with its node's path and its condition, and none of the
    file"""
    tree = changed()
    tree["deliverables"].append(vision(True, [{"about": "Who", "decided": "the team"}]))
    tree["deliverables"][1]["inputs"] = ["docs/product-vision.md", COMMAND, "docs/team-vision.md"]
    steps = {"about": "The steps", "decided": "five", "by": "reasoning"}
    tree["deliverables"][1]["necessary_conditions"][2]["decisions"].append(steps)
    command = tree["deliverables"][0]["necessary_conditions"]
    assert course.decisions(tree, GUIDE) == [
        {"path": GUIDE, "condition": "N3", **steps},
        *({"path": COMMAND, "condition": "N1", **d} for d in command[0]["decisions"]),
        {"path": COMMAND, "condition": "N2", **command[1]["decisions"][0]},
        {"path": "docs/team-vision.md", "condition": "N1", "about": "Who", "decided": "the team"},
    ]


@pytest.mark.supports("test_a_generator_starts_with_only_the_decisions_of_its_deliverable")
def test_decisions_leave_out_an_input_node_done_that_keeps_one_line():
    """Given the plan with the command done, keeping one line, and the guide resting on it
    When course.decisions gives the guide's
    Then it gives none, as the command's file holds what its decisions made"""
    tree = plan()
    tree["deliverables"][0] = {"name": "c", "path": COMMAND, "kind": "code", "status": "done"}
    assert course.decisions(tree, GUIDE) == []


@pytest.mark.supports("test_the_first_deliverable_of_the_work_gets_a_generator_with_its_cut")
def test_no_round_yet_gives_the_first_deliverables_generator_by_its_kind():
    """Given the plan and no Round
    When course.due gives the starts due
    Then the command's generator of round 1 by code is due, and no start of the guide, which rests
    on the command"""
    assert due(plan(), []) == [gen(1)]


@pytest.mark.supports("test_a_generator_running_gets_no_second_start_of_its_deliverable")
def test_a_generator_running_gives_none():
    """Given the command's generator of round 1 running, with no result
    When course.due gives the starts due
    Then none is due"""
    running = [gen(1)]
    assert due(plan(), [generator(1, "code", None)], running) == []


@pytest.mark.supports("test_a_generators_point_passes_its_check_and_starts_no_evaluator")
def test_a_generators_point_gives_none():
    """Given the command's generator ended with a point
    When course.due gives the starts due
    Then none is due"""
    assert due(plan(), [generator(1, "code", POINT)]) == []


@pytest.mark.supports("test_a_point_answered_gets_the_generator_again")
def test_a_generators_point_answered_gives_the_next_round():
    """Given the command's generator ended with a point, and a decision of the command changed
    since its Cut, as the user's answer settles it
    When course.due gives the starts due
    Then the generator of round 2 by code is due"""
    assert due(changed(), [generator(1, "code", POINT)]) == [gen(2)]


@pytest.mark.supports("test_a_point_answered_gets_the_generator_again")
def test_a_point_of_a_round_of_refactoring_answered_gives_the_next_round_of_refactoring():
    """Given round 1 judged good, round 2's generator by refactor-code ended with a point, and a
    decision of the command changed since its Cut
    When course.due gives the starts due
    Then the generator of round 3 by refactor-code is due, as the point's Round works by it"""
    starts = [generator(1, "code", MADE), *evaluators(1, {}), generator(2, "refactor-code", POINT)]
    assert due(changed(), starts) == [gen(3, "refactor-code")]


@pytest.mark.supports("test_the_sign_off_of_the_pull_request_ends_the_run")
def test_no_work_left_gives_none():
    """Given the plan with each deliverable done and no work left
    When course.due gives the starts due
    Then none is due"""
    tree = plan()
    tree["work"] = []
    assert due(tree, []) == []


@pytest.mark.supports("test_a_point_first_in_the_work_starts_no_role_while_it_waits")
def test_a_point_first_in_the_work_gives_none():
    """Given the plan with a point of the command first in the work
    When course.due gives the starts due
    Then none is due, as the orchestrator settles it or puts it to the user"""
    tree = plan()
    tree["work"].insert(0, {"do": "decide", "path": COMMAND, "condition": "N1", "about": "x"})
    assert due(tree, []) == []


@pytest.mark.supports("test_a_point_first_in_the_work_starts_no_role_while_it_waits")
def test_a_point_of_another_deliverable_first_in_the_work_leaves_the_command_due():
    """Given the plan in which the guide rests on the product vision alone, with a point of the
    guide first in the work
    When course.due gives the starts due
    Then the command's generator of round 1 is due, and no start of the guide while its point
    waits"""
    tree = side_by_side()
    tree["work"].insert(0, {"do": "decide", "path": GUIDE, "condition": "N1", "about": "x"})
    assert due(tree, []) == [gen(1)]


@pytest.mark.supports("test_a_deliverable_made_gets_one_evaluator_for_each_group_of_its_conditions")
def test_a_generator_made_gives_one_evaluator_for_each_group():
    """Given the command's generator of round 1 made
    When course.due gives the starts due
    Then one evaluator of round 1 by code is due for each group of code, and no start of the
    guide"""
    assert due(plan(), [generator(1, "code", MADE)]) == evs(1)


@pytest.mark.supports("test_a_deliverable_made_gives_lane_its_evaluators_beside_those_that_run")
def test_evaluators_running_leave_only_the_groups_none_runs():
    """Given the command made, and the evaluators of C1 and C3 running
    When course.due gives the starts due
    Then the evaluator of C2 alone is due"""
    running = [Due(COMMAND, "evaluator", g, "code", 1) for g in ("C1", "C3")]
    assert due(plan(), [generator(1, "code", MADE)], running) == evs(1, ["C2"])


@pytest.mark.supports("test_a_deliverable_made_gives_lane_its_evaluators_beside_those_that_run")
def test_an_evaluator_of_another_deliverable_running_leaves_the_same_group_due():
    """Given the plan in which the guide rests on the product vision alone, the command's round 1
    made, the guide's round 2 made, and the guide's evaluator of C1 running
    When course.due gives the starts due
    Then each evaluator of the command's round 1 is due, its C1 among them, and each of the
    guide's round 2 but C1"""
    tree = side_by_side()
    starts = [generator(1, "code", MADE), guide_generator(2, "readme", MADE, tree)]
    running = [Due(GUIDE, "evaluator", "C1", "readme", 2)]
    assert due(tree, starts, running) == [
        *evs(1),
        *evs(2, ["C2", "C3", "C4"], "readme", GUIDE),
    ]


@pytest.mark.supports("test_a_generator_running_gets_no_second_start_of_its_deliverable")
def test_a_generator_of_another_deliverable_running_leaves_this_ones_generator_due():
    """Given the plan in which the guide rests on the product vision alone, and the guide's
    generator of round 1 running, with no result
    When course.due gives the starts due
    Then the command's generator of round 2 is due, and no second start of the guide"""
    tree = side_by_side()
    starts = [guide_generator(1, "readme", None, tree)]
    assert due(tree, starts, [gen(1, "readme", GUIDE)]) == [gen(2)]


@pytest.mark.supports("test_an_evaluator_stopped_starts_again_with_a_fresh_cut_beside_its_first")
def test_an_evaluator_stopped_is_due_again_beside_the_groups_none_answered():
    """Given the command made, the evaluator of C1 answered, and the evaluator of C2 stopped with
    no result, none running
    When course.due gives the starts due
    Then the evaluators of C2 and C3 of round 1 are due"""
    answered, stopped, _ = evaluators(1, {})
    stopped = Start(1, "evaluator", "C2", stopped.cut, None)
    assert due(plan(), [generator(1, "code", MADE), answered, stopped]) == evs(1, ["C2", "C3"])


@pytest.mark.supports("test_a_finding_taken_into_its_decision_gets_the_next_round_of_content")
def test_findings_with_their_decision_changed_give_the_next_round_of_content():
    """Given round 1 judged with more on N2, and a decision under N2 added since its Cut
    When course.due gives the starts due
    Then the generator of round 2 by code is due"""
    starts = [generator(1, "code", MADE), *evaluators(1, SHORT)]
    assert due(changed(), starts) == [gen(2)]


@pytest.mark.supports("test_a_finding_taken_into_its_decision_gets_the_next_round_of_content")
def test_findings_with_no_decision_changed_give_none():
    """Given round 1 judged with more on N2, and no decision changed since its Cut
    When course.due gives the starts due
    Then none is due, as the findings wait for the orchestrator"""
    starts = [generator(1, "code", MADE), *evaluators(1, SHORT)]
    assert due(plan(), starts) == []


@pytest.mark.supports("test_a_finding_taken_into_its_decision_gets_the_next_round_of_content")
def test_findings_of_an_earlier_round_count_for_nothing_once_the_latest_is_judged_good():
    """Given round 1 judged with more on N2, a decision under N2 added, and round 2 by code made
    and judged good by its one group due, C1
    When course.due gives the starts due
    Then the generator of round 3 by refactor-code is due, as only the latest Round's findings
    count"""
    tree = changed()
    starts = [
        generator(1, "code", MADE),
        *evaluators(1, SHORT),
        generator(2, "code", MADE, tree),
        *evaluators(2, {}, {"C1": CODE_GROUPS["C1"]}),
    ]
    assert due(tree, starts) == [gen(3, "refactor-code")]


@pytest.mark.supports("test_a_finding_the_people_would_never_meet_gets_a_round_of_refactoring")
def test_findings_the_orchestrator_holds_good_give_a_round_of_refactoring():
    """Given round 1 judged with more on N2, and N2 good in the design tree with no decision
    changed, as the orchestrator found that the people would never meet it
    When course.due gives the starts due
    Then the generator of round 2 by refactor-code is due"""
    tree = plan()
    tree["deliverables"][0]["necessary_conditions"][1]["good"] = True
    starts = [generator(1, "code", MADE), *evaluators(1, SHORT)]
    assert due(tree, starts) == [gen(2, "refactor-code")]


@pytest.mark.supports("test_a_finding_the_people_would_never_meet_gets_a_round_of_refactoring")
def test_findings_on_two_conditions_one_held_good_still_give_the_next_round_of_content():
    """Given round 1 judged with more on N2 and N5, N2 good in the design tree, and a decision
    under N5 added since
    When course.due gives the starts due
    Then the generator of round 2 by code is due, as N5 stays short"""
    tree = plan()
    conditions = tree["deliverables"][0]["necessary_conditions"]
    conditions[1]["good"] = True
    conditions[4]["decisions"].append({"about": "The layout", "decided": "a table", "by": "maker"})
    starts = [generator(1, "code", MADE), *evaluators(1, {**SHORT, "N5": "w"})]
    assert due(tree, starts) == [gen(2)]


@pytest.mark.supports("test_a_finding_the_people_would_never_meet_gets_a_round_of_refactoring")
def test_findings_of_refactoring_on_an_id_the_tree_holds_good_still_count():
    """Given round 1 judged good, round 2 by refactor-code judged with more on its N2, the
    command's N2 of code good in the design tree, and a decision added since
    When course.due gives the starts due
    Then the generator of round 3 by refactor-code is due, as the design tree holds the conditions
    of code, not of refactor-code"""
    tree = changed()
    tree["deliverables"][0]["necessary_conditions"][1]["good"] = True
    starts = [
        generator(1, "code", MADE),
        *evaluators(1, {}),
        generator(2, "refactor-code", MADE),
        *evaluators(2, SHORT, REFACTORING, practice="refactor-code"),
    ]
    assert due(tree, starts) == [gen(3, "refactor-code")]


@pytest.mark.supports("test_a_users_decision_past_the_limit_gets_a_third_round")
def test_a_users_change_past_the_limit_gives_a_round_of_content():
    """Given two rounds of content short, and then a decision by the user under N2
    When course.due gives the starts due
    Then the generator of round 3 by code is due"""
    tree = changed()
    tree["deliverables"][0]["necessary_conditions"][1]["decisions"].append(
        {"about": "The row", "decided": "counted from 1", "by": "user"}
    )
    starts = [
        generator(1, "code", MADE),
        *evaluators(1, SHORT),
        generator(2, "code", MADE, changed()),
        *evaluators(2, SHORT, {"C1": CODE_GROUPS["C1"]}),
    ]
    assert due(tree, starts) == [gen(3)]


@pytest.mark.supports("test_a_users_decision_past_the_limit_gets_a_third_round")
def test_a_users_change_past_the_limit_of_refactoring_gives_a_round_of_refactoring():
    """Given content judged good, two rounds of refactoring short, and then a decision by the user
    When course.due gives the starts due
    Then the generator of round 4 by refactor-code is due"""
    tree = changed(changed(), "The row", "user")
    starts = [
        generator(1, "code", MADE),
        *evaluators(1, {}),
        generator(2, "refactor-code", MADE),
        *evaluators(2, SHORT, REFACTORING, practice="refactor-code"),
        generator(3, "refactor-code", MADE, changed()),
        *evaluators(3, SHORT, REFACTORING, practice="refactor-code"),
    ]
    assert due(tree, starts) == [gen(4, "refactor-code")]


@pytest.mark.supports("test_a_later_round_judges_only_the_groups_whose_decisions_changed")
def test_a_later_round_after_an_inputs_change_gives_each_group():
    """Given the guide's round 1 short, and a decision of the command, its input, changed since
    When course.due gives the starts due after round 2 is made
    Then an evaluator of each group of readme is due"""
    tree = plan()
    tree["work"] = tree["work"][1:]
    first = guide_generator(1, "readme", MADE, tree)
    later = changed()
    later["work"] = later["work"][1:]
    second = guide_generator(2, "readme", MADE, later)
    starts = [first, *evaluators(1, {"N1": "x"}, README_GROUPS, GUIDE, "readme"), second]
    assert due(later, starts) == evs(2, README_GROUPS, "readme", GUIDE)


@pytest.mark.supports("test_a_later_round_judges_only_the_groups_whose_decisions_changed")
def test_a_later_round_of_content_gives_evaluators_of_the_changed_groups_alone():
    """Given round 2's generator made, after a decision under N2 changed
    When course.due gives the starts due
    Then only the evaluator of C1 is due"""
    tree = changed()
    starts = [generator(1, "code", MADE), *evaluators(1, SHORT), generator(2, "code", MADE, tree)]
    assert due(tree, starts) == evs(2, ["C1"])


@pytest.mark.supports("test_a_later_round_judges_only_the_groups_whose_decisions_changed")
def test_a_later_round_with_decisions_changed_in_two_groups_gives_both():
    """Given round 2's generator made, after decisions under N2 and N8 changed
    When course.due gives the starts due
    Then the evaluators of C1 and C3 are due, and not C2's"""
    tree = changed()
    tree["deliverables"][0]["necessary_conditions"][7]["decisions"].append(
        {"about": "The tests", "decided": "one per line kind", "by": "maker"}
    )
    starts = [generator(1, "code", MADE), *evaluators(1, SHORT), generator(2, "code", MADE, tree)]
    assert due(tree, starts) == evs(2, ["C1", "C3"])


@pytest.mark.supports("test_content_judged_good_gets_a_round_of_refactoring")
def test_content_judged_good_gives_a_round_of_refactoring():
    """Given round 1 judged good on each condition
    When course.due gives the starts due
    Then the generator of round 2 by refactor-code is due"""
    starts = [generator(1, "code", MADE), *evaluators(1, {})]
    assert due(plan(), starts) == [gen(2, "refactor-code")]


@pytest.mark.supports("test_content_judged_good_gets_a_round_of_refactoring")
def test_a_guide_judged_good_gives_a_round_of_refactor_doc():
    """Given the command done, and the guide's round 1 judged good
    When course.due gives the starts due
    Then the guide's generator of round 2 by refactor-doc is due"""
    tree = plan()
    tree["deliverables"][0] = {"name": "c", "path": COMMAND, "kind": "code", "status": "done"}
    tree["work"] = tree["work"][1:]
    starts = [
        guide_generator(1, "readme", MADE, tree),
        *evaluators(1, {}, README_GROUPS, GUIDE, "readme"),
    ]
    assert due(tree, starts) == [gen(2, "refactor-doc", GUIDE)]


@pytest.mark.supports("test_content_judged_good_gets_a_round_of_refactoring")
def test_a_round_of_refactoring_made_gives_each_group_of_the_refactor_best_practice():
    """Given round 2 by refactor-code made
    When course.due gives the starts due
    Then one evaluator of round 2 by refactor-code is due for each group of refactor-code"""
    starts = [generator(1, "code", MADE), *evaluators(1, {}), generator(2, "refactor-code", MADE)]
    assert due(plan(), starts) == evs(2, REFACTORING, "refactor-code")


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
    assert due(tree, starts) == []


@pytest.mark.supports("test_findings_past_two_rounds_of_content_start_no_third")
def test_two_rounds_of_refactoring_short_give_none():
    """Given content judged good, and two rounds of refactoring, each judged with more on N2, a
    decision changed after each by reasoning
    When course.due gives the starts due
    Then none is due"""
    starts = [
        generator(1, "code", MADE),
        *evaluators(1, {}),
        generator(2, "refactor-code", MADE),
        *evaluators(2, SHORT, REFACTORING, practice="refactor-code"),
        generator(3, "refactor-code", MADE, changed()),
        *evaluators(3, SHORT, REFACTORING, practice="refactor-code"),
    ]
    assert due(changed(changed(), "The row"), starts) == []


@pytest.mark.supports("test_findings_past_two_rounds_of_content_start_no_third")
def test_a_round_of_content_short_after_a_point_counts_one_round_of_content():
    """Given round 1's generator ended with a point, round 2 made and judged with more on N2, and
    a decision under N2 added since
    When course.due gives the starts due
    Then the generator of round 3 by code is due, as a point is no Round of content toward the
    limit"""
    answered = changed()
    second = changed(changed(), "The row")
    starts = [
        generator(1, "code", POINT),
        generator(2, "code", MADE, answered),
        *evaluators(2, SHORT),
    ]
    assert due(second, starts) == [gen(3)]


@pytest.mark.supports("test_the_first_deliverable_of_the_work_gets_a_generator_with_its_cut")
def test_the_guide_waits_while_the_command_isnt_done():
    """Given the plan with the command's refactoring judged good, the command not yet done
    When course.due gives the starts due
    Then none is due, as the guide's input isn't done"""
    starts = [generator(1, "code", MADE), *evaluators(1, {}), generator(2, "refactor-code", MADE)]
    starts += evaluators(2, {}, REFACTORING, practice="refactor-code")
    assert due(plan(), starts) == []


@pytest.mark.supports("test_a_generator_stopped_starts_again_with_a_fresh_cut_in_the_next_round")
def test_a_generator_that_didnt_end_gives_it_again_in_the_next_round():
    """Given the command's generator of round 1 cut with no result, none running, as a pause
    stopped it
    When course.due gives the starts due
    Then the command's generator of round 2 by code is due, as the start that didn't end counts
    for nothing but for the next Round's number"""
    assert due(plan(), [generator(1, "code", None)]) == [gen(2)]


@pytest.mark.supports("test_refactoring_judged_good_leaves_the_deliverable_for_its_sign_off")
def test_refactoring_judged_good_gives_none():
    """Given round 1 judged good, and round 2 by refactor-code judged good
    When course.due gives the starts due
    Then none is due, as the deliverable waits for the user's sign-off"""
    starts = [
        generator(1, "code", MADE),
        *evaluators(1, {}),
        generator(2, "refactor-code", MADE),
        *evaluators(2, {}, REFACTORING, practice="refactor-code"),
    ]
    assert due(plan(), starts) == []


@pytest.mark.supports("test_a_finding_taken_into_its_decision_gets_the_next_round_of_content")
def test_refactoring_short_with_its_decision_changed_gives_the_next_round_of_refactoring():
    """Given round 2 by refactor-code judged with more on N2, and a decision under N2 added since
    When course.due gives the starts due
    Then the generator of round 3 by refactor-code is due"""
    starts = [
        generator(1, "code", MADE),
        *evaluators(1, {}),
        generator(2, "refactor-code", MADE),
        *evaluators(2, SHORT, REFACTORING, practice="refactor-code"),
    ]
    assert due(changed(), starts) == [gen(3, "refactor-code")]


@pytest.mark.supports("test_refactoring_judged_good_leaves_the_deliverable_for_its_sign_off")
def test_a_light_deliverable_judged_good_gives_none():
    """Given the plan with the command of the kind light, its round 1 judged good on each condition
    When course.due gives the starts due
    Then none is due, as a light deliverable gets no Round of refactoring and the guide waits for
    the command, its input, to be done"""
    tree = light()
    starts = [generator(1, "light", MADE, tree), *evaluators(1, {}, LIGHT_GROUPS, practice="light")]
    assert due(tree, starts) == []


@pytest.mark.supports("test_refactoring_judged_good_leaves_the_deliverable_for_its_sign_off")
def test_a_light_deliverable_judged_good_and_done_gives_the_next_deliverables_generator():
    """Given the light command's round 1 judged good, and the command then signed off and out of
    the work
    When course.due gives the starts due
    Then the guide's generator of round 2 by readme is due alone"""
    tree = light(done=True)
    starts = [generator(1, "light", MADE, tree), *evaluators(1, {}, LIGHT_GROUPS, practice="light")]
    assert due(tree, starts) == [gen(2, "readme", GUIDE)]


@pytest.mark.supports("test_a_finding_taken_into_its_decision_gets_the_next_round_of_content")
def test_a_light_deliverable_short_with_its_decision_changed_gives_the_next_round_of_light():
    """Given the light command's round 1 judged with more on N2, and a decision under N2 added since
    When course.due gives the starts due
    Then the generator of round 2 by light is due"""
    tree = light()
    starts = [generator(1, "light", MADE, tree)]
    starts += evaluators(1, SHORT, LIGHT_GROUPS, practice="light")
    assert due(changed(light()), starts) == [gen(2, "light")]


@pytest.mark.supports("test_a_deliverable_made_gets_one_evaluator_for_each_group_of_its_conditions")
def test_a_light_deliverable_made_gives_one_evaluator_for_its_one_group():
    """Given the light command's round 1 made
    When course.due gives the starts due
    Then one evaluator of round 1 by light is due, for C1, the light best practice's one group"""
    tree = light()
    assert due(tree, [generator(1, "light", MADE, tree)]) == evs(1, LIGHT_GROUPS, "light")


@pytest.mark.supports("test_deliverables_that_rest_on_none_being_made_start_at_once")
def test_deliverables_that_rest_on_none_being_made_give_a_generator_each_in_rounds_of_their_own():
    """Given the plan in which the guide rests on the product vision alone, and no Round
    When course.due gives the starts due
    Then the command's generator of round 1 by code and the guide's of round 2 by readme are due"""
    assert due(side_by_side(), []) == [gen(1), gen(2, "readme", GUIDE)]


@pytest.mark.supports("test_deliverables_that_rest_on_none_being_made_start_at_once")
def test_a_deliverable_beside_one_being_judged_gets_its_generator_in_the_next_round():
    """Given the plan in which the guide rests on the product vision alone, and the command's
    round 1 made, the guide's generator running in round 2
    When course.due gives the starts due
    Then each evaluator of the command's round 1 is due, and no start of the guide"""
    tree = side_by_side()
    guide = guide_generator(2, "readme", None, tree)
    running = [gen(2, "readme", GUIDE)]
    assert due(tree, [generator(1, "code", MADE), guide], running) == evs(1)


@pytest.mark.supports("test_deliverables_that_rest_on_none_being_made_start_at_once")
def test_a_deliverable_with_no_round_beside_one_being_judged_gets_the_next_number():
    """Given the plan in which the guide rests on the product vision alone, and the command's
    round 1 made, the guide with no Round
    When course.due gives the starts due
    Then each evaluator of the command's round 1, and the guide's generator of round 2, are due"""
    assert due(side_by_side(), [generator(1, "code", MADE)]) == [
        *evs(1),
        gen(2, "readme", GUIDE),
    ]


@pytest.mark.supports("test_deliverables_that_rest_on_none_being_made_start_at_once")
def test_each_deliverables_course_reads_its_own_latest_round():
    """Given the plan in which the guide rests on the product vision alone, the command's round 1
    judged good, and the guide's round 2 made after it
    When course.due gives the starts due
    Then the command's generator of round 3 by refactor-code, and each evaluator of the guide's
    round 2 by readme, are due"""
    tree = side_by_side()
    starts = [
        generator(1, "code", MADE),
        guide_generator(2, "readme", MADE, tree),
        *evaluators(1, {}),
    ]
    assert due(tree, starts) == [gen(3, "refactor-code"), *evs(2, README_GROUPS, "readme", GUIDE)]


def unsettled() -> dict[str, Any]:
    """The plan with a point still open under the command's N3, which the design tree holds with
    no `by`."""
    tree = plan()
    tree["deliverables"][0]["necessary_conditions"][2]["decisions"].append(
        {"about": "The currency", "decided": None}
    )
    return tree


@pytest.mark.supports("test_a_finding_taken_into_its_decision_gets_the_next_round_of_content")
def test_findings_beside_a_point_still_open_with_no_decision_changed_give_none():
    """Given the plan with a point still open under N3, and round 1, cut from it, judged with more
    on N2, no decision changed since
    When course.due gives the starts due
    Then none is due"""
    tree = unsettled()
    starts = [generator(1, "code", MADE, tree), *evaluators(1, SHORT)]
    assert due(tree, starts) == []


@pytest.mark.supports("test_a_point_answered_gets_the_generator_again")
def test_a_point_still_open_in_the_cut_settled_since_gives_the_next_round():
    """Given the plan with a point still open under N3, round 1's generator, cut from it, ended
    with that point, and the point settled by the user since
    When course.due gives the starts due
    Then the generator of round 2 by code is due"""
    settled = plan()
    settled["deliverables"][0]["necessary_conditions"][2]["decisions"].append(
        {"about": "The currency", "decided": "EUR alone", "by": "user"}
    )
    assert due(settled, [generator(1, "code", POINT, unsettled())]) == [gen(2)]


def run_folder(tmp: str, files: dict[str, Any]) -> str:
    """The run's folder with each file of its Rounds, as JSON."""
    run = os.path.join(tmp, RUN)
    write_files(run, {p: v if isinstance(v, str) else json.dumps(v) for p, v in files.items()})
    return run


@pytest.mark.supports("test_a_pick_up_in_a_new_conversation_gives_lane_each_role_stopped_again")
def test_each_gives_none_for_a_run_with_no_round(tmp_path: Any):
    """Given the run's folder with no rounds/, and then with rounds/ empty
    When rounds.each reads it
    Then it gives no start each time"""
    run = run_folder(str(tmp_path), {"design-tree.json": plan()})
    assert rounds.each(run) == []
    os.makedirs(os.path.join(run, "rounds"))
    assert rounds.each(run) == []


@pytest.mark.supports("test_a_pick_up_in_a_new_conversation_gives_lane_each_role_stopped_again")
def test_each_gives_each_start_in_the_order_of_its_rounds(tmp_path: Any):
    """Given round 1's generator and evaluators of C2 and C1 with their results, and round 2's
    generator with none, and round 10's generator with its result
    When rounds.each reads them
    Then it gives round 1's generator, its evaluators of C1 and C2, round 2's generator, and round
    10's, each whole: its round, role, group, Cut, result, and slot"""
    cuts = {n: {"role": "generator", "n": n} for n in (1, 2, 10)}
    judged = {"C1": {"good": [], "more": [{"condition": "N1", "good_when": "w"}]}}
    judged["C2"] = {"good": [{"condition": "N4", "lines": ["x:1"]}], "more": []}
    point = {"result": "point", "point": "p"}
    run = run_folder(
        str(tmp_path),
        {
            "rounds/1/generator.cut.json": cuts[1],
            "rounds/1/generator.json": MADE,
            "rounds/1/evaluator-C2.cut.json": {"group": "C2"},
            "rounds/1/evaluator-C2.json": judged["C2"],
            "rounds/1/evaluator-C1.cut.json": {"group": "C1"},
            "rounds/1/evaluator-C1.json": judged["C1"],
            "rounds/2/generator.cut.json": cuts[2],
            "rounds/10/generator.cut.json": cuts[10],
            "rounds/10/generator.json": point,
        },
    )
    assert list(rounds.each(run)) == [
        Start(1, "generator", "", cuts[1], MADE),
        Start(1, "evaluator", "C1", {"group": "C1"}, judged["C1"]),
        Start(1, "evaluator", "C2", {"group": "C2"}, judged["C2"]),
        Start(2, "generator", "", cuts[2], None),
        Start(10, "generator", "", cuts[10], point),
    ]


@pytest.mark.supports("test_an_evaluator_stopped_starts_again_with_a_fresh_cut_beside_its_first")
def test_each_gives_later_starts_of_a_role_and_group_after_the_first_by_their_slot(tmp_path: Any):
    """Given round 1's evaluator of C1 in slots 1, 2, and 10, and its evaluator of C2, the result
    beside slot 2 alone
    When rounds.each reads them
    Then it gives C1's starts by slot, 1, 2, and 10, each with its result or None, then C2's"""
    judged = {"good": [], "more": []}
    run = run_folder(
        str(tmp_path),
        {
            "rounds/1/evaluator-C1.10.cut.json": {"n": 10},
            "rounds/1/evaluator-C1.2.cut.json": {"n": 2},
            "rounds/1/evaluator-C1.2.json": judged,
            "rounds/1/evaluator-C1.cut.json": {"n": 1},
            "rounds/1/evaluator-C2.cut.json": {"n": 1},
        },
    )
    assert list(rounds.each(run)) == [
        Start(1, "evaluator", "C1", {"n": 1}, None, 1),
        Start(1, "evaluator", "C1", {"n": 2}, judged, 2),
        Start(1, "evaluator", "C1", {"n": 10}, None, 10),
        Start(1, "evaluator", "C2", {"n": 1}, None, 1),
    ]


@pytest.mark.supports("test_a_generator_stopped_starts_again_with_a_fresh_cut_in_the_next_round")
def test_each_gives_a_later_slot_of_the_generator_before_the_evaluators(tmp_path: Any):
    """Given round 1's generator in slots 1 and 2, the result beside slot 2, and its evaluator of
    C1
    When rounds.each reads them
    Then it gives the generator's slot 1, then its slot 2 with its result, then the evaluator"""
    run = run_folder(
        str(tmp_path),
        {
            "rounds/1/generator.cut.json": {"n": 1},
            "rounds/1/generator.2.cut.json": {"n": 2},
            "rounds/1/generator.2.json": MADE,
            "rounds/1/evaluator-C1.cut.json": {"n": 3},
        },
    )
    assert list(rounds.each(run)) == [
        Start(1, "generator", "", {"n": 1}, None, 1),
        Start(1, "generator", "", {"n": 2}, MADE, 2),
        Start(1, "evaluator", "C1", {"n": 3}, None, 1),
    ]


@pytest.mark.supports("test_each_rounds_results_lie_beside_their_cuts")
def test_each_leaves_alone_what_is_no_round_and_a_result_with_no_cut(tmp_path: Any):
    """Given round 1's generator, a file and a folder in rounds/ whose names are no number, and in
    round 1 a result of C1 with no Cut beside it
    When rounds.each reads them
    Then it gives round 1's generator alone"""
    run = run_folder(
        str(tmp_path),
        {
            "rounds/1/generator.cut.json": {"n": 1},
            "rounds/1/evaluator-C1.json": {"good": [], "more": []},
            "rounds/notes.json": {},
            "rounds/old/generator.cut.json": {"n": 2},
        },
    )
    assert list(rounds.each(run)) == [Start(1, "generator", "", {"n": 1}, None)]


@pytest.mark.supports("test_a_pick_up_in_a_new_conversation_gives_lane_each_role_stopped_again")
@pytest.mark.parametrize(
    ("files", "named"),
    [
        ({"rounds/1/generator.cut.json": "{"}, "rounds/1/generator.cut.json"),
        (
            {"rounds/1/generator.cut.json": {"n": 1}, "rounds/1/generator.json": "{"},
            "rounds/1/generator.json",
        ),
    ],
    ids=["a Cut", "a result"],
)
def test_each_refuses_a_cut_or_a_result_that_isnt_json_naming_it(
    tmp_path: Any, files: dict[str, Any], named: str
):
    """Given round 1's generator's Cut that isn't JSON, or its Cut with a result that isn't JSON
    When rounds.each reads it
    Then it refuses with Wrong, naming the file"""
    run = run_folder(str(tmp_path), files)
    with pytest.raises(Wrong) as refused:
        rounds.each(run)
    assert named in str(refused.value)


@pytest.mark.supports("test_an_evaluator_stopped_starts_again_with_a_fresh_cut_beside_its_first")
@pytest.mark.parametrize(
    ("role", "group", "slot", "name"),
    [
        ("generator", "", 1, "generator.cut.json"),
        ("generator", "", 2, "generator.2.cut.json"),
        ("evaluator", "C2", 1, "evaluator-C2.cut.json"),
        ("evaluator", "C2", 2, "evaluator-C2.2.cut.json"),
    ],
    ids=["generator", "generator's later slot", "evaluator", "evaluator's later slot"],
)
def test_path_names_the_cut_of_a_start(role: str, group: str, slot: int, name: str):
    """Given a start of round 3, the generator's or the evaluator's of C2, in slot 1 or 2
    When rounds.path names its Cut
    Then it gives rounds/3/ and the file of its role and group, with the slot past the first"""
    start = Start(3, role, group, {}, None, slot)
    assert rounds.path(RUN, start) == f"{RUN}/rounds/3/{name}"


@pytest.mark.supports("test_an_evaluator_stopped_starts_again_with_a_fresh_cut_beside_its_first")
@pytest.mark.parametrize(("held", "slot"), [(0, ""), (1, ".2"), (2, ".3")])
def test_fresh_gives_the_first_slot_that_holds_no_cut(tmp_path: Any, held: int, slot: str):
    """Given round 1's evaluator of C1 with no Cut, one Cut, or Cuts in slots 1 and 2
    When rounds.fresh names a new Cut of the start
    Then it gives slot 1, 2, or 3, the first that holds none"""
    names = ["evaluator-C1.cut.json", "evaluator-C1.2.cut.json"][:held]
    run = run_folder(str(tmp_path), {f"rounds/1/{n}": {} for n in names})
    start = Start(1, "evaluator", "C1", {}, None)
    assert rounds.fresh(run, start) == f"{run}/rounds/1/evaluator-C1{slot}.cut.json"


@pytest.mark.supports("test_an_evaluator_stopped_starts_again_with_a_fresh_cut_beside_its_first")
def test_fresh_leaves_alone_the_cuts_of_another_group_round_or_role_and_the_slot_given(
    tmp_path: Any,
):
    """Given round 1's Cuts of the generator and the evaluator of C2, and round 2's Cut of the
    evaluator of C1, and a start of round 1's evaluator of C1 given in slot 3
    When rounds.fresh names a new Cut of the start
    Then it gives round 1's slot 1 of C1"""
    names = ["1/generator", "1/evaluator-C2", "2/evaluator-C1"]
    run = run_folder(str(tmp_path), {f"rounds/{n}.cut.json": {} for n in names})
    start = Start(1, "evaluator", "C1", {}, None, 3)
    assert rounds.fresh(run, start) == f"{run}/rounds/1/evaluator-C1.cut.json"


def written(path: str) -> Any:
    """The JSON of the Cut written at the path."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def deliverable(tree: dict[str, Any], index: int) -> dict[str, str]:
    """The name, path, and kind of the tree's deliverable at the index, as a Cut holds them."""
    return {k: tree["deliverables"][index][k] for k in ("name", "path", "kind")}


@pytest.mark.supports("test_each_cut_holds_its_role_deliverable_best_practice_and_goal")
def test_write_gives_the_generator_its_deliverable_best_practice_goal_and_decisions(tmp_path: Any):
    """Given the plan, and the command's generator of round 1 due
    When cut.write writes its Cut
    Then it gives rounds/1/generator.cut.json, which holds the generator, the command's name,
    path, and kind, code, the goal, and each decision of the command, and nothing else"""
    run = run_folder(str(tmp_path), {"design-tree.json": plan()})
    path = cut.write(run, plan(), Due(COMMAND, "generator", "", "code", 1))
    assert path == f"{run}/rounds/1/generator.cut.json"
    assert written(path) == {
        "role": "generator",
        "deliverable": deliverable(plan(), 0),
        "best_practice": "code",
        "goal": GOAL,
        "decisions": decisions(plan()),
    }


@pytest.mark.supports("test_a_round_of_refactoring_comes_only_after_the_content_is_good")
def test_write_gives_a_generator_of_refactoring_the_best_practice_its_start_names(tmp_path: Any):
    """Given the plan, and the command's generator of round 2 by refactor-code due
    When cut.write writes its Cut
    Then it gives rounds/2/generator.cut.json, which names refactor-code, not the command's kind"""
    run = run_folder(str(tmp_path), {"design-tree.json": plan()})
    path = cut.write(run, plan(), Due(COMMAND, "generator", "", "refactor-code", 2))
    assert path == f"{run}/rounds/2/generator.cut.json"
    assert written(path) == {
        "role": "generator",
        "deliverable": deliverable(plan(), 0),
        "best_practice": "refactor-code",
        "goal": GOAL,
        "decisions": decisions(plan()),
    }


@pytest.mark.supports("test_an_evaluator_stopped_starts_again_with_a_fresh_cut_beside_its_first")
def test_write_beside_a_cut_with_no_result_writes_a_fresh_cut_from_the_tree_as_it_stands(
    tmp_path: Any,
):
    """Given the command's generator of round 1 cut, and then a decision changed in the plan
    When cut.write writes the same start's Cut again, as a stopped role starts again
    Then it gives slot 2 beside the first, holding the decisions as they stand, and leaves the
    first as it was"""
    run = run_folder(str(tmp_path), {"design-tree.json": plan()})
    start = Due(COMMAND, "generator", "", "code", 1)
    first = cut.write(run, plan(), start)
    again = cut.write(run, changed(), start)
    assert again == f"{run}/rounds/1/generator.2.cut.json"
    assert written(again)["decisions"] == decisions(changed())
    assert written(first)["decisions"] == decisions(plan())


@pytest.mark.supports("test_a_pick_up_from_the_repositorys_root_finds_the_run_in_rns_worktree")
def test_folder_gives_none_where_no_run_has_work_left(tmp_path: Any):
    """Given a worktree with no .rn/, and then one whose run's work is done, as a run merged, and
    one whose design tree isn't JSON
    When rounds.folder looks for the run's folder
    Then it gives None each time"""
    top = str(tmp_path)
    assert rounds.folder(top) is None
    done = json.dumps({"work": []})
    write_files(
        top, {".rn/20261101-a/design-tree.json": done, ".rn/20261102-b/design-tree.json": "{"}
    )
    os.makedirs(os.path.join(top, ".rn", "best-practices"))
    assert rounds.folder(top) is None


@pytest.mark.supports("test_a_pick_up_from_the_repositorys_root_finds_the_run_in_rns_worktree")
def test_folder_gives_the_run_with_work_left_in_the_top_or_in_rns_worktree(tmp_path: Any):
    """Given the repository's root, with a run done in its .rn/ and a run with work left in rn's
    worktree of that run
    When rounds.folder looks for the run's folder from the root, and then from that worktree
    Then it gives the worktree's run, from the top each time"""
    top = str(tmp_path)
    left = json.dumps(plan())
    tree = ".claude/worktrees/rn-20261119-b/.rn/20261119-b/design-tree.json"
    write_files(top, {".rn/20261101-a/design-tree.json": json.dumps({"work": []}), tree: left})
    assert rounds.folder(top) == ".claude/worktrees/rn-20261119-b/.rn/20261119-b"
    assert rounds.folder(os.path.join(top, ".claude/worktrees/rn-20261119-b")) == ".rn/20261119-b"


@pytest.mark.supports("test_a_pick_up_from_the_repositorys_root_finds_the_run_in_rns_worktree")
def test_folder_leaves_alone_a_worktree_that_isnt_rns(tmp_path: Any):
    """Given the repository's root with no run, and worktrees agent-1 and rnx-1, whose names
    nearly match rn's, each holding a run with work left
    When rounds.folder looks for the run's folder
    Then it gives None"""
    top = str(tmp_path)
    left = json.dumps(plan())
    write_files(
        top,
        {
            f".claude/worktrees/{name}/.rn/20261119-a/design-tree.json": left
            for name in ("agent-1", "rnx-1")
        },
    )
    assert rounds.folder(top) is None


@pytest.mark.supports("test_a_pick_up_from_the_repositorys_root_finds_the_run_in_rns_worktree")
def test_folder_gives_the_run_whose_design_tree_changed_last(tmp_path: Any):
    """Given three runs with work left, the one of the middle name changed last
    When rounds.folder looks for the run's folder
    Then it gives that run, neither the first nor the last by name"""
    top = str(tmp_path)
    left = json.dumps(plan())
    names = ("20261119-a", "20261119-b", "20261119-c")
    write_files(top, {f".rn/{n}/design-tree.json": left for n in names})
    for at, name in ((1, "20261119-a"), (3, "20261119-b"), (2, "20261119-c")):
        os.utime(os.path.join(top, ".rn", name, "design-tree.json"), (at, at))
    assert rounds.folder(top) == ".rn/20261119-b"


@pytest.mark.supports("test_a_pick_up_from_the_repositorys_root_finds_the_run_in_rns_worktree")
def test_folder_gives_the_tops_run_where_it_changed_after_the_worktrees(tmp_path: Any):
    """Given the repository's root with a run with work left, and rn's worktree of another run
    with work left, changed before it
    When rounds.folder looks for the run's folder from the root
    Then it gives the root's run"""
    top = str(tmp_path)
    left = json.dumps(plan())
    there = ".claude/worktrees/rn-20261119-b/.rn/20261119-b/design-tree.json"
    write_files(top, {".rn/20261119-a/design-tree.json": left, there: left})
    os.utime(os.path.join(top, there), (1, 1))
    assert rounds.folder(top) == ".rn/20261119-a"


@pytest.mark.supports("test_a_generator_starts_with_only_the_decisions_of_its_deliverable")
def test_write_gives_the_generator_the_decisions_of_an_input_node_with_no_file(tmp_path: Any):
    """Given the plan with a node of the product vision with no file, a decision under it, as the
    guide's input, and a decision under the guide
    When cut.write writes the guide's generator's Cut, the command done
    Then the Cut names the guide, the second of the deliverables, by readme, and holds the guide's
    decision and the node's, and none of another node"""
    tree = plan()
    who = {"about": "Who", "decided": "the team", "by": "user"}
    tree["deliverables"][0] = {"name": "c", "path": COMMAND, "kind": "code", "status": "done"}
    tree["deliverables"].append(vision(True, [who]))
    tree["deliverables"][1]["inputs"] = ["docs/team-vision.md", COMMAND]
    steps = {"about": "The steps", "decided": "five", "by": "reasoning"}
    tree["deliverables"][1]["necessary_conditions"][0]["decisions"].append(steps)
    tree["work"] = tree["work"][1:]
    run = run_folder(str(tmp_path), {"design-tree.json": tree})
    path = cut.write(run, tree, Due(GUIDE, "generator", "", "readme", 1))
    assert written(path) == {
        "role": "generator",
        "deliverable": deliverable(tree, 1),
        "best_practice": "readme",
        "goal": GOAL,
        "decisions": [
            {"path": GUIDE, "condition": "N1", **steps},
            {"path": "docs/team-vision.md", "condition": "N1", **who},
        ],
    }


@pytest.mark.supports("test_an_evaluator_starts_with_only_what_the_deliverables_people_have")
def test_write_gives_an_evaluator_its_group_and_the_conditions_due_and_no_decision(tmp_path: Any):
    """Given the plan, and the command's evaluator of C2 of round 1 due
    When cut.write writes its Cut
    Then it gives rounds/1/evaluator-C2.cut.json, which holds the evaluator, the command, code,
    the goal, C2, and N4 to N7, and no decision"""
    run = run_folder(str(tmp_path), {"design-tree.json": plan()})
    path = cut.write(run, plan(), Due(COMMAND, "evaluator", "C2", "code", 1))
    assert path == f"{run}/rounds/1/evaluator-C2.cut.json"
    assert written(path) == {
        "role": "evaluator",
        "deliverable": deliverable(plan(), 0),
        "best_practice": "code",
        "goal": GOAL,
        "group": "C2",
        "conditions": CODE_GROUPS["C2"],
    }


@pytest.mark.supports("test_a_round_of_refactoring_comes_only_after_the_content_is_good")
def test_write_gives_an_evaluator_of_refactoring_the_group_of_the_refactor_best_practice(
    tmp_path: Any,
):
    """Given the plan, and the command's evaluator of C2 of round 2 by refactor-code due
    When cut.write writes its Cut
    Then it gives rounds/2/evaluator-C2.cut.json, which holds refactor-code's C2, N2 to N6, not
    code's"""
    run = run_folder(str(tmp_path), {"design-tree.json": plan()})
    path = cut.write(run, plan(), Due(COMMAND, "evaluator", "C2", "refactor-code", 2))
    assert path == f"{run}/rounds/2/evaluator-C2.cut.json"
    assert written(path) == {
        "role": "evaluator",
        "deliverable": deliverable(plan(), 0),
        "best_practice": "refactor-code",
        "goal": GOAL,
        "group": "C2",
        "conditions": REFACTORING["C2"],
    }


@pytest.mark.supports("test_each_cut_holds_its_role_deliverable_best_practice_and_goal")
@pytest.mark.parametrize(
    ("start", "named"),
    [
        (Due("docs/faq.md", "generator", "", "code", 1), "docs/faq.md"),
        (Due("invoicer/__main__", "generator", "", "code", 1), "invoicer/__main__"),
        (Due(COMMAND, "evaluator", "C9", "code", 1), "C9"),
        (Due(COMMAND, "evaluator", "C4", "code", 1), "C4"),
    ],
    ids=["no such deliverable", "a near match", "no such group", "readme's group, not code's"],
)
def test_write_refuses_a_start_that_the_tree_doesnt_hold(tmp_path: Any, start: Due, named: str):
    """Given the plan, and a start of a deliverable that it doesn't hold, one whose path nearly
    matches the command's, a group that code doesn't hold, or a group that readme holds and code
    doesn't
    When cut.write writes its Cut
    Then it refuses with Wrong, naming it, and writes no Cut"""
    run = run_folder(str(tmp_path), {"design-tree.json": plan()})
    with pytest.raises(Wrong) as refused:
        cut.write(run, plan(), start)
    assert named in str(refused.value)
    assert not os.path.isdir(os.path.join(run, "rounds"))
