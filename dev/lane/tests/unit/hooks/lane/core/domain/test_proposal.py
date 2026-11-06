"""The proposal the user writes for lay.py: read and held to the JSON Schema docs/lanes.md
gives, then checked against the plugin's files; what this version does not lay yet, and anything
that cannot be laid, refused with what is wrong and what to do."""

import json
import os
import unittest

import helpers
from helpers import proposal


class ProposalTest(helpers.LayTest):
    def refused(self, given: object) -> str:
        """What lay.py says of the proposal given, refusing it."""
        path = self.propose(given)
        with self.assertRaises(proposal.Stop) as stop:
            proposal.proposal(path)
        return str(stop.exception)


class TestRead(ProposalTest):
    def test_the_readmes_proposal_is_read_with_each_step_found_in_its_file(self):
        # Given: the README's proposal
        # When: it is read
        found = proposal.proposal(helpers.PROPOSED)
        # Then: it gives the plugin, its name, and writer with its file, its lines and each step
        # with where it is among them
        self.assertEqual((found["plugin"], found["name"]), ("changelog", "changelog"))
        (writer,) = found["subagents"]
        file = os.path.join("changelog", "agents", "writer.md")
        self.assertEqual((writer["name"], writer["file"]), ("writer", file))
        self.assertEqual(writer["lines"], helpers.WRITER.splitlines(keepends=True))
        self.assertEqual(
            [(s["step"], s["span"]) for s in writer["steps"]], [(2, (9, 10)), (3, (10, 11))]
        )

    def test_the_proposals_schema_is_the_one_docs_lanes_md_gives(self):
        # Given: the proposal's JSON Schema docs/lanes.md gives under The proposal
        with open(os.path.join(helpers.LANE, "docs", "lanes.md"), encoding="utf-8") as f:
            text = f.read().split("## The proposal")[1].split("\n## ")[0]
        shown = json.loads(text.split("```json\n")[1].split("```")[0])
        # When: lay.py's is read
        # Then: they are the same
        self.assertEqual(proposal.PROPOSAL, shown)


class TestResults(ProposalTest):
    def test_results_and_routes_from_one_subagent_are_refused(self):
        # Given: routes from writer, and writer giving results of its own too
        self.write(self.skill_file, helpers.SKILL)
        self.write(os.path.join(self.plugin, "agents", "reviewer.md"), helpers.REVIEWER)
        given = {**self.proposal(results=["asks"]), "routes": helpers.ROUTES}
        # When: it is read
        # Then: it is refused, as the routes give writer's results
        self.assertIn(
            "gives writer its own results, though routes are from it; give its results in the"
            " routes alone",
            self.refused(given),
        )

    def test_a_result_not_a_word_is_refused_by_its_shape(self):
        # Given: writer giving a result of capitals
        # When: it is read
        # Then: it is refused by its shape
        self.assertIn(
            "out of its shape at $.subagents[0].results[0]",
            self.refused(self.proposal(results=["Asks"])),
        )


class TestDependency(ProposalTest):
    """Routes naming a subagent of a dependency, as docs/routes.md's A subagent of a dependency
    gives them."""

    def setUp(self) -> None:
        super().setUp()
        self.write(self.skill_file, helpers.SKILL)

    def declare(self, *names: str) -> None:
        """changelog's manifest declaring the dependencies of the names."""
        manifest = {"name": "changelog", "version": "0.1.0", "dependencies": list(names)}
        self.write_json(self.manifest(), manifest)

    def test_routes_to_a_declared_dependencys_subagent_are_read_with_no_file_of_it(self):
        # Given: changelog declaring checker, whose examiner the routes name
        self.declare("checker")
        given = {**self.proposal(), "routes": helpers.DEPENDENCY_ROUTES}
        # When: it is read
        found = proposal.proposal(self.propose(given))
        # Then: the routes are read as given, though no file of changelog's gives examiner
        self.assertEqual(found["routes"], helpers.DEPENDENCY_ROUTES)

    def test_a_dependency_the_manifest_does_not_declare_is_refused(self):
        # Given: changelog declaring no dependency
        given = {**self.proposal(), "routes": helpers.DEPENDENCY_ROUTES}
        # When: it is read
        said = self.refused(given)
        # Then: it is refused, telling to declare checker
        self.assertIn(
            "gives checker:examiner, a subagent of checker, which .claude-plugin/plugin.json does"
            " not declare among its dependencies; declare it there",
            said,
        )

    def test_a_dependencys_subagent_named_otherwise_is_refused(self):
        # Given: a route to a subagent named with two colons
        self.declare("checker")
        each = [dict(r) for r in helpers.DEPENDENCY_ROUTES["routes"]]
        for r in each:
            for k in ("from", "to"):
                if r.get(k) == "checker:examiner":
                    r[k] = "checker:a:b"
        given = {**self.proposal(), "routes": {**helpers.DEPENDENCY_ROUTES, "routes": each}}
        # When: it is read
        # Then: it is refused, as the name is no subagent's
        self.assertIn("gives checker:a:b, which names no subagent", self.refused(given))


class TestLanes(ProposalTest):
    def test_every_lane_docs_lanes_md_names_is_read_with_things_given_for_each_run(self):
        self.write_json(os.path.join(self.plugin, "forms", "e.json"), {"type": "object"})
        steps = [
            {
                "step": 1,
                "lanes": [
                    {"lane": "read_only", "takes": ["CHANGELOG.md"]},
                    {"lane": "read_whole", "takes": ["CHANGELOG.md"]},
                ],
            },
            {
                "step": 2,
                "lanes": [
                    {"lane": "run_only", "takes": ["git log --oneline"]},
                    {"lane": "hold", "takes": ["git push"]},
                    {"lane": "test_after", "takes": ["src/", "{test}"]},
                ],
            },
            {
                "step": 3,
                "lanes": [
                    {"lane": "write_only", "takes": ["{work}"]},
                    {"lane": "in_form", "takes": ["e.json", "${CLAUDE_PLUGIN_ROOT}/forms/e.json"]},
                    {"lane": "in_form", "takes": ["f.json", "{form}"]},
                ],
            },
            {
                "step": 4,
                "lanes": [
                    {"lane": "end_when", "takes": ["CHANGELOG.md"]},
                    {"lane": "every_item", "takes": ["r.md"]},
                ],
            },
        ]
        # Given: a lane of each type, some taking a thing given for each run
        self.propose(self.proposal(steps=steps))
        # When: the proposal is read
        (writer,) = proposal.proposal(helpers.PROPOSED)["subagents"]
        # Then: each is read as given, with no adapter
        self.assertEqual([s["lanes"] for s in writer["steps"]], [s["lanes"] for s in steps])
        self.assertEqual(writer["adapters"], [])

    def test_adapters_beside_the_proposal_are_run_on_their_cases_and_read(self):
        # Given: a values adapter for writer and an items adapter on its every_item, each kept
        # beside the proposal with its cases
        values = self.adapter("values-w", helpers.VALUES_ADAPTER, helpers.VALUES_CASES)
        items = self.adapter("items-f", helpers.ITEMS_ADAPTER, helpers.ITEMS_CASES)
        lane = {"lane": "every_item", "takes": ["r.md"], "adapter": items}
        self.propose(self.proposal(adapter=values, steps=[{"step": 4, "lanes": [lane]}]))
        # When: the proposal is read
        (writer,) = proposal.proposal(helpers.PROPOSED)["subagents"]
        # Then: each adapter is given with its source, its cases and how many it gave
        beside = os.path.join(os.path.dirname(helpers.PROPOSED), "changelog", "adapters")
        self.assertEqual(writer["adapter"], values)
        self.assertEqual(
            writer["adapters"],
            [
                {
                    "path": values,
                    "source": os.path.join(beside, "values-w.py"),
                    "cases": os.path.join(beside, "values-w.json"),
                    "count": 2,
                },
                {
                    "path": items,
                    "source": os.path.join(beside, "items-f.py"),
                    "cases": os.path.join(beside, "items-f.json"),
                    "count": 2,
                },
            ],
        )

    def test_a_subagents_steps_are_read_from_its_part(self):
        # Given: writer's entry naming its part, which holds its steps
        self.write(self.agent_file, helpers.PART_ENTRY.format(name="writer"))
        part = os.path.join(self.plugin, "prompts", "writer.md")
        self.write(part, helpers.WRITER.split("---\n\n", 1)[1])
        # When: the proposal is read
        (writer,) = proposal.proposal(helpers.PROPOSED)["subagents"]
        # Then: its file is the part, with each step found there
        self.assertEqual(writer["file"], os.path.join("changelog", "prompts", "writer.md"))
        self.assertEqual([s["span"] for s in writer["steps"]], [(3, 4), (4, 5)])
        # And: a part not there is refused
        os.remove(part)
        with self.assertRaises(proposal.Stop) as stop:
            proposal.proposal(helpers.PROPOSED)
        self.assertIn(
            "whose entry names its part prompts/writer.md, which is not there", str(stop.exception)
        )


class RoutesTest(ProposalTest):
    def setUp(self) -> None:
        super().setUp()
        self.write(self.skill_file, helpers.SKILL)
        self.write(os.path.join(self.plugin, "agents", "reviewer.md"), helpers.REVIEWER)

    def routed(self, routes: list) -> dict:
        """The proposal of docs/routes.md's routes changed to those given, with no subagents."""
        return {"plugin": "changelog", "routes": {**helpers.ROUTES, "routes": routes}}


class TestRoutes(RoutesTest):
    def test_routes_alone_are_read_as_given(self):
        # Given: a proposal of docs/routes.md's routes alone
        self.propose({"plugin": "changelog", "routes": helpers.ROUTES})
        # When: it is read
        found = proposal.proposal(helpers.PROPOSED)
        # Then: it gives the routes, and no subagents
        self.assertEqual((found["routes"], found["subagents"]), (helpers.ROUTES, []))

    def test_a_proposal_of_lanes_alone_has_no_routes(self):
        # Given: the README's proposal
        # When: it is read
        # Then: it gives no routes
        self.assertIsNone(proposal.proposal(helpers.PROPOSED)["routes"])

    def test_routes_that_cannot_be_laid_are_refused(self):
        routes = helpers.ROUTES["routes"]
        first, written, more, good = routes
        for given, said in (
            (
                self.routed(routes[:1]),
                "is out of its shape at $.routes.routes: expected at least 2",
            ),
            (
                self.routed([{**first, "on": "go"}, *routes[1:]]),
                "no one route from write with a `to`",
            ),
            (self.routed(routes[1:]), "no one route from write with a `to`"),
            (self.routed([first, *routes]), "no one route from write with a `to`"),
            (
                self.routed([first, {"from": "write", "on": "x"}, *routes[1:]]),
                "no one route from write",
            ),
            (
                self.routed([first, {"from": "writer", "to": "reviewer"}, more, good]),
                "a route from writer with no `on`",
            ),
            (
                self.routed([first, written, {"from": "editor", "to": "writer"}, more, good]),
                "a route from editor with no `on`",
            ),
            (self.routed([*routes, {**more, "to": "write"}]), "two routes from reviewer on `more`"),
            (
                self.routed([first, {**written, "to": "write"}, more, good]),
                "a route to write, the skill the routes start from",
            ),
            (
                self.routed([first, written, {**more, "to": "planner"}, good]),
                "a route to planner, which no route is from",
            ),
            (
                self.routed([first, written, more, {**good, "to": "writer"}]),
                "no route with neither a `to` nor `waits`",
            ),
            (
                self.routed([*routes, {"from": "reviewer", "on": "asks", "waits": False}]),
                "is out of its shape at $.routes.routes[4].waits",
            ),
            (
                self.routed([first, written, {**more, "waits": True}, good]),
                "a route from reviewer on `more` with both a `to` and `waits`",
            ),
            (self.routed([*routes, {"from": "a b", "on": "x"}]), "gives a subagent no name"),
            (
                self.routed([first, written, {"from": "planner", "on": "x"}, *routes[2:]]),
                "gives planner, which no file in agents/ names",
            ),
        ):
            with self.subTest(said=said):
                # Given: routes of one route, a first route on a result or none, two first
                # routes, one from write on a result, one with no `on`, two on one result, one to
                # write, one to a subagent nothing is routed from, none to the end, one whose
                # `waits` is not true, one with both a `to` and `waits`, a name no hook can carry,
                # or one no file gives
                # When: the proposal is read
                # Then: it is refused, saying which
                self.assertIn(said, self.refused(given))

    def test_routes_fanning_out_a_subagent_with_its_results_in_order_are_read(self):
        for precedence in (["more", "good"], {"reviewer": ["good", "more"]}, None):
            with self.subTest(precedence=precedence):
                # Given: reviewer fanned out, its results in an order for every subagent, in
                # its own, or writer alone fanned out, which gives one result
                given = {**helpers.ROUTES, "fan_out": ["reviewer"], "precedence": precedence}
                if precedence is None:
                    given = {**helpers.ROUTES, "fan_out": ["writer"]}
                self.propose({"plugin": "changelog", "routes": given})
                # When: the proposal is read
                # Then: it gives the routes as given
                self.assertEqual(proposal.proposal(helpers.PROPOSED)["routes"], given)

    def test_routes_fanning_out_what_they_cannot_are_refused(self):
        for fan_out, precedence, said in (
            (["reviewer"], None, "gives reviewer in `fan_out`, whose results `more` and `good`"),
            (
                ["reviewer"],
                ["more"],
                "gives reviewer in `fan_out`, whose results `more` and `good`",
            ),
            (
                ["reviewer"],
                {"writer": ["written"]},
                "gives reviewer in `fan_out`, whose results `more` and `good`",
            ),
            (["write"], ["more", "good"], "gives write in `fan_out`, which no route starts"),
            (["editor"], ["more", "good"], "gives editor in `fan_out`, which no route starts"),
            (None, ["more", "good", "more"], "gives `more` twice in an order of results"),
            (None, ["more", "done"], "gives `done` in an order of results, which no route is on"),
            (
                None,
                {"writer": ["more"]},
                "gives `more` in an order of results, which no route from writer is on",
            ),
            (
                None,
                {"editor": ["more"]},
                "gives an order of the results of editor, which no route is from",
            ),
            (["reviewer"], "more", "is out of its shape at $.routes.precedence"),
        ):
            with self.subTest(fan_out=fan_out, precedence=precedence):
                # Given: reviewer fanned out with no order of its results, one not holding
                # each, an order of another's alone; write or a subagent no route starts fanned
                # out; an order naming a result twice, one no route is on, one no route from
                # its subagent is on, or a subagent no route is from; or an order in no list
                given = dict(helpers.ROUTES)
                given.update({"fan_out": fan_out} if fan_out else {})
                given.update({"precedence": precedence} if precedence else {})
                # When: the proposal is read
                # Then: it is refused, saying which
                self.assertIn(said, self.refused({"plugin": "changelog", "routes": given}))

    def test_routes_on_files_that_cannot_hold_them_are_refused(self):
        skill = os.path.join("skills", "write", "SKILL.md")
        for file, text, step, said in (
            (skill, helpers.SKILL, 3, "gives step 3, which the Steps of write do not have"),
            (skill, None, 1, "gives write to start the routes, which no skills/write/SKILL.md"),
            (
                os.path.join("agents", "reviewer.md"),
                helpers.REVIEWER.replace("background: true\n", ""),
                1,
                "reviewer, whose file agents/reviewer.md does not set `background: true`",
            ),
            (
                os.path.join("agents", "reviewer.md"),
                helpers.REVIEWER.replace("background: true", "background: false"),
                1,
                "reviewer, whose file agents/reviewer.md does not set `background: true`",
            ),
            (
                os.path.join("agents", "reviewer.md"),
                "---\nname: reviewer\n---\n",
                1,
                "reviewer, whose file has no step to end by its result",
            ),
        ):
            with self.subTest(said=said):
                # Given: the routes laid on a step the skill write does not have, or on no
                # skill's file; reviewer not set to run in the background, or with no steps
                self.setUp()
                if text is None:
                    os.remove(self.skill_file)
                else:
                    self.write(os.path.join(self.plugin, file), text)
                given = {"plugin": "changelog", "routes": {**helpers.ROUTES, "step": step}}
                # When: the proposal is read
                # Then: it is refused, saying why
                told = self.refused(given)
                self.assertIn(said, told)
                self.assertIn(os.path.join(helpers.LANE, "docs", "routes.md"), told)

    def test_a_skill_named_by_no_name_is_refused(self):
        # Given: routes from a skill named with a blank
        given = {
            **helpers.ROUTES,
            "orchestrator": "a b",
            "routes": [{"from": "a b", "to": "writer"}, *helpers.ROUTES["routes"][1:]],
        }
        # When: the proposal is read
        # Then: it is refused, as no command can name the skill
        self.assertIn(
            "gives a skill no name", self.refused({"plugin": "changelog", "routes": given})
        )

    def test_a_skill_whose_part_is_not_there_is_refused(self):
        # Given: the skill write naming its part, which is not there
        self.write(
            self.skill_file,
            "---\nname: write\n---\n\nRead `${CLAUDE_PLUGIN_ROOT}/core/roles/orchestrator.md`.\n",
        )
        # When: the routes are proposed
        # Then: they are refused, naming the part
        self.assertIn(
            "gives write, whose skill names its part core/roles/orchestrator.md, which is not"
            " there",
            self.refused({"plugin": "changelog", "routes": helpers.ROUTES}),
        )

    def test_a_skills_steps_are_read_from_its_part_under_core_roles(self):
        # Given: the skill write naming its part, whose step 1 the routes are laid on
        self.write(
            self.skill_file,
            "---\nname: write\n---\n\nRead"
            " `${CLAUDE_PLUGIN_ROOT}/core/roles/orchestrator.md` whole first.\n",
        )
        self.write(
            os.path.join(self.plugin, "core", "roles", "orchestrator.md"),
            "## Steps\n\n1. Have the entries written.\n",
        )
        self.propose({"plugin": "changelog", "routes": helpers.ROUTES})
        # When: the proposal is read
        # Then: its routes are read
        self.assertEqual(proposal.proposal(helpers.PROPOSED)["routes"], helpers.ROUTES)

    def test_a_routed_subagent_not_set_to_run_in_the_background_is_told_how_to_set_it(self):
        # Given: reviewer's file not setting `background: true`
        self.write(
            os.path.join(self.plugin, "agents", "reviewer.md"),
            helpers.REVIEWER.replace("background: true\n", ""),
        )
        # When: the routes are proposed
        told = self.refused({"plugin": "changelog", "routes": helpers.ROUTES})
        # Then: it is refused, telling to set it in that file's frontmatter
        self.assertTrue(
            told.endswith(
                "; set `background: true` in its frontmatter, as"
                f" {os.path.join(helpers.LANE, 'docs', 'routes.md')} says, and run again."
            ),
            told,
        )

    def test_only_the_skill_needs_its_step(self):
        # Given: routes from write to editor, a name before write's, and reviewer, a name after,
        # neither having write's step 1
        other = "---\nname: {name}\ntools: Read\nbackground: true\n---\n\n## Steps\n\n2. Check.\n"
        for name in ("editor", "reviewer"):
            self.write(os.path.join(self.plugin, "agents", f"{name}.md"), other.format(name=name))
        given = {
            **helpers.ROUTES,
            "routes": [
                {"from": "write", "to": "editor"},
                {"from": "editor", "on": "edited", "to": "reviewer"},
                {"from": "reviewer", "on": "good"},
            ],
        }
        self.propose({"plugin": "changelog", "routes": given})
        # When: the proposal is read
        # Then: its routes are read
        self.assertEqual(proposal.proposal(helpers.PROPOSED)["routes"], given)


class TestRefused(ProposalTest):
    def test_a_proposal_that_cannot_be_read_is_refused(self):
        for given, said in (
            ("{", f"lay.py: {helpers.PROPOSED} holds no JSON;"),
            ({"subagents": []}, "lay.py: the proposal is out of its shape at $: expected the key"),
        ):
            with self.subTest(given=given):
                # Given: a proposal that is no JSON, or out of its shape
                # When: it is read
                # Then: it is refused, pointing to the shape docs/lanes.md gives
                told = self.refused(given)
                self.assertTrue(told.startswith(said), told)
                self.assertIn(os.path.join(helpers.LANE, "docs", "lanes.md"), told)

    def test_a_dependencys_folder_is_named_only_in_a_command_of_a_dependency_declared(self):
        take = "python3 ${dependency:checker}/scripts/check.py x"
        for dependencies, steps, said in (
            (["checker"], [{"step": 2, "lanes": [{"lane": "run_only", "takes": [take]}]}], ""),
            (
                [{"name": "checker"}],
                [{"step": 2, "lanes": [{"lane": "hold", "takes": [take]}]}],
                "",
            ),
            (
                ["checker"],
                [{"step": 3, "lanes": [{"lane": "test_after", "takes": ["a.md", take]}]}],
                "",
            ),
            (
                ["other"],
                [{"step": 2, "lanes": [{"lane": "run_only", "takes": [take]}]}],
                (
                    "gives run_only on step 2 of writer `${dependency:checker}`, which"
                    " .claude-plugin/plugin.json does not declare among its dependencies; declare"
                    " it there, as"
                ),
            ),
            (
                ["checker"],
                [
                    {
                        "step": 3,
                        "lanes": [{"lane": "write_only", "takes": ["${dependency:checker}/a"]}],
                    }
                ],
                (
                    "gives write_only on step 3 of writer `${dependency:checker}`, which only a"
                    " command may name;"
                ),
            ),
            (
                ["checker"],
                [
                    {
                        "step": 3,
                        "lanes": [{"lane": "test_after", "takes": ["${dependency:checker}", take]}],
                    }
                ],
                (
                    "gives test_after on step 3 of writer `${dependency:checker}`, which only a"
                    " command may name;"
                ),
            ),
        ):
            with self.subTest(dependencies=dependencies, steps=steps):
                # Given: writer's manifest declaring dependencies, and a lane naming checker's
                # folder in its command, in a path, or in an output
                manifest = {"name": "changelog", "version": "0.1.0", "dependencies": dependencies}
                self.write_json(self.manifest(), manifest)
                given = self.proposal(steps=steps)
                # When: the proposal is read
                # Then: a command of a dependency declared is read, and the rest refused
                if not said:
                    self.propose(given)
                    self.assertEqual(proposal.proposal(helpers.PROPOSED)["name"], "changelog")
                    continue
                self.assertIn(said, self.refused(given))

    def test_a_value_is_held_as_a_part_only_in_a_command(self):
        for steps, said in (
            ([{"step": 2, "lanes": [{"lane": "run_only", "takes": ["check.py {file}"]}]}], ""),
            ([{"step": 2, "lanes": [{"lane": "hold", "takes": ["git push {branch}"]}]}], ""),
            (
                [{"step": 3, "lanes": [{"lane": "test_after", "takes": ["{work}", "t {work}"]}]}],
                "",
            ),
            (
                [{"step": 3, "lanes": [{"lane": "write_only", "takes": ["docs/{work}.md"]}]}],
                (
                    "gives write_only on step 3 of writer `{work}` in a take, which only a command"
                    " may hold as a part;"
                ),
            ),
            (
                [{"step": 3, "lanes": [{"lane": "test_after", "takes": ["src/{work}", "t"]}]}],
                (
                    "gives test_after on step 3 of writer `{work}` in a take, which only a command"
                    " may hold as a part;"
                ),
            ),
        ):
            with self.subTest(steps=steps):
                # Given: a value as a part of a command run, held or tested by, or of an output
                given = self.proposal(steps=steps)
                # When: the proposal is read
                # Then: a value in a command is read, and one in an output refused
                if not said:
                    self.propose(given)
                    self.assertEqual(proposal.proposal(helpers.PROPOSED)["name"], "changelog")
                    continue
                self.assertIn(said, self.refused(given))

    def test_a_proposal_not_there_is_refused(self):
        # Given: no file at the path
        # When: it is read
        with self.assertRaises(proposal.Stop) as stop:
            proposal.proposal("gone.json")
        # Then: it is refused, saying so
        self.assertTrue(str(stop.exception).startswith("lay.py: there is no file gone.json;"))

    def test_takes_out_of_their_lanes_places_are_refused(self):
        for lane, takes, said in (
            ("in_form", ["entry.json"], "takes out of its places at $.form: expected at least 1"),
            ("test_after", ["src/"], "takes out of its places at $.test: expected at least 1"),
        ):
            with self.subTest(lane=lane):
                # Given: a lane of two places given a thing for its first alone
                steps = [{"step": 3, "lanes": [{"lane": lane, "takes": takes}]}]
                # When: the proposal is read
                # Then: it is refused, naming the place
                self.assertIn(
                    f"gives {lane} on step 3 of writer {said}",
                    self.refused(self.proposal(steps=steps)),
                )

    def test_an_in_form_lane_naming_a_form_it_cannot_read_is_refused(self):
        # Given: in_form naming a form not in the plugin
        lane = {"lane": "in_form", "takes": ["e.json", "${CLAUDE_PLUGIN_ROOT}/forms/gone.json"]}
        steps = [{"step": 3, "lanes": [lane]}]
        # When: the proposal is read
        # Then: it is refused, saying why
        self.assertIn(
            "gives in_form on step 3 of writer, which names the form"
            " ${CLAUDE_PLUGIN_ROOT}/forms/gone.json, which cannot be read",
            self.refused(self.proposal(steps=steps)),
        )

    def test_an_adapter_that_cannot_be_laid_is_refused(self):
        on_run = [{"step": 2, "lanes": [{**helpers.STEPS[0]["lanes"][0], "adapter": "hooks/a.py"}]}]
        for given, files, said in (
            (self.proposal(steps=on_run), [], "gives run_only on step 2 of writer an adapter"),
            (
                self.proposal(adapter="hooks/adapters/items-w.py"),
                [],
                (
                    "names the adapter hooks/adapters/items-w.py on writer, not as"
                    " hooks/adapters/values-<name>.py"
                ),
            ),
            (
                self.proposal(
                    steps=[
                        {
                            "step": 4,
                            "lanes": [
                                {
                                    "lane": "every_item",
                                    "takes": ["review.md"],
                                    "adapter": "hooks/adapters/values-f.py",
                                }
                            ],
                        }
                    ]
                ),
                [],
                (
                    "names the adapter hooks/adapters/values-f.py on step 4 of writer, not as"
                    " hooks/adapters/items-<name>.py"
                ),
            ),
            (self.proposal(adapter="hooks/adapters/values-w.py"), [], "which is not at"),
            (
                self.proposal(adapter="hooks/adapters/values-w.py"),
                [("values-w", helpers.VALUES_ADAPTER, None)],
                "whose cases are not at",
            ),
            (
                self.proposal(adapter="hooks/adapters/values-w.py"),
                [("values-w", helpers.VALUES_ADAPTER, "{")],
                "hold no JSON",
            ),
            (
                self.proposal(adapter="hooks/adapters/values-w.py"),
                [("values-w", helpers.VALUES_ADAPTER, [])],
                "whose cases are out of their shape at $: expected at least 1 item",
            ),
            (
                self.proposal(adapter="hooks/adapters/values-w.py"),
                [("values-w", helpers.VALUES_ADAPTER, [{"given": {}, "gives": {}}])],
                "whose cases are out of their shape at $[0].given",
            ),
            (
                self.proposal(adapter="hooks/adapters/values-w.py"),
                [("values-w", helpers.VALUES_ADAPTER, helpers.VALUES_CASES[:1])],
                "whose cases have none that gives nothing",
            ),
            (
                self.proposal(adapter="hooks/adapters/values-w.py"),
                [("values-w", "import sys\nsys.exit(3)\n", helpers.VALUES_CASES)],
                "which on its case 1 exited 3",
            ),
            (
                self.proposal(adapter="hooks/adapters/values-w.py"),
                [("values-w", "print('{\"values\": {}}')\n", helpers.VALUES_CASES)],
                'which on its case 1 gave {"values": {}}, not {"values": {"work": ["a.md"]}}',
            ),
        ):
            with self.subTest(said=said):
                # Given: an adapter on a lane reading no port, one named for another port, one not
                # beside the proposal, one with no cases, cases of no JSON or out of their shape,
                # none giving nothing, one failing, or one giving a case otherwise than it says
                for name, text, cases in files:
                    self.adapter(name, text, cases)
                # When: the proposal is read
                # Then: it is refused, saying which
                self.assertIn(said, self.refused(given))

    def test_a_lane_taking_nothing_or_an_empty_thing_is_refused(self):
        for takes, said in (([], "with no take"), (["git log", ""], "with a take that is empty")):
            with self.subTest(takes=takes):
                # Given: run_only on step 2 taking no command, or an empty one beside another
                steps = [{"step": 2, "lanes": [{"lane": "run_only", "takes": takes}]}]
                # When: the proposal is read
                # Then: it is refused
                self.assertIn(
                    f"gives run_only on step 2 of writer {said}",
                    self.refused(self.proposal(steps=steps)),
                )

    def test_a_plugin_that_cannot_be_found_or_named_is_refused(self):
        for manifest, said in (
            (None, "names changelog as the plugin, which has no"),
            ("{", "holds no JSON; fix it and run again."),
            ('{"name": "change log"}', "names the plugin by no name of letters, digits and -._"),
            ("[]", "names the plugin by no name of letters, digits and -._"),
        ):
            with self.subTest(manifest=manifest):
                # Given: a plugin with no manifest, one of no JSON, a name of a blank, or none
                if os.path.exists(self.manifest()):
                    os.remove(self.manifest())
                if manifest is not None:
                    self.write(self.manifest(), manifest)
                # When: the proposal is read
                # Then: it is refused
                self.assertIn(said, self.refused(helpers.PROPOSAL))

    def test_a_subagent_or_step_that_cannot_be_laid_is_refused(self):
        twice = {"name": "writer", "steps": helpers.STEPS}
        step_twice = [helpers.STEPS[0], helpers.STEPS[0]]
        no_step = [{"step": 9, "lanes": helpers.STEPS[0]["lanes"]}]
        for given, said in (
            (
                {"plugin": "changelog", "subagents": [{**twice, "name": "a b"}]},
                "gives a subagent no name",
            ),
            (
                {"plugin": "changelog", "subagents": [{**twice, "name": "lead"}]},
                "gives lead, which no file in agents/ names",
            ),
            ({"plugin": "changelog", "subagents": [twice, twice]}, "gives writer twice"),
            (self.proposal(steps=step_twice), "gives step 2 of writer twice"),
            (self.proposal(steps=no_step), "gives step 9, which the Steps of writer do not have"),
        ):
            with self.subTest(said=said):
                # Given: a subagent of a name no hook can carry, one no file gives, one given
                # twice, a step given twice, or a step its file does not have
                # When: the proposal is read
                # Then: it is refused, saying which
                self.assertIn(said, self.refused(given))

    def test_a_subagent_not_set_to_run_in_the_background_is_refused(self):
        for text in (
            helpers.WRITER.replace("background: true\n", ""),
            helpers.WRITER.replace("background: true", "background: false"),
        ):
            with self.subTest(text=text):
                # Given: writer's file setting no `background`, or setting it false
                self.write(self.agent_file, text)
                # When: the README's proposal is read
                # Then: it is refused, telling to set it in that file's frontmatter
                self.assertEqual(
                    self.refused(helpers.PROPOSAL),
                    "lay.py: the proposal gives writer, whose file agents/writer.md does not set"
                    " `background: true`, which lane needs to tell each of its runs from the"
                    " others; set `background: true` in its frontmatter, as"
                    f" {os.path.join(helpers.LANE, 'docs', 'lanes.md')} says, and run again.",
                )


if __name__ == "__main__":
    unittest.main()
