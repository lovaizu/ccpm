"""The unit cases of check/result.py, whether a role's result holds what its Cut gave it: for the
generator, a result that holds, one out of its schema, a good of a condition the deliverable lacks,
a point with no words, a file outside the deliverable's paths and the Round's folder beside files
inside them and one that nearly matches, and a line that no file of the deliverable holds; for the
evaluator, each condition answered once, and one unanswered, answered in both, answered twice, and
an ID the Cut doesn't hold; for the generator of a kind whose best practice holds a template.md,
each Markdown file of the deliverable off it, one on it, and a file that isn't Markdown, and the
same Markdown of a kind with no template.md, and of the evaluator; and a role of neither. Each Cut
and result is read from the JSON of its file. The conversation's folder, from which the Cut's paths
are given, is the user's repository's top, given as `cwd`, while the case's process runs in
another folder, so that a body that reads the Cut's paths from its own folder fails."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
import rn_files
from check.result import faults
from fault import Wrong
from repo_files import write_files
from template.check import faults as template_faults

NAME = "20261120-a-command-with-which-the"
COMMAND = rn_files.COMMAND
LINE = "from invoicer.lines import parse_lines"
TEXT = f'"""Prints an invoice."""\n{LINE}\n'
TEST_LINE = "def test_the_command_prints_the_total():"
GUIDE = rn_files.GUIDE
# A guide off the readme template: a heading and a paragraph, none of the template's sections.
OFF = "# Print an invoice\n\nSave the lines as lines.csv, and type the command.\n"
# A guide on the readme template: rn's own README, which check.sh holds to it.
with open(os.path.join(rn_files.RN, "README.md"), encoding="utf-8") as _f:
    ON = _f.read()
README_FORM = os.path.join(rn_files.PRACTICES, "readme", "template.md")


class Run:
    """The run of the case: the repository's top, the run's worktree, and the command's Round
    content-1, from the repository's top."""

    def __init__(self, repository: str):
        self.repository = repository
        self.worktree = rn_files.worktree_of(repository, NAME)
        folder = rn_files.folder_of(repository, NAME)
        self.round = os.path.relpath(rn_files.round_of(folder, COMMAND, "content", 1), repository)
        # The Round's folder from the worktree's top, as a generator's result names its files.
        self.round_in_worktree = os.path.relpath(
            os.path.join(repository, self.round), self.worktree
        )


@pytest.fixture
def run(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> Run:
    """The run, its worktree holding the command and its test under tests/, the case's process in a
    folder beside the repository."""
    repository = os.path.realpath(str(tmp_path))
    given = Run(repository)
    write_files(
        given.worktree,
        {COMMAND: TEXT, "tests/test_command.py": TEST_LINE + "\n", "README.md": "# invoicer\n"},
    )
    os.makedirs(os.path.join(repository, given.round))
    elsewhere = os.path.join(str(tmp_path), "elsewhere")
    os.makedirs(elsewhere)
    monkeypatch.chdir(elsewhere)
    return given


def from_json(run: Run, name: str, value: Any) -> Any:
    """The value written as JSON in the Round's folder and read back from its file."""
    path = os.path.join(run.repository, run.round, name)
    rn_files.write_json(path, value)
    return rn_files.read_json(path)


def generator_cut(run: Run, node: Any = None, kind: str = "light") -> Any:
    """The generator's Cut, of generator-cut.schema.json, of the node, else the command's of the
    kind light with its tests at tests/, by the best practice of the kind, read from JSON."""
    if node is None:
        node = rn_files.open_node(rn_files.COMMAND_NAME, COMMAND, "light", ["invoicer/lines.py"])
        node["more_paths"] = ["tests/"]
    cut = {
        "goal": rn_files.GOAL,
        "deliverable": node,
        "worktree": os.path.relpath(run.worktree, run.repository),
        "inputs": [
            os.path.relpath(os.path.join(run.worktree, "invoicer/lines.py"), run.repository)
        ],
        "best_practice": os.path.relpath(os.path.join(rn_files.PRACTICES, kind), run.repository),
        "stage": "content",
        "number": 1,
        "round": run.round,
        "findings": None,
        "last_good": None,
    }
    return from_json(run, "generator-cut.json", cut)


def evaluator_cut(run: Run) -> Any:
    """The command's evaluator's Cut, of evaluator-cut.schema.json, read from JSON."""
    cut = {
        "goal": rn_files.GOAL,
        "deliverable": {"name": rn_files.COMMAND_NAME, "path": COMMAND, "more_paths": ["tests/"]},
        "judges_by": rn_files.judged_by("light"),
        "worktree": os.path.relpath(run.worktree, run.repository),
        "round": run.round,
        "trial": "/tmp/rn-trial-x",
    }
    return from_json(run, "evaluator-cut.json", cut)


def generator(run: Run, result: Any) -> list[str]:
    """The faults of the generator's result, read from JSON, against its Cut."""
    cut = generator_cut(run)
    return faults(
        "generator", cut, from_json(run, "generator.json", result), run.worktree, run.repository
    )


def evaluator(run: Run, result: Any) -> list[str]:
    """The faults of the evaluator's result, read from JSON, against its Cut."""
    cut = evaluator_cut(run)
    return faults(
        "evaluator", cut, from_json(run, "evaluator.json", result), run.worktree, run.repository
    )


# The generator.


@pytest.mark.supports("test_a_generators_good_of_a_condition_its_deliverable_lacks_is_stopped")
def test_a_generators_made_that_holds_its_cut_has_no_fault(run: Run):
    """Given a generator's made naming the command, its test, and a note in the Round's folder,
    with N1 good by the command's line and N2 by the test's
    When its faults are asked
    Then there are none"""
    files = [COMMAND, "tests/test_command.py", os.path.join(run.round_in_worktree, "notes.md")]
    result = rn_files.made([("N1", [LINE]), ("N2", [TEST_LINE])], files)
    assert generator(run, result) == []


@pytest.mark.supports("test_a_generators_good_of_a_condition_its_deliverable_lacks_is_stopped")
def test_a_generators_made_with_no_good_and_no_file_has_no_fault(run: Run):
    """Given a generator's made with no good and no file, as its schema lets it
    When its faults are asked
    Then there are none"""
    assert generator(run, {"result": "made"}) == []


@pytest.mark.supports("test_a_generators_end_with_no_result_written_is_stopped")
def test_a_generators_point_with_its_words_has_no_fault(run: Run):
    """Given a generator's point with the point's words
    When its faults are asked
    Then there are none"""
    assert generator(run, rn_files.point()) == []


@pytest.mark.supports("test_a_generators_good_of_a_condition_its_deliverable_lacks_is_stopped")
def test_a_generators_result_out_of_its_schema_is_a_fault_at_its_place(run: Run):
    """Given a generator's result `done`
    When its faults are asked
    Then one names /result"""
    found = generator(run, {"result": "done"})
    assert any(each.startswith("/result") for each in found)


@pytest.mark.supports("test_a_generators_good_of_a_condition_its_deliverable_lacks_is_stopped")
def test_a_generators_good_of_a_condition_the_deliverable_lacks_is_a_fault_naming_it(run: Run):
    """Given a generator's made with N1 good and N9, which light's command doesn't hold, good
    When its faults are asked
    Then there is one, naming N9"""
    found = generator(run, rn_files.made([("N1", [LINE]), ("N9", [LINE])], [COMMAND]))
    assert len(found) == 1
    assert "N9" in found[0]


@pytest.mark.supports("test_a_generators_end_with_no_result_written_is_stopped")
def test_a_generators_point_with_no_words_is_a_fault(run: Run):
    """Given a generator's result `point` with no `point`
    When its faults are asked
    Then there is one, naming point"""
    found = generator(run, {"result": "point"})
    assert len(found) == 1
    assert "point" in found[0]


@pytest.mark.supports("test_a_generators_good_of_a_condition_its_deliverable_lacks_is_stopped")
@pytest.mark.parametrize(
    "outside", ["README.md", "tests-old/test_command.py", "invoicer/__main__.py.bak", "../notes.md"]
)
def test_a_generators_file_outside_its_paths_and_round_is_a_fault_naming_it(run: Run, outside: str):
    """Given a generator's made naming the command and a file outside the deliverable's paths and
    the Round's folder, one that nearly matches them among them
    When its faults are asked
    Then there is one, naming that file"""
    found = generator(run, rn_files.made([("N1", [LINE])], [COMMAND, outside]))
    assert len(found) == 1
    assert outside in found[0]


@pytest.mark.supports("test_a_generators_good_quoting_a_line_no_file_holds_is_stopped")
def test_a_generators_line_that_no_file_of_the_deliverable_holds_is_a_fault_naming_it(run: Run):
    """Given a generator's made whose N1 quotes the command's line and `# invoicer`, a line that
    only the README, outside the deliverable, holds
    When its faults are asked
    Then there is one, naming `# invoicer`"""
    found = generator(run, rn_files.made([("N1", [LINE, "# invoicer"])], [COMMAND]))
    assert len(found) == 1
    assert "# invoicer" in found[0]


@pytest.mark.supports("test_a_generators_good_quoting_a_line_no_file_holds_is_stopped")
def test_a_generators_line_changed_since_it_quoted_it_is_a_fault(run: Run):
    """Given a generator's made whose N1 quotes the command's line, and the command changed after
    so that it no longer holds it
    When its faults are asked
    Then there is one, naming the line"""
    result = rn_files.made([("N1", [LINE])], [COMMAND])
    write_files(run.worktree, {COMMAND: '"""Prints an invoice."""\n'})
    found = generator(run, result)
    assert len(found) == 1
    assert LINE in found[0]


# The evaluator.


def answers(good: list[str], more: list[str]) -> Any:
    """An evaluator's judged, each condition of `good` good by the command's line, and each of
    `more` with what would make it good."""
    return rn_files.judged([(c, [LINE]) for c in good], [(c, "They print it.") for c in more])


@pytest.mark.supports("test_an_evaluators_end_leaving_a_condition_unanswered_is_stopped")
def test_an_evaluators_answer_of_each_condition_once_has_no_fault(run: Run):
    """Given an evaluator's judged with N1 and N3 good and N2 more
    When its faults are asked
    Then there are none"""
    assert evaluator(run, answers(["N1", "N3"], ["N2"])) == []


@pytest.mark.supports("test_an_evaluators_end_leaving_a_condition_unanswered_is_stopped")
def test_an_evaluators_condition_unanswered_is_a_fault_naming_it(run: Run):
    """Given an evaluator's judged with N1 and N2 good, N3 unanswered
    When its faults are asked
    Then there is one, naming N3"""
    found = evaluator(run, answers(["N1", "N2"], []))
    assert len(found) == 1
    assert "N3" in found[0]


@pytest.mark.supports("test_an_evaluators_end_leaving_a_condition_unanswered_is_stopped")
def test_an_evaluators_conditions_each_unanswered_are_each_a_fault(run: Run):
    """Given an evaluator's judged with no answer at all
    When its faults are asked
    Then there are three, one naming each of N1, N2, and N3"""
    found = evaluator(run, answers([], []))
    assert len(found) == 3
    assert all(any(c in each for each in found) for c in ("N1", "N2", "N3"))


@pytest.mark.supports("test_an_evaluators_end_leaving_a_condition_unanswered_is_stopped")
def test_an_evaluators_condition_answered_good_and_more_is_a_fault_naming_it(run: Run):
    """Given an evaluator's judged with N1, N2, and N3 good, and N2 more as well
    When its faults are asked
    Then there is one, naming N2"""
    found = evaluator(run, answers(["N1", "N2", "N3"], ["N2"]))
    assert len(found) == 1
    assert "N2" in found[0]


@pytest.mark.supports("test_an_evaluators_end_leaving_a_condition_unanswered_is_stopped")
@pytest.mark.parametrize(
    ("good", "more"), [(["N1", "N1", "N2", "N3"], []), (["N2", "N3"], ["N1", "N1"])]
)
def test_an_evaluators_condition_answered_twice_is_a_fault_naming_it(
    run: Run, good: list[str], more: list[str]
):
    """Given an evaluator's judged answering N1 twice, in good or in more, and N2 and N3 once
    When its faults are asked
    Then there is one, naming N1"""
    found = evaluator(run, answers(good, more))
    assert len(found) == 1
    assert "N1" in found[0]


@pytest.mark.supports("test_an_evaluators_end_leaving_a_condition_unanswered_is_stopped")
@pytest.mark.parametrize("unknown", ["N4", "N10", "n1", "C1"])
def test_an_evaluators_id_the_cut_doesnt_hold_is_a_fault_naming_it(run: Run, unknown: str):
    """Given an evaluator's judged answering N1 to N3 once, and an ID the Cut doesn't hold among
    its conditions, such as one past the last, one whose prefix is N1, or a factor's ID
    When its faults are asked
    Then there is one, naming that ID"""
    found = evaluator(run, answers(["N1", "N2", "N3", unknown], []))
    assert len(found) == 1
    assert unknown in found[0]


@pytest.mark.supports("test_a_generators_good_quoting_a_line_no_file_holds_is_stopped")
def test_an_evaluators_line_in_the_deliverables_more_paths_holds(run: Run):
    """Given an evaluator's judged whose N2 quotes the line of the command's test under tests/
    When its faults are asked
    Then there are none"""
    result = rn_files.judged([("N1", [LINE]), ("N2", [TEST_LINE])], [("N3", "They print it.")])
    assert evaluator(run, result) == []


@pytest.mark.supports("test_a_generators_good_quoting_a_line_no_file_holds_is_stopped")
def test_an_evaluators_line_that_no_file_of_the_deliverable_holds_is_a_fault(run: Run):
    """Given an evaluator's judged whose N1 quotes `print('receipt')`, which no file holds
    When its faults are asked
    Then there is one, naming the line"""
    result = rn_files.judged([("N1", ["print('receipt')"]), ("N2", [LINE]), ("N3", [LINE])])
    found = evaluator(run, result)
    assert len(found) == 1
    assert "print('receipt')" in found[0]


@pytest.mark.supports("test_an_evaluators_end_leaving_a_condition_unanswered_is_stopped")
def test_an_evaluators_result_out_of_its_schema_is_a_fault(run: Run):
    """Given an evaluator's judged whose N1's good_when is empty
    When its faults are asked
    Then one names the place of good_when"""
    result = json.loads(json.dumps(answers(["N2", "N3"], ["N1"])))
    result["more"][0]["good_when"] = ""
    found = evaluator(run, result)
    assert any(each.startswith("/more/0/good_when") for each in found)


@pytest.mark.supports("test_an_evaluators_end_leaving_a_condition_unanswered_is_stopped")
@pytest.mark.parametrize("role", ["orchestrator", "Evaluator", ""])
def test_a_role_of_neither_is_refused(run: Run, role: str):
    """Given the evaluator's Cut and its judged
    When the faults of a role that is neither generator nor evaluator are asked
    Then it raises Wrong"""
    with pytest.raises(Wrong):
        faults(
            role, evaluator_cut(run), answers(["N1", "N2", "N3"], []), run.worktree, run.repository
        )


# The template check of a generator's Markdown.


def guide_node(kind: str, more: list[str] | None = None) -> Any:
    """The guide's open node of the kind, with the more paths given."""
    node = rn_files.open_node(rn_files.GUIDE_NAME, GUIDE, kind, [COMMAND])
    if more:
        node["more_paths"] = more
    return node


def guide_faults(run: Run, kind: str, text: str, more: list[str] | None = None) -> list[str]:
    """The faults of a generator's made of the guide of the kind, its text as given, with no
    good, against its Cut."""
    write_files(run.worktree, {GUIDE: text})
    cut = generator_cut(run, guide_node(kind, more), kind)
    result = from_json(run, "generator.json", rn_files.made([], [GUIDE, *(more or [])]))
    return faults("generator", cut, result, run.worktree, run.repository)


def template_places(text: str) -> list[str]:
    """Each fault that the readme template's check finds in the guide's text, as
    `<file>:<line>: <what>`, the file by its path from the worktree's top."""
    with open(README_FORM, encoding="utf-8") as f:
        form = f.read()
    return [f"{GUIDE}:{each.line}: {each.what}" for each in template_faults(form, text)]


@pytest.mark.supports("test_a_generators_end_with_its_deliverable_off_its_template_is_held")
def test_a_generators_markdown_off_its_kinds_template_gives_each_place(run: Run):
    """Given a generator's made of the guide, of the kind readme, whose best practice holds a
    template.md, the guide a heading and a paragraph alone
    When its faults are asked
    Then they are each place that the template check finds, as `docs/guide.md:<line>: <what>`,
    and nothing more"""
    places = template_places(OFF)
    assert places
    assert guide_faults(run, "readme", OFF) == places


@pytest.mark.supports("test_a_generators_end_with_its_deliverable_off_its_template_is_held")
def test_a_generators_markdown_on_its_kinds_template_has_no_fault(run: Run):
    """Given a generator's made of the guide, of the kind readme, the guide holding the template,
    as rn's own README does
    When its faults are asked
    Then there are none"""
    assert template_places(ON) == []
    assert guide_faults(run, "readme", ON) == []


@pytest.mark.supports("test_a_generators_end_with_its_deliverable_off_its_template_is_held")
def test_a_generators_file_that_isnt_markdown_isnt_held_to_the_template(run: Run):
    """Given a generator's made of the guide, of the kind readme, on the template, with a more path
    docs/lines.csv, a file that isn't Markdown, that holds none of it
    When its faults are asked
    Then there are none"""
    write_files(run.worktree, {"docs/lines.csv": "Hosting;40.00;1\n"})
    assert guide_faults(run, "readme", ON, ["docs/lines.csv"]) == []


@pytest.mark.supports("test_a_generators_end_with_its_deliverable_off_its_template_is_held")
def test_a_generators_markdown_of_a_kind_with_no_template_isnt_held(run: Run):
    """Given a generator's made of the guide, of the kind light, whose best practice's folder holds
    no template.md, the guide off the readme template
    When its faults are asked
    Then there are none"""
    assert not os.path.exists(os.path.join(rn_files.PRACTICES, "light", "template.md"))
    assert guide_faults(run, "light", OFF) == []


@pytest.mark.supports("test_a_generators_end_with_its_deliverable_off_its_template_is_held")
def test_an_evaluators_markdown_off_the_template_isnt_held(run: Run):
    """Given the guide off the readme template, and an evaluator's judged of it, each condition
    of readme answered good by its heading
    When the evaluator's faults are asked
    Then there are none, as the template check holds the generator alone"""
    write_files(run.worktree, {GUIDE: OFF})
    cut = from_json(
        run,
        "evaluator-cut.json",
        {
            "goal": rn_files.GOAL,
            "deliverable": {"name": rn_files.GUIDE_NAME, "path": GUIDE},
            "judges_by": rn_files.judged_by("readme"),
            "worktree": os.path.relpath(run.worktree, run.repository),
            "round": run.round,
            "trial": "/tmp/rn-trial-x",
        },
    )
    ids = rn_files.conditions("readme")
    result = from_json(
        run, "evaluator.json", rn_files.judged([(c, ["# Print an invoice"]) for c in ids])
    )
    assert faults("evaluator", cut, result, run.worktree, run.repository) == []


@pytest.mark.supports("test_a_generators_end_with_its_deliverable_off_its_template_is_held")
def test_a_generators_good_and_template_faults_come_together(run: Run):
    """Given a generator's made of the guide, of the kind readme, off the template, whose good of
    N1 quotes a line the guide doesn't hold
    When its faults are asked
    Then they hold one naming the line, and each place of the template check"""
    write_files(run.worktree, {GUIDE: OFF})
    cut = generator_cut(run, guide_node("readme"), "readme")
    result = from_json(
        run, "generator.json", rn_files.made([("N1", ["# Print a receipt"])], [GUIDE])
    )
    found = faults("generator", cut, result, run.worktree, run.repository)
    assert [each for each in found if "# Print a receipt" in each] != []
    assert set(template_places(OFF)) <= set(found)
    assert len(found) == len(template_places(OFF)) + 1


@pytest.mark.supports("test_a_generators_end_with_its_deliverable_off_its_template_is_held")
def test_each_markdown_file_is_named_from_the_worktrees_top_not_the_conversations_folder(
    run: Run,
):
    """Given a generator's made of the guide, of the kind readme, off the template, with a more
    path docs/print/steps.md off it too, the conversation working at the repository's top, apart
    from the worktree
    When its faults are asked
    Then they are each place of each file, the guide's as `docs/guide.md:<line>: <what>` and the
    steps' as `docs/print/steps.md:<line>: <what>`, and none names a file by its path from the
    conversation's folder"""
    steps = "docs/print/steps.md"
    write_files(run.worktree, {steps: OFF})
    found = guide_faults(run, "readme", OFF, [steps])
    expected = template_places(OFF) + [
        each.replace(f"{GUIDE}:", f"{steps}:", 1) for each in template_places(OFF)
    ]
    assert run.worktree != run.repository
    assert sorted(found) == sorted(expected)
    assert not any(each.startswith(".claude/") for each in found)
