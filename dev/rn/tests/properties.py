"""Property-based tests of rn's scripts: each behavior over a kind of input, checked on many inputs
Hypothesis makes, new on every run, CI included."""

import datetime
import os
import shutil
import unittest

# Hypothesis is installed on the newest Python alone, so the type check on 3.9 finds it missing.
try:
    import hypothesis  # pyrefly: ignore[missing-import]
    from hypothesis import strategies as st  # pyrefly: ignore[missing-import]
except ImportError:
    raise unittest.SkipTest("Hypothesis runs on the newest Python alone") from None

from helpers import testing
from test_rn import STEERED, LearningTest, RepoTest, plan, rn, said, steering, template

testing.load_hypothesis_profile()
ALLOWED = "abcdefghijklmnopqrstuvwxyz0123456789-"
# Any text a line of the steering can hold after an ID: no line break `splitlines` splits at,
# no lone surrogate, which a UTF-8 file cannot hold, and no blank at either end, which a line
# does not keep; some text, as an ID's line is not empty.
WORDS = st.text(
    st.characters(
        blacklist_categories=("Cs",),
        blacklist_characters="\n\r\x0b\x0c\x1c\x1d\x1e\x85  ",
    ),
    min_size=1,
).filter(lambda t: t.strip() == t and t)
# Any of those but a Markdown heading, which Next cannot hold, as an unit test has it.
SENTENCES = WORDS.filter(lambda t: not template.HEADING.fullmatch(t))
IDS = st.dictionaries(st.sampled_from(["G1", "AC1", "AC2", "AC3"]), st.text(max_size=3))


class PropertyTest(RepoTest):
    @hypothesis.given(st.text(alphabet=ALLOWED, min_size=1))
    def test_a_slug_of_lowercase_letters_digits_and_hyphens_is_taken(self, name):
        # Given: any slug of lowercase letters, digits and hyphens.
        # When: it is checked as a name.
        # Then: it is taken as it is.
        self.assertEqual(rn.named(name, "slug"), name)

    @hypothesis.given(
        st.tuples(
            st.text(alphabet=ALLOWED),
            st.characters().filter(lambda c: c not in ALLOWED),
            st.text(alphabet=ALLOWED),
        )
    )
    def test_a_name_with_any_other_character_stops(self, parts):
        # Given: any name holding a character other than lowercase letters, digits and hyphens.
        name = "".join(parts)
        # When: it is checked as a name.
        # Then: rn stops, naming it.
        with self.assertRaises(rn.Stop) as stop:
            rn.named(name, "kind")
        self.assertIn(f"the kind {name!r} is not", str(stop.exception))

    @hypothesis.given(st.text(alphabet=ALLOWED, min_size=1), st.booleans())
    def test_any_path_with_a_file_or_folder_there_is_taken(self, name, folder):
        # Given: a file, or a folder, at any path.
        path = os.path.join("held", "folder" if folder else "file", name)
        if folder:
            os.makedirs(path, exist_ok=True)
        else:
            self.write(path, "")
        # When: it is checked as what the receiver has.
        # Then: it is taken as it is.
        self.assertEqual(rn.held(path), path)

    @hypothesis.given(st.text(alphabet=ALLOWED, min_size=1))
    def test_any_path_with_nothing_there_stops(self, name):
        # Given: any path with nothing there.
        path = os.path.join("none", name)
        # When: it is checked as what the receiver has.
        # Then: rn stops, naming it.
        with self.assertRaises(rn.Stop) as stop:
            rn.held(path)
        self.assertIn(f"what the receiver has, {path}, is not there", str(stop.exception))

    @hypothesis.given(st.text().filter(lambda t: t.strip()))
    def test_any_text_with_a_word_is_taken(self, text):
        # Given: any text holding something other than blanks.
        # When: it is checked as given.
        # Then: it is taken as it is.
        self.assertEqual(rn.given(text, "receiver"), text)

    @hypothesis.given(st.text(alphabet=" \t\n\r"))
    def test_any_text_of_blanks_stops(self, text):
        # Given: any text of blanks alone, or nothing.
        # When: it is checked as given.
        # Then: rn stops, saying it is empty.
        with self.assertRaisesRegex(rn.Stop, "the receiver is empty"):
            rn.given(text, "receiver")

    @hypothesis.given(WORDS, st.lists(WORDS, min_size=1, max_size=5))
    def test_the_steering_gives_back_its_goal_and_each_criterion_as_written(self, goal, criteria):
        # Given: a steering whose goal and criteria are any texts a line can hold.
        listed = "\n".join(f"- AC{n}: {c}" for n, c in enumerate(criteria, 1))
        text = steering(part=plan(goal=f"G1: {goal}", criteria=listed, tasks=""))
        # When: it is held to its form, and its goal and criteria are read.
        held = rn.out_of_form(text)
        # Then: it holds, and gives back each as written, by its ID.
        want = {"G1": goal, **{f"AC{n}": c for n, c in enumerate(criteria, 1)}}
        self.assertEqual((held, rn.decided(text.splitlines(), ("", rn.CRITERIA))), ("", want))

    @hypothesis.given(SENTENCES, st.lists(WORDS, max_size=4))
    def test_the_steering_rn_writes_holds_its_form_and_reads_back(self, next_step, opened):
        # Given: any Next a line can hold but a heading, and any points open a line can hold.
        # When: rn writes the steering with them, and reads it back.
        open_lines = [f"- {o}" for o in dict.fromkeys(opened)] or ["None."]
        written = rn.render(rn.parsed(STEERED)._replace(next=next_step, open=open_lines))
        # Then: it holds its form, and gives them back as written.
        back = rn.parsed(written)
        self.assertEqual(
            (rn.out_of_form(written), back.next, back.open), ("", next_step, open_lines)
        )

    @hypothesis.given(IDS, IDS, st.sampled_from(["", "- "]))
    def test_what_changed_names_each_line_shown_once(self, before, now, bullet):
        # Given: any lines shown before and any now, by their keys, under a bullet or none.
        # When: what changed is said.
        told = rn.changes(before, now, bullet)
        # Then: each now is shown once as changed or named once among those as before, the last
        # line, and each gone named as removed, each change under the bullet.
        changed = [line[len(f"{bullet}Changed: ") :] for line in told if "Changed: " in line]
        same = [i for i in now if before.get(i) == now[i]]
        removed = [line[len(f"{bullet}Removed: ") :] for line in told if "Removed: " in line]
        last = told[-1] if same else ""
        words = last.removeprefix("(").removesuffix(" as before)").replace(" and ", ", ")
        self.assertEqual(
            (sorted(changed), removed, words.split(", ") if same else []),
            (
                sorted(now[i] for i in now if i not in same),
                [i for i in before if i not in now],
                same,
            ),
        )


class LearningPropertyTest(LearningTest):
    @hypothesis.given(
        st.lists(
            st.datetimes(datetime.datetime(2000, 1, 1), datetime.datetime(2099, 12, 31)).map(
                lambda t: f"{t:%Y-%m-%dT%H:%M:%S}.{t.microsecond // 1000:03d}Z"
            ),
            min_size=1,
            max_size=4,
            unique=True,
        )
    )
    def test_conversations_come_in_the_order_they_began(self, times):
        # Given: conversations begun at any times, as Claude Code writes them, named in another
        # order.
        shutil.rmtree(self.project, ignore_errors=True)
        for n, at in enumerate(times):
            self.conversation(f"c{n}", said(str(n), at, self.top))
        # When: the orchestrator has the records shown.
        # Then: each comes in the order it began.
        begun = sorted(range(len(times)), key=lambda n: times[n])
        self.assertEqual(self.shown(), [f"[user] {n}\n" for n in begun])


if __name__ == "__main__":
    unittest.main()
