"""The tests of each work's call: each decision kept in it, what the record settles of its CCS, the
compressor's reply put in, the CCS written for it, handed to turn or cut for the orchestrator to
write, and the checklists of a kind."""

from __future__ import annotations

import json
import os
import shutil
import unittest
from typing import Any
from unittest import mock

from helpers import (
    FOLDER,
    KIND,
    LEARNINGS,
    MARKDOWN,
    PLAN_CHECKLIST,
    RECORD,
    STEERING,
    RepoTest,
    call_at,
    ccs,
    items,
    json_text,
    plan,
    steered,
    task,
)

# A checklist of four questions, as rn's checklists are made: Q-2 and Q-4 the questions a test tells
# rn are judged on the built product, Q-2 between two others, holding a fence with a heading in it
# and a lower heading after it, and Q-4 the last, its heading right under the line before it; Q-1
# and Q-3 judged before it is built; and a Format whose template holds a heading in its fence.
BUILT_ITEMS = """# Code

The opening.

## Format

```markdown
### Not a question
```

## Questions

### Q-1: Read

Why: read.

### Q-2: Run

```markdown
## Not a heading
```

#### More of it

Why: run.

### Q-3: Said

Why: said.
### Q-4: Run again

Why: run again.
"""
BUILT = ("Q-2", "Q-4")
# The checklist above as a call before the build names it: every line but those questions.
WITHOUT_BUILT = """# Code

The opening.

## Format

```markdown
### Not a question
```

## Questions

### Q-1: Read

Why: read.

### Q-3: Said

Why: said.
"""


# rn's own checklists, which the tables of ccs.py tell of.
CHECKLISTS = os.path.dirname(os.path.dirname(PLAN_CHECKLIST))


# What the compressor gives of a task's CCS before the build, each role with a value and why, and
# from the build on, with the receiver, their use and what they have too.
GIVEN_BEFORE = (
    ("work", "docs/login.md", "The plan's decision: Login document: docs/login.md"),
    ("kind", KIND, "The architecture: docs are code here"),
    ("test", None, "The architecture names no command"),
)
GIVEN_BUILT = (
    ("work", "src/login.py", "docs/architecture.md:12, the login lives in src/"),
    ("kind", KIND, "docs/architecture.md:12, it is code"),
    ("receiver", "a new user", "docs/ux.md:3, who signs in"),
    ("use", "signing in", "docs/ux.md:4, what they do"),
    ("has", "README.md", "docs/ux.md:5, they read the README"),
    ("test", "sh dev/check.sh", "docs/architecture.md:40, the project's check"),
)


def reply(*given: tuple[str, Any, str]) -> str:
    """The compressor's reply giving each role with its value and why."""
    return json.dumps({"given": [{"role": r, "value": v, "why": w} for r, v, w in given]})


def without(given: tuple[tuple[str, Any, str], ...], role: str) -> tuple[Any, ...]:
    """The roles given but the one named."""
    return tuple(g for g in given if g[0] != role)


class DecideTest(RepoTest):
    """Each answer kept as a decision of the work it settles, in that work's call."""

    def setUp(self) -> None:
        super().setUp()
        self.session(steered(part=plan(tasks=[task(), task("T2")]), stage="architecture"))

    def decide(self, work: str = "t1", title: str = "License", says: str = "MIT") -> Any:
        """Keeps the decision of the work, with its title and what it says."""
        return self.ran("decide", work, "--title", title, "--says", says, "--message", "t1: MIT")

    def test_a_first_decision_is_written_into_the_works_first_call_committing_nothing(self):
        # Given: a session with no call.
        before = self.head()
        # When: the orchestrator keeps a decision of the work t1.
        out = self.decide()
        # Then: the first call holds the work, the stage, and the decision, written and not
        # committed, as the step it belongs to commits it as it ends; the step's commit then holds
        # the call, with the decision's message after its own.
        want = {
            "focal_entities": [{"work": "t1"}, {"stage": "architecture"}],
            "constraints": [{"decision": "License: MIT"}],
        }
        written = (out, self.read_json(call_at("0001")), self.head())
        self.ran("state", "--message", "The step ends")
        kept = (
            json.loads(self.out("show", f"origin/work:{call_at('0001')}")),
            self.out("log", "-1", "--format=%B", "origin/work"),
        )
        self.assertEqual(
            (written, kept),
            (({"call": "0001"}, want, before), (want, "The step ends\n\nt1: MIT\n\n")),
        )

    def test_a_decision_goes_into_the_works_latest_call_not_returned(self):
        # Given: a call on t1 and one on t2, neither returned, kept.
        self.call("0001", "t1", decisions=("Form: a page",))
        self.call("0002", "t2")
        self.kept()
        # When: the orchestrator keeps a decision of t1.
        out = self.decide()
        # Then: it is added to t1's call.
        self.assertEqual(
            (out["call"], self.read_json(call_at("0001"))["constraints"]),
            ("0001", [{"decision": "Form: a page"}, {"decision": "License: MIT"}]),
        )

    def test_a_decision_of_the_same_title_is_replaced_where_it_stands(self):
        # Given: a call on t1 with two decisions.
        self.call("0001", "t1", decisions=("License: Apache-2.0", "Form: a page"))
        self.kept()
        # When: the orchestrator keeps a decision of the first's title.
        self.decide()
        # Then: it replaces the first, where it stood.
        self.assertEqual(
            self.read_json(call_at("0001"))["constraints"],
            [{"decision": "License: MIT"}, {"decision": "Form: a page"}],
        )

    def test_a_decision_after_turn_returned_makes_a_new_call_carrying_the_decisions(self):
        # Given: a call on t1 returned, with its decisions, the languages and the fix.
        self.call("0001", "t1", decisions=("License: Apache-2.0", "Form: a page"), result={})
        ccs = self.read_json(call_at("0001"))
        ccs["constraints"] += [{"artifact-language": "English"}, {"fix": "fix.md"}]
        self.write_json(call_at("0001"), ccs)
        self.kept()
        # When: the orchestrator keeps a decision of t1.
        out = self.decide()
        # Then: a new call on t1 carries its decisions alone, the one of the same title replaced.
        want = {
            "focal_entities": [{"work": "t1"}, {"stage": "architecture"}],
            "constraints": [{"decision": "License: MIT"}, {"decision": "Form: a page"}],
        }
        self.assertEqual((out["call"], self.read_json(call_at("0002"))), ("0002", want))

    def test_a_decision_after_turn_returned_carries_the_choices_of_the_call_before(self):
        # Given: a call on t1 returned, holding a decision and a choice of the compressor's.
        self.call("0001", "t1", decisions=("Form: a page",), result={})
        ccs = self.read_json(call_at("0001"))
        ccs["constraints"].append({"chosen": "The receiver has docs/brand.md: the flow names it"})
        self.write_json(call_at("0001"), ccs)
        self.kept()
        # When: the orchestrator keeps a decision of t1.
        self.decide()
        # Then: the new call carries the decision and the choice, then the new decision.
        self.assertEqual(
            self.read_json(call_at("0002"))["constraints"],
            [
                {"decision": "Form: a page"},
                {"chosen": "The receiver has docs/brand.md: the flow names it"},
                {"decision": "License: MIT"},
            ],
        )

    def test_a_decision_of_a_part_after_it_is_cut_makes_a_new_call_carrying_the_decisions(self):
        for work, number, new, part in (
            ("plan", "0001", "0002", plan()),
            ("learnings", "0003", "0004", ""),
        ):
            with self.subTest(work=work):
                # Given: a call on the plan or the learnings with a decision, its part cut for the
                # orchestrator to write, with no result of turn's.
                self.call(number, work, decisions=("License: Apache-2.0",), part=part)
                self.kept()
                # When: the orchestrator keeps a decision of it.
                out = self.decide(work)
                # Then: a new call on it carries the decisions, the one of the same title replaced,
                # as the orchestrator writes the part from its CCS as it stood when cut.
                self.assertEqual(
                    (out["call"], self.read_json(call_at(new))["constraints"]),
                    (new, [{"decision": "License: MIT"}]),
                )

    def test_a_title_holding_a_colon_and_a_blank_stops(self):
        # Given: a session.
        # When: the orchestrator keeps a decision whose title holds `: `.
        out = self.stopped("decide", "t1", "--title", "A: B", "--says", "x", "--message", "m")
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
                argv = [part for pair in values.items() for part in pair]
                # When: the orchestrator keeps a decision with a value of blanks.
                # Then: rn says it is empty.
                self.assertIn(
                    f"rn: the {words} is empty; give it in words",
                    self.stopped("decide", "t1", *argv),
                )

    def test_a_work_rn_does_not_make_stops(self):
        for work in ("readme", "t", "tx", "t1.1", "t1.", "T1", "checklist-", "plans", "issue-1"):
            with self.subTest(work=work):
                # Given: a session.
                # When: the orchestrator keeps a decision of a work rn does not make.
                out = self.stopped("decide", work, "--title", "A", "--says", "B", "--message", "m")
                # Then: rn names the works it makes.
                self.assertIn(
                    f"rn: the work {work!r} is none rn makes; give plan, learnings, deliverable,"
                    " t<n> for task T<n>, or checklist-<kind>, such as t1",
                    out,
                )

    def test_each_work_rn_makes_is_taken(self):
        for work in ("plan", "learnings", "deliverable", "t2", "checklist-code"):
            with self.subTest(work=work):
                # Given: a session.
                # When: the orchestrator keeps a decision of a work rn makes.
                # Then: it is kept in a call on it.
                number = self.decide(work)["call"]
                self.assertEqual(
                    self.read_json(call_at(number))["focal_entities"][0], {"work": work}
                )

    def test_a_decision_of_a_task_the_plan_does_not_hold_stops(self):
        for work in ("t3", "t0"):
            with self.subTest(work=work):
                # Given: a session whose plan holds T1 and T2.
                # When: the orchestrator keeps a decision of a task it does not hold.
                out = self.stopped("decide", work, "--title", "A", "--says", "B", "--message", "m")
                # Then: rn names it, and says how a task's result is given.
                self.assertIn(
                    f"rn: the plan holds no task T{work[1:]}, whose result the work {work} is;"
                    " give the work of a task the plan holds as t<n>, such as t1, or write the"
                    " plan again with it, keep it, then run this again",
                    out,
                )

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
                    self.stopped("decide", "t1", "--title", "A", "--says", "B", "--message", "m"),
                )

    def test_a_decision_without_a_session_stops(self):
        # Given: a branch holding no session.
        self.git("checkout", "-q", "-b", "other", "main")
        # When: the orchestrator keeps a decision.
        # Then: rn says there is none.
        self.assertIn(
            "holds no session",
            self.stopped("decide", "t1", "--title", "A", "--says", "B", "--message", "m"),
        )


class TaskTest(RepoTest):
    """A task's CCS: what the record settles, given the compressor first, and its reply put in."""

    def setUp(self) -> None:
        super().setUp()
        self.session(steered(part=plan(tasks=[task(), task("T2", ("AC2",))]), stage="architecture"))

    def handed(self, work: str = "t1", given: tuple[Any, ...] = GIVEN_BEFORE) -> Any:
        """The call to turn rn gives for the task's CCS written with the compressor's reply."""
        return self.ran("ccs", work, "--reply", reply(*given))

    def test_a_task_given_no_reply_gives_what_the_record_settles_for_the_compressor(self):
        # Given: a session at the architecture stage, a call on the plan, and T3 done.
        self.call("0001", "plan", decisions=("Login document: docs/login.md",), part=plan())
        self.call("0002", "t3", works=("docs/t3.md",), result={})
        self.kept()
        before = self.head()
        # When: the orchestrator asks for T1's CCS with no reply.
        out = self.ran("ccs", "t1")
        # Then: rn gives the work, what the record settles of its CCS, the roles the compressor
        # gives before the build, and the files it reads them from beside the repository, and
        # writes nothing.
        # The CCS's keys are written out as turn reads them, not taken from rn.py.
        # pylint: disable=duplicate-code
        want = {
            "work": "t1",
            "settled": {
                "focal_entities": [
                    {"work": "t1"},
                    {"stage": "architecture"},
                    {"kind": ""},
                    {
                        "audience": "the user approving it at the architecture sign-off, and"
                        " whoever builds the later works to it"
                    },
                    {"has": MARKDOWN},
                    {"has": "docs/t3.md"},
                ],
                "goal_orientation": [
                    {"purpose": "approving it, then building each later work to it"},
                    {"task": "T1: The part T1."},
                    {"completion_criterion": "It does what it serves."},
                    {"serves": "AC1: A user signs in with their email."},
                ],
                "retrieved_artifacts": [],
                "constraints": [
                    {"artifact-language": "English"},
                    {"conversation-language": "Japanese"},
                    {"fix": self.fix},
                ],
            },
            "give": ["work", "kind", "has", "test"],
            "steering": STEERING,
            "plan": call_at("0001"),
            "made": [call_at("0002")],
            "latest": None,
        }
        # pylint: enable=duplicate-code
        self.assertEqual((out, self.head(), self.out("status", "--porcelain")), (want, before, ""))

    def test_from_the_build_on_the_compressor_gives_the_receiver_and_has_what_it_builds_on(self):
        # Given: a session at the build stage whose T2 builds on T1, done, and T3, done, too.
        self.session(steered(part=plan(tasks=[task("T2", builds_on=("T1",))]), stage="build"))
        self.call("0001", "t1", works=("src/t1.py", "src/t1b.py"), result={})
        self.call("0002", "t3", works=("src/t3.py",), result={})
        self.call("0003", "t2", decisions=("Form: a page",))
        self.kept()
        # When: the orchestrator asks for T2's CCS with no reply.
        out = self.ran("ccs", "t2")
        # Then: the receiver and their use are left to the compressor, what the receiver has is
        # the result of T1 alone, the decisions kept, the roles to give the receiver and their use
        # among them, and the work's latest call named.
        settled = out["settled"]
        self.assertEqual(
            (
                settled["focal_entities"][3:],
                settled["goal_orientation"][0],
                settled["constraints"][0],
                out["give"],
                out["latest"],
            ),
            (
                [{"audience": ""}, {"has": "src/t1.py"}, {"has": "src/t1b.py"}],
                {"purpose": ""},
                {"decision": "Form: a page"},
                ["work", "kind", "receiver", "use", "has", "test"],
                call_at("0003"),
            ),
        )

    def test_a_task_building_on_one_not_done_stops(self):
        for name, made in (("not called", ()), ("not returned", (("0001", None),))):
            with self.subTest(name=name):
                # Given: T2 building on T1, which the plan still holds.
                self.session(steered(part=plan(tasks=[task(), task("T2", builds_on=("T1",))])))
                for number, result in made:
                    self.call(number, "t1", result=result)
                self.kept()
                # When: the orchestrator asks for T2's CCS.
                # Then: rn says T1 is not made yet, and to carry it out first.
                self.assertIn(
                    "rn: T2 builds on T1, which turn has not yet made and the plan still holds;"
                    " carry out T1 first, then run this again",
                    self.stopped("ccs", "t2"),
                )

    def test_the_reply_writes_the_ccs_and_gives_the_call_to_hand_turn(self):
        # Given: a session at the architecture stage, a decision kept on T1.
        self.call("0001", "t1", decisions=("License: MIT",))
        self.kept()
        # When: the orchestrator has T1's CCS written with the compressor's reply.
        out = self.handed()
        # Then: rn gives the call to turn:up, the key of each role turn reads, where the result
        # goes, and the command that checks it, null as the compressor gave none; and the CCS
        # holds what the record settles with what the compressor gave, each choice with why after
        # the decisions.
        # pylint: disable=duplicate-code
        want_call = {
            "ccs": call_at("0001"),
            "kind": {
                "work": "path",
                "checklist": "checklist",
                "receiver": "audience",
                "use": "purpose",
                "has": "has",
                "each": "each",
            },
            "result": call_at("0001", "result.json"),
            "test": None,
        }
        want = {
            "focal_entities": [
                {"work": "t1"},
                {"stage": "architecture"},
                {"kind": "code"},
                {"path": "docs/login.md"},
                {
                    "audience": "the user approving it at the architecture sign-off, and whoever"
                    " builds the later works to it"
                },
                {"has": MARKDOWN},
            ],
            "goal_orientation": [
                {"purpose": "approving it, then building each later work to it"},
                {"task": "T1: The part T1."},
                {"completion_criterion": "It does what it serves."},
                {"serves": "AC1: A user signs in with their email."},
            ],
            "retrieved_artifacts": [{"checklist": self.checklist}],
            "constraints": [
                {"decision": "License: MIT"},
                {
                    "chosen": "The result is made at docs/login.md: The plan's decision: Login"
                    " document: docs/login.md"
                },
                {"chosen": "It is made as a code work: The architecture: docs are code here"},
                {
                    "chosen": "No command of the project checks it: The architecture names no"
                    " command"
                },
                {"artifact-language": "English"},
                {"conversation-language": "Japanese"},
                {"fix": self.fix},
            ],
        }
        # pylint: enable=duplicate-code
        self.assertEqual((out, self.read_json(call_at("0001"))), (want_call, want))

    def test_the_reply_from_the_build_on_names_the_receiver_and_the_command(self):
        # Given: a session at the build stage.
        self.session(steered(part=plan(tasks=[task()]), stage="build"))
        # When: the orchestrator has T1's CCS written with the compressor's reply.
        out = self.handed(given=GIVEN_BUILT)
        # Then: the CCS names the receiver, their use and what they have as the compressor gave
        # them, and the command, kept among the constraints, is the call's test.
        ccs = self.read_json(call_at("0001"))
        self.assertEqual(
            (
                ccs["focal_entities"][3:],
                ccs["goal_orientation"][0],
                {"test": "sh dev/check.sh"} in ccs["constraints"],
                out["test"],
            ),
            (
                [{"path": "src/login.py"}, {"audience": "a new user"}, {"has": "README.md"}],
                {"purpose": "signing in"},
                True,
                "sh dev/check.sh",
            ),
        )

    def test_the_reply_tells_what_turn_makes_on_a_line_after_the_call(self):
        # Given: a session.
        # When: the orchestrator has T1's CCS written with the compressor's reply.
        lines = self.printed("ccs", "t1", "--reply", reply(*GIVEN_BEFORE)).splitlines()
        # Then: rn prints the call, then the line telling the user what turn makes.
        self.assertEqual(
            lines[1:],
            [
                (
                    "turn makes T1, the part T1, and an AI that did not make it uses it in your"
                    " place before it comes back; say stop to stop it."
                )
            ],
        )

    def test_a_path_whose_first_name_sorts_before_the_parent_is_taken(self):
        # Given: a session.
        # When: the orchestrator has T1's CCS written with a reply naming `-notes.md`, which
        # leads out of nothing, though its name sorts before `..`.
        self.handed(given=(*without(GIVEN_BEFORE, "work"), ("work", "-notes.md", "w")))
        # Then: the CCS names it.
        entities = self.read_json(call_at("0001"))["focal_entities"]
        self.assertIn({"path": "-notes.md"}, entities)

    def test_the_reply_may_name_several_paths_and_files_the_receiver_has(self):
        # Given: a session.
        # When: the orchestrator has T1's CCS written with a reply naming two paths of the result
        # and two files the receiver has.
        given = (
            *GIVEN_BEFORE,
            ("work", "docs/", "The plan's decision"),
            ("has", "README.md", "The README"),
            ("has", ".", "The repository"),
        )
        self.handed(given=given)
        # Then: the CCS names each, after what the record settles the receiver has.
        entities = self.read_json(call_at("0001"))["focal_entities"]
        self.assertEqual(
            [e for e in entities if "path" in e or "has" in e],
            [
                {"path": "docs/login.md"},
                {"path": "docs/"},
                {"has": MARKDOWN},
                {"has": "README.md"},
                {"has": "."},
            ],
        )

    def test_a_reply_written_again_on_a_call_not_returned_fills_the_same_call(self):
        # Given: T1's call written with the compressor's reply, turn not yet returned.
        self.handed()
        # When: the orchestrator has it written again, as after a question of turn's the
        # compressor answers, giving another kind.
        given = (*without(GIVEN_BEFORE, "kind"), ("kind", "ux", "The answer to turn's question"))
        self.write(os.path.join(self.plugin, "checklists", "product", "ux.md"), "# UX\n")
        out = self.handed(given=given)
        # Then: the same call is filled with the reply as given, its choices replacing those
        # before, and the step's commit names the call once.
        self.ran("state", "--message", "The step ends")
        constraints = self.read_json(call_at("0001"))["constraints"]
        self.assertEqual(
            (
                out["ccs"],
                [e for e in constraints if "chosen" in e][1],
                self.out("log", "-1", "--format=%B"),
            ),
            (
                call_at("0001"),
                {"chosen": "It is made as a ux work: The answer to turn's question"},
                "The step ends\n\nCall 0001 on t1: handed to turn\n\n",
            ),
        )

    def test_a_call_returned_is_made_again_as_a_new_call_carrying_its_decisions(self):
        # Given: a call on T1 holding a decision, returned, and a call on T2.
        self.call("0001", "t1", decisions=("License: MIT",), result={})
        self.call("0002", "t2")
        self.kept()
        # When: the orchestrator has T1's CCS written again with the compressor's reply.
        out = self.handed()
        # Then: a new call is filled, carrying the decision.
        self.assertEqual(
            (out["ccs"], self.read_json(call_at("0003"))["constraints"][0]),
            (call_at("0003"), {"decision": "License: MIT"}),
        )

    def test_the_reply_returning_a_point_gives_it_and_writes_nothing(self):
        # Given: a session.
        before = self.head()
        # When: the orchestrator gives the compressor's reply returning a point.
        point = {"point": "Where does the login page go?", "why": "No file or decision says."}
        out = self.ran("ccs", "t1", "--reply", json.dumps(point))
        # Then: rn gives the point and why, and writes nothing.
        self.assertEqual((out, self.head(), self.out("status", "--porcelain")), (point, before, ""))

    def test_a_reply_out_of_its_form_stops_and_writes_nothing(self):
        again = "; start the compressor again with what `rn.py ccs <work>` printed, telling it so"
        cases = {
            "{": "rn: the compressor's reply is no JSON",
            "[]": "rn: the compressor's reply is out of its form: $: expected a value of one of"
            " its anyOf choices, found []",
            '{"given": []}': "rn: the compressor's reply is out of its form: $.given: expected at"
            " least 1 item, found none",
            json.dumps({"given": [{"role": "path", "value": "x", "why": "y"}]}): "rn: the"
            " compressor's reply is out of its form: $.given[0].role: expected one of",
            reply(*GIVEN_BEFORE, ("receiver", "someone", "w")): "rn: the compressor gave"
            " receiver, which the record settles for this work; it gives work, kind, has and"
            " test alone",
            reply(*GIVEN_BEFORE, ("kind", "ux", "w")): "rn: the compressor gave kind more than"
            " once, a role it gives once",
            reply(*without(GIVEN_BEFORE, "kind"), ("kind", None, "w")): "rn: the compressor gave"
            " kind as null, which test alone may be; give it",
            reply(*without(GIVEN_BEFORE, "work"), ("work", None, "w")): "rn: the compressor gave"
            " work as null, which test alone may be; give it",
            reply(*without(GIVEN_BEFORE, "test")): "rn: the compressor gave no test",
            reply(*without(without(GIVEN_BEFORE, "work"), "kind")): "rn: the compressor gave no"
            " work and kind",
        }
        for text, said in cases.items():
            with self.subTest(said=said):
                # Given: a session.
                # When: the orchestrator gives a reply out of its form.
                out = self.stopped("ccs", "t1", "--reply", text)
                # Then: rn names the point, says to start the compressor again, and writes
                # nothing.
                self.assertEqual(
                    (said in out, out.rstrip().endswith(again), self.out("status", "--porcelain")),
                    (True, True, ""),
                )

    def test_a_reply_whose_value_cannot_be_taken_stops_and_writes_nothing(self):
        self.session(steered(part=plan(tasks=[task()]), stage="build"))
        cases = {
            "rn: the result's path ../x.md leads out of the repository": (
                *without(GIVEN_BUILT, "work"),
                ("work", "../x.md", "w"),
            ),
            "rn: the result's path /x.md leads out of the repository": (
                *without(GIVEN_BUILT, "work"),
                ("work", "/x.md", "w"),
            ),
            "rn: what the receiver has, none.md, is not there": (
                *without(GIVEN_BUILT, "has"),
                ("has", "none.md", "w"),
            ),
            "rn: no file the receiver has is named, by the record or by the compressor": (
                without(GIVEN_BUILT, "has")
            ),
            "rn: the kind 'Code' is not lowercase letters": (
                *without(GIVEN_BUILT, "kind"),
                ("kind", "Code", "w"),
            ),
            "rn: there is no checklist for the kind api": (
                *without(GIVEN_BUILT, "kind"),
                ("kind", "api", "w"),
            ),
        }
        for said, given in cases.items():
            with self.subTest(said=said):
                # Given: a session at the build stage, T1 building on nothing.
                # When: the orchestrator gives a reply with a value rn cannot take.
                out = self.stopped("ccs", "t1", "--reply", reply(*given))
                # Then: rn names it, and writes nothing.
                self.assertEqual((said in out, self.out("status", "--porcelain")), (True, ""))

    def test_a_reply_given_for_a_work_rn_makes_alone_stops(self):
        for work in ("plan", "learnings", "deliverable", "checklist-code"):
            with self.subTest(work=work):
                # Given: a session.
                # When: the orchestrator gives a compressor's reply for a work rn makes alone.
                # Then: rn says to run it without one.
                self.assertIn(
                    f"rn: the work {work} is made as rn makes it every time, with no compressor;"
                    f" run `rn.py ccs {work}` without --reply",
                    self.stopped("ccs", work, "--reply", reply(*GIVEN_BEFORE)),
                )

    def test_an_empty_reply_stops(self):
        # Given: a session.
        # When: the orchestrator gives a reply of blanks.
        # Then: rn says it is empty.
        self.assertIn(
            "rn: the compressor's reply is empty; give it in words",
            self.stopped("ccs", "t1", "--reply", " "),
        )

    def test_the_ccs_of_a_task_the_plan_does_not_hold_stops(self):
        for work in ("t0", "t3"):
            with self.subTest(work=work):
                # Given: a session holding T1 and T2.
                # When: the orchestrator asks for the CCS of a task not held.
                # Then: rn says there is no such task.
                self.assertIn(
                    f"rn: the plan holds no task T{work[1:]}, whose result the work {work} is",
                    self.stopped("ccs", work),
                )

    def test_a_kind_of_document_is_named_with_rns_checklist_of_every_document(self):
        for kind, named in (("architecture", True), (KIND, False)):
            with self.subTest(kind=kind):
                # Given: rn's checklist of a kind of document, or of code.
                checklist = os.path.join(self.plugin, "checklists", "product", f"{kind}.md")
                self.write(checklist, "# A kind\n")
                self.session(steered(stage="architecture"))
                # When: the orchestrator has T1's CCS written, the compressor giving that kind.
                given = (*without(GIVEN_BEFORE, "kind"), ("kind", kind, "w"))
                written = self.handed(given=given)["ccs"]
                # Then: it names the kind's checklist, then rn's checklist of every document where
                # the kind is a document, and nothing more for code.
                found = self.read_json(written)["retrieved_artifacts"]
                doc = [{"checklist": self.doc}] if named else []
                self.assertEqual(found, [{"checklist": checklist}, *doc])
                shutil.rmtree(FOLDER)
                self.kept()

    def test_the_questions_asked_of_each_part_are_named_after_the_checklists(self):
        # Given: rn telling questions of its checklist of the kind and of its checklist of every
        # document asked of each part, in the build stage.
        checklist = os.path.join(self.plugin, "checklists", "product", "ux.md")
        self.write(checklist, "# UX\n")
        self.session(steered(stage="build"))
        each = {"product/ux.md": ("Q-6",), "doc.md": ("Q-3", "Q-8")}
        with mock.patch.dict(ccs.EACH, each):
            # When: the orchestrator has T1's CCS written, the compressor giving a ux work.
            given = (*without(GIVEN_BUILT, "kind"), ("kind", "ux", "w"))
            written = self.handed(given=given)["ccs"]
        # Then: it names each of them after the checklists, by its checklist's path and its ID,
        # in the order of the checklists.
        self.assertEqual(
            self.read_json(written)["retrieved_artifacts"],
            [
                {"checklist": checklist},
                {"checklist": self.doc},
                {"each": f"{checklist} Q-6"},
                {"each": f"{self.doc} Q-3"},
                {"each": f"{self.doc} Q-8"},
            ],
        )

    def test_before_the_build_a_checklist_is_named_by_a_copy_without_the_items_on_the_built(self):
        for stage in ("goal", "ux", "architecture"):
            with self.subTest(stage=stage):
                # Given: rn telling questions of the kind's checklist judged on the built product,
                # in a session at a stage before the build.
                self.write(self.checklist, BUILT_ITEMS)
                self.session(steered(stage=stage))
                # When: the orchestrator has T1's CCS written.
                with mock.patch.dict(ccs.BUILT, {f"product/{KIND}.md": BUILT}):
                    self.handed()
                # Then: the CCS names, in the checklist's place, a copy beside it holding every
                # line but those questions, written with it.
                copy = call_at("0001", "checklist-1.md")
                named = self.read_json(call_at("0001"))["retrieved_artifacts"]
                kept = self.out("ls-files", "-o", FOLDER).split()
                self.assertEqual(
                    (named, self.read(copy), sorted(kept)),
                    ([{"checklist": copy}], WITHOUT_BUILT, sorted([call_at("0001"), copy])),
                )
                shutil.rmtree(FOLDER)
                self.kept()

    def test_a_copy_before_the_build_is_numbered_by_its_place_and_asked_of_each_part(self):
        # Given: rn telling questions of its checklist of every document judged on the built
        # product and one asked of each part, the user's addition after it, in the goal stage.
        checklist = os.path.join(self.plugin, "checklists", "product", "ux.md")
        self.write(checklist, "# UX\n")
        self.write(self.doc, BUILT_ITEMS)
        addition = f"{RECORD}/checklists/ux.md"
        self.write(addition, BUILT_ITEMS)
        self.session()
        # When: the orchestrator has T1's CCS written, the compressor giving a ux work.
        with (
            mock.patch.dict(ccs.BUILT, {"doc.md": BUILT}),
            mock.patch.dict(ccs.EACH, {"doc.md": ("Q-3",)}),
        ):
            self.handed(given=(*without(GIVEN_BEFORE, "kind"), ("kind", "ux", "w")))
        # Then: rn's own and the user's addition are named as they are, and rn's checklist of
        # every document by a copy, second as it stands second, the question asked of each part
        # named in the copy.
        copy = call_at("0001", "checklist-2.md")
        self.assertEqual(
            (self.read_json(call_at("0001"))["retrieved_artifacts"], self.read(copy)),
            (
                [
                    {"checklist": checklist},
                    {"checklist": copy},
                    {"checklist": addition},
                    {"each": f"{copy} Q-3"},
                ],
                WITHOUT_BUILT,
            ),
        )

    def test_from_the_build_on_each_checklist_is_named_whole(self):
        for stage in ("build", "deliverable"):
            with self.subTest(stage=stage):
                # Given: rn telling questions of the kind's checklist judged on the built product,
                # in a session at the build stage or after.
                self.write(self.checklist, BUILT_ITEMS)
                self.session(steered(stage=stage))
                # When: the orchestrator has T1's CCS written.
                with mock.patch.dict(ccs.BUILT, {f"product/{KIND}.md": BUILT}):
                    self.handed(given=GIVEN_BUILT)
                # Then: the CCS names the checklist itself, and no copy is written.
                self.assertEqual(
                    (
                        self.read_json(call_at("0001"))["retrieved_artifacts"],
                        os.listdir(f"{FOLDER}/calls"),
                    ),
                    ([{"checklist": self.checklist}], ["0001-ccs.json"]),
                )
                shutil.rmtree(FOLDER)
                self.kept()

    def test_the_ccs_of_a_task_serving_two_criteria_holds_both(self):
        # Given: a session whose T2 has two completion criteria, serving AC2 and then AC1 and AC2.
        two = {
            **task("T2"),
            "completion_criteria": [
                {"what": "It shows the cart.", "contributes_to": ["AC2"]},
                {"what": "It keeps the user.", "contributes_to": ["AC1", "AC2"]},
            ],
        }
        self.session(steered(part=plan(tasks=[two]), stage="architecture"))
        # When: the orchestrator has T2's CCS written.
        self.handed("t2")
        # Then: it holds the task, each completion criterion, then each criterion once, in the
        # order first named.
        self.assertEqual(
            self.read_json(call_at("0001"))["goal_orientation"][1:],
            [
                {"task": "T2: The part T2."},
                {"completion_criterion": "It shows the cart."},
                {"completion_criterion": "It keeps the user."},
                {"serves": "AC2: A signed-in user sees only their cart, on every page."},
                {"serves": "AC1: A user signs in with their email."},
            ],
        )

    def test_before_the_build_the_receiver_has_the_result_of_each_task_done(self):
        # Given: T3 and T4 done, T3 made again after T4, and T1 called before, not done.
        self.call("0001", "t3", works=("docs/old.md",), result={})
        self.call("0002", "t4", works=("docs/t4.md",), result={})
        self.call("0003", "t3", works=("docs/t3.md",), result={})
        self.kept()
        # When: the orchestrator has T1's CCS written.
        self.handed()
        # Then: the receiver has the steering's Markdown, then the result of each task done, as
        # its latest call names it, in the order first called.
        entities = self.read_json(call_at("0004"))["focal_entities"]
        self.assertEqual(
            [e for e in entities if "has" in e],
            [{"has": MARKDOWN}, {"has": "docs/t3.md"}, {"has": "docs/t4.md"}],
        )


class CcsTest(RepoTest):
    """The CCS of each work rn makes the same way every time, written and handed to turn, or cut
    for the orchestrator to write where the work is the plan or the learnings."""

    def setUp(self) -> None:
        super().setUp()
        self.session(steered(part=plan(tasks=[task(), task("T2", ("AC2",))]), stage="architecture"))

    def test_ccs_tells_what_turn_makes_on_a_line_after_the_call(self):
        # Given: a session.
        # When: the orchestrator has a checklist's CCS written.
        code, out = self.rn("ccs", "checklist-code")
        # Then: rn prints the call, then the line telling the user what turn makes.
        lines = out.splitlines()
        tell = (
            "turn makes your checklist for code, and an AI that did not make it uses it in your"
            " place before it comes back; say stop to stop it."
        )
        self.assertEqual(
            (code, json.loads(lines[0])["ccs"].endswith("-ccs.json"), lines[1:]),
            (0, True, [tell]),
        )

    def test_ccs_writes_the_call_before_its_maker_takes_it(self):
        for work, argv, files, said in (
            (
                "t1",
                ["--reply", reply(*GIVEN_BEFORE)],
                [call_at("0001")],
                "Call 0001 on t1: handed to turn",
            ),
            (
                "plan",
                [],
                [call_at("0001"), call_at("0001", "plan.json")],
                "Call 0001 on plan: its part cut for the orchestrator to write",
            ),
        ):
            with self.subTest(work=work):
                # Given: a session.
                self.session(steered(stage="architecture"))
                before = self.head()
                # When: the orchestrator has the work's CCS written.
                self.ran("ccs", work, *argv)
                # Then: the CCS, and the part where the work has one, are written and not
                # committed, so a conversation cut while the work is made goes on from them; the
                # step's commit then holds them, with a message naming the call after its own.
                written = (sorted(self.out("ls-files", "-o", FOLDER).split()), self.head())
                self.ran("state", "--message", "The step ends")
                kept = (
                    sorted(self.out("show", "--name-only", "--format=", "origin/work").split()),
                    self.out("log", "-1", "--format=%B", "origin/work"),
                )
                self.assertEqual(
                    (written, kept), ((files, before), (files, f"The step ends\n\n{said}\n\n"))
                )
                shutil.rmtree(FOLDER)
                self.kept()

    def test_a_decision_while_turn_asks_commits_nothing(self):
        # Given: the call on t1 written, and the state turn keeps in its folder at the root while
        # it runs.
        self.ran("ccs", "t1", "--reply", reply(*GIVEN_BEFORE))
        self.write(".turn/20261025-result.json/run.json", "x\n")
        before = self.head()
        # When: the orchestrator keeps a decision while turn asks.
        self.ran("decide", "t1", "--title", "Login", "--says", "email", "--message", "Login")
        # Then: the decision is in the call, and nothing is committed, the run waiting on the
        # answer and its state left as they are.
        decided = {"decision": "Login: email"} in self.read_json(call_at("0001"))["constraints"]
        self.assertEqual((decided, self.head()), (True, before))

    def test_the_ccs_of_the_plan_serves_nothing_and_has_what_each_task_done_made(self):
        # Given: a session holding T1 and T2, with calls on T3, done, not returned, on T1, on T4,
        # done, not returned, and on T3 again, returned.
        self.call("0001", "t3")
        self.call("0002", "t1", result={})
        self.call("0003", "t4")
        self.call("0004", "t3", result={})
        self.kept()
        # When: the orchestrator has the CCS of the plan written.
        self.ran("ccs", "plan")
        # Then: it serves nothing, and has the repository, then, in the order made, the latest
        # call of each task done, returned by turn, which holds what the task served and decided
        # and the files it made, and none of turn's results.
        ccs = self.read_json(call_at("0005"))
        has = [e for e in ccs["focal_entities"] if "has" in e]
        self.assertEqual(
            (ccs["goal_orientation"][1:], has), ([], [{"has": "."}, {"has": call_at("0004")}])
        )

    def test_the_ccs_of_the_plan_has_what_the_tasks_done_made_in_the_order_made(self):
        # Given: a session with T4 done on the first call and T3 done on the second.
        self.call("0001", "t4", result={})
        self.call("0002", "t3", result={})
        self.kept()
        # When: the orchestrator has the CCS of the plan written.
        self.ran("ccs", "plan")
        # Then: it has the repository, then T4's call, then T3's, in the order they were made.
        has = [e for e in self.read_json(call_at("0003"))["focal_entities"] if "has" in e]
        self.assertEqual(has, [{"has": "."}, {"has": call_at("0001")}, {"has": call_at("0002")}])

    def test_the_ccs_of_a_checklist_or_the_learnings_has_nothing_the_tasks_done_made(self):
        for work in ("checklist-code", "learnings"):
            with self.subTest(work=work):
                # Given: a session with T3 done.
                self.call("0001", "t3", result={})
                self.kept()
                # When: the orchestrator has the CCS of a checklist, or of the learnings, written.
                made = self.ran("ccs", work)["ccs"]
                # Then: its receiver has no call of T3, as only the plan is made from what the
                # tasks done made.
                has = [e for e in self.read_json(made)["focal_entities"] if "has" in e]
                self.assertNotIn({"has": call_at("0001")}, has)
                shutil.rmtree(f"{FOLDER}/calls")
                self.kept()

    def test_the_ccs_of_the_finished_work_holds_each_goal_and_every_criterion(self):
        # Given: a file the branch changed.
        self.write("src/app.py", "x\n")
        self.kept()
        # When: the orchestrator has the CCS of the finished work written.
        made = self.ran("ccs", "deliverable")["ccs"]
        # Then: it holds the goal with why and every criterion, and the receiver has the
        # repository alone.
        ccs = self.read_json(made)
        self.assertEqual(
            (ccs["goal_orientation"][1:], [e for e in ccs["focal_entities"] if "has" in e]),
            (
                [
                    {"serves": "G1: Users sign in. So their carts stay theirs."},
                    {"serves": "AC1: A user signs in with their email."},
                    {"serves": "AC2: A signed-in user sees only their cart, on every page."},
                ],
                [{"has": "."}],
            ),
        )

    def test_the_ccs_of_a_checklist_or_the_learnings_serves_nothing(self):
        for work in ("checklist-code", "learnings"):
            with self.subTest(work=work):
                # Given: a session.
                # When: the orchestrator has the CCS of a checklist, or of the learnings, written.
                made = self.ran("ccs", work)["ccs"]
                # Then: it holds the use alone, as neither serves the user's work.
                self.assertEqual(len(self.read_json(made)["goal_orientation"]), 1)

    def test_ccs_of_a_part_gives_what_the_orchestrator_writes_it_from(self):
        script = os.path.join(self.plugin, "scripts", "rn.py")
        for work, number, name in (
            ("plan", "0001", "plan.json"),
            ("learnings", "0002", "learnings.md"),
        ):
            with self.subTest(work=work):
                # Given: a session, the plan's call 0001 and the learnings' 0002.
                # When: the orchestrator has the CCS of the plan or of the learnings written.
                out = self.printed("ccs", work)
                # Then: rn prints, on one line and nothing after it, the part to write, the CCS,
                # the kind's checklists, rn's checklist of every document among them, and the
                # command that runs rn's check of the part, as `state --put` holds it, by rn.py
                # where it is installed; no call to turn.
                want = {
                    "part": call_at(number, name),
                    "ccs": call_at(number),
                    "checklists": [self.own[work], self.doc],
                    "check": f"python3 {script} check {number}",
                }
                self.assertEqual(out.splitlines(), [json.dumps(want)])

    def test_the_command_names_rn_where_its_path_holds_a_space(self):
        # Given: rn installed in a folder whose path holds a space.
        spaced = os.path.join(self.base, "my plugin")
        shutil.copytree(self.plugin, spaced)
        self.plugin = spaced
        # When: the orchestrator has the CCS of the plan written.
        # Then: the command quotes the path, so the shell runs rn.py.
        script = os.path.join(spaced, "scripts", "rn.py")
        self.assertEqual(self.ran("ccs", "plan")["check"], f"python3 '{script}' check 0001")

    def test_each_work_rn_makes_itself_is_made_with_its_own_kind_receiver_use_and_had(self):
        cases = {
            "plan": ([call_at("0001", "plan.json")], "plan", "the user at the goal sign-off"),
            "learnings": (
                [call_at("0002", "learnings.md")],
                "learnings",
                "the user deciding each learning",
            ),
            "deliverable": (["src/app.py"], "deliverable", "the user at the deliverable"),
            "checklist-api": ([".rn/checklists/api.md"], "checklist", "whoever makes an api"),
            "checklist-code": ([".rn/checklists/code.md"], "checklist", "whoever makes a code"),
        }
        self.write("src/app.py", "x\n")
        self.kept()
        for work, (paths, kind, receiver) in cases.items():
            with self.subTest(work=work):
                # Given: a session, and a file the branch changed.
                # When: the orchestrator has the work's CCS written, giving nothing more.
                written = self.read_json(self.ran("ccs", work)["ccs"])
                entities = written["focal_entities"]
                # Then: it holds the paths, the kind and its checklist, the receiver, their use and
                # what they have, as rn makes that work every time, and no test.
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
                        [e for e in written["constraints"] if "test" in e],
                    ),
                    (paths, kind, {"checklist": self.own[kind]}, True, True, ["."], []),
                )

    def test_the_plan_is_cut_into_its_part_as_json_and_handed_as_the_work(self):
        # Given: a session.
        # When: the orchestrator has the CCS of the plan written.
        self.ran("ccs", "plan")
        # Then: the plan is cut into the call's part as JSON in the steering's form, one key or
        # value to a line, the work the CCS names.
        part = call_at("0001", "plan.json")
        self.assertEqual(
            (self.read(part), self.read_json(call_at("0001"))["focal_entities"][3]),
            (json_text(plan(tasks=[task(), task("T2", ("AC2",))])), {"path": part}),
        )

    def test_the_learnings_are_cut_into_a_part_of_their_name_with_none_of_those_kept(self):
        # Given: a session with a learning kept.
        self.write(LEARNINGS, "- L1: Kept.\n")
        self.kept()
        # When: the orchestrator has the CCS of the learnings written.
        self.ran("ccs", "learnings")
        # Then: the part is empty, as the form of rn's learnings checklist holds no heading, the
        # work the CCS names.
        part = call_at("0001", "learnings.md")
        self.assertEqual(
            (self.read(part), self.read_json(call_at("0001"))["focal_entities"][3]),
            ("", {"path": part}),
        )

    def test_the_ccs_of_a_checklist_names_rns_checklist_for_checklists_and_every_document(self):
        # Given: rn's checklist for checklists and its checklist of every document.
        # When: the orchestrator has the CCS of a checklist written.
        self.ran("ccs", "checklist-code")
        # Then: it names both, rn's checklist for checklists first.
        self.assertEqual(
            self.read_json(call_at("0001"))["retrieved_artifacts"],
            [{"checklist": self.own["checklist"]}, {"checklist": self.doc}],
        )

    def test_a_part_before_the_build_is_written_with_a_copy_without_the_items_on_the_built(self):
        # Given: rn telling questions of the learnings checklist judged on the built product, in
        # the goal stage.
        self.write(self.own["learnings"], BUILT_ITEMS)
        self.session(steered())
        # When: the orchestrator has the CCS of the learnings written.
        with mock.patch.dict(ccs.BUILT, {"session/learnings.md": BUILT}):
            given = self.ran("ccs", "learnings")["checklists"]
        # Then: the checklists it is given to write the part with are the copy, then rn's
        # checklist of every document.
        copy = call_at("0001", "checklist-1.md")
        self.assertEqual((given, self.read(copy)), ([copy, self.doc], WITHOUT_BUILT))

    def test_the_decisions_of_the_latest_call_not_returned_are_kept(self):
        # Given: a call on the finished work holding a decision, not returned.
        self.write("src/app.py", "x\n")
        self.call("0001", "deliverable", decisions=("License: MIT",))
        self.kept()
        # When: the orchestrator has its CCS written.
        out = self.ran("ccs", "deliverable")
        # Then: the same call is filled, its decision first among the constraints.
        self.assertEqual(
            (out["ccs"], self.read_json(call_at("0001"))["constraints"][0]),
            (call_at("0001"), {"decision": "License: MIT"}),
        )

    def test_a_part_cut_is_written_again_in_a_new_call_carrying_its_decisions(self):
        # Given: a call on the plan holding a decision, its part cut.
        self.call("0001", "plan", decisions=("Scope: the cart",), part=plan())
        self.kept()
        # When: the orchestrator has the plan's CCS written again, as it writes the plan again.
        out = self.ran("ccs", "plan")
        # Then: a new call is filled, carrying the decision, and the first is left as it was.
        self.assertEqual(
            (
                out["ccs"],
                self.read_json(call_at("0002"))["constraints"][0],
                self.read(call_at("0001", "plan.json")),
            ),
            (call_at("0002"), {"decision": "Scope: the cart"}, json_text(plan())),
        )

    def test_the_finished_work_is_every_file_the_branch_changed_outside_rn(self):
        # Given: a file the branch changed outside .rn/, and one it removed.
        self.write("src/app.py", "x\n")
        os.remove("README.md")
        self.git("rm", "-q", "--cached", "README.md")
        self.kept()
        # When: the orchestrator has the finished work's CCS written.
        self.ran("ccs", "deliverable")
        # Then: the work is the file changed outside .rn/ and there.
        works = [e for e in self.read_json(call_at("0001"))["focal_entities"] if "path" in e]
        self.assertEqual(works, [{"path": "src/app.py"}])

    def test_the_finished_work_with_no_file_changed_stops(self):
        # Given: a branch that changed nothing outside .rn/.
        # When: the orchestrator has the finished work's CCS written.
        # Then: rn says there is none, and what to do.
        self.assertIn(
            "rn: the branch changed no file outside .rn/ since it left origin/main",
            self.stopped("ccs", "deliverable"),
        )

    def test_ccs_is_written_one_key_to_a_line_with_text_beyond_ascii_as_it_is(self):
        # Given: a session at the build stage.
        self.session(steered(stage="build"))
        # When: the orchestrator has a CCS written with a receiver in Japanese.
        given = (*without(GIVEN_BUILT, "receiver"), ("receiver", "新しい利用者", "w"))
        self.ran("ccs", "t1", "--reply", reply(*given))
        # Then: it is written one key or value to a line, the Japanese as it is.
        text = self.read(call_at("0001"))
        self.assertEqual(
            (
                text.startswith('{\n "focal_entities": [\n  {\n   "work": "t1"'),
                "新しい利用者" in text,
            ),
            (True, True),
        )

    def test_ccs_with_moves_written_and_not_committed_writes_the_call_on_them(self):
        # Given: a decision of t1 written, and a file of the user's changed, neither committed.
        self.ran("decide", "t1", "--title", "Login", "--says", "email", "--message", "Login")
        self.write("README.md", "# app, changed\n")
        # When: the orchestrator has the CCS of t1 written.
        out = self.ran("ccs", "t1", "--reply", reply(*GIVEN_BEFORE))
        # Then: the call holds the decision, as the step's moves are committed as it ends.
        decided = {"decision": "Login: email"} in self.read_json(out["ccs"])["constraints"]
        self.assertEqual((out["ccs"], decided), (call_at("0001"), True))

    def test_a_work_rn_does_not_make_stops(self):
        # Given: a session.
        # When: the orchestrator has a CCS written for a work rn does not make.
        # Then: rn names it.
        self.assertIn("rn: the work 'readme' is none rn makes", self.stopped("ccs", "readme"))

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
        self.assertIn("below the top", self.stopped("ccs", "t1"))


class DecisionsTest(RepoTest):
    """Each decision of a work, as its latest call keeps it, and the checklists of its kind."""

    def setUp(self) -> None:
        super().setUp()
        self.session(steered(stage="architecture"))

    def test_the_kind_is_read_from_the_works_own_calls_alone(self):
        # Given: a call on t1 of a code work, then calls on the plan and on t2 naming a kind that
        # has no checklist.
        self.call("0001", "t1")
        self.call("0002", "plan", kind="api")
        self.call("0003", "t2", kind="api")
        self.kept()
        # When: the orchestrator asks for t1's decisions.
        # Then: rn gives the checklists of t1's own kind.
        self.assertEqual(self.ran("decisions", "t1")["checklists"], [self.checklist])

    def test_the_decisions_of_a_works_latest_call_are_given(self):
        # Given: a call on t1 returned, and one made again with a decision changed and one added.
        self.call("0001", "t1", decisions=("A: B",), result={})
        self.call("0002", "t1", decisions=("A: C", "D: E"))
        self.kept()
        # When: the orchestrator asks for t1's decisions.
        # Then: rn gives those of the latest call, with its number, and the checklists of the
        # kind the call names.
        self.assertEqual(
            self.ran("decisions", "t1"),
            {
                "work": "t1",
                "call": "0002",
                "decisions": ["A: C", "D: E"],
                "checklists": [self.checklist],
            },
        )

    def test_the_kind_is_that_of_the_works_latest_call_naming_one(self):
        # Given: a call on t1 of a ux work, returned, then a call holding a decision alone, as a
        # decision kept after turn returned makes it, naming no kind.
        ux = os.path.join(self.plugin, "checklists", "product", "ux.md")
        self.write(ux, "# UX\n")
        self.call("0001", "t1", result={}, kind="ux")
        self.call("0002", "t1", kind="code", result={})
        self.kept()
        self.ran("decide", "t1", "--title", "A", "--says", "B", "--message", "m")
        # When: the orchestrator asks for t1's decisions.
        # Then: rn gives the checklists of the kind of the latest call naming one, code.
        self.assertEqual(self.ran("decisions", "t1")["checklists"], [self.checklist])

    def test_a_task_never_called_has_no_decisions_and_no_checklist_yet(self):
        # Given: a session with no call on t1.
        # When: the orchestrator asks for its decisions.
        # Then: rn gives no call, no decision and no checklist, as the compressor gives its kind.
        self.assertEqual(
            self.ran("decisions", "t1"),
            {"work": "t1", "call": None, "decisions": [], "checklists": []},
        )

    def test_the_checklists_of_a_work_rn_makes_its_own_way_are_those_of_its_kind(self):
        for work, kind in (
            ("plan", "plan"),
            ("learnings", "learnings"),
            ("deliverable", "deliverable"),
            ("checklist-api", "checklist"),
        ):
            with self.subTest(work=work):
                # Given: rn's checklist of each kind of the works rn makes its own way.
                # When: the orchestrator asks for the decisions of one of those works.
                # Then: rn gives the checklist of its kind, with rn's checklist of every document
                # for a document, which the finished work is not, as its CCS would name them.
                doc = [] if kind == "deliverable" else [self.doc]
                self.assertEqual(self.ran("decisions", work)["checklists"], [self.own[kind], *doc])

    def test_the_users_addition_comes_after_rns_own_checklist(self):
        # Given: the user's addition for the kind of t1's call.
        self.write(f"{RECORD}/checklists/{KIND}.md", "# Ours\n")
        self.call("0001", "t1")
        self.kept()
        # When: the orchestrator asks for t1's decisions.
        # Then: rn gives its own checklist, then the user's.
        self.assertEqual(
            self.ran("decisions", "t1")["checklists"],
            [self.checklist, f"{RECORD}/checklists/{KIND}.md"],
        )

    def test_the_decisions_of_a_work_whose_kind_has_no_checklist_stop(self):
        # Given: a call on t1 of a kind with no checklist.
        self.call("0001", "t1", kind="api")
        self.kept()
        # When: the orchestrator asks for that work's decisions.
        # Then: rn says there is no checklist for the kind and how to make one.
        self.assertIn(
            "rn: there is no checklist for the kind api, neither rn's nor .rn/checklists/api.md;"
            " make .rn/checklists/api.md first",
            self.stopped("decisions", "t1"),
        )

    def test_the_decisions_of_a_task_the_plan_does_not_hold_stop(self):
        # Given: a session whose plan holds T1.
        # When: the orchestrator asks for the decisions of T5.
        # Then: rn says the plan holds no such task.
        self.assertIn("rn: the plan holds no task T5", self.stopped("decisions", "t5"))

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

    def test_rns_checklist_for_checklists_is_its_meta_checklist(self):
        # Given: rn's checklist for checklists, meta.md straight in rn's checklists.
        # When: the orchestrator asks for the checklists of a checklist.
        # Then: rn gives it, then rn's checklist of every document.
        self.assertEqual(self.ran("checklists", "checklist"), [self.own["checklist"], self.doc])

    def test_the_plans_checklists_are_rns_plan_checklist_and_its_checklist_of_every_document(self):
        # Given: rn's plan checklist, which holds its questions alone and asks nothing doc.md asks.
        # When: the orchestrator asks for the checklists of a plan.
        # Then: rn gives it, then rn's checklist of every document, as the user reads the plan's
        # Markdown as a document.
        self.assertEqual(self.ran("checklists", "plan"), [self.own["plan"], self.doc])

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


class UnbuiltTest(unittest.TestCase):
    """A checklist cut for a call before the build: each question judged on the built product taken
    out up to the next heading of its level or above, and every other line kept."""

    def test_a_question_cut_ends_at_a_heading_above_its_level(self):
        # Given: a checklist whose question judged on the built product is followed by a heading
        # of the level above, with a line under it.
        text = "# C\n\n### Q-1: Run\n\nWhy: run.\n\n## After\n\nKept.\n"
        # When: rn cuts it for a call before the build.
        # Then: the question is taken out, and the heading above its level and its line are kept.
        self.assertEqual(ccs.unbuilt(text, ("Q-1",)), "# C\n\n## After\n\nKept.\n")

    def test_the_lines_before_the_first_heading_are_kept(self):
        # Given: a checklist opening with frontmatter before its title, and a question judged on
        # the built product.
        text = "---\nname: c\n---\n# C\n\n### Q-1: Run\n\nWhy: run.\n"
        # When: rn cuts it for a call before the build.
        # Then: the frontmatter and the title are kept, and the question is taken out.
        self.assertEqual(ccs.unbuilt(text, ("Q-1",)), "---\nname: c\n---\n# C\n")


class ToldTest(unittest.TestCase):
    """What rn tells turn of its own checklists names what those checklists hold, so a checklist
    changed without the tables fails here rather than in a user's run."""

    def test_each_question_rn_tells_of_is_one_its_checklist_holds(self):
        for name, table in (("BUILT", ccs.BUILT), ("EACH", ccs.EACH)):
            for path, told in table.items():
                with self.subTest(table=name, path=path):
                    # Given: a checklist of rn's the table tells questions of.
                    with open(os.path.join(CHECKLISTS, path), encoding="utf-8") as f:
                        held = [i for _, i in items.items(f.read())]
                    # When: its questions are read.
                    # Then: each the table tells of is among them.
                    self.assertEqual([q for q in told if q not in held], [])

    def test_each_kind_of_document_has_rns_own_checklist(self):
        for kind in ccs.DOCUMENTS:
            with self.subTest(kind=kind):
                # Given: a kind rn gives its checklist of every document beside.
                # When: rn's own checklist of it is looked for.
                # Then: one is there.
                self.assertEqual(len(ccs.rns_own(kind, os.path.dirname(CHECKLISTS))), 1)


if __name__ == "__main__":
    unittest.main()
