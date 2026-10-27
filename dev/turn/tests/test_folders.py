"""Where a run keeps its files, as dev/architecture.md's Where a plugin writes its files places
them: its state and each role's reply in `.turn/<yyyymmdd>-<name>/` at the root of the repository,
the name made from the result's path, so a call again finds them on any day and runs at once do not
meet; and the result alone where the call puts it."""

import json
import os
import time
import unittest
from unittest import mock

from helpers import (
    CALL,
    CCS,
    CHECKLIST,
    FOUND,
    FOUND_B1,
    RESULT,
    RUN,
    TODAY,
    RepoTest,
    state,
)

# The day before TODAY, a run begun on it gone on with on TODAY, and the day before that.
YESTERDAY = "20261024"
EARLIER = "20261023"


class TestRunFolder(RepoTest):
    def start(self, result=RESULT):
        """Starts a run of the call with its result at the path; fails the test where it stops."""
        code, out = self.turn("start", json.dumps(dict(CALL, result=result)))
        self.assertEqual(code, 0, out)

    def runs(self, root="."):
        """The folders of turn's folder at the root, sorted."""
        return sorted(os.listdir(os.path.join(root, ".turn")))

    def test_a_result_in_a_subfolder_keeps_its_run_in_turn_s_folder_at_the_root(self):
        # Given: a call whose result goes in `.tasks`
        # When: the run is started
        # Then: its state is in `.turn/<today>-<the result's path, each / as %2F>/` at the root,
        # and the result's folder holds the CCS alone
        self.start()
        self.assertEqual(self.read_json(f"{RUN}/run.json")["call"]["result"], RESULT)
        self.assertEqual(os.listdir(".tasks"), ["readme.json"])

    def test_a_result_at_the_root_names_its_run_by_its_name(self):
        # Given: a call whose result goes at the root
        # When: the run is started
        # Then: its state is in `.turn/<today>-result.json/`
        self.start("result.json")
        self.assertEqual(self.runs(), [f"{TODAY}-result.json"])
        self.assertTrue(os.path.isfile(f".turn/{TODAY}-result.json/run.json"))

    def test_a_result_at_the_root_is_written_there_alone_once_the_run_returns(self):
        # Given: a run whose result goes at the root, every item given its Good
        self.started(dict(CALL, result="result.json"))
        # When: the run returns
        self.returned(self.first_read(FOUND, FOUND_B1))
        # Then: the result is at the root, and its run's folder is gone
        self.assertEqual(self.read_json("result.json")["work"], ["README.md"])
        self.assertEqual(self.runs(), [])

    def test_a_result_given_whole_names_its_run_by_its_path_from_the_root(self):
        # Given: a call whose result is given as a whole path
        # When: the run is started
        # Then: its run's folder is named by the result's path from the root, as given relative
        self.start(self.here(RESULT))
        self.assertEqual(self.runs(), [os.path.basename(RUN)])

    def test_a_call_from_a_subfolder_keeps_its_run_at_the_root(self):
        # Given: a task in `pkg`, a folder of the repository, and the call made from there
        for path, text in (
            ("checklists/readme.md", CHECKLIST),
            ("notes/readme.decisions.md", "# Decisions\n"),
            ("docs/start.md", "# Start\n"),
            ("README.md", "# csvtidy\n"),
        ):
            self.write(os.path.join("pkg", path), text)
        self.write_json(os.path.join("pkg", CALL["ccs"]), CCS)
        os.chdir("pkg")
        # When: the run is started
        self.start()
        # Then: its state is in turn's folder at the root, named by the result's path from the
        # root, and none is made in `pkg`
        self.assertEqual(self.runs(self.base), [f"{TODAY}-pkg%2F.tasks%2Freadme-result.json"])
        self.assertFalse(os.path.exists(".turn"))

    def test_a_result_in_no_repository_keeps_its_run_in_the_result_s_folder(self):
        # Given: a call made where no folder above the result marks a repository's root
        # When: the run is started
        # Then: turn's folder is made in the result's folder, the run named by the result's name
        with mock.patch.object(state, "REPOSITORY", ".no-repository"):
            self.start()
        self.assertEqual(self.runs(".tasks"), [f"{TODAY}-readme-result.json"])
        self.assertFalse(os.path.exists(".turn"))

    def test_a_run_called_again_the_same_day_is_found_in_its_folder(self):
        # Given: a run started and told its generator's start
        self.start()
        self.next()
        # When: the same call is made again the same day
        self.start()
        # Then: the run is gone on with from its folder, the one there is, the start to be told
        # again
        self.assertEqual(self.runs(), [os.path.basename(RUN)])
        self.assertNotIn("told", self.state()["next"])

    def test_a_run_begun_on_an_earlier_day_is_gone_on_with_from_its_folder(self):
        # Given: a run started the day before
        with mock.patch.object(time, "strftime", return_value=YESTERDAY):
            self.start()
        # When: it is gone on with today, and the generator becomes due
        move = self.due(self.next())
        # Then: the run is read from the folder of the day it began, its generator replying there,
        # and no folder of today is made
        prompt = json.loads(move["input"]["prompt"])
        folder = f".turn/{YESTERDAY}-.tasks%2Freadme-result.json"
        self.assertEqual(prompt["reply"], self.here(f"{folder}/generator.json"))
        self.assertEqual(self.runs(), [os.path.basename(folder)])

    def test_a_run_whose_result_names_glob_s_marks_is_found_on_a_later_day(self):
        # Given: a run started the day before on a result whose name holds `[` and `]`, which a
        # pattern of file names reads as a set of letters
        with mock.patch.object(time, "strftime", return_value=YESTERDAY):
            self.start("[a].json")
        # When: the same call is made again today
        self.start("[a].json")
        # Then: the run is found in the folder of the day it began, and no folder of today is made
        self.assertEqual(self.runs(), [f"{YESTERDAY}-[a].json"])

    def test_a_result_named_as_the_end_of_another_s_has_a_run_of_its_own(self):
        # Given: a run started the day before on `x-r.json`, whose folder's name ends as one of
        # `r.json` would
        with mock.patch.object(time, "strftime", return_value=YESTERDAY):
            self.start("x-r.json")
        # When: a run on `r.json` is started today
        self.start("r.json")
        # Then: it is kept in a folder of its own, of today
        self.assertEqual(self.runs(), [f"{YESTERDAY}-x-r.json", f"{TODAY}-r.json"])
        self.assertEqual(
            self.read_json(f".turn/{TODAY}-r.json/run.json")["call"]["result"], "r.json"
        )

    def test_of_two_folders_kept_for_a_result_the_earliest_day_s_is_gone_on_with(self):
        # Given: folders of the call's result kept from two days, the day before and the day
        # before that
        for day in (EARLIER, YESTERDAY):
            os.makedirs(f".turn/{day}-.tasks%2Freadme-result.json")
        # When: the run is started today
        self.start()
        # Then: it is kept in the folder of the earliest day, and no folder of today is made
        self.assertTrue(os.path.isfile(f".turn/{EARLIER}-.tasks%2Freadme-result.json/run.json"))
        self.assertEqual(len(self.runs()), 2)

    def test_two_runs_at_once_with_other_results_keep_folders_of_their_own(self):
        # Given: a run started on the call's result
        self.start()
        # When: a run on another result is started beside it
        self.start(".tasks/other-result.json")
        # Then: each is kept in a folder of its own, holding its own call
        other = f".turn/{TODAY}-.tasks%2Fother-result.json"
        self.assertEqual(self.runs(), sorted([os.path.basename(RUN), os.path.basename(other)]))
        results = [self.read_json(f"{f}/run.json")["call"]["result"] for f in (RUN, other)]
        self.assertEqual(results, [RESULT, ".tasks/other-result.json"])


if __name__ == "__main__":
    unittest.main()
