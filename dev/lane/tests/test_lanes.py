"""Each lane's wording, held to lane's docs/lanes.md, and the sentence made from it with what the lane
takes, the one the step says and the subagent is told."""

import json
import os
import re
import types
import unittest
from unittest import mock

import helpers
from helpers import lanes

# A row of the lanes' table: its action, its lane, its sentence and when its hook tells it.
ROW = re.compile(r"^\| (?P<action>[a-z ]+) \| (?P<lane>[a-z_]+) \| (?P<sentence>.+?) \| .+ \|$")


def readme_rows() -> dict:
    """Each lane of the lanes' table, by its name: its action and its sentence."""
    with open(os.path.join(helpers.LANE, "docs", "lanes.md"), encoding="utf-8") as f:
        found = [ROW.match(line) for line in f.read().splitlines()]
    return {m["lane"]: (m["action"], m["sentence"]) for m in found if m}


class TestWording(unittest.TestCase):
    def test_each_lane_has_the_action_and_wording_of_its_row_in_the_readme(self):
        # Given: the lanes' table
        rows = readme_rows()
        for name, lane in lanes.LANES.items():
            with self.subTest(lane=name):
                # When: the lane in lanes/ is read
                # Then: its action and its wording are those of its row
                self.assertEqual((lane.ACTION, lane.WORDING), rows[name])


class TestSentence(unittest.TestCase):
    def test_one_thing_taken_is_put_in_its_quotes(self):
        # Given: hands_off taking one command
        # When: its sentence is made
        # Then: the command stands where the wording shows `<commands>`
        self.assertEqual(lanes.sentence("hands_off", ["git push"]), "Do not run `git push`.")

    def test_two_things_taken_are_joined_by_or(self):
        # Given: hands_off taking two commands
        # When: its sentence is made
        # Then: each is in quotes of its own, joined by `or`, as the README's example reads
        self.assertEqual(lanes.sentence("hands_off", ["git commit", "git push"]), helpers.SENTENCE)

    def test_three_things_taken_are_listed_with_or_before_the_last(self):
        # Given: hands_off taking three commands
        # When: its sentence is made
        # Then: they are listed with commas, `or` before the last
        self.assertEqual(
            lanes.sentence("hands_off", ["a", "b", "c"]), "Do not run `a`, `b` or `c`."
        )

    def test_a_wording_showing_two_things_puts_in_each_taken_in_turn(self):
        # Given: in_form taking an output and its form
        # When: its sentence is made
        # Then: each stands in its own place, in the order taken
        self.assertEqual(
            lanes.sentence("in_form", ["out.json", "${CLAUDE_PLUGIN_ROOT}/forms/out.json"]),
            "Write `out.json` in the form of `${CLAUDE_PLUGIN_ROOT}/forms/out.json`.",
        )

    def test_a_lane_holding_more_than_it_shows_shows_the_first_alone(self):
        # Given: wait_for taking the approval and the commands it holds back
        # When: its sentence is made
        # Then: the approval alone stands where the wording shows `<approval>`
        self.assertEqual(
            lanes.sentence("wait_for", ["OK", "lay.py write", "git push"]),
            "Do not go on until `OK`.",
        )

    def test_how_many_things_a_lane_shows(self):
        # Given: wait_for, which shows the approval alone, and hands_off, which shows all
        # When: how many it shows is read
        # Then: it is one for wait_for, all for hands_off
        self.assertEqual((lanes.shown("wait_for"), lanes.shown("hands_off")), (1, None))


class TestTakes(unittest.TestCase):
    def test_a_lane_showing_one_thing_takes_one_or_more(self):
        for takes, fits in (([], False), (["a"], True), (["a", "b"], True)):
            with self.subTest(takes=takes):
                # Given: hands_off, whose wording shows one thing
                # When: it is given so many things
                # Then: it takes one or more
                self.assertEqual(lanes.fits("hands_off", takes), fits)

    def test_a_lane_showing_two_things_takes_two_alone(self):
        for takes, fits in ((["a"], False), (["a", "b"], True), (["a", "b", "c"], False)):
            with self.subTest(takes=takes):
                # Given: in_form, whose wording shows an output and a form
                # When: it is given so many things
                # Then: it takes two alone, one for each
                self.assertEqual(lanes.fits("in_form", takes), fits)

    def test_a_lane_showing_two_things_takes_one_for_each_the_last_taking_the_rest(self):
        for takes, fits in ((["a"], False), (["a", "b"], True), (["a", "b", "c"], True)):
            with self.subTest(takes=takes):
                # Given: test_after, whose wording shows an output and a test, and names no most
                # When: it is given so many things
                # Then: it takes one for each place or more
                self.assertEqual(lanes.fits("test_after", takes), fits)

    def test_a_lane_holding_more_than_it_shows_takes_one_or_more_after_those(self):
        for takes, fits in ((["OK"], False), (["OK", "a"], True), (["OK", "a", "b"], True)):
            with self.subTest(takes=takes):
                # Given: wait_for, whose sentence shows the approval alone
                # When: it is given so many things
                # Then: it takes the approval and one or more commands its hook holds back
                self.assertEqual(lanes.fits("wait_for", takes), fits)

    def test_a_lane_showing_two_of_one_place_takes_one_or_more_after_them(self):
        # Given: a lane of one place whose sentence shows the first two things it takes
        two = types.SimpleNamespace(WORDING="Put `<a>`.", SHOWN=2)
        for takes, fits in ((["a", "b"], False), (["a", "b", "c"], True)):
            with self.subTest(takes=takes), mock.patch.dict(lanes.LANES, {"two": two}):
                # When: it is given so many things
                # Then: it takes the two it shows and one or more after them
                self.assertEqual(lanes.fits("two", takes), fits)

    def test_a_lane_naming_a_most_takes_no_more(self):
        # Given: a lane of one place that names the most things it takes, three
        three = types.SimpleNamespace(WORDING="Put `<a>`.", MOST=3)
        for takes, fits in ((["a", "b"], True), (["a", "b", "c"], True), (["a"] * 4, False)):
            with self.subTest(takes=takes), mock.patch.dict(lanes.LANES, {"three": three}):
                # When: it is given so many things
                # Then: it takes one or more, up to three
                self.assertEqual(lanes.fits("three", takes), fits)


class TestSlots(unittest.TestCase):
    def test_each_place_takes_one_thing_in_order(self):
        # Given: test_after, whose wording shows two places, taking an output and a test
        # When: its sentence is made
        # Then: the output stands in the first place and the test in the second
        self.assertEqual(
            lanes.sentence("test_after", ["app.py", "make test"]),
            "After changing `app.py`, pass `make test`.",
        )

    def test_the_last_place_takes_the_rest_as_a_list(self):
        # Given: test_after taking an output and three tests
        # When: its sentence is made
        # Then: the tests are listed in the last place, `or` before the last
        self.assertEqual(
            lanes.sentence("test_after", ["app.py", "a", "b", "c"]),
            "After changing `app.py`, pass `a`, `b` or `c`.",
        )

    def test_every_place_but_the_last_takes_one_thing(self):
        # Given: a lane whose wording shows three places, taking four things
        three = types.SimpleNamespace(WORDING="Put `<a>` into `<b>` by `<c>`.")
        with mock.patch.dict(lanes.LANES, {"three": three}):
            # When: its sentence is made
            said = lanes.sentence("three", ["w", "x", "y", "z"])
        # Then: the first two places take one thing each, and the last the rest
        self.assertEqual(said, "Put `w` into `x` by `y` or `z`.")

    def test_a_lane_counts_the_places_its_wording_shows(self):
        # Given: a lane of one place and one of two
        # When: its places are counted
        # Then: each has as many as its wording shows
        self.assertEqual((lanes.slots("hands_off"), lanes.slots("test_after")), (1, 2))


class TestHeldOn(unittest.TestCase):
    def test_a_lane_is_held_on_the_events_its_module_names_or_on_a_tool_call(self):
        # Given: the lanes lane lays
        # When: the events each is held on are read
        # Then: those on how the subagent ends are held on SubagentStop, as_printed, whose hand-on
        # may be the last reply, on both, every other on PreToolUse alone
        held = {
            "test_after": ("SubagentStop",),
            "end_when": ("SubagentStop",),
            "every_item": ("SubagentStop",),
            "as_printed": ("PreToolUse", "SubagentStop"),
        }
        for name in lanes.LANES:
            with self.subTest(lane=name):
                self.assertEqual(lanes.held_on(name), held.get(name, ("PreToolUse",)))


class TestAlone(unittest.TestCase):
    def test_the_things_standing_each_alone_in_a_place_are_counted(self):
        # Given: lanes of one place, of two, and wait_for, which shows its approval alone
        # When: the things each takes that stand alone in a place are counted
        # Then: they are those before the last place, and the approval of wait_for
        found = {n: lanes.alone(n) for n in ("hands_off", "in_form", "test_after", "wait_for")}
        self.assertEqual(found, {"hands_off": 0, "in_form": 1, "test_after": 1, "wait_for": 1})

    def test_a_lane_of_three_places_has_two_things_standing_alone(self):
        # Given: a lane whose wording shows three places
        three = types.SimpleNamespace(WORDING="Put `<a>` into `<b>` by `<c>`.")
        with mock.patch.dict(lanes.LANES, {"three": three}):
            # When: the things it takes that stand alone in a place are counted
            # Then: they are the two before its last place
            self.assertEqual(lanes.alone("three"), 2)


class TestTaken(helpers.PluginTest):
    # A hook's command laying start_with on step 1 and hands_off on step 3 of the subagent.
    COMMAND = (
        'exec python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lane/pretooluse.py" notes:changelog-writer'
        " '1:start_with:python3 scripts/given.py' 3:hands_off:git"
    )

    def taken(self, hooks, lane="start_with"):
        """What each lane of the kind takes in changelog-writer, read from the hooks written."""
        if hooks is not None:
            self.write(os.path.join(self.plugin, "hooks", "hooks.json"), hooks)
        return lanes.taken(self.plugin, helpers.AGENT, lane)

    def entry(self, command):
        return {"matcher": ".*", "hooks": [{"type": "command", "command": command}]}

    def test_what_each_lane_of_the_kind_takes_in_the_subagent_is_read_from_its_hooks(self):
        # Given: the subagent's hook laying start_with and hands_off, beside the hooks of
        # other subagents, and one lane does not read
        others = [self.COMMAND.replace("changelog-writer", n) for n in ("a", "z")]
        wrong = self.COMMAND.replace("3:hands_off:git", "3:no_lane:git")
        entries = [self.entry(c) for c in (*others, wrong, self.COMMAND)]
        hooks = json.dumps({"hooks": {"PreToolUse": entries}})
        for lane, takes in (
            ("start_with", [["python3 scripts/given.py"]]),
            ("hands_off", [["git"]]),
        ):
            with self.subTest(lane=lane):
                # When: what its lanes of the kind take is read
                # Then: it is what its lane of the kind takes in the hook lane reads, once
                self.assertEqual(self.taken(hooks, lane), takes)

    def test_hooks_not_there_or_not_json_give_none(self):
        for hooks in (None, "{", "[]"):
            with self.subTest(hooks=hooks):
                # Given: no hooks.json, one not JSON, or one holding no hook
                # When: what start_with takes is read
                # Then: there is nothing
                self.assertEqual(self.taken(hooks), [])


class TestHookWords(unittest.TestCase):
    COMMAND = (
        'check || exit 2; exec python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lane/pretooluse.py"'
        " notes:changelog-writer '3:hands_off:git commit,git push'"
    )

    def test_the_words_a_hooks_command_gives_its_event_script_are_read(self):
        # Given: a hook's command as lane:up writes it
        # When: its words for PreToolUse are read
        # Then: they are the subagent, then each lane laid
        self.assertEqual(
            lanes.hook_words(self.COMMAND, "PreToolUse"),
            ["notes:changelog-writer", "3:hands_off:git commit,git push"],
        )

    def test_a_command_of_another_event_no_subagent_or_unread_words_gives_none(self):
        for command, event in (
            (self.COMMAND, "SubagentStop"),
            (self.COMMAND.replace("notes:changelog-writer", "writer"), "PreToolUse"),
            (self.COMMAND + " 'open", "PreToolUse"),
            (None, "PreToolUse"),
        ):
            with self.subTest(command=command, event=event):
                # Given: a command running another event's script, naming no subagent as
                # <plugin>:<name>, giving words the shell cannot read, or none at all
                # When: its words are read
                # Then: there are none
                self.assertEqual(lanes.hook_words(command, event), [])


class TestWords(unittest.TestCase):
    def test_a_lane_is_written_as_its_step_its_name_and_what_it_takes(self):
        # Given: hands_off on step 3 taking two commands
        # When: it is written for the hook's command
        # Then: it reads `<step>:<lane>:<what it takes>`, the things taken joined by commas
        self.assertEqual(
            lanes.word(3, "hands_off", ["git commit", "git push"]),
            "3:hands_off:git commit,git push",
        )


if __name__ == "__main__":
    unittest.main()
