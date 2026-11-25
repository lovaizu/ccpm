"""The unit cases of rounds/course.py, which Round a deliverable takes next: one for each row of
next_of's decision table, in the order its contract gives, each row's boundaries of LIMIT Rounds of
content in a course and of the one refactor Round, a course started again after a Round put up for
the sign-off, the last Round picked among several, and each transition that a run brings: a point
kept as an open decision and then answered, a generator's made with no evaluator yet, an evaluator's
findings, the content at LIMIT whose findings left the pruner keeps as open decisions, which then
waits on the sign-off before the answer, and past which a remedy that the pruner wrote since the
last Cut takes another content Round, a refactor Round made, which no evaluator judges, a Round put
up and a send-back after it, and a pause that leaves a Round with its Cut and no result, of the
generator or of the evaluator, at Round 1 and at LIMIT, which spends no Round. Then next_with_fixes,
with the Fixes after the Rounds: none, as next_of; a Fix whose fixer wrote nothing, its Cut written
or not; a Fix fixed or naming a decision, the node as its fixer's Cut held it, changed since, or
with no Cut, and a decision weighed by a commit since; Rounds after a Fix, which count alone toward
the limit; and Fixes past LIMIT Rounds, which spend no Round; mended and next_in, reading the Fixes
from a run's files; the pruner where the last Round's point or findings are unweighed, before an
answer and after a put-up; and asked, with no Round and past the limit."""

from __future__ import annotations

import os
from collections.abc import Sequence
from typing import Any

import pytest
import rn_files
from repository.place import RunPlace
from rounds.course import (
    JUDGED,
    LIMIT,
    POINT,
    Done,
    Mend,
    Next,
    asked,
    mended,
    next_in,
    next_of,
    next_with_fixes,
)
from rounds.files import Fix, Round

COMMAND = rn_files.COMMAND


@pytest.fixture
def results(tmp_path: Any) -> str:
    """The folder where the case writes each role's result, to read it back as its use does."""
    return str(tmp_path)


def read_back(folder: str, name: str, value: Any) -> Any:
    """The value written as JSON in the folder and read back from its file."""
    path = os.path.join(folder, f"{name}.json")
    rn_files.write_json(path, value)
    return rn_files.read_json(path)


def rounds(folder: str, *each: tuple[Any, ...]) -> list[Done]:
    """The command's Rounds, each by its stage, number, generator's result, and evaluator's
    result, None where the role wrote none, each result read back from JSON, and, where a fifth
    item is given, the state it was put up with for the sign-off, read back from JSON."""
    found: list[Done] = []
    for stage, number, made, judged, *marked in each:
        place = rn_files.round_of(os.path.join(folder, "run"), COMMAND, stage, number)
        generator = None if made is None else read_back(folder, f"g-{stage}-{number}", made)
        evaluator = None if judged is None else read_back(folder, f"e-{stage}-{number}", judged)
        round_ = Round(place, COMMAND, stage, number)
        put_up = read_back(folder, f"p-{stage}-{number}", marked[0]) if marked else None
        found.append(Done(round_, generator, evaluator, put_up))
    return found


# The states of the command put up for the sign-off, as `put-up.json` holds them: each condition
# good, and N1 not good, keeping the finding left as a proposal, as `node(open_decision=True)`.
GOOD_PUT_UP = {"short": [], "open": []}
LEFT_PUT_UP = {"short": ["N1"], "open": [{"condition": "N1", "about": "a comma in a line"}]}


def node(good: bool | Sequence[str] = False, open_decision: bool = False, folder: str = "") -> Any:
    """The command's open node, of the kind light, its conditions good as given, N1 holding an
    answered decision and, where `open_decision`, an open one, as a point or a finding left is
    kept; read back from JSON where a folder is given."""
    decisions = [rn_files.decision("the tax rate", "with each invoice", "user")]
    if open_decision:
        decisions.append(rn_files.decision("a comma in a line", None))
    given = rn_files.decided(
        rn_files.open_node(rn_files.COMMAND_NAME, COMMAND, "light", ["invoicer/lines.py"], good),
        {"N1": decisions},
    )
    return read_back(folder, "node", given) if folder else given


MADE_ALL = rn_files.made([("N1", ["print"]), ("N2", ["print"]), ("N3", ["print"])], [COMMAND])
POINTED = rn_files.point("Should a line's quantity default to 1?")
SHORT = rn_files.judged([("N2", ["print"]), ("N3", ["print"])], [("N1", "They print it.")])
GOOD = rn_files.judged([("N1", ["print"]), ("N2", ["print"]), ("N3", ["print"])])


# The answer, where a decision of the node is open.


@pytest.mark.supports("test_a_deliverable_whose_point_waits_on_the_user_gets_no_cut")
def test_an_open_decision_waits_on_the_answer_after_a_point(results: str):
    """Given the command whose generator gave a point in content-1, kept as an open decision of N1
    When what it waits on is asked
    Then it waits on the answer, with no stage, resuming nothing"""
    done = rounds(results, ("content", 1, POINTED, None))
    assert next_of(node(open_decision=True, folder=results), done, False) == Next(
        "answer", None, False
    )


@pytest.mark.supports("test_a_deliverable_whose_point_waits_on_the_user_gets_no_cut")
def test_an_open_decision_waits_on_the_answer_before_the_evaluator_due(results: str):
    """Given the command made in content-1 with no evaluator yet, and an open decision of N1, as
    the pruner keeps a point that the user settles
    When what it waits on is asked
    Then it waits on the answer, the first row that holds"""
    done = rounds(results, ("content", 1, MADE_ALL, None))
    assert next_of(node(open_decision=True, folder=results), done, False) == Next(
        "answer", None, False
    )


@pytest.mark.supports("test_a_deliverable_whose_point_waits_on_the_user_gets_no_cut")
def test_an_open_decision_waits_on_the_answer_with_no_round_yet(results: str):
    """Given the command with no Round, and an open decision of N1 that the plan left for the user
    When what it waits on is asked
    Then it waits on the answer"""
    assert next_of(node(open_decision=True, folder=results), [], False) == Next(
        "answer", None, False
    )


# The pruner, where the last Round's result asks a judgment that no commit weighed yet.


def unweighed(done: list[Done]) -> list[Done]:
    """The Rounds, the last one's result unweighed, as `so_far` gives it before the tree's commit
    after it."""
    return [*done[:-1], done[-1]._replace(unweighed=True)]


@pytest.mark.supports("test_a_generators_point_goes_to_a_pruner_which_leaves_open_only_the_users")
@pytest.mark.parametrize("open_decision", [False, True], ids=["none open", "one open"])
def test_a_point_unweighed_waits_on_the_pruner_of_the_stage_point(
    results: str, open_decision: bool
):
    """Given the command whose generator gave a point in content-1, unweighed, with no decision
    open or with one
    When what it waits on is asked
    Then it waits on the pruner of the stage point, before any answer"""
    done = unweighed(rounds(results, ("content", 1, POINTED, None)))
    assert next_of(node(open_decision=open_decision, folder=results), done, False) == Next(
        "pruner", POINT, False
    )


@pytest.mark.supports(
    "test_a_judged_rounds_result_is_weighed_whole_by_one_pruner_with_each_node_it_touches"
)
def test_a_judged_round_unweighed_waits_on_the_pruner_of_the_stage_judged(results: str):
    """Given the command whose evaluator judged content-1 short, unweighed
    When what it waits on is asked
    Then it waits on the pruner of the stage judged, not on a new Round"""
    done = unweighed(rounds(results, ("content", 1, MADE_ALL, SHORT)))
    assert next_of(node(folder=results), done, False) == Next("pruner", JUDGED, False)


@pytest.mark.supports("test_a_finding_left_past_two_content_rounds_goes_to_the_user_as_a_proposal")
def test_a_round_put_up_and_unweighed_waits_on_the_signoff(results: str):
    """Given the command whose content-1, judged good, is put up with the node's state, unweighed
    When what it waits on is asked
    Then it waits on the sign-off, as the put-up comes after the weighing"""
    done = unweighed(rounds(results, ("content", 1, MADE_ALL, GOOD, GOOD_PUT_UP)))
    assert next_of(node(good=True, folder=results), done, False) == Next("sign-off", None, False)


@pytest.mark.supports("test_a_finding_left_past_two_content_rounds_goes_to_the_user_as_a_proposal")
def test_asked_gives_each_open_decision_but_the_proposals_past_the_limit(results: str):
    """Given the command with an open decision of N1, not good, and one of N2, good: with no
    Round, and past LIMIT Rounds of content with N1 short
    When the decisions that wait on the user's answer are asked
    Then they're both with no Round, and N2's alone past the limit, N1's being a proposal"""
    given = node(good=["N2", "N3"], open_decision=True)
    given["necessary_conditions"][1]["decisions"].append(rn_files.decision("the currency", None))
    both = [
        {"condition": "N1", "about": "a comma in a line"},
        {"condition": "N2", "about": "the currency"},
    ]
    assert asked(given, [], []) == both
    past = rounds(results, *[("content", n, MADE_ALL, SHORT) for n in range(1, LIMIT + 1)])
    assert asked(given, past, []) == both[1:]


# The generator resuming the last Round, where its last result is `point`.


@pytest.mark.supports(
    "test_a_resumed_generator_after_its_answer_ends_with_made_and_the_evaluator_is_due"
)
def test_a_point_answered_resumes_the_generator_in_its_round(results: str):
    """Given the command whose generator gave a point in content-1, now answered by the user
    When what it waits on is asked
    Then the generator resumes the last Round, of the stage content"""
    done = rounds(results, ("content", 1, POINTED, None))
    assert next_of(node(folder=results), done, False) == Next("generator", "content", True)


@pytest.mark.supports(
    "test_a_resumed_generator_after_its_answer_ends_with_made_and_the_evaluator_is_due"
)
def test_a_point_answered_in_a_later_round_resumes_that_one(results: str):
    """Given the command judged short in content-1, whose generator gave a point in content-2, now
    answered
    When what it waits on is asked
    Then the generator resumes content-2, the last Round, and not the first"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", 2, POINTED, None))
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next(
        "generator", "content", True
    )


@pytest.mark.supports(
    "test_a_resumed_generator_after_its_answer_ends_with_made_and_the_evaluator_is_due"
)
def test_a_point_answered_in_a_refactor_round_resumes_it(results: str):
    """Given the guide-like command, refactored, judged good in content-1, whose generator gave a
    point in refactor-2, now answered
    When what it waits on is asked
    Then the generator resumes refactor-2"""
    done = rounds(results, ("content", 1, MADE_ALL, GOOD), ("refactor", 2, POINTED, None))
    assert next_of(node(True, folder=results), done, True) == Next("generator", "refactor", True)


# The evaluator in the last Round, where the generator made it and the evaluator wrote nothing.


@pytest.mark.supports("test_a_generators_made_makes_the_evaluator_due_in_the_same_round")
def test_a_round_made_with_no_evaluator_yet_waits_on_the_evaluator(results: str):
    """Given the command made in content-1, no evaluator's result yet
    When what it waits on is asked
    Then the evaluator in the last Round, of the stage content"""
    done = rounds(results, ("content", 1, MADE_ALL, None))
    assert next_of(node(folder=results), done, False) == Next("evaluator", "content", False)


@pytest.mark.supports("test_no_evaluator_is_due_after_a_refactor_round")
def test_a_refactor_round_made_waits_on_no_evaluator(results: str):
    """Given the command judged good in content-1 and made in refactor-2, no evaluator's result in
    it
    When what it waits on is asked
    Then the sign-off, as no evaluator judges a refactor Round"""
    done = rounds(results, ("content", 1, MADE_ALL, GOOD), ("refactor", 2, MADE_ALL, None))
    assert next_of(node(True, folder=results), done, True) == Next("sign-off", None, False)


@pytest.mark.supports("test_a_pause_while_the_evaluator_tries_pushes_its_cut")
def test_a_round_made_after_an_earlier_one_judged_waits_on_its_evaluator(results: str):
    """Given the command judged short in content-1 and made in content-2, its evaluator stopped by
    a pause with no result
    When what it waits on is asked
    Then the evaluator in content-2, the last Round, and not a new Round from content-1's
    findings"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", 2, MADE_ALL, None))
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next(
        "evaluator", "content", False
    )


# The generator in a new content Round, where there's no Round yet.


@pytest.mark.supports(
    "test_a_signoff_of_the_plan_makes_it_done_and_starts_the_generator_of_each_deliverable_due"
)
@pytest.mark.parametrize("refactors", [False, True])
def test_no_round_yet_waits_on_the_generator_in_a_new_content_round(results: str, refactors: bool):
    """Given the command with no Round and no open decision, its kind refactored or not
    When what it waits on is asked
    Then the generator in a new Round of the stage content"""
    assert next_of(node(folder=results), [], refactors) == Next("generator", "content", False)


# A condition not good: a new Round of the last stage below LIMIT, else the pruner.


@pytest.mark.supports("test_the_generators_cut_holds_the_pruners_remedy_and_no_evaluators_finding")
def test_a_condition_short_after_one_content_round_gets_another(results: str):
    """Given the command judged short on N1 in content-1, LIMIT being 2
    When what it waits on is asked
    Then the generator in a new content Round"""
    assert LIMIT == 2
    done = rounds(results, ("content", 1, MADE_ALL, SHORT))
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next(
        "generator", "content", False
    )


@pytest.mark.supports("test_a_deliverable_short_after_two_content_rounds_gets_no_third")
def test_a_condition_short_after_limit_content_rounds_waits_on_the_pruner(results: str):
    """Given the command judged short on N1 in content-1 and content-2, LIMIT Rounds of content
    When what it waits on is asked
    Then the pruner, with no stage, as no third content Round comes"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", 2, MADE_ALL, SHORT))
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next("pruner", None, False)


# The user's decisions that a Round's generator was given in its Cut: none, as before the user
# answered, and the tax rate, the answer that node() holds.
BEFORE_ANSWER: frozenset[tuple[str, str]] = frozenset()
WITH_ANSWER = frozenset({("N1", "the tax rate")})


@pytest.mark.supports("test_a_users_answer_after_two_content_rounds_gets_a_new_content_round")
def test_a_users_answer_after_limit_content_rounds_starts_the_course_again(results: str):
    """Given the command judged short on N1 in content-1 and content-2, LIMIT Rounds, neither
    generator given the user's answer on N1 that the node holds now
    When what it waits on is asked
    Then the generator in a new content Round, as the limit stops a remake asked by findings, and
    the user's answer starts the course again"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", 2, MADE_ALL, SHORT))
    done = [each._replace(given=BEFORE_ANSWER) for each in done]
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next(
        "generator", "content", False
    )


@pytest.mark.supports("test_a_users_answer_after_two_content_rounds_gets_a_new_content_round")
def test_limit_content_rounds_after_a_users_answer_wait_on_the_pruner(results: str):
    """Given the command judged short on N1 in content-1 and content-2, neither generator given the
    user's answer on N1, then short in content-3 and content-4, each generator given it
    When what it waits on is asked
    Then the pruner, as the course since the answer has LIMIT Rounds"""
    done = rounds(
        results,
        ("content", 1, MADE_ALL, SHORT),
        ("content", 2, MADE_ALL, SHORT),
        ("content", 3, MADE_ALL, SHORT),
        ("content", 4, MADE_ALL, SHORT),
    )
    given = [BEFORE_ANSWER, BEFORE_ANSWER, WITH_ANSWER, WITH_ANSWER]
    done = [each._replace(given=g) for each, g in zip(done, given)]
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next("pruner", None, False)


@pytest.mark.supports("test_a_deliverable_short_after_two_content_rounds_gets_no_third")
def test_limit_content_rounds_each_given_the_users_answer_wait_on_the_pruner(results: str):
    """Given the command judged short on N1 in content-1 and content-2, each generator given the
    user's answer on N1 that the node holds
    When what it waits on is asked
    Then the pruner, as no answer came since the Rounds"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", 2, MADE_ALL, SHORT))
    done = [each._replace(given=WITH_ANSWER) for each in done]
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next("pruner", None, False)


# The remedies in the node that a Round's generator was given in its Cut, by condition, about, and
# decided: none, as node() holds the user's answer alone, which is no remedy.
NO_REMEDY: frozenset[tuple[str, str, str]] = frozenset()
REMEDY = rn_files.decision("a comma in a line", "A line's comma is read as a decimal.", "maker")


def remedied(results: str, open_decision: bool = False) -> Any:
    """The command's node with N1 not good, holding the remedy that the pruner wrote of a finding
    beside the user's answer, and, where `open_decision`, an open one; read back from JSON."""
    given = node(["N2", "N3"], open_decision)
    given["necessary_conditions"][0]["decisions"].append(REMEDY)
    return read_back(results, "remedied", given)


@pytest.mark.supports("test_a_pruners_remedy_after_two_content_rounds_gets_a_new_content_round")
@pytest.mark.parametrize("count", [LIMIT, LIMIT + 1])
def test_a_remedy_written_since_the_last_cut_past_limit_gets_a_new_content_round(
    results: str, count: int
):
    """Given the command judged short on N1 in <count> content Rounds, LIMIT or one past it, each
    generator's Cut given the user's answer and holding no remedy, and the node now holding the
    remedy that the pruner wrote of the last finding
    When what it waits on is asked
    Then the generator in a new content Round, as the limit stops only a remake that the pruner
    gave no remedy for"""
    done = rounds(results, *[("content", n, MADE_ALL, SHORT) for n in range(1, count + 1)])
    done = [each._replace(given=WITH_ANSWER, remedies=NO_REMEDY) for each in done]
    assert next_of(remedied(results), done, False) == Next("generator", "content", False)


@pytest.mark.supports("test_a_pruners_remedy_after_two_content_rounds_gets_a_new_content_round")
def test_a_remedy_past_limit_with_an_open_decision_waits_on_the_answer(results: str):
    """Given the command judged short on N1 in LIMIT content Rounds, and the node now holding a
    remedy of N1 beside an open decision of N1, a point the pruner left for the user
    When what it waits on is asked
    Then the answer, as the next Round makes by the point once it's settled"""
    done = rounds(results, *[("content", n, MADE_ALL, SHORT) for n in range(1, LIMIT + 1)])
    done = [each._replace(given=WITH_ANSWER, remedies=NO_REMEDY) for each in done]
    assert next_of(remedied(results, True), done, False) == Next("answer", None, False)


@pytest.mark.supports("test_a_deliverable_short_after_two_content_rounds_gets_no_third")
@pytest.mark.parametrize(
    ("open_decision", "waits_on"), [(False, "pruner"), (True, "sign-off")], ids=["none", "kept"]
)
def test_no_remedy_since_the_last_cut_past_limit_leaves_the_findings_to_the_user(
    results: str, open_decision: bool, waits_on: str
):
    """Given the command judged short on N1 in LIMIT content Rounds, the last generator's Cut
    holding no remedy, and the node holding the user's answer alone, no remedy, and no open
    decision, or the finding kept as one
    When what it waits on is asked
    Then the pruner, to keep each finding left, or the sign-off with the finding as a proposal, as
    no remedy came since the last Cut"""
    done = rounds(results, *[("content", n, MADE_ALL, SHORT) for n in range(1, LIMIT + 1)])
    done = [each._replace(given=WITH_ANSWER, remedies=NO_REMEDY) for each in done]
    left = node(["N2", "N3"], open_decision, folder=results)
    assert next_of(left, done, False) == Next(waits_on, None, False)


@pytest.mark.supports("test_a_send_back_after_the_refactor_round_is_remade_in_a_new_content_round")
@pytest.mark.parametrize("content", sorted({1, LIMIT}))
def test_a_condition_short_after_the_refactor_round_gets_a_new_content_round(
    results: str, content: int
):
    """Given the command judged good in content-<content>, below LIMIT or at it, each Round before
    it judged short, then made in refactor-<content + 1>, put up, and the node holding N1 not
    good, as a send-back holds it
    When what it waits on is asked
    Then the generator in a new content Round, as the send-back starts the course again, whatever
    the content took before"""
    each = [("content", n, MADE_ALL, SHORT) for n in range(1, content)]
    done = rounds(
        results,
        *each,
        ("content", content, MADE_ALL, GOOD),
        ("refactor", content + 1, MADE_ALL, None, GOOD_PUT_UP),
    )
    assert next_of(node(["N2", "N3"], folder=results), done, True) == Next(
        "generator", "content", False
    )


@pytest.mark.supports("test_a_send_back_after_the_refactor_round_is_remade_in_a_new_content_round")
def test_a_content_round_after_a_round_put_up_counts_alone_toward_the_limit(results: str):
    """Given the command judged short in content-1 and good in content-2, made in refactor-3, put
    up, then judged short on N1 in content-4, after a send-back
    When what it waits on is asked
    Then the generator in a new content Round, as the course since refactor-3 holds one Round,
    fewer than LIMIT"""
    done = rounds(
        results,
        ("content", 1, MADE_ALL, SHORT),
        ("content", 2, MADE_ALL, GOOD),
        ("refactor", 3, MADE_ALL, None, GOOD_PUT_UP),
        ("content", 4, MADE_ALL, SHORT),
    )
    assert next_of(node(["N2", "N3"], folder=results), done, True) == Next(
        "generator", "content", False
    )


@pytest.mark.supports("test_a_deliverable_short_after_two_content_rounds_gets_no_third")
def test_limit_content_rounds_after_a_round_put_up_wait_on_the_pruner(results: str):
    """Given the command judged good in content-1, made in refactor-2, put up, then judged short
    on N1 in content-3 and content-4, LIMIT Rounds since refactor-2
    When what it waits on is asked
    Then the pruner, as the course again has LIMIT Rounds"""
    done = rounds(
        results,
        ("content", 1, MADE_ALL, GOOD),
        ("refactor", 2, MADE_ALL, None, GOOD_PUT_UP),
        ("content", 3, MADE_ALL, SHORT),
        ("content", 4, MADE_ALL, SHORT),
    )
    assert next_of(node(["N2", "N3"], folder=results), done, True) == Next("pruner", None, False)


@pytest.mark.supports("test_a_send_back_after_the_refactor_round_is_remade_in_a_new_content_round")
def test_each_condition_good_after_a_content_round_past_the_refactor_round_refactors_again(
    results: str,
):
    """Given a refactored kind's command judged good in content-1, made in refactor-2, put up, then
    judged good in content-3, after a send-back
    When what it waits on is asked
    Then the generator in a new refactor Round, as a refactor Round follows the content again"""
    done = rounds(
        results,
        ("content", 1, MADE_ALL, GOOD),
        ("refactor", 2, MADE_ALL, None, GOOD_PUT_UP),
        ("content", 3, MADE_ALL, GOOD),
    )
    assert next_of(node(True, folder=results), done, True) == Next("generator", "refactor", False)


@pytest.mark.supports("test_the_generators_cut_holds_the_pruners_remedy_and_no_evaluators_finding")
def test_a_condition_the_node_holds_short_counts_though_the_evaluator_found_it_good(results: str):
    """Given the command judged good on each condition in content-1, the node holding N1 not good
    When what it waits on is asked
    Then the generator in a new content Round, as the node's conditions decide, not the
    evaluator's"""
    done = rounds(results, ("content", 1, MADE_ALL, GOOD))
    assert next_of(node(["N2", "N3"], folder=results), done, True) == Next(
        "generator", "content", False
    )


# Each condition good: a refactor Round where the kind is refactored and has none, else sign-off.


@pytest.mark.supports(
    "test_a_deliverable_with_each_condition_good_is_refactored_by_its_refactor_best_practice"
)
def test_each_condition_good_after_content_gets_a_refactor_round(results: str):
    """Given a refactored kind's deliverable judged good in content-1, each condition good
    When what it waits on is asked
    Then the generator in a new refactor Round"""
    done = rounds(results, ("content", 1, MADE_ALL, GOOD))
    assert next_of(node(True, folder=results), done, True) == Next("generator", "refactor", False)


@pytest.mark.supports("test_the_refactoring_generators_made_waits_on_the_signoff_with_no_evaluator")
def test_each_condition_good_after_a_refactor_round_waits_on_the_signoff(results: str):
    """Given a refactored kind's deliverable judged short in content-1 and good in content-2, and
    made in refactor-3
    When what it waits on is asked
    Then the sign-off, and not a second refactor Round"""
    done = rounds(
        results,
        ("content", 1, MADE_ALL, SHORT),
        ("content", 2, MADE_ALL, GOOD),
        ("refactor", 3, MADE_ALL, None),
    )
    assert next_of(node(True, folder=results), done, True) == Next("sign-off", None, False)


@pytest.mark.supports(
    "test_a_finding_the_people_would_never_meet_is_dropped_by_holding_its_condition_good"
)
def test_each_condition_good_of_a_kind_not_refactored_waits_on_the_signoff(results: str):
    """Given the command, of the kind light, which isn't refactored, judged short on N1 in
    content-1, the pruner holding N1 good as its people would never meet it
    When what it waits on is asked
    Then the sign-off"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT))
    assert next_of(node(True, folder=results), done, False) == Next("sign-off", None, False)


@pytest.mark.supports("test_a_deliverable_short_after_two_content_rounds_gets_no_third")
def test_each_condition_good_after_limit_content_rounds_isnt_held_back_by_the_limit(results: str):
    """Given a refactored kind's deliverable judged short in content-1 and good in content-2
    When what it waits on is asked
    Then the generator in a new refactor Round, the limit counting content alone"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", 2, MADE_ALL, GOOD))
    assert next_of(node(True, folder=results), done, True) == Next("generator", "refactor", False)


# A pause that leaves a Round with its Cut and no result.


@pytest.mark.supports(
    "test_a_pick_up_starts_the_stopped_generator_again_in_its_round_with_a_fresh_cut"
)
def test_a_round_whose_generator_was_stopped_resumes_it_there(results: str):
    """Given the command whose generator, in content-1, was stopped by a pause before it wrote a
    result
    When what it waits on is asked
    Then the generator in the last Round again, content-1, as S2 starts each role stopped again
    from the Round's files, not a new Round"""
    done = rounds(results, ("content", 1, None, None))
    assert next_of(node(folder=results), done, False) == Next("generator", "content", True)


@pytest.mark.supports(
    "test_a_pick_up_starts_the_stopped_generator_again_in_its_round_with_a_fresh_cut"
)
def test_a_second_round_whose_generator_was_stopped_resumes_it_there(results: str):
    """Given the command judged short in content-1, whose generator, in content-2, was stopped by a
    pause before it wrote a result
    When what it waits on is asked
    Then the generator in content-2 again, not the pruner, as the Round was never made"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", 2, None, None))
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next(
        "generator", "content", True
    )


@pytest.mark.supports(
    "test_a_pick_up_starts_the_stopped_generator_again_in_its_round_with_a_fresh_cut"
)
def test_a_refactor_round_whose_generator_was_stopped_resumes_it_there(results: str):
    """Given a refactored kind's command judged good in content-1, whose generator, in refactor-2,
    was stopped by a pause before it wrote a result
    When what it waits on is asked
    Then the generator in refactor-2 again, not a new refactor Round or the sign-off"""
    done = rounds(results, ("content", 1, MADE_ALL, GOOD), ("refactor", 2, None, None))
    assert next_of(node(True, folder=results), done, True) == Next("generator", "refactor", True)


@pytest.mark.supports(
    "test_a_pick_up_starts_the_stopped_generator_again_in_its_round_with_a_fresh_cut"
)
def test_a_round_at_limit_whose_generator_was_stopped_resumes_it_not_the_pruner(
    results: str,
):
    """Given the command judged short in content-1, and the LIMIT-th Round, content-2, whose
    generator a pause stopped before it wrote a result
    When what it waits on is asked
    Then the generator in content-2 again, spending no Round, as the stopped Round was never
    made"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", LIMIT, None, None))
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next(
        "generator", "content", True
    )


@pytest.mark.supports("test_a_pick_up_starts_the_stopped_evaluator_again_in_its_round")
@pytest.mark.parametrize("number", [1, LIMIT])
def test_a_round_whose_evaluator_was_stopped_waits_on_the_evaluator_there(
    results: str, number: int
):
    """Given the command made in content-<number>, Round 1 or the LIMIT-th, each Round before it
    judged short, its evaluator stopped by a pause before it wrote a result
    When what it waits on is asked
    Then the evaluator in that Round"""
    each = [("content", n, MADE_ALL, SHORT) for n in range(1, number)]
    done = rounds(results, *each, ("content", number, MADE_ALL, None))
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next(
        "evaluator", "content", False
    )


# The sign-off past the limit, with the findings left kept as open decisions.


@pytest.mark.supports("test_a_finding_left_past_two_content_rounds_goes_to_the_user_as_a_proposal")
def test_findings_kept_open_past_limit_content_rounds_wait_on_the_signoff(results: str):
    """Given the command judged short on N1 in content-1 and content-2, LIMIT Rounds each with
    both results, and the finding left kept as an open decision of N1
    When what it waits on is asked
    Then the sign-off, before the answer that the open decision would ask"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", 2, MADE_ALL, SHORT))
    assert next_of(node(["N2", "N3"], open_decision=True, folder=results), done, False) == Next(
        "sign-off", None, False
    )


@pytest.mark.supports("test_a_send_back_past_the_contents_limit_is_remade_in_rounds_of_its_own")
def test_a_round_put_up_with_each_condition_good_waits_on_the_signoff(results: str):
    """Given a refactored kind's command judged good in content-1, made in refactor-2, put up, each
    condition good
    When what it waits on is asked
    Then the sign-off, as the mark ends its Rounds with no send-back"""
    done = rounds(
        results, ("content", 1, MADE_ALL, GOOD), ("refactor", 2, MADE_ALL, None, GOOD_PUT_UP)
    )
    assert next_of(node(True, folder=results), done, True) == Next("sign-off", None, False)


@pytest.mark.supports("test_a_send_back_past_the_contents_limit_is_remade_in_rounds_of_its_own")
def test_proposals_kept_at_a_round_put_up_past_the_limit_wait_on_the_signoff(results: str):
    """Given the command judged short on N1 in content-1 and content-2, content-2 put up, with the
    finding left kept as an open decision of N1
    When what it waits on is asked
    Then the sign-off, as the user hasn't sent it back"""
    done = rounds(
        results, ("content", 1, MADE_ALL, SHORT), ("content", 2, MADE_ALL, SHORT, LEFT_PUT_UP)
    )
    assert next_of(node(["N2", "N3"], open_decision=True, folder=results), done, False) == Next(
        "sign-off", None, False
    )


@pytest.mark.supports("test_a_send_back_past_the_contents_limit_is_remade_in_rounds_of_its_own")
@pytest.mark.parametrize("put_up", [True, False])
def test_a_send_back_past_the_limit_gets_a_new_content_round_once_put_up(
    results: str, put_up: bool
):
    """Given the command judged short in content-1 and good in content-2, LIMIT Rounds, put up or
    not, and the node holding N1 not good with no open decision, as a send-back holds it
    When what it waits on is asked
    Then, put up, the generator in a new content Round, as the send-back gets Rounds of its own;
    else the pruner, as findings left past the limit wait on it"""
    second = ("content", 2, MADE_ALL, GOOD, *([GOOD_PUT_UP] if put_up else []))
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), second)
    expected = Next("generator", "content", False) if put_up else Next("pruner", None, False)
    assert next_of(node(["N2", "N3"], folder=results), done, False) == expected


@pytest.mark.supports("test_a_send_back_past_the_contents_limit_is_remade_in_rounds_of_its_own")
def test_a_send_back_settling_the_proposal_gets_a_new_content_round(results: str):
    """Given the command judged short on N1 in content-1 and content-2, content-2 put up with the
    finding left kept as an open decision of N1, then sent back, the user's words settling it
    When what it waits on is asked
    Then the generator in a new content Round, as the state put up changed"""
    done = rounds(
        results, ("content", 1, MADE_ALL, SHORT), ("content", 2, MADE_ALL, SHORT, LEFT_PUT_UP)
    )
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next(
        "generator", "content", False
    )


@pytest.mark.supports("test_a_deliverable_whose_point_waits_on_the_user_gets_no_cut")
def test_a_new_point_on_a_condition_not_good_after_a_round_put_up_waits_on_the_answer(
    results: str,
):
    """Given a refactored kind's command judged good in content-1, made in refactor-2, put up with
    each condition good, then held not good on N1 with an open decision of N1, a point of the
    pruner's after a send-back
    When what it waits on is asked
    Then the answer, as a decision opened since the Round put up is a point, not a proposal"""
    done = rounds(
        results, ("content", 1, MADE_ALL, GOOD), ("refactor", 2, MADE_ALL, None, GOOD_PUT_UP)
    )
    assert next_of(node(["N2", "N3"], open_decision=True, folder=results), done, True) == Next(
        "answer", None, False
    )


@pytest.mark.supports("test_a_deliverable_whose_point_waits_on_the_user_gets_no_cut")
def test_an_open_decision_of_a_good_condition_after_a_round_put_up_waits_on_the_answer(
    results: str,
):
    """Given a refactored kind's command judged good in content-1, made in refactor-2, put up, the
    node holding N1 not good after a send-back, with an open decision of N1 and of N2, good
    When what it waits on is asked
    Then the answer, as an open decision of a condition good is a point"""
    done = rounds(
        results, ("content", 1, MADE_ALL, GOOD), ("refactor", 2, MADE_ALL, None, GOOD_PUT_UP)
    )
    assert next_of(with_open(["N2", "N3"], ["N1", "N2"], results), done, True) == Next(
        "answer", None, False
    )


@pytest.mark.supports("test_a_finding_left_past_two_content_rounds_goes_to_the_user_as_a_proposal")
def test_findings_kept_open_past_limit_rounds_after_a_round_put_up_wait_on_the_signoff(
    results: str,
):
    """Given a refactored kind's command judged good in content-1, made in refactor-2, put up, then
    judged short on N1 in content-3 and content-4, and the finding left kept as an open decision
    of N1
    When what it waits on is asked
    Then the sign-off, as the course since refactor-2 has LIMIT Rounds, each with both results"""
    done = rounds(
        results,
        ("content", 1, MADE_ALL, GOOD),
        ("refactor", 2, MADE_ALL, None, GOOD_PUT_UP),
        ("content", 3, MADE_ALL, SHORT),
        ("content", 4, MADE_ALL, SHORT),
    )
    assert next_of(node(["N2", "N3"], open_decision=True, folder=results), done, True) == Next(
        "sign-off", None, False
    )


@pytest.mark.supports("test_a_deliverable_short_after_two_content_rounds_gets_no_third")
def test_an_open_decision_below_limit_waits_on_the_answer_not_the_signoff(results: str):
    """Given the command judged short on N1 in content-1 alone, one Round below LIMIT, and an
    open decision of N1
    When what it waits on is asked
    Then the answer, as the stage hasn't LIMIT Rounds"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT))
    assert next_of(node(["N2", "N3"], open_decision=True, folder=results), done, False) == Next(
        "answer", None, False
    )


@pytest.mark.supports("test_a_deliverable_whose_point_waits_on_the_user_gets_no_cut")
def test_a_point_open_in_the_limit_round_waits_on_the_answer_not_the_signoff(results: str):
    """Given the command judged short in content-1, whose generator gave a point in content-2, the
    LIMIT-th Round, kept as an open decision of N1, with no evaluator's result
    When what it waits on is asked
    Then the answer, as the LIMIT-th Round lacks its evaluator's result"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", 2, POINTED, None))
    assert next_of(node(["N2", "N3"], open_decision=True, folder=results), done, False) == Next(
        "answer", None, False
    )


@pytest.mark.supports("test_a_deliverable_short_after_two_content_rounds_gets_no_third")
def test_limit_rounds_judged_with_no_decision_open_wait_on_the_pruner(results: str):
    """Given the command judged short on N1 in content-1 and content-2, and no decision open, as
    the pruner hasn't kept the finding left yet
    When what it waits on is asked
    Then the pruner, to keep it, and not the sign-off"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", 2, MADE_ALL, SHORT))
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next("pruner", None, False)


@pytest.mark.supports("test_a_deliverable_whose_point_waits_on_the_user_gets_no_cut")
def test_a_point_open_in_the_refactor_round_waits_on_the_answer_not_the_signoff(results: str):
    """Given a refactored kind's command judged short on N1 in content-1 and content-2, LIMIT
    Rounds each with both results, whose generator gave a point in refactor-3, kept as an open
    decision of N1, the node holding N1 not good
    When what it waits on is asked
    Then the answer, as the last Round is the refactor Round, not the course's LIMIT-th"""
    done = rounds(
        results,
        ("content", 1, MADE_ALL, SHORT),
        ("content", 2, MADE_ALL, SHORT),
        ("refactor", 3, POINTED, None),
    )
    assert next_of(node(["N2", "N3"], open_decision=True, folder=results), done, True) == Next(
        "answer", None, False
    )


# Past the limit, an open decision of a condition not good is a proposal, and one of a condition
# good a point: the decision table of which open decisions the node holds.


def with_open(good: Sequence[str], on: Sequence[str], folder: str) -> Any:
    """The command's open node, its conditions good as given, with an open decision of each
    condition of `on`, read back from JSON."""
    given = rn_files.decided(
        rn_files.open_node(rn_files.COMMAND_NAME, COMMAND, "light", ["invoicer/lines.py"], good),
        {each: [rn_files.decision(f"the point of {each}", None)] for each in on},
    )
    return read_back(folder, "node", given)


@pytest.mark.supports("test_a_finding_left_past_two_content_rounds_goes_to_the_user_as_a_proposal")
@pytest.mark.parametrize(
    ("good", "on", "waits_on"),
    [
        (["N2", "N3"], ["N1"], "sign-off"),
        (["N3"], ["N1", "N2"], "sign-off"),
        (["N1", "N2", "N3"], ["N1"], "answer"),
        (["N2", "N3"], ["N2"], "answer"),
        (["N2", "N3"], ["N1", "N2"], "answer"),
        (["N3"], ["N1"], "pruner"),
    ],
)
def test_open_decisions_past_limit_are_proposals_of_conditions_not_good_and_points_of_good_ones(
    results: str, good: list[str], on: list[str], waits_on: str
):
    """Given the command judged short in content-1 and content-2, LIMIT Rounds each with both
    results, its conditions good as given, and an open decision of each condition of `on`
    When what it waits on is asked
    Then the sign-off where each open decision is of a condition not good and each condition not
    good keeps one; the answer where an open decision is of a condition good, a point; and the
    pruner where a condition not good keeps none yet"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", 2, MADE_ALL, SHORT))
    assert next_of(with_open(good, on, results), done, False) == Next(waits_on, None, False)


@pytest.mark.supports("test_a_deliverable_whose_point_waits_on_the_user_gets_no_cut")
@pytest.mark.parametrize("number", sorted({1, LIMIT - 1}))
def test_an_open_decision_of_a_condition_not_good_below_limit_is_a_point(results: str, number: int):
    """Given the command judged short on N1 in content-1 to content-<number>, below LIMIT, and an
    open decision of N1
    When what it waits on is asked
    Then the answer, as below the limit an open decision is a point, not a proposal"""
    done = rounds(results, *[("content", each, MADE_ALL, SHORT) for each in range(1, number + 1)])
    assert next_of(with_open(["N2", "N3"], ["N1"], results), done, False) == Next(
        "answer", None, False
    )


# The Fixes after the Rounds.

FIXED = {"result": "fixed", "files": [COMMAND]}
DECISION = {"result": "decision", "decision": "N1 decides the lines as the user wrote them."}


def a_fix(
    folder: str, number: int, fixer: Any = None, given: Any = None, weighed: str | None = None
) -> Mend:
    """The command's Fix fix-<number>, with the fixer's result, None where it wrote none, the node
    its Cut held, None where it holds no Cut, each read back from JSON, and the commit that
    weighed it, None where none did."""
    place = rn_files.round_of(os.path.join(folder, "run"), COMMAND, "fix", number)
    result = None if fixer is None else read_back(folder, f"f-{number}", fixer)
    node_given = None if given is None else read_back(folder, f"n-{number}", given)
    return Mend(Fix(place, COMMAND, number), result, node_given, weighed)


def judged_good(folder: str) -> list[Done]:
    """The command judged good in content-1, put up with each condition good."""
    return rounds(folder, ("content", 1, MADE_ALL, GOOD, GOOD_PUT_UP))


@pytest.mark.supports("test_a_fix_counts_toward_no_limit_of_the_rounds")
def test_with_no_fix_it_waits_on_what_next_of_gives(results: str):
    """Given the command made in content-1 with no evaluator yet, and no Fix
    When what it waits on is asked with its Fixes
    Then the evaluator in content-1, as next_of gives it"""
    done = rounds(results, ("content", 1, MADE_ALL, None))
    assert next_with_fixes(node(folder=results), done, [], False) == Next(
        "evaluator", "content", False
    )


@pytest.mark.supports("test_a_mend_within_the_decisions_starts_its_fixer_at_once_with_no_pruner")
def test_a_fix_with_no_cut_waits_on_a_new_fixer(results: str):
    """Given the command judged good in content-1 and put up, and fix-2 holding its problem alone
    When what it waits on is asked
    Then the fixer, of the stage fix, a new one"""
    assert next_with_fixes(
        node(True, folder=results), judged_good(results), [a_fix(results, 2)], False
    ) == Next("fixer", "fix", False)


@pytest.mark.supports("test_a_pick_up_starts_the_stopped_fixer_again_in_its_fix_with_a_fresh_cut")
def test_a_fix_whose_fixer_was_stopped_resumes_it(results: str):
    """Given the command judged good in content-1, and fix-2 whose fixer's Cut holds the node, and
    no fixer's result, as a pause stopped it
    When what it waits on is asked
    Then the fixer, of the stage fix, resuming"""
    held_node = node(True, folder=results)
    fixes = [a_fix(results, 2, given=held_node)]
    assert next_with_fixes(held_node, judged_good(results), fixes, False) == Next(
        "fixer", "fix", True
    )


@pytest.mark.supports(
    "test_a_put_up_that_the_repositorys_push_check_refuses_is_mended_by_a_fix_and_put_up_again"
)
@pytest.mark.parametrize("cut", [True, False], ids=["the node its Cut held", "no Cut"])
def test_a_fix_fixed_waits_on_the_signoff(results: str, cut: bool):
    """Given the command judged good in content-1, and fix-2 fixed, its fixer's Cut holding the
    node as it stands, or no Cut
    When what it waits on is asked
    Then the sign-off, for the command to be put up again"""
    held_node = node(True, folder=results)
    fixes = [a_fix(results, 2, FIXED, held_node if cut else None)]
    assert next_with_fixes(held_node, judged_good(results), fixes, False) == Next(
        "sign-off", None, False
    )


@pytest.mark.supports(
    "test_a_fixers_decision_goes_to_one_pruner_and_the_deliverable_takes_content_rounds_again"
)
def test_a_fixs_decision_waits_on_the_pruner_to_weigh_it(results: str):
    """Given the command judged good in content-1, and fix-2 whose fixer named a decision, its Cut
    holding the node as it stands
    When what it waits on is asked
    Then the pruner, of the stage fix"""
    held_node = node(True, folder=results)
    fixes = [a_fix(results, 2, DECISION, held_node)]
    assert next_with_fixes(held_node, judged_good(results), fixes, False) == Next(
        "pruner", "fix", False
    )


@pytest.mark.supports("test_a_fixers_decision_that_the_pruner_cuts_ends_the_fix")
@pytest.mark.parametrize("status", ["open", "done"])
def test_a_fixs_decision_weighed_with_the_node_unchanged_waits_on_the_signoff(
    results: str, status: str
):
    """Given the command, open or done, judged good in content-1 and put up, and fix-2 whose fixer
    named a decision, its Cut holding the node as it stands, and a commit of the tree since,
    the pruner having cut the decision
    When what it waits on is asked
    Then the sign-off, as the Fix is over and the command is back where its Rounds were over"""
    held_node = node(True, folder=results)
    held_node["status"] = status
    fixes = [a_fix(results, 2, DECISION, held_node, "5de44e4")]
    assert next_with_fixes(held_node, judged_good(results), fixes, False) == Next(
        "sign-off", None, False
    )


@pytest.mark.supports(
    "test_a_fixers_decision_goes_to_one_pruner_and_the_deliverable_takes_content_rounds_again"
)
def test_a_fixs_decision_weighed_with_the_node_changed_takes_a_new_content_round(results: str):
    """Given the command judged good in content-1, and fix-2 whose fixer named a decision, its Cut
    holding the node with each condition good, a commit of the tree since, and the node now
    holding N1 not good, as the pruner wrote the decision
    When what it waits on is asked
    Then the generator in a new content Round"""
    fixes = [a_fix(results, 2, DECISION, node(True, folder=results), "5de44e4")]
    assert next_with_fixes(
        node(["N2", "N3"], folder=results), judged_good(results), fixes, False
    ) == Next("generator", "content", False)


@pytest.mark.supports(
    "test_a_fixers_decision_goes_to_one_pruner_and_the_deliverable_takes_content_rounds_again"
)
@pytest.mark.parametrize("fixer", [DECISION, FIXED], ids=["decision", "fixed"])
def test_a_fix_whose_node_changed_since_takes_a_new_content_round(results: str, fixer: Any):
    """Given the command judged short on N1 in content-1 and content-2, LIMIT Rounds, then good,
    and fix-3, its fixer's Cut holding the node with each condition good, and the node now holding
    N1 not good, as a pruner wrote a decision since
    When what it waits on is asked
    Then the generator in a new content Round, as a course anew, the Rounds before the Fix
    counting toward no limit"""
    done = rounds(
        results,
        ("content", 1, MADE_ALL, SHORT),
        ("content", 2, MADE_ALL, GOOD, GOOD_PUT_UP),
    )
    fixes = [a_fix(results, 3, fixer, node(True, folder=results))]
    assert next_with_fixes(node(["N2", "N3"], folder=results), done, fixes, False) == Next(
        "generator", "content", False
    )


@pytest.mark.supports(
    "test_a_fixers_decision_goes_to_one_pruner_and_the_deliverable_takes_content_rounds_again"
)
def test_a_fix_whose_node_changed_to_an_open_decision_waits_on_the_answer(results: str):
    """Given the command judged good in content-1, and fix-2 whose fixer named a decision, its
    Cut holding the node with each condition good, and the node now holding an open decision of
    N1, a point that the pruner left for the user
    When what it waits on is asked
    Then the answer"""
    fixes = [a_fix(results, 2, DECISION, node(True, folder=results))]
    assert next_with_fixes(
        node(["N2", "N3"], open_decision=True, folder=results), judged_good(results), fixes, False
    ) == Next("answer", None, False)


@pytest.mark.supports(
    "test_a_fixers_decision_goes_to_one_pruner_and_the_deliverable_takes_content_rounds_again"
)
def test_rounds_after_a_fix_count_alone_toward_the_limit(results: str):
    """Given the command judged short in content-1 and content-2, fix-3 whose fixer named a
    decision, and content-4 judged short
    When what it waits on is asked
    Then the generator in a new content Round, as content-4 alone counts toward the limit"""
    done = rounds(
        results,
        ("content", 1, MADE_ALL, SHORT),
        ("content", 2, MADE_ALL, SHORT),
        ("content", 4, MADE_ALL, SHORT),
    )
    fixes = [a_fix(results, 3, DECISION, node(True, folder=results))]
    assert next_with_fixes(node(["N2", "N3"], folder=results), done, fixes, False) == Next(
        "generator", "content", False
    )


@pytest.mark.supports(
    "test_a_fixers_decision_goes_to_one_pruner_and_the_deliverable_takes_content_rounds_again"
)
def test_limit_rounds_after_a_fix_wait_on_the_pruner(results: str):
    """Given the command judged good in content-1, fix-2 whose fixer named a decision, and
    content-3 and content-4 judged short, LIMIT Rounds after the Fix
    When what it waits on is asked
    Then the pruner, to keep each finding left"""
    done = rounds(
        results,
        ("content", 1, MADE_ALL, GOOD, GOOD_PUT_UP),
        ("content", 3, MADE_ALL, SHORT),
        ("content", 4, MADE_ALL, SHORT),
    )
    fixes = [a_fix(results, 2, DECISION, node(True, folder=results))]
    assert next_with_fixes(node(["N2", "N3"], folder=results), done, fixes, False) == Next(
        "pruner", None, False
    )


@pytest.mark.supports("test_a_fix_counts_toward_no_limit_of_the_rounds")
def test_fixes_past_limit_rounds_each_wait_on_their_fixer(results: str):
    """Given the command judged short on N1 in content-1 and content-2, LIMIT Rounds, the finding
    kept as an open decision and put up, then fix-3 fixed and fix-4 holding its problem alone
    When what it waits on is asked
    Then the fixer, as no Fix spends a Round of the limit"""
    left = with_open(["N2", "N3"], ["N1"], results)
    done = rounds(
        results,
        ("content", 1, MADE_ALL, SHORT),
        ("content", 2, MADE_ALL, SHORT, LEFT_PUT_UP),
    )
    fixes = [a_fix(results, 3, FIXED, left), a_fix(results, 4)]
    assert next_with_fixes(left, done, fixes, False) == Next("fixer", "fix", False)


# Reading the Fixes from a run's files.

NAME = "20261120-a-command-with-which-the"


@pytest.fixture
def run(tmp_path: Any) -> RunPlace:
    """The walkthrough's run in a repository of the case, its design tree written."""
    repository = os.path.realpath(str(tmp_path))
    rn_files.run_folder(repository, NAME, rn_files.walkthrough_tree(NAME))
    return RunPlace(repository, NAME)


@pytest.mark.supports("test_a_pick_up_starts_the_stopped_fixer_again_in_its_fix_with_a_fresh_cut")
def test_mended_gives_each_fix_with_its_result_and_the_node_its_cut_held(run: RunPlace):
    """Given a run whose command has content-1, fix-2 fixed with its fixer's Cut, and fix-3
    holding its problem alone
    When the command's Fixes are asked
    Then they are fix-2 with its result and node, and fix-3 with neither"""
    folder = rn_files.folder_of(run.repository, NAME)
    rn_files.a_round(folder, COMMAND, "content", 1)
    held_node = node(True)
    second = rn_files.round_of(folder, COMMAND, "fix", 2)
    rn_files.write_json(os.path.join(second, "fixer-cut.json"), {"deliverable": held_node})
    rn_files.write_json(os.path.join(second, "fixer.json"), FIXED)
    third = rn_files.round_of(folder, COMMAND, "fix", 3)
    rn_files.write_json(os.path.join(third, "problem.json"), {"source": "put-up", "words": "x"})
    assert mended(run, COMMAND) == [
        Mend(Fix(second, COMMAND, 2), FIXED, held_node),
        Mend(Fix(third, COMMAND, 3), None, None),
    ]


@pytest.mark.supports("test_a_mend_within_the_decisions_starts_its_fixer_at_once_with_no_pruner")
def test_next_in_reads_the_fixes_of_the_run(run: RunPlace):
    """Given a run whose command has content-1 made and judged good, and fix-2 holding its problem
    alone
    When what the command waits on in the run is asked
    Then the fixer, of the stage fix, a new one"""
    folder = rn_files.folder_of(run.repository, NAME)
    rn_files.a_round(folder, COMMAND, "content", 1, {"generator": MADE_ALL, "evaluator": GOOD})
    fix = rn_files.round_of(folder, COMMAND, "fix", 2)
    rn_files.write_json(os.path.join(fix, "problem.json"), {"source": "put-up", "words": "x"})
    assert next_in(run, node(True)) == Next("fixer", "fix", False)
