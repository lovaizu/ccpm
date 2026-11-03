"""The routes: the result command each subagent gives its result by, and the next start, decided
from the routes and the starts of the orchestrator as they came back, with the result each started
subagent gave, and the line the orchestrator is told of it."""

import unittest

import helpers
from helpers import routes

# Each start of docs/routes.md's run, as lead's calls came back: writer, then reviewer, ended.
WRITER = routes.Start("writer", "completed", "w1")
REVIEWER = routes.Start("reviewer", "completed", "r1")


def decided(starts: list, results: dict, ended: tuple = ()) -> routes.Next:
    """The next start after the starts, each started subagent's ID giving the result of `results`,
    those of `ended` ended in the background."""
    return routes.next_start(helpers.ROUTES, starts, results.get, lambda a: a in ended)


class TestCommands(unittest.TestCase):
    def test_a_result_command_names_the_script_by_the_plugins_folder_the_subagent_and_result(self):
        # Given: reviewer giving `more`
        # When: its command is made
        # Then: it runs the result script in the plugin's hooks/lane/ with the name and result
        self.assertEqual(routes.command("reviewer", "more"), f"{helpers.GIVE} reviewer more")

    def test_each_subagent_gives_the_results_its_routes_are_on_in_their_order(self):
        for name, ons in (("writer", ["written"]), ("reviewer", ["more", "good"]), ("lead", [])):
            with self.subTest(name=name):
                # Given: docs/routes.md's routes
                # When: the results of the subagent are asked for
                # Then: they are the `on` of each route from it, in order; none for lead
                self.assertEqual(routes.ons(helpers.ROUTES, name), ons)

    def test_the_subagents_named_are_the_orchestrator_then_each_in_the_routes(self):
        # Given: docs/routes.md's routes
        # When: the subagents they name are asked for
        # Then: they are lead, writer and reviewer, each once
        self.assertEqual(routes.named(helpers.ROUTES), ["lead", "writer", "reviewer"])

    def test_the_subagents_giving_results_are_those_routed_from_but_the_orchestrator(self):
        # Given: docs/routes.md's routes
        # When: the subagents that give results are asked for
        # Then: they are writer and reviewer
        self.assertEqual(routes.giving(helpers.ROUTES), ["writer", "reviewer"])


class TestNextStart(unittest.TestCase):
    def test_with_no_start_yet_the_orchestrators_route_is_due(self):
        # Given: no start of lead's yet
        # When: the next start is decided
        # Then: writer is due, after no result
        self.assertEqual(decided([], {}), routes.Next("start", "writer", None))

    def test_each_result_leads_to_its_routes_start_or_to_the_end(self):
        for starts, results, found in (
            ([WRITER], {"w1": "written"}, routes.Next("start", "reviewer", ("writer", "written"))),
            (
                [WRITER, REVIEWER],
                {"w1": "written", "r1": "more"},
                routes.Next("start", "writer", ("reviewer", "more")),
            ),
            (
                [WRITER, REVIEWER],
                {"w1": "written", "r1": "good"},
                routes.Next("end", "", ("reviewer", "good")),
            ),
        ):
            with self.subTest(results=results):
                # Given: writer ended with `written`, then reviewer with `more` or `good`
                # When: the next start is decided
                # Then: it is the `to` of the route of the last result, or the end
                self.assertEqual(decided(starts, results), found)

    def test_the_orchestrators_route_is_due_wherever_it_lies_in_the_routes(self):
        # Given: lead's route listed after routes from author and writer
        given = {
            **helpers.ROUTES,
            "routes": [
                {"from": "writer", "on": "written", "to": "reviewer"},
                {"from": "author", "on": "drafted", "to": "writer"},
                {"from": "lead", "to": "author"},
            ],
        }
        # When: the next start is decided with no start yet
        # Then: lead's route is due, and no other
        found = routes.next_start(given, [], {}.get, lambda a: False)
        self.assertEqual(found, routes.Next("start", "author", None))

    def test_a_start_still_in_the_background_leaves_a_later_start_to_decide(self):
        # Given: writer launched in the background and still running, then reviewer started and
        # ended with `good`
        starts = [routes.Start("writer", "async_launched", "w1"), REVIEWER]
        # When: the next start is decided
        # Then: reviewer's result decides it, as only a start whose subagent has ended counts
        found = decided(starts, {"r1": "good"})
        self.assertEqual(found, routes.Next("end", "", ("reviewer", "good")))

    def test_a_subagent_ended_with_no_result_is_due_again(self):
        # Given: writer ended with no result given
        # When: the next start is decided
        # Then: writer is due again, as its start led nowhere
        self.assertEqual(decided([WRITER], {}), routes.Next("start", "writer", None))

    def test_a_subagent_in_the_background_is_waited_for_until_it_ends(self):
        started = [routes.Start("writer", "async_launched", "w1")]
        for ended, found in (
            ((), routes.Next("wait", "writer", None)),
            (("w1",), routes.Next("start", "reviewer", ("writer", "written"))),
        ):
            with self.subTest(ended=ended):
                # Given: writer launched in the background, running or ended with `written`
                # When: the next start is decided
                # Then: lead waits for it, or, once it has ended, reviewer is due
                self.assertEqual(decided(started, {"w1": "written"}, ended), found)

    def test_starts_after_the_end_are_left_out(self):
        # Given: reviewer's `good`, then writer started again, its orchestrator being free
        starts = [WRITER, REVIEWER, routes.Start("writer", "completed", "w2")]
        # When: the next start is decided
        # Then: it is still the end
        found = decided(starts, {"w1": "written", "r1": "good", "w2": "written"})
        self.assertEqual(found, routes.Next("end", "", ("reviewer", "good")))


class TestLine(unittest.TestCase):
    def test_each_next_start_is_told_in_its_line_of_docs_routes_md(self):
        for found, said in (
            (routes.Next("start", "writer", None), "Start `changelog:writer`."),
            (
                routes.Next("start", "reviewer", ("writer", "written")),
                "writer gave `written`. Start `changelog:reviewer`.",
            ),
            (
                routes.Next("wait", "writer", None),
                "Wait for `changelog:writer` to end: you are told the next start once it has.",
            ),
            (
                routes.Next("end", "", ("reviewer", "good")),
                "reviewer gave `good`. Start no more subagents.",
            ),
        ):
            with self.subTest(found=found):
                # Given: a next start of each kind
                # When: its line is made for changelog
                # Then: it reads as the table of docs/routes.md has it
                self.assertEqual(routes.line(found, "changelog"), said)


if __name__ == "__main__":
    unittest.main()
