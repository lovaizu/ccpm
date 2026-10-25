"""The tests of each work handed to turn: each decision kept in the work's call, the CCS written for
it, and the checklists of a kind."""

from __future__ import annotations

import json
import os
import unittest
from typing import Any

from helpers import (
    FOLDER,
    KIND,
    LEARNINGS,
    NEEDED,
    RECORD,
    RepoTest,
    call_at,
    options,
    plan,
    steered,
    task,
)


class DecideTest(RepoTest):
    """Each answer kept as a decision of the work it settles, in that work's call to turn."""

    def setUp(self) -> None:
        super().setUp()
        self.session(steered(stage="design"))

    def decide(self, work: str = "t1.1", title: str = "License", says: str = "MIT") -> Any:
        """Keeps the decision of the work, with its title and what it says."""
        return self.ran("decide", work, "--title", title, "--says", says, "--message", "t1.1: MIT")

    def test_a_first_decision_makes_the_works_first_call_and_keeps_it(self):
        # Given: a session with no call.
        # When: the orchestrator keeps a decision of the work t1.
        out = self.decide()
        # Then: the first call holds the work, the stage, and the decision, kept on the remote
        # with the message.
        want = {
            "focal_entities": [{"work": "t1.1"}, {"stage": "design"}],
            "constraints": [{"decision": "License: MIT"}],
        }
        kept = (
            self.read_json(call_at("0001")),
            json.loads(self.out("show", f"origin/work:{call_at('0001')}")),
            self.out("log", "-1", "--format=%B", "origin/work"),
        )
        self.assertEqual(
            (out, kept), ({"call": "0001", "kept": self.head()}, (want, want, "t1.1: MIT\n\n"))
        )

    def test_a_decision_goes_into_the_works_latest_call_not_returned(self):
        # Given: a call on t1.1 and one on t2.1, neither returned, kept.
        self.call("0001", "t1.1", decisions=("Form: a page",))
        self.call("0002", "t2.1")
        self.kept()
        # When: the orchestrator keeps a decision of t1.
        out = self.decide()
        # Then: it is added to t1.1's call.
        self.assertEqual(
            (out["call"], self.read_json(call_at("0001"))["constraints"]),
            ("0001", [{"decision": "Form: a page"}, {"decision": "License: MIT"}]),
        )

    def test_a_decision_of_the_same_title_is_replaced_where_it_stands(self):
        # Given: a call on t1.1 with two decisions.
        self.call("0001", "t1.1", decisions=("License: Apache-2.0", "Form: a page"))
        self.kept()
        # When: the orchestrator keeps a decision of the first's title.
        self.decide()
        # Then: it replaces the first, where it stood.
        self.assertEqual(
            self.read_json(call_at("0001"))["constraints"],
            [{"decision": "License: MIT"}, {"decision": "Form: a page"}],
        )

    def test_a_decision_after_turn_returned_makes_a_new_call_carrying_the_decisions(self):
        # Given: a call on t1.1 returned, with its decisions, the languages and the fix.
        self.call("0001", "t1.1", decisions=("License: Apache-2.0", "Form: a page"), result={})
        ccs = self.read_json(call_at("0001"))
        ccs["constraints"] += [{"artifact-language": "English"}, {"fix": "fix.md"}]
        self.write_json(call_at("0001"), ccs)
        self.kept()
        # When: the orchestrator keeps a decision of t1.
        out = self.decide()
        # Then: a new call on t1.1 carries its decisions alone, the one of the same title replaced.
        want = {
            "focal_entities": [{"work": "t1.1"}, {"stage": "design"}],
            "constraints": [{"decision": "License: MIT"}, {"decision": "Form: a page"}],
        }
        self.assertEqual((out["call"], self.read_json(call_at("0002"))), ("0002", want))

    def test_a_title_holding_a_colon_and_a_blank_stops(self):
        # Given: a session.
        # When: the orchestrator keeps a decision whose title holds `: `.
        out = self.stopped("decide", "t1.1", "--title", "A: B", "--says", "x", "--message", "m")
        # Then: rn says why, and to give the title without it.
        self.assertIn(
            "rn: the title 'A: B' holds `: `, which parts a decision's title from what it says;"
            " give the title without it",
            out,
        )

    def test_an_empty_value_stops(self):
        for option, words in (
            ("--title", "title"),
            ("--says", "decision"),
            ("--message", "message"),
        ):
            with self.subTest(option=option):
                # Given: a session.
                values = {"--title": "License", "--says": "MIT", "--message": "m", option: " "}
                # When: the orchestrator keeps a decision with a value of blanks.
                # Then: rn says it is empty.
                self.assertIn(
                    f"rn: the {words} is empty; give it in words",
                    self.stopped("decide", "t1.1", *options(values)),
                )

    def test_a_work_rn_does_not_make_stops(self):
        for work in ("readme", "t", "tx", "t1", "t1.", "T1.1", "checklist-", "plans"):
            with self.subTest(work=work):
                # Given: a session.
                # When: the orchestrator keeps a decision of a work rn does not make.
                out = self.stopped("decide", work, "--title", "A", "--says", "B", "--message", "m")
                # Then: rn names the works it makes.
                self.assertIn(
                    f"rn: the work {work!r} is none rn makes; give plan, learnings, deliverable,"
                    " t<n>.<k> for action k of task T<n>, checklist-<kind>, or issue-<n> for the"
                    " issue n to rn's makers, such as t1.2",
                    out,
                )

    def test_each_work_rn_makes_is_taken(self):
        for work in ("plan", "learnings", "deliverable", "t1.4", "checklist-code"):
            with self.subTest(work=work):
                # Given: a session.
                # When: the orchestrator keeps a decision of a work rn makes.
                # Then: it is kept in a call on it.
                number = self.decide(work)["call"]
                self.assertEqual(
                    self.read_json(call_at(number))["focal_entities"][0], {"work": work}
                )

    def test_a_decision_of_an_action_the_steering_does_not_hold_stops(self):
        for work in ("t3.1", "t1.5"):
            with self.subTest(work=work):
                # Given: a session whose T1 has four actions.
                # When: the orchestrator keeps a decision of an action it does not hold.
                out = self.stopped("decide", work, "--title", "A", "--says", "B", "--message", "m")
                # Then: rn names it, and says how a task's work is given.
                self.assertIn(f"rn: the steering holds no action {work.upper()} of turn's", out)

    def test_a_ccs_that_is_no_json_object_stops(self):
        for text in ("{", "[]"):
            with self.subTest(text=text):
                # Given: a call whose CCS is no JSON object.
                self.write(call_at("0001"), text)
                # When: the orchestrator keeps a decision.
                # Then: rn names it and says how to restore it.
                self.assertIn(
                    f"rn: {call_at('0001')} is no CCS, a JSON object; restore it with `git checkout"
                    f" HEAD -- {call_at('0001')}`, as rn's scripts alone write it, then run this"
                    " again",
                    self.stopped("decide", "t1.1", "--title", "A", "--says", "B", "--message", "m"),
                )

    def test_a_decision_without_a_session_stops(self):
        # Given: a branch holding no session.
        self.git("checkout", "-q", "-b", "other", "main")
        # When: the orchestrator keeps a decision.
        # Then: rn says there is none.
        self.assertIn(
            "holds no session",
            self.stopped("decide", "t1.1", "--title", "A", "--says", "B", "--message", "m"),
        )


class CcsTest(RepoTest):
    """Each work handed to turn as a CCS."""

    def setUp(self) -> None:
        super().setUp()
        tasks = f"{task()}\n\n{task('T2', 'G1 and AC2')}"
        self.session(steered(part=plan(tasks=tasks), stage="design"))

    def ccs(self, work: str = "t1.1", *paths: str, **more: str) -> Any:
        """The CCS of the work written, with the paths given, README.md where none is, and the
        options needed; gives the call."""
        given = paths or (
            ("README.md",) if work not in ("plan", "learnings", "deliverable") else ()
        )
        return self.ran("ccs", work, *given, *options({**NEEDED, **more}))

    def test_ccs_gives_the_call_to_hand_turn(self):
        # Given: a session.
        # When: the orchestrator has the CCS of t1.1 written.
        # Then: rn gives the call to turn:up: the CCS, the key of each role turn reads from it,
        # where the result goes, of the first call, and no test, given as null.
        # The keys are written out as turn is to read them, not taken from rn.py, so a change to
        # them in rn.py by mistake fails the test; the duplicate-code check leaves them out, as the
        # user chose.
        # pylint: disable=duplicate-code
        want = {
            "ccs": call_at("0001"),
            "kind": {
                "work": "path",
                "checklist": "checklist",
                "receiver": "audience",
                "use": "purpose",
                "has": "has",
            },
            "result": call_at("0001", "result.json"),
            "test": None,
        }
        # pylint: enable=duplicate-code
        self.assertEqual(self.ccs(), want)

    def test_ccs_keeps_the_call_before_turn_is_handed_it(self):
        # Given: a session.
        # When: the orchestrator has the CCS of the plan written.
        self.ccs("plan")
        # Then: the CCS and the part are committed and pushed with a message naming the call, and
        # nothing is left to keep, so a conversation cut while turn runs goes on from them.
        kept = (
            sorted(self.out("show", "--name-only", "--format=", "origin/work").split()),
            self.out("log", "-1", "--format=%s", "origin/work").strip(),
            self.head(),
            self.out("status", "--porcelain"),
        )
        want = (
            [call_at("0001"), call_at("0001", "steering.md")],
            "Call 0001 on plan: handed to turn",
            self.head("origin/work"),
            "",
        )
        self.assertEqual(kept, want)

    def test_ccs_made_again_the_same_keeps_nothing_more(self):
        # Given: the call on t1.1 kept, turn not yet returned.
        self.ccs()
        before = self.head()
        # When: the orchestrator has the same CCS written again, as a fresh conversation does.
        out = self.ccs()
        # Then: the same call is given, and no commit is made.
        self.assertEqual((out["ccs"], self.head()), (call_at("0001"), before))

    def test_turns_files_at_the_root_are_kept_with_the_move(self):
        # Given: the call on t1.1 kept, and the state turn keeps in its folder at the root while it
        # runs
        self.ccs()
        self.write(".turn/20261025-result.json/run.json", "x\n")
        # When: the orchestrator keeps a decision while turn asks
        self.ran("decide", "t1.1", "--title", "Login", "--says", "email", "--message", "Login")
        # Then: the decision's commit holds the CCS and turn's state, as git keeps what the user's
        # .gitignore does not name, and nothing is left
        changed = self.out("show", "--name-only", "--format=", "HEAD").split()
        left = self.out("status", "--porcelain", "-uall")
        self.assertEqual(
            (changed, left), ([call_at("0001"), ".turn/20261025-result.json/run.json"], "")
        )

    def test_turns_files_named_by_gitignore_are_no_change_to_keep(self):
        # Given: a .gitignore naming turn's folder, kept, the call on t1.1 kept, and the state turn
        # keeps there while it runs
        self.write(".gitignore", ".turn/\n")
        self.commit_with("ignore turn's folder")
        self.ccs()
        self.write(".turn/20261025-result.json/run.json", "x\n")
        before = self.head()
        # When: the orchestrator has the CCS written again, as a fresh conversation does
        out = self.ccs()
        # Then: it does not stop, gives the same call, and keeps nothing
        self.assertEqual((out["ccs"], self.head()), (call_at("0001"), before))

    def test_the_ccs_of_a_task_holds_what_its_task_serves(self):
        # Given: a session whose T1 serves AC1.
        # When: the orchestrator has the CCS of t1.1 written, with a path the receiver has.
        self.ran("ccs", "t1.1", "README.md", *options(NEEDED))
        # Then: it holds the work, the stage, the path, the receiver and what they have; the use
        # and the criterion T1 serves as text; the checklists; and the languages and the fix.
        want = {
            "focal_entities": [
                {"work": "t1.1"},
                {"stage": "design"},
                {"kind": "code"},
                {"path": "README.md"},
                {"audience": "a new user"},
                {"has": "."},
            ],
            "goal_orientation": [
                {"purpose": "to try it"},
                {"serves": "AC1: A user signs in with their email."},
            ],
            "retrieved_artifacts": [{"checklist": self.checklist}],
            "constraints": [
                {"artifact-language": "English"},
                {"conversation-language": "Japanese"},
                {"fix": self.fix},
            ],
        }
        self.assertEqual(self.read_json(call_at("0001")), want)

    def test_the_ccs_of_a_task_serving_the_goal_holds_the_goal(self):
        # Given: a session whose T2 serves G1 and AC2.
        # When: the orchestrator has the CCS of t2.1 written.
        self.ccs("t2.1")
        # Then: it holds the goal and AC2, each as one line.
        self.assertEqual(
            self.read_json(call_at("0001"))["goal_orientation"][1:],
            [
                {"serves": "G1: Users sign in, so their carts stay theirs."},
                {"serves": "AC2: A signed-in user sees only their cart, on every page."},
            ],
        )

    def test_the_ccs_of_the_plan_serves_nothing_and_has_what_each_task_done_made(self):
        # Given: a session holding T1 and T2, with calls on T3, done, not returned, on T1, on T4,
        # done, not returned, and on T3 again, returned.
        self.call("0001", "t3.1")
        self.call("0002", "t1.1", result={})
        self.call("0003", "t4.1")
        self.call("0004", "t3.1", result={})
        self.kept()
        # When: the orchestrator has the CCS of the plan written, with a path the receiver has.
        self.ccs("plan", **{"--has": "README.md"})
        # Then: it serves nothing, and has the path given, then, in the order made, the latest
        # call of each work of a task done, which holds what the work served and decided and the
        # files it made, returned or not, and none of turn's results.
        ccs = self.read_json(call_at("0005"))
        has = [e for e in ccs["focal_entities"] if "has" in e]
        want = (
            [{"purpose": "to try it"}],
            [{"has": "README.md"}, {"has": call_at("0003")}, {"has": call_at("0004")}],
        )
        self.assertEqual((ccs["goal_orientation"], has), want)

    def test_the_ccs_of_the_finished_work_and_of_a_task_has_nothing_of_the_tasks_done(self):
        # Given: a session holding T1 and T2, with a call on T3, done, returned.
        self.call("0001", "t3.1", result={})
        self.kept()
        # When: the orchestrator has the CCS of the finished work written, then of t1.
        made = [self.ccs(work, "README.md")["ccs"] for work in ("deliverable", "t1.1")]
        # Then: each has what was given alone.
        has = [[e for e in self.read_json(p)["focal_entities"] if "has" in e] for p in made]
        self.assertEqual(has, [[{"has": "."}], [{"has": "."}]])

    def test_the_ccs_of_a_checklist_or_the_learnings_serves_nothing(self):
        for work, paths in (("checklist-code", (".rn/checklists/code.md",)), ("learnings", ())):
            with self.subTest(work=work):
                # Given: a session.
                # When: the orchestrator has the CCS of a checklist, or of the learnings, written.
                made = self.ccs(work, *paths)["ccs"]
                # Then: it holds the use alone, as neither serves the user's work.
                self.assertEqual(
                    self.read_json(made)["goal_orientation"], [{"purpose": "to try it"}]
                )

    def test_the_ccs_of_the_finished_work_holds_the_goal_and_every_criterion(self):
        # Given: a session.
        # When: the orchestrator has the CCS of the finished work written.
        self.ccs("deliverable", "README.md")
        # Then: it holds the goal and every criterion.
        self.assertEqual(
            self.read_json(call_at("0001"))["goal_orientation"],
            [
                {"purpose": "to try it"},
                {"serves": "G1: Users sign in, so their carts stay theirs."},
                {"serves": "AC1: A user signs in with their email."},
                {"serves": "AC2: A signed-in user sees only their cart, on every page."},
            ],
        )

    def test_the_ccs_of_an_action_the_steering_does_not_hold_stops(self):
        for work in ("t0.1", "t3.1", "t1.5"):
            with self.subTest(work=work):
                # Given: a session with T1 and T2, each of four actions.
                # When: the orchestrator has the CCS of an action not held written.
                # Then: rn says there is no such action of turn's, and how a task's work is given.
                self.assertIn(
                    f"rn: the steering holds no action {work.upper()} of turn's, which the work"
                    f" {work} is; give the work of an action turn makes as t<n>.<action>, such as"
                    " t1.2, or have turn make the plan again with it, keep it, then run this again",
                    self.stopped("ccs", work, "README.md", *options(NEEDED)),
                )

    def test_the_ccs_of_an_action_of_the_orchestrators_stops(self):
        # Given: a session whose T1's first action is the orchestrator's.
        orchestrators = "Settle part 1 of T1. The orchestrator, with the user."
        tasks = task().replace(
            "Make part 1 of T1, `src/t1-1.py` as a code work. turn.", orchestrators
        )
        self.session(steered(part=plan(tasks=tasks), stage="design"))
        # When: the orchestrator has the CCS of that action written.
        # Then: rn says the steering holds no such action of turn's.
        self.assertIn(
            "rn: the steering holds no action T1.1 of turn's, which the work t1.1 is",
            self.stopped("ccs", "t1.1", "README.md", *options(NEEDED)),
        )

    def test_the_ccs_of_an_action_names_the_path_and_the_kind_it_names(self):
        # Given: a session whose T1's second action makes `src/t1-2.py` as a code work.
        # When: the orchestrator has its CCS written with no path and no kind.
        self.ran("ccs", "t1.2", *options(NEEDED))
        # Then: it holds that path, and the checklists of that kind.
        ccs = self.read_json(call_at("0001"))
        self.assertEqual(
            (ccs["focal_entities"][3], ccs["retrieved_artifacts"]),
            ({"path": "src/t1-2.py"}, [{"checklist": self.checklist}]),
        )

    def test_the_call_of_a_tasks_last_action_of_turns_tests_its_result(self):
        # Given: a session whose T1's check is a command, its last action, the fourth, turn's.
        tasks = task(test="sh dev/check.sh")
        self.session(steered(part=plan(tasks=tasks), stage="build"))
        # When: the orchestrator has the CCS of each of its actions written.
        tests = [self.ccs(f"t1.{k}")["test"] for k in (1, 2, 3, 4)]
        # Then: the call of the last gives turn that command, which checks the result it makes,
        # and those before it none, as they make the check and see it fail.
        self.assertEqual(tests, [None, None, None, "sh dev/check.sh"])

    def test_the_call_of_a_task_with_no_command_or_of_another_work_tests_nothing(self):
        # Given: a session whose T1 gives no command that checks its result.
        # When: the orchestrator has the CCS of T1's last action written, and of the finished work.
        tests = [self.ccs(work, "README.md")["test"] for work in ("t1.4", "deliverable")]
        # Then: neither gives turn a command.
        self.assertEqual(tests, [None, None])

    def test_each_work_rn_makes_itself_is_made_with_its_own_kind_receiver_use_and_had(self):
        root = os.path.realpath(self.plugin)
        cases = {
            "plan": (
                [call_at("0001", "steering.md")],
                "plan",
                "the user at the plan sign-off",
                ".",
            ),
            "deliverable": (["src/app.py"], "deliverable", "the user at the deliverable", "."),
            "checklist-api": ([".rn/checklists/api.md"], "checklist", "whoever makes an api", "."),
            "issue-1": ([f"{FOLDER}/issue-1.md"], "issue", "rn's makers", root),
        }
        self.write("src/app.py", "x\n")
        self.kept()
        for work, (paths, kind, receiver, has) in cases.items():
            with self.subTest(work=work):
                # Given: a session, and a file the branch changed.
                # When: the orchestrator has the work's CCS written, giving nothing more.
                written = self.read_json(self.ran("ccs", work)["ccs"])
                entities = written["focal_entities"]
                # Then: it holds the paths, the kind and its checklist, the receiver, their use and
                # what they have, as rn makes that work every time.
                self.assertEqual(
                    (
                        [e["path"] for e in entities if "path" in e],
                        next(e["kind"] for e in entities if "kind" in e),
                        written["retrieved_artifacts"][0],
                        next(e["audience"] for e in entities if "audience" in e).startswith(
                            receiver
                        ),
                        bool(written["goal_orientation"][0]["purpose"]),
                        [e["has"] for e in entities if "has" in e],
                    ),
                    (paths, kind, {"checklist": self.own[kind]}, True, True, [has]),
                )

    def test_a_work_made_again_takes_what_its_last_call_named(self):
        # Given: the call on t1.2 made with a receiver, a use and what they have, and returned.
        self.ran("ccs", "t1.2", "--receiver", "a new user", "--use", "to try it", "--has", ".")
        self.write_json(call_at("0001", "result.json"), {})
        self.kept()
        # When: the orchestrator has its CCS written again, giving nothing more.
        out = self.ran("ccs", "t1.2")
        # Then: a new call names the same, its stage now.
        before, now = (self.read_json(call_at(n)) for n in ("0001", "0002"))
        self.assertEqual((out["ccs"], now), (call_at("0002"), before))

    def test_a_work_with_no_receiver_use_or_had_given_or_kept_stops(self):
        for left, option in (("receiver", "--receiver"), ("use", "--use"), ("has", "--has")):
            with self.subTest(left=left):
                # Given: a session with no call on t1.2.
                given = {"--receiver": "r", "--use": "u", "--has": "."}
                del given[option]
                # When: the orchestrator has its CCS written without one of them.
                out = self.stopped("ccs", "t1.2", *options(given))
                # Then: rn says none is given or kept, and to give it.
                self.assertIn(
                    f"rn: no {left} of the work t1.2 is given, and no call on it names one; give"
                    f" it with {option}",
                    out,
                )

    def test_the_plan_is_cut_into_its_part_and_handed_as_the_work(self):
        # Given: a session.
        # When: the orchestrator has the CCS of the plan written.
        self.ccs("plan")
        # Then: the part from the title through the tasks is cut into the call's part, the work
        # the CCS names.
        part = call_at("0001", "steering.md")
        tasks = f"{task()}\n\n{task('T2', 'G1 and AC2')}"
        self.assertEqual(
            (self.read(part), self.read_json(call_at("0001"))["focal_entities"][3]),
            (plan(tasks=tasks) + "\n", {"path": part}),
        )

    def test_the_learnings_are_cut_into_a_part_of_their_name_with_none_of_those_kept(self):
        # Given: a session with a learning kept.
        self.write(LEARNINGS, "- L1: Kept.\n")
        self.kept()
        # When: the orchestrator has the CCS of the learnings written.
        self.ccs("learnings")
        # Then: the part is empty, as the form of rn's learnings checklist holds no heading, the
        # work the CCS names.
        part = call_at("0001", "learnings.md")
        self.assertEqual(
            (self.read(part), self.read_json(call_at("0001"))["focal_entities"][3]),
            ("", {"path": part}),
        )

    def test_a_path_given_for_a_part_rn_cuts_stops(self):
        for work in ("plan", "learnings"):
            with self.subTest(work=work):
                # Given: a session.
                # When: the orchestrator has the CCS of the plan or the learnings written with a
                # path.
                # Then: rn says it is a part rn cuts.
                self.assertIn(
                    f"rn: the work {work} is a part rn cuts for turn from the session's record;"
                    " give no path of it",
                    self.stopped("ccs", work, "README.md", *options(NEEDED)),
                )

    def test_the_ccs_of_a_checklist_names_rns_usability_after_its_checklists(self):
        # Given: rn's checklist for checklists.
        # When: the orchestrator has the CCS of a checklist written.
        self.ran("ccs", "checklist-code")
        # Then: it names rn's usability.md after the checklists.
        self.assertEqual(
            self.read_json(call_at("0001"))["retrieved_artifacts"],
            [{"checklist": self.own["checklist"]}, {"source": self.usability}],
        )

    def test_the_ccs_of_another_kind_names_its_checklists_alone(self):
        for kind in ("architecture", KIND):
            with self.subTest(kind=kind):
                # Given: rn's checklist of the kind, and a task whose first action makes a work of
                # it.
                checklist = os.path.join(self.plugin, "checklists", "product", f"{kind}.md")
                self.write(checklist, "# A kind\n")
                made = task().replace("as a code work", f"as a {kind} work", 1)
                self.session(steered(part=plan(tasks=made), stage="design"))
                # When: the orchestrator has the CCS of that action written.
                written = self.ccs("t1.1")["ccs"]
                # Then: it names the kind's checklist alone.
                found = self.read_json(written)["retrieved_artifacts"]
                self.assertEqual(found, [{"checklist": checklist}])

    def test_the_decisions_of_the_latest_call_not_returned_are_kept(self):
        # Given: a call on t1.1 holding a decision, not returned.
        self.call("0001", "t1.1", decisions=("License: MIT",))
        self.kept()
        # When: the orchestrator has its CCS written.
        out = self.ccs()
        # Then: the same call is filled, its decision first among the constraints.
        self.assertEqual(
            (out["ccs"], self.read_json(call_at("0001"))["constraints"][0]),
            (call_at("0001"), {"decision": "License: MIT"}),
        )

    def test_a_call_returned_is_made_again_as_a_new_call_carrying_its_decisions(self):
        # Given: a call on t1.1 holding a decision, returned, and a call on t2.
        self.call("0001", "t1.1", decisions=("License: MIT",), result={})
        self.call("0002", "t2.1")
        self.kept()
        # When: the orchestrator has t1.1's CCS written.
        out = self.ccs()
        # Then: a new call is filled, carrying the decision.
        self.assertEqual(
            (out["ccs"], self.read_json(call_at("0003"))["constraints"][0]),
            (call_at("0003"), {"decision": "License: MIT"}),
        )

    def test_the_finished_work_is_every_file_the_branch_changed_outside_rn(self):
        # Given: two files the branch changed outside .rn/, and one it removed.
        self.write("src/app.py", "x\n")
        os.remove("README.md")
        self.git("rm", "-q", "--cached", "README.md")
        self.kept()
        # When: the orchestrator has the finished work's CCS written with no path.
        self.ccs("deliverable")
        # Then: the work is the file changed outside .rn/ and there.
        works = [e for e in self.read_json(call_at("0001"))["focal_entities"] if "path" in e]
        self.assertEqual(works, [{"path": "src/app.py"}])

    def test_the_finished_work_given_paths_is_those_paths(self):
        # Given: a file the branch changed.
        self.write("src/app.py", "x\n")
        self.kept()
        # When: the orchestrator has the finished work's CCS written with a path.
        self.ccs("deliverable", "README.md")
        # Then: the work is that path.
        works = [e for e in self.read_json(call_at("0001"))["focal_entities"] if "path" in e]
        self.assertEqual(works, [{"path": "README.md"}])

    def test_the_finished_work_with_no_file_changed_stops(self):
        # Given: a branch that changed nothing outside .rn/.
        # When: the orchestrator has the finished work's CCS written with no path.
        # Then: rn says there is none, and what to do.
        self.assertIn(
            "rn: the branch changed no file outside .rn/ since it left origin/main",
            self.stopped("ccs", "deliverable", *options(NEEDED)),
        )

    def test_ccs_is_written_one_key_to_a_line_with_text_beyond_ascii_as_it_is(self):
        # Given: a session.
        # When: the orchestrator has a CCS written with a receiver in Japanese.
        self.ccs(**{"--receiver": "新しい利用者"})
        # Then: it is written one key or value to a line, the Japanese as it is.
        text = self.read(call_at("0001"))
        self.assertEqual(
            (
                text.startswith('{\n "focal_entities": [\n  {\n   "work": "t1.1"'),
                "新しい利用者" in text,
            ),
            (True, True),
        )

    def test_ccs_with_the_record_not_kept_stops(self):
        # Given: a change not kept.
        self.write("notes.md", "x\n")
        self.write("README.md", "# app, changed\n")
        # When: the orchestrator has a CCS written.
        # Then: rn names the changes and says to keep the move first.
        self.assertIn(
            "rn: the record has changes not kept, README.md, notes.md; rn goes on only from what is"
            " pushed, so keep the move with `rn.py state --next <n> --message <what it brought>`"
            " first",
            self.stopped("ccs", "t1.1", "README.md", *options(NEEDED)),
        )

    def test_ccs_with_commits_not_pushed_stops(self):
        # Given: a commit not pushed.
        self.git("commit", "-q", "--allow-empty", "-m", "c")
        # When: the orchestrator has a CCS written.
        # Then: rn says to push first.
        self.assertIn(
            "rn: the branch has 1 commit(s) not pushed; push with `git push`",
            self.stopped("ccs", "t1.1", "README.md", *options(NEEDED)),
        )

    def test_ccs_on_a_branch_never_pushed_stops(self):
        # Given: a branch never pushed.
        self.git("checkout", "-q", "-b", "lone")
        # When: the orchestrator has a CCS written.
        # Then: rn says to push the branch.
        self.assertIn(
            "push the branch with `git push -u origin HEAD`",
            self.stopped("ccs", "t1.1", "README.md", *options(NEEDED)),
        )

    def test_ccs_with_what_the_receiver_has_not_there_stops(self):
        # Given: a session.
        self.kept()
        # When: the orchestrator has a CCS written naming a path not there as what the receiver
        # has.
        # Then: rn says it is not there.
        self.assertIn(
            "rn: what the receiver has, none.md, is not there",
            self.stopped("ccs", "t1.1", "README.md", *options(NEEDED), "--has", "none.md"),
        )

    def test_an_empty_or_wrong_value_stops(self):
        self.kept()
        for work, paths, given, said in (
            ("t1.1", ["README.md"], {"--receiver": " "}, "rn: the receiver is empty"),
            ("t1.1", ["README.md"], {"--use": " "}, "rn: the use is empty"),
            ("t1.1", [" "], {}, "rn: the path of the work is empty"),
            ("readme", ["README.md"], {}, "rn: the work 'readme' is none rn makes"),
        ):
            with self.subTest(said=said):
                # Given: a session.
                # When: the orchestrator has a CCS written with a value it does not take.
                # Then: rn names it.
                argv = [work, *paths, *options({**NEEDED, **given})]
                self.assertIn(said, self.stopped("ccs", *argv))

    def test_a_ccs_that_cannot_be_written_writes_nothing(self):
        for work in ("plan", "learnings"):
            with self.subTest(work=work):
                # Given: a session, and rn's checklist of the work's kind not there.
                os.remove(self.own[work])
                # When: the orchestrator has the CCS of the work, a part rn cuts, written.
                out = self.stopped("ccs", work)
                # Then: rn says there is no checklist for it, and writes nothing.
                self.assertEqual(
                    (f"no checklist for the kind {work}" in out, self.out("status", "-s")),
                    (True, ""),
                )

    def test_ccs_below_the_top_stops(self):
        # Given: rn run below the top.
        os.makedirs("src")
        os.chdir("src")
        # When: the orchestrator has a CCS written.
        # Then: rn says to run it from the top.
        self.assertIn("below the top", self.stopped("ccs", "t1.1", "README.md", *options(NEEDED)))


class DecisionsTest(RepoTest):
    """Each decision of a work, as its latest call keeps it."""

    def setUp(self) -> None:
        super().setUp()
        self.session(steered(stage="design"))

    def test_the_decisions_of_a_works_latest_call_are_given(self):
        # Given: a call on t1.1 returned, and one made again with a decision changed and one added.
        self.call("0001", "t1.1", decisions=("A: B",), result={})
        self.call("0002", "t1.1", decisions=("A: C", "D: E"))
        self.kept()
        # When: the orchestrator asks for t1.1's decisions.
        # Then: rn gives those of the latest call, with its number.
        self.assertEqual(
            self.ran("decisions", "t1.1"),
            {"work": "t1.1", "call": "0002", "decisions": ["A: C", "D: E"]},
        )

    def test_a_work_never_called_has_no_decisions(self):
        # Given: a session with no call on t1.2.
        # When: the orchestrator asks for its decisions.
        # Then: rn gives no call and no decision.
        self.assertEqual(
            self.ran("decisions", "t1.2"), {"work": "t1.2", "call": None, "decisions": []}
        )

    def test_the_decisions_of_a_work_rn_does_not_make_stop(self):
        # Given: a session.
        # When: the orchestrator asks for the decisions of a work rn does not make.
        # Then: rn names the works it makes.
        self.assertIn("rn: the work 'readme' is none rn makes", self.stopped("decisions", "readme"))


class ChecklistsTest(RepoTest):
    def test_rns_own_checklist_is_found_in_a_folder_of_rns_checklists(self):
        # Given: rn's checklist for the kind, in a folder of rn's checklists.
        # When: the orchestrator asks for the kind's checklists.
        # Then: rn gives it.
        self.assertEqual(self.ran("checklists", KIND), [self.checklist])

    def test_rns_own_checklist_is_found_straight_in_its_folder(self):
        # Given: rn's checklist for checklists, straight in rn's checklists.
        checklist = os.path.join(self.plugin, "checklists", "checklist.md")
        self.write(checklist, "# Checklist\n")
        # When: the orchestrator asks for its checklists.
        # Then: rn gives it.
        self.assertEqual(self.ran("checklists", "checklist"), [checklist])

    def test_the_users_addition_comes_after_rns_own(self):
        # Given: the user's addition for the kind.
        self.write(f"{RECORD}/checklists/{KIND}.md", "# Ours\n")
        # When: the orchestrator asks for the kind's checklists.
        # Then: rn gives its own, then the user's.
        self.assertEqual(
            self.ran("checklists", KIND), [self.checklist, f"{RECORD}/checklists/{KIND}.md"]
        )

    def test_the_users_addition_alone_is_the_whole_checklist(self):
        # Given: the user's checklist for a kind rn has none of.
        self.write(f"{RECORD}/checklists/api.md", "# API\n")
        # When: the orchestrator asks for its checklists.
        # Then: rn gives the user's.
        self.assertEqual(self.ran("checklists", "api"), [f"{RECORD}/checklists/api.md"])

    def test_a_kind_without_checklists_stops(self):
        # Given: a kind with no checklist.
        # When: the orchestrator asks for its checklists.
        # Then: rn says there is none and how to make one.
        self.assertIn(
            "rn: there is no checklist for the kind api, neither rn's nor .rn/checklists/api.md;"
            " make .rn/checklists/api.md first",
            self.stopped("checklists", "api"),
        )

    def test_a_kind_of_other_characters_stops(self):
        # Given: a kind with a character other than lowercase letters, digits and hyphens.
        # When: the orchestrator asks for its checklists.
        # Then: rn says what a kind holds.
        self.assertIn("the kind '../x' is not", self.stopped("checklists", "../x"))


if __name__ == "__main__":
    unittest.main()
