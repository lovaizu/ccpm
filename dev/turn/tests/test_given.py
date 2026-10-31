"""What each role is given to read: none of the run's own files, the result and turn's folder at the
root, as a role's lane lets it read anything under a folder it is given."""

import os
import unittest

from helpers import RepoTest, prompts


class GivenTest(RepoTest):
    """A run of turn on a layout of files the test lays."""

    def lay(self, *paths):
        """Writes an empty file at each path."""
        for path in paths:
            self.write(path, "")


class TestWithoutRunFiles(GivenTest):
    def setUp(self):
        super().setUp()
        # A repository holding only the files each test lays.
        os.makedirs("place/.git")
        os.chdir("place")

    def test_a_folder_holding_the_result_two_levels_down_is_given_as_its_entries(self):
        # Given: the result two folders down from `.`, with files beside it, one named as the
        # result with more after it, at each level
        # When: `.` is given
        # Then: every entry is given but the folder on the way to the result, which is opened the
        # same way level by level, and in the result's folder every entry but the result, sorted
        self.lay(
            "b.md",
            "a/x.md",
            "a/run/result.json",
            "a/run/result.json.run.json",
            "a/run/result.jsonx",
            "a/run/notes.md",
        )
        self.assertEqual(
            prompts.without_run_files(["."], "a/run/result.json"),
            [
                ".git",
                "a/run/notes.md",
                "a/run/result.json.run.json",
                "a/run/result.jsonx",
                "a/x.md",
                "b.md",
            ],
        )

    def test_a_folder_not_holding_the_result_is_given_as_it_is(self):
        # Given: the result in `.tasks`, and folders beside it, one named as `.tasks` cut short
        # When: each of them is given
        # Then: each is given as it is
        self.lay(".tasks/result.json", ".task/a.md", "docs/a.md")
        self.assertEqual(
            prompts.without_run_files([".task", "docs"], ".tasks/result.json"), [".task", "docs"]
        )

    def test_the_result_s_own_folder_is_given_as_its_entries_but_the_result(self):
        # Given: the result in `.tasks`, with the CCS beside it
        # When: `.tasks` is given
        # Then: every entry of `.tasks` is given but the result
        self.lay(".tasks/ccs.json", ".tasks/result.json")
        self.assertEqual(
            prompts.without_run_files([".tasks"], ".tasks/result.json"), [".tasks/ccs.json"]
        )

    def test_turn_s_folder_at_the_root_is_left_out_of_the_root_s_entries(self):
        # Given: the result in `.tasks`, and turn's folder at the root holding this run's folder
        # and another's
        self.lay(
            ".tasks/result.json",
            ".turn/20261025-.tasks%2Fresult.json/call.json",
            ".turn/20261024-other.json/generator.json",
            "README.md",
        )
        # When: `.` is given
        # Then: every entry of `.` is given but turn's folder, `.tasks` opened to leave out the
        # result
        self.assertEqual(
            prompts.without_run_files(["."], ".tasks/result.json"), [".git", "README.md"]
        )

    def test_a_path_in_turn_s_folder_or_the_result_is_left_out(self):
        # Given: the result in `.tasks`, turn's folder at the root, and a folder named as turn's
        # elsewhere
        self.lay(
            ".tasks/result.json",
            ".turn/20261025-.tasks%2Fresult.json/call.json",
            ".turn/20261025-.tasks%2Fresult.json/generator.json",
            "docs/.turn/a.md",
        )
        paths = [
            ".tasks/result.json",
            ".turn",
            ".turn/20261025-.tasks%2Fresult.json",
            ".turn/20261025-.tasks%2Fresult.json/call.json",
            ".turn/20261025-.tasks%2Fresult.json/generator.json",
            "docs/.turn/a.md",
        ]
        # When: the result, turn's folder, a run's folder, its call and a role's reply in it, and
        # the file in the folder elsewhere are given
        # Then: the file elsewhere alone is given
        self.assertEqual(
            prompts.without_run_files(paths, ".tasks/result.json"), ["docs/.turn/a.md"]
        )

    def test_a_result_at_the_top_is_left_out_of_the_top_s_entries(self):
        # Given: the result at the top of `.`
        # When: `.` is given
        # Then: every entry of `.` is given but the result
        self.lay("result.json", "README.md", "docs/a.md")
        self.assertEqual(
            prompts.without_run_files(["."], "result.json"), [".git", "README.md", "docs"]
        )

    def test_a_path_met_again_is_given_once_where_it_is_first_met(self):
        # Given: the result in `.tasks`, and a file given by itself and again as an entry of `.`
        self.lay(".tasks/result.json", "a.md", "b.md")
        # When: the file and `.` are given
        # Then: the file is given once, where it is first met
        self.assertEqual(
            prompts.without_run_files(["b.md", "."], ".tasks/result.json"), ["b.md", ".git", "a.md"]
        )

    def test_a_path_kept_apart_is_left_out_and_the_folders_on_its_way_opened(self):
        # Given: the result in `.tasks`, the CCS at the top of `.`, and a file in a folder
        self.lay(".tasks/result.json", "ccs.json", "README.md", "docs/a.md", "docs/ccs.md")
        # When: `.` and the CCS itself are given, the CCS kept apart
        # Then: the CCS is left out, `.` given as its other entries, and a folder not on the way
        # to the result or the CCS given as it is
        self.assertEqual(
            prompts.without_run_files([".", "ccs.json"], ".tasks/result.json", apart=("ccs.json",)),
            [".git", "README.md", "docs"],
        )

    def test_a_path_kept_apart_inside_a_folder_leaves_its_folder_s_other_entries(self):
        # Given: the result at the top, and the CCS in `notes` beside another file
        self.lay("result.json", "notes/ccs.json", "notes/a.md")
        # When: `notes` is given, the CCS kept apart
        # Then: `notes` is given as its other entries
        self.assertEqual(
            prompts.without_run_files(["notes"], "result.json", apart=("notes/ccs.json",)),
            ["notes/a.md"],
        )

    def test_the_paths_are_given_in_their_order(self):
        # Given: the result in `.tasks`, and paths that are none of the run's files
        # When: they are given
        # Then: they are given in the order they came, each as it is
        self.lay(".tasks/result.json", "z.md", "a.md")
        self.assertEqual(
            prompts.without_run_files(["z.md", "a.md"], ".tasks/result.json"), ["z.md", "a.md"]
        )


if __name__ == "__main__":
    unittest.main()
