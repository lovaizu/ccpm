"""lay.py's course: the proposal printed as each step will read, for the developer AI's approval;
once approved, written word for word into its plugin from the same file, Claude Code's check run on
it, and the proposal removed; and a plugin laid before brought up to lane's code."""

import json
import os
import subprocess
import unittest
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
REVIEWER = "---\nname: reviewer\n---\n\n## Steps\n\n1. Compare the entries.\n"
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
        effect = FileNotFoundError() if missing else None
        with mock.patch.object(
            layer.subprocess, "run", return_value=done, side_effect=effect
        ) as run:
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


if __name__ == "__main__":
    unittest.main()
