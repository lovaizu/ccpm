"""scripts/plan.py, what the planner runs on a run's folder: start, hand, ready and next move the
work the run is at, each printing what the planner gives and ends with, 0, or why it cannot, 1;
check says whether the Run holds and where the run is, 0, each fault, 1, or why it could not
check, 2. And what a person or CI runs on a best practice: form, its faults and its Markdown left
behind; markdown, written beside it; and sources, each ground whose page is not the one meant."""

import contextlib
import copy
import io
import json
import os
import runpy
import unittest
import urllib.request
from unittest import mock

import helpers
from helpers import met, phases, plan, practices, runs, short

from unit.core.domain.test_practices import DATA, response

RUN = helpers.RUN
DESIGN = os.path.join(RUN, runs.DESIGN)
USAGE = (
    "usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan.py start|hand|ready|next|check <run>\n"
    "       python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan.py form|markdown|sources"
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
        made = os.path.join(runs.REPOSITORY, "man-page.json")
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
    """form, markdown and sources, on a best practice of the kind `kind`."""

    def setUp(self) -> None:
        super().setUp()
        self.path = os.path.join(self.base, "kind.json")
        self.write_json(self.path, DATA)

    def test_form_fails_until_markdown_writes_it(self):
        self.assertEqual(ran("form", self.path)[0], 1)
        self.assertEqual(ran("markdown", self.path), (0, "", ""))
        self.assertEqual(
            self.read(os.path.join(self.base, "kind.md")), practices.markdown("kind", DATA)
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
        for question in data["benefits"]:
            question["about"] = "the whole"
        self.write_json(self.path, data)
        self.write(os.path.join(self.base, "kind-template.md"), "# <P>\n\n## Use\n")
        ran("markdown", self.path)
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertIn(f"plan.py: {self.path}: section Use has no question about it", err)
        self.assertIn(
            "[kind-template.md](kind-template.md)", self.read(os.path.join(self.base, "kind.md"))
        )

    def test_form_fails_on_a_json_out_of_its_schema(self):
        self.write_json(self.path, {"goal": "g"})
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertIn("is out of its form", err)

    def test_form_fails_on_a_markdown_changed_by_hand(self):
        made = practices.markdown("kind", DATA)
        for changed in (made + "More.\n", made[:-1]):
            with self.subTest(changed=changed[-6:]):
                self.write(os.path.join(self.base, "kind.md"), changed)
                code, _, err = ran("form", self.path)
                self.assertEqual(code, 1)
                self.assertIn("kind.md is not as its JSON makes it; run plan.py markdown", err)

    def test_each_command_names_a_json_it_cannot_read(self):
        self.write(self.path, "{")
        for command in ("form", "markdown", "sources"):
            with self.subTest(command=command):
                code, _, err = ran(command, self.path)
                self.assertEqual(code, 1)
                self.assertIn(f"plan.py: {self.path}: {self.path} is not JSON", err)
        self.assertFalse(os.path.exists(os.path.join(self.base, "kind.md")))

    def test_sources_fails_on_a_ground_whose_page_is_not_the_one_meant(self):
        practices.fetch.cache_clear()
        self.addCleanup(practices.fetch.cache_clear)
        page = response("text/html", b"<title>T</title> y")
        with mock.patch.object(urllib.request, "urlopen", return_value=page):
            self.assertEqual(ran("sources", self.path), (0, "", ""))
        practices.fetch.cache_clear()
        with mock.patch.object(urllib.request, "urlopen", return_value=response("text/html", b"T")):
            code, _, err = ran("sources", self.path)
        self.assertEqual(code, 1)
        self.assertIn("does not hold its quote", err)


if __name__ == "__main__":
    unittest.main()
