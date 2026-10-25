"""What the flow gives the orchestrator and each role to read: whole paths in the folder the call
was made from, wherever the session's working folder moves, and none of the run's own files, kept
beside the result, as a role's lane lets it read anything under a folder it is given."""

import json
import os
import unittest

from helpers import CALL, CAN, CCS, GOOD, RESULT, RepoTest, prompts


class GivenTest(RepoTest):
    """A run of turn on a layout of files the test lays."""

    def lay(self, *paths):
        """Writes an empty file at each path."""
        for path in paths:
            self.write(path, "")


class TestWithoutRunFiles(GivenTest):
    def setUp(self):
        super().setUp()
        # A folder holding only the files each test lays.
        os.makedirs("place")
        os.chdir("place")

    def test_a_folder_holding_the_result_two_levels_down_is_given_as_its_entries(self):
        # Given: the result two folders down from `.`, with the run's files beside it and files
        # whose names only begin like the result's, at each level
        # When: `.` is given
        # Then: every entry is given but the folder on the way to the result, which is opened the
        # same way level by level, and in the result's folder every entry but the result and the
        # files whose names begin with the result's name and a dot, sorted
        self.lay(
            "b.md",
            "a/x.md",
            "a/run/result.json",
            "a/run/result.json.run.json",
            "a/run/result.json.generator.json",
            "a/run/result.jsonx",
            "a/run/notes.md",
            "a/run/result.json.records/1.txt",
        )
        self.assertEqual(
            prompts.without_run_files(["."], "a/run/result.json"),
            ["a/run/notes.md", "a/run/result.jsonx", "a/x.md", "b.md"],
        )

    def test_a_folder_not_holding_the_result_is_given_as_it_is(self):
        # Given: the result in `.tasks`, and folders beside it, one named as `.tasks` cut short
        # When: each of them is given
        # Then: each is given as it is
        self.lay(".tasks/result.json", ".tasks/result.json.run.json", ".task/a.md", "docs/a.md")
        self.assertEqual(
            prompts.without_run_files([".task", "docs"], ".tasks/result.json"), [".task", "docs"]
        )

    def test_the_result_s_own_folder_is_given_as_its_entries_but_the_run_s_files(self):
        # Given: the result in `.tasks`, with the run's files and the CCS beside it
        # When: `.tasks` is given
        # Then: every entry of `.tasks` is given but the result and the run's files
        self.lay(".tasks/ccs.json", ".tasks/result.json", ".tasks/result.json.run.json")
        self.assertEqual(
            prompts.without_run_files([".tasks"], ".tasks/result.json"), [".tasks/ccs.json"]
        )

    def test_a_path_that_is_one_of_the_run_s_files_is_left_out(self):
        # Given: the result in `.tasks`, with the run's files beside it, and a file elsewhere named
        # as one of them
        # When: the result, each run's file, a file inside one, and the file elsewhere are given
        # Then: the result, the run's files and what is in them are left out, the file elsewhere
        # given
        self.lay(
            ".tasks/result.json",
            ".tasks/result.json.run.json",
            ".tasks/result.json.first-user.json",
            ".tasks/result.json.records/1.txt",
            "docs/result.json.run.json",
        )
        paths = [
            ".tasks/result.json",
            ".tasks/result.json.run.json",
            ".tasks/result.json.first-user.json",
            ".tasks/result.json.records",
            ".tasks/result.json.records/1.txt",
            "docs/result.json.run.json",
        ]
        self.assertEqual(
            prompts.without_run_files(paths, ".tasks/result.json"), ["docs/result.json.run.json"]
        )

    def test_a_result_at_the_top_leaves_out_its_files_from_the_top_s_entries(self):
        # Given: the result at the top of `.`, with the run's files beside it
        # When: `.` is given
        # Then: every entry of `.` is given but the result and the run's files
        self.lay("result.json", "result.json.run.json", "README.md", "docs/a.md")
        self.assertEqual(prompts.without_run_files(["."], "result.json"), ["README.md", "docs"])

    def test_a_path_met_again_is_given_once_where_it_is_first_met(self):
        # Given: the result in `.tasks`, and a file given by itself and again as an entry of `.`
        self.lay(".tasks/result.json", "a.md", "b.md")
        # When: the file and `.` are given
        # Then: the file is given once, where it is first met
        self.assertEqual(
            prompts.without_run_files(["b.md", "."], ".tasks/result.json"), ["b.md", "a.md"]
        )

    def test_a_path_kept_apart_is_left_out_and_the_folders_on_its_way_opened(self):
        # Given: the result in `.tasks`, the CCS at the top of `.`, and a file in a folder
        self.lay(".tasks/result.json", "ccs.json", "README.md", "docs/a.md", "docs/ccs.md")
        # When: `.` and the CCS itself are given, the CCS kept apart
        # Then: the CCS is left out, `.` given as its other entries, and a folder not on the way
        # to the result or the CCS given as it is
        self.assertEqual(
            prompts.without_run_files([".", "ccs.json"], ".tasks/result.json", apart=("ccs.json",)),
            ["README.md", "docs"],
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


class TestStartGiven(RepoTest):
    """What the start gives the orchestrator to read for its check."""

    def test_the_start_gives_what_the_orchestrator_reads_before_any_work_is_made(self):
        # Given: a CCS naming the work, the checklist, the decisions and a page the receiver has
        # When: the run is started, and started again on the same call
        # Then: each time it gives the CCS and every file it names but the work, which the
        # orchestrator reads whole for its check
        given = [
            self.here(".tasks/readme.json"),
            self.here("checklists/readme.md"),
            self.here("notes/readme.decisions.md"),
            self.here("docs/start.md"),
        ]
        for _ in range(2):
            code, out = self.turn("start", json.dumps(CALL))
            self.assertEqual((code, json.loads(out)["given"]), (0, given))


class TestRolesGiven(GivenTest):
    """A run whose receiver has the whole repository, `.`, as a maintainer's repository is to its
    maintainer."""

    def setUp(self):
        super().setUp()
        artifacts = [a for a in CCS["retrieved_artifacts"] if "page" not in a] + [{"page": "."}]
        self.write_json(CALL["ccs"], dict(CCS, retrieved_artifacts=artifacts))
        # Every entry of `.`, `.tasks` opened, as the run's files are written by the start.
        self.entries = [
            self.here(p) for p in (".tasks/readme.json", "README.md", "checklists", "docs", "notes")
        ]

    def test_start_prints_a_given_without_the_run_s_files(self):
        # Given: a call whose receiver has `.`
        # When: the run is started
        # Then: the start's `given` holds the CCS and each file it names but the work, `.` as its
        # entries without the run's state, each path once
        code, out = self.turn("start", json.dumps(CALL))
        self.assertEqual(code, 0, out)
        given = [
            self.here(".tasks/readme.json"),
            self.here("checklists/readme.md"),
            self.here("notes/readme.decisions.md"),
        ] + self.entries[1:]
        self.assertEqual(json.loads(out)["given"], given)

    def test_the_generator_is_given_no_run_s_file(self):
        # Given: a call whose receiver has `.`, checked to give every item its Good
        # When: the generator is to be started
        # Then: its `given` holds the CCS, the work and each file the CCS names, `.` as its entries
        # without the run's files, each path once
        self.started()
        self.assertEqual(
            self.prompt()["given"],
            [
                self.here(".tasks/readme.json"),
                self.here("README.md"),
                self.here("checklists/readme.md"),
                self.here("notes/readme.decisions.md"),
            ]
            + self.entries[2:],
        )

    def test_the_first_user_is_given_neither_the_ccs_nor_the_generator_s_reply_nor_the_state(self):
        # Given: a call whose receiver has `.`, the CCS beside the result, and a generator that
        # replied with every item's Good, its reply beside the result
        # When: the first user is to be started
        # Then: its `given` holds the work, `.` as its entries without the CCS and the run's files,
        # and the checklists, each path once
        self.started()
        move = self.due(self.made())
        self.assertTrue(os.path.exists(RESULT + ".generator.json"))
        self.assertEqual(
            json.loads(move["input"]["prompt"])["given"],
            [self.here("README.md")] + self.entries[2:] + [self.here("checklists/readme.md")],
        )


class TestFolderMoved(RepoTest):
    """The session's working folder moves when the calling AI runs `cd`, and every agent's commands
    and hooks then run from there; the run's paths still mean where the call was made."""

    def test_each_role_is_given_whole_paths_of_where_the_call_was_made(self):
        # Given: a run started, and the session's working folder moved to notes/
        # When: the orchestrator goes on with the result the start gave
        # Then: the generator's prompt names each file as a whole path in the folder the call was
        # made from, as its hooks and its commands run from notes/
        self.turn("start", json.dumps(CALL))
        os.chdir("notes")
        self.result = self.here(RESULT)
        move = json.loads(self.due(self.next({"items": CAN, "questions": []}))["input"]["prompt"])
        self.assertEqual(move["work"], [self.here("README.md")])
        self.assertEqual(move["checklists"], [self.here("checklists/readme.md")])
        self.assertEqual(move["reply"], self.here(RESULT + ".generator.json"))
        self.assertIn(self.here(CALL["ccs"]), move["given"])

    def test_a_round_goes_on_from_another_folder_with_lines_named_by_whole_paths(self):
        # Given: a run started, and the session's working folder moved to notes/
        # When: the generator replies at the whole path it was given, with lines named by whole
        # paths, and the first user is due
        # Then: the reply is taken, and the first user is given the work's parts as the run names
        # them and whole paths for its files
        self.started()
        os.chdir("notes")
        self.result = self.here(RESULT)
        lines = [self.here("README.md:1-3")]
        out = self.made(dict(GOOD, lines=lines), dict(GOOD, item="B-1", lines=lines))
        prompt = json.loads(self.due(out)["input"]["prompt"])
        self.assertEqual(prompt["parts"], [self.here("README.md:1-3")])
        self.assertEqual(prompt["given"][0], self.here("README.md"))
        code, out = self.turn("parts", self.result)
        self.assertEqual((code, json.loads(out)), (0, {"parts": [self.here("README.md:1-3")]}))


if __name__ == "__main__":
    unittest.main()
