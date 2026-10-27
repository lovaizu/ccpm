# Parts no purpose needs (audit of 2026-10-27)

Every file of lane, turn and rn read whole by three readers, one per plugin, each judging every
mechanism against its plugin's README and UX alone; each finding checked by hand against the source
and the user's earlier decisions. Put to the user one at a time, in this order; the user judges each.

## Added by the maker, unasked (16)

1. turn's `blocked`/`stopped`: a role stops the whole run and returns it, gone on with by a call
   again; with Principle 11, rn's handling and the flow's `unread` stop. The UX has only a question
   the run goes on from (dev/turn/ux.md, "A point only the user can decide"); a stop brings nothing
   back. Origin: widened from the user's question about hooks ("could not check" vs "no problem").
   0c8d1ce, 79b4805, 5dc063f.
2. turn's generator asks the user to add a file the work needs to the CCS
   (plugins/turn/prompts/generator.md step 6), against the UX "a choice the purpose settles, turn
   makes and names in the result". 40c6cc2.
3. turn's orchestrator words the questions for items left without Good, a second question path
   with its own stage and pages (orchestrator.md step 4, flow.py left, turn.py pages). cfea4d8.
4. turn's two nested bounds, three send-backs a round in two rounds, the second starting both roles
   anew (flow.py SENDS, MORE); no ground given, the time to a question doubled. fd270d7.
5. turn's three guards for `turn.py next` going to the background: WAIT, next.lock, unsent.
   1bb493f, 0c8d1ce.
6. lane's read-the-part-whole-first guard laid on every subagent with a part, with no line in the
   proposal (guard.py, entries.py), where lanes go only where a step alone does not hold and twenty
   runs held it. 2a181e0.
7. lane's layer reads an old hook-command form no released lane wrote (layer.py:219-263). d247485.
8. lane's record.py functions nothing but tests uses: agent_id, prompt (record.py:99, 173).
9. lane's two conditions for one rule, a told subagent never held for good (hook.py:156-164,
   guard.py:369-373); doubtful.
10. dev/lane/testing.py helpers lane's tests do not use (GitTest, the Hypothesis profile).
11. rn's issue to its makers made through turn and a stand-in reader, though the user reads it whole
    (plugins/rn/prompts/learnings.md:32-38), against Principle 4's caller-read works. 883aac2.
12. rn's stops said to come to the learnings (dev/rn/architecture.md:176-184), with nothing that
    finds them; settled with 1. c29568e.
13. rn.py history counts planned remakes as works made again (history.py:55-67). cf00730.
14. rn's scripts tell the orchestrator to run git push / commit, which it must not
    (repo.py:183, session.py:202).
15. rn's learnings appended and renumbered for a second writing no step makes
    (session.py:386-431). 4ac5e7e.
16. rn's move trials' checklists in the old `Look for` form, judged as following the template
    (dev/rn/trials/moves/place.py:66, cases.py:395).

## For the user to decide (6)

17. lane tells a subagent to stop its job where lane cannot check (guard.py:115, 246).
18. lane stops a command it cannot read (c01093d), the hooks matter itself.
19. a run value `null` rests every lane taking it, write_only included (cbc7631, the user's).
20. rn's code checklist asks ccpm's own rules of every user's code: property tests, no surviving
    mutant, tests in seconds, formatter/linter/type checker (code.md B-6, B-8, B-10).
21. rn's document templates held to a user's existing documents (doubtful).
22. rn's sign-offs: README/UX and code differ (T35 changes it).

## Raised and left, as the user decided them

The generator's lines for every item (T37), fix.md on every call (2026-10-24), adapters of three
ports (2026-10-25), judge.py (2026-10-25).
