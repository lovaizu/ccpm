"""domain/edits.py, the planner's edits: a tree edit written, each node it touches listed, the
change committed with the result the planner gives, a deliverable done committed and pushed, the
report of what rn decided without asking, and a tree's form and order checked."""

from __future__ import annotations

import json
import os
import subprocess

import helpers
from helpers import GOAL, RUN, edits, repository, runs, starts

from unit.domain.test_repository import gh
from unit.domain.test_starts import good, made

READING = os.path.join(RUN, "turns", "02-readme-md-reading", "01")
CONTENT = os.path.join(RUN, "turns", "01-readme-md", "01")


class Base(helpers.RunTest):
    def writes(self, nodes=(), answers=(), grounds="g"):
        """The planner's edit of the nodes and answers written: what tree.py printed."""
        path = self.edit({"grounds": grounds, "nodes": list(nodes), "answers": list(answers)})
        return edits.write(RUN, path)

    def stopped(self, call, *args):
        """What the call stops with."""
        with self.assertRaises(starts.Stop) as stop:
            call(*args)
        return str(stop.exception)

    def laid(self):
        """The walkthrough's plan laid and committed, its goal the user's, and the README's point
        open."""
        tree = helpers.decided(helpers.walkthrough(), 1, "Q6", "the list", None)
        self.commits(tree)
        return tree


class Write(Base):
    def test_the_first_edit_gives_the_tree_its_goal(self):
        os.makedirs(RUN)
        said = self.writes([{"id": "goal", "decided": GOAL, "by": "maker"}])
        self.assertEqual(
            said, "rn: the tree holds, and each node it touches is answered. Now commit."
        )
        self.assertEqual(
            self.tree_now(), {"goal": {"decided": GOAL, "by": "maker"}, "deliverables": []}
        )

    def test_a_tree_with_no_goal_out_of_form_or_out_of_order_is_left_as_it_was(self):
        os.makedirs(RUN)
        self.assertEqual(
            self.stopped(self.writes, []), "the tree has no goal yet: give it one at goal"
        )
        self.lays(helpers.walkthrough())
        before = self.tree_now()
        self.assertIn(
            "edit.json is out of its form", self.stopped(self.writes, [{"id": "D1", "name": 1}])
        )
        added = {
            "after": "goal",
            "name": "n",
            "path": "n.md",
            "kind": "readme",
            "inputs": [],
            "preconditions": [],
        }
        said = self.stopped(self.writes, [{**added, "status": "done"}])
        self.assertIn("design-tree.json is out of its form", said)
        said = self.stopped(self.writes, [{"id": "D2", "inputs": ["gone.md"]}])
        self.assertEqual(said, "D2 names gone.md in its inputs, neither a deliverable nor a file")
        self.assertIn("D9 is no node", self.stopped(self.writes, [{"id": "D9"}]))
        self.assertEqual(self.tree_now(), before)

    def test_each_node_touched_is_listed_until_answered(self):
        self.laid()
        said = self.writes([{"id": "D1Q6-1", "decided": "each file", "by": "user"}])
        self.assertEqual(
            said,
            "rn: the tree holds. Answer each node the change touches in your next edit, as holding"
            " or not: goal, D1, D1Q6, D2.",
        )
        said = self.writes(answers=[{"id": n, "holds": True} for n in ("goal", "D1")])
        self.assertIn("as holding or not: D1Q6, D2.", said)
        said = self.writes(answers=[{"id": n, "holds": True} for n in ("D1Q6", "D2")])
        self.assertIn("each node it touches is answered", said)

    def test_a_change_starts_the_answers_again(self):
        self.laid()
        self.writes([{"id": "D1Q6-1", "decided": "each file", "by": "user"}])
        self.writes(answers=[{"id": n, "holds": True} for n in ("goal", "D1", "D1Q6", "D2")])
        said = self.writes([{"id": "D1", "status": "doing"}])
        self.assertIn("as holding or not: goal, D1Q6, D2.", said)

    def test_each_decision_not_the_users_goes_to_the_commit_with_its_grounds(self):
        self.laid()
        self.writes(
            [
                {
                    "id": "D1Q2",
                    "about": "the gain",
                    "decided": "less clutter",
                    "by": "reasoning",
                    "grounds": "the product vision",
                },
                {
                    "id": "D1Q3",
                    "about": "the limit",
                    "decided": "Linux and macOS",
                    "by": "research",
                },
                {"id": "D1Q6-1", "decided": "each file", "by": "user"},
                {"id": "goal", "decided": GOAL, "by": "maker"},
            ],
            grounds="The README's points settled.",
        )
        kept = runs.kept(RUN, starts.EDITS)
        self.assertEqual(
            kept,
            [
                {
                    "grounds": "The README's points settled.",
                    "decided": [
                        "Decided: less clutter (the product vision)",
                        "Decided: Linux and macOS (research)",
                    ],
                }
            ],
        )


class Commit(Base):
    def ready_to_commit(self):
        """The README's point settled by the user, as handed, each node touched answered."""
        self.laid()
        self.handed(
            {"run": RUN, "decisions": [{"at": "D1Q6-1", "decided": "each file", "by": "user"}]}
        )
        starts.start("planner")
        self.writes([{"id": "D1Q6-1", "decided": "each file", "by": "user"}], grounds="The list.")

    def test_a_change_commits_with_its_grounds_and_the_result_to_give(self):
        self.ready_to_commit()
        self.writes(
            [{"id": "D1", "status": "doing"}],
            answers=[{"id": n, "holds": True} for n in ("goal", "D1Q6-1", "D2", "D1Q6")],
            grounds="Ready.",
        )
        said = edits.commit(RUN)
        self.assertEqual(
            said,
            f"rn: committed on rn/20261108-tidy-dry-run. Give `ready` by its command, and end with"
            f" this message: the tree of {RUN} is committed.",
        )
        self.assertEqual(repository.messages(RUN)[-1], f"rn: The list. Ready.\n\nRn-Run: {RUN}")
        self.assertIsNone(runs.pending(RUN))
        self.assertIsNone(runs.kept(RUN, starts.EDITS))

    def test_a_node_unanswered_or_a_decision_not_as_handed_stops_the_commit(self):
        self.ready_to_commit()
        self.assertEqual(
            self.stopped(edits.commit, RUN),
            "answer each node the change touches first: goal, D1, D1Q6, D2",
        )
        self.writes(
            [{"id": "D1Q6-1", "decided": "a count", "by": "user"}],
            answers=[{"id": n, "holds": True} for n in ("goal", "D1", "D1Q6", "D2")],
        )
        self.assertEqual(
            self.stopped(edits.commit, RUN),
            "the tree doesn't hold the decision handed at D1Q6-1: each file",
        )

    def test_a_deliverable_with_no_point_open_must_be_doing(self):
        tree = helpers.walkthrough()
        self.commits(tree)
        self.writes([{"id": "D1", "name": "the dry run"}])
        self.writes(answers=[{"id": n, "holds": True} for n in ("goal", "D2")])
        self.assertEqual(
            self.stopped(edits.commit, RUN), "D1 has no point open: set its status to doing"
        )

    def test_asks_while_the_goal_isnt_the_users_or_a_point_is_open(self):
        os.makedirs(RUN)
        self.writes([{"id": "goal", "decided": GOAL, "by": "maker"}])
        self.assertIn("Give `asks`", edits.commit(RUN))
        self.assertEqual(repository.messages(RUN), [f"rn: g\n\nRn-Run: {RUN}"])
        tree = helpers.decided(helpers.walkthrough(), 1, "Q6", "the list", None)
        self.lays(tree)
        self.writes(answers=[])
        self.assertIn("Give `asks`", edits.commit(RUN))

    def test_done_once_no_deliverable_is_left(self):
        self.lays({"goal": {"decided": GOAL, "by": "user"}, "deliverables": []})
        self.assertIn("Give `done`", edits.commit(RUN))

    def test_a_turn_of_what_it_says_holds_each_intent_good(self):
        tree = helpers.walkthrough()
        tree["deliverables"][0]["status"] = "doing"
        self.commits(tree)
        runs.keep(RUN, starts.CUT, {"kind": "turn", "path": "README.md", "reading": False})
        self.writes([{"id": "D1Q1", "good": True}])
        self.writes(
            answers=[
                {"id": n, "holds": True}
                for n in (
                    "goal",
                    "D1",
                    "D1Q2",
                    "D1Q3",
                    "D1Q4",
                    "D1Q5",
                    "D1Q6",
                    "D1Q7",
                    "D1Q8",
                    "D1Q9",
                    "D1Q10",
                    "D1Q11",
                    "D2",
                )
            ]
        )
        said = self.stopped(edits.commit, RUN)
        self.assertEqual(
            said,
            "the turn met each intent of README.md: make Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10, Q11"
            " good",
        )

    def test_a_turn_of_how_it_reads_commits_by_deliver(self):
        self.commits(good(helpers.walkthrough()))
        runs.keep(RUN, starts.CUT, {"kind": "turn", "path": "README.md", "reading": True})
        self.assertEqual(
            self.stopped(edits.commit, RUN),
            "README.md reads well: set it done, and run tree.py deliver",
        )


class Deliver(Base):
    def setUp(self) -> None:
        super().setUp()
        tree = good(helpers.walkthrough())
        self.commits(tree)
        for path, record in (
            (
                CONTENT,
                {
                    **made(made=["README.md", "tests/test_dry_run.py"]),
                    "decided": [
                        {
                            "intent": "Q6",
                            "about": "the order",
                            "decided": "--dry-run comes first",
                            "grounds": "README best practice",
                        }
                    ],
                },
            ),
            (READING, made()),
        ):
            self.write_json(os.path.join(path, runs.MADE), record)
        self.write("tests/test_dry_run.py", "x\n")
        self.write("README.md", "# tidy --dry-run\n")
        runs.keep(RUN, starts.CUT, {"kind": "turn", "path": "README.md", "reading": True})
        self.writes(
            [{"id": "D1", "status": "done"}, {"id": "D2", "status": "doing"}],
            grounds="The README reads well.",
        )
        self.writes(answers=[{"id": "goal", "holds": True}])
        subprocess.run(
            ["git", "init", "-q", "--bare", os.path.join(self.base, "origin.git")], check=True
        )
        self.git("remote", "add", "origin", os.path.join(self.base, "origin.git"))
        path = os.environ["PATH"]
        os.environ["PATH"] = f"{gh(os.path.join(self.base, 'bin'), False)}:{path}"
        self.addCleanup(os.environ.__setitem__, "PATH", path)

    def test_the_deliverable_its_files_and_the_run_committed_and_pushed(self):
        said = edits.deliver(RUN)
        self.assertEqual(
            said,
            "rn: committed README.md on rn/20261108-tidy-dry-run, and pushed:"
            " https://github.com/tidy-sort/tidy/pull/8. Give `ready` by its command, and end with"
            " this message: README.md is done.",
        )
        message = repository.messages(RUN)[-1]
        self.assertEqual(
            message,
            "rn: README.md: the readme of tidy\n\nThe README reads well. g\n\n"
            f"Decided: --dry-run comes first (README best practice)\n\nRn-Run: {RUN}",
        )
        shown = repository.ran("git", "show", "--name-only", "--format=", "HEAD")
        self.assertIn("tests/test_dry_run.py", shown)
        self.assertIn("README.md", shown)

    def test_a_push_it_cant_make_is_named_the_commit_kept(self):
        self.git("remote", "remove", "origin")
        said = edits.deliver(RUN)
        self.assertIn(
            "rn: committed README.md on rn/20261108-tidy-dry-run, which isn't pushed:"
            " `git push -q` gave:",
            said,
        )
        self.assertIn("Name what's missing in your message for the user. Give `ready`", said)

    def test_the_last_deliverable_done_gives_done_with_the_report(self):
        tree = self.tree_now()
        del tree["deliverables"][1]
        self.lays(tree)
        self.writes(answers=[{"id": "goal", "holds": True}])
        said = edits.deliver(RUN)
        self.assertIn(
            "Give `done` by its command, and end with this message:\nDone: README.md is changed,"
            " with tests/test_dry_run.py.",
            said,
        )
        self.assertIn(
            "Decided without asking you:\n- --dry-run comes first (README best practice)", said
        )

    def test_none_set_done_stops_it(self):
        self.commits(good(helpers.walkthrough()))
        self.assertEqual(
            self.stopped(edits.deliver, RUN),
            "set the one deliverable whose turn of how it reads came back good done",
        )


class Report(Base):
    def test_each_deliverable_and_no_decision_taken_without_asking(self):
        done = [
            {"name": n, "path": p, "kind": "readme", "status": "done"}
            for n, p in (("r", "README.md"), ("c", "tidy/cli.py"))
        ]
        self.commits({"goal": {"decided": GOAL, "by": "user"}, "deliverables": done})
        self.assertEqual(
            edits.report(RUN),
            "Done: README.md and tidy/cli.py are changed. Each was tried as its people would use"
            " it, and meets every question of its kind's best practice.",
        )


class Check(Base):
    def test_a_tree_in_order_and_one_out_of_it(self):
        self.lays(helpers.walkthrough())
        self.assertEqual(edits.check(runs.tree_path(RUN)), [])
        tree = helpers.walkthrough()
        tree["deliverables"].reverse()
        self.lays(tree)
        self.assertEqual(
            edits.check(runs.tree_path(RUN)),
            ["D1 takes README.md in its inputs, which comes later"],
        )
        self.assertEqual(json.loads(self.read(runs.tree_path(RUN)))["goal"]["by"], "user")


class TurnGood(Base):
    def test_a_turn_of_what_it_says_commits_once_each_intent_is_good(self):
        tree = helpers.walkthrough()
        tree["deliverables"][0]["status"] = "doing"
        self.commits(tree)
        runs.keep(RUN, starts.CUT, {"kind": "turn", "path": "README.md", "reading": False})
        self.writes([{"id": f"D1Q{n}", "good": True} for n in range(1, 12)])
        self.writes(answers=[{"id": n, "holds": True} for n in ("goal", "D1", "D2")])
        self.assertIn("Give `ready`", edits.commit(RUN))
