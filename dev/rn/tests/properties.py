"""Property-based tests of rn's scripts: each behavior over a kind of input, checked on many inputs
Hypothesis makes, new on every run, CI included."""

from __future__ import annotations

import datetime
import os
import shutil
import unittest

from helpers import (
    STEERED,
    RepoTest,
    ccs,
    learnings,
    plan,
    proposal,
    said,
    steered,
    steering,
    stop,
    task,
    template,
    testing,
)

hypothesis = testing.hypothesis()
st = hypothesis.strategies
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
# Any of those but a Markdown heading, which Next cannot hold, as
# StateTest.test_a_move_the_steering_cannot_hold_stops_and_keeps_nothing has it.
SENTENCES = WORDS.filter(lambda t: not template.HEADING.fullmatch(t))
# Any of those but a fence and the line saying an item is judged on the built product, as a line of
# an item's body.
BODY = SENTENCES.filter(lambda t: not t.startswith(("```", "~~~")) and t != ccs.BUILT)
IDS = st.dictionaries(st.sampled_from(["G1", "AC1", "AC2", "AC3"]), st.text(max_size=3))


class PropertyTest(RepoTest):
    @hypothesis.given(st.text(alphabet=ALLOWED, min_size=1))
    def test_a_slug_of_lowercase_letters_digits_and_hyphens_is_taken(self, name):
        # Given: any slug of lowercase letters, digits and hyphens.
        # When: it is checked as a name.
        # Then: it is taken as it is.
        self.assertEqual(stop.named(name, "slug"), name)

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
        with self.assertRaises(stop.Stop) as stopped:
            stop.named(name, "kind")
        self.assertIn(f"the kind {name!r} is not", str(stopped.exception))

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
        self.assertEqual(ccs.has_path(path), path)

    @hypothesis.given(st.text(alphabet=ALLOWED, min_size=1))
    def test_any_path_with_nothing_there_stops(self, name):
        # Given: any path with nothing there.
        path = os.path.join("none", name)
        # When: it is checked as what the receiver has.
        # Then: rn stops, naming it.
        with self.assertRaises(stop.Stop) as stopped:
            ccs.has_path(path)
        self.assertIn(f"what the receiver has, {path}, is not there", str(stopped.exception))

    @hypothesis.given(st.text().filter(lambda t: t.strip()))
    def test_any_text_with_a_word_is_taken(self, text):
        # Given: any text holding something other than blanks.
        # When: it is checked as given.
        # Then: it is taken as it is.
        self.assertEqual(stop.given(text, "receiver"), text)

    @hypothesis.given(st.text(alphabet=" \t\n\r"))
    def test_any_text_of_blanks_stops(self, text):
        # Given: any text of blanks alone, or nothing.
        # When: it is checked as given.
        # Then: rn stops, saying it is empty.
        with self.assertRaisesRegex(stop.Stop, "the receiver is empty"):
            stop.given(text, "receiver")

    @hypothesis.given(st.lists(st.tuples(st.booleans(), st.lists(BODY, max_size=3)), max_size=5))
    def test_a_checklist_before_the_build_keeps_each_item_not_judged_on_the_built(self, made):
        # Given: a checklist of any items, each judged on the built product or not, with any lines
        # under its Scope but a heading or a fence.
        blocks = [
            [f"### B-{n}: T", "", "Scope: whole", "", *([ccs.BUILT] if built else []), *body, ""]
            for n, (built, body) in enumerate(made, 1)
        ]
        text = "\n".join(["# C", "", *(line for b in blocks for line in b)])
        # When: rn cuts it for a call before the build.
        # Then: it gives every line of the items not judged on the built product, or nothing to
        # write where none is.
        kept = [
            "# C",
            "",
            *(line for b, (built, _) in zip(blocks, made) if not built for line in b),
        ]
        want = "\n".join(kept).rstrip() + "\n" if any(built for built, _ in made) else None
        self.assertEqual(ccs.unbuilt(text), want)

    @hypothesis.given(WORDS, st.lists(WORDS, min_size=1, max_size=5))
    def test_the_steering_gives_back_its_goal_and_each_criterion_as_written(self, goal, criteria):
        # Given: a steering whose goal and criteria are any texts a line can hold.
        listed = "\n".join(f"- AC{n}: {c}" for n, c in enumerate(criteria, 1))
        text = steered(part=plan(goal=f"G1: {goal}", criteria=listed, tasks=""))
        # When: it is held to its form, and its goal and criteria are read.
        held = steering.out_of_form(text)
        # Then: it holds, and gives back each as written, by its ID.
        want = {"G1": goal, **{f"AC{n}": c for n, c in enumerate(criteria, 1)}}
        self.assertEqual((held, steering.decided(text.splitlines())), ("", want))

    @hypothesis.given(SENTENCES, st.lists(WORDS, max_size=4))
    def test_the_steering_rn_writes_holds_its_form_and_reads_back(self, next_step, opened):
        # Given: any Next a line can hold but a heading, and any points open a line can hold.
        # When: rn writes the steering with them, and reads it back.
        open_lines = [f"- {o}" for o in dict.fromkeys(opened)] or ["None."]
        written = steering.render(
            steering.parsed(STEERED)._replace(next=next_step, open=open_lines)
        )
        # Then: it holds its form, and gives them back as written.
        back = steering.parsed(written)
        self.assertEqual(
            (steering.out_of_form(written), back.next, back.open), ("", next_step, open_lines)
        )

    @hypothesis.given(IDS, IDS)
    def test_what_changed_names_each_line_shown_once(self, before, now):
        # Given: any lines of the steering shown before and any now, by their keys.
        # When: what changed is said.
        bullet = ""
        told = proposal.changes(before, now)
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

    @hypothesis.given(IDS, IDS)
    def test_what_changed_shows_each_choice_once_and_each_gone_by_its_words(self, before, now):
        # Given: any choices shown before and any now, by what was chosen.
        # When: what changed is said.
        told = proposal.choices_changed(before, now)
        # Then: each now is shown once, in order, marked where it is changed or added, then each
        # gone by what it said.
        self.assertEqual(
            told,
            [f"- {'' if before.get(t) == said else 'Changed: '}{said}" for t, said in now.items()]
            + [f"- Removed: {said}" for t, said in before.items() if t not in now],
        )

    @hypothesis.given(
        st.integers(0, 4),
        st.lists(st.tuples(st.integers(0, 99), WORDS), max_size=4),
    )
    def test_learnings_put_back_are_numbered_on_from_those_kept(self, kept, made):
        # Given: any count of learnings kept, and any learnings of a part, numbered as turn may
        # number them, each of any text a line can hold.
        before = [f"- L{n}: Kept {n}." for n in range(1, kept + 1)]
        part = [f"- L{n}: {text}" for n, text in made]
        # When: they are put back.
        # Then: those kept stay, and each of the part follows, numbered on from them, its text as
        # written.
        want = before + [f"- L{kept + k}: {text}" for k, (_, text) in enumerate(made, 1)]
        self.assertEqual(learnings.put(before, part), want)

    @hypothesis.given(
        st.text(alphabet=" x", min_size=1, max_size=5),
        st.text(alphabet=" x", min_size=1, max_size=5),
    )
    def test_the_ticks_of_a_plan_put_back_are_those_kept(self, was, made):
        # Given: a task's actions ticked as any ticks, and a part written of the same task, its
        # actions ticked as any ticks, of any count.
        # When: the part is put back.
        lines = steering.put_plan(
            plan(tasks=task(ticks=was)).splitlines(), plan(tasks=task(ticks=made)).splitlines()
        )
        # Then: each action is ticked as the one of its number was before, or not where none was.
        want = [was[k] if k < len(was) else " " for k in range(len(made))]
        actions = steering.tasks_of(lines)[0].actions
        self.assertEqual([line[steering.TICK] for _, line, _ in actions], want)

    @hypothesis.given(WORDS.filter(lambda t: ": " not in t), WORDS, WORDS)
    def test_a_choice_given_again_replaces_the_one_of_the_same_what(self, what, why, other):
        # Given: a choice of anything chosen without `: `, which parts it from why, kept, and
        # given again with any other why.
        kept, again = f"{what}: {why}", f"{what}: {other}"
        # When: the choices of the call are made.
        # Then: the one given stands alone, whole.
        self.assertEqual(ccs.chosen_with([kept], [again]), [again])


class SearchPropertyTest(RepoTest):
    def setUp(self) -> None:
        super().setUp()
        self.session()

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
        # order, each holding the words searched for.
        shutil.rmtree(self.project, ignore_errors=True)
        for n, at in enumerate(times):
            self.conversation(f"c{n}", said(f"cart {n}", at, self.top))
        # When: the orchestrator searches the session's conversations for the words.
        # Then: each comes in the order it began.
        begun = sorted(range(len(times)), key=lambda n: times[n])
        found = [f["said"] for f in self.ran("search", "cart")["found"]]
        self.assertEqual(found, [f"[user] cart {n}" for n in begun])

    @hypothesis.given(WORDS, WORDS)
    def test_any_words_said_are_found_where_they_are_said_alone(self, said_words, other):
        # Given: a conversation holding any words, and one holding any other.
        hypothesis.assume(said_words not in other)
        shutil.rmtree(self.project, ignore_errors=True)
        self.conversation("a", said(other, "2026-10-20T09:00:00Z", self.top))
        self.conversation("b", said(said_words, "2026-10-20T09:05:00Z", self.top))
        # When: the orchestrator searches for the first.
        # Then: rn finds them where they are said, and only there.
        found = self.ran("search", "--", said_words)["found"]
        self.assertEqual([f["said"] for f in found], [f"[user] {said_words}"])


class HistoryPropertyTest(RepoTest):
    # The commit the session was first kept at, which each example starts from.
    kept_at: str | None = None

    @hypothesis.given(WORDS.filter(lambda t: ": " not in t), WORDS, WORDS)
    def test_a_decision_replaced_is_given_with_what_it_was_and_is(self, title, was, now):
        # Given: a decision of any title without `: ` kept as anything it says, then replaced
        # with anything else, each by rn.py decide in a step of its own, on a session as it was
        # first kept, as one the examples before went on with would hold their history too, which
        # each example would read again.
        hypothesis.assume(was != now)
        if self.kept_at is None:
            self.session(steered(stage="design"))
            self.kept_at = self.head()
        self.git("reset", "-q", "--hard", self.kept_at)
        self.git("push", "-q", "--force")
        for says in (was, now):
            self.ran("decide", "t1.1", f"--title={title}", f"--says={says}", "--message=m")
            self.ran("state", "--message=m")
        # When: the orchestrator asks for the history.
        # Then: rn gives it replaced last, with what it was and what it is now.
        found = [(r["was"], r["now"]) for r in self.ran("history")["replaced"]]
        self.assertEqual(found[-1:], [(f"{title}: {was}", f"{title}: {now}")])


if __name__ == "__main__":
    unittest.main()
