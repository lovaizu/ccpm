import json
import os
import subprocess
import sys
import unittest
from unittest import mock

from helpers import CHECKLISTS, NOTES, ROOT, Repo, laid, run, settle, started


class Start(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()

    def tearDown(self):
        self.repo.close()

    def test_a_job_lists_writ_s_checklists_and_the_user_s_each_with_its_name_and_version(self):
        # Given: the user keeps a checklist of their own for release notes
        self.repo.write(".writ/checklists/notes.md", NOTES)
        # When: a job starts
        got = started(self.repo)
        # Then: every checklist of writ's and the user's is listed with what names its kind
        listed = {c["name"]: c for c in got["checklists"]}
        self.assertEqual(
            set(listed), {"checklist", "code", "design", "doc", "prompt", "readme", "notes"}
        )
        self.assertEqual(
            listed["readme"],
            {
                "path": os.path.join(CHECKLISTS, "readme.md"),
                "name": "readme",
                "version": listed["readme"]["version"],
                "title": "README",
                "whose": "writ",
            },
        )
        self.assertEqual(
            (listed["notes"]["path"], listed["notes"]["title"], listed["notes"]["whose"]),
            (".writ/checklists/notes.md", "Release notes", "the user"),
        )
        # Then: the job is open for this session, in a folder of its own
        self.assertTrue(got["folder"].startswith(".writ/jobs/"))
        self.assertEqual(
            self.repo.json(".writ/job.json"), {"session": "s1", "folder": got["folder"]}
        )

    def test_without_jq_the_job_stops_before_anything_is_asked_and_says_what_to_install(self):
        # Given: jq is not installed
        with mock.patch("shutil.which", return_value=None):
            # When: a job starts
            code, out = run(self.repo, "start", "s1")
        # Then: it stops, says to install jq, and opens no job
        self.assertEqual(code, 1)
        self.assertIn("install it (https://jqlang.org/download/)", out)
        self.assertFalse(self.repo.exists(".writ/job.json"))

    def test_a_command_writ_does_not_have_is_answered_with_how_to_call_it(self):
        # Given: a job is open
        started(self.repo)
        # When: a command is called that does not exist, or with too few words
        for args in (["nothing"], ["form"]):
            code, out = run(self.repo, *args)
            # Then: it says how each command is called
            self.assertEqual(code, 1)
            self.assertIn("usage: up.py start <session>", out)

    def test_the_script_run_as_writ_s_skill_runs_it_exits_with_what_its_command_says(self):
        # Given: the script's file
        script = os.path.join(ROOT, "writ", "scripts", "up.py")
        # When: writ's skill runs it with no command
        done = subprocess.run([sys.executable, script], check=False, capture_output=True, text=True)
        # Then: it exits with 1 and says how it is called
        self.assertEqual(done.returncode, 1)
        self.assertIn("usage: up.py start <session>", done.stdout)


class Form(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()

    def tearDown(self):
        self.repo.close()

    def test_the_form_has_a_place_for_what_the_document_is_and_one_for_each_item(self):
        # Given: a job for a README
        # When: its form is laid for the checklists for every document and for READMEs
        folder = laid(self.repo, "doc", "readme")
        # Then: there is an empty place for every item of both, named as turn names them
        form = self.repo.json(f"{folder}/form.json")
        self.assertEqual(
            form["items"]["doc B-1"], {"title": "What it covers", "decision": "", "settled": ""}
        )
        self.assertIn("readme B-3", form["items"])
        self.assertTrue(all(i.split()[0] in ("doc", "readme") for i in form["items"]))
        # Then: and one for each thing turn needs to know of the document
        self.assertEqual(
            {k: v for k, v in form.items() if k != "items"},
            {
                "deliverable": "",
                "receiver": "",
                "use": "",
                "acceptance": "",
                "language": "",
                "sources": [],
                "checklists": [
                    os.path.join(CHECKLISTS, "doc.md"),
                    os.path.join(CHECKLISTS, "readme.md"),
                ],
            },
        )

    def test_a_fenced_example_in_a_checklist_is_not_an_item(self):
        # Given: the user's checklist shows an item's heading inside a fenced example
        self.repo.write(".writ/checklists/notes.md", NOTES)
        folder = started(self.repo)["folder"]
        # When: the form is laid for it
        run(self.repo, "form", folder, ".writ/checklists/notes.md")
        # Then: only the real item has a place
        self.assertEqual(list(self.repo.json(f"{folder}/form.json")["items"]), ["notes B-1"])

    def test_a_file_that_is_not_a_checklist_is_refused(self):
        # Given: a job is open
        folder = started(self.repo)["folder"]
        # When: the form is laid for a file that is not there, and one with no name and version
        code, out = run(self.repo, "form", folder, "missing.md", "docs/notes.md")
        # Then: both are named, and no form is laid
        self.assertEqual(code, 1)
        self.assertIn("missing.md is not there", out)
        self.assertIn("docs/notes.md does not open with a name and a version", out)
        self.assertFalse(self.repo.exists(f"{folder}/form.json"))


class Ccs(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()

    def tearDown(self):
        self.repo.close()

    def test_no_ccs_is_written_while_a_place_is_left_empty(self):
        # Given: a form whose receiver and one item are not settled
        folder = laid(self.repo, "doc")
        form = settle(self.repo, folder, receiver="")
        form["items"]["doc B-2"]["decision"] = ""
        self.repo.write(f"{folder}/form.json", json.dumps(form))
        # When: the CCS is asked for
        code, out = run(self.repo, "ccs", folder)
        # Then: each empty place is named, and no CCS is written
        self.assertEqual(code, 1)
        self.assertIn("receiver is not settled", out)
        self.assertIn("doc B-2: the decision is not settled", out)
        self.assertFalse(self.repo.exists(f"{folder}/in-1.json"))

    def test_a_form_broken_while_it_was_filled_is_named_as_such(self):
        # Given: the form was left as text that is not JSON
        folder = laid(self.repo, "doc")
        self.repo.write(f"{folder}/form.json", "{")
        # When: the CCS is asked for
        code, out = run(self.repo, "ccs", folder)
        # Then: it says the form is not JSON
        self.assertEqual((code, out), (1, "the form is not JSON\n"))

    def test_a_decision_must_say_it_came_from_the_user_or_from_a_file_that_is_there(self):
        # Given: one decision settled by nothing named, one from a file that is not there
        folder = laid(self.repo, "doc")
        form = settle(self.repo, folder)
        form["items"]["doc B-1"]["settled"] = "I think so"
        form["items"]["doc B-2"]["settled"] = "docs/gone.md:3"
        form["items"]["doc B-3"]["settled"] = ""
        self.repo.write(f"{folder}/form.json", json.dumps(form))
        # When: the CCS is asked for
        code, out = run(self.repo, "ccs", folder)
        # Then: each is named with what it must say
        self.assertEqual(code, 1)
        for item in ("doc B-1", "doc B-2", "doc B-3"):
            self.assertIn(
                f"{item}: say where it is settled: answer, proposal confirmed, or a file", out
            )

    def test_a_settled_form_becomes_the_ccs_turn_is_called_with(self):
        # Given: every place is settled, by the notes, an answer and a confirmed proposal
        folder = laid(self.repo, "doc")
        form = settle(self.repo, folder, sources=["docs/notes.md"], language="English")
        form["items"]["doc B-1"].update(decision="Under the MIT license.", settled="answer")
        form["items"]["doc B-2"].update(decision="Leaves out tabs.", settled="proposal confirmed")
        self.repo.write(f"{folder}/form.json", json.dumps(form))
        # When: the CCS is asked for
        code, out = run(self.repo, "ccs", folder)
        # Then: it says what to call turn with
        self.assertEqual(code, 0, out)
        self.assertEqual(out, f"in: {folder}/in-1.json\nout: {folder}/out-1.json\n")
        # Then: the CCS gives turn the document, its reader, its use, the checklists, the sources
        # and the decisions
        ccs = self.repo.json(f"{folder}/in-1.json")
        self.assertEqual(
            ccs["focal_entities"],
            [{"deliverable": "README.md"}, {"receiver": "developers with messy CSV files"}],
        )
        self.assertEqual(
            ccs["goal_orientation"],
            [
                {"use": "to decide on the tool and start"},
                {"acceptance": "they tidy their first folder"},
            ],
        )
        self.assertEqual(
            ccs["retrieved_artifacts"],
            [
                {"viewpoint": os.path.join(CHECKLISTS, "doc.md")},
                {"source": f"{folder}/decisions.md"},
                {"source": "docs/notes.md"},
            ],
        )
        self.assertEqual(ccs["constraints"], [{"language": "English"}])
        for part in (
            "predictive_cue",
            "uncertainty_signal",
            "semantic_gist",
            "relational_map",
            "episodic_trace",
        ):
            self.assertEqual(ccs[part], [])
        # Then: the decisions say, for each item, what the document gives and where it was settled
        decisions = self.repo.read(f"{folder}/decisions.md")
        self.assertIn(
            "## doc B-1: What it covers\n\nUnder the MIT license.\n\nSettled by: answer\n",
            decisions,
        )
        self.assertIn("Leaves out tabs.\n\nSettled by: proposal confirmed\n", decisions)
        self.assertIn("Settled by: docs/notes.md:1\n", decisions)

    def test_a_form_with_no_use_or_language_leaves_them_out_of_the_ccs(self):
        # Given: every place turn needs is settled, and the use and the language are left empty
        folder = laid(self.repo, "doc")
        settle(self.repo, folder, use="")
        # When: the CCS is asked for
        code, _ = run(self.repo, "ccs", folder)
        # Then: the CCS names no use and no language
        ccs = self.repo.json(f"{folder}/in-1.json")
        self.assertEqual(code, 0)
        self.assertEqual(ccs["goal_orientation"], [{"acceptance": "they tidy their first folder"}])
        self.assertEqual(ccs["constraints"], [])


class End(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()

    def tearDown(self):
        self.repo.close()

    def test_a_job_turn_returned_done_ends_with_where_the_document_is(self):
        # Given: turn returned done on the job's CCS
        folder = laid(self.repo, "doc")
        settle(self.repo, folder)
        run(self.repo, "ccs", folder)
        ccs = self.repo.json(f"{folder}/in-1.json")
        ccs["predictive_cue"] = [{"next": "done"}]
        self.repo.write(f"{folder}/out-1.json", json.dumps(ccs))
        # When: the job ends
        code, out = run(self.repo, "end", folder)
        # Then: it says where the document is, and the job is closed
        self.assertEqual((code, out), (0, "README.md is written.\n"))
        self.assertFalse(self.repo.exists(".writ/job.json"))

    def test_a_job_ends_only_on_what_turn_returned(self):
        # Given: the CCS was written, and turn has returned nothing yet
        folder = laid(self.repo, "doc")
        settle(self.repo, folder)
        run(self.repo, "ccs", folder)
        # When: the job is ended
        code, out = run(self.repo, "end", folder)
        # Then: it says turn has not returned, and the job stays open
        self.assertEqual(code, 1)
        self.assertIn(f"{folder}/out-1.json is not there", out)
        self.assertTrue(self.repo.exists(".writ/job.json"))
