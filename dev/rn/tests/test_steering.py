"""The tests of the steering's form, which a steering is held to at every keep, of the plan the
orchestrator writes, held to the plan's part of it, and of the Markdown the user reads of it."""

from __future__ import annotations

import copy
import json
import unittest

from helpers import (
    PLAN_CHECKLIST,
    STEERED,
    plan,
    schema,
    steered,
    steering,
    task,
    template,
)


def changed(data: dict, path: tuple, value: object) -> dict:
    """A copy of the data with the value at the path, a key or index each, set as given."""
    found = copy.deepcopy(data)
    at = found
    for step in path[:-1]:
        at = at[step]
    at[path[-1]] = value
    return found


class FormTest(unittest.TestCase):
    """What a steering is held to at every keep: forms/steering.json, each text some words, a
    sign-off waiting only at a stage of one, the pull request's URL, and the plan's IDs, each named
    one the plan holds, no task building on itself and each goal served."""

    def test_rns_form_is_one_lanes_schema_reader_reads_whole(self):
        # Given: rn's form of the steering.
        # When: lane's reader of JSON Schema reads it.
        # Then: it reads it whole, so no value is let through by a keyword left unread.
        self.assertIsNone(schema.checked(steering.FORM))

    def test_a_steering_in_form_holds(self):
        cases = {
            "the whole": STEERED,
            "a plan not yet made": steered(part=plan(goals=(), criteria=(), tasks=())),
            "no task left": steered(part=plan(tasks=())),
            "a pull request not opened": steered(pr=None),
            "points open": steered(opened=("One.\nStill open.", "Two.")),
            "a sign-off waiting at its stage": steered(stage="ux", waiting=True),
            "a task serving two criteria": steered(part=plan(tasks=[task(serves=("AC1", "AC2"))])),
            "a task building on a task left": steered(
                part=plan(tasks=[task(), task("T2", builds_on=("T1",))])
            ),
            "a task numbered above 9": steered(part=plan(tasks=[task("T10")])),
        }
        for name, data in cases.items():
            with self.subTest(name=name):
                # Given: a steering in its form.
                # When: it is held to its form.
                # Then: it holds.
                self.assertEqual(steering.out_of_form(data), "")

    def test_a_task_building_on_a_task_done_holds(self):
        # Given: a steering whose task builds on T1, which is done and so no longer in the plan.
        data = steered(part=plan(tasks=[task("T2", builds_on=("T1",))]))
        # When: it is held to its form, T1 among the tasks done.
        # Then: it holds.
        self.assertEqual(steering.out_of_form(data, {"T1"}), "")

    def test_a_steering_out_of_its_schema_is_named_at_its_place(self):
        cases = {
            "$: expected an object, found []": [],
            '$: expected the key "status", found an object without it': {
                k: v for k, v in STEERED.items() if k != "status"
            },
            '$.status.stage: expected one of "goal", "ux", "architecture", "build",'
            ' "deliverable", "learnings", "finished", found "done"': changed(
                STEERED, ("status", "stage"), "done"
            ),
            "$.plan.tasks[0].completion_criteria: expected at least 1 item, found none": changed(
                STEERED, ("plan", "tasks", 0, "completion_criteria"), []
            ),
            '$.plan.goals[0]: expected only the keys "id", "what", "why", found the key "how"': (
                changed(STEERED, ("plan", "goals", 0, "how"), "x")
            ),
            "$.session.pr: expected a string or null, found 7": changed(
                STEERED, ("session", "pr"), 7
            ),
        }
        for point, data in cases.items():
            with self.subTest(point=point):
                # Given: a steering out of its form's schema.
                # When: it is held to its form.
                # Then: the point is named at its place, what was expected and what was found.
                self.assertEqual(steering.out_of_form(data), point)

    def test_what_a_schema_cannot_hold_is_named_at_its_place(self):
        cases = {
            '$.session.title: expected some words, found "  "': changed(
                STEERED, ("session", "title"), "  "
            ),
            '$.status.open_questions[1]: expected some words, found ""': steered(
                opened=("One.", "")
            ),
            '$.plan.goals[0].why: expected some words, found "\\n"': changed(
                STEERED, ("plan", "goals", 0, "why"), "\n"
            ),
            "$.status.awaiting_signoff: expected false at the build stage, which has no"
            " sign-off, found true": steered(stage="build", waiting=True),
            "$.session.pr: expected the pull request's URL, or null before it is opened, found"
            " https://github.com/o/r": steered(pr="https://github.com/o/r"),
        }
        for point, data in cases.items():
            with self.subTest(point=point):
                # Given: a steering its schema holds, with a value out of its form beyond it.
                # When: it is held to its form.
                # Then: the point is named at its place.
                self.assertEqual(steering.out_of_form(data), point)


class PlanTest(unittest.TestCase):
    """What the plan is held to beyond its schema, in the steering and as the part the orchestrator
    writes: each ID of its letters numbered from 1 and once, each ID named one the plan holds or a
    task done, no task building on itself, and each goal served by a criterion."""

    def test_ids_out_of_form_are_named_at_their_place(self):
        two = [task(), task()]
        cases = {
            "$.goals[0].id: expected G<n>, n from 1, found Goal1": changed(
                plan(), ("goals", 0, "id"), "Goal1"
            ),
            "$.acceptance_criteria[1].id: expected AC<n>, n from 1, found AC0": changed(
                plan(), ("acceptance_criteria", 1, "id"), "AC0"
            ),
            "$.tasks[0].id: expected T<n>, n from 1, found T01": plan(tasks=[task("T01")]),
            "$.tasks[0].id: expected T<n>, n from 1, found G1": plan(tasks=[task("G1")]),
            "$.acceptance_criteria[1].id: expected each ID once, found AC1 again": changed(
                plan(), ("acceptance_criteria", 1, "id"), "AC1"
            ),
            "$.tasks[1].id: expected each ID once, found T1 again": plan(tasks=two),
        }
        for point, part in cases.items():
            with self.subTest(point=point):
                # Given: a plan whose ID is out of its form.
                # When: it is held to its form as a part the orchestrator wrote.
                # Then: the point is named at its place in the part.
                self.assertEqual(steering.part_out(part), point)

    def test_an_id_named_that_the_plan_does_not_hold_is_named(self):
        cases = {
            "$.acceptance_criteria[0].contributes_to: expected only goals the plan holds, found"
            " G2": changed(plan(), ("acceptance_criteria", 0, "contributes_to"), ["G2", "G3"]),
            "$.tasks[0].completion_criteria[0].contributes_to: expected only acceptance"
            " criteria the plan holds, found AC3": plan(tasks=[task(serves=("AC3",))]),
            "$.tasks[0].completion_criteria[0].contributes_to: expected only acceptance"
            " criteria the plan holds, found G1": plan(tasks=[task(serves=("G1",))]),
            "$.tasks[0].builds_on: expected only tasks or tasks done the plan holds, found T2": (
                plan(tasks=[task(builds_on=("T2",))])
            ),
        }
        for point, part in cases.items():
            with self.subTest(point=point):
                # Given: a plan naming an ID it does not hold.
                # When: it is held to its form, no task done.
                # Then: the point is named at its place.
                self.assertEqual(steering.part_out(part), point)

    def test_a_task_building_on_itself_is_named(self):
        cases = {
            "at once": [task(builds_on=("T1",))],
            "through another": [task(builds_on=("T2",)), task("T2", builds_on=("T1",))],
            "through two others": [
                task(builds_on=("T3",)),
                task("T2", builds_on=("T1",)),
                task("T3", builds_on=("T2",)),
            ],
        }
        for name, tasks in cases.items():
            with self.subTest(name=name):
                # Given: a plan whose first task builds on itself.
                # When: it is held to its form.
                # Then: the point is named at that task.
                self.assertEqual(
                    steering.part_out(plan(tasks=tasks)),
                    "$.tasks[0].builds_on: expected no task it builds on to build on it, found T1"
                    " building on itself",
                )

    def test_tasks_building_on_one_another_in_a_line_or_on_one_task_hold(self):
        cases = {
            "a line": [task(), task("T2", builds_on=("T1",)), task("T3", builds_on=("T2",))],
            "two on one": [task(), task("T2", builds_on=("T1",)), task("T3", builds_on=("T1",))],
            "one on two": [task(), task("T2"), task("T3", builds_on=("T1", "T2"))],
        }
        for name, tasks in cases.items():
            with self.subTest(name=name):
                # Given: a plan whose tasks build on one another with no task on itself.
                # When: it is held to its form.
                # Then: it holds.
                self.assertEqual(steering.part_out(plan(tasks=tasks)), "")

    def test_a_goal_no_criterion_serves_is_named(self):
        # Given: a plan whose second goal no criterion contributes to.
        goals = [*plan()["goals"], {"id": "G2", "what": "Admins see who signed in.", "why": "W."}]
        # When: it is held to its form.
        # Then: the point is named at that goal.
        self.assertEqual(
            steering.part_out(plan(goals=goals)),
            "$.goals[1]: expected an acceptance criterion contributing to G2, found none",
        )

    def test_a_part_out_of_the_plans_schema_is_named_at_its_place_in_the_part(self):
        # Given: a part the orchestrator wrote whose task has no completion criterion.
        part = plan(tasks=[{k: v for k, v in task().items() if k != "completion_criteria"}])
        # When: it is held to its form.
        # Then: the point is named at its place in the part, not in the steering.
        self.assertEqual(
            steering.part_out(part),
            '$.tasks[0]: expected the key "completion_criteria", found an object without it',
        )

    def test_a_part_with_an_empty_text_is_named(self):
        # Given: a part whose task says nothing of its result.
        part = changed(plan(), ("tasks", 0, "what"), "")
        # When: it is held to its form.
        # Then: the point is named at its place in the part.
        self.assertEqual(steering.part_out(part), '$.tasks[0].what: expected some words, found ""')

    def test_a_steerings_plan_out_of_form_is_named_at_its_place_in_the_steering(self):
        # Given: a steering whose task serves a criterion its plan does not hold.
        data = steered(part=plan(tasks=[task(serves=("AC3",))]))
        # When: it is held to its form.
        # Then: the point is named at its place in the steering.
        self.assertEqual(
            steering.out_of_form(data),
            "$.plan.tasks[0].completion_criteria[0].contributes_to: expected only acceptance"
            " criteria the plan holds, found AC3",
        )


class MarkdownTest(unittest.TestCase):
    """The Markdown the user reads of the steering, written from it: the plan in the form of rn's
    plan checklist, then where the session stands."""

    def test_the_plans_markdown_holds_rns_plan_checklists_format(self):
        # Given: rn's plan checklist's Format, the first fence under its heading, and the
        # Markdown of a steering with every part of a plan.
        with open(PLAN_CHECKLIST, encoding="utf-8") as f:
            lines = f.read().splitlines()
        heading = lines.index("## Format")
        fences = [n for n in range(heading, len(lines)) if lines[n].startswith("```")]
        asked = template.read("\n".join(lines[fences[0] + 1 : fences[1]]))
        said = steering.markdown(STEERED)
        # When: the plan's part of it, up to where the session stands, is held to the Format.
        # Then: it holds.
        self.assertEqual(template.held(asked, said.split("\n## Where it stands")[0]), "")

    def test_the_markdown_gives_the_plan_and_where_the_session_stands(self):
        # Given: a steering with two goals, the second's words and why of two lines each, a task
        # building on two, of two lines, as is its completion criterion, a criterion of two lines,
        # a sign-off waiting, Next of two lines and two points open.
        goals = [*plan()["goals"], {"id": "G2", "what": "Admins\nsee it.", "why": "They\naudit."}]
        criteria = changed(plan()["acceptance_criteria"], (1, "contributes_to"), ["G1", "G2"])
        criteria[0]["what"] = "A user signs in\nwith their email."
        three = task("T3", serves=("AC1", "AC2"), builds_on=("T1", "T2"))
        three["what"] = "The part\nT3."
        three["completion_criteria"][0]["what"] = "It does\nwhat it serves."
        data = steered(
            part=plan(goals=goals, criteria=criteria, tasks=[three]),
            stage="goal",
            waiting=True,
            next_step="2. Ask the user\nthe first point.",
            opened=("Which email?\nOr a phone.", "Two."),
        )
        # When: its Markdown is written.
        # Then: it holds the title, the goals with why, each criterion and task with what it
        # serves or builds on, each completion criterion, then the stage with the sign-off
        # waiting, Next and each point open.
        self.assertEqual(
            steering.markdown(data),
            "# Add login\n\n"
            "## Goals\n\n"
            "- G1: Users sign in\n\n  So their carts stay theirs.\n\n"
            "- G2: Admins\n  see it.\n\n  They\n  audit.\n\n"
            "## Acceptance criteria\n\n"
            "- AC1: A user signs in\n  with their email. Serves G1.\n\n"
            "- AC2: A signed-in user sees only their cart, on every page. Serves G1 and G2.\n\n"
            "## Tasks\n\n"
            "- T3: The part\n  T3. Builds on T1 and T2.\n\n"
            "  - It does\n    what it serves. Serves AC1 and AC2.\n\n"
            "## Where it stands\n\n"
            "Stage: goal, the goal sign-off waiting.\n\n"
            "Next: 2. Ask the user\nthe first point.\n\n"
            "Open:\n\n- Which email?\n  Or a phone.\n- Two.\n",
        )

    def test_a_plan_not_made_and_nothing_open_show_as_none(self):
        # Given: a steering at its start, with no goal, criterion or task and nothing open.
        data = steered(part=plan(goals=(), criteria=(), tasks=()), stage="ux")
        # When: its Markdown is written.
        # Then: it holds the title and where it stands alone, no task building on any as none.
        self.assertEqual(
            steering.markdown(data),
            "# Add login\n\n## Where it stands\n\nStage: ux.\n\n"
            "Next: 2. Ask the user the first point.\n\nOpen:\n\nNone.\n",
        )

    def test_a_task_building_on_none_says_so(self):
        # Given: a steering whose task builds on no task.
        # When: its Markdown is written.
        # Then: the task says it builds on none.
        self.assertIn("- T1: The part T1. Builds on none.\n", steering.markdown(STEERED))


class ReadTest(unittest.TestCase):
    """How a steering's text is read: the steering, its stage, and what the plan says."""

    def test_a_signoff_waits_only_where_the_steering_says_true(self):
        for value, waiting in ((True, "ux"), (False, None), (1, None), (2, None)):
            with self.subTest(value=value):
                # Given: a steering at the ux stage whose awaiting_signoff is true, false, or a
                # number, as only a hand would write it.
                data = changed(steered(stage="ux"), ("status", "awaiting_signoff"), value)
                # When: the sign-off it sets waiting is read.
                # Then: it is the ux's for true alone.
                self.assertEqual(steering.signoff_of(json.dumps(data)), waiting)

    def test_a_text_that_is_no_json_is_no_steering(self):
        for text in (None, "", "{", "---\nstage: goal\n---\n"):
            with self.subTest(text=text):
                # Given: no text, or a text that is no JSON.
                # When: it is read as a steering, and its stage.
                # Then: neither is there.
                self.assertEqual((steering.read(text), steering.stage_of(text)), (None, None))

    def test_the_stage_of_a_steering_is_read(self):
        # Given: a steering at the ux stage, as JSON.
        text = json.dumps(steered(stage="ux"))
        # When: its stage is read.
        # Then: it is ux.
        self.assertEqual(steering.stage_of(text), "ux")

    def test_a_json_without_a_stage_has_none(self):
        for text in ("[]", "{}", '{"status": {}}', '{"status": 1}'):
            with self.subTest(text=text):
                # Given: JSON that holds no stage where a steering holds it.
                # When: its stage is read.
                # Then: there is none.
                self.assertIsNone(steering.stage_of(text))

    def test_what_the_plan_says_of_each_goal_and_criterion_is_given_by_id(self):
        # Given: a plan whose goal ends with a full stop.
        part = changed(plan(), ("goals", 0, "what"), "Users sign in.")
        # When: what it says of each goal and criterion is read.
        # Then: each goal is given with why, in one sentence each, and each criterion as it is.
        self.assertEqual(
            steering.decided(part),
            {
                "G1": "Users sign in. So their carts stay theirs.",
                "AC1": "A user signs in with their email.",
                "AC2": "A signed-in user sees only their cart, on every page.",
            },
        )

    def test_the_tasks_done_are_told_with_what_comes_next(self):
        # Given: a plan of two tasks.
        part = plan(tasks=[task(), task("T2")])
        # When: the line told for T1 and T2 done, or for none, is made.
        # Then: it names each with what it made, and the last weighed next; none for none.
        self.assertEqual(
            (steering.told_done(part, ["T1", "T2"]), steering.told_done(part, [])),
            (
                (
                    "Done: T1, the part T1; T2, the part T2. Next: what T2 brought is weighed"
                    " against the plan."
                ),
                "",
            ),
        )


if __name__ == "__main__":
    unittest.main()
