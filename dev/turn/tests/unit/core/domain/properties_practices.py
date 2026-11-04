"""Properties of practices.py over many best practices and pages: a best practice whose questions
ask of every part and the whole, each met by one practice in order, shows no fault of its form, and
a part no question asks of is named; the groups hold each question once, join exactly the questions
that ask of a part in common or of the whole, and come in the order of their first question; and a
page reads as the same words whatever inline tags, blocks, spaces, quotes and case it writes them
with."""

import unittest

import helpers
from helpers import practices

hypothesis = helpers.testing.hypothesis()
given, st = hypothesis.given, hypothesis.strategies

PARTS = ["a", "b", "c", "d", "e"]


@st.composite
def sound(draw) -> dict:
    """A best practice in form: parts p1 on, some made of parts, each part that holds none asked of
    by a question, one question about the whole, a practice for each question in order, and each
    ground whole with an https link."""
    parts, leaves = [], []
    for _ in range(draw(st.integers(0, 4))):
        made: dict = {"id": f"p{len(leaves) + len(parts) + 1}", "what": "w"}
        inner = [{"id": f"{made['id']}-{n}", "what": "w"} for n in range(draw(st.integers(0, 2)))]
        if inner:
            made["parts"] = inner
        parts.append(made)
        leaves += [i["id"] for i in inner] or [made["id"]]
    abouts = [[practices.WHOLE]] + [[] for _ in range(draw(st.integers(0, 3)))]
    for leaf in leaves:
        abouts[draw(st.integers(0, len(abouts) - 1))].append(leaf)
    abouts = [a for a in abouts if a]
    draw(st.randoms()).shuffle(abouts)
    ground = {"title": "t", "url": "https://example.com", "by": "b", "quote": "q"}
    return {
        "goal": "g",
        "parts": parts,
        "benefits": [
            {"id": f"Q{n}", "about": ", ".join(a), "what": "w"} for n, a in enumerate(abouts, 1)
        ],
        "practices": [
            {"benefit": f"Q{n}", "thinking": "t", "steps": [], "grounds": [ground]}
            for n in range(1, len(abouts) + 1)
        ],
    }


@st.composite
def asked(draw) -> dict:
    """A best practice's questions, each about one to three of five parts, or about the whole beside
    them."""
    abouts = draw(
        st.lists(
            st.lists(
                st.sampled_from([*PARTS, practices.WHOLE]), min_size=1, max_size=3, unique=True
            ),
            min_size=1,
            max_size=8,
        )
    )
    return {"benefits": [{"id": f"Q{n}", "about": ", ".join(a)} for n, a in enumerate(abouts, 1)]}


def shared(a: set, b: set) -> bool:
    """Whether two questions' abouts ask of the same: both of the whole, or neither and a part in
    common."""
    if practices.WHOLE in a or practices.WHOLE in b:
        return practices.WHOLE in a and practices.WHOLE in b
    return bool(a & b)


class TestFaults(unittest.TestCase):
    @given(sound())
    def test_a_best_practice_asking_of_each_part_and_the_whole_has_no_fault(self, data):
        self.assertEqual(practices.faults(data), [])

    @given(sound())
    def test_a_part_no_question_asks_of_is_named(self, data):
        data["parts"].append({"id": "lone", "what": "w"})
        self.assertEqual(practices.faults(data), ["part lone has no question about it"])


class TestGroups(unittest.TestCase):
    @given(asked())
    def test_the_groups_join_exactly_the_questions_that_ask_of_the_same(self, data):
        found = practices.groups(data, "k")
        where = {q: n for n, g in enumerate(found) for q in g["questions"]}
        names = [f"k/{q['id']}" for q in data["benefits"]]
        # Each question lies in one group, and the groups are G1 on.
        self.assertEqual(sorted(q for g in found for q in g["questions"]), sorted(names))
        self.assertEqual([g["id"] for g in found], [f"G{n}" for n in range(1, len(found) + 1)])
        abouts = {
            f"k/{q['id']}": {a.strip() for a in q["about"].split(",")} for q in data["benefits"]
        }
        for q in names:
            for r in names:
                if shared(abouts[q], abouts[r]):
                    self.assertEqual(where[q], where[r])
        # Each group is joined through questions that ask of the same, so none holds two apart.
        for g in found:
            reached, waiting = set(), [g["questions"][0]]
            while waiting:
                at = waiting.pop()
                reached.add(at)
                waiting += [
                    r for r in g["questions"] if r not in reached and shared(abouts[at], abouts[r])
                ]
            self.assertEqual(reached, set(g["questions"]))

    @given(asked())
    def test_the_groups_come_in_the_order_of_their_first_question(self, data):
        found = practices.groups(data, "k")
        numbers = [[practices.number(q.split("/")[1]) for q in g["questions"]] for g in found]
        for n in numbers:
            self.assertEqual(n, sorted(n))
        self.assertEqual([n[0] for n in numbers], sorted(n[0] for n in numbers))


# What may stand between two words, and inside one, without changing how a page reads.
BETWEEN = st.sampled_from(
    [" ", "  ", "\n", "\t ", "<p>", "</div>", "<br>", "<li>", "<style>x</style>"]
)
INSIDE = st.sampled_from(["", "", "<em>", "</em>", '<a href="x">', "</a>", "<span>", "</code>"])
WORDS = st.lists(st.text("abcXYZ'\"-", min_size=1, max_size=6), min_size=1, max_size=6)
# Marks a page may write for the plain ones.
MARKS = {"'": "’", '"': "“", "-": "—"}


class TestPlain(unittest.TestCase):
    @given(WORDS, st.data())
    def test_a_page_reads_as_its_words_however_it_writes_them(self, words, data):
        written = []
        for word in words:
            chars = [
                data.draw(st.sampled_from([c, c.swapcase(), MARKS.get(c, c)])) + data.draw(INSIDE)
                for c in word
            ]
            written.append(data.draw(INSIDE) + "".join(chars))
        page = "".join(w + data.draw(BETWEEN) for w in written)
        self.assertEqual(practices.plain(page), practices.plain(" ".join(words)))


if __name__ == "__main__":
    unittest.main()
