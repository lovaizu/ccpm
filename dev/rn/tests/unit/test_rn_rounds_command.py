"""The unit cases of rounds/command.py and rounds/files.py, rounds' command line as the orchestrator
runs it: a deliverable's course from its first Round to its end, each Round's folder by its step,
its stage, and its number, a deliverable that a later step names again starting its own Rounds in
that step, a point weighed, findings left confirmed by the user, a Fix made from the problem's
words, fixed, and refactored, and each refusal: a result out of its schema, a Fix before the
Rounds are over or with no words, a confirming with nothing to confirm, a folder that's no Round's,
and arguments of another form."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
import rn_files
from place import RunPlace
from rounds.command import USAGE, main

NAME = "20261126-invoice-from-statement"
ROUNDS = f".rn/{NAME}/rounds/1/invoice%2F__main__.py"
CODE = os.path.join(rn_files.PRACTICES, "code")
REFACTOR = os.path.join(rn_files.PRACTICES, "refactor-code")
MADE = {"result": "made", "files": [rn_files.COMMAND], "good": []}
GOOD = {"result": "judged", "good": [{"condition": "N1", "lines": ["print"]}], "more": []}
MORE = {"result": "judged", "good": [], "more": [{"condition": "N1", "good_when": "it prints"}]}


@pytest.fixture
def made(tmp_path: Any) -> RunPlace:
    """A run whose folder holds the walkthrough's steering."""
    held = RunPlace(str(tmp_path), NAME)
    rn_files.write_json(held.steering, rn_files.steering())
    return held


def call(run_: RunPlace, *argv: str, words: str = "") -> tuple[int, str, str]:
    return main([argv[0], f".rn/{NAME}", *argv[1:]], run_.worktree, rn_files.RN, lambda: words)


def wrote(run_: RunPlace, folder: str, file: str, value: Any) -> None:
    rn_files.write_json(os.path.join(run_.worktree, folder, file), value)


def test_a_deliverable_goes_from_its_first_round_to_its_end(made: RunPlace) -> None:
    """Given a deliverable with no Round.
    When `next` runs after each role writes its result.
    Then it starts content-1, gives its evaluator, then refactor-2 to the refactorer once each
    condition is good, then the end."""
    first = os.path.join(made.worktree, ROUNDS, "content-1")
    assert call(made, "next", rn_files.COMMAND) == (0, f"generator\t{first}\t{CODE}\n", "")
    wrote(made, first, "generator.json", MADE)
    judges = os.path.join(first, "judges-by.json")
    assert call(made, "next", rn_files.COMMAND) == (0, f"evaluator\t{first}\t{judges}\n", "")
    with open(judges, encoding="utf-8") as f:
        assert json.load(f) == rn_files.judged_by("code")
    wrote(made, first, "evaluator.json", GOOD)
    second = os.path.join(made.worktree, ROUNDS, "refactor-2")
    refactorer = (0, f"refactorer\t{second}\t{REFACTOR}\n", "")
    assert call(made, "next", rn_files.COMMAND) == refactorer
    assert call(made, "next", rn_files.COMMAND) == refactorer
    wrote(made, second, "refactorer.json", MADE)
    assert call(made, "next", rn_files.COMMAND) == (0, "done\n", "")


def test_a_point_goes_to_a_pruner_then_to_a_new_round(made: RunPlace) -> None:
    """Given a first Round whose generator gave a point.
    When `next` runs, then `weighed` on the Round.
    Then the point's file is due to weigh, then content-2 starts."""
    call(made, "next", rn_files.COMMAND)
    first = os.path.join(made.worktree, ROUNDS, "content-1")
    wrote(made, first, "generator.json", {"result": "point", "point": "Which rate?"})
    assert call(made, "next", rn_files.COMMAND) == (0, f"weigh\t{first}/generator.json\n", "")
    second = os.path.join(made.worktree, ROUNDS, "content-2")
    assert call(made, "weighed", f"{ROUNDS}/content-1") == (0, f"generator\t{second}\t{CODE}\n", "")


def test_a_fix_is_made_from_the_problems_words_and_fixed(made: RunPlace) -> None:
    """Given a deliverable whose Rounds are over.
    When `fix` runs with the user's words, then `next`, then `next` once the fixer fixed it.
    Then fix-3 holds the words, its fixer is due, then refactor-4."""
    call(made, "next", rn_files.COMMAND)
    wrote(made, f"{ROUNDS}/content-1", "generator.json", MADE)
    wrote(made, f"{ROUNDS}/content-1", "evaluator.json", GOOD)
    call(made, "next", rn_files.COMMAND)
    wrote(made, f"{ROUNDS}/refactor-2", "refactorer.json", MADE)
    fix = os.path.join(made.worktree, ROUNDS, "fix-3")
    assert call(made, "fix", rn_files.COMMAND, words="合計が出ない") == (0, f"{fix}\n", "")
    with open(os.path.join(fix, "problem.md"), encoding="utf-8") as f:
        assert f.read() == "合計が出ない\n"
    assert call(made, "next", rn_files.COMMAND) == (0, f"fixer\t{fix}\t{CODE}\n", "")
    wrote(made, fix, "fixer.json", {"result": "fixed", "files": [rn_files.COMMAND]})
    again = os.path.join(made.worktree, ROUNDS, "refactor-4")
    assert call(made, "next", rn_files.COMMAND) == (0, f"refactorer\t{again}\t{REFACTOR}\n", "")


def test_findings_left_at_the_limit_go_to_the_user_who_confirms_them(made: RunPlace) -> None:
    """Given two Rounds judged with findings, each weighed.
    When `next` runs, then `confirmed`.
    Then the last evaluator's result is due to confirm, then refactor-3 to the refactorer."""
    for number in (1, 2):
        call(made, "next", rn_files.COMMAND)
        folder = f"{ROUNDS}/content-{number}"
        wrote(made, folder, "generator.json", MADE)
        wrote(made, folder, "evaluator.json", MORE)
        call(made, "weighed", folder)
    last = os.path.join(made.worktree, ROUNDS, "content-2")
    assert call(made, "next", rn_files.COMMAND) == (0, f"confirm\t{last}/evaluator.json\n", "")
    third = os.path.join(made.worktree, ROUNDS, "refactor-3")
    assert call(made, "confirmed", rn_files.COMMAND) == (
        0,
        f"refactorer\t{third}\t{REFACTOR}\n",
        "",
    )


def test_a_confirming_with_nothing_to_confirm_is_refused(made: RunPlace) -> None:
    """Given a deliverable with no Round.
    When `confirmed` runs.
    Then it gives 1 saying why."""
    code, _, err = call(made, "confirmed", rn_files.COMMAND)
    assert (code, "no findings wait on the user's confirming" in err) == (1, True)


@pytest.mark.parametrize(
    ("words", "says"), [("合計が出ない\n", "its Rounds aren't over"), (" \n", "words are empty")]
)
def test_a_fix_before_the_rounds_are_over_or_with_no_words_is_refused(
    made: RunPlace, words: str, says: str
) -> None:
    """Given a deliverable with no Round.
    When `fix` runs with words, or with none.
    Then it gives 1 saying why, and makes no Fix."""
    code, _, err = call(made, "fix", rn_files.COMMAND, words=words)
    assert (code, says in err, os.path.exists(os.path.join(made.worktree, ROUNDS))) == (
        1,
        True,
        False,
    )


def test_a_result_out_of_its_schema_is_refused(made: RunPlace) -> None:
    """Given a Round whose generator wrote a result of no known word.
    When `next` runs.
    Then it gives 1 naming the place."""
    call(made, "next", rn_files.COMMAND)
    wrote(made, f"{ROUNDS}/content-1", "generator.json", {"result": "done"})
    code, _, err = call(made, "next", rn_files.COMMAND)
    assert (code, "generator-round.schema.json: /result: takes one of made, point" in err) == (
        1,
        True,
    )


@pytest.mark.parametrize("folder", [ROUNDS, f"{ROUNDS}/content-9", f".rn/{NAME}"])
def test_a_folder_that_is_no_rounds_is_refused_as_weighed(made: RunPlace, folder: str) -> None:
    """Given a deliverable's folder, a Round not made, and the run's folder.
    When `weighed` runs on it.
    Then it gives 1, as none is a Round's or a Fix's folder."""
    os.makedirs(os.path.join(made.worktree, ROUNDS), exist_ok=True)
    code, _, err = call(made, "weighed", folder)
    assert (code, "isn't a Round's or a Fix's folder" in err) == (1, True)


@pytest.mark.parametrize("argv", [[], ["make", "a", "b"], ["next", "a"]])
def test_arguments_of_another_form_give_the_usage(argv: list[str]) -> None:
    """Given no subcommand, one that isn't rounds', or too few arguments.
    When rounds runs.
    Then it gives 2 with the usage."""
    assert main(argv, "/", rn_files.RN) == (2, "", USAGE)


def kind_of(run_: RunPlace, kind: str) -> None:
    """Gives the command the kind in the run's steering."""
    held = rn_files.steering()
    held["state"]["steps"][0]["deliverables"][0]["kind"] = kind
    rn_files.write_json(run_.steering, held)


def test_a_kind_that_no_refactoring_takes_goes_to_its_end_and_takes_a_fix(
    made: RunPlace,
) -> None:
    """Given a deliverable of the kind light, judged with each condition good.
    When `next` runs, then `fix` with the user's words.
    Then the end, with no Round of refactoring made, and then the Fix fix-2 with its fixer due."""
    kind_of(made, "light")
    call(made, "next", rn_files.COMMAND)
    wrote(made, f"{ROUNDS}/content-1", "generator.json", MADE)
    wrote(made, f"{ROUNDS}/content-1", "evaluator.json", GOOD)
    assert call(made, "next", rn_files.COMMAND) == (0, "done\n", "")
    assert sorted(os.listdir(os.path.join(made.worktree, ROUNDS))) == ["content-1"]
    fix = os.path.join(made.worktree, ROUNDS, "fix-2")
    assert call(made, "fix", rn_files.COMMAND, words="LICENSE: missing") == (0, f"{fix}\n", "")
    light = os.path.join(rn_files.PRACTICES, "light")
    assert call(made, "next", rn_files.COMMAND) == (0, f"fixer\t{fix}\t{light}\n", "")


@pytest.mark.parametrize(
    ("deliverable", "kind", "says"),
    [
        ("docs/other.md", "code", "no step names the deliverable"),
        (rn_files.COMMAND, "poem", "no best practice of the kind 'poem'"),
    ],
)
def test_a_deliverable_no_step_names_or_of_a_kind_with_no_best_practice_is_refused(
    made: RunPlace, deliverable: str, kind: str, says: str
) -> None:
    """Given a path that no step names, or a deliverable of a kind that rn has no best practice of.
    When `next` runs.
    Then it gives 1 saying why."""
    kind_of(made, kind)
    code, _, err = call(made, "next", deliverable)
    assert (code, says in err) == (1, True)


def test_a_deliverable_that_a_later_step_names_again_starts_its_rounds_in_that_step(
    made: RunPlace,
) -> None:
    """Given a deliverable whose Rounds in step 1 are over, its step done, and a step 2 that adds
    to it.
    When `next` runs on it.
    Then content-1 of step 2 starts, and a Fix of it lies in step 2."""
    call(made, "next", rn_files.COMMAND)
    first = os.path.join(made.worktree, ROUNDS, "content-1")
    wrote(made, first, "generator.json", MADE)
    call(made, "next", rn_files.COMMAND)
    wrote(made, first, "evaluator.json", GOOD)
    call(made, "next", rn_files.COMMAND)
    wrote(made, os.path.join(ROUNDS, "refactor-2"), "refactorer.json", MADE)
    added = dict(rn_files.step(), settles="print a second page")
    rn_files.write_json(
        made.steering,
        rn_files.steering([rn_files.step("done", done=(rn_files.COMMAND, rn_files.GUIDE)), added]),
    )
    later = os.path.join(made.worktree, f".rn/{NAME}/rounds/2/invoice%2F__main__.py", "content-1")
    assert call(made, "next", rn_files.COMMAND) == (0, f"generator\t{later}\t{CODE}\n", "")


def test_a_fix_of_a_deliverable_whose_step_is_done_lies_in_that_step(made: RunPlace) -> None:
    """Given a deliverable whose Rounds in step 1 are over, and step 1 done.
    When `fix` runs with the user's words.
    Then the Fix lies in step 1's folder of the deliverable."""
    call(made, "next", rn_files.COMMAND)
    first = os.path.join(made.worktree, ROUNDS, "content-1")
    wrote(made, first, "generator.json", MADE)
    call(made, "next", rn_files.COMMAND)
    wrote(made, first, "evaluator.json", GOOD)
    call(made, "next", rn_files.COMMAND)
    wrote(made, os.path.join(ROUNDS, "refactor-2"), "refactorer.json", MADE)
    rn_files.write_json(
        made.steering,
        rn_files.steering([rn_files.step("done", done=(rn_files.COMMAND, rn_files.GUIDE))]),
    )
    fix = os.path.join(made.worktree, ROUNDS, "fix-3")
    assert call(made, "fix", rn_files.COMMAND, words="the total is off") == (0, f"{fix}\n", "")
