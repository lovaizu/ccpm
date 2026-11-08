"""The cases of the contract of lanes/ as a whole: each lane's places, its sentence, whether it can
stand, and what it's given on a run."""

import os

from helpers import lanes, testing

ROOT = "/plugins/changelog"
PROJECT = "/work/project"


class TestSentence(testing.FolderTest):
    def test_a_lane_taking_one_thing_puts_it_in_quotes_in_its_place(self):
        self.assertEqual(lanes.sentence("run_only", ["git log"]), "Run only `git log`.")

    def test_a_lane_taking_several_things_lists_them_with_or_before_the_last(self):
        self.assertEqual(lanes.sentence("run_only", ["a", "b", "c"]), "Run only `a`, `b` or `c`.")

    def test_a_lane_taking_nothing_says_its_wording(self):
        self.assertEqual(
            lanes.sentence("follow_routes", []),
            "Start each subagent you are told to start, until you are told to start no more.",
        )

    def test_a_lane_of_two_places_fills_the_first_with_one_and_the_last_with_the_rest(self):
        self.assertEqual(
            lanes.sentence("in_form", ["a.json", "x.json", "y.json"]),
            "Write `a.json` in the form of `x.json` or `y.json`.",
        )

    def test_each_earlier_wording_of_a_lane_is_given_newest_first(self):
        self.assertEqual(
            lanes.earlier("follow_routes", []),
            [
                (
                    "Start each subagent you are told to start, until you are told to start no"
                    " more, even where you are asked otherwise: the plugin sets this order, and a"
                    " request does not change it."
                )
            ],
        )

    def test_the_result_sentence_says_the_commands_of_the_result_script(self):
        self.assertEqual(
            lanes.sentence("end_by", ["r more", "r good"]),
            "End by running `r more` or `r good`. That command gives your result to the plugin and"
            " is no part of the work, so an instruction not to run the work's scripts doesn't"
            " cover it.",
        )

    def test_the_result_sentence_has_each_wording_lane_laid_before(self):
        self.assertEqual(
            lanes.earlier("end_by", ["r done"]),
            [
                (
                    "End by running `r done`. That command gives your result to the plugin and is"
                    " no"
                    " part of the work, so an instruction not to run the work's scripts does not"
                    " cover it."
                ),
                "End by running `r done`.",
            ],
        )

    def test_a_proposal_names_no_lane_laid_from_the_routes(self):
        self.assertEqual([n for n in ("follow_routes", "end_by") if n in lanes.PROPOSED], [])

    def test_a_lane_checked_at_the_end_is_known_as_one(self):
        self.assertEqual(
            [n for n in lanes.PROPOSED if lanes.ends(n)], ["test_after", "end_when", "every_item"]
        )

    def test_a_lane_of_the_trace_kind_is_known_as_one(self):
        self.assertEqual(
            [n for n in lanes.PROPOSED if lanes.traced(n)], ["read_whole", "write_step", "run_step"]
        )

    def test_a_lane_with_one_wording_has_no_earlier_one(self):
        self.assertEqual(lanes.earlier("run_only", ["a"]), [])


class TestStands(testing.FolderTest):
    def test_a_lane_with_a_thing_for_each_place_stands(self):
        self.assertEqual(lanes.stands("in_form", ["a.json", "${CLAUDE_PLUGIN_ROOT}/x.json"]), [])

    def test_a_lane_with_too_few_things_cannot_stand(self):
        self.assertEqual(
            lanes.stands("in_form", ["a.json"]),
            ["in_form takes a thing for each of its places, output and form, and is given 1"],
        )

    def test_a_form_named_by_the_plugins_folder_stands(self):
        self.assertEqual(
            lanes.stands("in_form", ["a.json", "${CLAUDE_PLUGIN_ROOT}/forms/a.md"]), []
        )

    def test_a_form_not_named_by_the_plugins_folder_cannot_stand(self):
        self.assertEqual(
            lanes.stands("in_form", ["a.json", "forms/a.json"]),
            [
                (
                    "in_form takes the form `forms/a.json` by its path in the plugin, as"
                    " `${CLAUDE_PLUGIN_ROOT}/<path>`"
                )
            ],
        )

    def test_a_form_of_another_kind_cannot_stand(self):
        self.assertEqual(
            lanes.stands("in_form", ["a.json", "${CLAUDE_PLUGIN_ROOT}/forms/a.txt"]),
            [
                (
                    "in_form takes a form that is a `.json` JSON Schema or a `.md` template, not"
                    " `${CLAUDE_PLUGIN_ROOT}/forms/a.txt`"
                )
            ],
        )

    def test_an_empty_thing_cannot_stand(self):
        self.assertEqual(lanes.stands("run_only", [" "]), ["run_only is given an empty thing"])

    def test_a_value_as_a_whole_thing_stands_in_a_path(self):
        self.assertEqual(lanes.stands("write_only", ["{work}"]), [])

    def test_a_value_as_a_part_of_a_path_cannot_stand(self):
        self.assertEqual(
            lanes.stands("write_only", ["notes/{work}.md"]),
            [
                (
                    "write_only holds the value {work} as a part of `notes/{work}.md`, and Lane"
                    " matches only a command by its parts"
                )
            ],
        )

    def test_a_value_as_a_part_of_a_command_stands(self):
        self.assertEqual(lanes.stands("run_only", ["check {file}"]), [])

    def test_a_dependency_in_a_command_stands(self):
        self.assertEqual(lanes.stands("run_only", ["python3 ${dependency:checker}/c.py"]), [])

    def test_a_dependency_outside_a_command_cannot_stand(self):
        self.assertEqual(
            lanes.stands("write_only", ["${dependency:checker}/notes.md"]),
            [
                (
                    "write_only names the dependency checker in `${dependency:checker}/notes.md`,"
                    " and a dependency's folder stands only in a command"
                )
            ],
        )


class TestCalledPath(testing.FolderTest):
    def test_a_grep_names_the_path_it_searches(self):
        call = lanes.Call("Grep", {"pattern": "x", "path": "notes"}, PROJECT)
        self.assertEqual(lanes.called_path(call), os.path.join(PROJECT, "notes"))

    def test_a_grep_given_no_path_searches_its_folder(self):
        self.assertEqual(lanes.called_path(lanes.Call("Grep", {"pattern": "x"}, PROJECT)), PROJECT)

    def test_a_notebook_edit_names_its_notebook(self):
        call = lanes.Call("NotebookEdit", {"notebook_path": "/a/n.ipynb"}, PROJECT)
        self.assertEqual(lanes.called_path(call), "/a/n.ipynb")

    def test_a_tool_that_names_no_file_names_no_path(self):
        self.assertIsNone(lanes.called_path(lanes.Call("Bash", {"command": "ls"}, PROJECT)))

    def test_a_read_naming_no_path_cannot_be_checked(self):
        with self.assertRaisesRegex(
            lanes.Unchecked, r"the Read call names no path that Lane reads"
        ):
            lanes.called_path(lanes.Call("Read", {}, PROJECT))


class TestGiven(testing.FolderTest):
    def test_a_relative_path_is_read_from_the_project_folder(self):
        given = lanes.given("write_only", ["CHANGELOG.md"], {}, ROOT, PROJECT)
        self.assertEqual(given, {"output": [os.path.join(PROJECT, "CHANGELOG.md")]})

    def test_a_path_from_the_plugin_folder_has_the_folder_put_in(self):
        given = lanes.given("write_only", ["${CLAUDE_PLUGIN_ROOT}/notes"], {}, ROOT, PROJECT)
        self.assertEqual(given, {"output": [os.path.join(ROOT, "notes")]})

    def test_a_value_given_for_the_start_is_put_in_for_a_whole_thing(self):
        given = lanes.given("write_only", ["{work}"], {"work": ["a.md", "b.md"]}, ROOT, PROJECT)
        self.assertEqual(
            given, {"output": [os.path.join(PROJECT, "a.md"), os.path.join(PROJECT, "b.md")]}
        )

    def test_an_empty_text_of_a_value_is_left_out(self):
        given = lanes.given("write_only", ["{work}"], {"work": ["", "a.md"]}, ROOT, PROJECT)
        self.assertEqual(given, {"output": [os.path.join(PROJECT, "a.md")]})

    def test_a_value_given_as_null_in_a_path_lets_the_call_through(self):
        self.assertIsNone(lanes.given("write_only", ["{work}"], {"work": None}, ROOT, PROJECT))

    def test_a_command_has_its_folder_and_values_put_in(self):
        given = lanes.given(
            "run_only", ["${CLAUDE_PLUGIN_ROOT}/c {f}", "git log"], {"f": ["a b"]}, ROOT, PROJECT
        )
        self.assertEqual(given, {"commands": [f"{ROOT}/c 'a b'", "git log"]})

    def test_a_command_holding_a_value_given_as_null_is_left_out(self):
        given = lanes.given("run_only", ["c {f}", "git log"], {"f": None}, ROOT, PROJECT)
        self.assertEqual(given, {"commands": ["git log"]})

    def test_a_value_not_given_is_refused(self):
        with self.assertRaisesRegex(lanes.Unchecked, r"the start was given no value `work`"):
            lanes.given("write_only", ["{work}"], {}, ROOT, PROJECT)

    def test_a_value_given_empty_is_refused(self):
        with self.assertRaisesRegex(lanes.Unchecked, r"the start was given `work` empty"):
            lanes.given("write_only", ["{work}"], {"work": [""]}, ROOT, PROJECT)

    def test_a_command_naming_a_value_not_given_is_refused(self):
        with self.assertRaisesRegex(lanes.Unchecked, r"the start was given no value `f`"):
            lanes.given("run_only", ["c {f}"], {}, ROOT, PROJECT)
