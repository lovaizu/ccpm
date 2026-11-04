"""The routes: the result command each subagent gives its result by, and the next start, decided
from the routes and the starts of the orchestrator as they came back, with the result each started
subagent gave, and the line the orchestrator is told of it."""

import json
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
        self.assertEqual(decided([WRITER], {}), routes.Next("start", "writer", None, True))

    def test_a_result_no_route_is_on_has_its_subagent_due_again(self):
        # Given: writer ended with a result no route from it is on, as the result script refuses
        # When: the next start is decided
        # Then: writer is due again, as its start led nowhere
        found = decided([WRITER], {"w1": "drafted"})
        self.assertEqual(found, routes.Next("start", "writer", None, True))

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


# docs/routes.md's routes with reviewer run several at once, its results taken in their order.
FANNED = {**helpers.ROUTES, "fan_out": ["reviewer"], "precedence": ["more", "good"]}


def fanned(
    starts: list, results: dict, ended: tuple = (), given: dict = FANNED, left: tuple = ()
) -> routes.Next:
    """The next start after the starts by the routes given, reviewer fanned out by default, the
    runs of `left` having ended with no result once."""
    return routes.next_start(given, starts, results.get, lambda a: a in ended, lambda a: a in left)


def reviewer(agent: str, joined: str = "") -> routes.Start:
    """A start of reviewer launched in the background, joined to the starts before it as given."""
    return routes.Start("reviewer", "async_launched", agent, joined)


class TestFanOut(unittest.TestCase):
    def test_runs_joined_are_waited_for_until_every_one_has_ended(self):
        starts = [WRITER, reviewer("r1"), reviewer("r2", "more")]
        for ended in ((), ("r1",), ("r2",)):
            with self.subTest(ended=ended):
                # Given: two runs of reviewer at once, none or one of them ended with `good`
                # When: the next start is decided
                # Then: lead waits for every run, and may start more of them
                found = fanned(starts, {"w1": "written", "r1": "good", "r2": "good"}, ended)
                self.assertEqual(found, routes.Next("wait", "reviewer", None, more=True))

    def test_the_runs_ended_give_the_result_they_share_or_the_first_in_the_order(self):
        starts = [WRITER, reviewer("r1"), reviewer("r2", "more"), reviewer("r3", "more")]
        for given, found in (
            (["good", "good", "good"], routes.Next("end", "", ("reviewer", "good"), runs=3)),
            (
                ["good", "more", "good"],
                routes.Next("start", "writer", ("reviewer", "more"), runs=3),
            ),
            (
                ["more", "good", "good"],
                routes.Next("start", "writer", ("reviewer", "more"), runs=3),
            ),
        ):
            with self.subTest(given=given):
                # Given: three runs of reviewer at once, all ended, giving the results
                results = {"w1": "written", **dict(zip(("r1", "r2", "r3"), given))}
                # When: the next start is decided
                # Then: the route is that of the result they share, or of `more`, the first of
                # the routes' order among those they gave
                self.assertEqual(fanned(starts, results, ("r1", "r2", "r3")), found)

    def test_the_order_of_a_subagents_own_results_comes_before_the_shared_one(self):
        # Given: an order for every subagent, `good` first, and reviewer's own, `more` first
        given = {**FANNED, "precedence": {"reviewer": ["more", "good"], "writer": ["written"]}}
        starts = [WRITER, reviewer("r1"), reviewer("r2", "more")]
        # When: its two runs give `good` and `more`
        found = fanned(starts, {"w1": "written", "r1": "good", "r2": "more"}, ("r1", "r2"), given)
        # Then: `more` is the result, by reviewer's own order
        self.assertEqual(found, routes.Next("start", "writer", ("reviewer", "more"), runs=2))

    def test_runs_giving_differing_results_with_no_order_cannot_be_told(self):
        for precedence in ((), ({"writer": ["written"]},), (["good"],)):
            with self.subTest(precedence=precedence):
                # Given: reviewer fanned out, with no order, an order of another's results only,
                # or one that does not hold `more`
                given = {**helpers.ROUTES, "fan_out": ["reviewer"]}
                given.update({"precedence": precedence[0]} if precedence else {})
                starts = [WRITER, reviewer("r1"), reviewer("r2", "more")]
                results = {"w1": "written", "r1": "good", "r2": "more"}
                # When: its two runs give `good` and `more`
                # Then: the next start cannot be told, naming the results given
                with self.assertRaises(routes.Unordered) as stop:
                    fanned(starts, results, ("r1", "r2"), given)
                self.assertEqual(
                    str(stop.exception),
                    "the runs of reviewer at once gave `good` and `more`, and the routes order"
                    " not each of them in `precedence`",
                )

    def test_a_run_ended_with_no_result_has_its_subagent_started_again_into_the_runs(self):
        first = [WRITER, reviewer("r1"), reviewer("r2", "more")]
        for starts, results, found in (
            (first, {"r1": "good"}, routes.Next("start", "reviewer", None, True)),
            (
                [*first, reviewer("r3", "again")],
                {"r1": "good", "r3": "more"},
                routes.Next("start", "writer", ("reviewer", "more"), runs=2),
            ),
            (
                [*first, reviewer("r3", "again")],
                {"r1": "good"},
                routes.Next("start", "reviewer", None, True),
            ),
            (
                [*first, reviewer("r3", "again"), reviewer("r4", "again")],
                {"r1": "good", "r4": "good"},
                routes.Next("end", "", ("reviewer", "good"), runs=2),
            ),
        ):
            with self.subTest(starts=starts, results=results):
                # Given: two runs of reviewer at once, one ending with no result, then started
                # again once or twice, the run started again giving a result or none
                results = {"w1": "written", **results}
                # When: the next start is decided, every run ended
                # Then: reviewer is due again while a run is owed a result, and the route of the
                # results is taken once each is given
                ended = ("r1", "r2", "r3", "r4")
                self.assertEqual(fanned(starts, results, ended), found)

    def test_a_run_started_again_takes_the_place_of_one_with_no_result_given_one_after(self):
        for given, starts, results, found in (
            (
                helpers.ROUTES,
                [WRITER, reviewer("r1"), reviewer("r2", routes.AGAIN)],
                {"r1": "more", "r2": "good"},
                routes.Next("end", "", ("reviewer", "good")),
            ),
            (
                FANNED,
                [WRITER, reviewer("r1"), reviewer("r2", "more"), reviewer("r3", routes.AGAIN)],
                {"r1": "more", "r2": "good", "r3": "good"},
                routes.Next("end", "", ("reviewer", "good"), runs=2),
            ),
        ):
            with self.subTest(given=given):
                # Given: reviewer, alone or fanned out, its run r1 ended with no result and
                # started again, then resumed, giving `more`
                results = {"w1": "written", **results}
                ended = ("r1", "r2", "r3")
                # When: the next start is decided, every run ended
                # Then: r1 is out of the count, the run started again in its place
                self.assertEqual(fanned(starts, results, ended, given, ("r1",)), found)

    def test_a_start_not_joined_counts_alone_whatever_its_subagent(self):
        # Given: two runs of reviewer, the second not joined to the first, both ended
        starts = [WRITER, reviewer("r1"), reviewer("r2")]
        # When: the first gives `more` and the second `good`
        found = fanned(starts, {"w1": "written", "r1": "more", "r2": "good"}, ("r1", "r2"))
        # Then: the second decides alone, as each start not joined counts as it always has
        self.assertEqual(found, routes.Next("end", "", ("reviewer", "good")))

    def test_a_run_joined_after_the_others_led_to_the_end_still_counts_with_them(self):
        # Given: two runs of reviewer at once, the first ended with `good` before the second's
        # start came back, then a start not joined and one joined after that
        starts = [WRITER, reviewer("r1"), reviewer("r2", "more")]
        later = [reviewer("r3"), reviewer("r4", "more")]
        results = {"w1": "written", "r1": "good", "r2": "more", "r3": "more", "r4": "more"}
        ended = ("r1", "r2", "r3", "r4")
        # When: the next start is decided, every run ended
        # Then: the second's `more` counts with the first's, and the starts after the next
        # start not joined to the runs are left out, as the guard keeps none once at the end
        expected = routes.Next("start", "writer", ("reviewer", "more"), runs=2)
        self.assertEqual(fanned(starts, results, ended), expected)
        fixed = {**results, "r2": "good"}
        found = fanned([*starts, *later], fixed, ended)
        self.assertEqual(found, routes.Next("end", "", ("reviewer", "good"), runs=2))

    def test_a_start_joined_counts_with_the_runs_of_its_own_subagent_alone(self):
        # Subagents fanned out whose names sort before writer's and after it.
        given = {**FANNED, "fan_out": ["author", "reviewer", "zeta"]}
        for name in ("author", "zeta"):
            with self.subTest(name=name):
                # Given: writer ended with `written`, then a start of another subagent kept as
                # joined to it, ended in the foreground with `good`
                starts = [WRITER, routes.Start(name, "completed", "x1", routes.MORE)]
                # When: the next start is decided
                # Then: it counts alone, its `good` leading nowhere, as it is not writer's
                found = fanned(starts, {"w1": "written", "x1": "good"}, (), given)
                self.assertEqual(found, routes.Next("start", name, None, True))
        # And: a run of reviewer joined by its name read from JSON, not a text the code writes,
        # joins it
        same = json.loads('"reviewer"')
        starts = [WRITER, reviewer("r1"), routes.Start(same, "async_launched", "r2", routes.MORE)]
        found = fanned(starts, {"w1": "written", "r1": "good"}, ("r1",))
        self.assertEqual(found, routes.Next("wait", "reviewer", None, more=True))

    def test_runs_giving_more_results_than_are_owed_count_each(self):
        # Given: reviewer, then a run of it started again though none ended with no result
        starts = [WRITER, reviewer("r1"), reviewer("r2", routes.AGAIN)]
        # When: both give `good`
        found = fanned(starts, {"w1": "written", "r1": "good", "r2": "good"}, ("r1", "r2"))
        # Then: the route of `good` is taken, from both
        self.assertEqual(found, routes.Next("end", "", ("reviewer", "good"), runs=2))

    def test_a_subagent_not_fanned_out_is_waited_for_with_no_more_runs(self):
        # Given: writer, not fanned out, running in the background
        starts = [routes.Start("writer", "async_launched", "w1")]
        # When: the next start is decided
        # Then: lead waits for it, starting no more of it
        found = fanned(starts, {})
        self.assertEqual(found, routes.Next("wait", "writer", None))


# What is wrong with routes fanning out reviewer with its results not ordered.
UNORDERED = (
    "gives reviewer in `fan_out`, whose results `more` and `good` the routes do not order in"
    " `precedence`, so the result of its runs at once could not be told"
)


class TestUnordered(unittest.TestCase):
    def test_a_subagent_fanned_out_whose_results_the_order_does_not_hold_is_named(self):
        for given, said in (
            (FANNED, None),
            ({**helpers.ROUTES, "fan_out": ["writer"]}, None),
            (
                {**helpers.ROUTES, "fan_out": ["reviewer"]},
                UNORDERED,
            ),
            (
                {**helpers.ROUTES, "fan_out": ["reviewer"], "precedence": ["good"]},
                UNORDERED,
            ),
        ):
            with self.subTest(given=given):
                # Given: reviewer fanned out with its results in order, writer of one result
                # fanned out, or reviewer fanned out with no order or one not holding `more`
                # When: the routes are checked for an order of results they lack
                # Then: the subagent whose results are not ordered is named, or none is
                self.assertEqual(routes.unordered(given), said)


class TestLine(unittest.TestCase):
    def test_each_next_start_is_told_in_its_line_of_docs_routes_md(self):
        for found, said in (
            (routes.Next("start", "writer", None), "Start `changelog:writer`."),
            (
                routes.Next("start", "writer", None, True),
                "writer ended with no result. Start `changelog:writer` again.",
            ),
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
            (
                routes.Next("wait", "reviewer", None, more=True),
                (
                    "Wait for every run of `changelog:reviewer` to end: you are told the next"
                    " start once each has."
                ),
            ),
            (
                routes.Next("start", "writer", ("reviewer", "more"), runs=2),
                "The 2 runs of reviewer gave `more`. Start `changelog:writer`.",
            ),
            (
                routes.Next("end", "", ("reviewer", "good"), runs=3),
                "The 3 runs of reviewer gave `good`. Start no more subagents.",
            ),
        ):
            with self.subTest(found=found):
                # Given: a next start of each kind
                # When: its line is made for changelog
                # Then: it reads as the table of docs/routes.md has it
                self.assertEqual(routes.line(found, "changelog"), said)


class TestRefused(unittest.TestCase):
    """The checks of the routes alone that `lay.py print` makes and the guard makes again on the
    routes laid, kept in routes.py alone (dev/lane/architecture.md, What each role alone
    decides)."""

    def given(self, **changed) -> dict:
        """docs/routes.md's routes, changed as given."""
        return {**helpers.ROUTES, **changed}

    def test_docs_routes_mds_routes_are_refused_by_nothing(self):
        # Given: docs/routes.md's routes
        # When: they are checked
        # Then: nothing refuses them
        self.assertEqual(routes.refused(helpers.ROUTES), "")

    def test_routes_that_cannot_be_followed_are_refused_saying_why(self):
        each = helpers.ROUTES["routes"]
        for changed, said in (
            ({"routes": each[1:]}, "gives the routes no one route from lead with a `to`"),
            ({"routes": [{"from": "lead"}, *each[1:]]}, "gives the routes no one route from lead"),
            ({"routes": [*each, {"from": "writer"}]}, "gives a route from writer with no `on`"),
            ({"routes": [*each, each[1]]}, "gives two routes from writer on `written`"),
            (
                {"routes": [*each, {"from": "reviewer", "on": "x", "to": "lead"}]},
                "gives a route to lead, the orchestrator",
            ),
            (
                {"routes": [*each, {"from": "reviewer", "on": "x", "to": "linter"}]},
                "gives a route to linter, which no route is from",
            ),
            (
                {"routes": [*each[:3], {"from": "reviewer", "on": "good", "to": "writer"}]},
                "gives no route without a `to`",
            ),
            (
                {"precedence": {"lead": ["more"]}},
                "gives an order of the results of lead, which no route is from",
            ),
            ({"precedence": ["more", "more"]}, "gives `more` twice in an order of results"),
            ({"precedence": ["late"]}, "gives `late` in an order of results, which no route is on"),
            (
                {"precedence": {"writer": ["more"]}},
                "gives `more` in an order of results, which no route from writer is on",
            ),
            ({"fan_out": ["lead"]}, "gives lead in `fan_out`, which no route starts"),
            ({"fan_out": ["reviewer"]}, "gives reviewer in `fan_out`, whose results"),
        ):
            with self.subTest(changed=changed):
                # Given: docs/routes.md's routes, changed so they cannot be followed
                # When: they are checked
                # Then: they are refused, saying why, as the proposal's error goes on
                found = routes.refused(self.given(**changed))
                self.assertTrue(found.startswith(said), found)


class TestDependency(unittest.TestCase):
    """A route naming a subagent of a dependency, `<dependency>:<name>`, as docs/routes.md's A
    subagent of a dependency gives it."""

    def test_a_subagent_is_named_by_claude_codes_type_its_plugins_or_its_own(self):
        for name, found in (
            ("writer", "changelog:writer"),
            ("checker:examiner", "checker:examiner"),
        ):
            with self.subTest(name=name):
                # Given: a subagent of changelog, or of its dependency checker
                # When: its type is asked for
                # Then: it is changelog's name before its own, or the name as the routes give it
                self.assertEqual(routes.kind(name, "changelog"), found)

    def test_a_dependencys_subagent_gives_its_result_by_its_own_plugins_script(self):
        # Given: checker's examiner giving `done`
        # When: its command is made
        # Then: it runs the result script in checker's folder, as lane names a dependency's
        self.assertEqual(routes.command("checker:examiner", "done"), f"{helpers.EXAMINED} done")

    def test_the_orchestrator_is_told_to_start_a_dependencys_subagent_by_its_type(self):
        # Given: writer's `written`, which leads to checker's examiner
        due = decided_by(helpers.DEPENDENCY_ROUTES, [WRITER], {"w1": "written"})
        # When: lead is told the start
        # Then: it names examiner by its type, checker's
        self.assertEqual(
            routes.line(due, "changelog"), "writer gave `written`. Start `checker:examiner`."
        )

    def test_a_result_of_the_dependencys_subagent_leads_to_its_route(self):
        # Given: writer's `written`, and examiner's `asks`
        examiner = routes.Start("checker:examiner", "completed", "e1")
        # When: the next start is decided
        due = decided_by(
            helpers.DEPENDENCY_ROUTES, [WRITER, examiner], {"w1": "written", "e1": "asks"}
        )
        # Then: the run ends, as the route on `asks` starts no one
        self.assertEqual(due, routes.Next("end", "", ("checker:examiner", "asks")))

    def test_an_orchestrator_of_another_plugin_is_refused(self):
        # Given: routes whose orchestrator is checker's examiner
        given = {**helpers.DEPENDENCY_ROUTES, "orchestrator": "checker:examiner"}
        given["routes"] = [
            {"from": "checker:examiner", "to": "writer"},
            {"from": "writer", "on": "x"},
        ]
        # When: they are checked
        # Then: they are refused, as its steps lie in another plugin
        self.assertTrue(
            routes.refused(given).startswith(
                "gives checker:examiner as the orchestrator, a subagent of another plugin"
            )
        )


def decided_by(given: dict, starts: list, results: dict) -> routes.Next:
    """The next start of the routes given after the starts, as `decided` gives it."""
    return routes.next_start(given, starts, results.get, lambda a: False)


if __name__ == "__main__":
    unittest.main()
