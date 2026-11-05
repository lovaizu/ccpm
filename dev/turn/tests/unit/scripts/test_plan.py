"""scripts/plan.py, what the planner runs on a run's folder: start, hand, ready and next move the
work the run is at, each printing what the planner gives and ends with, 0, or why it cannot, 1;
check says whether the Run holds and where the run is, 0, each fault, 1, or why it could not
check, 2. And what a person or CI runs on a best practice: form, its faults and its Markdown and
the copy of its example left behind; markdown, its Markdown written beside it; and example, the copy
of its example written from its source."""

import contextlib
import copy
import io
import json
import os
import runpy
import unittest
from unittest import mock

import helpers
from helpers import met, phases, plan, practices, runs, short

from unit.core.domain.test_practices import DATA

RUN = helpers.RUN
DESIGN = os.path.join(RUN, runs.DESIGN)
USAGE = (
    "usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan.py start|hand|ready|next|check <run>\n"
    "       python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan.py form|markdown|example"
    " <best practice json>...\n"
)


def ran(*argv):
    """What plan.py gives on the arguments: its exit code, what it printed, and its errors."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = plan.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class Usage(unittest.TestCase):
    def test_a_call_it_does_not_take_gives_2_and_its_usage(self):
        for argv in ((), ("start",), ("start", "a", "b"), ("go", "a"), ("form",)):
            with self.subTest(argv=argv):
                self.assertEqual(ran(*argv), (2, "", USAGE))

    def test_the_script_takes_the_arguments_after_its_own_path(self):
        with (
            mock.patch.object(plan.sys, "argv", ["plan.py"]),
            contextlib.redirect_stderr(io.StringIO()),
            self.assertRaises(SystemExit) as end,
        ):
            runpy.run_path(plan.__file__, run_name="__main__")
        self.assertEqual(end.exception.code, 2)


class Script(helpers.RepositoryTest):
    def test_the_script_runs_the_command_given_after_its_own_path(self):
        with (
            mock.patch.object(plan.sys, "argv", ["plan.py", "check", RUN]),
            contextlib.redirect_stdout(io.StringIO()) as out,
            self.assertRaises(SystemExit) as end,
        ):
            runpy.run_path(plan.__file__, run_name="__main__")
        self.assertEqual(end.exception.code, 0)
        self.assertTrue(out.getvalue().startswith(f"plan.py: {RUN} holds no Run yet."))


class Start(helpers.RepositoryTest):
    def test_a_run_begun_prints_the_request_to_end_with(self):
        self.calls()
        self.assertEqual(
            ran("start", RUN),
            (
                0,
                f"plan.py: {RUN} is begun, and its design handed over at {DESIGN}. Give `handed`,"
                " and end with this Request as it is:\n"
                + runs.request(DESIGN, "a note on tidy")
                + "\n",
                "",
            ),
        )

    def test_a_kind_new_to_turn_names_the_design_of_its_best_practice(self):
        self.calls(helpers.call(kind="man-page", kind_goal="Someone learns each option."))
        design = os.path.join(RUN, "best-practice", runs.DESIGN)
        code, out, _ = ran("start", RUN)
        self.assertEqual(code, 0)
        self.assertIn(f"its design handed over at {design}. Give `handed`", out)

    def test_a_run_that_cannot_begin_gives_1_and_why(self):
        self.calls(helpers.call(given={"kind": "readme"}))
        self.assertEqual(
            ran("start", RUN),
            (
                1,
                "",
                f"plan.py: {RUN} cannot start: the kind is note, but the calling AI gave readme\n",
            ),
        )


class Ready(helpers.RepositoryTest):
    def test_the_work_goes_to_its_rounds_and_the_generators_line_is_printed(self):
        self.lay_run([helpers.work(at="pin")])
        self.assertEqual(
            ran("ready", RUN),
            (
                0,
                "plan.py: the work of note is in its rounds. Give `ready`, and end with this line,"
                " for up to start the generator with:\n"
                + runs.generator_values(RUN, helpers.work())
                + "\n",
                "",
            ),
        )

    def test_a_work_with_no_paths_gives_1(self):
        self.lay_run([helpers.work(at="pin", paths=[])])
        code, out, err = ran("ready", RUN)
        self.assertEqual((code, out), (1, ""))
        self.assertIn("has no paths", err)


class Hand(helpers.RoundsTest):
    def test_the_shortfalls_go_to_pin_each_with_the_decisions_that_serve_its_question(self):
        phases.settle(RUN)
        self.answers("generator.json", {**met(), "open": [{"question": "note/Q3", "what": "w"}]})
        self.answers("G2.json", short("note/Q2"))
        code, out, err = ran("hand", RUN)
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(
            out,
            "plan.py: the design of note is handed to Pin again. Give `handed`, and end with this"
            " Request as it is, with on its last lines any change the request names, as given:\n"
            + json.dumps({"design": DESIGN})
            + "\nThe work made from this design falls short; each point names the decisions that"
            " serve its question:\n"
            "- note/Q3, left open: w (D1)\n"
            "- note/Q2: note/Q2 lacks (D2, D3)\n",
        )
        self.assertEqual(self.run_data()["works"][0]["at"], "pin")

    def test_with_no_shortfall_the_request_names_the_design_alone(self):
        code, out, _ = ran("hand", RUN)
        self.assertEqual(code, 0)
        self.assertTrue(out.endswith("as given:\n" + json.dumps({"design": DESIGN}) + "\n"), out)

    def test_a_design_it_cannot_read_gives_1(self):
        os.remove(DESIGN)
        code, _, err = ran("hand", RUN)
        self.assertEqual(code, 1)
        self.assertIn(f"plan.py: {RUN} cannot hand: there is no file {DESIGN}", err)


class Next(helpers.RoundsTest):
    def test_the_last_work_finished_ends_the_run_with_the_message(self):
        self.finished()
        self.assertEqual(
            ran("next", RUN),
            (
                0,
                "plan.py: the run is done. Give `done`, and end with this Message as it is:\n"
                + runs.done(helpers.work())
                + "\n",
                "",
            ),
        )
        self.assertEqual(self.run_data()["works"][0]["at"], "done")

    def test_a_best_practice_finished_hands_over_the_work_by_it(self):
        made = runs.practice_in(runs.REPOSITORY, "man-page")
        self.write_json(made, helpers.PRACTICE)
        self.lay_run(
            [
                helpers.work(kind="meta", paths=[made]),
                helpers.work(kind="man-page", practice=made, paths=[], at="waits"),
            ]
        )
        self.finished()
        code, out, _ = ran("next", RUN)
        self.assertEqual(code, 0)
        self.assertEqual(
            out,
            "plan.py: the work of meta is done, and the next handed over at"
            f" {DESIGN}. Give `handed`, and end with this Request as it is:\n"
            + runs.request(DESIGN, "a note on tidy")
            + "\n",
        )

    def test_rounds_that_have_not_met_every_question_give_1(self):
        phases.settle(RUN)
        self.assertEqual(
            ran("next", RUN),
            (
                1,
                "",
                (
                    f"plan.py: {RUN} cannot next: the rounds of note have not met every question of"
                    " both phases\n"
                ),
            ),
        )


class Check(helpers.RoundsTest):
    def checked(self):
        return ran("check", RUN)

    def holds(self, said):
        return (0, f"plan.py: {RUN} holds. {said}\n", "")

    def test_no_run_yet_says_how_to_begin_one(self):
        os.remove(os.path.join(RUN, "run.json"))
        self.assertEqual(
            self.checked(),
            (
                0,
                (
                    f"plan.py: {RUN} holds no Run yet. Settle the kind, write {RUN}/call.json"
                    f" in the form of {os.path.join(helpers.files.FORMS, 'call.json')}, then run"
                    f" plan.py start {RUN}.\n"
                ),
                "",
            ),
        )

    def test_a_work_with_pin(self):
        self.lay_run([helpers.work(at="pin", paths=[])])
        self.assertEqual(
            self.checked(),
            self.holds(
                f"The design of note is with Pin, at {DESIGN}.\nOnce Pin hands it back confirmed,"
                f" write into the work's paths, commands and files in {RUN}/run.json what the"
                f" design gives, then run plan.py ready {RUN}. To go on with it after the run"
                f" stopped, or to hand Pin a change, run plan.py hand {RUN}."
            ),
        )

    def test_a_work_whose_rounds_go_on(self):
        self.assertEqual(
            self.checked(),
            self.holds(
                f"The work of note is in its rounds.\nTo go on with them, run plan.py ready {RUN}."
                f" To hand Pin a change, run plan.py hand {RUN}."
            ),
        )

    def test_a_round_that_fell_short(self):
        phases.settle(RUN)
        self.answers("G1.json", short("note/Q1"))
        self.assertEqual(
            self.checked(),
            self.holds(
                f"The work of note is in its rounds.\nIts last round fell short: run plan.py hand"
                f" {RUN}."
            ),
        )

    def test_rounds_that_met_every_question(self):
        self.finished()
        self.assertEqual(
            self.checked(),
            self.holds(
                f"The work of note is in its rounds.\nIts rounds have met every question: run"
                f" plan.py next {RUN}."
            ),
        )

    def test_a_run_done(self):
        self.lay_run([helpers.work(at="done")])
        self.assertEqual(
            self.checked(),
            self.holds(
                "The run is done. Give `done`, and end with this Message as it is:\n"
                + runs.done(helpers.work(at="done"))
                + f"\nTo hand Pin a change, run plan.py hand {RUN}."
            ),
        )

    def test_a_work_in_its_rounds_with_no_paths_does_not_hold(self):
        self.lay_run([helpers.work(at="done", paths=[]), helpers.work(at="pin", paths=["d/"])])
        self.assertEqual(
            self.checked(),
            (
                1,
                (
                    f"plan.py: {RUN} does not hold:\n"
                    "- the work of note has no paths: write them into its paths\n"
                ),
                "",
            ),
        )

    def test_a_run_it_cannot_read_gives_2(self):
        self.write(os.path.join(RUN, "run.json"), "{")
        code, out, err = self.checked()
        self.assertEqual((code, out), (2, ""))
        self.assertIn(f"plan.py: could not check {RUN}:", err)


class Practices(helpers.testing.FolderTest):
    """form and markdown, on a best practice of the kind `kind`."""

    def setUp(self) -> None:
        super().setUp()
        self.folder = os.path.join(self.base, "kind")
        self.path = os.path.join(self.folder, "best-practice.json")
        self.write_json(self.path, DATA)

    def test_form_fails_until_markdown_writes_it(self):
        self.assertEqual(ran("form", self.path)[0], 1)
        self.assertEqual(ran("markdown", self.path), (0, "", ""))
        self.assertEqual(
            self.read(os.path.join(self.folder, "best-practice.md")),
            practices.markdown("kind", DATA),
        )
        self.assertEqual(ran("form", self.path), (0, "", ""))

    def test_form_fails_on_a_fault_of_the_form(self):
        data = copy.deepcopy(DATA)
        data["practices"].pop()
        self.write_json(self.path, data)
        ran("markdown", self.path)
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertIn(f"plan.py: {self.path}: {practices.faults(data)[0]}", err)

    def test_form_holds_the_questions_to_the_template_beside_it(self):
        data = copy.deepcopy(DATA)
        del data["parts"]
        for question in data["intents"]:
            question["about"] = "the whole"
        data["template"] = "template.md"
        self.write_json(self.path, data)
        self.write(os.path.join(self.folder, "template.md"), "# <P>\n\n## Use\n")
        ran("markdown", self.path)
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertIn(f"plan.py: {self.path}: section Use has no question about it", err)
        self.assertIn(
            "[template.md](template.md)", self.read(os.path.join(self.folder, "best-practice.md"))
        )

    def test_form_fails_on_a_file_it_names_that_is_not_beside_it(self):
        self.write_json(self.path, dict(DATA, example="example.md"))
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertIn(f"plan.py: {self.path}: its example example.md is not beside it", err)

    def test_form_fails_on_a_json_out_of_its_schema(self):
        self.write_json(self.path, {"goal": "g"})
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertIn("is out of its form", err)

    def test_form_fails_on_a_markdown_changed_by_hand(self):
        made = practices.markdown("kind", DATA)
        for changed in (made + "More.\n", made[:-1]):
            with self.subTest(changed=changed[-6:]):
                self.write(os.path.join(self.folder, "best-practice.md"), changed)
                code, _, err = ran("form", self.path)
                self.assertEqual(code, 1)
                self.assertIn(
                    "best-practice.md is not as its JSON makes it; run plan.py markdown", err
                )

    def sourced(self) -> str:
        """Names a source for the example, and writes it with a figure; gives the example's path."""
        self.write_json(self.path, dict(DATA, example="example.md", source="../doc/source.md"))
        self.write(os.path.join(self.base, "doc", "source.md"), "![A](images/a.svg) [b](b.md)\n")
        self.write(os.path.join(self.base, "doc", "images", "a.svg"), "<svg/>")
        ran("markdown", self.path)
        return os.path.join(self.folder, "example.md")

    def test_form_fails_until_example_copies_the_source_and_its_figures(self):
        example = self.sourced()
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertIn(f"plan.py: {self.path}: {example} is not a copy of its source", err)
        self.assertIn("; run plan.py example", err)
        self.assertEqual(ran("example", self.path), (0, "", ""))
        self.assertEqual(self.read(example), "![A](images/a.svg) [b](../doc/b.md)\n")
        self.assertEqual(self.read(os.path.join(self.folder, "images", "a.svg")), "<svg/>")
        self.assertEqual(ran("form", self.path), (0, "", ""))

    def test_form_fails_on_a_copy_or_figure_changed_by_hand(self):
        example = self.sourced()
        ran("example", self.path)
        figure = os.path.join(self.folder, "images", "a.svg")
        cuts = [(f, lambda text: "changed") for f in (example, figure)]
        cuts += [(f, lambda text: text[:-1]) for f in (example, figure)]
        for changed, cut in cuts:
            with self.subTest(changed=changed, cut=cut("ab")):
                ran("example", self.path)
                self.write(changed, cut(self.read(changed)))
                code, _, err = ran("form", self.path)
                self.assertEqual(code, 1)
                self.assertIn(f"{changed} is not a copy of its source; run plan.py example", err)

    def test_a_source_or_figure_not_there_is_named(self):
        self.sourced()
        os.remove(os.path.join(self.base, "doc", "images", "a.svg"))
        for command in ("form", "example"):
            with self.subTest(command=command):
                code, _, err = ran(command, self.path)
                self.assertEqual(code, 1)
                self.assertIn("a.svg, which its example copies, is not there", err)

    def test_a_source_with_no_example_to_copy_to_is_named(self):
        self.write_json(self.path, dict(DATA, source="../doc/source.md"))
        ran("markdown", self.path)
        for command in ("form", "example"):
            with self.subTest(command=command):
                code, _, err = ran(command, self.path)
                self.assertEqual(code, 1)
                self.assertIn("its source ../doc/source.md has no example to be copied to", err)

    def test_form_fails_on_a_figure_left_from_an_old_source_until_example_removes_it(self):
        self.sourced()
        ran("example", self.path)
        old = os.path.join(self.folder, "images", "old.svg")
        self.write(old, "<svg/>")
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertIn(
            f"plan.py: {self.path}: {old} is neither the template's nor the example's;"
            " run plan.py example",
            err,
        )
        self.assertEqual(ran("example", self.path), (0, "", ""))
        self.assertFalse(os.path.exists(old))
        self.assertEqual(ran("form", self.path), (0, "", ""))

    def test_form_says_to_remove_a_leftover_where_no_source_makes_the_example(self):
        ran("markdown", self.path)
        stray = os.path.join(self.folder, "notes.md")
        self.write(stray, "n")
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertIn(f"{stray} is neither the template's nor the example's; remove it", err)

    def test_example_leaves_every_file_where_the_source_cannot_be_copied(self):
        self.sourced()
        stray = os.path.join(self.folder, "notes.md")
        self.write(stray, "n")
        os.remove(os.path.join(self.base, "doc", "source.md"))
        self.assertEqual(ran("example", self.path)[0], 1)
        self.assertTrue(os.path.exists(stray))

    def test_example_names_a_best_practice_with_no_source(self):
        code, _, err = ran("example", self.path)
        self.assertEqual(code, 1)
        self.assertIn(f"plan.py: {self.path}: it names no source to copy its example from", err)

    def test_each_command_names_a_json_it_cannot_read(self):
        self.write(self.path, "{")
        for command in ("form", "markdown", "example"):
            with self.subTest(command=command):
                code, _, err = ran(command, self.path)
                self.assertEqual(code, 1)
                self.assertIn(f"plan.py: {self.path}: {self.path} is not JSON", err)
        self.assertFalse(os.path.exists(os.path.join(self.folder, "best-practice.md")))


if __name__ == "__main__":
    unittest.main()
