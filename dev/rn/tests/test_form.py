import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "rn" / "hooks"))

from checks import Record, open_names, steering_form, trace

PLAN = """---
rn: 0.9.0
pr: https://github.com/o/r/pull/1
status: running
artifact-language: English
conversation-language: English
readme: README.md
design: docs/design.md
verification: docs/verification.md
---

# Goal

# Acceptance criteria

## Attractive quality

- A1: a gain

## Must-be quality

- M1: what is taken for granted

# Assumptions

# Rules

# Tasks

### [x] #1: Plan sign-off
### [ ] #2: Design sign-off

# Not yet specified
"""

PLANNED = PLAN.replace(
    "### [ ] #2: Design sign-off\n",
    "### [x] #2: Design sign-off\n### [ ] #3: Build it\n\nServes: A1, M1\n",
)

VERIFICATION = """---
name: verification
version: 0.1.0
---

## Scenes

### A1: a gain

- what is put in

  Passes when it happens.

## Machine checks

| Command | Criteria |
|---|---|
| make test | M1 |
"""


class StopAssertions(unittest.TestCase):
    def assertStops(self, sentences, *words):
        """One sentence of rn's stop names every word given, and says why the form matters."""
        named = [s for s in sentences if all(w in s for w in words)]
        self.assertTrue(named, f"no stop names {words}: {sentences}")
        self.assertTrue(named[0].startswith("rn: "), named[0])
        self.assertIn(", since ", named[0])


class SteeringForm(StopAssertions):
    def test_a_plan_in_the_template_form_is_let_through(self):
        # Given: a plan with every key, heading and task heading of the template
        # When: the plan's form is checked
        # Then: nothing is stopped
        self.assertEqual(steering_form.check(Record(".rn/s", PLAN)), [])

    def test_a_plan_without_front_matter_is_stopped(self):
        # Given: a plan whose keys are not between `---` lines at its top, missing the first or the last
        # When: the plan's form is checked
        # Then: rn stops it, naming the plan and its front matter, and why the form matters
        for plan in (PLAN.replace("---\n", "", 1), PLAN.replace("\n---\n", "\n", 1)):
            with self.subTest(plan=plan[:20]):
                self.assertStops(
                    steering_form.check(Record(".rn/s", plan)), ".rn/s/steering.md", "front matter"
                )

    def test_a_plan_missing_a_key_of_the_template_is_stopped(self):
        # Given: a plan whose front matter lacks one key the template gives
        # When: the plan's form is checked
        # Then: rn stops it, naming the plan and the key, and why the form matters
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
                plan = "\n".join(
                    line for line in PLAN.split("\n") if not line.startswith(key + ":")
                )
                self.assertStops(
                    steering_form.check(Record(".rn/s", plan)), ".rn/s/steering.md", f"`{key}`"
                )

    def test_a_status_other_than_running_or_finished_is_stopped(self):
        # Given: a plan whose status is neither running nor finished
        # When: the plan's form is checked
        # Then: rn stops it, naming the plan and the status, and why the form matters
        for status in ("paused", "Running"):
            with self.subTest(status=status):
                plan = PLAN.replace("status: running", f"status: {status}")
                self.assertStops(
                    steering_form.check(Record(".rn/s", plan)), ".rn/s/steering.md", f"`{status}`"
                )

    def test_a_finished_status_is_let_through(self):
        # Given: a plan whose status is finished
        # When: the plan's form is checked
        # Then: nothing is stopped
        plan = PLAN.replace("status: running", "status: finished")
        self.assertEqual(steering_form.check(Record(".rn/s", plan)), [])

    def test_a_plan_missing_a_heading_of_the_template_is_stopped(self):
        # Given: a plan without one heading of the template, or with it at another level
        # When: the plan's form is checked
        # Then: rn stops it, naming the plan and the heading, and why the form matters
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
            for written in ("", "#" + heading):
                with self.subTest(heading=heading, written=written):
                    plan = PLAN.replace(f"\n{heading}\n", f"\n{written}\n")
                    self.assertStops(
                        steering_form.check(Record(".rn/s", plan)),
                        ".rn/s/steering.md",
                        f"`{heading}`",
                    )

    def test_a_task_heading_out_of_the_template_form_is_stopped(self):
        # Given: a task heading other than `### [ ] #N: name` or `### [x] #N: name`
        # When: the plan's form is checked
        # Then: rn stops it, naming the plan and the heading, and why the form matters
        for heading in (
            "### #2: Design sign-off",
            "### [X] #2: Design sign-off",
            "### [ ] 2: Design sign-off",
            "### [ ] #2 Design sign-off",
            "### [ ] #2: ",
            "### [] #2: Design sign-off",
        ):
            with self.subTest(heading=heading):
                plan = PLAN.replace("### [ ] #2: Design sign-off", heading)
                self.assertStops(
                    steering_form.check(Record(".rn/s", plan)), ".rn/s/steering.md", f"`{heading}`"
                )

    def test_a_task_id_given_twice_is_stopped(self):
        # Given: a plan with two tasks numbered #2
        # When: the plan's form is checked
        # Then: rn stops it, naming the plan and #2, and why the form matters
        plan = PLAN.replace("# Not yet specified", "### [ ] #2: Again\n\n# Not yet specified")
        self.assertStops(steering_form.check(Record(".rn/s", plan)), ".rn/s/steering.md", "#2")

    def test_a_criterion_id_given_twice_is_stopped(self):
        # Given: a plan whose must-be criterion takes the ID A1 an attractive one has
        # When: the plan's form is checked
        # Then: rn stops it, naming the plan and A1, and why the form matters
        plan = PLAN.replace("- M1:", "- A1:")
        self.assertStops(steering_form.check(Record(".rn/s", plan)), ".rn/s/steering.md", "A1")


class OpenNames(StopAssertions):
    def test_items_named_number_kind_about_are_let_through(self):
        # Given: an item of open/ named {NN}-{kind}-{about}.md with each kind
        # When: the names in open/ are checked
        # Then: nothing is stopped
        for name in ("04-report-task-3.md", "02-feedback-plan.md", "01-notes-question.md"):
            with self.subTest(name=name):
                self.assertEqual(open_names.check(Record(".rn/s", PLAN, {name: ""})), [])

    def test_an_item_not_named_number_kind_about_is_stopped(self):
        # Given: an item of open/ whose name lacks the number, a known kind, the about or `.md`
        # When: the names in open/ are checked
        # Then: rn stops it, naming the item, and why the form matters
        for name in (
            "1-notes-plan.md",
            "notes-plan.md",
            "01-note-plan.md",
            "01-Notes-plan.md",
            "01-notesplan.md",
            "01-notes-.md",
            "01-notes-plan.txt",
        ):
            with self.subTest(name=name):
                self.assertStops(
                    open_names.check(Record(".rn/s", PLAN, {name: ""})), f".rn/s/open/{name}"
                )


class Trace(StopAssertions):
    def test_tasks_serving_every_criterion_the_plan_holds_are_let_through(self):
        # Given: a planned task serving each criterion the plan holds
        # When: the references to criteria are checked
        # Then: nothing is stopped
        self.assertEqual(trace.check(Record(".rn/s", PLANNED)), [])

    def test_a_task_serving_a_criterion_the_plan_does_not_hold_is_stopped(self):
        # Given: a task whose Serves line names A2, which the plan does not hold
        # When: the references to criteria are checked
        # Then: rn stops it, naming the plan, the task and A2, and why the form matters
        plan = PLANNED.replace("Serves: A1, M1", "Serves: A1, M1, A2")
        self.assertStops(trace.check(Record(".rn/s", plan)), ".rn/s/steering.md", "#3", "A2")

    def test_once_tasks_are_planned_a_criterion_no_task_serves_is_stopped(self):
        # Given: a planned task serving A1 alone, with M1 served by none
        # When: the references to criteria are checked
        # Then: rn stops it, naming the plan and M1, and why it matters
        plan = PLANNED.replace("Serves: A1, M1", "Serves: A1")
        self.assertStops(trace.check(Record(".rn/s", plan)), ".rn/s/steering.md", "M1")

    def test_before_tasks_are_planned_criteria_without_a_task_are_let_through(self):
        # Given: a plan with only its sign-offs as tasks
        # When: the references to criteria are checked
        # Then: nothing is stopped
        self.assertEqual(trace.check(Record(".rn/s", PLAN)), [])

    def test_a_question_serving_criteria_the_plan_holds_or_the_goal_is_let_through(self):
        # Given: a question item whose first line serves criteria the plan holds, or the goal
        # When: the references to criteria are checked
        # Then: nothing is stopped
        for first in ("Serves: A1", "Serves: A1, M1", "Serves: goal"):
            with self.subTest(first=first):
                items = {"03-notes-question.md": first + "\nWhich one?\n"}
                self.assertEqual(trace.check(Record(".rn/s", PLAN, items)), [])

    def test_a_question_not_opening_with_what_it_serves_is_stopped(self):
        # Given: a question item whose first line is not Serves with criteria the plan holds or the goal
        # When: the references to criteria are checked
        # Then: rn stops it, naming the item, and why it matters
        for text in (
            "Which one?\n",
            "\nServes: A1\n",
            "Serves:\n",
            "Serves: A9\n",
            "Serves: goals\n",
        ):
            with self.subTest(text=text):
                items = {"03-notes-question.md": text}
                self.assertStops(
                    trace.check(Record(".rn/s", PLAN, items)), ".rn/s/open/03-notes-question.md"
                )

    def test_an_item_other_than_a_question_needs_no_serves_line(self):
        # Given: a notes item about the plan, not a question, with no Serves line
        # When: the references to criteria are checked
        # Then: nothing is stopped
        items = {"03-notes-plan.md": "Where the plan stands.\n"}
        self.assertEqual(trace.check(Record(".rn/s", PLAN, items)), [])

    def test_a_verification_document_in_its_form_is_let_through(self):
        # Given: a verification document with its front matter, a scene for A1 and M1 in a machine check
        # When: the verification document is checked
        # Then: nothing is stopped
        self.assertEqual(trace.check(Record(".rn/s", PLAN, {}, VERIFICATION, "1.0.0")), [])

    def test_a_verification_document_without_its_name_and_version_is_stopped(self):
        # Given: a verification document of a session later than rn 0.9 without `name: verification` or `version`
        # When: the verification document is checked
        # Then: rn stops it, naming the document and its front matter, and why the form matters
        for text in (
            VERIFICATION.split("---\n", 2)[2],
            VERIFICATION.replace("name: verification", "name: plan"),
            VERIFICATION.replace("version: 0.1.0\n", ""),
        ):
            with self.subTest(text=text[:40]):
                self.assertStops(
                    trace.check(Record(".rn/s", PLAN, {}, text, "0.10.0")),
                    "docs/verification.md",
                    "front matter",
                )

    def test_a_session_of_rn_0_9_may_have_a_verification_document_without_front_matter(self):
        # Given: a session whose rn field is 0.9.x, with a verification document without front matter
        # When: the verification document is checked
        # Then: nothing is stopped
        text = VERIFICATION.split("---\n", 2)[2]
        self.assertEqual(trace.check(Record(".rn/s", PLAN, {}, text, "0.9.3")), [])

    def test_a_verification_document_without_scenes_or_machine_checks_is_stopped(self):
        # Given: a verification document without the `## Scenes` or the `## Machine checks` heading
        # When: the verification document is checked
        # Then: rn stops it, naming the document and the heading, and why the form matters
        for heading in ("## Scenes", "## Machine checks"):
            with self.subTest(heading=heading):
                text = VERIFICATION.replace(heading + "\n", "")
                self.assertStops(
                    trace.check(Record(".rn/s", PLAN, {}, text, "1.0.0")),
                    "docs/verification.md",
                    f"`{heading}`",
                )

    def test_an_attractive_criterion_without_its_scene_is_stopped(self):
        # Given: a plan with A2, and a verification document with a scene for A1 alone
        # When: the verification document is checked
        # Then: rn stops it, naming the document and A2, and why the form matters
        plan = PLAN.replace("- A1: a gain\n", "- A1: a gain\n- A2: another gain\n")
        self.assertStops(
            trace.check(Record(".rn/s", plan, {}, VERIFICATION, "1.0.0")),
            "docs/verification.md",
            "`### A2:`",
        )

    def test_a_scene_for_a_criterion_the_plan_does_not_hold_is_stopped(self):
        # Given: a verification document with a scene for A7, which the plan does not hold
        # When: the verification document is checked
        # Then: rn stops it, naming the document and A7, and why it matters
        text = VERIFICATION.replace("## Machine checks", "### A7: gone\n\n## Machine checks")
        self.assertStops(
            trace.check(Record(".rn/s", PLAN, {}, text, "1.0.0")), "docs/verification.md", "A7"
        )

    def test_a_must_be_criterion_named_in_no_pass_and_no_machine_check_is_stopped(self):
        # Given: a verification document naming M1 only outside a scene's pass and a check's criteria, or only as part of M10
        # When: the verification document is checked
        # Then: rn stops it, naming the document and M1, and why it matters
        for text in (
            VERIFICATION.replace("| M1 |", "| M10 |"),
            VERIFICATION.replace("| M1 |", "| |").replace(
                "- what is put in", "- what is put in for M1"
            ),
        ):
            with self.subTest(text=text):
                self.assertStops(
                    trace.check(Record(".rn/s", PLAN, {}, text, "1.0.0")),
                    "docs/verification.md",
                    "M1",
                )

    def test_a_must_be_criterion_named_in_a_scenes_pass_is_let_through(self):
        # Given: a verification document naming M1 in a scene's pass and in no machine check
        # When: the verification document is checked
        # Then: nothing is stopped
        text = VERIFICATION.replace("| M1 |", "| |").replace(
            "it happens.", "it happens, as M1 asks."
        )
        self.assertEqual(trace.check(Record(".rn/s", PLAN, {}, text, "1.0.0")), [])

    def test_a_verification_document_the_plan_names_but_that_does_not_exist_is_not_checked(self):
        # Given: a plan naming a verification document that does not exist
        # When: the references to criteria are checked
        # Then: nothing about the verification document is stopped
        self.assertEqual(trace.check(Record(".rn/s", PLAN, {}, None, "1.0.0")), [])


if __name__ == "__main__":
    unittest.main()
