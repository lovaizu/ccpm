"""How runs.py begins and moves a run's works, by the classes of its contract: a best practice found
in the repository or in Turn, read or refused; the points a calling AI settled, handed over word for
word or refused; a kind Turn knows, or one new to it whose best practice is made first; and each
work waiting, with Pin, in its rounds or done."""

import json
import os
import unittest

import helpers
from helpers import files, practices, runs

RUN = helpers.RUN
DESIGN = os.path.join(RUN, runs.DESIGN)


class PracticeOf(helpers.RepositoryTest):
    def test_the_repositorys_best_practice_is_taken_over_turns_own(self):
        path = os.path.join(".turn", "best-practices", "readme", "best-practice.json")
        self.write_json(path, helpers.PRACTICE)
        self.assertEqual(runs.practice_of("readme"), path)

    def test_turns_own_is_taken_where_the_repository_has_none(self):
        self.assertEqual(
            runs.practice_of("readme"), os.path.join(runs.OWN, "readme", "best-practice.json")
        )

    def test_a_kind_neither_has_has_none(self):
        self.assertIsNone(runs.practice_of("man-page"))


class ReadPractice(helpers.RepositoryTest):
    def test_one_in_form_is_read(self):
        self.assertEqual(runs.read_practice(helpers.NOTE), helpers.PRACTICE)

    def test_one_missing_no_json_or_out_of_its_schema_is_refused(self):
        self.write("no.json", "{")
        self.write_json("list.json", [])
        for path, said in (
            ("gone.json", "there is no file gone.json"),
            ("no.json", "no.json is not JSON"),
            ("list.json", "list.json is out of its form"),
        ):
            with self.subTest(path=path), self.assertRaises(files.Unreadable) as raised:
                runs.read_practice(path)
            self.assertIn(said, str(raised.exception))

    def test_one_out_of_its_form_is_refused_with_each_fault(self):
        data = helpers.practice()
        data["practices"].pop()
        self.write_json("short.json", data)
        with self.assertRaises(files.Unreadable) as raised:
            runs.read_practice("short.json")
        self.assertEqual(
            str(raised.exception),
            "the best practice short.json is out of its form: " + "; ".join(practices.faults(data)),
        )


class Current(unittest.TestCase):
    def test_the_first_work_not_done(self):
        works = [{"at": "done"}, {"at": "pin"}, {"at": "waits"}]
        self.assertIs(runs.current({"works": works}), works[1])

    def test_the_last_where_each_is_done(self):
        works = [{"at": "done"}, {"at": "done"}]
        self.assertIs(runs.current({"works": works}), works[1])


class GivenFaults(unittest.TestCase):
    def test_a_call_that_gives_nothing_or_the_same_kind_has_none(self):
        self.assertEqual(runs.given_faults(helpers.call()), [])
        self.assertEqual(runs.given_faults(helpers.call(given={"kind": "note"})), [])

    def test_another_kind_than_the_calls(self):
        for kind in ("readme", "man-page"):
            with self.subTest(kind=kind):
                self.assertEqual(
                    runs.given_faults(helpers.call(given={"kind": kind})),
                    [f"the kind is note, but the calling AI gave {kind}"],
                )

    def test_a_decision_settled_by_the_maker_ai_has_none(self):
        given = {"decisions": [helpers.SETTLED]}
        self.assertEqual(runs.given_faults(helpers.call(given=given)), [])

    def test_a_decision_open_or_settled_by_another(self):
        said = (
            "the calling AI's decision D1 is not decided with settled_by maker,"
            " as Calling Turn asks"
        )
        for change in ({"decided": None}, {"settled_by": "user"}, {"settled_by": None}):
            given = {"decisions": [{**helpers.SETTLED, **change}]}
            with self.subTest(change=change):
                self.assertEqual(runs.given_faults(helpers.call(given=given)), [said])


class Start(helpers.RepositoryTest):
    def test_a_kind_it_knows_is_handed_to_pin_with_its_questions(self):
        # Given: a Call of note, which the repository has a best practice of
        # When: the run begins
        request = self.started()
        # Then: the Run holds the one work with Pin; the hand-over asks each question of note under
        # the planner's reading of the goal, not yet confirmed; the Standards are written; and the
        # Request names the design tree, then the request
        self.assertEqual(self.run_data(), {"works": [helpers.work(paths=[], at="pin")]})
        self.assertEqual(
            helpers.tree.load(DESIGN),
            {
                "goal": {"what": helpers.CALL["goal"], "grounds": []},
                "questions": [
                    {"id": f"note/Q{n}", "what": q["what"]}
                    for n, q in enumerate(helpers.PRACTICE["intents"], 1)
                ],
                "decisions": [],
            },
        )
        self.assertEqual(
            self.read_json(os.path.join(RUN, runs.STANDARD)),
            practices.standard(helpers.PRACTICE),
        )
        reading = runs.read_practice(runs.practice_in(runs.OWN, "refactor-doc"))
        self.assertEqual(
            self.read_json(os.path.join(RUN, runs.READING)), practices.standard(reading)
        )
        self.assertEqual(request, json.dumps({"design": DESIGN}) + "\na note on tidy")

    def test_what_the_calling_ai_settled_is_handed_over_word_for_word(self):
        # Given: a Call whose calling AI gave the kind, the goal, a decision and the work's path
        goal = {"what": "A newcomer sorts their folder.", "grounds": ["the person, 2026-11-03"]}
        given = {"kind": "note", "goal": goal, "decisions": [helpers.SETTLED], "work": ["N.md"]}
        # When: the run begins
        self.started(helpers.call(given=given))
        # Then: the hand-over holds its goal and decision as given, and the work its path
        tree = helpers.tree.load(DESIGN)
        self.assertEqual((tree["goal"], tree["decisions"]), (goal, [helpers.SETTLED]))
        self.assertEqual(self.run_data()["works"][0]["paths"], ["N.md"])

    def test_a_kind_new_to_turn_has_its_best_practice_made_first(self):
        # Given: a Call of man-page, which no best practice is of, with the kind's purpose
        purpose = "Someone who types man tidy learns each option."
        data = helpers.call(kind="man-page", kind_goal=purpose)
        # When: the run begins
        request = self.started(data)
        # Then: the Run holds the best practice's work with Pin, by meta, then the man page's,
        # waiting; the hand-over asks meta's questions of the kind's purpose
        made = runs.practice_in(runs.REPOSITORY, "man-page")
        folder = os.path.join(RUN, "best-practice")
        meta = runs.practice_in(runs.OWN, "meta")
        self.assertEqual(
            self.run_data()["works"],
            [
                helpers.work(
                    kind="meta",
                    practice=meta,
                    folder=folder,
                    paths=[made],
                    at="pin",
                ),
                helpers.work(kind="man-page", practice=made, paths=[], at="waits"),
            ],
        )
        tree = helpers.tree.load(os.path.join(folder, runs.DESIGN))
        self.assertEqual(tree["goal"], {"what": purpose, "grounds": []})
        self.assertEqual(tree["questions"], runs.questions("meta", runs.read_practice(meta)))
        self.assertEqual(
            request,
            json.dumps({"design": os.path.join(folder, runs.DESIGN)})
            + "\nThe best practice of the kind man-page, which Turn has none of, to make this"
            " request by: a note on tidy",
        )

    def test_a_call_of_meta_makes_one_best_practice_under_the_calls_goal(self):
        # Given: a Call of meta, whose best practice Turn has, with no kind_goal
        request = self.started(helpers.call(kind="meta"))
        # Then: the one work, by meta, is handed to Pin under the Call's goal and request
        meta = runs.practice_in(runs.OWN, "meta")
        works = self.run_data()["works"]
        self.assertEqual(works, [helpers.work(kind="meta", practice=meta, paths=[], at="pin")])
        self.assertEqual(
            helpers.tree.load(DESIGN)["goal"], {"what": helpers.CALL["goal"], "grounds": []}
        )
        self.assertEqual(request, json.dumps({"design": DESIGN}) + "\na note on tidy")

    def test_the_hand_over_is_written_as_pins_markdown(self):
        # Given: a Call whose calling AI gave a decision
        given = {"kind": "note", "decisions": [helpers.SETTLED]}
        # When: the run begins
        self.started(helpers.call(given=given))
        # Then: the design tree is the hand-over as Pin's tree.py writes it
        self.assertEqual(self.read(DESIGN), helpers.tree.markdown(helpers.tree.load(DESIGN)))
        self.assertIn(
            "- **D1 Which run the steps show**: tidy --dry-run, then tidy (maker)\n",
            self.read(DESIGN),
        )

    def test_points_out_of_the_design_trees_form_are_refused_with_nothing_written(self):
        # Given: a Call whose calling AI gave a decision Pin's design tree cannot hold
        given = {"decisions": [{**helpers.SETTLED, "what": "two\nlines"}]}
        # When: the run begins
        with self.assertRaises(files.Unreadable) as raised:
            self.started(helpers.call(given=given))
        # Then: it is refused, naming the fault, and nothing is written
        self.assertEqual(
            str(raised.exception),
            "the design cannot be handed to Pin: decisions[0].what must be one line of text, not"
            " empty, with no `**`",
        )
        self.assertFalse(os.path.exists(DESIGN))
        self.assertFalse(os.path.exists(os.path.join(RUN, runs.RUN)))

    def test_a_kind_new_to_turn_with_no_purpose_is_refused(self):
        with self.assertRaises(files.Unreadable) as raised:
            self.started(helpers.call(kind="man-page"))
        self.assertIn("write into call.json its kind_goal", str(raised.exception))
        self.assertFalse(os.path.exists(os.path.join(RUN, runs.RUN)))

    def test_points_that_cannot_be_handed_over_as_given_are_refused(self):
        with self.assertRaises(files.Unreadable) as raised:
            self.started(helpers.call(given={"kind": "readme"}))
        self.assertEqual(str(raised.exception), "the kind is note, but the calling AI gave readme")
        self.assertFalse(os.path.exists(os.path.join(RUN, runs.RUN)))

    def test_a_run_begun_before_or_with_no_call_is_refused(self):
        with self.assertRaises(files.Unreadable):
            runs.start(RUN)
        self.started()
        with self.assertRaises(files.Unreadable) as raised:
            runs.start(RUN)
        self.assertIn("has begun already", str(raised.exception))

    def test_a_best_practice_out_of_its_form_is_refused_with_nothing_written(self):
        data = helpers.practice()
        data["intents"][0]["id"] = "Q9"
        self.write_json(helpers.NOTE, data)
        with self.assertRaises(files.Unreadable):
            self.started()
        self.assertFalse(os.path.exists(os.path.join(RUN, runs.RUN)))
        self.assertFalse(os.path.exists(DESIGN))


class Request(unittest.TestCase):
    def test_a_path_out_of_ascii_is_written_as_it_is(self):
        self.assertEqual(
            runs.request("ノート/design-tree.md", "メモ"),
            '{"design": "ノート/design-tree.md"}\nメモ',
        )


class GeneratorValues(unittest.TestCase):
    def test_a_run_out_of_ascii_is_written_as_it_is(self):
        self.assertIn('"run": "ノート"', runs.generator_values("ノート", helpers.work()))

    def test_names_the_run_the_work_and_the_generators_answers(self):
        self.assertEqual(
            runs.generator_values(RUN, helpers.work()),
            helpers.line(
                {
                    "run": RUN,
                    "work": ["NOTES.md"],
                    "answers": os.path.join(RUN, "verification", "generator.json"),
                }
            ),
        )


class WorkFaults(helpers.RepositoryTest):
    def test_files_have_none(self):
        self.assertEqual(runs.work_faults(helpers.work(paths=["a.md", "b/c.py"])), [])

    def test_no_paths(self):
        self.assertEqual(
            runs.work_faults(helpers.work(paths=[])),
            ["the work of note has no paths: write them into its paths"],
        )

    def test_a_folder_named_as_such_or_lying_there(self):
        os.makedirs("docs")
        self.assertEqual(
            runs.work_faults(helpers.work(paths=["src/", "docs", "a.md"])),
            [
                "the path src/ is a folder: name each file of the work",
                "the path docs is a folder: name each file of the work",
            ],
        )


class Ready(helpers.RepositoryTest):
    def test_a_work_with_pin_goes_to_its_rounds(self):
        self.lay_run([helpers.work(at="pin")])
        self.assertEqual(runs.ready(RUN), runs.generator_values(RUN, helpers.work()))
        self.assertEqual(self.run_data()["works"][0]["at"], "rounds")

    def test_a_work_in_its_rounds_stays_there(self):
        self.lay_run([helpers.work()])
        self.assertEqual(runs.ready(RUN), runs.generator_values(RUN, helpers.work()))
        self.assertEqual(self.run_data()["works"][0]["at"], "rounds")

    def test_a_work_with_no_paths_stays_with_pin(self):
        self.lay_run([helpers.work(at="pin", paths=[])])
        with self.assertRaises(files.Unreadable) as raised:
            runs.ready(RUN)
        self.assertEqual(str(raised.exception), runs.work_faults(helpers.work(paths=[]))[0])
        self.assertEqual(self.run_data()["works"][0]["at"], "pin")

    def test_a_work_done_is_refused(self):
        self.lay_run([helpers.work(at="done")])
        with self.assertRaises(files.Unreadable) as raised:
            runs.ready(RUN)
        self.assertIn("the work is done", str(raised.exception))


class Hand(helpers.RepositoryTest):
    def test_the_work_in_its_rounds_goes_to_pin(self):
        self.lay_run([helpers.work(at="done"), helpers.work()])
        self.assertEqual(runs.hand(RUN), helpers.work(at="pin"))
        self.assertEqual([w["at"] for w in self.run_data()["works"]], ["done", "pin"])

    def test_the_last_work_done_goes_to_pin_for_a_change(self):
        self.lay_run([helpers.work(at="done")])
        runs.hand(RUN)
        self.assertEqual(self.run_data()["works"][0]["at"], "pin")


class Advance(helpers.RepositoryTest):
    def test_the_last_work_done_ends_the_run(self):
        self.lay_run([helpers.work()])
        self.assertEqual(runs.advance(RUN), "")
        self.assertEqual(self.run_data()["works"][0]["at"], "done")

    def test_a_best_practice_made_begins_the_work_by_it(self):
        # Given: the best practice of man-page made, in its rounds, the man page waiting
        made = runs.practice_in(runs.REPOSITORY, "man-page")
        self.write_json(made, helpers.PRACTICE)
        folder = os.path.join(RUN, "best-practice")
        self.lay_run(
            [
                helpers.work(kind="meta", folder=folder, paths=[made]),
                helpers.work(kind="man-page", practice=made, paths=[], at="waits"),
            ]
        )
        # When: the run goes on
        request = runs.advance(RUN)
        # Then: the best practice's work is done, its Markdown beside it, and the man page is
        # handed to Pin with its questions under the Call's goal
        self.assertEqual([w["at"] for w in self.run_data()["works"]], ["done", "pin"])
        self.assertEqual(
            self.read(os.path.join(runs.REPOSITORY, "man-page", "best-practice.md")),
            practices.markdown("man-page", helpers.PRACTICE),
        )
        tree = helpers.tree.load(DESIGN)
        self.assertEqual(tree["goal"]["what"], helpers.CALL["goal"])
        self.assertEqual(tree["questions"][0]["id"], "man-page/Q1")
        self.assertEqual(request, json.dumps({"design": DESIGN}) + "\na note on tidy")

    def test_a_best_practice_made_out_of_its_form_keeps_the_work_in_its_rounds(self):
        made = runs.practice_in(runs.REPOSITORY, "man-page")
        self.write_json(made, {"goal": "g"})
        self.lay_run(
            [
                helpers.work(kind="meta", paths=[made]),
                helpers.work(kind="man-page", practice=made, at="waits"),
            ]
        )
        with self.assertRaises(files.Unreadable):
            runs.advance(RUN)
        self.assertEqual([w["at"] for w in self.run_data()["works"]], ["rounds", "waits"])

    def test_the_last_of_two_works_done_ends_the_run(self):
        self.lay_run([helpers.work(kind="meta", at="done"), helpers.work()])
        self.assertEqual(runs.advance(RUN), "")
        self.assertEqual([w["at"] for w in self.run_data()["works"]], ["done", "done"])

    def test_a_work_not_in_its_rounds_is_refused(self):
        for at in ("pin", "waits"):
            with self.subTest(at=at):
                self.lay_run([helpers.work(at=at)])
                with self.assertRaises(files.Unreadable) as raised:
                    runs.advance(RUN)
                self.assertEqual(
                    str(raised.exception), f"the work of note is not in its rounds, but {at}"
                )


class Done(unittest.TestCase):
    def test_names_the_paths_the_questions_and_where_the_checks_lie(self):
        self.assertEqual(
            runs.done(helpers.work(paths=["NOTES.md", "a.md"])),
            "Done: NOTES.md, a.md written, and not committed. It meets every question of note and"
            f" of refactor-doc. {RUN}/verification/ shows the lines that meet each question.",
        )


if __name__ == "__main__":
    unittest.main()
