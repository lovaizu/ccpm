"""S1 of dev/lane/architecture.md, `lay.py print`, one test for each of its paths: lay.py run as the
developer AI runs it on the README's walkthrough, a double of the developer AI writing a set
proposal, and lay.py, proposal.py, lanes/, routes.py, ports.py and the adapter run real."""

import json
import os
import unittest

import helpers


class TestLaid(helpers.WalkthroughTest):
    def test_the_proposal_without_an_adapter_is_printed_as_the_walkthrough_shows(self):
        # Given: the walkthrough's plugin and proposal
        # When: lay.py print is run on the proposal
        done = self.lay_py("print")
        # Then: it prints the steps as they will read, as the walkthrough shows, and exits 0
        self.assertEqual((done.returncode, done.stdout), (0, helpers.shown(helpers.README_PRINTED)))

    def test_the_proposal_with_an_adapter_is_printed_with_the_adapter_run_on_its_cases(self):
        # Given: the walkthrough's proposal with writer's values read by an adapter beside it
        self.adapter()
        self.propose(lambda p: p["subagents"][0].update(adapter="hooks/adapters/values-w.py"))
        # When: lay.py print is run on it
        done = self.lay_py("print")
        # Then: it shows the adapter given its cases as they say, and exits 0
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn(
            "  adapter hooks/adapters/values-w.py: its 2 cases given as they say\n", done.stdout
        )

    def test_the_proposal_with_routes_is_printed_with_the_routes_first(self):
        # Given: the walkthrough's plugin with lead and reviewer, and docs/routes.md's routes
        self.write(os.path.join("changelog", "agents", "lead.md"), helpers.LEAD)
        self.write(os.path.join("changelog", "agents", "reviewer.md"), helpers.REVIEWER)
        self.propose(lambda p: p.update(routes=helpers.ROUTES))
        # When: lay.py print is run on it
        done = self.lay_py("print")
        # Then: it shows the routes, then each step as it will read, the routes' sentences laid
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertTrue(
            done.stdout.startswith("Routes of lead, laid on its step 1:\n"), done.stdout
        )
        self.assertIn(
            "1. Have writer write the entries for the next release and reviewer review them."
            f" {helpers.FOLLOW}\n",
            done.stdout,
        )
        self.assertIn(f"{helpers.END_REVIEWER}\n", done.stdout)


class TestRefused(helpers.WalkthroughTest):
    def refused(self) -> str:
        """What lay.py print says of the proposal kept, which it refuses, exiting 1."""
        done = self.lay_py("print")
        self.assertEqual(done.returncode, 1, done.stdout)
        return done.stdout

    def test_a_proposal_out_of_its_form_is_refused_saying_where(self):
        # Given: the walkthrough's proposal with a key the proposal's schema has not
        self.propose(lambda p: p.update(owner="me"))
        # When: lay.py print is run on it
        # Then: it says where it is out of its shape and how to write it, and exits 1
        self.assertTrue(self.refused().startswith("lay.py: the proposal is out of its shape at $"))

    def test_a_proposal_with_a_rule_that_cannot_be_laid_is_refused_saying_why(self):
        for change, said in (
            (
                lambda p: p["subagents"][0]["steps"][0].update(step=9),
                "gives step 9, which the Steps of writer do not have",
            ),
            (
                lambda p: p["subagents"][0]["steps"][0]["lanes"][0].update(takes=[""]),
                "gives run_only on step 2 of writer with a take that is empty",
            ),
        ):
            with self.subTest(said=said):
                # Given: the walkthrough's proposal with a lane on a step writer has not, or
                # taking an empty thing
                self.propose(change)
                # When: lay.py print is run on it
                # Then: it says what is wrong and how to fix it, and exits 1
                self.assertTrue(self.refused().startswith(f"lay.py: the proposal {said};"))

    def test_a_proposal_with_routes_that_cannot_be_followed_is_refused_saying_why(self):
        # Given: routes whose every route has a `to`, so the run cannot end
        self.write(os.path.join("changelog", "agents", "lead.md"), helpers.LEAD)
        self.write(os.path.join("changelog", "agents", "reviewer.md"), helpers.REVIEWER)
        endless = {
            **helpers.ROUTES,
            "routes": [
                *helpers.ROUTES["routes"][:3],
                {"from": "reviewer", "on": "good", "to": "writer"},
            ],
        }
        self.propose(lambda p: p.update(routes=endless))
        # When: lay.py print is run on it
        # Then: it says the run cannot end, and exits 1
        self.assertTrue(
            self.refused().startswith(
                "lay.py: the proposal gives no route without a `to`, so the run cannot end;"
            )
        )

    def test_a_proposal_whose_adapter_gives_a_case_otherwise_is_refused(self):
        # Given: the adapter beside the proposal, one of its cases saying it gives another value
        beside = self.adapter()
        cases = [dict(c) for c in helpers.VALUES_CASES]
        cases[0] = {**cases[0], "gives": {"values": {"work": ["b.md"]}}}
        self.write(os.path.join(beside, "values-w.json"), json.dumps(cases))
        self.propose(lambda p: p["subagents"][0].update(adapter="hooks/adapters/values-w.py"))
        # When: lay.py print is run on it
        # Then: it names the case and what the adapter gave, and exits 1
        said = self.refused()
        self.assertIn(
            "names the adapter hooks/adapters/values-w.py, which on its case 1 gave", said
        )


if __name__ == "__main__":
    unittest.main()
