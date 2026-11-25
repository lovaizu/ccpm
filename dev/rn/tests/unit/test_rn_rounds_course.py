"""The unit cases of rounds/course.py, which Round a deliverable takes next: one for each row of
next_of's decision table, in the order its contract gives, and each boundary that tells two rows
apart: an open decision with no Round and after a point; the pruner where the last Round's point or
findings are unweighed, before an answer, and the sign-off before it where the Round is put up; a
point answered, which resumes its Round; a Round made with no evaluator yet, of content and of
refactoring, which no evaluator judges; no Round yet; a condition short below LIMIT Rounds of
content and at it; a course started again by the user's answer and by a Round put up, each counting
LIMIT Rounds anew; a remedy that the pruner wrote since the last Cut past LIMIT, alone or beside an
open decision, and none; each condition good, refactored or not; a pause at LIMIT that leaves a
Round with no generator's or no evaluator's result, which spends no Round; proposals kept at a
Round put up, a new point after one, and a point open in the LIMIT-th Round or in a refactor Round;
and the table of which open decisions past the limit are proposals. Then asked, with no Round and
past the limit; next_with_fixes, with the Fixes after the Rounds: none, as next_of; a Fix whose
fixer wrote nothing, its Cut written or not; a Fix fixed, naming a decision, and weighed since; the
node changed since its fixer's Cut; and Rounds after a Fix, which count alone toward the limit; and
mended and next_in, reading the Fixes from a run's files."""

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


def test_an_open_decision_waits_on_the_answer_after_a_point(results: str):
    """Given the command whose generator gave a point in content-1, kept as an open decision of N1
    When what it waits on is asked
    Then it waits on the answer, with no stage, resuming nothing"""
    done = rounds(results, ("content", 1, POINTED, None))
    assert next_of(node(open_decision=True, folder=results), done, False) == Next(
        "answer", None, False
    )


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


def test_a_point_unweighed_waits_on_the_pruner_of_the_stage_point(results: str):
    """Given the command whose generator gave a point in content-1, unweighed, with a decision
    open
    When what it waits on is asked
    Then it waits on the pruner of the stage point, before any answer"""
    done = unweighed(rounds(results, ("content", 1, POINTED, None)))
    assert next_of(node(open_decision=True, folder=results), done, False) == Next(
        "pruner", POINT, False
    )


def test_a_judged_round_unweighed_waits_on_the_pruner_of_the_stage_judged(results: str):
    """Given the command whose evaluator judged content-1 short, unweighed
    When what it waits on is asked
    Then it waits on the pruner of the stage judged, not on a new Round"""
    done = unweighed(rounds(results, ("content", 1, MADE_ALL, SHORT)))
    assert next_of(node(folder=results), done, False) == Next("pruner", JUDGED, False)


def test_a_round_put_up_and_unweighed_waits_on_the_signoff(results: str):
    """Given the command whose content-1, judged good, is put up with the node's state, unweighed
    When what it waits on is asked
    Then it waits on the sign-off, as the put-up comes after the weighing"""
    done = unweighed(rounds(results, ("content", 1, MADE_ALL, GOOD, GOOD_PUT_UP)))
    assert next_of(node(good=True, folder=results), done, False) == Next("sign-off", None, False)


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


def test_a_point_answered_resumes_the_generator_in_its_round(results: str):
    """Given the command whose generator gave a point in content-1, now answered by the user
    When what it waits on is asked
    Then the generator resumes the last Round, of the stage content"""
    done = rounds(results, ("content", 1, POINTED, None))
    assert next_of(node(folder=results), done, False) == Next("generator", "content", True)


# The evaluator in the last Round, where the generator made it and the evaluator wrote nothing.


def test_a_round_made_with_no_evaluator_yet_waits_on_the_evaluator(results: str):
    """Given the command made in content-1, no evaluator's result yet
    When what it waits on is asked
    Then the evaluator in the last Round, of the stage content"""
    done = rounds(results, ("content", 1, MADE_ALL, None))
    assert next_of(node(folder=results), done, False) == Next("evaluator", "content", False)


def test_a_refactor_round_made_waits_on_no_evaluator(results: str):
    """Given the command judged good in content-1 and made in refactor-2, no evaluator's result in
    it
    When what it waits on is asked
    Then the sign-off, as no evaluator judges a refactor Round"""
    done = rounds(results, ("content", 1, MADE_ALL, GOOD), ("refactor", 2, MADE_ALL, None))
    assert next_of(node(True, folder=results), done, True) == Next("sign-off", None, False)


# The generator in a new content Round, where there's no Round yet.


def test_no_round_yet_waits_on_the_generator_in_a_new_content_round(results: str):
    """Given the command with no Round and no open decision, its kind refactored
    When what it waits on is asked
    Then the generator in a new Round of the stage content"""
    assert next_of(node(folder=results), [], True) == Next("generator", "content", False)


# A condition not good: a new Round of the last stage below LIMIT, else the pruner.


def test_a_condition_short_after_one_content_round_gets_another(results: str):
    """Given the command judged short on N1 in content-1, LIMIT being 2
    When what it waits on is asked
    Then the generator in a new content Round"""
    assert LIMIT == 2
    done = rounds(results, ("content", 1, MADE_ALL, SHORT))
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next(
        "generator", "content", False
    )


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


# The remedies in the node that a Round's generator was given in its Cut, by condition, about, and
# decided: none, as node() holds the user's answer alone, which is no remedy.
NO_REMEDY: frozenset[tuple[str, str, str]] = frozenset()
REMEDY = rn_files.decision("a comma in a line", "A line's comma is read as a decimal.", "reasoning")


def remedied(results: str, open_decision: bool = False) -> Any:
    """The command's node with N1 not good, holding the remedy that the pruner wrote of a finding
    beside the user's answer, and, where `open_decision`, an open one; read back from JSON."""
    given = node(["N2", "N3"], open_decision)
    given["necessary_conditions"][0]["decisions"].append(REMEDY)
    return read_back(results, "remedied", given)


def test_a_remedy_written_since_the_last_cut_past_limit_gets_a_new_content_round(results: str):
    """Given the command judged short on N1 in LIMIT content Rounds, each
    generator's Cut given the user's answer and holding no remedy, and the node now holding the
    remedy that the pruner wrote of the last finding
    When what it waits on is asked
    Then the generator in a new content Round, as the limit stops only a remake that the pruner
    gave no remedy for"""
    done = rounds(results, *[("content", n, MADE_ALL, SHORT) for n in range(1, LIMIT + 1)])
    done = [each._replace(given=WITH_ANSWER, remedies=NO_REMEDY) for each in done]
    assert next_of(remedied(results), done, False) == Next("generator", "content", False)


def test_a_remedy_past_limit_with_an_open_decision_waits_on_the_answer(results: str):
    """Given the command judged short on N1 in LIMIT content Rounds, and the node now holding a
    remedy of N1 beside an open decision of N1, a point the pruner left for the user
    When what it waits on is asked
    Then the answer, as the next Round makes by the point once it's settled"""
    done = rounds(results, *[("content", n, MADE_ALL, SHORT) for n in range(1, LIMIT + 1)])
    done = [each._replace(given=WITH_ANSWER, remedies=NO_REMEDY) for each in done]
    assert next_of(remedied(results, True), done, False) == Next("answer", None, False)


def test_no_remedy_since_the_last_cut_past_limit_waits_on_the_pruner(results: str):
    """Given the command judged short on N1 in LIMIT content Rounds, each generator's Cut given
    the user's answer and holding no remedy, and the node holding the user's answer alone, no
    remedy, and no open decision
    When what it waits on is asked
    Then the pruner, to keep each finding left, as no remedy came since the last Cut"""
    done = rounds(results, *[("content", n, MADE_ALL, SHORT) for n in range(1, LIMIT + 1)])
    done = [each._replace(given=WITH_ANSWER, remedies=NO_REMEDY) for each in done]
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next("pruner", None, False)


def test_a_condition_short_after_the_refactor_round_gets_a_new_content_round(results: str):
    """Given the command judged short in content-1 and good in content-2, LIMIT Rounds, then made
    in refactor-3, put up, and the node holding N1 not good, as a send-back holds it
    When what it waits on is asked
    Then the generator in a new content Round, as the send-back starts the course again, whatever
    the content took before"""
    done = rounds(
        results,
        ("content", 1, MADE_ALL, SHORT),
        ("content", 2, MADE_ALL, GOOD),
        ("refactor", 3, MADE_ALL, None, GOOD_PUT_UP),
    )
    assert next_of(node(["N2", "N3"], folder=results), done, True) == Next(
        "generator", "content", False
    )


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


# Each condition good: a refactor Round where the kind is refactored and has none, else sign-off.


def test_each_condition_good_after_content_gets_a_refactor_round(results: str):
    """Given a refactored kind's deliverable judged good in content-1, each condition good
    When what it waits on is asked
    Then the generator in a new refactor Round"""
    done = rounds(results, ("content", 1, MADE_ALL, GOOD))
    assert next_of(node(True, folder=results), done, True) == Next("generator", "refactor", False)


def test_each_condition_good_of_a_kind_not_refactored_waits_on_the_signoff(results: str):
    """Given the command, of the kind light, which isn't refactored, judged short on N1 in
    content-1, the pruner holding N1 good as its people would never meet it
    When what it waits on is asked
    Then the sign-off"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT))
    assert next_of(node(True, folder=results), done, False) == Next("sign-off", None, False)


# A pause that leaves a Round with its Cut and no result.


def test_a_round_at_limit_whose_generator_was_stopped_resumes_it_not_the_pruner(results: str):
    """Given the command judged short in content-1, and the LIMIT-th Round, content-2, whose
    generator a pause stopped before it wrote a result
    When what it waits on is asked
    Then the generator in content-2 again, spending no Round, as the stopped Round was never
    made"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", LIMIT, None, None))
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next(
        "generator", "content", True
    )


def test_a_round_at_limit_whose_evaluator_was_stopped_waits_on_the_evaluator_there(results: str):
    """Given the command judged short in content-1, and made in content-2, the LIMIT-th Round,
    its evaluator stopped by a pause before it wrote a result
    When what it waits on is asked
    Then the evaluator in content-2, not the pruner"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", LIMIT, MADE_ALL, None))
    assert next_of(node(["N2", "N3"], folder=results), done, False) == Next(
        "evaluator", "content", False
    )


# The sign-off past the limit, with the findings left kept as open decisions.


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


def test_a_point_open_in_the_limit_round_waits_on_the_answer_not_the_signoff(results: str):
    """Given the command judged short in content-1, whose generator gave a point in content-2, the
    LIMIT-th Round, kept as an open decision of N1, with no evaluator's result
    When what it waits on is asked
    Then the answer, as the LIMIT-th Round lacks its evaluator's result"""
    done = rounds(results, ("content", 1, MADE_ALL, SHORT), ("content", 2, POINTED, None))
    assert next_of(node(["N2", "N3"], open_decision=True, folder=results), done, False) == Next(
        "answer", None, False
    )


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


@pytest.mark.parametrize(
    ("good", "on", "waits_on"),
    [
        (["N2", "N3"], ["N1"], "sign-off"),
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


def test_with_no_fix_it_waits_on_what_next_of_gives(results: str):
    """Given the command made in content-1 with no evaluator yet, and no Fix
    When what it waits on is asked with its Fixes
    Then the evaluator in content-1, as next_of gives it"""
    done = rounds(results, ("content", 1, MADE_ALL, None))
    assert next_with_fixes(node(folder=results), done, [], False) == Next(
        "evaluator", "content", False
    )


def test_a_fix_with_no_cut_waits_on_a_new_fixer(results: str):
    """Given the command judged good in content-1 and put up, and fix-2 holding its problem alone
    When what it waits on is asked
    Then the fixer, of the stage fix, a new one"""
    assert next_with_fixes(
        node(True, folder=results), judged_good(results), [a_fix(results, 2)], False
    ) == Next("fixer", "fix", False)


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


def test_a_fix_fixed_waits_on_the_signoff(results: str):
    """Given the command judged good in content-1, and fix-2 fixed, with no fixer's Cut
    When what it waits on is asked
    Then the sign-off, for the command to be put up again"""
    held_node = node(True, folder=results)
    fixes = [a_fix(results, 2, FIXED)]
    assert next_with_fixes(held_node, judged_good(results), fixes, False) == Next(
        "sign-off", None, False
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


def test_a_fixs_decision_weighed_with_the_node_unchanged_waits_on_the_signoff(results: str):
    """Given the command, done, judged good in content-1 and put up, and fix-2 whose fixer
    named a decision, its Cut holding the node as it stands, and a commit of the tree since,
    the pruner having cut the decision
    When what it waits on is asked
    Then the sign-off, as the Fix is over and the command is back where its Rounds were over"""
    held_node = node(True, folder=results)
    held_node["status"] = "done"
    fixes = [a_fix(results, 2, DECISION, held_node, "5de44e4")]
    assert next_with_fixes(held_node, judged_good(results), fixes, False) == Next(
        "sign-off", None, False
    )


def test_a_fix_whose_node_changed_since_takes_a_new_content_round(results: str):
    """Given the command judged short on N1 in content-1, then good in content-2, LIMIT Rounds,
    and fix-3 fixed, its fixer's Cut holding the node with each condition good, and the node now
    holding N1 not good, as a pruner wrote a decision since
    When what it waits on is asked
    Then the generator in a new content Round, as a course anew, the Rounds before the Fix
    counting toward no limit"""
    done = rounds(
        results,
        ("content", 1, MADE_ALL, SHORT),
        ("content", 2, MADE_ALL, GOOD, GOOD_PUT_UP),
    )
    fixes = [a_fix(results, 3, FIXED, node(True, folder=results))]
    assert next_with_fixes(node(["N2", "N3"], folder=results), done, fixes, False) == Next(
        "generator", "content", False
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


# Reading the Fixes from a run's files.

NAME = "20261120-a-command-with-which-the"


@pytest.fixture
def run(tmp_path: Any) -> RunPlace:
    """The walkthrough's run in a repository of the case, its design tree written."""
    repository = os.path.realpath(str(tmp_path))
    rn_files.run_folder(repository, NAME, rn_files.walkthrough_tree(NAME))
    return RunPlace(repository, NAME)


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
