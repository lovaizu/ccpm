import os
import sys
import unittest

HOOKS = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "rn", "hooks")
)
sys.path.insert(0, HOOKS)

from checks import Record, older, open_names, run, steering_form, trace

FOLDER = ".rn/20261001-coupon"

PLAN = """---
rn: 0.9.0
pr: https://github.com/o/r/pull/1
status: running
artifact-language: English
conversation-language: Japanese
readme: README.md
design: docs/design.md
verification: docs/verification.md
---

# Goal

No coupon makes an order cost more.

# Acceptance criteria

## Attractive quality

- A1: A percent coupon over 100% takes the items' total to 0.

## Must-be quality

- M1: The tests pass as before.

# Assumptions

# Rules

# Tasks

### [x] #1: Plan sign-off
### [ ] #2: Design sign-off

# Not yet specified
"""

TASKS = """### [x] #1: Plan sign-off
### [x] #2: Design sign-off
### [ ] #3: Hold the total at 0

Serves: A1, M1

### [ ] #4: Deliverable sign-off
"""

VERIFICATION = """---
name: verification
version: 0.1.0
---

# shop verification

## Scenes

### A1: A percent coupon over 100% takes the items' total to 0

- A percent coupon of 150.

  Passes when the items' total is 0.

## Machine checks

| Command | Criteria |
|---|---|
| `npm test` | M1 |
"""

# A plan naming its verification document and nothing else, for a stop that rests on the document
# alone.
NAMES_VERIFICATION = "---\nverification: docs/verification.md\n---\n"

PLAN_FORM = (
    "since rn's commands and checks read the plan by that form, and a later conversation goes on"
    " from it only when the form holds."
)
OPEN_NAME = (
    "is not named `{NN}-{kind}-{about}.md` with the kind `report`, `feedback` or `notes`; rename"
    " it as step 3 of rn's references/record.md says, since rn's commands and checks find each"
    " item of open/ by its name."
)


def record(plan="", items=None, verification=None, rn=None):
    """A record holding only the parts a test gives it, so each test shows what its check reads."""
    return Record(FOLDER, plan, items or {}, verification, rn)


def planned(plan=PLAN, tasks=TASKS):
    return plan.replace("### [x] #1: Plan sign-off\n### [ ] #2: Design sign-off\n", tasks)


class SessionTest(unittest.TestCase):
    def test_a_session_with_no_rn_field_or_one_below_0_9_0_is_older(self):
        # Given: a plan with no rn field, or one written by rn before 0.9.0
        # When: whether an earlier rn started the session is asked
        # Then: it is older
        for rn in (None, "0.8.0", "0.8.12"):
            with self.subTest(rn=rn):
                self.assertTrue(older(record(rn=rn)))

    def test_a_session_from_rn_0_9_0_on_is_not_older(self):
        # Given: a plan written by rn 0.9.0 or later
        # When: whether an earlier rn started the session is asked
        # Then: it is not older
        for rn in ("0.9.0", "0.10.0", "1.0.0"):
            with self.subTest(rn=rn):
                self.assertFalse(older(record(rn=rn)))

    def test_every_checks_sentences_are_given_in_the_order_of_the_checks(self):
        # Given: two checks, each stopping a record with a sentence of its own
        # When: both are run on a record
        # Then: the sentences of the first come before those of the second
        def first(found):
            return ["rn: first."]

        def second(found):
            return ["rn: second.", "rn: third."]

        self.assertEqual(
            run((first, second), record()), ["rn: first.", "rn: second.", "rn: third."]
        )


class PlanFormTest(unittest.TestCase):
    def test_a_plan_in_the_templates_form_is_let_through(self):
        # Given: a plan with every key, heading and task as the template gives them, its status
        #   running or finished and a task numbered past 9
        # When: the plan's form is checked
        # Then: nothing is stopped
        tenth = PLAN.replace("### [ ] #2: Design sign-off", "### [ ] #10: Design sign-off")
        for plan in (tenth, tenth.replace("status: running", "status: finished")):
            with self.subTest(plan=plan):
                self.assertEqual(steering_form.check(record(plan)), [])

    def test_a_plan_without_front_matter_is_stopped(self):
        # Given: a plan whose keys are not between two `---` lines
        # When: the plan's form is checked
        # Then: a single stop says, under Working out the plan, that the plan has no front
        #   matter, what to put back, and why
        plan = PLAN.replace("---\nrn:", "rn:", 1)
        self.assertEqual(
            steering_form.check(record(plan)),
            [
                (
                    f'rn: in "Working out the plan" of conduct.md, {FOLDER}/steering.md opens with no'
                    " front matter between two `---` lines; put back the front matter of the template"
                    f" in rn's checklists/plan.md, {PLAN_FORM}"
                )
            ],
        )

    def test_a_plan_missing_a_key_of_the_template_is_stopped(self):
        # Given: a plan whose front matter lacks one of the template's keys
        # When: the plan's form is checked
        # Then: a single stop says, under Working out the plan, which key the plan lacks, to add
        #   it, and why
        for key in (
            "rn",
            "pr",
            "status",
            "artifact-language",
            "conversation-language",
            "readme",
            "design",
            "verification",
        ):
            with self.subTest(key=key):
                line = next(line for line in PLAN.splitlines() if line.startswith(key + ":"))
                self.assertEqual(
                    steering_form.check(record(PLAN.replace(line + "\n", ""))),
                    [
                        (
                            f'rn: in "Working out the plan" of conduct.md, {FOLDER}/steering.md has no'
                            f" `{key}` key in its front matter; add `{key}` as the template in rn's"
                            f" checklists/plan.md gives it, {PLAN_FORM}"
                        )
                    ],
                )

    def test_a_status_other_than_running_or_finished_is_stopped(self):
        # Given: a plan whose status is neither running nor finished, among them one that holds
        #   running as its first letters
        # When: the plan's form is checked
        # Then: a single stop says, under Working out the plan, the status found, what to set it
        #   to, and why
        for status in ("paused", "Running", "runningx", ""):
            with self.subTest(status=status):
                plan = PLAN.replace("status: running", f"status: {status}")
                self.assertEqual(
                    steering_form.check(record(plan)),
                    [
                        (
                            f'rn: in "Working out the plan" of conduct.md, {FOLDER}/steering.md has'
                            f" `status: {status}`; set it to `running`, or to `finished` once the"
                            f" Deliverable sign-off is approved, {PLAN_FORM}"
                        )
                    ],
                )

    def test_a_plan_missing_a_heading_of_the_template_is_stopped(self):
        # Given: a plan that lacks one of the template's headings
        # When: the plan's form is checked
        # Then: a single stop says, under Working out the plan, which heading the plan lacks, to
        #   put it back, and why
        for heading in (
            "# Goal",
            "# Acceptance criteria",
            "## Attractive quality",
            "## Must-be quality",
            "# Assumptions",
            "# Rules",
            "# Tasks",
            "# Not yet specified",
        ):
            with self.subTest(heading=heading):
                plan = PLAN.replace(f"\n{heading}\n", "\n")
                self.assertEqual(
                    steering_form.check(record(plan)),
                    [
                        (
                            f'rn: in "Working out the plan" of conduct.md, {FOLDER}/steering.md has no'
                            f" `{heading}` heading; put it back where the template in rn's"
                            f" checklists/plan.md has it, {PLAN_FORM}"
                        )
                    ],
                )

    def test_a_task_heading_out_of_the_templates_form_is_stopped(self):
        # Given: a plan with a task heading that is not `### [ ] #N: name` or `### [x] #N: name`
        # When: the plan's form is checked
        # Then: a single stop says, under Working out the plan, the heading found, how to write
        #   it, and why
        for heading in (
            "### #2: Design sign-off",
            "### [X] #2: Design sign-off",
            "### [ ] 2: Design sign-off",
            "### [ ] #2 Design sign-off",
            "### [ ] #2: ",
        ):
            with self.subTest(heading=heading):
                plan = PLAN.replace("### [ ] #2: Design sign-off", heading)
                self.assertEqual(
                    steering_form.check(record(plan)),
                    [
                        (
                            f'rn: in "Working out the plan" of conduct.md, {FOLDER}/steering.md has'
                            f" the task heading `{heading}`; write it as `### [ ] #N: name`, or"
                            f" `### [x] #N: name` once the task is done, {PLAN_FORM}"
                        )
                    ],
                )

    def test_an_id_given_twice_is_stopped(self):
        # Given: a plan where two tasks have the same number, two attractive criteria the same
        #   ID, or two must-be criteria the same ID
        # When: the plan's form is checked
        # Then: a single stop says, under Working out the plan, the ID given twice, what to give
        #   instead, and why
        for plan, broken in (
            (
                PLAN.replace("#2: Design", "#1: Design"),
                "gives #1 to more than one task; give the later task the next unused id",
            ),
            (
                PLAN.replace("total to 0.\n", "total to 0.\n- A1: Another gain.\n"),
                "gives A1 to more than one criterion; give the later criterion the next unused ID",
            ),
            (
                PLAN.replace("as before.\n", "as before.\n- M1: Another given.\n"),
                "gives M1 to more than one criterion; give the later criterion the next unused ID",
            ),
        ):
            with self.subTest(broken=broken):
                self.assertEqual(
                    steering_form.check(record(plan)),
                    [
                        (
                            f'rn: in "Working out the plan" of conduct.md, {FOLDER}/steering.md'
                            f" {broken}, {PLAN_FORM}"
                        )
                    ],
                )


class OpenNamesTest(unittest.TestCase):
    def test_items_named_as_the_record_says_are_let_through(self):
        # Given: items of open/ named with a number of two or more digits, a kind of report,
        #   feedback or notes, and what they are about
        # When: the names of open/ are checked
        # Then: nothing is stopped
        for name in ("01-notes-pause.md", "12-report-task-3.md", "100-feedback-plan.md"):
            with self.subTest(name=name):
                self.assertEqual(open_names.check(record(items={name: ""})), [])

    def test_an_item_named_otherwise_is_stopped(self):
        # Given: an item of open/ whose name lacks its number, its kind, what it is about or
        #   `.md`, or holds a kind with letters added
        # When: the names of open/ are checked
        # Then: a single stop names the item, says it is not named as the record says, how to
        #   name it, and why
        for name in (
            "notes-plan.md",
            "1-notes-plan.md",
            "01-note-plan.md",
            "01-notesx-plan.md",
            "01-notes-.md",
            "01-notes-plan.txt",
        ):
            with self.subTest(name=name):
                problems = open_names.check(record(items={name: ""}))
                self.assertEqual(len(problems), 1)
                self.assertTrue(problems[0].endswith(f"{FOLDER}/open/{name} {OPEN_NAME}"))

    def test_a_misnamed_items_stop_names_the_step_that_writes_such_an_item(self):
        # Given: a misnamed item of open/ whose name tells what it holds, or does not
        # When: the names of open/ are checked
        # Then: the stop opens with the part of the conductor's steps that writes such an item,
        #   or with the part that takes items up where the name tells nothing
        for name, step in (
            ("1-notes-question.md", "Asking the user"),
            ("1-notes-proposal.md", "Stopping for the user"),
            ("1-report-plan.md", "Making a work through turn"),
            ("1-feedback-plan.md", "Feedback"),
            ("1-notes-pause.md", "Taking up the session"),
        ):
            with self.subTest(name=name):
                problem = open_names.check(record(items={name: ""}))[0]
                self.assertTrue(problem.startswith(f'rn: in "{step}" of conduct.md,'))


class TraceTest(unittest.TestCase):
    def test_a_plan_whose_tasks_serve_every_criterion_is_let_through(self):
        # Given: a plan with tasks beyond the sign-offs that together serve every criterion
        # When: the record's references are checked
        # Then: nothing is stopped
        self.assertEqual(trace.check(record(planned())), [])

    def test_a_task_serving_a_criterion_the_plan_lacks_is_stopped(self):
        # Given: a task whose Serves line names an attractive or a must-be criterion the plan
        #   does not have
        # When: the record's references are checked
        # Then: a single stop says, under Planning the tasks, the task and the criterion it
        #   cannot serve, what to serve instead, and why
        for criterion in ("A2", "M2"):
            with self.subTest(criterion=criterion):
                tasks = TASKS.replace("Serves: A1, M1", f"Serves: A1, M1, {criterion}")
                self.assertEqual(
                    trace.check(record(planned(tasks=tasks))),
                    [
                        (
                            f'rn: in "Planning the tasks" of conduct.md, {FOLDER}/steering.md has #3'
                            f" serve {criterion}, which no criterion of the plan has; serve only"
                            " criteria the plan lists under `# Acceptance criteria`, since each"
                            " task is judged by the criteria it serves."
                        )
                    ],
                )

    def test_a_criterion_no_task_serves_is_stopped_once_tasks_are_planned(self):
        # Given: a plan with tasks beyond the sign-offs, none of which serves one attractive or
        #   one must-be criterion
        # When: the record's references are checked
        # Then: a single stop says, under Planning the tasks, the criterion left unserved, how
        #   to serve it, and why
        for served, criterion in (("M1", "A1"), ("A1", "M1")):
            with self.subTest(criterion=criterion):
                plan = planned(tasks=TASKS.replace("Serves: A1, M1", f"Serves: {served}"))
                self.assertEqual(
                    trace.check(record(plan)),
                    [
                        (
                            f'rn: in "Planning the tasks" of conduct.md, {FOLDER}/steering.md has'
                            f" no task serving {criterion}; add {criterion} to the `Serves:` line of"
                            " the task that brings it to hold, or plan one, since a criterion no"
                            " task serves is never built."
                        )
                    ],
                )

    def test_criteria_no_task_serves_are_let_through_while_only_sign_offs_are_planned(self):
        # Given: a plan whose only tasks are the sign-offs
        # When: the record's references are checked
        # Then: nothing is stopped
        self.assertEqual(trace.check(record(PLAN)), [])

    def test_a_task_heading_out_of_form_is_left_to_the_check_of_the_plans_form(self):
        # Given: a plan whose only task beyond the sign-offs has a heading out of the template's
        #   form, serving no criterion
        # When: the record's references are checked
        # Then: nothing is stopped, since the heading is the plan form's to stop
        plan = planned(tasks=TASKS.replace("### [ ] #3:", "### #3:").replace("A1, M1", ""))
        self.assertEqual(trace.check(record(plan)), [])

    def test_a_question_item_that_does_not_serve_criteria_of_the_plan_is_stopped(self):
        # Given: a question item whose first line is not `Serves:`, names nothing, or names an
        #   attractive or a must-be criterion the plan lacks, or what is not `goal`
        # When: the record's references are checked
        # Then: a single stop says, under Asking the user, what the item's first line lacks,
        #   how to open it, and why
        fix = (
            "; open it with `Serves:` and the IDs of the criteria the question rests on, or"
            " `goal`, since the question is judged by what it serves."
        )
        for first, broken in (
            ("Which way?", "does not open with `Serves:` and what it serves"),
            ("Serves:", "does not open with `Serves:` and what it serves"),
            ("Serves: ,", "does not open with `Serves:` and what it serves"),
            ("Serves: A2", "serves A2, which is neither a criterion of the plan nor `goal`"),
            ("Serves: M2", "serves M2, which is neither a criterion of the plan nor `goal`"),
            ("Serves: goals", "serves goals, which is neither a criterion of the plan nor `goal`"),
        ):
            with self.subTest(first=first):
                name = "02-notes-question.md"
                self.assertEqual(
                    trace.check(record(items={name: first + "\n"})),
                    [f'rn: in "Asking the user" of conduct.md, {FOLDER}/open/{name} {broken}{fix}'],
                )

    def test_a_question_item_serving_criteria_of_the_plan_or_the_goal_is_let_through(self):
        # Given: a question item whose first line serves criteria of the plan, or `goal`
        # When: the record's references are checked
        # Then: nothing is stopped
        for first in ("Serves: goal", "Serves: A1, M1", "Serves: M1"):
            with self.subTest(first=first):
                items = {"02-notes-question.md": first + "\nWhy?"}
                self.assertEqual(trace.check(record(PLAN, items)), [])

    def test_a_verification_document_with_its_scenes_and_must_be_criteria_is_let_through(self):
        # Given: a verification document with a scene for each attractive criterion of the plan
        #   and each must-be criterion named in a machine check
        # When: the record's references are checked
        # Then: nothing is stopped
        self.assertEqual(trace.check(record(PLAN, verification=VERIFICATION)), [])

    def test_a_verification_document_without_its_front_matter_is_stopped(self):
        # Given: a verification document without front matter in a session past 0.9.x or one
        #   whose plan has no rn field, or with front matter lacking the `name` line, naming
        #   another document, or lacking a `version`
        # When: the record's references are checked
        # Then: a single stop says, under Working out the design, that the document lacks its
        #   front matter, what to put back, and why
        bare = VERIFICATION.split("---\n", 2)[2]
        for rn, text in (
            ("0.10.0", bare),
            ("1.0.0", bare),
            (None, bare),
            ("0.9.0", VERIFICATION.replace("name: verification\n", "")),
            ("0.9.0", VERIFICATION.replace("name: verification", "name: design")),
            ("0.9.0", VERIFICATION.replace("version: 0.1.0\n", "")),
        ):
            with self.subTest(rn=rn, text=text):
                self.assertEqual(
                    trace.check(record(PLAN, verification=text, rn=rn)),
                    [
                        (
                            'rn: in "Working out the design" of conduct.md, docs/verification.md'
                            " does not open with front matter giving `name: verification` and its"
                            " `version`; put back the front matter of the template in rn's"
                            " checklists/verification.md, since turn uses the deliverable against"
                            " the document as a checklist only by that front matter."
                        )
                    ],
                )

    def test_a_verification_document_without_front_matter_is_let_through_for_rn_0_9(self):
        # Given: a session started by rn 0.9.x, which wrote no front matter, with a verification
        #   document without one
        # When: the record's references are checked
        # Then: nothing is stopped
        bare = VERIFICATION.split("---\n", 2)[2]
        for rn in ("0.9.0", "0.9.3"):
            with self.subTest(rn=rn):
                self.assertEqual(trace.check(record(PLAN, verification=bare, rn=rn)), [])

    def test_a_document_the_plan_does_not_name_as_its_verification_is_let_through(self):
        # Given: a plan naming no verification document, and a document with neither front
        #   matter nor headings beside it
        # When: the record's references are checked
        # Then: nothing is stopped
        self.assertEqual(trace.check(record(verification="Scenes.\n")), [])

    def test_a_verification_document_missing_a_heading_is_stopped(self):
        # Given: a verification document holding its Machine checks heading but not its Scenes
        #   heading, or the other way round
        # When: the record's references are checked
        # Then: a stop says, under Working out the design, the heading the document lacks, to
        #   put it back, and why
        for missing, held in (
            ("## Scenes", "## Machine checks"),
            ("## Machine checks", "## Scenes"),
        ):
            with self.subTest(missing=missing):
                self.assertIn(
                    'rn: in "Working out the design" of conduct.md, docs/verification.md has no'
                    f" `{missing}` heading; put it back as the template in rn's"
                    " checklists/verification.md gives it, since rn's checks find each"
                    " criterion's scene and machine check under it.",
                    trace.check(record(NAMES_VERIFICATION, verification=held + "\n")),
                )

    def test_an_attractive_criterion_without_a_scene_is_stopped(self):
        # Given: a verification document with no scene for an attractive criterion of the plan
        # When: the record's references are checked
        # Then: a single stop says, under Working out the design, the criterion without a
        #   scene, what to add, and why
        plan = PLAN.replace("total to 0.\n", "total to 0.\n- A2: Another gain.\n", 1)
        self.assertEqual(
            trace.check(record(plan, verification=VERIFICATION)),
            [
                (
                    'rn: in "Working out the design" of conduct.md, docs/verification.md has no'
                    " scene for A2; add `### A2:` under `## Scenes` with what is put in and what"
                    " must happen, since each attractive criterion is checked by the scenes the user"
                    " approved."
                )
            ],
        )

    def test_a_scene_for_a_criterion_the_plan_lacks_is_stopped(self):
        # Given: a verification document with a scene headed by an attractive or a must-be
        #   criterion the plan does not have
        # When: the record's references are checked
        # Then: a single stop says, under Working out the design, the criterion the scene
        #   names, how to head scenes, and why
        for criterion in ("A3", "M3"):
            with self.subTest(criterion=criterion):
                text = VERIFICATION.replace(
                    "## Machine checks", f"### {criterion}: Gone\n\n## Machine checks"
                )
                self.assertEqual(
                    trace.check(record(PLAN, verification=text)),
                    [
                        (
                            'rn: in "Working out the design" of conduct.md, docs/verification.md'
                            f" has a scene for {criterion}, which no criterion of the plan has; head"
                            " each scene with the ID of an attractive criterion of the plan, since"
                            " rn's checks find each criterion's scene by its ID."
                        )
                    ],
                )

    def test_a_must_be_criterion_no_scene_or_check_names_is_stopped(self):
        # Given: a verification document that names a must-be criterion of the plan in no
        #   scene's pass and no machine check's criteria, only a longer ID beginning with it
        # When: the record's references are checked
        # Then: a single stop says, under Working out the design, the criterion left unchecked,
        #   where to name it, and why
        text = VERIFICATION.replace("| M1 |", "| M10 |")
        self.assertEqual(
            trace.check(record(PLAN, verification=text)),
            [
                (
                    'rn: in "Working out the design" of conduct.md, docs/verification.md names M1'
                    " in no scene's pass and no machine check's criteria; name M1 in the machine"
                    " check that judges it, or in the pass of a scene where no machine can, since a"
                    " must-be criterion no check covers breaks unseen."
                )
            ],
        )

    def test_a_must_be_criterion_named_in_a_scenes_pass_is_let_through(self):
        # Given: a verification document naming a must-be criterion only in a scene's pass
        # When: the record's references are checked
        # Then: nothing is stopped
        text = VERIFICATION.replace("| M1 |", "| |").replace("is 0.", "is 0 (M1).")
        self.assertEqual(trace.check(record(PLAN, verification=text)), [])


if __name__ == "__main__":
    unittest.main()
