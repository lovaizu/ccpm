"""The unit cases of rounds/files.py, where each Round of a deliverable lies and what it holds:
Round.cut and Round.result for each role and a role of neither; `of` with none, one, and several
Rounds, content before refactor and each stage by its number as a number, another deliverable's
Rounds beside them, among them one whose path differs only by `/` against `-`, and a folder of
another form; each folder named by the deliverable's path percent-encoded whole, paths holding `-`
and `%` among them; `at` from an absolute and a relative folder, and
from a folder outside the run's Rounds; `new` past the stage's last, a gap among them included, and
a stage of neither; and `result` written, not written, and not JSON."""

from __future__ import annotations

import os
from typing import Any

import pytest
import rn_files
from fault import Wrong
from repository.place import RunPlace
from rounds.files import Round, at, new, of, result

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


@pytest.mark.supports("test_an_evaluators_findings_go_to_the_next_rounds_generator_as_given")
def test_of_a_deliverable_with_no_round_gives_none(run: RunPlace):
    """Given a run with no Round
    When the guide's Rounds are asked
    Then there are none"""
    assert of(run, GUIDE) == []


@pytest.mark.supports("test_an_evaluators_findings_go_to_the_next_rounds_generator_as_given")
def test_of_a_deliverable_with_one_round_gives_it(run: RunPlace):
    """Given a run whose guide has Round content-1
    When the guide's Rounds are asked
    Then it gives content-1 alone, with the guide's path, stage, and number"""
    rn_files.a_round(folder(run), GUIDE, "content", 1)
    assert seen(of(run, GUIDE)) == [expected(run, GUIDE, "content", 1)]


@pytest.mark.supports("test_an_evaluators_findings_go_to_the_next_rounds_generator_as_given")
def test_of_gives_content_before_refactor_each_by_its_number(run: RunPlace):
    """Given a run whose guide has Rounds refactor-1, content-10, content-2, and content-1, made in
    that order
    When the guide's Rounds are asked
    Then it gives content-1, content-2, content-10, then refactor-1, as numbers order them"""
    for stage, number in (("refactor", 1), ("content", 10), ("content", 2), ("content", 1)):
        rn_files.a_round(folder(run), GUIDE, stage, number)
    assert seen(of(run, GUIDE)) == [
        expected(run, GUIDE, "content", 1),
        expected(run, GUIDE, "content", 2),
        expected(run, GUIDE, "content", 10),
        expected(run, GUIDE, "refactor", 1),
    ]


@pytest.mark.supports("test_an_evaluators_findings_go_to_the_next_rounds_generator_as_given")
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


@pytest.mark.supports("test_an_evaluators_findings_go_to_the_next_rounds_generator_as_given")
@pytest.mark.parametrize("name", ["content-x", "draft-1", "content-0", "content1"])
def test_of_refuses_a_folder_of_another_form(run: RunPlace, name: str):
    """Given a run whose guide's Rounds folder holds content-1 and a folder of another form
    When the guide's Rounds are asked
    Then it raises Wrong naming the folder"""
    rn_files.a_round(folder(run), GUIDE, "content", 1)
    os.makedirs(os.path.join(folder(run), "rounds", "docs%2Fguide.md", name))
    with pytest.raises(Wrong, match=name):
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


@pytest.mark.supports("test_an_evaluators_findings_go_to_the_next_rounds_generator_as_given")
def test_new_with_no_round_of_the_stage_makes_its_first(run: RunPlace):
    """Given a run with no Round
    When a new content Round of the guide is made
    Then it is content-1, its folder made"""
    made = new(run, GUIDE, "content")
    assert seen([made]) == [expected(run, GUIDE, "content", 1)]
    assert os.path.isdir(made.folder)


@pytest.mark.supports("test_an_evaluators_findings_go_to_the_next_rounds_generator_as_given")
def test_new_makes_the_round_one_past_the_stages_last(run: RunPlace):
    """Given a run whose guide has Rounds content-1 and content-3, and refactor-1
    When a new content Round, then a new refactor Round, of the guide are made
    Then they are content-4 and refactor-2, each folder made"""
    for stage, number in (("content", 1), ("content", 3), ("refactor", 1)):
        rn_files.a_round(folder(run), GUIDE, stage, number)
    content, refactor = new(run, GUIDE, "content"), new(run, GUIDE, "refactor")
    assert seen([content, refactor]) == [
        expected(run, GUIDE, "content", 4),
        expected(run, GUIDE, "refactor", 2),
    ]
    assert os.path.isdir(content.folder) and os.path.isdir(refactor.folder)


@pytest.mark.supports("test_an_evaluators_findings_go_to_the_next_rounds_generator_as_given")
def test_new_counts_only_the_deliverables_own_rounds(run: RunPlace):
    """Given a run whose command has Rounds content-1 and content-2
    When a new content Round of the guide is made
    Then it is the guide's content-1"""
    for number in (1, 2):
        rn_files.a_round(folder(run), rn_files.COMMAND, "content", number)
    assert seen([new(run, GUIDE, "content")]) == [expected(run, GUIDE, "content", 1)]


@pytest.mark.supports("test_an_evaluators_findings_go_to_the_next_rounds_generator_as_given")
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


@pytest.mark.supports("test_an_evaluators_findings_go_to_the_next_rounds_generator_as_given")
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


@pytest.mark.supports("test_an_evaluators_findings_go_to_the_next_rounds_generator_as_given")
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
