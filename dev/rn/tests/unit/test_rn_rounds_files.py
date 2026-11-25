"""The unit cases of rounds/files.py, where each Round of a deliverable lies and what it holds:
Round.cut and Round.result, and of a role of neither; `of` with no Round, another deliverable's
Rounds beside them, one whose path differs only by `-` against `/` among them, a folder of another
form, and a Round and a Fix that share a number; `at` from an absolute and a relative folder, the
deliverable's path turned back from its percent-encoding, from a folder outside the run's Rounds,
and from a Fix's folder; `new` named by the deliverable's path percent-encoded whole, past the
deliverable's last Round or Fix with a gap, and of a stage of neither; `result` written, not
written, and not JSON; `mark` of the last of several Rounds with a state, again, of a Fix last, and
of a deliverable with none; `given` of a Round whose generator's Cut holds the deliverable's node,
and of one with no Cut; and the Fixes: Fix's paths; `fixes` and `of` each giving theirs apart, in
the order they were made by their numbers as numbers; `new_fix` past each Round; `problem`, and of
a source of none and words of only spaces; `problem_of`, `fixer_result`, and `fixer_given` written
and not written; `weigh` and `weighed` of a Round; and `reopen` of a Round holding a weighed point
and of one holding no result."""

from __future__ import annotations

import os
from typing import Any

import pytest
import rn_files
from fault import Wrong
from repository.place import RunPlace
from rounds.files import (
    Fix,
    Round,
    at,
    fixer_given,
    fixer_result,
    fixes,
    given,
    mark,
    marked,
    new,
    new_fix,
    of,
    problem,
    problem_of,
    reopen,
    result,
    weigh,
    weighed,
)

NAME = "20261120-a-command-with-which-the"
GUIDE = rn_files.GUIDE


@pytest.fixture
def run(tmp_path: Any) -> RunPlace:
    """The walkthrough's run in a repository of the case, its design tree written, no Round."""
    repository = os.path.realpath(str(tmp_path))
    rn_files.run_folder(repository, NAME, rn_files.walkthrough_tree(NAME))
    return RunPlace(repository, NAME)


def folder(run: RunPlace) -> str:
    """The run's folder, as the architecture's Directory structure places it."""
    return rn_files.folder_of(run.repository, NAME)


def seen(rounds: list[Round]) -> list[tuple[str, str, str, int]]:
    """Each Round as its folder, normalized, its deliverable, stage, and number."""
    return [(os.path.normpath(r.folder), r.deliverable, r.stage, r.number) for r in rounds]


def expected(run: RunPlace, deliverable: str, stage: str, number: int) -> tuple[str, str, str, int]:
    """The Round as `seen` gives it, at the place that rounds/files.py's module opening names."""
    return (rn_files.round_of(folder(run), deliverable, stage, number), deliverable, stage, number)


def test_a_rounds_cut_and_result_lie_in_its_folder():
    """Given a Round whose folder is /r/rounds/docs%2Fguide.md/content-1
    When the generator's Cut's path and the evaluator's result's path are asked
    Then they are <folder>/generator-cut.json and <folder>/evaluator.json"""
    round_ = Round("/r/rounds/docs%2Fguide.md/content-1", GUIDE, "content", 1)
    assert (round_.cut("generator"), round_.result("evaluator")) == (
        os.path.join(round_.folder, "generator-cut.json"),
        os.path.join(round_.folder, "evaluator.json"),
    )


def test_a_rounds_paths_of_a_role_of_neither_are_refused():
    """Given a Round
    When its Cut's or result's path is asked for a role that is neither generator nor evaluator
    Then each raises Wrong"""
    round_ = Round("/r/rounds/docs%2Fguide.md/content-1", GUIDE, "content", 1)
    with pytest.raises(Wrong):
        round_.cut("orchestrator")
    with pytest.raises(Wrong):
        round_.result("orchestrator")


def test_of_a_deliverable_with_no_round_gives_none(run: RunPlace):
    """Given a run with no Round
    When the guide's Rounds are asked
    Then there are none"""
    assert of(run, GUIDE) == []


def test_of_leaves_out_another_deliverables_rounds(run: RunPlace):
    """Given a run whose guide, docs/guide.md, has Round content-1, and whose command, and a
    deliverable docs-guide.md, its path differing only by `-` against `/`, each have Rounds
    content-1 and content-2
    When the guide's Rounds are asked
    Then it gives the guide's content-1 alone"""
    rn_files.a_round(folder(run), GUIDE, "content", 1)
    for other in (rn_files.COMMAND, "docs-guide.md"):
        for number in (1, 2):
            rn_files.a_round(folder(run), other, "content", number)
    assert seen(of(run, GUIDE)) == [expected(run, GUIDE, "content", 1)]


def test_of_refuses_a_folder_of_another_form(run: RunPlace):
    """Given a run whose guide's Rounds folder holds content-1 and a folder of another form
    When the guide's Rounds are asked
    Then it raises Wrong naming the folder"""
    rn_files.a_round(folder(run), GUIDE, "content", 1)
    os.makedirs(os.path.join(folder(run), "rounds", "docs%2Fguide.md", "draft-1"))
    with pytest.raises(Wrong, match="draft-1"):
        of(run, GUIDE)


def test_of_refuses_a_round_and_a_fix_that_share_a_number(run: RunPlace):
    """Given a run whose guide has Rounds content-1 and content-2, and Fix fix-2
    When the guide's Rounds are asked
    Then it raises Wrong naming both folders that share the number 2"""
    for number in (1, 2):
        rn_files.a_round(folder(run), GUIDE, "content", number)
    a_fix(run, 2)
    with pytest.raises(Wrong, match="content-2.*fix-2|fix-2.*content-2"):
        of(run, GUIDE)


def test_at_an_absolute_folder_gives_its_round(run: RunPlace):
    """Given a run whose deliverable docs/100%/a b.md, its path holding `/`, `%`, and a space, has
    Round refactor-2
    When the Round of its absolute folder is asked
    Then it gives refactor-2 of the deliverable, by its path as the design tree holds it"""
    deliverable = "docs/100%/a b.md"
    place = rn_files.a_round(folder(run), deliverable, "refactor", 2)
    assert seen([at(run, place)]) == [expected(run, deliverable, "refactor", 2)]


def test_at_a_folder_from_the_folder_the_command_runs_in_gives_its_round(
    run: RunPlace, monkeypatch: pytest.MonkeyPatch
):
    """Given a run whose command has Round content-1, and a command running at the repository's
    top
    When the Round of its folder from there is asked
    Then it gives content-1 of the command"""
    place = rn_files.a_round(folder(run), rn_files.COMMAND, "content", 1)
    monkeypatch.chdir(run.repository)
    given = os.path.relpath(place, run.repository)
    assert seen([at(run, given)]) == [expected(run, rn_files.COMMAND, "content", 1)]


def test_at_a_folder_outside_the_runs_rounds_is_refused(run: RunPlace, tmp_path: Any):
    """Given a run, and a folder content-1 outside its Rounds
    When the Round of that folder is asked
    Then it raises Wrong naming the folder"""
    outside = os.path.join(str(tmp_path), "elsewhere", "docs%2Fguide.md", "content-1")
    os.makedirs(outside)
    with pytest.raises(Wrong, match="elsewhere"):
        at(run, outside)


def test_new_makes_the_round_one_past_the_deliverables_last(run: RunPlace):
    """Given a run whose guide has Rounds content-1 and refactor-2, and Fix fix-4, a gap before it
    When a new content Round, then a new refactor Round, of the guide are made
    Then they are content-5 and refactor-6, each one past the last Round or Fix, each folder
    made"""
    for stage, number in (("content", 1), ("refactor", 2)):
        rn_files.a_round(folder(run), GUIDE, stage, number)
    a_fix(run, 4)
    content, refactor = new(run, GUIDE, "content"), new(run, GUIDE, "refactor")
    assert seen([content, refactor]) == [
        expected(run, GUIDE, "content", 5),
        expected(run, GUIDE, "refactor", 6),
    ]
    assert os.path.isdir(content.folder) and os.path.isdir(refactor.folder)


def test_new_of_a_stage_of_neither_is_refused(run: RunPlace):
    """Given a run with no Round
    When a new Round of a stage that is neither content nor refactor is made
    Then it raises Wrong, and the run's folder holds no Rounds folder"""
    with pytest.raises(Wrong):
        new(run, GUIDE, "refactoring")
    assert not os.path.exists(os.path.join(folder(run), "rounds", "docs%2Fguide.md"))


def test_result_gives_the_result_the_role_wrote(run: RunPlace):
    """Given a Round of the guide whose evaluator wrote its result
    When the evaluator's result is asked
    Then it gives the result as its JSON holds it"""
    written = rn_files.judged(more=[("N1", "They print it.")])
    place = rn_files.a_round(folder(run), GUIDE, "content", 1, {"evaluator": written})
    assert result(Round(place, GUIDE, "content", 1), "evaluator") == rn_files.read_json(
        os.path.join(place, "evaluator.json")
    )


def test_result_of_a_role_that_wrote_none_is_none(run: RunPlace):
    """Given a Round of the guide holding only the generator's Cut, as a pause leaves it
    When the generator's result is asked
    Then it gives None"""
    place = rn_files.a_round(folder(run), GUIDE, "content", 1)
    rn_files.write_json(os.path.join(place, "generator-cut.json"), {"goal": rn_files.GOAL})
    assert result(Round(place, GUIDE, "content", 1), "generator") is None


def test_result_that_isnt_json_is_refused_naming_it(run: RunPlace):
    """Given a Round of the guide whose generator.json holds `made` as plain text
    When the generator's result is asked
    Then it raises Wrong naming generator.json"""
    place = rn_files.a_round(folder(run), GUIDE, "content", 1)
    with open(os.path.join(place, "generator.json"), "w", encoding="utf-8") as f:
        f.write("made\n")
    with pytest.raises(Wrong, match="generator.json"):
        result(Round(place, GUIDE, "content", 1), "generator")


def test_new_names_the_folder_by_the_deliverables_path_percent_encoded_whole(run: RunPlace):
    """Given a run with no Round
    When a new content Round of docs/100%/a b.md is made
    Then it's content-1, its folder rounds/docs%2F100%25%2Fa%20b.md/content-1, made, as
    quote(path, safe="") gives the path"""
    made = new(run, "docs/100%/a b.md", "content")
    place = os.path.join(folder(run), "rounds", "docs%2F100%25%2Fa%20b.md", "content-1")
    assert seen([made]) == [(place, "docs/100%/a b.md", "content", 1)]
    assert os.path.isdir(place)


def test_mark_marks_the_deliverables_last_round_alone_with_the_state(run: RunPlace):
    """Given a run whose guide has Rounds content-1 and refactor-2, and whose command has
    content-3
    When the guide's last Round is marked as put up with N1 not good and an open decision of N1,
    then again with each condition good
    Then each mark gives refactor-2, which holds the last state, and content-1 and the command's
    content-3 hold none"""
    for stage, number in (("content", 1), ("refactor", 2)):
        rn_files.a_round(folder(run), GUIDE, stage, number)
    rn_files.a_round(folder(run), rn_files.COMMAND, "content", 3)
    left = {"short": ["N1"], "open": [{"condition": "N1", "about": "a comma in a line"}]}
    given = [mark(run, GUIDE, left), mark(run, GUIDE, {"short": [], "open": []})]
    rounds = [each for each in given if isinstance(each, Round)]
    assert seen(rounds) == [expected(run, GUIDE, "refactor", 2)] * 2
    assert [marked(each) for each in of(run, GUIDE)] == [None, {"short": [], "open": []}]
    assert marked(of(run, rn_files.COMMAND)[0]) is None


def test_mark_of_a_deliverable_with_no_round_marks_none(run: RunPlace):
    """Given a run with no Round
    When the plan's last Round is marked as put up
    Then it gives None, and the run's folder holds no Rounds folder"""
    assert mark(run, rn_files.plan_path(NAME), {"short": [], "open": []}) is None
    assert not os.path.exists(os.path.join(folder(run), "rounds"))


def test_given_is_the_node_that_the_generators_cut_held(run: RunPlace):
    """Given a run whose guide's Round content-1 holds a generator's Cut with the guide's node
    When the node its generator was given is asked
    Then it's that node"""
    place = rn_files.a_round(folder(run), GUIDE, "content", 1)
    node = rn_files.open_node("The guide", GUIDE, "readme")
    rn_files.write_json(os.path.join(place, "generator-cut.json"), {"deliverable": node})
    assert given(of(run, GUIDE)[0]) == node


def test_given_of_a_round_with_no_generators_cut_is_none(run: RunPlace):
    """Given a run whose guide's Round content-1 holds no generator's Cut
    When the node its generator was given is asked
    Then it's None"""
    rn_files.a_round(folder(run), GUIDE, "content", 1)
    assert given(of(run, GUIDE)[0]) is None


# The Fixes.

# A problem of a put-up that the repository's checks refused, in the words they printed.
REFUSED = {"source": "put-up", "words": "lint: docs/guide.md:3: a line ends in a space\n"}


def a_fix(run: RunPlace, number: int, written: dict[str, Any] | None = None) -> str:
    """Writes the guide's Fix folder fix-<number> with each file given, by its name, as JSON,
    and gives the folder."""
    place = rn_files.round_of(folder(run), GUIDE, "fix", number)
    os.makedirs(place, exist_ok=True)
    for name, value in (written or {}).items():
        rn_files.write_json(os.path.join(place, name), value)
    return place


def seen_fixes(found: list[Fix]) -> list[tuple[str, str, int]]:
    """Each Fix as its folder, normalized, its deliverable, and its number."""
    return [(os.path.normpath(f.folder), f.deliverable, f.number) for f in found]


def test_a_fixs_problem_cut_and_result_lie_in_its_folder():
    """Given a Fix whose folder is /r/rounds/docs%2Fguide.md/fix-3
    When its problem's, its fixer's Cut's, and its fixer's result's paths are asked
    Then they are <folder>/problem.json, <folder>/fixer-cut.json, and <folder>/fixer.json"""
    fix = Fix("/r/rounds/docs%2Fguide.md/fix-3", GUIDE, 3)
    assert (fix.problem, fix.cut, fix.result) == (
        os.path.join(fix.folder, "problem.json"),
        os.path.join(fix.folder, "fixer-cut.json"),
        os.path.join(fix.folder, "fixer.json"),
    )


def test_fixes_and_rounds_are_each_given_apart_in_the_order_they_were_made(run: RunPlace):
    """Given a run whose guide has content-1, fix-12, refactor-2, fix-3, and content-4, their
    folders made in that order
    When the guide's Fixes, then its Rounds, are asked
    Then the Fixes are fix-3, then fix-12, by their numbers as numbers, and the Rounds content-1,
    refactor-2, and content-4, none of the Fixes among them"""
    rn_files.a_round(folder(run), GUIDE, "content", 1)
    a_fix(run, 12)
    rn_files.a_round(folder(run), GUIDE, "refactor", 2)
    a_fix(run, 3)
    rn_files.a_round(folder(run), GUIDE, "content", 4)
    assert seen_fixes(fixes(run, GUIDE)) == [
        (rn_files.round_of(folder(run), GUIDE, "fix", 3), GUIDE, 3),
        (rn_files.round_of(folder(run), GUIDE, "fix", 12), GUIDE, 12),
    ]
    assert seen(of(run, GUIDE)) == [
        expected(run, GUIDE, "content", 1),
        expected(run, GUIDE, "refactor", 2),
        expected(run, GUIDE, "content", 4),
    ]


def test_at_a_fixs_folder_is_refused(run: RunPlace):
    """Given a run whose guide has Round content-1 and Fix fix-2
    When the Round of the Fix's folder is asked, as repository trial takes a Round's
    Then it raises Wrong naming the folder, as a Fix is no Round"""
    rn_files.a_round(folder(run), GUIDE, "content", 1)
    place = a_fix(run, 2)
    with pytest.raises(Wrong, match="fix-2: isn't a Round's folder of the run"):
        at(run, place)


def test_new_fix_makes_the_fix_one_past_the_last_round_holding_its_problem(run: RunPlace):
    """Given a run whose guide has Rounds content-1 and refactor-2
    When a new Fix of the guide is made with a problem of put-up
    Then it is fix-3, its folder made, holding problem.json with the problem as given"""
    for stage, number in (("content", 1), ("refactor", 2)):
        rn_files.a_round(folder(run), GUIDE, stage, number)
    made = new_fix(run, GUIDE, REFUSED)
    place = rn_files.round_of(folder(run), GUIDE, "fix", 3)
    assert seen_fixes([made]) == [(place, GUIDE, 3)]
    assert rn_files.read_json(os.path.join(place, "problem.json")) == REFUSED


def test_problem_holds_the_source_and_the_words_as_given():
    """Given the source final-check and its words, with a new line at their end
    When the problem is asked
    Then it holds the source and the words as given, the new line kept"""
    words = "lint: docs/guide.md:3: a line ends in a space\n"
    assert problem("final-check", words) == {"source": "final-check", "words": words}


def test_problem_of_a_source_of_none_is_refused_naming_each():
    """Given the source push, none of put-up, final-check, and send-back
    When the problem is asked
    Then it raises Wrong naming each source it takes"""
    with pytest.raises(Wrong, match="put-up, final-check, send-back"):
        problem("push", "the words")


def test_problem_with_no_words_is_refused_saying_to_give_them_on_stdin():
    """Given the source put-up, and words of only spaces
    When the problem is asked
    Then it raises Wrong saying to give the words on stdin"""
    with pytest.raises(Wrong, match="give them on stdin"):
        problem("put-up", " \n\t")


def test_a_fixs_problem_result_and_node_are_those_it_holds_or_none(run: RunPlace):
    """Given a run whose guide has fix-1 holding its problem alone, and fix-2 holding its
    problem, a fixer's Cut with the guide's node, and the fixer's decision
    When each Fix's problem, fixer's result, and the node its Cut held are asked
    Then fix-1 gives its problem and None for the others, and fix-2 the problem, the decision,
    and the node"""
    node = rn_files.open_node("The guide", GUIDE, "readme")
    decided = {"result": "decision", "decision": "N1 decides the guide's order."}
    a_fix(run, 1, {"problem.json": REFUSED})
    written = {"problem.json": REFUSED, "fixer-cut.json": {"deliverable": node}}
    a_fix(run, 2, {**written, "fixer.json": decided})
    assert [(problem_of(f), fixer_result(f), fixer_given(f)) for f in fixes(run, GUIDE)] == [
        (REFUSED, None, None),
        (REFUSED, decided, node),
    ]


def test_mark_of_a_deliverable_whose_last_folder_is_a_fix_marks_the_fix(run: RunPlace):
    """Given a run whose guide has Round content-1 and fix-2
    When the guide is marked as put up with each condition good
    Then the mark gives fix-2, which holds the state, and content-1 holds none"""
    rn_files.a_round(folder(run), GUIDE, "content", 1)
    a_fix(run, 2, {"problem.json": REFUSED})
    (fix,) = fixes(run, GUIDE)
    assert mark(run, GUIDE, {"short": [], "open": []}) == fix
    assert marked(fix) == {"short": [], "open": []}
    assert marked(of(run, GUIDE)[0]) is None


def test_a_round_is_weighed_once_weigh_marks_it_with_the_commit(run: RunPlace):
    """Given a run whose guide's Round content-1 holds a generator's point
    When weighed is asked, then weigh marks it with a commit's hash, and weighed is asked again
    Then it's None first, then the hash, held in content-1's weighed.json"""
    place = rn_files.a_round(folder(run), GUIDE, "content", 1, {"generator": rn_files.point()})
    (round_,) = of(run, GUIDE)
    assert weighed(round_) is None
    weigh(round_, "5de44e4")
    assert weighed(round_) == "5de44e4"
    assert rn_files.read_json(os.path.join(place, "weighed.json")) == {"commit": "5de44e4"}


@pytest.mark.parametrize(
    "results",
    [{"generator": rn_files.point(), **rn_files.WEIGHED}, {}],
    ids=["a weighed point", "no result"],
)
def test_reopen_takes_the_point_and_its_mark_out_of_the_round(
    run: RunPlace, results: dict[str, Any]
):
    """Given a run whose guide's Round content-1 holds the generator's Cut, and its weighed point
    with its mark, or no result
    When the Round is reopened
    Then it holds the generator's Cut alone"""
    place = rn_files.a_round(folder(run), GUIDE, "content", 1, {"generator-cut": {}, **results})
    (round_,) = of(run, GUIDE)
    reopen(round_)
    assert sorted(os.listdir(place)) == ["generator-cut.json"]
