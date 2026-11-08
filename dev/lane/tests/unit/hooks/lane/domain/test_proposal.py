"""The cases of proposal.py's contract: whether `lay.py` can lay a proposal, held to its form and
checked against the plugin's files, as the architecture's sequence "S1: lay.py print" draws it."""

import json
import os

import helpers
from helpers import proposal, testing


class ProposalTest(testing.FolderTest):
    def setUp(self):
        super().setUp()
        self.root = os.path.join(self.base, "changelog")
        helpers.changelog(self.root, with_lanes=False)
        self.path = os.path.join(self.base, ".lane", "20261108-changelog", "changelog.json")

    def propose(self, data=None, **more):
        given = {"plugin": "changelog", "subagents": [helpers.WRITER_LANES], **more}
        helpers.write(self.path, json.dumps(given if data is None else data))

    def refused(self):
        with self.assertRaises(proposal.Refused) as caught:
            proposal.checked(self.path)
        return caught.exception.faults


class TestChecked(ProposalTest):
    def test_a_proposal_that_can_stand_gives_its_plugin_and_lanes(self):
        self.propose()
        found = proposal.checked(self.path)
        self.assertEqual(
            (found.root, found.manifest.name, found.laid.roles[0].name),
            (self.root, "changelog", "writer"),
        )

    def test_a_proposal_gives_the_part_of_each_role(self):
        self.propose()
        found = proposal.checked(self.path)
        self.assertEqual(found.parts["writer"].path, os.path.join(self.root, "agents", "writer.md"))

    def test_a_plugin_folder_from_the_root_is_read_as_it_is(self):
        self.propose(plugin=self.root)
        self.assertEqual(proposal.checked(self.path).root, self.root)

    def test_a_proposal_kept_outside_a_lane_folder_is_refused(self):
        self.path = os.path.join(self.base, "changelog.json")
        self.propose()
        self.assertEqual(
            self.refused(),
            [
                (
                    f"{self.path} lies outside .lane/<yyyymmdd>-<plugin>/, where lay.py keeps a"
                    " proposal at the root of the repository the plugin is in"
                )
            ],
        )

    def test_a_proposal_that_is_no_json_is_refused(self):
        helpers.write(self.path, "{")
        self.assertEqual(
            self.refused(),
            [
                (
                    f"{self.path} is no JSON: Expecting property name enclosed in double quotes:"
                    " line 1 column 2 (char 1)"
                )
            ],
        )

    def test_a_proposal_that_is_not_there_is_refused(self):
        self.assertEqual(self.refused(), [f"{self.path} isn't there"])

    def test_a_proposal_out_of_its_form_is_refused(self):
        self.propose({"subagents": [helpers.WRITER_LANES]})
        self.assertEqual(
            self.refused(),
            [
                (
                    f'{self.path} is out of its form: $: expected the key "plugin", found an object'
                    " without it"
                )
            ],
        )

    def test_a_lane_that_cannot_stand_is_refused(self):
        lane = {"lane": "in_form", "takes": ["a"]}
        self.propose(subagents=[{"name": "writer", "steps": [{"step": 1, "lanes": [lane]}]}])
        self.assertEqual(
            self.refused(),
            [
                (
                    "step 1 of writer: in_form takes a thing for each of its places, output and"
                    " form, and is given 1"
                )
            ],
        )

    def test_a_plugin_folder_holding_no_manifest_is_refused(self):
        self.propose(plugin="nowhere")
        self.assertEqual(
            self.refused(),
            [f"{os.path.join(self.base, 'nowhere')} holds no .claude-plugin/plugin.json"],
        )

    def test_a_role_with_no_entry_is_refused(self):
        self.propose(subagents=[{**helpers.WRITER_LANES, "name": "noter"}])
        self.assertEqual(self.refused(), [f"no agents/*.md names `noter` in {self.root}"])

    def test_a_role_not_set_to_run_in_the_background_is_refused(self):
        path = os.path.join(self.root, "agents", "writer.md")
        helpers.write(path, helpers.WRITER.replace("background: true\n", ""))
        self.propose()
        self.assertEqual(
            self.refused(),
            [
                (
                    f"{path} doesn't set `background: true`, which a role with lanes or named by"
                    " the routes sets"
                )
            ],
        )

    def test_a_lane_on_a_step_the_steps_dont_hold_is_refused(self):
        lanes = [{"lane": "write_only", "takes": ["a"]}]
        self.propose(subagents=[{"name": "writer", "steps": [{"step": 9, "lanes": lanes}]}])
        self.assertEqual(
            self.refused(),
            [f"step 9 of writer: {os.path.join(self.root, 'agents', 'writer.md')} holds no step 9"],
        )

    def test_a_lane_on_any_step_stands_where_the_part_holds_no_numbered_list(self):
        path = os.path.join(self.root, "agents", "writer.md")
        helpers.write(path, "---\nname: writer\nbackground: true\n---\nWrite the entries.\n")
        self.propose()
        self.assertEqual(proposal.checked(self.path).parts["writer"].steps, [])

    def test_a_dependency_the_manifest_does_not_declare_is_refused(self):
        lanes = [{"lane": "run_only", "takes": ["python3 ${dependency:checker}/c.py"]}]
        self.propose(subagents=[{"name": "writer", "steps": [{"step": 2, "lanes": lanes}]}])
        self.assertEqual(
            self.refused(),
            [
                (
                    "step 2 of writer: run_only names the dependency checker, which the manifest"
                    " of changelog doesn't declare"
                )
            ],
        )

    def test_a_dependency_the_manifest_declares_stands(self):
        helpers.write(
            os.path.join(self.root, ".claude-plugin", "plugin.json"),
            json.dumps({"name": "changelog", "dependencies": ["checker"]}),
        )
        lanes = [{"lane": "run_only", "takes": ["python3 ${dependency:checker}/c.py"]}]
        self.propose(subagents=[{"name": "writer", "steps": [{"step": 2, "lanes": lanes}]}])
        self.assertEqual(proposal.checked(self.path).manifest.dependencies, ("checker",))


class TestSharedPart(ProposalTest):
    def share(self):
        helpers.share_part(self.root)

    def roles(self, writer_takes, drafter_takes):
        return [
            {"name": n, "steps": [{"step": 2, "lanes": [{"lane": "write_only", "takes": t}]}]}
            for n, t in (("writer", writer_takes), ("drafter", drafter_takes))
        ]

    def test_roles_sharing_a_part_with_the_same_lanes_stand(self):
        self.share()
        self.propose(subagents=self.roles(["a"], ["a"]))
        self.assertEqual(len(proposal.checked(self.path).laid.roles), 2)

    def test_roles_sharing_a_part_with_different_lanes_are_refused(self):
        self.share()
        self.propose(subagents=self.roles(["a"], ["b"]))
        self.assertEqual(
            self.refused(),
            [
                (
                    "writer and drafter share the part"
                    f" {os.path.join(self.root, 'domain', 'writer.md')} and lay different lanes on"
                    " step 2 of it"
                )
            ],
        )

    def test_a_role_laid_before_whose_entry_is_gone_shares_no_part(self):
        laid = {"subagents": [{**helpers.WRITER_LANES, "name": "gone"}]}
        helpers.write(os.path.join(self.root, "hooks", "lanes.json"), json.dumps(laid))
        self.propose()
        self.assertEqual(proposal.checked(self.path).laid.roles[0].name, "writer")

    def test_a_role_sharing_a_part_with_one_laid_before_is_held_to_its_lanes(self):
        self.share()
        laid = {"subagents": self.roles(["a"], ["b"])[1:]}
        helpers.write(os.path.join(self.root, "hooks", "lanes.json"), json.dumps(laid))
        self.propose(subagents=self.roles(["a"], [])[:1])
        self.assertEqual(
            self.refused(),
            [
                (
                    "writer and drafter share the part"
                    f" {os.path.join(self.root, 'domain', 'writer.md')} and lay different lanes on"
                    " step 2 of it"
                )
            ],
        )


class TestRoutes(ProposalTest):
    def route(self, **more):
        self.propose(routes={**helpers.ROUTES, **more})

    def skill_path(self):
        return os.path.join(self.root, "skills", "write", "SKILL.md")

    def test_routes_that_can_be_followed_give_the_skills_part(self):
        self.route()
        skill = proposal.checked(self.path).skill
        self.assertEqual(skill.path if skill else None, self.skill_path())

    def test_each_role_the_routes_name_has_its_part(self):
        self.route()
        self.assertEqual(sorted(proposal.checked(self.path).parts), ["reviewer", "writer"])

    def test_a_proposal_of_routes_alone_stands(self):
        self.propose({"plugin": "changelog", "routes": helpers.ROUTES})
        self.assertIsNone(proposal.checked(self.path).laid.role("writer"))

    def test_routes_whose_skill_is_not_there_are_refused(self):
        lead = [{"from": "draft", "to": "writer"}, {"from": "writer", "on": "done"}]
        self.route(orchestrator="draft", routes=lead)
        self.assertEqual(self.refused(), [f"{self.root} holds no skills/draft/SKILL.md"])

    def test_routes_on_a_step_the_skill_does_not_hold_are_refused(self):
        self.route(step=7)
        self.assertEqual(
            self.refused(),
            [f"the routes lie on step 7 of write, and {self.skill_path()} holds no step 7"],
        )

    def test_routes_on_a_step_of_a_skill_with_no_numbered_list_are_refused(self):
        helpers.write(self.skill_path(), "---\nname: write\n---\nStart writer.\n")
        self.route()
        self.assertEqual(
            self.refused(),
            [
                (
                    f"the routes lie on step 1 of write, and {self.skill_path()} holds no numbered"
                    " list, so they give no step"
                )
            ],
        )

    def test_routes_with_no_step_stand_beside_a_skill_with_no_numbered_list(self):
        helpers.write(self.skill_path(), "Start writer.\n")
        self.propose(routes={k: v for k, v in helpers.ROUTES.items() if k != "step"})
        skill = proposal.checked(self.path).skill
        self.assertEqual(skill.steps if skill else None, [])

    def test_a_role_the_routes_name_not_set_to_run_in_the_background_is_refused(self):
        path = os.path.join(self.root, "agents", "reviewer.md")
        helpers.write(path, helpers.REVIEWER.replace("background: true\n", ""))
        self.route()
        self.assertEqual(
            self.refused(),
            [
                (
                    f"{path} doesn't set `background: true`, which a role with lanes or named by"
                    " the routes sets"
                )
            ],
        )

    def test_a_dependency_the_routes_name_and_the_manifest_does_not_declare_is_refused(self):
        lead = [
            helpers.ROUTES["routes"][0],
            {"from": "writer", "on": "written", "to": "checker:examiner"},
            {"from": "checker:examiner", "on": "done"},
        ]
        self.route(routes=lead)
        self.assertEqual(
            self.refused(),
            [
                (
                    "the routes name checker:examiner, and the manifest of changelog doesn't"
                    " declare"
                    " checker"
                )
            ],
        )

    def test_routes_that_cannot_be_followed_are_refused(self):
        self.route(fan_out=["noter"])
        self.assertEqual(self.refused(), ["fan_out names noter, which no route starts"])
