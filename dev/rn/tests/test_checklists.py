import json
import os

from helpers import RepoTest, rn_checklist


class TestChecklists(RepoTest):
    def test_each_kind_rn_keeps_is_found_with_the_checklists_its_opening_applies(self):
        # Given: a repository with no checklists of its own
        # When: rn is asked for the checklists of each kind it keeps
        # Then: it lists rn's checklist for the kind, from the folder of what the kind is for, after
        #   rn's readability checklist where the kind's opening applies it, and ends well
        expected = {
            "readability": ["readability"],
            "checklist": ["readability", "checklist"],
            "readme": ["readability", "product/readme"],
            "ux": ["readability", "product/ux"],
            "design": ["readability", "product/design"],
            "prompt": ["readability", "product/prompt"],
            "code": ["product/code"],
            "plan": ["readability", "session/plan"],
            "proposal": ["readability", "session/proposal"],
            "verification": ["readability", "verification"],
        }
        for kind, names in expected.items():
            with self.subTest(kind=kind):
                code, out = self.rn("checklists", kind)
                self.assertEqual(code, 0)
                self.assertEqual(
                    [(c["path"], c["name"]) for c in json.loads(out)],
                    [(rn_checklist(path), os.path.basename(path)) for path in names],
                )

    def test_a_kind_with_no_checklist_found_gives_an_empty_list(self):
        # Given: a repository with no checklists of its own
        # When: rn is asked for a kind neither rn nor the user keeps
        # Then: it prints an empty list and ends well
        code, out = self.rn("checklists", "release-notes")
        self.assertEqual((code, json.loads(out)), (0, []))

    def test_a_kind_that_is_not_words_joined_by_hyphens_stops(self):
        # Given: a kind that holds a path, a capital letter or a stray hyphen
        # When: rn is asked for its checklists
        # Then: rn stops, saying the kind is not words joined by hyphens and giving one that is
        for kind in ["../code", "notes/code", "Code", "-code", "code-", "release--notes"]:
            with self.subTest(kind=kind):
                self.assertEqual(
                    self.rn("checklists", kind),
                    (
                        1,
                        (
                            f"{kind}: a kind is a word or words joined by hyphens, "
                            "such as release-notes\n"
                        ),
                    ),
                )

    def test_the_users_checklist_comes_after_rns_for_the_same_kind(self):
        # Given: the user keeps a checklist of their own for code
        # When: rn is asked for the checklists of code
        # Then: rn's comes first, then the user's, with the name and version its front matter gives
        self.write(".rn/checklists/code.md", "---\nname: our-code\nversion: 1.2.0\n---\n")
        _, out = self.rn("checklists", "code")
        listed = json.loads(out)
        self.assertEqual(
            [c["path"] for c in listed], [rn_checklist("product/code"), ".rn/checklists/code.md"]
        )
        self.assertEqual(
            listed[1], {"path": ".rn/checklists/code.md", "name": "our-code", "version": "1.2.0"}
        )

    def test_a_checklist_the_users_opening_names_comes_first(self):
        # Given: the user's checklist for a kind rn does not keep, whose opening names readability.md
        # When: rn is asked for the checklists of that kind
        # Then: rn's readability checklist comes first, then the user's
        self.write(
            ".rn/checklists/release-notes.md",
            "---\nname: release-notes\nversion: 0.1.0\n---\n`readability.md`\n",
        )
        _, out = self.rn("checklists", "release-notes")
        self.assertEqual(
            [c["path"] for c in json.loads(out)],
            [rn_checklist("readability"), ".rn/checklists/release-notes.md"],
        )

    def test_a_checklist_an_opening_names_that_rn_does_not_keep_is_left_out(self):
        # Given: the user's checklist whose opening names a checklist rn does not have
        # When: rn is asked for the checklists of its kind
        # Then: only the user's checklist is listed
        self.write(
            ".rn/checklists/release-notes.md",
            "---\nname: release-notes\nversion: 0.1.0\n---\n`style-guide.md`\n",
        )
        _, out = self.rn("checklists", "release-notes")
        self.assertEqual([c["path"] for c in json.loads(out)], [".rn/checklists/release-notes.md"])

    def test_a_checklist_named_below_the_opening_does_not_apply(self):
        # Given: the user's checklist that names readability.md only under its first section heading
        # When: rn is asked for the checklists of its kind
        # Then: rn's readability checklist is not listed
        self.write(
            ".rn/checklists/release-notes.md",
            "---\nname: release-notes\nversion: 0.1.0\n---\n## Benefit\n`readability.md`\n",
        )
        _, out = self.rn("checklists", "release-notes")
        self.assertEqual([c["path"] for c in json.loads(out)], [".rn/checklists/release-notes.md"])

    def test_a_checklist_named_by_two_openings_is_listed_once(self):
        # Given: the user's readme checklist whose opening names readability.md, as rn's readme one does
        # When: rn is asked for the checklists of readme
        # Then: rn's readability checklist is listed once, first
        self.write(
            ".rn/checklists/readme.md",
            "---\nname: our-readme\nversion: 0.1.0\n---\n`readability.md`\n",
        )
        _, out = self.rn("checklists", "readme")
        self.assertEqual(
            [c["path"] for c in json.loads(out)],
            [
                rn_checklist("readability"),
                rn_checklist("product/readme"),
                ".rn/checklists/readme.md",
            ],
        )

    def test_a_checklist_without_its_name_and_version_stops(self):
        # Given: the user's checklist with no front matter, or front matter lacking the name or
        #   the version
        # When: rn is asked for the checklists of its kind
        # Then: rn stops, naming the checklist and saying to open it with its name and version
        for text in [
            "",
            "---\nversion: 0.1.0\n---\n",
            "---\nname: release-notes\n---\n",
        ]:
            with self.subTest(text=text):
                self.write(".rn/checklists/release-notes.md", text)
                self.assertEqual(
                    self.rn("checklists", "release-notes"),
                    (
                        1,
                        (
                            ".rn/checklists/release-notes.md: open the checklist with front matter "
                            "giving its name and version\n"
                        ),
                    ),
                )
