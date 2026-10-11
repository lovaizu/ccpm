"""Tests for turn's CCS check, run as turn runs it: the script, from inside the repository."""

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

PLUGIN_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "turn")
ENTRY = os.path.join(PLUGIN_ROOT, "scripts", "check.py")


def ccs(viewpoint):
    return {
        "focal_entities": [{"deliverable": "SETUP.md"}, {"receiver": "A new team member"}],
        "goal_orientation": [{"acceptance": "Starts the app without asking anyone"},
                             {"use": "Run the steps from the top"}],
        "retrieved_artifacts": [{"viewpoint": viewpoint}, {"source": "package.json"}],
        "constraints": [{"language": "English"}],
        "episodic_trace": [],
        "semantic_gist": [],
        "relational_map": [],
        "predictive_cue": [],
        "uncertainty_signal": [],
    }


def returned(given):
    out = copy.deepcopy(given)
    out["predictive_cue"] = [{"next": "ask the user"}]
    out["uncertainty_signal"] = [{"more": "Starts the app without asking anyone: step 3 needs var/"},
                                 {"gap": "Who gives the API token?"}]
    out["relational_map"] = [{"learning": "The steps were written where var/ already existed"}]
    out["episodic_trace"] = [{"generator-1": "wrote SETUP.md"}, {"first-user-12": "ran npm start"},
                             {"git": "no commit"}, {"evidence": ".setup/task-2.evidence.json"}]
    return out


class CheckTest(unittest.TestCase):

    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp())
        self.repo = os.path.join(self.root, "repo")
        os.makedirs(self.repo)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        self.viewpoint = os.path.join(self.root, "plugin", "viewpoints", "setup.md")
        self.write(self.viewpoint, "- Every step was typed.\n")
        self.write(os.path.join(self.repo, "package.json"), "{}\n")
        self.given = ccs(self.viewpoint)

    def tearDown(self):
        shutil.rmtree(self.root)

    def write(self, path, text):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)

    def save(self, name, data):
        self.write(os.path.join(self.repo, ".setup", name),
                   data if isinstance(data, str) else json.dumps(data))

    def run_check(self, mode, cwd=None):
        return subprocess.run(
            [sys.executable, ENTRY, mode, ".setup/task-1.json", ".setup/task-2.json"],
            cwd=cwd or self.repo, capture_output=True, text=True)

    def check_in(self, data):
        self.save("task-1.json", data)
        return self.run_check("in")

    def check_out(self, data):
        self.save("task-1.json", self.given)
        self.save("task-2.json", data)
        return self.run_check("out")

    def assertProblems(self, result, *fragments):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        lines = result.stdout.strip().splitlines()
        self.assertEqual(len(lines), len(fragments), result.stdout)
        for line, fragment in zip(lines, fragments):
            self.assertIn(fragment, line)

    def test_a_ccs_written_by_the_plugin_is_received_with_no_output(self):
        # Given: a CCS in good form, as the calling plugin writes it
        data = self.given
        # When: it is checked as received
        result = self.check_in(data)
        # Then: it passes and prints nothing
        self.assertEqual((result.returncode, result.stdout), (0, ""), result.stderr)

    def test_a_ccs_that_keeps_what_was_received_is_returned_with_no_output(self):
        # Given: a CCS to return that keeps what was received and adds next, a More, a gap, a learning and the records
        data = returned(self.given)
        # When: it is checked as returned
        result = self.check_out(data)
        # Then: it passes and prints nothing
        self.assertEqual((result.returncode, result.stdout), (0, ""), result.stderr)

    def test_a_call_without_mode_and_two_files_shows_how_to_call_it(self):
        # Given: a call that gives the CCS received but no place to return to
        command = [sys.executable, ENTRY, "in", ".setup/task-1.json"]
        # When: it is made
        result = subprocess.run(command, cwd=self.repo, capture_output=True, text=True)
        # Then: it fails and shows how to call it
        self.assertEqual(result.returncode, 2)
        self.assertIn("check.py in <in> <out>", result.stdout)

    def test_a_check_outside_a_git_repository_stops(self):
        # Given: a folder that is not in a git repository
        outside = os.path.join(self.root, "plugin")
        # When: a CCS is checked from there
        result = self.run_check("in", cwd=outside)
        # Then: it fails with that one problem
        self.assertProblems(result, "not inside a git repository")

    def test_a_ccs_that_is_not_json_stops_the_check(self):
        # Given: a CCS that is not JSON
        data = "{not json"
        # When: it is checked as received
        result = self.check_in(data)
        # Then: it fails with that one problem
        self.assertProblems(result, "cannot be read as JSON")

    def test_a_ccs_that_is_not_an_object_is_reported(self):
        # Given: a CCS that is a list, not an object
        data = []
        # When: it is checked as received
        result = self.check_in(data)
        # Then: it fails with that one problem
        self.assertProblems(result, "not a JSON object")

    def test_a_missing_part_and_a_part_not_of_the_nine_are_reported(self):
        # Given: a CCS missing one of its nine parts and holding a part not among them
        data = self.given
        del data["relational_map"]
        data["notes"] = []
        # When: it is checked as received
        result = self.check_in(data)
        # Then: it fails and names both
        self.assertProblems(result, "part relational_map is missing", "part notes is not one of the nine")

    def test_entries_out_of_form_are_reported(self):
        # Given: a CCS with a part that is not a list, entries of more or fewer than one kind, a value that is not text, and kinds not in the tables
        data = self.given
        data["semantic_gist"] = "a summary"
        data["relational_map"] = [{"learning": "a", "note": "b"}, "c"]
        data["constraints"] = [{"language": 1}, {"tone": "polite"}]
        data["episodic_trace"] = [{"reviewer-1": "read it"}, {"generator-0": "wrote"}]
        # When: it is checked as received
        result = self.check_in(data)
        # Then: it fails with one line for each, in order
        self.assertProblems(
            result,
            "constraints: the value of language is not a string",
            "constraints: kind tone is not in the tables",
            "episodic_trace: kind reviewer-1 is not in the tables",
            "episodic_trace: kind generator-0 is not in the tables",
            "relational_map: {\"learning\": \"a\", \"note\": \"b\"} is not one",
            "relational_map: \"c\" is not one",
            "semantic_gist is not a list")

    def test_a_ccs_without_the_four_required_kinds_is_reported(self):
        # Given: a CCS with no deliverable, receiver, acceptance or viewpoint
        data = self.given
        data["focal_entities"] = []
        data["goal_orientation"] = [{"use": "Run the steps"}]
        data["retrieved_artifacts"] = []
        # When: it is checked as received
        result = self.check_in(data)
        # Then: it fails and names each of the four
        self.assertProblems(result, "focal_entities has no deliverable", "focal_entities has no receiver",
                            "goal_orientation has no acceptance", "retrieved_artifacts has no viewpoint")

    def test_places_that_do_not_exist_are_reported(self):
        # Given: a CCS whose viewpoint and source do not exist
        data = self.given
        data["retrieved_artifacts"] = [{"viewpoint": "/gone/viewpoints/setup.md"},
                                       {"source": "docs/missing.md"}]
        # When: it is checked as received
        result = self.check_in(data)
        # Then: it fails and names both
        self.assertProblems(result, "viewpoint /gone/viewpoints/setup.md does not exist",
                            "source docs/missing.md does not exist")

    def test_a_deliverable_outside_the_repository_is_reported(self):
        # Given: a CCS with one deliverable above the repository and one at a path from the top of the disk
        data = self.given
        data["focal_entities"] = [{"deliverable": "../SETUP.md"}, {"deliverable": "/tmp/SETUP.md"},
                                  {"receiver": "A new team member"}]
        # When: it is checked as received
        result = self.check_in(data)
        # Then: it fails and names both as not inside the repository
        self.assertProblems(result, "deliverable ../SETUP.md is not a path inside",
                            "deliverable /tmp/SETUP.md is not a path inside")

    def test_a_deliverable_that_is_or_holds_a_viewpoint_or_a_source_is_reported(self):
        # Given: a CCS whose deliverable is its source, and one whose deliverable is a folder holding its source
        self.write(os.path.join(self.repo, "docs", "app.md"), "# App\n")
        cases = [("package.json", "package.json"), ("docs", "docs/app.md")]
        for deliverable, source in cases:
            with self.subTest(deliverable=deliverable):
                data = copy.deepcopy(self.given)
                data["focal_entities"][0] = {"deliverable": deliverable}
                data["retrieved_artifacts"][1] = {"source": source}
                # When: it is checked as received
                result = self.check_in(data)
                # Then: it fails and says the deliverable would change the measure
                self.assertProblems(result, f"deliverable {deliverable} is or holds source {source}")

    def test_a_file_to_return_to_that_already_exists_is_reported(self):
        # Given: a file already where the CCS is to be returned
        self.save("task-2.json", "{}")
        # When: a CCS in good form is checked as received
        result = self.check_in(self.given)
        # Then: it fails and says that file already exists
        self.assertProblems(result, ".setup/task-2.json already exists")

    def test_a_returned_ccs_that_cannot_be_read_stops_the_check(self):
        # Given: a returned CCS that is empty
        data = ""
        # When: it is checked as returned
        result = self.check_out(data)
        # Then: it fails with that one problem
        self.assertProblems(result, "task-2.json: cannot be read as JSON")

    def test_a_returned_ccs_out_of_form_is_reported(self):
        # Given: a returned CCS with a kind not in the tables
        data = returned(self.given)
        data["semantic_gist"] = [{"summary": "it went well"}]
        # When: it is checked as returned
        result = self.check_out(data)
        # Then: it fails and names that kind
        self.assertProblems(result, "semantic_gist: kind summary is not in the tables")

    def test_a_returned_ccs_with_entries_that_turn_does_not_write_is_reported(self):
        # Given: a returned CCS holding an entry in semantic_gist and a link in relational_map
        data = returned(self.given)
        data["semantic_gist"] = [{"difference": "var/ missing → fixed"}]
        data["relational_map"] = [{"link": "SETUP.md ← package.json"}]
        # When: it is checked as returned
        result = self.check_out(data)
        # Then: it fails and names both kinds
        self.assertProblems(result, "relational_map: kind link is not in the tables",
                            "semantic_gist: kind difference is not in the tables")

    def test_a_returned_ccs_that_changed_what_the_plugin_wrote_is_reported(self):
        # Given: a returned CCS with its acceptance changed and a rule put before the received constraints
        data = returned(self.given)
        data["goal_orientation"][0] = {"acceptance": "Starts the app, asking at most once"}
        data["constraints"] = [{"rule": "Type each step"}, {"language": "English"}]
        # When: it is checked as returned
        result = self.check_out(data)
        # Then: it fails and names both
        self.assertProblems(result, "goal_orientation is not as received",
                            "constraints does not keep its received lines first")

    def test_a_returned_ccs_without_exactly_one_fixed_next_is_reported(self):
        # Given: returned CCSs with no next, two, one not among the fixed words, and one to the caller with no reason
        cases = [[], [{"next": "done"}, {"next": "done"}], [{"next": "finished"}],
                 [{"next": "to the caller: "}]]
        for cue in cases:
            with self.subTest(cue=cue):
                data = returned(self.given)
                data["predictive_cue"] = cue
                # When: each is checked as returned
                result = self.check_out(data)
                # Then: each fails, saying it needs exactly one next
                self.assertProblems(result, "predictive_cue needs exactly one next")

    def test_every_fixed_next_is_returned_with_no_output(self):
        # Given: returned CCSs whose next is done, ask the user, to the caller with a reason, and stopped with where to carry on
        for value in ["done", "ask the user", "to the caller: the acceptance says nothing on Docker",
                      "stopped: first-user-2"]:
            with self.subTest(value=value):
                data = returned(self.given)
                data["predictive_cue"] = [{"next": value}]
                # When: each is checked as returned
                result = self.check_out(data)
                # Then: each passes and prints nothing
                self.assertEqual((result.returncode, result.stdout), (0, ""), result.stderr)


if __name__ == "__main__":
    unittest.main()
