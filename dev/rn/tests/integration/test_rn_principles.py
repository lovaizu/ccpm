"""The integration cases of each principle item of rn's architecture: each where the parts keep it,
on the bench of the README's walkthrough through the double of Claude Code, and each with the
fixture `broken`, which takes the part that holds the item out of the bench's copy of rn where
TRACE_BROKEN is 1, as the plugin guide's A principle's test seen to fail says. A part taken out is
an interface given again at the end of its module, so the copy runs without what holds the item."""

from __future__ import annotations

import json
import os
import shutil
from collections.abc import Callable

import pytest
from rn_bench import (
    COMMAND,
    GUIDE,
    RUN,
    Bench,
    decided,
    head,
    judged,
    made,
    none_due,
    read_json,
    side_by_side,
    typed,
)

# Why a case is xfail while its body isn't written.
NO_STARTS_DUE = "starts_due.main isn't built yet"
NO_GUARD = "Lane's guard and rn's rules.main aren't built yet, so no guard holds rn's steps"


def given_again(b: Bench, module: str, code: str) -> None:
    """Gives an interface of the bench's module again, at the end of its file."""
    with open(os.path.join(b.rn, "domain", module), "a", encoding="utf-8") as f:
        f.write("\n\n" + code)


def without_the_check(b: Bench) -> None:
    """commit.commit commits with no check of the design tree."""
    given_again(
        b,
        "tree/commit.py",
        "def commit(top, run, plugin, ground):\n"
        "    from tree import git\n\n"
        "    return git.commit(top, run, ground)\n",
    )


def main_given_again(b: Bench, adapter: str, code: str) -> None:
    """Gives the main of the bench's adapter of rn's again, before the adapter runs it."""
    path = os.path.join(b.rn, "lane", "adapters", f"{adapter}.py")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    run = 'if __name__ == "__main__":'
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.replace(run, code + "\n\n" + run))


def due_before_sign_off(b: Bench) -> None:
    """rn's adapter of the starts due gives the generator whatever the run's commands are."""
    main_given_again(
        b,
        "starts_due",
        "def main(given, cwd):\n"
        '    return 0, \'{"starts": [{"role": "rn:generator", "count": 1}]}\', \'\'\n',
    )


def one_at_a_time(b: Bench) -> None:
    """The course takes only the first deliverable of the work that can be made now."""
    given_again(
        b,
        "tree/course.py",
        "_all_ready = _ready\n\n\n"
        "def _ready(tree, nodes):\n"
        "    return _all_ready(tree, nodes)[:1]\n",
    )


def without_the_guard(b: Bench) -> None:
    """rn's rules for Lane taken out, so that Lane's guard holds none of rn's steps."""
    rules = os.path.join(b.rn, "lane", "rules.json")
    if os.path.exists(rules):
        os.remove(rules)


def due_without_course(b: Bench) -> None:
    """course.due gives the generator, then each evaluator, at once, with no round's course."""
    given_again(
        b,
        "tree/course.py",
        "def due(tree, starts, running):\n"
        "    path = tree['work'][0]['path']\n"
        "    return [\n"
        "        Due(path, 'generator', '', 'code', 1),\n"
        "        Due(path, 'evaluator', 'C1', 'code', 1),\n"
        "    ]\n",
    )


def cut_of_the_whole_tree(b: Bench) -> None:
    """cut.write gives each role the whole design tree."""
    given_again(
        b,
        "tree/cut.py",
        "def write(run, tree, due):\n"
        "    import json, os\n"
        "    from tree import rounds\n\n"
        "    path = os.path.join(run, 'rounds', str(due.round), due.role + '.cut.json')\n"
        "    os.makedirs(os.path.dirname(path), exist_ok=True)\n"
        "    with open(path, 'w') as f:\n"
        "        json.dump({'role': due.role, 'tree': tree}, f)\n"
        "    return path\n",
    )


def results_unchecked(b: Bench) -> None:
    """Each check of a role's result finds no fault."""
    for module in ("check/generator.py", "check/evaluator.py"):
        given_again(b, module, "def faults(*given):\n    return []\n")


BREAKS: dict[str, Callable[[Bench], None]] = {
    "test_an_edit_out_of_form_is_refused_before_its_commit": without_the_check,
    "test_a_generators_point_starts_no_other_role": due_without_course,
    "test_work_that_rests_on_a_plan_waits_for_its_sign_off": due_before_sign_off,
    "test_an_evaluator_starts_with_only_what_the_deliverables_people_have": cut_of_the_whole_tree,
    "test_an_evaluators_answer_beside_good_and_more_is_held": results_unchecked,
    "test_no_evaluator_starts_before_the_generator_ends": due_without_course,
    "test_a_round_of_refactoring_comes_only_after_the_content_is_good": due_without_course,
    "test_findings_past_the_limit_start_no_further_round": due_without_course,
    "test_a_generator_starts_with_only_the_decisions_of_its_deliverable": cut_of_the_whole_tree,
    "test_a_role_that_ends_with_no_result_in_its_file_is_held": results_unchecked,
    "test_a_role_that_writes_beside_its_deliverable_is_told_its_step": without_the_guard,
    "test_deliverables_that_rest_on_none_being_made_start_at_once": one_at_a_time,
    "test_a_new_conversation_goes_on_from_the_files_alone": due_without_course,
}


@pytest.fixture
def broken(b: Bench, request: pytest.FixtureRequest) -> None:
    """Takes out the part that holds the case's principle item where TRACE_BROKEN is 1."""
    if os.environ.get("TRACE_BROKEN") == "1":
        BREAKS[request.node.originalname](b)


def make(b: Bench, more: dict[str, str]) -> None:
    """One round of the command: its generator makes it, and each evaluator due judges it, more on
    each condition named."""
    made(b)
    judged(b, more)


@pytest.mark.supports("P1.1")
def test_an_edit_out_of_form_is_refused_before_its_commit(b: Bench, broken: None):
    """Given the orchestrator's edit that leaves a decision with no `by`
    When it runs tree.py commit
    Then it gives 1 naming where the tree leaves its form, and the branch keeps its last commit"""
    tree = b.tree()
    tree["deliverables"][0]["necessary_conditions"][0]["decisions"].append(
        {"about": "x", "decided": "y"}
    )
    b.write_tree(tree)
    answer = b.commit(b.converse(), "An edit out of form")
    assert answer.exit_code == 1
    assert "deliverables/0/necessary_conditions/0/decisions/2" in answer.output
    assert head(b) == "The plan, signed off"


@pytest.mark.supports("P1.2")
def test_a_generators_point_starts_no_other_role(b: Bench, broken: None):
    """Given the command's generator ended with a point for the user
    When the orchestrator runs rn's script of each role's Cut
    Then none is due, as the point waits for the user's answer"""
    cut = b.cut("generator")
    b.write_result(cut, {"result": "point", "point": "EUR alone? I recommend EUR alone."})
    assert none_due(b, "evaluator")
    assert none_due(b, "generator")


@pytest.mark.xfail(strict=True, reason=NO_STARTS_DUE)
@pytest.mark.supports("P1.3")
def test_work_that_rests_on_a_plan_waits_for_its_sign_off(b: Bench, broken: None):
    """Given /rn:up typed with a request, and the orchestrator putting the plan up for the
    person's sign-off
    When Lane asks rn's adapter of the starts due, before the person types /rn:ty
    Then it gives no start, so that the guard stops any start of the command's generator"""
    words = "a command with which the accounting team prints an invoice from its lines"
    code, printed, said = b.due(words, [typed("rn:up")])
    assert (code, printed) == (0, {"starts": []}), said


@pytest.mark.supports("P2.1")
def test_an_evaluator_starts_with_only_what_the_deliverables_people_have(b: Bench, broken: None):
    """Given the command made
    When the orchestrator runs rn's script of an evaluator's Cut
    Then its Cut holds the command, the goal with its people's state, and its group's conditions,
    and none of the decisions the generator made it from"""
    made(b)
    cut = b.cut("evaluator")
    with open(os.path.join(b.repo, cut), encoding="utf-8") as f:
        written = json.load(f)
    assert written["deliverable"]["path"] == COMMAND
    assert "decisions" not in written


@pytest.mark.supports("P2.2")
def test_an_evaluators_answer_beside_good_and_more_is_held(b: Bench, broken: None):
    """Given the command's first evaluator due
    When it ends with no answer and a fix of its own beside
    Then rn's check gives 1, naming the fix, as a trial names only what's good and what would make
    it good"""
    made(b)
    cut = b.cut("evaluator")
    b.write_result(cut, {"good": [], "more": [], "fix": "rename main to run"})
    agent = b.converse().start("rn:evaluator", "Carry out your steps", "judge the command")[1]
    assert agent is not None
    answer = b.check(agent, "evaluator", cut)
    assert answer.exit_code == 1
    assert "fix" in answer.output


@pytest.mark.supports("P3.1")
def test_no_evaluator_starts_before_the_generator_ends(b: Bench, broken: None):
    """Given the command's generator started, with no result yet
    When the orchestrator runs rn's script of an evaluator's Cut
    Then none is due, as making and judging are separate roles"""
    b.cut("generator")
    assert none_due(b, "evaluator")


@pytest.mark.supports("P3.2")
def test_a_round_of_refactoring_comes_only_after_the_content_is_good(b: Bench, broken: None):
    """Given round 1 of the command judged with more on N4
    When the orchestrator runs rn's script of the generator's Cut
    Then round 2 works by the code best practice, not the refactor one"""
    make(b, {"N4": "A colleague reads each step of the command at a glance"})
    decided(b, 3, {"about": "The steps", "decided": "one function a step", "by": "reasoning"})
    cut = b.cut("generator")
    with open(os.path.join(b.repo, cut), encoding="utf-8") as f:
        assert json.load(f)["best_practice"] == "code"


@pytest.mark.supports("P3.3")
def test_findings_past_the_limit_start_no_further_round(b: Bench, broken: None):
    """Given two rounds of the command's content, each judged with more on N4, and each finding
    taken into a decision of N4
    When the orchestrator runs rn's script of the generator's Cut
    Then none is due"""
    for steps in ("one function a step", "one module a step"):
        make(b, {"N4": "A colleague reads each step at a glance"})
        decided(b, 3, {"about": "The steps", "decided": steps, "by": "reasoning"})
    assert none_due(b, "generator")


@pytest.mark.supports("P4.1")
def test_a_generator_starts_with_only_the_decisions_of_its_deliverable(b: Bench, broken: None):
    """Given the plan, with a decision under the guide
    When the orchestrator runs rn's script of the command's generator's Cut
    Then its Cut holds the command's decisions alone"""
    tree = b.tree()
    tree["deliverables"][1]["necessary_conditions"][0]["decisions"].append(
        {"about": "The guide's people", "decided": "the accounting team", "by": "user"}
    )
    b.write_tree(tree)
    cut = b.cut("generator")
    with open(os.path.join(b.repo, cut), encoding="utf-8") as f:
        written = json.load(f)
    assert {d["path"] for d in written["decisions"]} == {COMMAND}
    assert GUIDE not in json.dumps(written)


@pytest.mark.supports("P4.2")
def test_a_role_that_ends_with_no_result_in_its_file_is_held(b: Bench, broken: None):
    """Given the command's generator started
    When it ends with no result written beside its Cut
    Then rn's check gives 1, as what a role makes stays in files"""
    cut = b.cut("generator")
    agent = b.converse().start("rn:generator", "Carry out your steps", "make the command")[1]
    assert agent is not None
    assert b.check(agent, "generator", cut).exit_code == 1


@pytest.mark.xfail(strict=True, reason=NO_GUARD)
@pytest.mark.supports("P5.1")
def test_a_role_that_writes_beside_its_deliverable_is_told_its_step(b: Bench, broken: None):
    """Given the command's generator started with its Cut
    When it writes a file other than its deliverable and its result
    Then the guard stops the write with the step's sentence"""
    c = b.converse()
    _, agent = b.start(c, "generator", "make the command")
    assert agent is not None
    answer = agent.write(os.path.join(b.repo, "invoicer", "notes.py"), "")
    assert answer.blocked


@pytest.mark.supports("P5.2")
def test_deliverables_that_rest_on_none_being_made_start_at_once(b: Bench, broken: None):
    """Given the plan in which the guide rests on the product vision alone, not on the command
    When the orchestrator runs rn's script of the generator's Cut twice, as Lane gives two due
    Then it gives a Cut of the command and then one of the guide, each in a Round of its own"""
    side_by_side(b)
    first, second = b.cut("generator"), b.cut("generator")
    assert first != second
    paths = {read_json(b, cut)["deliverable"]["path"] for cut in (first, second)}
    assert paths == {COMMAND, GUIDE}


@pytest.mark.supports("P6.1")
def test_a_new_conversation_goes_on_from_the_files_alone(b: Bench, broken: None):
    """Given round 1 of the command made and judged with more on N4, its decision changed, and the
    system's temporary folder cleared
    When the orchestrator runs rn's script of the generator's Cut
    Then round 2 is due, from the run's folder alone"""
    make(b, {"N4": "A colleague reads each step at a glance"})
    decided(b, 3, {"about": "The steps", "decided": "one function a step", "by": "reasoning"})
    shutil.rmtree(b.env["TMPDIR"])
    os.makedirs(b.env["TMPDIR"])
    assert b.cut("generator") == f"{RUN}/rounds/2/generator.cut.json"
