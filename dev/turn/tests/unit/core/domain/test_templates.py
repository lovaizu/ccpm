"""How practices.py checks a best practice's form and makes the Markdown a person reads: the check
names each fault and each Markdown not as its JSON makes it, write puts the Markdown beside the
JSON, and sources names each ground whose page is not the one meant."""

import copy
import email.message
import http.client
import io
import unittest
import urllib.error
import urllib.request
from typing import Any
from unittest import mock

from helpers import templates as practices

G = {"title": "T", "url": "https://x.example/t", "by": "X, 2020", "quote": "y"}
DATA = {
    "goal": "The reader gets it.",
    "parts": [{"id": "a", "what": "A.", "parts": [{"id": "b", "what": "B."}]}],
    "benefits": [
        {"id": "Q1", "about": "a", "what": "Does it?"},
        {"id": "Q2", "about": "b, the whole", "what": "After Q1, does all?"},
    ],
    "practices": [
        {"benefit": "Q1", "thinking": "Think.", "steps": ["Do."], "grounds": [G]},
        {"benefit": "Q2", "thinking": "Then.", "steps": [], "grounds": []},
    ],
}


def changed(change):
    data = copy.deepcopy(DATA)
    change(data)
    return practices.faults(data)


class Faults(unittest.TestCase):
    def test_a_sound_best_practice_has_none(self):
        self.assertEqual(practices.faults(DATA), [])

    def test_questions_out_of_number_order(self):
        def swap(d):
            d["benefits"].reverse()
            d["practices"].reverse()

        self.assertIn("questions are Q2, Q1, not numbered in order from Q1", changed(swap))

    def test_practices_not_in_the_questions_order(self):
        def swap(d):
            d["practices"].reverse()

        expected = "practices meet Q2, Q1, not each question once in its order"
        self.assertEqual(changed(swap), [expected])

    def test_a_question_with_no_method(self):
        def drop(d):
            d["practices"].pop()

        self.assertEqual(changed(drop), ["practices meet Q1, not each question once in its order"])

    def test_about_a_part_that_is_not_there(self):
        def wrong(d):
            d["benefits"][0]["about"] = "c"

        self.assertEqual(changed(wrong), ["Q1 is about c, which is no part"])

    def test_a_part_named_twice(self):
        def twice(d):
            d["parts"].append({"id": "a", "what": "Again."})

        self.assertEqual(changed(twice), ["part a is named more than once"])

    def test_a_ground_missing_a_field_or_with_no_https_link(self):
        def missing(d):
            d["practices"][0]["grounds"] = [dict(G, title=""), dict(G, url="x.example")]

        self.assertEqual(
            changed(missing),
            ["Q1 ground 1 has no title", "Q1 ground 2 links no https page"],
        )

    def test_a_question_named_in_the_text_that_is_not_there(self):
        def name(d):
            d["practices"][1]["thinking"] = "As Q3 says."

        self.assertEqual(changed(name), ["Q3 is named, but there is no such question"])

    def test_a_ground_naming_a_question_is_its_source_s_words(self):
        def quote(d):
            d["practices"][0]["grounds"] = [dict(G, quote="see Q9")]

        self.assertEqual(changed(quote), [])

    def test_a_part_no_question_is_about(self):
        def add(d):
            d["parts"].append({"id": "c", "what": "C."})

        self.assertEqual(changed(add), ["part c has no question about it"])

    def test_no_question_about_the_whole(self):
        def narrow(d):
            d["benefits"][1]["about"] = "b"

        self.assertEqual(changed(narrow), ["no question is about the whole"])

    def test_a_best_practice_of_one_question_about_the_whole(self):
        data = {
            "goal": "G.",
            "benefits": [{"id": "Q1", "about": "the whole", "what": "Does it?"}],
            "practices": [{"benefit": "Q1", "thinking": "T.", "steps": [], "grounds": []}],
        }
        self.assertEqual(practices.faults(data), [])

    def test_two_questions_of_one_number(self):
        def same(d):
            d["benefits"][1]["id"] = "Q1"
            d["practices"][1]["benefit"] = "Q1"

        self.assertIn("questions are Q1, Q1, not numbered in order from Q1", changed(same))

    def test_a_question_numbered_otherwise_is_not_named_as_missing(self):
        def letter(d):
            d["benefits"][0]["id"] = "A"
            d["practices"][0]["benefit"] = "A"

        self.assertEqual(
            changed(letter),
            [
                "questions are A, Q2, not numbered in order from Q1",
                "Q1 is named, but there is no such question",
            ],
        )

    def test_about_a_part_named_after_the_whole_that_is_not_there(self):
        def wrong(d):
            d["benefits"][0]["about"] = "z"

        self.assertEqual(changed(wrong), ["Q1 is about z, which is no part"])

    def test_a_question_named_in_a_benefit_that_is_not_there(self):
        def name(d):
            d["benefits"][0]["what"] = "Before Q3, does it?"

        self.assertEqual(changed(name), ["Q3 is named, but there is no such question"])

    def test_a_value_that_is_no_text_names_no_question(self):
        def number(d):
            d["parts"][0]["level"] = 3

        self.assertEqual(changed(number), [])


class Plain(unittest.TestCase):
    def test_reads_a_page_as_its_words(self):
        page = "<p>A <b>Bold</b> &amp; <code>`x`</code> \u201cquoted\u201d \u2014 "
        page += "it\u2019s <i>so</i> .</p>"
        self.assertEqual(practices.plain(page), 'a bold & x "quoted" - it\'s so.')

    def test_leaves_out_the_styles_and_scripts_a_browser_does_not_show(self):
        page = (
            '<h4>The product</h4><style>.a{b:c}</style><SCRIPT type="x">var d;</SCRIPT><p>helps</p>'
        )
        self.assertEqual(practices.plain(page), "the product helps")

    def test_joins_the_text_of_inline_tags_as_a_browser_shows_it(self):
        page = (
            '<pre><var class="var">program</var>:<var>file</var>:<code>n</code>: <em>m</em></pre>'
        )
        self.assertEqual(practices.plain(page), "program:file:n: m")
        page = '<a href="x">li</a><span>nk</span> <b>b</b><i>i</i><strong>s</strong>'
        self.assertEqual(practices.plain(page), "link bis")

    def test_keeps_the_text_of_blocks_apart(self):
        self.assertEqual(
            practices.plain("<p>one</p><p>two</p><li>three<br>four"), "one two three four"
        )


def response(kind, body):
    """What urlopen gives for a page of the kind and body, as a context manager."""
    answer = mock.MagicMock()
    answer.__enter__.return_value.headers.get.return_value = kind
    answer.__enter__.return_value.read.return_value = body
    return answer


def refused(test, code):
    """A server's refusal with the code, closed when the test ends, as urlopen's caller would; it
    holds its body, as urlopen's always does, for Python 3.9 cannot close one that holds none."""
    body = io.BytesIO(b"")
    error = urllib.error.HTTPError("https://x.example/t", code, "no", email.message.Message(), body)
    test.addCleanup(error.close)
    return error


class Fetch(unittest.TestCase):
    def setUp(self):
        practices.fetch.cache_clear()
        self.addCleanup(practices.fetch.cache_clear)
        self.sleep = mock.patch.object(practices.time, "sleep").start()
        self.addCleanup(mock.patch.stopall)

    def opened(self, *answers):
        return mock.patch.object(urllib.request, "urlopen", side_effect=answers)

    def test_gives_the_type_and_the_body_opening_each_page_once(self):
        with self.opened(response("text/html", b"page")) as urlopen:
            self.assertEqual(practices.fetch("https://x.example/t"), ("text/html", b"page"))
            self.assertEqual(practices.fetch("https://x.example/t"), ("text/html", b"page"))
        self.assertEqual(urlopen.call_count, 1)
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://x.example/t")
        self.assertEqual(request.get_header("User-agent"), practices.AGENT)
        self.assertIn("practices.py", practices.AGENT)

    def test_reads_a_file_on_github_as_its_own_text(self):
        with self.opened(response("text/plain", b"file")) as urlopen:
            practices.fetch("https://github.com/o/r/blob/main/a/b.md")
        expected = "https://raw.githubusercontent.com/o/r/main/a/b.md"
        self.assertEqual(urlopen.call_args.args[0].full_url, expected)

    def test_asks_again_after_a_longer_wait_each_time_it_is_asked_to(self):
        page = response("text/html", b"page")
        with self.opened(*[refused(self, 429) for _ in range(3)], page) as urlopen:
            self.assertEqual(practices.fetch("https://x.example/t"), ("text/html", b"page"))
        self.assertEqual(urlopen.call_count, practices.TRIES)
        self.assertEqual(
            self.sleep.call_args_list,
            [
                mock.call(practices.WAIT),
                mock.call(2 * practices.WAIT),
                mock.call(3 * practices.WAIT),
            ],
        )

    def test_gives_up_after_its_tries(self):
        with (
            self.opened(*[refused(self, 429) for _ in range(practices.TRIES)]),
            self.assertRaises(urllib.error.HTTPError),
        ):
            practices.fetch("https://x.example/t")
        self.assertEqual(self.sleep.call_count, practices.TRIES - 1)

    def test_any_other_refusal_is_not_asked_again(self):
        for code in (404, 500):
            with self.subTest(code=code):
                practices.fetch.cache_clear()
                with (
                    self.opened(refused(self, code)) as urlopen,
                    self.assertRaises(urllib.error.HTTPError),
                ):
                    practices.fetch("https://x.example/t")
                self.assertEqual((urlopen.call_count, self.sleep.call_count), (1, 0))

    def test_waits_15_seconds_first_and_gives_a_page_30_seconds(self):
        page = response("text/html", b"page")
        with self.opened(refused(self, 429), page) as urlopen:
            practices.fetch("https://x.example/t")
        self.assertEqual(self.sleep.call_args_list, [mock.call(15)])
        self.assertEqual(urlopen.call_args.kwargs, {"timeout": 30})


def page(body, kind="text/html; charset=utf-8"):
    return lambda url: (kind, body.encode("utf-8"))


def failing(error):
    def get(url):
        raise error

    return get


class Sources(unittest.TestCase):
    def test_a_page_holding_its_title_and_words_is_the_one_meant(self):
        data = copy.deepcopy(DATA)
        data["practices"][0]["grounds"] = [dict(G, quote="it\u2019s so")]
        self.assertEqual(practices.sources(data, page("<title>T</title><p>It's so.</p>")), [])

    def test_a_page_not_holding_its_title_or_its_words(self):
        where = "Q1 ground 1 (https://x.example/t)"
        self.assertEqual(
            practices.sources(DATA, page("<p>none</p>")),
            [f"{where} does not hold its title", f"{where} does not hold its quote"],
        )

    def test_a_page_that_is_no_html_or_text_is_not_checked(self):
        where = "Q1 ground 1 (https://x.example/t)"
        self.assertEqual(
            practices.sources(DATA, page("", "application/pdf")),
            [f"{where} not checked: the page is application/pdf"],
        )
        self.assertEqual(
            practices.sources(DATA, page("", "")), [f"{where} not checked: the page is of no type"]
        )

    def test_a_page_of_xhtml_is_checked(self):
        self.assertEqual(practices.sources(DATA, page("T y", "application/xhtml+xml")), [])

    def test_each_way_a_page_fails_to_open(self):
        for error in (
            refused(self, 404),
            urllib.error.URLError("no such host"),
            TimeoutError("timed out"),
            ConnectionResetError("reset"),
            http.client.IncompleteRead(b""),
            http.client.InvalidURL("bad"),
        ):
            with self.subTest(error=error):
                found = practices.sources(DATA, failing(error))
                self.assertEqual(
                    found, [f"Q1 ground 1 (https://x.example/t) does not open: {error}"]
                )

    def test_each_ground_after_one_not_checked_is_checked(self):
        data = copy.deepcopy(DATA)
        data["practices"][0]["grounds"] = [G, dict(G, url="https://x.example/u")]
        for first, said in (
            (failing(TimeoutError("timed out")), "does not open: timed out"),
            (page("", "application/pdf"), "not checked: the page is application/pdf"),
        ):
            with self.subTest(said=said):

                def get(url, first=first):
                    return first(url) if url.endswith("/t") else ("text/html", b"<p>none</p>")

                found = practices.sources(data, get)
                self.assertEqual(found[0], f"Q1 ground 1 (https://x.example/t) {said}")
                self.assertIn("Q1 ground 2 (https://x.example/u) does not hold its title", found)

    def test_a_fault_of_the_script_is_not_taken_for_a_page_that_fails_to_open(self):
        with self.assertRaises(TypeError):
            practices.sources(DATA, failing(TypeError("a bug")))


class Markdown(unittest.TestCase):
    def test_holds_each_part_question_and_method_under_its_question(self):
        text = practices.markdown("kind", DATA)
        expected = ["# kind", "The reader gets it.", "## Parts", "- **a**: A.", "  - **b**: B."]
        expected += ["- **Q1** (a): Does it?", "### Q1: Does it?", "**Thinking**: Think."]
        expected += ["1. Do.", '- [T](https://x.example/t), X, 2020: "y"']
        for line in expected:
            self.assertIn(line, text)
        self.assertLess(text.index("## Benefits"), text.index("## Practices"))

    def test_sets_each_part_under_the_one_it_is_in(self):
        c: dict[str, Any] = {"id": "c", "what": "C."}
        b: dict[str, Any] = {"id": "b", "what": "B.", "parts": [c]}
        data = {**DATA, "parts": [{"id": "a", "what": "A.", "parts": [b]}]}
        lines = practices.markdown("kind", data).splitlines()
        start = lines.index("## Parts") + 2
        self.assertEqual(
            lines[start : start + 3], ["- **a**: A.", "  - **b**: B.", "    - **c**: C."]
        )

    def test_leaves_out_what_a_best_practice_has_none_of(self):
        data = copy.deepcopy(DATA)
        del data["parts"]
        text = practices.markdown("kind", data)
        self.assertNotIn("## Parts", text)
        self.assertEqual(text.count("**Steps**"), 1)
        self.assertEqual(text.count("**Grounds**"), 1)


class Standard(unittest.TestCase):
    def test_gives_the_goal_parts_and_questions_alone(self):
        # Given: a template with its practices
        # When: its standard is taken out
        # Then: the practices are left out, the rest as written
        self.assertEqual(
            practices.standard(DATA),
            {"goal": DATA["goal"], "parts": DATA["parts"], "benefits": DATA["benefits"]},
        )

    def test_a_template_of_no_parts_gives_none(self):
        data = copy.deepcopy(DATA)
        del data["parts"]
        self.assertNotIn("parts", practices.standard(data))


class Groups(unittest.TestCase):
    def questions(self, *abouts):
        """A template whose questions are about the parts given, one each, in order."""
        return {"benefits": [{"id": f"Q{n}", "about": a} for n, a in enumerate(abouts, 1)]}

    def test_questions_about_the_same_parts_go_together(self):
        # Given: Q1 and Q3 about part a, Q2 about b
        data = self.questions("a", "b", "a")
        # Then: Q1 and Q3 go in one group, Q2 in another, each question named with the kind
        self.assertEqual(
            practices.groups(data, "k"),
            [{"id": "G1", "questions": ["k/Q1", "k/Q3"]}, {"id": "G2", "questions": ["k/Q2"]}],
        )

    def test_a_question_about_two_parts_joins_their_groups(self):
        data = self.questions("a", "b", "a, b", "c")
        self.assertEqual(
            practices.groups(data, "k"),
            [
                {"id": "G1", "questions": ["k/Q1", "k/Q2", "k/Q3"]},
                {"id": "G2", "questions": ["k/Q4"]},
            ],
        )

    def test_a_join_found_late_takes_in_a_group_made_before(self):
        # Given: Q2 about b, then Q3 joining c, which Q1 is about, to b
        data = self.questions("c", "b", "b, c")
        self.assertEqual(
            practices.groups(data, "k"), [{"id": "G1", "questions": ["k/Q1", "k/Q2", "k/Q3"]}]
        )

    def test_questions_of_the_whole_go_in_one_group(self):
        data = self.questions("the whole", "a", "b, the whole")
        self.assertEqual(
            practices.groups(data, "k"),
            [{"id": "G1", "questions": ["k/Q1", "k/Q3"]}, {"id": "G2", "questions": ["k/Q2"]}],
        )


if __name__ == "__main__":
    unittest.main()
