"""The cases of routes.py's contract: whether a plugin can follow its routes, which results a role
may give, and which start is due from the starts kept, as plugins/lane/docs/routes.md gives them."""

import helpers
from helpers import called, laid, routes, testing

# The walkthrough's routes: write starts writer, then reviewer, and writer again on `more`.
CHANGELOG = helpers.ROUTES
ROUTES = routes.parsed(CHANGELOG)


def given(**more):
    return routes.parsed({**CHANGELOG, **more})


def start(role, result=None, running=False, agent="a"):
    return called.Start(agent, role, "", running, result)


def group(*starts):
    return called.Group(starts[0].role, tuple(starts))


class TestParsed(testing.FolderTest):
    def test_each_route_keeps_where_it_leads(self):
        self.assertEqual(ROUTES.routes[1], routes.Route("writer", "written", "reviewer", False))

    def test_a_route_that_waits_has_no_to(self):
        found = given(
            routes=[*CHANGELOG["routes"], {"from": "writer", "on": "asks", "waits": True}]
        )
        self.assertEqual(found.routes[-1], routes.Route("writer", "asks", None, True))

    def test_the_skill_step_and_command_are_kept(self):
        found = given(command="python3 s.py")
        self.assertEqual(
            (found.orchestrator, found.step, found.command), ("write", 1, "python3 s.py")
        )

    def test_routes_with_no_step_lay_no_sentence_in_the_skill(self):
        data = {k: v for k, v in CHANGELOG.items() if k != "step"}
        self.assertIsNone(routes.parsed(data).step)


class TestFaults(testing.FolderTest):
    def faults(self, **more):
        return routes.faults(given(**more))

    def test_the_walkthroughs_routes_can_be_followed(self):
        self.assertEqual(routes.faults(ROUTES), [])

    def test_routes_with_no_first_start_are_a_fault(self):
        self.assertEqual(
            self.faults(routes=CHANGELOG["routes"][1:]),
            ["the routes hold no route from write with a `to` and no `on`, the first start"],
        )

    def test_two_first_starts_are_a_fault(self):
        first = CHANGELOG["routes"][0]
        self.assertEqual(
            self.faults(routes=[first, *CHANGELOG["routes"]]),
            ["the routes hold more than one route from write"],
        )

    def test_a_route_from_a_subagent_with_no_on_is_a_fault(self):
        self.assertEqual(
            self.faults(routes=[*CHANGELOG["routes"], {"from": "reviewer", "to": "writer"}]),
            ["the route from reviewer to writer has no `on`"],
        )

    def test_two_routes_from_one_subagent_on_one_result_are_a_fault(self):
        twice = {"from": "reviewer", "on": "good", "to": "writer"}
        self.assertEqual(
            self.faults(routes=[*CHANGELOG["routes"], twice]),
            ["two routes from reviewer are on `good`"],
        )

    def test_a_route_with_both_a_to_and_waits_is_a_fault(self):
        both = {"from": "writer", "on": "asks", "to": "reviewer", "waits": True}
        self.assertEqual(
            self.faults(routes=[*CHANGELOG["routes"], both]),
            ["the route from writer on `asks` has both a `to` and `waits`"],
        )

    def test_a_subagent_started_with_no_route_from_it_is_a_fault(self):
        lost = {"from": "writer", "on": "lost", "to": "noter"}
        self.assertEqual(
            self.faults(routes=[*CHANGELOG["routes"], lost]),
            ["noter is started, and no route is from it, so it has no result to give"],
        )

    def test_routes_with_no_end_are_a_fault(self):
        loop = [*CHANGELOG["routes"][:3], {"from": "reviewer", "on": "good", "to": "writer"}]
        self.assertEqual(
            self.faults(routes=loop),
            ["no route has neither a `to` nor `waits`, so the run can't end"],
        )

    def test_a_route_that_waits_from_a_subagent_that_fans_out_is_a_fault(self):
        asks = {"from": "reviewer", "on": "asks", "waits": True}
        self.assertEqual(
            self.faults(
                routes=[*CHANGELOG["routes"], asks],
                fan_out=["reviewer"],
                precedence=["asks", "more", "good"],
            ),
            ["reviewer fans out, so Lane can't tell which of its starts to resume on `asks`"],
        )

    def test_fan_out_of_a_subagent_no_route_starts_is_a_fault(self):
        self.assertEqual(
            self.faults(fan_out=["noter"]),
            ["fan_out names noter, which no route starts"],
        )

    def test_a_subagent_that_fans_out_with_its_results_unordered_is_a_fault(self):
        self.assertEqual(
            self.faults(fan_out=["reviewer"]),
            ["reviewer fans out and gives more than one result, so precedence orders each of them"],
        )

    def test_an_order_naming_a_result_no_route_is_on_is_a_fault(self):
        self.assertEqual(
            self.faults(precedence=["more", "good", "lost"]),
            ["precedence names `lost`, which no route is on"],
        )

    def test_an_order_naming_a_result_twice_is_a_fault(self):
        self.assertEqual(
            self.faults(precedence={"reviewer": ["more", "more", "good"]}),
            ["precedence names `more` twice for reviewer"],
        )

    def test_one_order_for_each_subagent_holds_its_results(self):
        self.assertEqual(
            self.faults(fan_out=["reviewer"], precedence={"reviewer": ["more", "good"]}), []
        )


class TestResults(testing.FolderTest):
    def test_a_subagent_routes_are_from_gives_the_results_they_are_on(self):
        self.assertEqual(
            routes.allowed(laid.parsed({"routes": CHANGELOG}), "reviewer"), ["more", "good"]
        )

    def test_the_skill_gives_the_results_of_the_routes_that_end_the_run(self):
        self.assertEqual(routes.allowed(laid.parsed({"routes": CHANGELOG}), "write"), ["good"])

    def test_a_role_with_no_route_gives_the_results_its_lanes_name(self):
        role = {"name": "noter", "results": ["asks", "done"], "steps": []}
        self.assertEqual(
            routes.allowed(laid.parsed({"subagents": [role]}), "noter"), ["asks", "done"]
        )

    def test_a_role_with_no_route_beside_routes_gives_the_results_its_lanes_name(self):
        role = {"name": "noter", "results": ["asks"], "steps": []}
        found = laid.parsed({"subagents": [role], "routes": CHANGELOG})
        self.assertEqual(routes.allowed(found, "noter"), ["asks"])

    def test_a_role_with_no_route_and_no_results_named_gives_done(self):
        role = {"name": "noter", "steps": []}
        self.assertEqual(routes.allowed(laid.parsed({"subagents": [role]}), "noter"), ["done"])

    def test_each_role_the_routes_name_is_named_once(self):
        self.assertEqual(routes.named(ROUTES), ["writer", "reviewer"])


def commands(name, *results):
    return [f"python3 ${{CLAUDE_PLUGIN_ROOT}}/hooks/lane/result.py {name} {r}" for r in results]


class TestResultCommands(testing.FolderTest):
    def lanes(self, *lanes, **more):
        role = {"name": "noter", "steps": [{"step": 1, "lanes": list(lanes)}], **more}
        return laid.parsed({"subagents": [role]})

    def test_a_subagent_routes_are_from_gives_a_command_for_each_result(self):
        found = laid.parsed({"routes": CHANGELOG})
        self.assertEqual(
            routes.result_commands(found, "reviewer"), commands("reviewer", "more", "good")
        )

    def test_the_skill_gives_a_command_for_each_result_that_ends_the_run(self):
        found = laid.parsed({"routes": CHANGELOG})
        self.assertEqual(routes.result_commands(found, "write"), commands("write", "good"))

    def test_a_role_with_a_lane_checked_at_the_end_gives_done(self):
        found = self.lanes({"lane": "end_when", "takes": ["a"]})
        self.assertEqual(routes.result_commands(found, "noter"), commands("noter", "done"))

    def test_a_role_with_a_lane_of_the_trace_kind_gives_done(self):
        found = self.lanes({"lane": "write_step", "takes": ["a"]})
        self.assertEqual(routes.result_commands(found, "noter"), commands("noter", "done"))

    def test_a_role_with_results_named_gives_each(self):
        found = self.lanes({"lane": "write_only", "takes": ["a"]}, results=["asks", "done"])
        self.assertEqual(routes.result_commands(found, "noter"), commands("noter", "asks", "done"))

    def test_a_role_whose_lanes_check_no_end_gives_no_result(self):
        found = self.lanes({"lane": "write_only", "takes": ["a"]})
        self.assertEqual(routes.result_commands(found, "noter"), [])

    def test_a_name_neither_the_lanes_nor_the_routes_give_gives_no_result(self):
        self.assertEqual(routes.result_commands(laid.parsed({"routes": CHANGELOG}), "noter"), [])


class TestCombined(testing.FolderTest):
    def test_starts_that_gave_one_result_give_it(self):
        self.assertEqual(routes.combined(ROUTES, "reviewer", ["good", "good"]), "good")

    def test_starts_that_gave_different_results_give_the_first_in_the_order(self):
        found = given(precedence=["more", "good"])
        self.assertEqual(routes.combined(found, "reviewer", ["good", "more", "good"]), "more")

    def test_the_order_of_a_subagent_by_its_name_is_taken(self):
        found = given(precedence={"reviewer": ["good", "more"]})
        self.assertEqual(routes.combined(found, "reviewer", ["more", "good"]), "good")

    def test_different_results_no_order_holds_give_none(self):
        self.assertIsNone(routes.combined(ROUTES, "reviewer", ["more", "good"]))


class TestDue(testing.FolderTest):
    def test_a_run_with_no_start_has_the_first_start_due(self):
        self.assertEqual(routes.due(ROUTES, []), routes.Due("start", "writer"))

    def test_a_start_still_running_has_a_wait_due(self):
        self.assertEqual(
            routes.due(ROUTES, [group(start("writer", running=True))]),
            routes.Due("wait", "writer", count=1),
        )

    def test_a_result_whose_route_has_a_to_has_that_start_due(self):
        self.assertEqual(
            routes.due(ROUTES, [group(start("writer", "written"))]),
            routes.Due("start", "reviewer", "written", "writer", 1),
        )

    def test_the_routes_are_followed_through_each_start(self):
        groups = [group(start("writer", "written")), group(start("reviewer", "more"))]
        self.assertEqual(
            routes.due(ROUTES, groups), routes.Due("start", "writer", "more", "reviewer", 1)
        )

    def test_a_result_whose_route_ends_the_run_has_the_end_due(self):
        groups = [group(start("writer", "written")), group(start("reviewer", "good"))]
        self.assertEqual(
            routes.due(ROUTES, groups), routes.Due("end", "reviewer", "good", "reviewer", 1)
        )

    def test_a_result_whose_route_waits_has_the_point_due(self):
        found = given(
            routes=[*CHANGELOG["routes"], {"from": "writer", "on": "asks", "waits": True}]
        )
        self.assertEqual(
            routes.due(found, [group(start("writer", "asks", agent="w1"))]),
            routes.Due("waits", "writer", "asks", "writer", 1, "w1"),
        )

    def test_a_start_that_ended_with_no_result_is_due_again(self):
        self.assertEqual(
            routes.due(ROUTES, [group(start("writer"))]), routes.Due("again", "writer")
        )

    def test_starts_at_once_whose_results_no_order_holds_are_unordered(self):
        groups = [
            group(start("writer", "written")),
            group(start("reviewer", "more"), start("reviewer", "good")),
        ]
        self.assertEqual(routes.due(ROUTES, groups), routes.Due("unordered", "reviewer"))

    def test_starts_at_once_give_the_count_of_their_runs(self):
        found = given(fan_out=["reviewer"], precedence=["more", "good"])
        groups = [
            group(start("writer", "written")),
            group(start("reviewer", "good"), start("reviewer", "more")),
        ]
        self.assertEqual(
            routes.due(found, groups), routes.Due("start", "writer", "more", "reviewer", 2)
        )


class TestTyped(testing.FolderTest):
    def test_a_role_of_the_plugin_is_named_with_the_plugins_name(self):
        self.assertEqual(routes.typed("changelog", "writer"), "changelog:writer")

    def test_a_role_of_a_dependency_is_named_as_it_is(self):
        self.assertEqual(routes.typed("changelog", "checker:examiner"), "checker:examiner")
