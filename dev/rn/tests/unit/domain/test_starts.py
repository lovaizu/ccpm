"""domain/starts.py, what tree.py gives for each start: the change kept for the planner, the run at
hand, each role's cut, the points open, and where the work stands."""

from __future__ import annotations

import json
import os

import helpers
from helpers import GOAL, RUN, runs, starts

READING = ".rn/20261108-tidy-dry-run/turns/02-readme-md-reading/01"
CONTENT = ".rn/20261108-tidy-dry-run/turns/01-readme-md/01"


def good(tree, n=1):
    """The tree with each intent of the deliverable of the number good."""
    for i in tree["deliverables"][n - 1]["vital_few"]:
        i["good"] = True
    return tree


def made(made=("README.md",), open_=(), commands=()):
    return {"made": list(made), "commands": list(commands), "decided": [], "open": list(open_)}


def answered(ids, lacks=(), open_=()):
    return {
        "met": [{"question": q, "lines": ["tidy"]} for q in ids if q not in lacks],
        "not_met": [{"question": q, "lacks": "they can't tell"} for q in lacks],
        "open": [
            {"question": q, "about": "the list", "what": "each file or a count?"} for q in open_
        ],
    }


class Base(helpers.RunTest):
    def round_of(self, path, record=None, groups=None):
        """The round at the path, with the Making record and each group's Answers given."""
        os.makedirs(path, exist_ok=True)
        if record is not None:
            self.write_json(os.path.join(path, runs.MADE), record)
        for name, data in (groups or {}).items():
            self.write_json(os.path.join(path, f"evaluator-{name}.json"), data)

    def readme_groups(self, lacks=(), open_=()):
        """Answers of each group of the readme best practice, all met but those given."""
        found = helpers.practices.groups(starts.practice_of(RUN, "readme"))
        return {f"G{n}": answered(g, lacks, open_) for n, g in enumerate(found, 1)}


class Change(Base):
    def test_a_request_is_kept_for_a_new_run(self):
        with helpers.mock.patch.object(runs, "today", return_value="20261108"):
            said = self.handed({"request": "tidy dry run"})
        self.assertIn("the change for .rn/20261108-tidy-dry-run is kept", said)
        self.assertEqual(
            runs.pending(RUN), {"change": {"request": "tidy dry run"}, "decisions": []}
        )

    def test_decisions_are_kept_each_with_the_key_of_its_node(self):
        self.lays(helpers.decided(helpers.walkthrough("maker"), 1, "Q6", "the list", None))
        self.handed(
            {
                "run": RUN + "/",
                "decisions": [
                    {"at": "goal", "decided": GOAL, "by": "user"},
                    {"at": "D1Q6-1", "decided": "each file", "by": "user"},
                    {
                        "at": "D1Q2",
                        "about": "the gain",
                        "decided": "g",
                        "by": "reasoning",
                        "grounds": "README best practice",
                    },
                ],
            }
        )
        keys = [d["key"] for d in (runs.pending(RUN) or {})["decisions"]]
        self.assertEqual(
            keys,
            [["goal"], ["x", "README.md", "Q6", "the list"], ["x", "README.md", "Q2", "the gain"]],
        )

    def test_a_change_out_of_form_or_at_no_node_is_refused(self):
        self.lays(helpers.walkthrough())
        for text, said in (
            ("{", "the change is no JSON"),
            ('{"request": 1}', "the change is out of its form: $.request"),
            (
                json.dumps({"request": "r", "run": RUN}),
                "the change holds a request or a run, not both",
            ),
            (json.dumps({"run": ".rn/gone"}), ".rn/gone is no run of this repository"),
            (json.dumps({"run": "elsewhere/x"}), "elsewhere/x is no run of this repository"),
            (
                json.dumps({"run": RUN, "decisions": [{"at": "D9", "decided": "d", "by": "user"}]}),
                "D9 is no node of the tree",
            ),
            (
                json.dumps(
                    {"run": RUN, "decisions": [{"at": "D1Q6", "decided": "d", "by": "user"}]}
                ),
                "the decision at the intent D1Q6 needs its about",
            ),
            (
                json.dumps({"run": RUN, "decisions": [{"at": "D1", "decided": "d", "by": "user"}]}),
                "D1 is a deliverable: name the goal, an intent or a decision",
            ),
        ):
            with self.subTest(text=text):
                with self.assertRaises(starts.Stop) as stop:
                    starts.change(text)
                self.assertIn(said, str(stop.exception))

    def test_a_decision_stands_where_the_tree_holds_it_as_handed(self):
        tree = helpers.decided(helpers.walkthrough(), 1, "Q6", "the list", "each file")
        on = {"key": ["x", "README.md", "Q6", "the list"], "decided": "each file", "by": "user"}
        self.assertTrue(starts.stands(tree, on))
        self.assertFalse(starts.stands(tree, {**on, "by": "reasoning"}))
        self.assertTrue(starts.stands(tree, {"key": ["goal"], "decided": GOAL, "by": "user"}))
        self.assertFalse(starts.stands(tree, {"key": ["goal"], "decided": "other", "by": "user"}))


class AtHand(Base):
    def test_the_run_handed_then_the_one_cut_last_then_the_one_left(self):
        with self.assertRaises(starts.Stop):
            starts.at_hand()
        self.lays(helpers.walkthrough(), ".rn/a")
        self.assertEqual(starts.at_hand(), ".rn/a")
        self.lays(helpers.walkthrough(), ".rn/b")
        with self.assertRaises(starts.Stop):
            starts.at_hand()
        starts.mark(".rn/a", {})
        os.utime(os.path.join(runs.temporary(".rn/a"), starts.AT), (1, 1))
        starts.mark(".rn/b", {})
        self.assertEqual(starts.at_hand(), ".rn/b")
        runs.keep(".rn/a", runs.CHANGE, {})
        self.assertEqual(starts.at_hand(), ".rn/a")


class Planner(Base):
    def test_a_new_run_is_made_and_its_goal_asked_for(self):
        with helpers.mock.patch.object(runs, "today", return_value="20261108"):
            self.handed({"request": "tidy dry run"})
        cut = starts.start("planner")
        values = json.loads(cut.splitlines()[0])
        self.assertEqual(values["run"], RUN)
        self.assertEqual(values["tree"], runs.tree_path(RUN))
        self.assertEqual(values["edit"], os.path.join(runs.temporary(RUN), runs.EDIT))
        self.assertTrue(values["practice"].endswith(os.path.join("plan", "best-practice.json")))
        self.assertIsNone(values["vital_few"])
        self.assertIn("# A new run", cut)
        self.assertIn("tidy dry run", cut)
        self.assertTrue(os.path.isdir(RUN))
        self.assertEqual(runs.kept(RUN, starts.CUT), {"kind": "request"})

    def test_the_decisions_settled_each_at_its_node(self):
        self.lays(helpers.decided(helpers.walkthrough("maker"), 1, "Q6", "the list", None))
        self.handed(
            {
                "run": RUN,
                "decisions": [
                    {"at": "goal", "decided": GOAL, "by": "user"},
                    {"at": "D1Q6-1", "decided": "each file", "by": "user"},
                    {
                        "at": "D1Q2",
                        "about": "the gain",
                        "decided": "g",
                        "by": "reasoning",
                        "grounds": "it",
                    },
                ],
            }
        )
        cut = starts.start("planner")
        self.assertIn(f"- at goal: {GOAL} (by user)", cut)
        self.assertIn("- at D1Q6-1: each file (by user)", cut)
        self.assertIn(
            "- at D1Q2, a new decision about the gain: g (by reasoning; grounds: it)", cut
        )
        self.assertIn("The goal is newly the user's", cut)
        self.assertIn("    - D1Q6-1 the list: open", cut)

    def test_a_goal_not_settled_by_the_user_lays_out_no_plan(self):
        self.lays(helpers.walkthrough("maker"))
        self.handed({"run": RUN, "decisions": [{"at": "goal", "decided": "h", "by": "maker"}]})
        self.assertNotIn("newly the user's", starts.start("planner"))

    def test_a_run_named_alone_is_picked_up(self):
        self.lays(helpers.decided(helpers.walkthrough(), 1, "Q6", "the list", None))
        self.handed({"run": RUN})
        cut = starts.start("planner")
        self.assertIn("# Picking up", cut)
        self.assertIn("Give `asks`", cut)

    def test_the_one_run_left_is_picked_up_ready_or_with_a_point(self):
        tree = helpers.walkthrough()
        tree["deliverables"][0]["status"] = "doing"
        self.lays(tree)
        self.assertIn("is ready to make. Give `ready`", starts.start("planner"))
        self.lays(helpers.walkthrough("maker"))
        self.assertIn("Give `asks`", starts.start("planner"))

    def test_a_run_done_or_none_left_or_more_than_one(self):
        self.assertIn(
            "Give `done` by its command, and end with this message: rn has no work",
            starts.start("planner"),
        )
        tree = {"goal": {"decided": GOAL, "by": "user"}, "deliverables": []}
        self.lays(tree)
        self.handed({"run": RUN})
        self.assertIn(f"{RUN} is done", starts.start("planner"))
        runs.drop(RUN, runs.CHANGE)
        self.lays(helpers.walkthrough(), ".rn/a")
        self.lays(helpers.walkthrough(), ".rn/b")
        cut = starts.start("planner")
        self.assertIn("Give `asks`", cut)
        self.assertIn(f"- .rn/a: {GOAL}\n- .rn/b: {GOAL}", cut)
        self.assertEqual(json.loads(cut.splitlines()[0])["run"], None)

    def test_a_turn_come_back_good_of_what_it_says_or_how_it_reads(self):
        self.lays(helpers.walkthrough())
        self.round_of(CONTENT, made(), self.readme_groups())
        cut = starts.start("planner")
        self.assertIn("The turn of what D1 README.md says came back good", cut)
        self.assertEqual(
            runs.kept(RUN, starts.CUT), {"kind": "turn", "path": "README.md", "reading": False}
        )
        self.lays(good(helpers.walkthrough()))
        self.round_of(READING, made(), {"G1": answered([f"Q{n}" for n in range(1, 9)])})
        self.assertIn("The turn of how D1 README.md reads came back good", starts.start("planner"))

    def test_a_turn_not_good_yet_is_no_turn_answer(self):
        self.lays(helpers.walkthrough())
        self.assertIsNone(starts.turn_good(RUN))
        self.round_of(CONTENT, made(), self.readme_groups(lacks=["Q1"]))
        self.assertIsNone(starts.turn_good(RUN))
        self.lays({"goal": {"decided": GOAL, "by": "user"}, "deliverables": []})
        self.assertIsNone(starts.turn_good(RUN))
        self.assertIsNone(starts.turn_good(".rn/none"))

    def test_a_role_rn_has_no(self):
        with self.assertRaises(starts.Stop) as stop:
            starts.start("pinner")
        self.assertIn("rn has no role pinner", str(stop.exception))


class Generator(Base):
    def test_a_turn_of_what_it_says_its_first_round_made(self):
        tree = helpers.decided(helpers.walkthrough(), 1, "Q6", "the list", "each file")
        tree = helpers.decided(tree, 1, "Q6", "the count", None)
        tree["deliverables"][0]["status"] = "doing"
        self.lays(tree)
        cut = starts.start("generator")
        self.assertNotIn("the count", cut)
        values = json.loads(cut.splitlines()[0])
        self.assertEqual(
            {k: values[k] for k in ("run", "deliverable", "inputs", "tests", "proposal", "record")},
            {
                "run": RUN,
                "deliverable": "README.md",
                "inputs": ["dev/product-vision.md"],
                "tests": None,
                "proposal": None,
                "record": os.path.join(CONTENT, runs.MADE),
            },
        )
        self.assertIn("- Q6 the list: each file", cut)
        self.assertIn("A turn of what it says, a deliverable of the kind readme.", cut)
        self.assertIn("- Q1: Telling a colleague", cut)
        self.assertTrue(os.path.isdir(CONTENT))
        # And: started again before the round has a record, it's the same round
        self.assertEqual(
            json.loads(starts.start("generator").splitlines()[0])["record"], values["record"]
        )

    def test_the_next_round_after_shortfalls_with_what_the_people_lacked(self):
        self.lays(helpers.walkthrough())
        self.round_of(CONTENT, made(), self.readme_groups(lacks=["Q5"]))
        cut = starts.start("generator")
        self.assertIn(
            os.path.join(".rn/20261108-tidy-dry-run/turns/01-readme-md/02", runs.MADE), cut
        )
        self.assertIn("- Q5: they can't tell", cut)
        self.assertIn("None yet.", cut)

    def test_a_turn_of_how_it_reads(self):
        self.lays(good(helpers.walkthrough()))
        cut = starts.start("generator")
        self.assertIn("A turn of how it reads, by the best practice refactor-doc", cut)
        self.assertNotIn("## Its intents", cut)
        self.assertIn(os.path.join(RUN, "turns", "01-readme-md-reading", "01", runs.MADE), cut)

    def test_a_code_deliverable_takes_its_commands_from_its_decisions(self):
        tree = {
            "goal": {"decided": GOAL, "by": "user"},
            "deliverables": [
                helpers.deliverable("tidy/cli.py", "code", inputs=["README.md", "tidy"])
            ],
        }
        tree = helpers.decided(tree, 1, "Q6", "tests command", "python3 -m unittest")
        self.lays(tree)
        values = json.loads(starts.start("generator").splitlines()[0])
        self.assertEqual(
            (values["tests"], values["coverage"], values["inputs"]),
            ("python3 -m unittest", None, ["README.md"]),
        )

    def test_a_plugin_has_its_proposal(self):
        tree = {
            "goal": {"decided": GOAL, "by": "user"},
            "deliverables": [helpers.deliverable("plugins/tidy", "plugin")],
        }
        self.lays(tree)
        values = json.loads(starts.start("generator").splitlines()[0])
        self.assertEqual(values["proposal"], ".lane/20261108-tidy/tidy.json")
        self.assertIsNone(values["inputs"])

    def test_no_deliverable_left_or_a_kind_with_no_best_practice(self):
        with self.assertRaises(starts.Stop):
            starts.start("generator")
        self.lays({"goal": {"decided": GOAL, "by": "user"}, "deliverables": []})
        with self.assertRaises(starts.Stop) as stop:
            starts.start("generator")
        self.assertIn("has no deliverable left to make", str(stop.exception))
        d = {**helpers.deliverable("tidy.1", "readme", vital_few=[]), "kind": "man-page"}
        self.lays({"goal": {"decided": GOAL, "by": "user"}, "deliverables": [d]})
        with self.assertRaises(starts.Stop) as stop:
            starts.start("generator")
        self.assertIn("the kind man-page has no best practice yet", str(stop.exception))


class Evaluator(Base):
    def test_each_group_cut_once_in_order_then_the_first_without_answers(self):
        tree = helpers.decided(
            helpers.walkthrough(), 1, "Q1", "accepted shortfall", "a long opening", "user"
        )
        self.lays(tree)
        self.round_of(CONTENT, made(made=["README.md", "gone.md"]))
        cut = starts.start("evaluator")
        values = json.loads(cut.splitlines()[0])
        self.assertEqual(values["files"], ["README.md"])
        self.assertEqual(
            values["reads"],
            [
                "README.md",
                "dev/product-vision.md",
                os.path.join(CONTENT, runs.TRY),
                os.path.join(CONTENT, "evaluator-G1.json"),
            ],
        )
        self.assertIn("# The intents of G1, 1 of 6", cut)
        self.assertIn(
            "The people it's for, and what they're after: Someone who meets the product", cut
        )
        self.assertIn("- Q1: a long opening", cut)
        self.assertIn("- dev/product-vision.md", cut)
        for n in range(2, 7):
            self.assertIn(f"# The intents of G{n}, {n} of 6", starts.start("evaluator"))
        self.write_json(os.path.join(CONTENT, "evaluator-G1.json"), answered(["Q1"]))
        self.assertIn("# The intents of G2, 2 of 6", starts.start("evaluator"))
        for name, data in self.readme_groups().items():
            self.write_json(os.path.join(CONTENT, f"evaluator-{name}.json"), data)
        with self.assertRaises(starts.Stop) as stop:
            starts.start("evaluator")
        self.assertIn("each group of the round has its Answers", str(stop.exception))

    def test_a_turn_of_how_it_reads_gets_no_accepted_lack(self):
        tree = good(
            helpers.decided(
                helpers.walkthrough(), 1, "Q1", "accepted shortfall", "a long opening", "user"
            )
        )
        tree["deliverables"][0]["inputs"] = []
        self.lays(tree)
        self.round_of(READING, made())
        cut = starts.start("evaluator")
        self.assertIn("# The intents of G1, 1 of 1", cut)
        self.assertNotIn("accepted", cut)
        self.assertNotIn("takes its content from", cut)

    def test_no_round_made_to_judge(self):
        with self.assertRaises(starts.Stop):
            starts.start("evaluator")
        self.lays({"goal": {"decided": GOAL, "by": "user"}, "deliverables": []})
        with self.assertRaises(starts.Stop) as stop:
            starts.start("evaluator")
        self.assertIn("has no deliverable left to judge", str(stop.exception))
        self.lays(helpers.walkthrough())
        with self.assertRaises(starts.Stop) as stop:
            starts.start("evaluator")
        self.assertIn("start the generator", str(stop.exception))
        self.round_of(CONTENT, made(open_=[{"intent": "Q6", "about": "a", "what": "w"}]))
        with self.assertRaises(starts.Stop):
            starts.start("evaluator")


class Points(Base):
    def test_the_goal_to_confirm(self):
        self.lays(helpers.walkthrough("maker"))
        self.assertEqual(starts.points(), f"Run: {RUN}\nThe goal, to confirm, at goal: {GOAL}")

    def test_the_plan_and_each_point_open_the_trees_then_the_rounds(self):
        tree = helpers.decided(helpers.walkthrough(), 1, "Q6", "the list", None)
        tree = helpers.decided(tree, 1, "Q2", "the gain", "g")
        self.lays(tree)
        self.round_of(
            CONTENT, made(open_=[{"intent": "Q6", "about": "the count", "what": "a count?"}])
        )
        said = starts.points()
        self.assertIn(
            "Plan, back from the goal:\n1. README.md: the readme of tidy\n"
            "2. tidy/cli.py: the code of tidy",
            said,
        )
        self.assertIn(
            "D1 README.md, of the kind readme, takes its content from dev/product-vision.md.", said
        )
        self.assertIn("Its points open:\n- D1Q6-1 the list: open. Q6: After the walkthrough", said)
        self.assertIn("- D1Q6 the count: a count?. Q6: After the walkthrough", said)

    def test_a_point_a_round_found_that_the_tree_settles_is_none(self):
        tree = helpers.decided(helpers.walkthrough(), 1, "Q6", "the count", "each file")
        self.lays(tree)
        self.round_of(
            CONTENT, made(open_=[{"intent": "Q6", "about": "the count", "what": "a count?"}])
        )
        self.assertIn("No point of D1 is open.", starts.points())

    def test_a_round_not_open_gives_no_point(self):
        self.lays(helpers.walkthrough())
        self.round_of(CONTENT, made(), self.readme_groups(lacks=["Q1"]))
        self.assertIn("No point of D1 is open.", starts.points())

    def test_every_deliverable_done(self):
        done = {"name": "r", "path": "README.md", "kind": "readme", "status": "done"}
        self.lays({"goal": {"decided": GOAL, "by": "user"}, "deliverables": [done]})
        said = starts.points()
        self.assertIn("1. README.md: r (done)", said)
        self.assertTrue(said.endswith("Every deliverable is done."))
        self.assertEqual(starts.status(), f"Done: {GOAL}")

    def test_where_the_work_stands(self):
        tree = helpers.walkthrough()
        tree["deliverables"][0] = helpers.done("README.md", "r")
        self.lays(tree)
        self.assertEqual(starts.status(), f'Picking up "{GOAL}" at 2. tidy/cli.py, README.md done.')
        self.lays(helpers.walkthrough())
        self.assertEqual(starts.status(), f'Picking up "{GOAL}" at 1. README.md.')

    def test_a_run_with_no_tree(self):
        with self.assertRaises(starts.Stop) as stop:
            starts.the_tree(RUN)
        self.assertIn("has no design tree", str(stop.exception))
        with self.assertRaises(starts.Stop):
            starts.practice_of(RUN, "man-page")


class OnBranches(Base):
    """Runs that lie on rn's work branches, `rn/<name>`, with another branch checked out."""

    def away(self):
        """The walkthrough's run committed on its branch, main checked out after it."""
        self.commits(helpers.decided(helpers.walkthrough(), 1, "Q6", "the list", None))
        self.git("switch", "-q", "main")
        self.assertFalse(os.path.exists(runs.tree_path(RUN)))

    def test_the_one_run_waiting_on_its_branch_is_picked_up_there(self):
        self.away()
        cut = starts.start("planner")
        self.assertIn(f"# Picking up\n\n{RUN} stopped at D1 README.md", cut)
        self.assertEqual(
            helpers.repository.ran("git", "branch", "--show-current"), "rn/20261108-tidy-dry-run"
        )
        self.assertTrue(os.path.exists(runs.tree_path(RUN)))

    def test_more_than_one_waiting_on_any_branch_asks_which(self):
        self.away()
        self.lays(helpers.walkthrough(), ".rn/20261107-tidy-readme")
        cut = starts.start("planner")
        self.assertIn(f"- .rn/20261107-tidy-readme: {GOAL}\n- {RUN}: {GOAL}", cut)
        self.assertEqual(helpers.repository.ran("git", "branch", "--show-current"), "main")

    def test_a_run_named_on_its_branch_is_handed_and_picked_up_there(self):
        self.away()
        self.lays(helpers.walkthrough(), ".rn/20261107-tidy-readme")
        self.handed({"run": RUN})
        self.assertIn("# Picking up", starts.start("planner"))
        self.assertEqual(
            helpers.repository.ran("git", "branch", "--show-current"), "rn/20261108-tidy-dry-run"
        )

    def test_a_branch_of_rn_with_no_run_on_it_is_none(self):
        self.git("branch", "rn/20261101-gone")
        self.assertIn("rn has no work left to pick up", starts.start("planner"))


class Edges(Base):
    """The cases on either side of each comparison, so a mutant of it fails a test."""

    def test_two_runs_done_leave_none_at_hand(self):
        done = {
            "goal": {"decided": GOAL, "by": "user"},
            "deliverables": [helpers.done("README.md", "r")],
        }
        self.lays(done, ".rn/a")
        self.lays(done, ".rn/b")
        with self.assertRaises(starts.Stop):
            starts.at_hand()

    def test_a_cut_keeps_each_letter_as_it_is(self):
        self.assertEqual(starts.line({"run": "é"}), '{"run": "é"}')

    def test_a_run_outside_rns_folder_is_refused_however_its_name_sorts(self):
        self.lays(helpers.walkthrough(), ".a/x")
        with self.assertRaises(starts.Stop):
            starts.change(json.dumps({"run": ".a/x"}))

    def test_a_role_rn_has_no_on_either_side_of_its_roles(self):
        for role in ("aaa", "zzz", "generators"):
            with self.subTest(role=role), self.assertRaises(starts.Stop):
                starts.start(role)

    def test_a_new_runs_cut_given_twice(self):
        with helpers.mock.patch.object(runs, "today", return_value="20261108"):
            self.handed({"request": "tidy dry run"})
        starts.start("planner")
        self.assertIn("# A new run", starts.start("planner"))

    def test_a_decision_not_the_goals_lays_out_no_plan_and_each_stands_on_a_line(self):
        self.lays(
            helpers.decided(
                helpers.decided(helpers.walkthrough(), 1, "Q6", "a", None), 1, "Q7", "b", None
            )
        )
        self.handed(
            {
                "run": RUN,
                "decisions": [
                    {"at": "D1Q6-1", "decided": "x", "by": "user"},
                    {"at": "D1Q7-1", "decided": "y", "by": "reasoning"},
                ],
            }
        )
        cut = starts.start("planner")
        self.assertNotIn("newly the user's", cut)
        self.assertIn("- at D1Q6-1: x (by user)\n- at D1Q7-1: y (by reasoning)", cut)

    def test_the_second_deliverable_at_hand(self):
        tree = helpers.walkthrough()
        tree["deliverables"][0] = helpers.done("README.md", "r")
        tree["deliverables"][1]["status"] = "doing"
        tree = helpers.decided(tree, 2, "Q6", "tests command", "python3 -m unittest")
        self.lays(tree)
        self.assertIn("at D2 tidy/cli.py, which is ready to make", starts.start("planner"))
        cut = starts.start("generator")
        values = json.loads(cut.splitlines()[0])
        self.assertEqual(
            (values["deliverable"], values["tests"], values["proposal"]),
            ("tidy/cli.py", "python3 -m unittest", None),
        )
        self.assertIn("# D2 tidy/cli.py", cut)
        self.assertIn("D2 tidy/cli.py, of the kind code", starts.points())
        self.assertEqual(starts.status(), f'Picking up "{GOAL}" at 2. tidy/cli.py, README.md done.')

    def test_a_reading_round_with_a_record_and_no_answers_isnt_good(self):
        self.lays(good(helpers.walkthrough()))
        self.round_of(READING.replace("02-", "01-"), made())
        self.assertIsNone(starts.turn_good(RUN))

    def test_the_points_of_the_last_round_alone(self):
        self.lays(helpers.walkthrough())
        self.round_of(CONTENT, made(open_=[{"intent": "Q6", "about": "old", "what": "o?"}]))
        second = os.path.join(os.path.dirname(CONTENT), "02")
        self.round_of(second, made(open_=[{"intent": "Q6", "about": "new", "what": "n?"}]))
        said = starts.points()
        self.assertIn("- D1Q6 new: n?.", said)
        self.assertNotIn("old", said)

    def test_the_generator_after_two_rounds(self):
        self.lays(helpers.walkthrough())
        self.round_of(CONTENT, made(), self.readme_groups(lacks=["Q1"]))
        second = os.path.join(os.path.dirname(CONTENT), "02")
        self.round_of(second, made(), self.readme_groups(lacks=["Q2"]))
        cut = starts.start("generator")
        self.assertIn("- Q2: they can't tell", cut)
        self.assertNotIn("- Q1: they can't tell", cut)
        self.assertIn(os.path.join(os.path.dirname(CONTENT), "03"), cut)

    def test_the_evaluator_cuts_a_new_round_from_its_first_group(self):
        self.lays(helpers.walkthrough())
        self.round_of(CONTENT, made(), self.readme_groups(lacks=["Q1"]))
        second = os.path.join(os.path.dirname(CONTENT), "02")
        self.round_of(second, made())
        runs.keep(RUN, starts.CUT, {"kind": "evaluator", "round": CONTENT, "cut": ["G1", "G2"]})
        cut = starts.start("evaluator")
        self.assertIn("# The intents of G1, 1 of 6", cut)
        self.assertIn(second, cut)

    def test_a_lack_accepted_by_the_user_alone(self):
        tree = helpers.decided(helpers.walkthrough(), 1, "Q1", "accepted shortfall", "long", "user")
        tree = helpers.decided(tree, 1, "Q1", "a choice", "short", "user")
        tree = helpers.decided(tree, 1, "Q2", "accepted shortfall", "mine", "reasoning")
        self.lays(tree)
        self.round_of(CONTENT, made())
        cut = starts.start("evaluator")
        self.assertIn("- Q1: long", cut)
        self.assertNotIn("short", cut.split("## Lacks the user accepted")[1])
        self.assertNotIn("mine", cut)
