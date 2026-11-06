"""The lanes lane lays, by their names, and the sentence of each, made from its wording with what
it takes, which the step says and the guard tells."""

import unittest
from unittest import mock

import helpers
from helpers import lanes, schema

# docs/lanes.md's table of the lanes, its action and wording, and whether each rests on the calls
# kept.
TABLE = (
    ("read_only", "read", "Read only `<input>`.", False),
    ("read_whole", "read", "Read `<input>` to its end.", True),
    ("write_only", "write", "Write only `<output>`.", False),
    ("in_form", "write", "Write `<output>` in the form of `<form>`.", False),
    ("edit_only", "write", "Once `<output>` is made, change it only with Edit.", False),
    ("run_only", "run", "Run only `<commands>`.", False),
    ("hold", "run", "Run `<commands>` only with the person's approval.", False),
    ("test_after", "test", "After changing `<output>`, pass `<test>`.", True),
    ("end_when", "end", "End only once `<output>` is made.", False),
    ("every_item", "end", "Answer every item of `<input>`.", True),
)


class TestLanes(unittest.TestCase):
    def test_the_lanes_laid_are_those_docs_lanes_md_names_in_its_order(self):
        # Given: the lanes this version lays
        # When: they are listed
        # Then: they are the table's, in its order
        self.assertEqual(list(lanes.LANES), [row[0] for row in TABLE])

    def test_each_lane_has_its_action_wording_and_calls_as_docs_lanes_md_gives_them(self):
        for lane, action, wording, rests in TABLE:
            with self.subTest(lane=lane):
                # Given: the lane's row of docs/lanes.md
                # When: its module is read
                # Then: it has the row's action and wording, and rests on the calls kept as the
                # table of its places says
                module = lanes.LANES[lane]
                self.assertEqual((module.ACTION, module.WORDING), (action, wording))
                self.assertEqual(lanes.calls(lane), rests)

    def test_the_lanes_checked_at_the_end_are_those_docs_lanes_md_names(self):
        # Given: the lanes
        # When: those checked as the subagent gives its result are read
        # Then: they are read_whole, test_after, end_when and every_item
        ending = [lane for lane, *_ in TABLE if lanes.ends(lane)]
        self.assertEqual(ending, ["read_whole", "test_after", "end_when", "every_item"])
        self.assertFalse(lanes.ends("result"))


class TestPlaces(unittest.TestCase):
    def test_a_lanes_places_are_those_its_wording_shows_in_order(self):
        for lane, places in (
            ("read_only", ["input"]),
            ("in_form", ["output", "form"]),
            ("test_after", ["output", "test"]),
            ("follow_routes", []),
            ("result", ["commands"]),
        ):
            with self.subTest(lane=lane):
                # Given: the lane
                # When: its places are read
                # Then: they are the `<...>` of its wording
                self.assertEqual(lanes.places(lane), places)

    def test_takes_fill_one_in_each_place_but_the_last_which_takes_the_rest(self):
        for lane, takes, placed in (
            ("write_only", ["a", "b"], {"output": ["a", "b"]}),
            ("test_after", ["src/", "t1", "t2"], {"output": ["src/"], "test": ["t1", "t2"]}),
            ("in_form", ["a.json"], {"output": ["a.json"], "form": []}),
            ("follow_routes", [], {}),
        ):
            with self.subTest(lane=lane, takes=takes):
                # Given: the lane's takes
                # When: they are put in its places
                # Then: the first places take one each, and the last the rest
                self.assertEqual(lanes.placed(lane, takes), placed)

    def test_takes_of_a_wording_of_three_places_fill_each_but_the_last_with_one(self):
        # Given: a sentence of three places, as a wording may show them
        wording = ("end", "Put `<first>` and `<second>` in `<rest>`.")
        with mock.patch.dict(lanes.ROUTED, {"three": wording}):
            # When: takes are put in its places
            found = lanes.placed("three", ["a", "b", "c", "d"])
        # Then: the first two take one each, and the last the rest
        self.assertEqual(found, {"first": ["a"], "second": ["b"], "rest": ["c", "d"]})

    def test_a_lanes_in_holds_no_place_the_lane_has_not(self):
        # Given: run_only given its commands and a place it has not
        given = {"takes": {"commands": ["ls"], "output": ["a.md"]}}
        # When: it is held to run_only's IN
        # Then: it is out of it at the place
        out = schema.held(lanes.given_in("run_only"), given)
        self.assertIn("$.takes", out.told() if out else "")
        # And: one given beside its takes a field it has not is out of it too
        out = schema.held(lanes.given_in("run_only"), {"takes": {"commands": ["ls"]}, "x": 1})
        self.assertIn("$:", out.told() if out else "")

    def test_a_lanes_in_asks_one_or_more_texts_in_each_place_and_the_calls_where_it_rests_on_them(
        self,
    ):
        # Given: test_after's IN, and run_only's
        after, run = lanes.given_in("test_after"), lanes.given_in("run_only")
        # When: they are read
        # Then: each asks its places, each one or more texts, and test_after the calls kept
        self.assertEqual(after["required"], ["takes", "calls"])
        self.assertEqual(run["required"], ["takes"])
        self.assertEqual(after["properties"]["takes"]["required"], ["output", "test"])
        self.assertEqual(run["properties"]["takes"]["properties"]["commands"]["minItems"], 1)


class TestSentence(unittest.TestCase):
    def test_one_thing_taken_is_put_in_its_quotes(self):
        # Given: run_only taking one command
        # When: its sentence is made
        # Then: the command is in quotes in its place
        self.assertEqual(
            lanes.sentence("run_only", ["git log --oneline"]), "Run only `git log --oneline`."
        )

    def test_things_taken_are_listed_with_commas_and_or_before_the_last(self):
        for takes, said in (
            (["a.md", "b.md"], "Write only `a.md` or `b.md`."),
            (["a.md", "b.md", "c/"], "Write only `a.md`, `b.md` or `c/`."),
        ):
            with self.subTest(takes=takes):
                # Given: write_only taking two or three outputs
                # When: its sentence is made
                # Then: each is quoted, listed with commas and or before the last
                self.assertEqual(lanes.sentence("write_only", takes), said)

    def test_the_sentences_of_the_routes_are_made_as_docs_routes_md_writes_them(self):
        for lane, takes, said in (
            ("follow_routes", [], helpers.FOLLOW),
            ("result", [f"{helpers.GIVE} writer written"], helpers.END_WRITER),
            (
                "result",
                [f"{helpers.GIVE} reviewer more", f"{helpers.GIVE} reviewer good"],
                helpers.END_REVIEWER,
            ),
        ):
            with self.subTest(lane=lane, takes=takes):
                # Given: the skill's step, or a subagent's last step with its commands
                # When: the sentence laid there is made
                # Then: it reads as docs/routes.md writes it
                self.assertEqual(lanes.sentence(lane, takes), said)

    def test_the_result_sentence_says_its_command_is_no_part_of_the_work(self):
        # Given: a subagent's last step with its result command, as a subagent told to run none of
        # the work's scripts reads it
        # When: the sentence laid there is made
        # Then: it says the command gives the result to the plugin and is no part of the work
        self.assertEqual(
            lanes.sentence("result", ["give"]),
            "End by running `give`. That command gives your result to the plugin and is no part of"
            " the work, so an instruction not to run the work's scripts does not cover it.",
        )

    def test_the_result_sentence_is_given_in_each_wording_lane_laid_before(self):
        # Given: a subagent's last step with its result command
        # When: the sentence laid there is made in the wordings lane laid before
        # Then: it is the one wording before the current, which said no more than the commands
        self.assertEqual(lanes.earlier("result", ["give"]), ["End by running `give`."])

    def test_a_sentence_whose_wording_never_changed_has_none_laid_before(self):
        for lane, takes in (("run_only", ["git log"]), ("follow_routes", [])):
            with self.subTest(lane=lane):
                # Given: a lane, or a sentence laid from the routes, whose wording lane never
                # changed
                # When: its sentence is made in the wordings laid before
                # Then: there is none
                self.assertEqual(lanes.earlier(lane, takes), [])

    def test_the_sentences_of_the_routes_have_their_actions_and_follow_routes_hook(self):
        for lane, action in (("follow_routes", "follow"), ("result", "end")):
            with self.subTest(lane=lane):
                # Given: a sentence laid from the routes
                # When: its action and hook are read
                # Then: they are its own action, and follow_routes, which lays and checks it
                self.assertEqual((lanes.action(lane), lanes.kind(lane)), (action, "follow_routes"))
        # And: a lane's own are its module's and its name
        self.assertEqual((lanes.action("run_only"), lanes.kind("run_only")), ("run", "run_only"))

    def test_each_place_takes_its_own_things(self):
        for lane, takes, said in (
            (
                "in_form",
                ["entry.json", "${CLAUDE_PLUGIN_ROOT}/forms/entry.json"],
                "Write `entry.json` in the form of `${CLAUDE_PLUGIN_ROOT}/forms/entry.json`.",
            ),
            ("test_after", ["src/", "t1", "t2"], "After changing `src/`, pass `t1` or `t2`."),
            ("in_form", ["entry.json"], "Write `entry.json` in the form of ."),
        ):
            with self.subTest(lane=lane, takes=takes):
                # Given: a lane of two places, with a thing for each, more for the last, or
                # none for the last
                # When: its sentence is made
                # Then: each place is filled with its own things, or left empty
                self.assertEqual(lanes.sentence(lane, takes), said)

    def test_a_take_is_put_in_as_it_is_written(self):
        # Given: a command holding a backslash and a comma
        take = r"grep -c '\d,' notes.md"
        # When: run_only's sentence is made
        # Then: the command is put in word for word
        self.assertEqual(lanes.sentence("run_only", [take]), f"Run only `{take}`.")


class TestRefused(helpers.PluginTest):
    """The checks of a lane's takes that `lay.py print` makes and the guard makes again on the lanes
    laid, kept in lanes/ alone (dev/lane/architecture.md, What each role alone decides)."""

    def test_takes_lay_py_lays_are_refused_by_nothing(self):
        for kind, takes in (
            ("run_only", ["git log --oneline"]),
            ("run_only", ["python3 check.py {file}"]),
            ("write_only", ["{work}"]),
            ("in_form", ["notes.json", "{form}"]),
        ):
            with self.subTest(kind=kind, takes=takes):
                # Given: the lane, taking things lay.py lays
                # When: its takes are checked
                # Then: nothing refuses them
                self.assertEqual(lanes.refused(kind, takes, self.plugin), lanes.Refused(""))

    def test_takes_that_cannot_be_laid_are_refused_saying_why(self):
        for kind, takes, said in (
            ("run_only", [], "with no take"),
            ("run_only", ["git log", ""], "with a take that is empty"),
            ("in_form", ["notes.json"], "takes out of its places at $.form: expected at least 1"),
            (
                "write_only",
                ["${dependency:checker}/x"],
                "`${dependency:checker}`, which only a command",
            ),
            ("read_only", ["notes/{name}.md"], "`{name}` in a take, which only a command"),
            ("in_form", ["notes.json", "forms/none.json"], ", which names the form"),
        ):
            with self.subTest(kind=kind, takes=takes):
                # Given: the lane, taking things lay.py cannot lay
                # When: its takes are checked
                found = lanes.refused(kind, takes, self.plugin)
                # Then: they are refused, saying why, as the proposal's error goes on
                self.assertTrue(found.said.startswith(said), found.said)
                self.assertFalse(found.declare)

    def test_a_dependency_the_manifest_does_not_declare_is_refused_to_be_declared(self):
        # Given: run_only naming the folder of checker, which changelog's manifest does not declare
        # When: its takes are checked
        found = lanes.refused("run_only", ["python3 ${dependency:checker}/x.py"], self.plugin)
        # Then: it is refused, the fix being to declare it
        self.assertEqual(
            found,
            lanes.Refused(
                "`${dependency:checker}`, which .claude-plugin/plugin.json does not declare among"
                " its dependencies",
                True,
            ),
        )


if __name__ == "__main__":
    unittest.main()
