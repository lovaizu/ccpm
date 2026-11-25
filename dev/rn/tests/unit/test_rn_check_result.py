"""The unit cases of check/result.py, whether a role's result holds what its Cut gave it: for the
generator, a result that holds, one out of its schema, a good of a condition the deliverable lacks,
a point with no words, a file outside the deliverable's paths and the Round's folder, and a line
that no file of the deliverable holds; for the fixer, files in the deliverable's paths and the
Fix's folder, a file outside them, a result out of its schema, and a guide off its template, which
the fixer isn't held to; for the evaluator, each condition answered once, and one unanswered,
answered in both, answered twice, and an ID the Cut doesn't hold; a role of none of them; and for
the generator of a kind whose best practice holds a template.md, the deliverable's Markdown path
off it, one on it, one held in the Cut's language, a Markdown more path, and Markdown files inside
a folder deliverable, and the same Markdown of a kind with no template.md. Each Cut and result is
read from the JSON of its file. The conversation's folder, from which the Cut's paths are given, is
the user's repository's top, given as `cwd`, while the case's process runs in another folder, so
that a body that reads the Cut's paths from its own folder fails."""

from __future__ import annotations

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
        self.fix = os.path.relpath(rn_files.round_of(folder, COMMAND, "fix", 2), repository)
        self.folder = os.path.relpath(folder, repository)
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
    kind light with its tests at tests/, by the kind's best practice, with the
    kind's template where its folder holds one, read from JSON."""
    template = os.path.join(rn_files.PRACTICES, kind, "template.md")
    if node is None:
        node = rn_files.open_node(rn_files.COMMAND_NAME, COMMAND, "light", ["invoicer/lines.py"])
        node["more_paths"] = ["tests/"]
    cut = {
        "goal": rn_files.GOAL,
        "language": rn_files.DELIVERABLES_LANGUAGE,
        "deliverable": node,
        "worktree": os.path.relpath(run.worktree, run.repository),
        "inputs": [
            os.path.relpath(os.path.join(run.worktree, "invoicer/lines.py"), run.repository)
        ],
        "best_practice": os.path.relpath(os.path.join(rn_files.PRACTICES, kind), run.repository),
        "template": (
            os.path.relpath(template, run.repository) if os.path.isfile(template) else None
        ),
        "stage": "content",
        "number": 1,
        "round": run.round,
        "trial": "/tmp/rn-trial-x",
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


def fixer_cut(run: Run, node: Any = None) -> Any:
    """The fixer's Cut, of fixer-cut.schema.json, of the node, else the command's with its tests
    at tests/, read from JSON in the Fix's folder."""
    if node is None:
        node = rn_files.open_node(rn_files.COMMAND_NAME, COMMAND, "light", ["invoicer/lines.py"])
        node["more_paths"] = ["tests/"]
    paths = [node["path"], *node.get("more_paths", [])]
    cut = {
        "deliverable": node,
        "worktree": os.path.relpath(run.worktree, run.repository),
        "paths": [os.path.relpath(os.path.join(run.worktree, p), run.repository) for p in paths],
        "problem": {"source": "put-up", "words": "lint: a line ends in a space"},
        "run": run.folder,
        "fix": run.fix,
    }
    path = os.path.join(run.repository, run.fix, "fixer-cut.json")
    rn_files.write_json(path, cut)
    return rn_files.read_json(path)


def fixer(run: Run, result: Any, node: Any = None) -> list[str]:
    """The faults of the fixer's result, read from JSON in the Fix's folder, against its Cut of the
    node, else the command's."""
    cut = fixer_cut(run, node)
    path = os.path.join(run.repository, run.fix, "fixer.json")
    rn_files.write_json(path, result)
    return faults("fixer", cut, rn_files.read_json(path), run.worktree, run.repository)


# The generator.


def test_a_generators_made_that_holds_its_cut_has_no_fault(run: Run):
    """Given a generator's made naming the command, its test, and a note in the Round's folder,
    with N1 good by the command's line and N2 by the test's
    When its faults are asked
    Then there are none"""
    files = [COMMAND, "tests/test_command.py", os.path.join(run.round_in_worktree, "notes.md")]
    result = rn_files.made([("N1", [LINE]), ("N2", [TEST_LINE])], files)
    assert generator(run, result) == []


def test_a_generators_result_out_of_its_schema_is_a_fault_at_its_place(run: Run):
    """Given a generator's result `done`
    When its faults are asked
    Then one names /result"""
    found = generator(run, {"result": "done"})
    assert any(each.startswith("/result") for each in found)


def test_a_generators_good_of_a_condition_the_deliverable_lacks_is_a_fault_naming_it(run: Run):
    """Given a generator's made with N1 good and N9, which light's command doesn't hold, good
    When its faults are asked
    Then there is one, naming N9"""
    found = generator(run, rn_files.made([("N1", [LINE]), ("N9", [LINE])], [COMMAND]))
    assert len(found) == 1
    assert "N9" in found[0]


def test_a_generators_point_with_no_words_is_a_fault(run: Run):
    """Given a generator's result `point` with no `point`
    When its faults are asked
    Then there is one, naming point"""
    found = generator(run, {"result": "point"})
    assert len(found) == 1
    assert "point" in found[0]


def test_a_generators_file_outside_its_paths_and_round_is_a_fault_naming_it(run: Run):
    """Given a generator's made naming the command and tests-old/test_command.py, a file outside
    the deliverable's paths and the Round's folder that nearly matches its more path tests/
    When its faults are asked
    Then there is one, naming that file, the deliverable's paths, and the Round's folder"""
    outside = "tests-old/test_command.py"
    found = generator(run, rn_files.made([("N1", [LINE])], [COMMAND, outside]))
    assert found == [
        f"{outside}: lies outside the deliverable's paths and the Round's folder; write only there"
    ]


def test_a_generators_line_that_no_file_of_the_deliverable_holds_is_a_fault_naming_it(run: Run):
    """Given a generator's made whose N1 quotes the command's line and `# invoicer`, a line that
    only the README, outside the deliverable, holds
    When its faults are asked
    Then there is one, naming `# invoicer`"""
    found = generator(run, rn_files.made([("N1", [LINE, "# invoicer"])], [COMMAND]))
    assert len(found) == 1
    assert "# invoicer" in found[0]


# The fixer.


def test_a_fixers_files_in_its_paths_and_fix_have_no_fault(run: Run):
    """Given a fixer's fixed naming the command, a file under its more path tests/, and a file in
    the Fix's folder, by its path from the worktree's top
    When its faults are asked
    Then there is none"""
    inside = os.path.relpath(os.path.join(run.repository, run.fix, "notes.txt"), run.worktree)
    files = [COMMAND, "tests/test_command.py", inside]
    assert fixer(run, {"result": "fixed", "files": files}) == []


def test_a_fixers_file_outside_its_paths_and_fix_is_a_fault_naming_it(run: Run):
    """Given a fixer's fixed naming the command and the run's design tree, beside the Fix's folder
    When its faults are asked
    Then there is one, naming that file, the deliverable's paths, and the Fix's folder"""
    outside = os.path.join(".rn", NAME, "design-tree.json")
    found = fixer(run, {"result": "fixed", "files": [COMMAND, outside]})
    assert found == [
        f"{outside}: lies outside the deliverable's paths and the Fix's folder; write only there"
    ]


def test_a_fixers_result_out_of_its_schema_is_a_fault(run: Run):
    """Given a fixer's fixed with no files, out of fixer-fix.schema.json
    When its faults are asked
    Then there is at least one, the result left unchecked by its files"""
    assert fixer(run, {"result": "fixed"}) != []


def test_a_fixers_markdown_off_its_kinds_template_isnt_held(run: Run):
    """Given the guide, of the kind readme, off its template, and a fixer's fixed naming it
    When its faults are asked
    Then there is none, as the fixer mends within the decisions, by no best practice"""
    write_files(run.worktree, {GUIDE: OFF})
    node = rn_files.done_node(rn_files.GUIDE_NAME, GUIDE, "readme")
    assert fixer(run, {"result": "fixed", "files": [GUIDE]}, node) == []


# The evaluator.


def answers(good: list[str], more: list[str]) -> Any:
    """An evaluator's judged, each condition of `good` good by the command's line, and each of
    `more` with what would make it good."""
    return rn_files.judged([(c, [LINE]) for c in good], [(c, "They print it.") for c in more])


def test_an_evaluators_answer_of_each_condition_once_has_no_fault(run: Run):
    """Given an evaluator's judged with N1 and N3 good and N2 more
    When its faults are asked
    Then there are none"""
    assert evaluator(run, answers(["N1", "N3"], ["N2"])) == []


def test_an_evaluators_condition_unanswered_is_a_fault_naming_it(run: Run):
    """Given an evaluator's judged with N1 and N2 good, N3 unanswered
    When its faults are asked
    Then there is one, naming N3"""
    found = evaluator(run, answers(["N1", "N2"], []))
    assert len(found) == 1
    assert "N3" in found[0]


def test_an_evaluators_condition_answered_good_and_more_is_a_fault_naming_it(run: Run):
    """Given an evaluator's judged with N1, N2, and N3 good, and N2 more as well
    When its faults are asked
    Then there is one, naming N2"""
    found = evaluator(run, answers(["N1", "N2", "N3"], ["N2"]))
    assert len(found) == 1
    assert "N2" in found[0]


def test_an_evaluators_condition_answered_twice_is_a_fault_naming_it(run: Run):
    """Given an evaluator's judged answering N1 twice in good, and N2 and N3 once
    When its faults are asked
    Then there is one, naming N1"""
    found = evaluator(run, answers(["N1", "N1", "N2", "N3"], []))
    assert len(found) == 1
    assert "N1" in found[0]


def test_an_evaluators_id_the_cut_doesnt_hold_is_a_fault_naming_it(run: Run):
    """Given an evaluator's judged answering N1 to N3 once, and N4, which the Cut doesn't hold
    When its faults are asked
    Then there is one, naming N4"""
    found = evaluator(run, answers(["N1", "N2", "N3", "N4"], []))
    assert len(found) == 1
    assert "N4" in found[0]


def test_a_role_of_neither_is_refused(run: Run):
    """Given the evaluator's Cut and its judged
    When the faults of the role orchestrator, none of generator, evaluator, and fixer, are asked
    Then it raises Wrong"""
    with pytest.raises(Wrong):
        faults(
            "orchestrator",
            evaluator_cut(run),
            answers(["N1", "N2", "N3"], []),
            run.worktree,
            run.repository,
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


def test_a_generators_markdown_off_its_kinds_template_gives_each_place(run: Run):
    """Given a generator's made of the guide, of the kind readme, whose best practice holds a
    template.md, the guide a heading and a paragraph alone
    When its faults are asked
    Then they are each place that the template check finds, as `docs/guide.md:<line>: <what>`,
    and nothing more"""
    places = template_places(OFF)
    assert places
    assert guide_faults(run, "readme", OFF) == places


def test_a_generators_markdown_on_its_kinds_template_has_no_fault(run: Run):
    """Given a generator's made of the guide, of the kind readme, the guide holding the template,
    as rn's own README does
    When its faults are asked
    Then there are none"""
    assert template_places(ON) == []
    assert guide_faults(run, "readme", ON) == []


# A guide in Japanese on the readme template in its own words: a title and two paragraphs.
ON_JA = (
    "# 請求書印刷\n\n請求書印刷は表の行から請求書を印刷するコマンドです。\n\n"
    "表に行を持つときに使えます。一度で請求書が手に入ります。\n"
)


def test_a_generators_markdown_is_held_to_the_template_in_its_cuts_language(run: Run):
    """Given a generator's made of the guide, of the kind readme, whose Cut's language is Japanese,
    the guide in Japanese on the template's form in its own words, which leaves the template's
    English words
    When its faults are asked
    Then there are none, as the template check holds the guide in the Cut's language"""
    assert template_places(ON_JA) != []
    write_files(run.worktree, {GUIDE: ON_JA})
    cut = generator_cut(run, guide_node("readme"), "readme")
    cut["language"] = "Japanese"
    result = from_json(run, "generator.json", rn_files.made([], [GUIDE]))
    assert faults("generator", cut, result, run.worktree, run.repository) == []


def test_a_generators_markdown_of_a_kind_with_no_template_isnt_held(run: Run):
    """Given a generator's made of the guide, of the kind light, whose best practice's folder holds
    no template.md, the guide off the readme template
    When its faults are asked
    Then there are none"""
    assert not os.path.exists(os.path.join(rn_files.PRACTICES, "light", "template.md"))
    assert guide_faults(run, "light", OFF) == []


def test_a_markdown_more_path_isnt_held_to_the_template(run: Run):
    """Given a generator's made of the guide, of the kind readme, on the template, with a more
    path docs/print/steps.md off it
    When its faults are asked
    Then there are none, as the template holds only the document that the kind makes, at the
    deliverable's path"""
    steps = "docs/print/steps.md"
    write_files(run.worktree, {steps: OFF})
    assert guide_faults(run, "readme", ON, [steps]) == []


def test_markdown_inside_a_folder_deliverable_isnt_held_to_the_template(run: Run):
    """Given a generator's made of a skeleton, of the kind readme, whose path is the folder
    skeleton/, holding a README.md and a skills/on/SKILL.md, each off the readme template
    When its faults are asked
    Then there are none, as no file found in a folder is the document that the kind makes"""
    inside = {"skeleton/README.md": OFF, "skeleton/skills/on/SKILL.md": OFF}
    write_files(run.worktree, inside)
    node = rn_files.open_node("rn's skeleton", "skeleton/", "readme", [])
    cut = generator_cut(run, node, "readme")
    result = from_json(run, "generator.json", rn_files.made([], ["skeleton/"]))
    assert faults("generator", cut, result, run.worktree, run.repository) == []
