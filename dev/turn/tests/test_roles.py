"""What each role is given, as turn.py prints it when the role first runs it: the files the CCS
names now, as whole paths in the folder the call was made from, and none of the run's own files; the
generator also what the first user's last reading left without Good and the choices its own last
claim named, the first user the receiver, their use and the parts of the work."""

import json
import os
import unittest

from helpers import (
    ALL_GOOD,
    CALL,
    CCS,
    CHECKLIST,
    CHOSEN,
    CLAIM,
    EACH,
    EACH_CCS,
    EACH_ITEM,
    FIRST_READ,
    NEEDED_B1,
    RESULT,
    SECTIONED,
    RepoTest,
    StartedTest,
)


class TestGenerator(StartedTest):
    def test_the_generator_is_given_what_it_makes_the_work_from_and_where_it_replies(self):
        # Given: a run started, nothing in its folder but the call
        # When: the generator first runs turn.py
        # Then: it is given the CCS and every file it names, the work, the checklists, no item
        # asked of each part, the call's test, no need and no choice yet, where it replies, the
        # result, and the check of its claim, each path whole
        self.assertEqual(
            self.printed("generator", self.result),
            {
                "given": [
                    self.here(CALL["ccs"]),
                    self.here("README.md"),
                    self.here("checklists/readme.md"),
                    self.here("notes/readme.decisions.md"),
                    self.here("docs/start.md"),
                ],
                "work": [self.here("README.md")],
                "checklists": [self.here("checklists/readme.md")],
                "each": [],
                "test": "sh tests/readme.sh",
                "needs": [],
                "chosen": [],
                "reply": self.kept("generator.json"),
                "result": self.result,
                "check": f"turn.py claim {self.result}",
            },
        )

    def test_the_generator_is_given_the_calls_test_or_null(self):
        for test in ("make check", None):
            with self.subTest(test=test):
                # Given: a run whose call's test is a command, or null, the caller saying the work
                # has none
                os.remove(self.kept("call.json"))
                result = self.started(dict(CALL, test=test))
                # When: the generator first runs turn.py
                # Then: it is given the call's test as it was given
                self.assertEqual(self.printed("generator", result)["test"], test)

    def test_the_generator_is_given_each_item_the_last_reading_left_without_good(self):
        # Given: the first user's last reading, one item at its lines and one with what the
        # receiver would need
        self.read_as(FIRST_READ)
        # When: the generator runs turn.py
        # Then: it is given the item without Good with its need, as the reading gave it
        self.assertEqual(self.printed("generator", self.result)["needs"], [NEEDED_B1])

    def test_a_reading_with_every_good_or_out_of_its_form_gives_no_need(self):
        # Given: the first user's last reading finding every Good, or one leaving an item out, or
        # one that is no JSON
        for reading in (json.dumps(ALL_GOOD), json.dumps({"items": [NEEDED_B1]}), "read"):
            with self.subTest(reading=reading):
                self.write(self.kept("first-user.json"), reading)
                # When: the generator runs turn.py
                # Then: it is given no need, as only a reading in its form says what is needed
                self.assertEqual(self.printed("generator", self.result)["needs"], [])

    def test_the_generator_is_given_the_choices_its_last_claim_named(self):
        # Given: the generator's last claim, naming a choice it made
        self.claimed(CLAIM)
        # When: the generator runs turn.py again, as after an answer or a call again
        # Then: it is given that choice
        self.assertEqual(self.printed("generator", self.result)["chosen"], [CHOSEN])

    def test_a_claim_out_of_its_form_gives_no_choice(self):
        # Given: the generator's last claim, with a choice without its why, choices that are no
        # list, or no JSON
        for claim in (
            json.dumps(dict(CLAIM, chosen=[{"chosen": "x"}])),
            json.dumps(dict(CLAIM, chosen={})),
            "made",
        ):
            with self.subTest(claim=claim):
                self.write(self.kept("generator.json"), claim)
                # When: the generator runs turn.py
                # Then: it is given no choice
                self.assertEqual(self.printed("generator", self.result)["chosen"], [])

    def test_a_file_an_answer_adds_to_the_ccs_is_given_from_then_on(self):
        # Given: a run started, and the calling AI keeping an answer in the CCS that adds LICENSE
        # to the work
        ccs = self.read_json(CALL["ccs"])
        ccs["focal_entities"].append({"deliverable": "LICENSE"})
        self.write_json(CALL["ccs"], ccs)
        # When: the generator runs turn.py again
        given = self.printed("generator", self.result)
        # Then: LICENSE is among the work it makes
        self.assertEqual(given["work"], [self.here("README.md"), self.here("LICENSE")])

    def test_a_checklist_an_answer_adds_is_given_with_its_items(self):
        # Given: a run started, and the CCS then naming a second checklist
        self.write("checklists/more.md", CHECKLIST)
        ccs = self.read_json(CALL["ccs"])
        ccs["retrieved_artifacts"].append({"checklist": "checklists/more.md"})
        self.write_json(CALL["ccs"], ccs)
        # When: the generator runs turn.py again
        # Then: it is given both checklists
        self.assertEqual(
            self.printed("generator", self.result)["checklists"],
            [self.here("checklists/readme.md"), self.here("checklists/more.md")],
        )

    def test_a_folder_the_ccs_names_with_a_trailing_slash_is_given_as_the_folder(self):
        # Given: a CCS naming a folder with a trailing slash, as a caller names a folder
        self.write_json(
            CALL["ccs"], dict(CCS, goal_orientation=CCS["goal_orientation"] + [{"page": "docs/"}])
        )
        # When: the generator runs turn.py
        # Then: it is given the folder, so the files inside it are found within it
        given = self.printed("generator", self.result)["given"]
        self.assertIn(self.here("docs"), given)
        self.assertNotIn(self.here("docs/"), given)

    def test_a_run_never_started_stops(self):
        # Given: no run started with its result at the path
        # When: a role runs turn.py on it
        # Then: it stops, saying no run is going there and how to start one
        for command in ("generator", "first-user", "parts", "claim", "reading", "end"):
            with self.subTest(command=command):
                out = self.stopped(command, self.here("other.json"))
                self.assertIn("no run is going with its result at", out)
                self.assertIn("turn.py start", out)


class TestFirstUser(StartedTest):
    def test_the_first_user_is_given_what_the_receiver_has_and_where_it_replies(self):
        # Given: a run started
        # When: the first user first runs turn.py
        # Then: it is given the work, what the receiver has and the checklists, no item asked of
        # each part, the receiver, their use, the parts of the work, where it replies and the
        # check of its reading, each path whole; and neither the CCS, the decisions, the call's
        # test, nor any claim
        self.assertEqual(
            self.printed("first-user", self.result),
            {
                "given": [
                    self.here("README.md"),
                    self.here("docs/start.md"),
                    self.here("checklists/readme.md"),
                ],
                "work": [self.here("README.md")],
                "checklists": [self.here("checklists/readme.md")],
                "each": [],
                "receiver": ["a developer new to it"],
                "use": ["to try it on their own files"],
                "parts": [self.here("README.md:1-3")],
                "reply": self.kept("first-user.json"),
                "check": f"turn.py reading {self.result}",
            },
        )

    def test_the_parts_are_given_anew_as_the_work_now_stands(self):
        # Given: a run whose work was mended into a title, an opening and a section
        self.write("README.md", SECTIONED)
        # When: the first user runs turn.py again to read the mended work
        # Then: it is given the parts as the work now stands
        self.assertEqual(
            self.printed("first-user", self.result)["parts"],
            [self.here("README.md:1-4"), self.here("README.md:5-7")],
        )

    def test_the_parts_are_printed_when_asked(self):
        # Given: a run whose work is a title, an opening and a section
        self.write("README.md", SECTIONED)
        # When: the parts are asked for
        # Then: each part is printed as its lines in the work, by whole path
        self.assertEqual(
            self.printed("parts", self.result),
            {"parts": [self.here("README.md:1-4"), self.here("README.md:5-7")]},
        )


class TestEachPart(RepoTest):
    def test_each_role_is_given_the_items_asked_of_each_part_by_whole_path(self):
        # Given: a run whose CCS asks an item of each part of the work
        self.write("checklists/readme.md", CHECKLIST + EACH)
        self.write_json(CALL["ccs"], EACH_CCS)
        result = self.started()
        for role in ("generator", "first-user"):
            with self.subTest(role=role):
                # When: the role first runs turn.py
                # Then: it is given that item, its checklist by whole path
                self.assertEqual(
                    self.printed(role, result)["each"],
                    [dict(EACH_ITEM, checklist=self.here(EACH_ITEM["checklist"]))],
                )


class TestReceiverHasTheRepository(RepoTest):
    """A run whose receiver has the whole repository, `.`, as a maintainer's repository is to its
    maintainer."""

    def setUp(self):
        super().setUp()
        artifacts = [a for a in CCS["retrieved_artifacts"] if "page" not in a] + [{"page": "."}]
        self.write_json(CALL["ccs"], dict(CCS, retrieved_artifacts=artifacts))
        self.result = self.started()
        self.claimed(CLAIM)
        self.read_as(FIRST_READ)
        # Every entry of `.` but `.git`, `.tasks` opened, as the result goes there, and turn's
        # folder left out, as the run's files are there.
        self.entries = [self.here(p) for p in ("checklists", "docs", "notes")]

    def test_the_generator_is_given_no_run_s_file(self):
        # Given: a call whose receiver has `.`, a claim and a reading in the run's folder
        # When: the generator runs turn.py
        # Then: its `given` holds the CCS, the work and each file the CCS names, `.` as its entries
        # without the run's files, each path once
        self.assertEqual(
            self.printed("generator", self.result)["given"],
            [
                self.here(".tasks/readme.json"),
                self.here("README.md"),
                self.here("checklists/readme.md"),
                self.here("notes/readme.decisions.md"),
                self.here(".git"),
                *self.entries,
            ],
        )

    def test_the_first_user_is_given_neither_the_ccs_nor_the_run_s_files(self):
        # Given: a call whose receiver has `.`, the CCS beside the result, a claim and a reading in
        # the run's folder
        # When: the first user runs turn.py
        # Then: its `given` holds the work, `.` as its entries without the CCS and the run's files,
        # and the checklists, each path once
        self.assertEqual(
            self.printed("first-user", self.result)["given"],
            [
                self.here("README.md"),
                self.here(".git"),
                *self.entries,
                self.here("checklists/readme.md"),
            ],
        )


class TestFolderMoved(StartedTest):
    """The session's working folder moves when the calling AI runs `cd`, and every agent's commands
    and hooks then run from there; the run's paths still mean where the call was made."""

    def test_each_role_is_given_whole_paths_of_where_the_call_was_made(self):
        # Given: a run started, and the session's working folder moved to notes/
        os.chdir("notes")
        # When: each role runs turn.py with the result the start gave
        # Then: each is given each file as a whole path in the folder the call was made from
        for role in ("generator", "first-user"):
            with self.subTest(role=role):
                given = self.printed(role, self.result)
                self.assertEqual(given["work"], [self.here("README.md")])
                self.assertEqual(given["checklists"], [self.here("checklists/readme.md")])
                self.assertEqual(given["reply"], self.kept(f"{role}.json"))

    def test_a_result_named_from_the_root_is_found_from_there_alone(self):
        # Given: a run started, and the session's working folder moved to notes/
        os.chdir("notes")
        # When: a role names the result by its path from the root, not the whole path the start
        # printed
        # Then: no run is found there, as the path names a file under notes/
        self.assertIn("no run is going", self.stopped("generator", RESULT))


if __name__ == "__main__":
    unittest.main()
