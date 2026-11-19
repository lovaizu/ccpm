"""The integration cases of S1, a deliverable made in rounds: the orchestrator's commit of each edit
of the design tree, the starts due that rn's adapter gives Lane, each start with its Cut that rn's
script writes, each role's end held by rn's check, and the course of the rounds, joined on the bench
of the README's walkthrough through the double of Claude Code, one case for each path of S1's
sequence that rn's parts carry."""

from __future__ import annotations

import pytest
import rn_bench
from repo_files import write_files
from rn_bench import (
    COMMAND,
    GUIDE,
    RUN,
    Bench,
    command_done,
    decided,
    head,
    none_due,
    read_json,
    started,
    typed,
)

# Why a case is xfail while its body isn't written.
NO_STARTS_DUE = "starts_due.main isn't built yet"

TAX_RATE = {"path": COMMAND, "condition": "N1", "about": "The tax rate"}
LINES = {"path": COMMAND, "condition": "N1", "about": "The lines"}
# A decision under the command's N2, from a finding of its evaluator.
WRONG_LINE = {"about": "A wrong line", "decided": "named by its number", "by": "reasoning"}
# The groups of the code best practice's conditions, as its best-practice.json bundles them.
CODE_GROUPS = {"C1": ["N1", "N2", "N3"], "C2": ["N4", "N5", "N6", "N7"], "C3": ["N8"]}
# The words of the walkthrough's request.
REQUEST = "a command with which the accounting team prints an invoice from its lines"


def made(b: Bench, carried_out: list[dict[str, str]] | None = None) -> str:
    """The command's generator ends with the command made and a place for each decision named, its
    Cut's two by default, and gives its Cut's path."""
    return rn_bench.made(b, [TAX_RATE, LINES] if carried_out is None else carried_out)


def judged(b: Bench, more: dict[str, str]) -> list[str]:
    """Each evaluator due judges the command, more on each condition named, and gives each Cut."""
    return [cut for _, cut in rn_bench.judged(b, more)]


@pytest.mark.xfail(strict=True, reason=NO_STARTS_DUE)
@pytest.mark.supports("S1")
def test_a_new_request_starts_no_role_while_its_plan_waits_for_sign_off(b: Bench):
    """Given /rn:up typed with the walkthrough's request, and the plan put up
    When Lane asks rn's adapter of the starts due
    Then it gives no start, as the plan waits for /rn:ty"""
    assert b.starts(REQUEST, [typed("rn:up")]) == {}


@pytest.mark.xfail(strict=True, reason=NO_STARTS_DUE)
@pytest.mark.supports("S1")
def test_a_plan_sent_back_starts_no_role_until_its_sign_off(b: Bench):
    """Given /rn:up typed with the request, and then /rn:gm with what to change
    When Lane asks rn's adapter of the starts due
    Then it gives no start, as the plan changed waits for its sign-off"""
    assert b.starts(REQUEST, [typed("rn:up"), typed("rn:gm")]) == {}


@pytest.mark.xfail(strict=True, reason=NO_STARTS_DUE)
@pytest.mark.supports("S1")
def test_a_plan_signed_off_gives_lane_the_generator_of_its_first_deliverable(b: Bench):
    """Given /rn:up typed with the request, and then /rn:ty
    When Lane asks rn's adapter of the starts due
    Then it gives one start of rn:generator"""
    assert b.starts(REQUEST, [typed("rn:up"), typed("rn:ty")]) == {"rn:generator": 1}


@pytest.mark.supports("S1")
def test_an_edit_of_the_design_tree_is_committed_with_its_ground(b: Bench):
    """Given the plan signed off, and the orchestrator's edit that settles a point of the command
    When it runs tree.py commit with the point's ground
    Then the work's branch gets one commit of the run's folder, with the ground as its message"""
    decided(
        b, 1, {"about": "The command's name", "decided": "python3 -m invoicer", "by": "reasoning"}
    )
    answer = b.commit(b.converse(), "A module's -m is how invoicer's users run Python")
    assert answer.exit_code == 0, answer.output
    assert head(b) == "A module's -m is how invoicer's users run Python"


@pytest.mark.supports("S1")
def test_a_point_first_in_the_work_starts_no_role_while_it_waits(b: Bench):
    """Given the orchestrator's edit that puts a point of the command, the currency, first in the
    work, for the user to settle
    When the orchestrator runs rn's script of the generator's Cut
    Then no start of the generator is due"""
    tree = b.tree()
    tree["work"].insert(
        0, {"do": "decide", "path": COMMAND, "condition": "N1", "about": "The currency"}
    )
    b.write_tree(tree)
    assert none_due(b, "generator")


@pytest.mark.supports("S1")
def test_the_first_deliverable_of_the_work_gets_a_generator_with_its_cut(b: Bench):
    """Given the plan signed off, the command first in the work
    When the orchestrator runs rn's script of the generator's Cut
    Then it gives the path of the Cut of round 1, and the Cut names the
    command, the code best practice, the goal, and each decision of the command"""
    cut = b.cut("generator")
    assert cut == f"{RUN}/rounds/1/generator.cut.json"
    written = read_json(b, cut)
    assert (written["role"], written["deliverable"]["path"]) == ("generator", COMMAND)
    assert written["best_practice"] == "code"
    assert written["goal"] == b.tree()["goal"]["decided"]
    assert [d["about"] for d in written["decisions"]] == ["The tax rate", "The lines"]


@pytest.mark.supports("S1")
def test_a_generators_point_passes_its_check_and_starts_no_evaluator(b: Bench):
    """Given the generator of the command started
    When it ends with a point it can't settle
    Then rn's check gives 0, and no evaluator is due, as the point goes to the orchestrator"""
    c = b.converse()
    cut, agent = b.start(c, "generator", "make the command")
    assert agent is not None
    b.write_result(cut, {"result": "point", "point": "Print in EUR alone? I recommend EUR alone."})
    assert b.check(agent, "generator", cut).exit_code == 0
    assert none_due(b, "evaluator")


@pytest.mark.supports("S1")
def test_a_point_answered_gets_the_generator_again(b: Bench):
    """Given the command's generator ended with a point on the currency
    When the orchestrator takes the user's answer into a decision under N1 and commits it
    Then the generator of round 2 is due, its Cut holding the answer"""
    cut = b.cut("generator")
    b.write_result(cut, {"result": "point", "point": "Print in EUR alone? I recommend EUR alone."})
    answer = {"about": "The currency", "decided": "EUR alone", "by": "user"}
    decided(b, 0, answer, "The accounting team invoices in EUR alone")
    again = b.cut("generator")
    assert again == f"{RUN}/rounds/2/generator.cut.json"
    assert "The currency" in [d["about"] for d in read_json(b, again)["decisions"]]


@pytest.mark.supports("S1")
def test_a_generators_result_that_carries_out_each_decision_passes_its_check(b: Bench):
    """Given the generator's Cut of the command
    When it ends with the command made and a place for each decision of its Cut
    Then rn's check gives 0"""
    cut = made(b)
    agent = b.converse().start("rn:generator", started(cut)["prompt"], "make the command")[1]
    assert agent is not None
    assert b.check(agent, "generator", cut).exit_code == 0


@pytest.mark.supports("S1")
def test_a_generators_result_that_leaves_a_decision_out_is_held_naming_it(b: Bench):
    """Given the generator's Cut of the command
    When it ends with a place for the lines alone
    Then rn's check gives 1, naming the tax rate"""
    cut = made(b, [LINES])
    agent = b.converse().start("rn:generator", started(cut)["prompt"], "make the command")[1]
    assert agent is not None
    answer = b.check(agent, "generator", cut)
    assert answer.exit_code == 1
    assert "The tax rate" in answer.output


@pytest.mark.supports("S1")
def test_a_deliverable_made_gets_one_evaluator_for_each_group_of_its_conditions(b: Bench):
    """Given the command made, its result accepted
    When the orchestrator runs rn's script of each evaluator's Cut, one after another
    Then it gives one Cut for each group of the code best practice, each with that group's
    conditions, and then none"""
    made(b)
    cuts = judged(b, {})
    groups = {read_json(b, cut)["group"]: read_json(b, cut)["conditions"] for cut in cuts}
    assert groups == CODE_GROUPS


@pytest.mark.xfail(strict=True, reason=NO_STARTS_DUE)
@pytest.mark.supports("S1")
def test_a_deliverable_made_gives_lane_its_evaluators_beside_those_that_run(b: Bench):
    """Given the command made, and the evaluator of C1 started with no result yet
    When Lane asks rn's adapter of the starts due, with the starts of the run
    Then it gives two starts of rn:evaluator, for C2 and C3"""
    cut = made(b)
    first = b.cut("evaluator")
    moves = [
        typed("rn:up"),
        started(cut),
        {"kind": "result", "role": "rn:generator", "result": "made"},
    ]
    assert b.starts(moves=[*moves, started(first)]) == {"rn:evaluator": 2}


@pytest.mark.supports("S1")
def test_an_evaluators_result_that_answers_each_condition_of_its_group_passes_its_check(b: Bench):
    """Given an evaluator's Cut of the group C3 of the command
    When it ends answering N8 good with its lines
    Then rn's check gives 0"""
    made(b)
    cut = next(c for c in judged(b, {}) if c.endswith("evaluator-C3.cut.json"))
    agent = b.converse().start("rn:evaluator", started(cut)["prompt"], "judge the command")[1]
    assert agent is not None
    assert b.check(agent, "evaluator", cut).exit_code == 0


@pytest.mark.supports("S1")
def test_an_evaluators_result_that_leaves_a_condition_unanswered_is_held_naming_it(b: Bench):
    """Given an evaluator's Cut of the group C1 of the command
    When it ends answering N1 and N2 alone
    Then rn's check gives 1, naming N3"""
    made(b)
    cut = next(c for c in judged(b, {}) if c.endswith("evaluator-C1.cut.json"))
    b.write_result(
        cut,
        {"good": [{"condition": c, "lines": [f"{COMMAND}:1"]} for c in ("N1", "N2")], "more": []},
    )
    agent = b.converse().start("rn:evaluator", started(cut)["prompt"], "judge the command")[1]
    assert agent is not None
    answer = b.check(agent, "evaluator", cut)
    assert answer.exit_code == 1
    assert "N3" in answer.output


@pytest.mark.supports("S1")
def test_a_finding_taken_into_its_decision_gets_the_next_round_of_content(b: Bench):
    """Given round 1 of the command judged, with more on N2
    When the orchestrator takes the finding into a decision under N2 and commits it
    Then the generator of round 2 is due, by the code best practice"""
    made(b)
    judged(b, {"N2": "The team sees a wrong line named, not a trace"})
    decided(b, 1, WRONG_LINE, "The accounting team mends a wrong line by its number")
    cut = b.cut("generator")
    assert cut == f"{RUN}/rounds/2/generator.cut.json"
    assert read_json(b, cut)["best_practice"] == "code"


@pytest.mark.supports("S1")
def test_a_finding_the_people_would_never_meet_gets_a_round_of_refactoring(b: Bench):
    """Given round 1 of the command judged, with more on N2
    When the orchestrator holds N2 good, as the people would never meet the finding, and commits
    Then the generator of round 2 is due, by the refactor-code best practice"""
    made(b)
    judged(b, {"N2": "The team sees a wrong line named, not a trace"})
    tree = b.tree()
    tree["deliverables"][0]["necessary_conditions"][1]["good"] = True
    b.write_tree(tree)
    assert read_json(b, b.cut("generator"))["best_practice"] == "refactor-code"


@pytest.mark.supports("S1")
def test_content_judged_good_gets_a_round_of_refactoring(b: Bench):
    """Given round 1 of the command judged good on each condition
    When the orchestrator runs rn's script of the generator's Cut
    Then the generator of round 2 is due, by the refactor-code best practice"""
    made(b)
    judged(b, {})
    cut = b.cut("generator")
    assert cut == f"{RUN}/rounds/2/generator.cut.json"
    assert read_json(b, cut)["best_practice"] == "refactor-code"


@pytest.mark.supports("S1")
def test_refactoring_judged_good_leaves_the_deliverable_for_its_sign_off(b: Bench):
    """Given round 1 of the command judged good, and round 2's refactoring made and judged good
    When the orchestrator runs rn's script of each role's Cut
    Then no start of the command is due, as it waits for the user's sign-off"""
    made(b)
    judged(b, {})
    made(b, [])
    assert [read_json(b, c)["best_practice"] for c in judged(b, {})] == ["refactor-code"] * 3
    assert none_due(b, "generator") and none_due(b, "evaluator")


@pytest.mark.supports("S1")
def test_findings_past_two_rounds_of_content_start_no_third(b: Bench):
    """Given two rounds of the command's content, each judged with more on N2, its decision changed
    after each
    When the orchestrator runs rn's script of the generator's Cut
    Then none is due, as each finding left goes to the user as a proposal"""
    for wrong in ("named by its number", "named by its row"):
        made(b)
        judged(b, {"N2": "The team sees a wrong line named"})
        decided(b, 1, {**WRONG_LINE, "decided": wrong}, f"A wrong line {wrong}")
    assert none_due(b, "generator")


@pytest.mark.supports("S1")
def test_a_users_decision_past_the_limit_gets_a_third_round(b: Bench):
    """Given two rounds of the command's content short on N2, and the user's decision under N2 on
    the proposal
    When the orchestrator runs rn's script of the generator's Cut
    Then the generator of round 3 is due, by the code best practice"""
    for by in ("reasoning", "user"):
        made(b)
        judged(b, {"N2": "The team sees a wrong line named"})
        decided(b, 1, {**WRONG_LINE, "decided": f"named by {by}", "by": by}, f"By {by}")
    cut = b.cut("generator")
    assert cut == f"{RUN}/rounds/3/generator.cut.json"
    assert read_json(b, cut)["best_practice"] == "code"


@pytest.mark.supports("S1")
def test_a_generators_end_with_its_deliverable_off_its_template_is_held(b: Bench):
    """Given the command done, and the guide's generator started by the readme best practice
    When it ends with a guide that holds a section FAQ, which readme's template doesn't
    Then rn's check gives 1, naming the guide's line of FAQ"""
    command_done(b)
    cut = b.cut("generator")
    write_files(b.repo, {GUIDE: "# Printing an invoice\n\n## FAQ\n"})
    b.write_result(cut, {"result": "made", "carried_out": []})
    agent = b.converse().start("rn:generator", started(cut)["prompt"], "make the guide")[1]
    assert agent is not None
    answer = b.check(agent, "generator", cut)
    assert answer.exit_code == 1
    assert f'{GUIDE}:3: "## FAQ" lies beside the template' in answer.output


@pytest.mark.xfail(strict=True, reason=NO_STARTS_DUE)
@pytest.mark.supports("S1")
def test_the_sign_off_of_the_pull_request_ends_the_run(b: Bench):
    """Given each deliverable done and no work left, and the pull request put up
    When the person types /rn:ty, and Lane asks rn's adapter of the starts due
    Then it gives that the run ends"""
    tree = b.tree()
    tree["work"] = []
    b.write_tree(tree)
    code, printed, said = b.due(moves=[typed("rn:up"), typed("rn:ty")])
    assert (code, printed) == (0, {"ends": True}), said


@pytest.mark.xfail(strict=True, reason=NO_STARTS_DUE)
@pytest.mark.supports("S1")
def test_a_sign_off_with_work_left_doesnt_end_the_run(b: Bench):
    """Given the command made and its round 1 judged good, the guide still in the work
    When the person types /rn:ty, and Lane asks rn's adapter of the starts due
    Then it gives the generator of the command's refactoring, not the run's end"""
    made(b)
    judged(b, {})
    assert b.starts(moves=[typed("rn:up"), typed("rn:ty")]) == {"rn:generator": 1}
