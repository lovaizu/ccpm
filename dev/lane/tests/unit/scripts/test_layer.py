"""lay.py's course: the proposal printed as each step will read, for the developer AI's approval;
once approved, written word for word into its plugin from the same file, Claude Code's check run on
it, and the proposal removed; and a plugin laid before brought up to lane's code."""

import json
import os
import subprocess
import unittest
from typing import Any
from unittest import mock

import helpers
from helpers import layer, proposal

# What `lay.py write` says of the README's proposal.
WROTE = """Wrote steps 2 and 3 of writer into agents/writer.md.
Wrote the hooks of writer into hooks/hooks.json.
Wrote the lanes laid into hooks/lanes.json.
Put lane's code in hooks/lane/.
claude plugin validate passed.
Removed the proposal {proposal}.
Removed its folder {folder}.
"""
REVIEWER = "---\nname: reviewer\nbackground: true\n---\n\n## Steps\n\n1. Compare the entries.\n"
# A subagent the routes may start, whose name sorts before lead's.
EDITOR = "---\nname: editor\nbackground: true\n---\n\n## Steps\n\n1. Edit the entries.\n"
# What `lay.py print` prints of the README's proposal with docs/routes.md's routes.
ROUTES_PRINTED = f"""Routes of lead, laid on its step 1:
  first             start writer
  writer `written`  start reviewer
  reviewer `more`   start writer
  reviewer `good`   start no more

Lanes of writer, each hook acting in writer alone:
  step 2  run:   {helpers.RUN:<{len(helpers.END_WRITER)}}  hook run_only
  step 3  write: {helpers.WRITE:<{len(helpers.END_WRITER)}}  hook write_only
  step 4  end:   {helpers.END_WRITER}  hook follow_routes

2. Read the commits since then with `git log --oneline`. Run only `git log --oneline`.
3. Write the new entries into `CHANGELOG.md`. Write only `CHANGELOG.md`.
4. Reply with the entries you wrote. {helpers.END_WRITER}

Lanes of lead, each hook acting in lead alone:
  step 1  follow: {helpers.FOLLOW}  hook follow_routes

1. Have writer write the entries for the next release and reviewer review them. {helpers.FOLLOW}

Lanes of reviewer, each hook acting in reviewer alone:
  step 2  end: {helpers.END_REVIEWER}  hook follow_routes

2. Compare them with the commits, and reply with what you found. {helpers.END_REVIEWER}
"""
# What `lay.py write` says of it.
ROUTES_WROTE = """Wrote steps 2, 3 and 4 of writer into agents/writer.md.
Wrote step 1 of lead into agents/lead.md.
Wrote step 2 of reviewer into agents/reviewer.md.
Wrote the hooks of writer, lead and reviewer into hooks/hooks.json.
Wrote the lanes laid and the routes into hooks/lanes.json.
Put lane's code in hooks/lane/.
claude plugin validate passed.
"""


class LayerTest(helpers.LayTest):
    def lanes_json(self) -> dict:
        """The plugin's hooks/lanes.json."""
        return self.read_json(os.path.join(self.plugin, "hooks", "lanes.json"))

    def wrote(self, returncode: int = 0, missing: bool = False) -> str:
        """What `lay.py write` says of the proposal kept, Claude Code's check exiting with the code
        given, or claude not on PATH."""
        done = subprocess.CompletedProcess([], returncode, "out\n", "err\n")
        real = subprocess.run

        def ran(args: list, **given: Any) -> subprocess.CompletedProcess:
            # An adapter is run as it is, and Claude Code's check stood in for.
            if args[0] != "claude":
                return real(args, **given)
            if missing:
                raise FileNotFoundError()
            return done

        with mock.patch.object(layer.subprocess, "run", side_effect=ran) as run:
            said = layer.written(helpers.PROPOSED)
        self.assertEqual(run.call_args.args[0], ["claude", "plugin", "validate", "changelog"])
        return said


class TestPrinted(LayerTest):
    def test_the_readmes_proposal_is_printed_as_the_readme_shows_it(self):
        # Given: the README's proposal
        # When: it is printed
        # Then: it reads as the README's walkthrough shows
        self.assertEqual(layer.printed(helpers.PROPOSED), helpers.PRINTED)

    def test_a_step_whose_lanes_are_taken_out_is_shown_so(self):
        # Given: the README's lanes laid, and a proposal laying step 3 alone
        self.lay()
        self.propose(self.proposal(steps=[helpers.STEPS[1]]))
        # When: it is printed
        # Then: step 2 is shown with its lane taken out, and as it will read
        self.assertEqual(
            layer.printed(helpers.PROPOSED),
            "Lanes of writer, each hook acting in writer alone:\n"
            "  step 3  write: Write only `CHANGELOG.md`.  hook write_only\n"
            "  step 2  no lane: the sentences laid before taken out\n"
            "\n"
            "3. Write the new entries into `CHANGELOG.md`. Write only `CHANGELOG.md`.\n"
            "2. Read the commits since then with `git log --oneline`.\n",
        )

    def test_lanes_json_that_cannot_be_read_stops_the_print(self):
        # Given: hooks/lanes.json of no JSON
        self.write(os.path.join(self.plugin, "hooks", "lanes.json"), "{")
        # When: the proposal is printed
        with self.assertRaises(proposal.Stop) as stop:
            layer.printed(helpers.PROPOSED)
        # Then: it stops, naming the file and what is wrong
        self.assertEqual(
            str(stop.exception),
            "lay.py: changelog/hooks/lanes.json holds no JSON; fix it and run again.",
        )


class TestWritten(LayerTest):
    def test_the_readmes_proposal_is_written_as_the_readme_shows_it(self):
        # Given: the README's proposal
        # When: it is written
        said = self.wrote()
        # Then: lay.py says what the README shows, writer reads as printed, the hook and the lanes
        # are written, lane's code is put in, and the proposal and its folder are gone
        folder = os.path.join(self.base, ".lane", "20261102-changelog")
        self.assertEqual(said, WROTE.format(proposal=helpers.PROPOSED, folder=folder))
        self.assertEqual(self.read(self.agent_file), helpers.LAID)
        hooks = self.read_json(os.path.join(self.plugin, "hooks", "hooks.json"))
        self.assertEqual(hooks, helpers.HOOKS)
        self.assertEqual(self.lanes_json(), helpers.RULES)
        for script in ("pretooluse.py", "subagentstop.py", "result.py"):
            self.assertTrue(os.path.isfile(os.path.join(self.plugin, "hooks", "lane", script)))
        self.assertFalse(os.path.exists(folder))
        self.assertTrue(os.path.isdir(".lane"))

    def test_one_step_is_said_alone(self):
        # Given: a proposal laying step 3 of writer alone
        self.propose(self.proposal(steps=[helpers.STEPS[1]]))
        # When: it is written
        # Then: lay.py says the step alone
        self.assertTrue(self.wrote().startswith("Wrote step 3 of writer into agents/writer.md.\n"))

    def test_the_proposals_folder_holding_more_is_kept(self):
        # Given: a note of the developer AI's beside the proposal
        self.write(os.path.join(".lane", "20261102-changelog", "note.md"), "")
        # When: the proposal is written
        said = self.wrote()
        # Then: the proposal is gone and its folder kept
        self.assertNotIn("Removed its folder", said)
        self.assertFalse(os.path.exists(helpers.PROPOSED))

    def test_the_lanes_of_another_subagent_laid_before_are_kept_while_its_file_is_there(self):
        for kept in (True, False):
            with self.subTest(kept=kept):
                # Given: reviewer with lanes laid before, its file there or gone
                self.setUp()
                self.write(os.path.join(self.plugin, "agents", "reviewer.md"), REVIEWER)
                laid = {"name": "reviewer", "steps": [helpers.STEPS[0]]}
                self.write_json(
                    os.path.join(self.plugin, "hooks", "lanes.json"), {"subagents": [laid]}
                )
                if not kept:
                    os.remove(os.path.join(self.plugin, "agents", "reviewer.md"))
                # When: the README's proposal is written
                said = self.wrote()
                # Then: reviewer's lanes are kept, and its hook with writer's, where its file is
                names = [a["name"] for a in self.lanes_json()["subagents"]]
                self.assertEqual(names, ["reviewer", "writer"] if kept else ["writer"])
                hooked = "reviewer and writer" if kept else "writer"
                self.assertIn(f"Wrote the hooks of {hooked} into hooks/hooks.json.\n", said)

    def test_claude_codes_check_failing_stops_with_what_it_found(self):
        # Given: Claude Code's check finding the plugin malformed
        # When: the proposal is written
        with self.assertRaises(proposal.Stop) as stop:
            self.wrote(returncode=1)
        # Then: it stops with what the check printed, the proposal kept to run again
        self.assertEqual(
            str(stop.exception),
            "lay.py: claude plugin validate found changelog malformed:\nout\nerr\nfix what it"
            f" names, then run `lay.py write {helpers.PROPOSED}` again.",
        )
        self.assertTrue(os.path.isfile(helpers.PROPOSED))

    def test_claude_not_on_path_stops_saying_so(self):
        # Given: no claude on PATH
        # When: the proposal is written
        with self.assertRaises(proposal.Stop) as stop:
            self.wrote(missing=True)
        # Then: it stops, telling to install Claude Code
        self.assertEqual(
            str(stop.exception), "lay.py: claude is not on PATH; install Claude Code and run again."
        )


class RoutesTest(LayerTest):
    def setUp(self) -> None:
        super().setUp()
        self.write(os.path.join(self.plugin, "agents", "lead.md"), helpers.LEAD)
        self.write(os.path.join(self.plugin, "agents", "reviewer.md"), helpers.REVIEWER)
        self.propose({**helpers.PROPOSAL, "routes": helpers.ROUTES})

    def agent(self, name: str) -> str:
        """The text of the subagent's file."""
        return self.read(os.path.join(self.plugin, "agents", f"{name}.md"))


class TestRoutes(RoutesTest):
    def test_the_routes_are_printed_and_each_routed_steps_sentence(self):
        # Given: the README's proposal with docs/routes.md's routes
        # When: it is printed
        # Then: the routes are shown, then writer's lanes with its result command, then lead's
        # and reviewer's steps as they will read
        self.assertEqual(layer.printed(helpers.PROPOSED), ROUTES_PRINTED)

    def test_the_subagents_fanned_out_and_the_orders_of_results_are_printed(self):
        for precedence, said in (
            (["more", "good"], "  results taken first to last: `more`, `good`\n"),
            (
                {"reviewer": ["more", "good"], "writer": ["written"]},
                (
                    "  results of reviewer taken first to last: `more`, `good`\n"
                    "  results of writer taken first to last: `written`\n"
                ),
            ),
        ):
            with self.subTest(precedence=precedence):
                # Given: docs/routes.md's routes with reviewer fanned out, its results in order
                routed = {**helpers.ROUTES, "fan_out": ["reviewer"], "precedence": precedence}
                # When: they are printed
                found = layer.routes_printed(routed)
                # Then: below the routes, the subagents run at once and each order are printed
                rows = ROUTES_PRINTED.split("\n\n")[0] + "\n"
                self.assertEqual(found, rows + "  runs at once of reviewer\n" + said)

    def test_the_routes_are_written_with_each_routed_steps_sentence(self):
        # Given: the README's proposal with docs/routes.md's routes
        # When: it is written
        said = self.wrote()
        # Then: each subagent reads as printed, the hooks are those of all three, and the
        # routes are in hooks/lanes.json beside the lanes
        self.assertTrue(said.startswith(ROUTES_WROTE), said)
        self.assertEqual(
            [self.agent(n) for n in ("lead", "writer", "reviewer")],
            [helpers.LEAD_LAID, helpers.WRITER_LAID, helpers.REVIEWER_LAID],
        )
        self.assertEqual(self.lanes_json(), {**helpers.RULES, "routes": helpers.ROUTES})
        hooks = self.read_json(os.path.join(self.plugin, "hooks", "hooks.json"))
        self.assertIn("changelog:reviewer", hooks["hooks"]["PreToolUse"][0]["hooks"][0]["command"])

    def test_routes_laid_before_are_kept_where_the_proposal_gives_none(self):
        # Given: the routes laid, then the README's proposal alone
        self.wrote()
        self.propose(helpers.PROPOSAL)
        # When: it is written
        self.wrote()
        # Then: the routes and their sentences are kept
        self.assertEqual(self.lanes_json()["routes"], helpers.ROUTES)
        self.assertEqual(self.agent("reviewer"), helpers.REVIEWER_LAID)

    def test_routes_given_anew_take_the_sentences_of_those_before_out(self):
        # Given: the routes laid, then routes of writer alone, ending once it has written
        self.wrote()
        alone = [{"from": "lead", "to": "writer"}, {"from": "writer", "on": "written"}]
        self.propose({"plugin": "changelog", "routes": {**helpers.ROUTES, "routes": alone}})
        # When: they are printed and written
        printed = layer.printed(helpers.PROPOSED)
        said = self.wrote()
        # Then: reviewer's sentence is shown taken out and is gone, its hooks with it
        self.assertIn(
            "Lanes of reviewer, each hook acting in reviewer alone:\n"
            "  step 2  no lane: the sentences laid before taken out\n",
            printed,
        )
        self.assertEqual(self.agent("reviewer"), helpers.REVIEWER)
        self.assertIn("Wrote the hooks of writer and lead into hooks/hooks.json.\n", said)
        self.assertEqual(self.lanes_json()["routes"]["routes"], alone)
        self.assertEqual(self.agent("writer"), helpers.WRITER_LAID)

    def test_the_orchestrator_given_lanes_is_laid_the_routes_and_no_other_is(self):
        # Given: routes from lead to editor, a name before lead's, lead given a lane of its own
        self.write(os.path.join(self.plugin, "agents", "editor.md"), EDITOR)
        given = {
            **helpers.ROUTES,
            "routes": [{"from": "lead", "to": "editor"}, {"from": "editor", "on": "edited"}],
        }
        lead = {"name": "lead", "steps": [{"step": 2, "lanes": helpers.STEPS[0]["lanes"]}]}
        self.propose({"plugin": "changelog", "subagents": [lead], "routes": given})
        # When: it is printed
        printed = layer.printed(helpers.PROPOSED)
        # Then: lead follows the routes beside its lane, and editor gives its result alone
        self.assertIn(f"  step 1  follow: {helpers.FOLLOW}", printed)
        self.assertNotIn("follow:", printed.split("Lanes of editor")[1])

    def test_each_subagent_of_the_routes_before_whose_file_is_there_is_written(self):
        # Given: the routes laid, writer's file then removed, and routes of lead and editor
        self.wrote()
        os.remove(os.path.join(self.plugin, "agents", "writer.md"))
        self.write(os.path.join(self.plugin, "agents", "editor.md"), EDITOR)
        given = [{"from": "lead", "to": "editor"}, {"from": "editor", "on": "edited"}]
        self.propose({"plugin": "changelog", "routes": {**helpers.ROUTES, "routes": given}})
        # When: they are written
        said = self.wrote()
        # Then: reviewer, routed before after writer, has its sentence taken out
        self.assertIn("Wrote step 2 of reviewer into agents/reviewer.md.\n", said)
        self.assertEqual(self.agent("reviewer"), helpers.REVIEWER)

    def test_a_subagent_of_the_routes_before_whose_file_is_gone_is_left_out(self):
        # Given: the routes laid, reviewer's file then removed, and routes of writer alone
        self.wrote()
        os.remove(os.path.join(self.plugin, "agents", "reviewer.md"))
        alone = [{"from": "lead", "to": "writer"}, {"from": "writer", "on": "written"}]
        self.propose({"plugin": "changelog", "routes": {**helpers.ROUTES, "routes": alone}})
        # When: they are written
        said = self.wrote()
        # Then: reviewer is neither written nor hooked
        self.assertNotIn("reviewer", said)


class TestBroughtUp(LayerTest):
    def setUp(self) -> None:
        super().setUp()
        self.wrote()

    def test_an_older_copy_is_brought_up_and_the_lanes_laid_said(self):
        # Given: the README's lanes laid, with a copy of lane's code of version 0.0.1
        self.write(os.path.join(self.plugin, "hooks", "lane", "VERSION"), "0.0.1\n")
        # When: the plugin is brought up
        said = layer.brought_up(self.plugin)
        # Then: the copy is lane's version, and each lane laid is said
        version = self.read(os.path.join(self.plugin, "hooks", "lane", "VERSION")).strip()
        self.assertEqual(
            said,
            f"Brought lane's code in hooks/lane/ up from 0.0.1 to {version}.\n"
            f"Laid before on step 2 of writer: {json.dumps(helpers.STEPS[0]['lanes'][0])}\n"
            f"Laid before on step 3 of writer: {json.dumps(helpers.STEPS[1]['lanes'][0])}\n",
        )

    def test_hooks_of_another_form_are_written_in_this_one(self):
        # Given: the hooks in the old shape, and step 2 no longer saying its sentence
        old = {
            "matcher": "Bash",
            "hooks": [{"type": "command", "command": "/hooks/lane/pretooluse.py changelog:writer"}],
        }
        entries_file = os.path.join(self.plugin, "hooks", "hooks.json")
        self.write_json(entries_file, {"hooks": {"PreToolUse": [old]}})
        self.write(self.agent_file, helpers.LAID.replace(f" {helpers.RUN}", ""))
        # When: the plugin is brought up
        said = layer.brought_up(self.plugin)
        # Then: the hook is written anew, and the lane whose step changed is said so
        self.assertEqual(self.read_json(entries_file), helpers.HOOKS)
        self.assertIn("Wrote the hooks of writer into hooks/hooks.json.\n", said)
        self.assertIn(
            f'Laid before on step 2 of writer, whose step no longer says "{helpers.RUN}": ', said
        )

    def test_a_plugin_up_to_date_is_said_so(self):
        # Given: the README's lanes laid just now
        # When: the plugin is brought up
        # Then: nothing is done, and the lanes laid are said
        self.assertTrue(
            layer.brought_up(self.plugin).startswith(
                "hooks/lane/ holds no older copy of lane's code.\n"
            )
        )

    def test_a_folder_of_no_plugin_is_refused(self):
        # Given: a folder with no plugin's manifest
        # When: it is brought up
        with self.assertRaises(proposal.Stop) as stop:
            layer.brought_up(self.base)
        # Then: it is refused, naming it
        self.assertIn(
            f"lay.py: {self.base} holds no .claude-plugin/plugin.json", str(stop.exception)
        )


# The README's proposal with an end lane on writer's step 3, every_item read by an adapter, and a
# values adapter for writer.
ITEMS = "hooks/adapters/items-f.py"
VALUES = "hooks/adapters/values-w.py"
EVERY = {"lane": "every_item", "takes": ["review.md"], "adapter": ITEMS}
DONE = f"End by running `{helpers.GIVE} writer done`."


class AdaptedTest(LayerTest):
    def setUp(self) -> None:
        super().setUp()
        self.adapter("items-f", helpers.ITEMS_ADAPTER, helpers.ITEMS_CASES)
        self.adapter("values-w", helpers.VALUES_ADAPTER, helpers.VALUES_CASES)
        steps = [helpers.STEPS[0], {"step": 3, "lanes": [helpers.STEPS[1]["lanes"][0], EVERY]}]
        self.propose(self.proposal(adapter=VALUES, steps=steps))


class TestAdapted(AdaptedTest):
    def test_the_adapters_are_shown_and_the_result_command_done_laid_on_the_last_step(self):
        # Given: the proposal with an end lane and two adapters
        # When: it is printed
        said = layer.printed(helpers.PROPOSED)
        # Then: each adapter is shown with its cases, and the last step ends by `done`
        self.assertIn(f"  adapter {VALUES}: its 2 cases given as they say\n", said)
        self.assertIn(f"  adapter {ITEMS}: its 2 cases given as they say\n", said)
        self.assertIn(f"4. Reply with the entries you wrote. {DONE}\n", said)
        self.assertIn(f"  step 4  end:   {DONE}  hook follow_routes\n", said)

    def test_the_adapters_are_written_into_the_plugin_and_removed_from_beside_the_proposal(self):
        # Given: the proposal with two adapters, kept beside it
        # When: it is written
        said = self.wrote()
        # Then: each adapter is in the plugin's hooks/adapters/ with its cases, and in its lanes
        adapters = os.path.join(self.plugin, "hooks", "adapters")
        self.assertEqual(self.read(os.path.join(adapters, "items-f.py")), helpers.ITEMS_ADAPTER)
        self.assertEqual(
            self.read_json(os.path.join(adapters, "values-w.json")), helpers.VALUES_CASES
        )
        (writer,) = self.lanes_json()["subagents"]
        self.assertEqual(writer["adapter"], VALUES)
        self.assertEqual(writer["steps"][1]["lanes"][1], EVERY)
        self.assertIn(f"Wrote the adapter {ITEMS} with its cases.\n", said)
        # And: the proposal's folder is gone, the adapters' with it
        self.assertFalse(os.path.exists(os.path.dirname(helpers.PROPOSED)))
        self.assertTrue(
            said.endswith(
                f"Removed its folder {os.path.abspath(os.path.dirname(helpers.PROPOSED))}.\n"
            )
        )
        self.assertEqual(said.count("Removed its folder"), 1)
        # And: writer's last step ends by its result command
        self.assertIn(f"you wrote. {DONE}\n", self.read(self.agent_file))

    def test_the_folder_beside_kept_where_it_holds_more(self):
        # Given: another file beside the adapters
        beside = os.path.join(os.path.dirname(helpers.PROPOSED), "changelog", "adapters")
        self.write(os.path.join(beside, "notes.md"), "x")
        # When: the proposal is written
        said = self.wrote()
        # Then: the file and its folders are kept
        self.assertTrue(os.path.exists(os.path.join(beside, "notes.md")))
        self.assertNotIn("Removed its folder", said)

    def test_an_adapter_laid_before_is_said_by_up(self):
        # Given: the proposal written
        self.wrote()
        # When: the plugin is brought up
        said = layer.brought_up(self.plugin)
        # Then: writer's values adapter is said beside its lanes
        self.assertIn(f'Laid before on writer: {{"adapter": "{VALUES}"}}\n', said)
        self.assertIn(f"Laid before on step 3 of writer: {json.dumps(EVERY)}\n", said)


class TestPart(LayerTest):
    def setUp(self) -> None:
        super().setUp()
        self.part = os.path.join(self.plugin, "prompts", "writer.md")
        self.write(self.part, helpers.WRITER.split("---\n\n", 1)[1])
        self.entry = helpers.PART_ENTRY
        self.write(self.agent_file, self.entry.format(name="writer"))

    def test_the_lanes_are_written_into_the_part(self):
        # Given: writer's steps in its part
        # When: the README's proposal is written
        said = self.wrote()
        # Then: the part's steps say the sentences, and its entry is as it was
        self.assertIn(f"`git log --oneline`. {helpers.RUN}\n", self.read(self.part))
        self.assertEqual(self.read(self.agent_file), self.entry.format(name="writer"))
        self.assertTrue(said.startswith("Wrote steps 2 and 3 of writer into prompts/writer.md.\n"))

    def test_subagents_sharing_a_part_laying_one_set_of_lanes_are_written(self):
        # Given: drafter, whose entry names writer's part, given the same lanes
        self.write(
            os.path.join(self.plugin, "agents", "drafter.md"), self.entry.format(name="drafter")
        )
        given = {
            "plugin": "changelog",
            "subagents": [
                {"name": "writer", "steps": helpers.STEPS},
                {"name": "drafter", "steps": helpers.STEPS},
            ],
        }
        self.propose(given)
        # When: the proposal is written
        self.wrote()
        # Then: the part says each sentence once
        self.assertEqual(self.read(self.part).count(helpers.RUN), 1)

    def test_subagents_sharing_a_part_laying_different_lanes_are_refused(self):
        for before in (False, True):
            with self.subTest(before=before):
                # Given: drafter, whose entry names writer's part, laying another lane on its
                # step 2, by the proposal or as laid before
                self.write(
                    os.path.join(self.plugin, "agents", "drafter.md"),
                    self.entry.format(name="drafter"),
                )
                other = [{"step": 2, "lanes": [{"lane": "run_only", "takes": ["git diff"]}]}]
                agents = [{"name": "writer", "steps": helpers.STEPS}]
                if before:
                    self.write_json(
                        os.path.join(self.plugin, "hooks", "lanes.json"),
                        {"subagents": [{"name": "drafter", "steps": other}]},
                    )
                else:
                    agents.append({"name": "drafter", "steps": other})
                self.propose({"plugin": "changelog", "subagents": agents})
                # When: the proposal is printed
                with self.assertRaises(proposal.Stop) as stop:
                    layer.printed(helpers.PROPOSED)
                # Then: it is refused, naming both and the step
                self.assertIn(
                    "share their part prompts/writer.md, and would lay different lanes on its"
                    " step 2",
                    str(stop.exception),
                )
                self.assertIn("writer and drafter", str(stop.exception))

    def drafter(self) -> None:
        """drafter, whose entry names writer's part."""
        self.write(
            os.path.join(self.plugin, "agents", "drafter.md"), self.entry.format(name="drafter")
        )

    def refused(self, agents: list) -> str:
        """What stops the print of a proposal of the subagents."""
        self.propose({"plugin": "changelog", "subagents": agents})
        with self.assertRaises(proposal.Stop) as stop:
            layer.printed(helpers.PROPOSED)
        return str(stop.exception)

    def test_a_step_one_sharer_lays_lanes_on_and_the_other_none_is_refused(self):
        # Given: drafter, sharing writer's part, laying writer's step 3 alone, given first
        self.drafter()
        agents = [
            {"name": "drafter", "steps": helpers.STEPS[1:]},
            {"name": "writer", "steps": helpers.STEPS},
        ]
        # When: the proposal is printed
        # Then: it is refused, naming both and step 2
        self.assertIn(
            "drafter and writer share their part prompts/writer.md, and would lay different lanes"
            " on its step 2",
            self.refused(agents),
        )

    def test_sharers_are_held_after_a_subagent_with_no_part(self):
        # Given: reviewer, whose steps are in its entry, then writer and drafter sharing writer's
        # part, laying different lanes on step 2
        self.drafter()
        self.write(os.path.join(self.plugin, "agents", "reviewer.md"), REVIEWER)
        other = [{"step": 2, "lanes": [{"lane": "run_only", "takes": ["git diff"]}]}]
        agents = [
            {"name": "reviewer", "steps": [{"step": 1, "lanes": helpers.STEPS[0]["lanes"]}]},
            {"name": "writer", "steps": helpers.STEPS},
            {"name": "drafter", "steps": other},
        ]
        # When: the proposal is printed
        # Then: it is refused
        self.assertIn("writer and drafter share their part", self.refused(agents))

    def test_a_sharer_the_proposal_gives_is_held_by_its_lanes_not_those_before(self):
        # Given: writer and drafter laid before with different lanes on step 2, then the
        # proposal giving writer drafter's
        self.drafter()
        other = [{"step": 2, "lanes": [{"lane": "run_only", "takes": ["git diff"]}]}]
        laid = {
            "subagents": [
                {"name": "writer", "steps": other},
                {"name": "drafter", "steps": helpers.STEPS},
            ]
        }
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)
        self.propose(
            {"plugin": "changelog", "subagents": [{"name": "writer", "steps": helpers.STEPS}]}
        )
        # When: the proposal is printed
        # Then: it is printed, writer laying what drafter lays
        self.assertIn("Lanes of writer", layer.printed(helpers.PROPOSED))


class TestValidated(LayerTest):
    def test_claude_codes_check_failing_is_told_as_it_printed(self):
        # Given: a claude on PATH whose check fails, printing what it found
        folder = os.path.join(self.base, "bin")
        self.write(os.path.join(folder, "claude"), "#!/bin/sh\necho found x\nexit 1\n")
        os.chmod(os.path.join(folder, "claude"), 0o755)
        path = mock.patch.dict(os.environ, {"PATH": folder + os.pathsep + os.environ["PATH"]})
        # When: the plugin is checked
        with path, self.assertRaises(proposal.Stop) as stop:
            layer.validated(self.plugin, helpers.PROPOSED)
        # Then: it stops with what the check printed, as text
        self.assertIn("malformed:\nfound x\nfix what it names", str(stop.exception))


if __name__ == "__main__":
    unittest.main()
