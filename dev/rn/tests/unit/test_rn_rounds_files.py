"""The unit cases of rounds/files.py, where each Round of a deliverable lies and what it holds:
Round.cut and Round.result for each role and a role of neither; `of` with none, one, and several
Rounds, in the order they were made by their numbers as numbers, a content Round after a refactor
one among them, another deliverable's Rounds beside them, among them one whose path differs only by
`/` against `-`, a folder of another form, and two folders that share a number; each folder named
by the deliverable's path percent-encoded whole, paths holding `-` and `%` among them; `at` from an
absolute and a relative folder, and from a folder outside the run's Rounds; `new` past the
deliverable's last Round of either stage, a gap among them included, and a stage of neither;
`mark` of the last of several Rounds with a state, again, of a Fix last, and of a deliverable with
none, and
`marked` of a Round marked, of one not, and of a mark that isn't JSON; `given` of a Round whose
generator's Cut holds the deliverable's node, and of one with no Cut; `result` written, not
written, and not JSON; and the Fixes: Fix's paths; `fixes` with none, and several among Rounds,
`of` leaving them out; a Round and a Fix that share a number; `at` of a Fix's folder; `new` and
`new_fix` numbered past each Round and Fix; `problem` of each source, and of a source of none and
words empty or only spaces; `problem_of`, `fixer_result`, and `fixer_given` written, not written,
and not JSON; `weigh` and `weighed` of a Fix and of a Round; and `reopen` of a Round holding a
weighed point and of one holding no result."""

from __future__ import annotations

import os
from collections.abc import Callable
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


@pytest.mark.supports("test_a_generators_made_makes_the_evaluator_due_in_the_same_round")
@pytest.mark.parametrize("role", ["generator", "evaluator"])
def test_a_rounds_cut_of_each_role_lies_in_its_folder(role: str):
    """Given a Round whose folder is /r/rounds/docs%2Fguide.md/content-1
    When its Cut's path is asked for the role
    Then it is <folder>/<role>-cut.json"""
    round_ = Round("/r/rounds/docs%2Fguide.md/content-1", GUIDE, "content", 1)
    assert round_.cut(role) == os.path.join(round_.folder, f"{role}-cut.json")


@pytest.mark.supports("test_a_generators_made_makes_the_evaluator_due_in_the_same_round")
@pytest.mark.parametrize("role", ["generator", "evaluator"])
def test_a_rounds_result_of_each_role_lies_in_its_folder(role: str):
    """Given a Round whose folder is /r/rounds/docs%2Fguide.md/content-1
    When its result's path is asked for the role
    Then it is <folder>/<role>.json"""
    round_ = Round("/r/rounds/docs%2Fguide.md/content-1", GUIDE, "content", 1)
    assert round_.result(role) == os.path.join(round_.folder, f"{role}.json")


@pytest.mark.supports("test_a_generators_made_makes_the_evaluator_due_in_the_same_round")
@pytest.mark.parametrize("role", ["orchestrator", "Generator", ""])
def test_a_rounds_paths_of_a_role_of_neither_are_refused(role: str):
    """Given a Round
    When its Cut's or result's path is asked for a role that is neither generator nor evaluator
    Then each raises Wrong"""
    round_ = Round("/r/rounds/docs%2Fguide.md/content-1", GUIDE, "content", 1)
    with pytest.raises(Wrong):
        round_.cut(role)
    with pytest.raises(Wrong):
        round_.result(role)


@pytest.mark.supports("test_the_generators_cut_holds_the_pruners_remedy_and_no_evaluators_finding")
def test_of_a_deliverable_with_no_round_gives_none(run: RunPlace):
    """Given a run with no Round
    When the guide's Rounds are asked
    Then there are none"""
    assert of(run, GUIDE) == []


@pytest.mark.supports("test_the_generators_cut_holds_the_pruners_remedy_and_no_evaluators_finding")
def test_of_a_deliverable_with_one_round_gives_it(run: RunPlace):
    """Given a run whose guide has Round content-1
    When the guide's Rounds are asked
    Then it gives content-1 alone, with the guide's path, stage, and number"""
    rn_files.a_round(folder(run), GUIDE, "content", 1)
    assert seen(of(run, GUIDE)) == [expected(run, GUIDE, "content", 1)]


@pytest.mark.supports("test_a_send_back_after_the_refactor_round_is_remade_in_a_new_content_round")
def test_of_gives_the_rounds_in_the_order_they_were_made_by_their_numbers(run: RunPlace):
    """Given a run whose guide has Rounds content-11, refactor-10, content-2, and content-1, their
    folders made in that order
    When the guide's Rounds are asked
    Then it gives content-1, content-2, refactor-10, then content-11, as numbers order them, the
    content Round after the refactor one last"""
    for stage, number in (("content", 11), ("refactor", 10), ("content", 2), ("content", 1)):
        rn_files.a_round(folder(run), GUIDE, stage, number)
    assert seen(of(run, GUIDE)) == [
        expected(run, GUIDE, "content", 1),
        expected(run, GUIDE, "content", 2),
        expected(run, GUIDE, "refactor", 10),
        expected(run, GUIDE, "content", 11),
    ]


@pytest.mark.supports("test_the_generators_cut_holds_the_pruners_remedy_and_no_evaluators_finding")
def test_of_leaves_out_another_deliverables_rounds(run: RunPlace):
    """Given a run whose guide has Round content-1, and whose command, and a deliverable
    docs/guide.md.old beside the guide, each have Rounds content-1 and content-2
    When the guide's Rounds are asked
    Then it gives the guide's content-1 alone"""
    rn_files.a_round(folder(run), GUIDE, "content", 1)
    for other in (rn_files.COMMAND, "docs/guide.md.old"):
        for number in (1, 2):
            rn_files.a_round(folder(run), other, "content", number)
    assert seen(of(run, GUIDE)) == [expected(run, GUIDE, "content", 1)]


@pytest.mark.supports("test_the_generators_cut_holds_the_pruners_remedy_and_no_evaluators_finding")
@pytest.mark.parametrize("name", ["content-x", "draft-1", "content-0", "content1"])
def test_of_refuses_a_folder_of_another_form(run: RunPlace, name: str):
    """Given a run whose guide's Rounds folder holds content-1 and a folder of another form
    When the guide's Rounds are asked
    Then it raises Wrong naming the folder"""
    rn_files.a_round(folder(run), GUIDE, "content", 1)
    os.makedirs(os.path.join(folder(run), "rounds", "docs%2Fguide.md", name))
    with pytest.raises(Wrong, match=name):
        of(run, GUIDE)


@pytest.mark.supports("test_a_send_back_after_the_refactor_round_is_remade_in_a_new_content_round")
def test_of_refuses_two_folders_that_share_a_number(run: RunPlace):
    """Given a run whose guide has Rounds content-1, content-2, and refactor-2
    When the guide's Rounds are asked
    Then it raises Wrong naming both folders that share the number 2"""
    for stage, number in (("content", 1), ("content", 2), ("refactor", 2)):
        rn_files.a_round(folder(run), GUIDE, stage, number)
    with pytest.raises(Wrong, match="content-2.*refactor-2|refactor-2.*content-2"):
        of(run, GUIDE)


@pytest.mark.supports(
    "test_a_pick_up_starts_the_stopped_generator_again_in_its_round_with_a_fresh_cut"
)
def test_at_an_absolute_folder_gives_its_round(run: RunPlace):
    """Given a run whose guide has Round refactor-2
    When the Round of its absolute folder is asked
    Then it gives refactor-2 of the guide, by the guide's path in the design tree"""
    place = rn_files.a_round(folder(run), GUIDE, "refactor", 2)
    assert seen([at(run, place)]) == [expected(run, GUIDE, "refactor", 2)]


@pytest.mark.supports(
    "test_a_pick_up_starts_the_stopped_generator_again_in_its_round_with_a_fresh_cut"
)
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


@pytest.mark.supports(
    "test_a_pick_up_starts_the_stopped_generator_again_in_its_round_with_a_fresh_cut"
)
def test_at_a_folder_outside_the_runs_rounds_is_refused(run: RunPlace, tmp_path: Any):
    """Given a run, and a folder content-1 outside its Rounds
    When the Round of that folder is asked
    Then it raises Wrong naming the folder"""
    outside = os.path.join(str(tmp_path), "elsewhere", "docs%2Fguide.md", "content-1")
    os.makedirs(outside)
    with pytest.raises(Wrong, match="elsewhere"):
        at(run, outside)


@pytest.mark.supports(
    "test_a_pick_up_starts_the_stopped_generator_again_in_its_round_with_a_fresh_cut"
)
def test_at_the_rounds_folder_of_a_deliverable_is_refused(run: RunPlace):
    """Given a run whose guide has Round content-1
    When the Round of the guide's Rounds folder, one level above content-1, is asked
    Then it raises Wrong"""
    place = rn_files.a_round(folder(run), GUIDE, "content", 1)
    with pytest.raises(Wrong):
        at(run, os.path.dirname(place))


@pytest.mark.supports("test_the_generators_cut_holds_the_pruners_remedy_and_no_evaluators_finding")
def test_new_with_no_round_of_the_stage_makes_its_first(run: RunPlace):
    """Given a run with no Round
    When a new content Round of the guide is made
    Then it is content-1, its folder made"""
    made = new(run, GUIDE, "content")
    assert seen([made]) == [expected(run, GUIDE, "content", 1)]
    assert os.path.isdir(made.folder)


@pytest.mark.supports("test_a_send_back_after_the_refactor_round_is_remade_in_a_new_content_round")
def test_new_makes_the_round_one_past_the_deliverables_last(run: RunPlace):
    """Given a run whose guide has Rounds content-1 and refactor-3, a gap between them
    When a new content Round, then a new refactor Round, of the guide are made
    Then they are content-4 and refactor-5, each one past the last Round of either stage, each
    folder made"""
    for stage, number in (("content", 1), ("refactor", 3)):
        rn_files.a_round(folder(run), GUIDE, stage, number)
    content, refactor = new(run, GUIDE, "content"), new(run, GUIDE, "refactor")
    assert seen([content, refactor]) == [
        expected(run, GUIDE, "content", 4),
        expected(run, GUIDE, "refactor", 5),
    ]
    assert os.path.isdir(content.folder) and os.path.isdir(refactor.folder)


@pytest.mark.supports("test_the_generators_cut_holds_the_pruners_remedy_and_no_evaluators_finding")
def test_new_counts_only_the_deliverables_own_rounds(run: RunPlace):
    """Given a run whose command has Rounds content-1 and content-2
    When a new content Round of the guide is made
    Then it is the guide's content-1"""
    for number in (1, 2):
        rn_files.a_round(folder(run), rn_files.COMMAND, "content", number)
    assert seen([new(run, GUIDE, "content")]) == [expected(run, GUIDE, "content", 1)]


@pytest.mark.supports("test_the_generators_cut_holds_the_pruners_remedy_and_no_evaluators_finding")
@pytest.mark.parametrize("stage", ["Content", "refactoring", ""])
def test_new_of_a_stage_of_neither_is_refused(run: RunPlace, stage: str):
    """Given a run with no Round
    When a new Round of a stage that is neither content nor refactor is made
    Then it raises Wrong, and the run's folder holds no Rounds folder"""
    with pytest.raises(Wrong):
        new(run, GUIDE, stage)
    assert not os.path.exists(os.path.join(folder(run), "rounds", "docs%2Fguide.md"))


@pytest.mark.supports("test_a_generators_made_makes_the_evaluator_due_in_the_same_round")
@pytest.mark.parametrize(
    ("role", "written"),
    [
        ("generator", rn_files.made([("N1", ["# Print an invoice"])], [GUIDE])),
        ("evaluator", rn_files.judged(more=[("N1", "They print it.")])),
    ],
)
def test_result_gives_the_result_the_role_wrote(run: RunPlace, role: str, written: Any):
    """Given a Round of the guide whose role wrote its result
    When the role's result is asked
    Then it gives the result as its JSON holds it"""
    place = rn_files.a_round(folder(run), GUIDE, "content", 1, {role: written})
    assert result(Round(place, GUIDE, "content", 1), role) == rn_files.read_json(
        os.path.join(place, f"{role}.json")
    )


@pytest.mark.supports(
    "test_a_pick_up_starts_the_stopped_generator_again_in_its_round_with_a_fresh_cut"
)
@pytest.mark.parametrize("role", ["generator", "evaluator"])
def test_result_of_a_role_that_wrote_none_is_none(run: RunPlace, role: str):
    """Given a Round of the guide holding only the role's Cut, as a pause leaves it
    When the role's result is asked
    Then it gives None"""
    place = rn_files.a_round(folder(run), GUIDE, "content", 1)
    rn_files.write_json(os.path.join(place, f"{role}-cut.json"), {"goal": rn_files.GOAL})
    assert result(Round(place, GUIDE, "content", 1), role) is None


@pytest.mark.supports("test_a_generators_made_makes_the_evaluator_due_in_the_same_round")
def test_result_that_isnt_json_is_refused_naming_it(run: RunPlace):
    """Given a Round of the guide whose generator.json holds `made` as plain text
    When the generator's result is asked
    Then it raises Wrong naming generator.json"""
    place = rn_files.a_round(folder(run), GUIDE, "content", 1)
    with open(os.path.join(place, "generator.json"), "w", encoding="utf-8") as f:
        f.write("made\n")
    with pytest.raises(Wrong, match="generator.json"):
        result(Round(place, GUIDE, "content", 1), "generator")


@pytest.mark.supports("test_the_generators_cut_holds_the_pruners_remedy_and_no_evaluators_finding")
@pytest.mark.parametrize(
    ("deliverable", "named"),
    [
        ("docs/guide.md", "docs%2Fguide.md"),
        ("docs-guide.md", "docs-guide.md"),
        ("invoicer/__main__.py", "invoicer%2F__main__.py"),
        ("docs/100%/a b.md", "docs%2F100%25%2Fa%20b.md"),
        ("README.md", "README.md"),
    ],
)
def test_new_names_the_folder_by_the_deliverables_path_percent_encoded_whole(
    run: RunPlace, deliverable: str, named: str
):
    """Given a run with no Round
    When a new content Round of the deliverable is made
    Then its folder is rounds/<the path as quote(path, safe="") gives it>/content-1, made"""
    made = new(run, deliverable, "content")
    place = os.path.join(folder(run), "rounds", named, "content-1")
    assert seen([made]) == [(place, deliverable, "content", 1)]
    assert os.path.isdir(place)


@pytest.mark.supports("test_the_generators_cut_holds_the_pruners_remedy_and_no_evaluators_finding")
def test_paths_that_differ_only_by_slash_and_dash_keep_their_rounds_apart(run: RunPlace):
    """Given a run whose deliverable docs/guide.md has Round content-1, and another docs-guide.md
    has Rounds content-1 and content-2
    When each one's Rounds are asked, and a new content Round of docs/guide.md is made
    Then docs/guide.md has content-1 alone, docs-guide.md both of its own, and the new Round is
    docs/guide.md's content-2"""
    rn_files.a_round(folder(run), "docs/guide.md", "content", 1)
    for number in (1, 2):
        rn_files.a_round(folder(run), "docs-guide.md", "content", number)
    assert seen(of(run, "docs/guide.md")) == [expected(run, "docs/guide.md", "content", 1)]
    assert seen(of(run, "docs-guide.md")) == [
        expected(run, "docs-guide.md", "content", 1),
        expected(run, "docs-guide.md", "content", 2),
    ]
    assert seen([new(run, "docs/guide.md", "content")]) == [
        expected(run, "docs/guide.md", "content", 2)
    ]


@pytest.mark.supports(
    "test_a_pick_up_starts_the_stopped_generator_again_in_its_round_with_a_fresh_cut"
)
@pytest.mark.parametrize(
    "deliverable", ["docs/guide.md", "docs-guide.md", "docs/100%/a b.md", "a%2Fb.md"]
)
def test_at_turns_the_folders_name_back_into_the_deliverables_path(run: RunPlace, deliverable: str):
    """Given a run whose deliverable, its path holding `/`, `-`, `%`, or a space, has Round
    refactor-1
    When the Round of its folder is asked
    Then it gives refactor-1 of the deliverable by its path as the design tree holds it"""
    place = rn_files.a_round(folder(run), deliverable, "refactor", 1)
    assert seen([at(run, place)]) == [expected(run, deliverable, "refactor", 1)]


@pytest.mark.supports("test_a_send_back_past_the_contents_limit_is_remade_in_rounds_of_its_own")
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


@pytest.mark.supports("test_a_send_back_past_the_contents_limit_is_remade_in_rounds_of_its_own")
def test_mark_of_a_deliverable_with_no_round_marks_none(run: RunPlace):
    """Given a run with no Round
    When the plan's last Round is marked as put up
    Then it gives None, and the run's folder holds no Rounds folder"""
    assert mark(run, rn_files.plan_path(NAME), {"short": [], "open": []}) is None
    assert not os.path.exists(os.path.join(folder(run), "rounds"))


@pytest.mark.supports("test_a_send_back_past_the_contents_limit_is_remade_in_rounds_of_its_own")
def test_marked_refuses_a_mark_that_isnt_json(run: RunPlace):
    """Given a run whose guide's Round content-1 holds a put-up.json that isn't JSON
    When the state it was put up with is asked
    Then it raises Wrong naming the file"""
    place = rn_files.a_round(folder(run), GUIDE, "content", 1)
    with open(os.path.join(place, "put-up.json"), "w", encoding="utf-8") as file:
        file.write("{")
    with pytest.raises(Wrong, match="put-up.json"):
        marked(of(run, GUIDE)[0])


@pytest.mark.supports("test_a_users_answer_after_two_content_rounds_gets_a_new_content_round")
def test_given_is_the_node_that_the_generators_cut_held(run: RunPlace):
    """Given a run whose guide's Round content-1 holds a generator's Cut with the guide's node
    When the node its generator was given is asked
    Then it's that node"""
    place = rn_files.a_round(folder(run), GUIDE, "content", 1)
    node = rn_files.open_node("The guide", GUIDE, "readme")
    rn_files.write_json(os.path.join(place, "generator-cut.json"), {"deliverable": node})
    assert given(of(run, GUIDE)[0]) == node


@pytest.mark.supports("test_a_users_answer_after_two_content_rounds_gets_a_new_content_round")
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


@pytest.mark.supports(
    "test_a_put_up_that_the_repositorys_push_check_refuses_is_mended_by_a_fix_and_put_up_again"
)
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


@pytest.mark.supports("test_a_fix_counts_toward_no_limit_of_the_rounds")
def test_fixes_of_a_deliverable_with_none_gives_none(run: RunPlace):
    """Given a run whose guide has Round content-1 and no Fix
    When the guide's Fixes are asked
    Then there are none"""
    rn_files.a_round(folder(run), GUIDE, "content", 1)
    assert fixes(run, GUIDE) == []


@pytest.mark.supports("test_a_fix_counts_toward_no_limit_of_the_rounds")
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


@pytest.mark.supports("test_a_fix_counts_toward_no_limit_of_the_rounds")
@pytest.mark.parametrize("ask", [of, fixes], ids=["of", "fixes"])
def test_a_round_and_a_fix_that_share_a_number_are_refused(
    run: RunPlace, ask: Callable[[RunPlace, str], list[Any]]
):
    """Given a run whose guide has content-1, content-2, and fix-2
    When the guide's Rounds, or its Fixes, are asked
    Then it raises Wrong naming both folders that share the number 2"""
    for number in (1, 2):
        rn_files.a_round(folder(run), GUIDE, "content", number)
    a_fix(run, 2)
    with pytest.raises(Wrong, match="content-2.*fix-2|fix-2.*content-2"):
        ask(run, GUIDE)


@pytest.mark.supports(
    "test_a_put_up_that_the_repositorys_push_check_refuses_is_mended_by_a_fix_and_put_up_again"
)
def test_at_a_fixs_folder_is_refused(run: RunPlace):
    """Given a run whose guide has Round content-1 and Fix fix-2
    When the Round of the Fix's folder is asked, as repository.py trial takes a Round's
    Then it raises Wrong naming the folder, as a Fix is no Round"""
    rn_files.a_round(folder(run), GUIDE, "content", 1)
    place = a_fix(run, 2)
    with pytest.raises(Wrong, match="fix-2: isn't a Round's folder of the run"):
        at(run, place)


@pytest.mark.supports(
    "test_a_fixers_decision_goes_to_one_pruner_and_the_deliverable_takes_content_rounds_again"
)
def test_new_makes_the_round_one_past_the_deliverables_last_fix(run: RunPlace):
    """Given a run whose guide has Round content-1 and Fix fix-2
    When a new content Round of the guide is made
    Then it is content-3, numbered with the Fix"""
    rn_files.a_round(folder(run), GUIDE, "content", 1)
    a_fix(run, 2)
    assert seen([new(run, GUIDE, "content")]) == [expected(run, GUIDE, "content", 3)]


@pytest.mark.supports(
    "test_a_put_up_that_the_repositorys_push_check_refuses_is_mended_by_a_fix_and_put_up_again"
)
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


@pytest.mark.supports("test_a_fix_counts_toward_no_limit_of_the_rounds")
def test_new_fix_after_a_fix_makes_the_next(run: RunPlace):
    """Given a run whose guide has Round content-1 and Fix fix-2
    When a new Fix of the guide is made
    Then it is fix-3, and fix-2 is as it was"""
    rn_files.a_round(folder(run), GUIDE, "content", 1)
    a_fix(run, 2, {"problem.json": REFUSED, "fixer.json": {"result": "fixed", "files": []}})
    made = new_fix(run, GUIDE, {"source": "send-back", "words": "Name the command's flag."})
    assert made.number == 3
    assert fixer_result(fixes(run, GUIDE)[0]) == {"result": "fixed", "files": []}


@pytest.mark.supports(
    "test_a_put_up_that_the_repositorys_push_check_refuses_is_mended_by_a_fix_and_put_up_again"
)
@pytest.mark.parametrize("source", ["put-up", "final-check", "send-back"])
def test_problem_of_each_source_holds_it_and_the_words_as_given(source: str):
    """Given a source of the problem and its words, with a new line at their end
    When the problem is asked
    Then it holds the source and the words as given, the new line kept"""
    words = "lint: docs/guide.md:3: a line ends in a space\n"
    assert problem(source, words) == {"source": source, "words": words}


@pytest.mark.supports(
    "test_a_put_up_that_the_repositorys_push_check_refuses_is_mended_by_a_fix_and_put_up_again"
)
@pytest.mark.parametrize("source", ["put_up", "push", "", "Send-back"])
def test_problem_of_a_source_of_none_is_refused_naming_each(source: str):
    """Given a source that is none of put-up, final-check, and send-back, one that nearly matches
    among them
    When the problem is asked
    Then it raises Wrong naming each source it takes"""
    with pytest.raises(Wrong, match="put-up, final-check, send-back"):
        problem(source, "the words")


@pytest.mark.supports(
    "test_a_put_up_that_the_repositorys_push_check_refuses_is_mended_by_a_fix_and_put_up_again"
)
@pytest.mark.parametrize("words", ["", " \n\t"], ids=["empty", "only spaces"])
def test_problem_with_no_words_is_refused_saying_to_give_them_on_stdin(words: str):
    """Given the source put-up, and words empty or only spaces
    When the problem is asked
    Then it raises Wrong saying to give the words on stdin"""
    with pytest.raises(Wrong, match="give them on stdin"):
        problem("put-up", words)


@pytest.mark.supports(
    "test_the_fixers_cut_holds_the_deliverables_node_paths_and_problem_and_where_it_writes"
)
def test_problem_of_a_fix_is_the_problem_it_holds_or_none(run: RunPlace):
    """Given a run whose guide has fix-1 holding its problem, and fix-2 holding none
    When each Fix's problem is asked
    Then it's the problem of fix-1, and None for fix-2"""
    a_fix(run, 1, {"problem.json": REFUSED})
    a_fix(run, 2)
    assert [problem_of(each) for each in fixes(run, GUIDE)] == [REFUSED, None]


@pytest.mark.supports("test_a_pick_up_starts_the_stopped_fixer_again_in_its_fix_with_a_fresh_cut")
def test_a_fixs_result_and_node_are_none_before_its_fixer_writes_them(run: RunPlace):
    """Given a run whose guide has fix-1 holding its problem alone
    When the fixer's result and the node its Cut held are asked
    Then each is None"""
    a_fix(run, 1, {"problem.json": REFUSED})
    (fix,) = fixes(run, GUIDE)
    assert (fixer_result(fix), fixer_given(fix)) == (None, None)


@pytest.mark.supports(
    "test_a_fixers_decision_goes_to_one_pruner_and_the_deliverable_takes_content_rounds_again"
)
def test_a_fixs_result_and_node_are_those_its_fixer_was_given_and_wrote(run: RunPlace):
    """Given a run whose guide has fix-1 holding its problem, a fixer's Cut with the guide's
    node, and the fixer's decision
    When the fixer's result and the node its Cut held are asked
    Then they are the decision and the node"""
    node = rn_files.open_node("The guide", GUIDE, "readme")
    decided = {"result": "decision", "decision": "N1 decides the guide's order."}
    written = {"problem.json": REFUSED, "fixer-cut.json": {"deliverable": node}}
    a_fix(run, 1, {**written, "fixer.json": decided})
    (fix,) = fixes(run, GUIDE)
    assert (fixer_result(fix), fixer_given(fix)) == (decided, node)


@pytest.mark.supports("test_a_fixers_decision_that_the_pruner_cuts_ends_the_fix")
def test_a_fix_is_weighed_once_weigh_marks_it_with_the_commit(run: RunPlace):
    """Given a run whose guide has fix-1 holding its problem and a fixer's decision
    When weighed is asked, then weigh marks it with a commit's hash, and weighed is asked again
    Then it's None first, then the hash, held in fix-1's weighed.json"""
    a_fix(run, 1, {"problem.json": REFUSED, "fixer.json": {"result": "decision", "decision": "x"}})
    (fix,) = fixes(run, GUIDE)
    assert weighed(fix) is None
    weigh(fix, "5de44e4")
    assert weighed(fix) == "5de44e4"
    assert rn_files.read_json(os.path.join(fix.folder, "weighed.json")) == {"commit": "5de44e4"}


@pytest.mark.supports(
    "test_a_put_up_that_the_repositorys_push_check_refuses_is_mended_by_a_fix_and_put_up_again"
)
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


@pytest.mark.supports("test_a_generators_point_goes_to_a_pruner_which_leaves_open_only_the_users")
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


@pytest.mark.supports("test_a_generators_point_goes_to_a_pruner_which_leaves_open_only_the_users")
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


@pytest.mark.supports("test_a_fixers_file_outside_its_deliverable_is_refused_by_check_py")
@pytest.mark.parametrize("name", ["problem.json", "fixer-cut.json", "fixer.json"])
def test_a_fixs_file_that_isnt_json_is_refused_naming_it(run: RunPlace, name: str):
    """Given a run whose guide's fix-1 holds the file, which isn't JSON
    When its problem, the node its fixer's Cut held, and the fixer's result are asked
    Then the one that reads the file raises Wrong naming it"""
    place = a_fix(run, 1)
    with open(os.path.join(place, name), "w", encoding="utf-8") as file:
        file.write("{")
    (fix,) = fixes(run, GUIDE)
    read = {"problem.json": problem_of, "fixer-cut.json": fixer_given, "fixer.json": fixer_result}
    with pytest.raises(Wrong, match=name):
        read[name](fix)
