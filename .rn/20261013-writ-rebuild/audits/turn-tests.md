# turn tests and trials audit (read-only, at c537dc3)

Scope: every file `git ls-files dev/turn/tests dev/turn/trials` lists (41 files), judged by
`rn/checklists/product/code.md` and `dev/architecture.md` Unit tests / Acceptance tests; turn's
scripts and agents read to judge them. Ran: `python -m unittest discover -s dev/turn/tests`
(171 tests, OK, 0.22 s), the property tests on the dev profile (8, OK, 0.41 s), coverage (turn's
five scripts 100% line and branch), `ruff check` / `ruff format --check` on dev/turn (pass). Not run:
mutation testing, CI profile of the property tests, any trial (they start Claude Code).

## A. Places the maintainer's decisions touch

Decision "only the first user looks for Good; the orchestrator's Good check goes":

1. `dev/turn/tests/test_next.py:348-483` `class TestGoodCheck` — the whole class holds the Good check
   (shown, held, untrue, out of form, fence). Goes; its three paging tests (:438-475, "goods, page 1
   of 3") are the only tests of `run.paged` with more than one page and must move to another view
   that pages (`check` or `left`), or paging loses its tests.
2. `dev/turn/tests/helpers.py:107-116` `HOLDS`, `UNTRUE` and `:292-297` `def held` — go;
   `first_read` (:282) then ends the round straight into the learner or the next round.
3. `dev/turn/tests/test_next.py:496-506` `left()` asserts "turn:up found 1 of 1 Goods hold"; and every
   `self.held()` in TestRounds (:494, 514, 546, 597, 600, 608, 610, 616, 619), TestEachPart (:667),
   TestLearner (:692, 716, 783), TestRecordsShown (:797) — rewrite on the first user's reading alone.
4. `dev/turn/tests/test_rounds.py:121-127` "the orchestrator check them"/`{"goods": ...}`,
   `:129-138` "the fourth stop goes to the check of the Good", `:140-150` "its Good checked to hold"
   / `HOLDS`, `:244-257` `test_the_good_check_s_outcome_is_told_before_the_next_round`, `:266`,
   `:371-379` `test_a_run_stopped_after_the_first_user_s_reading_goes_on_from_the_check`.
5. `dev/turn/tests/test_forms.py:286-321` `class TestHeld`, imports `HOLDS`, `UNTRUE` (:9, :16).
6. `dev/turn/tests/properties.py:23` `forms.HELD` in `FORMS`, `:27` `"holds"` in `KEYS`.
7. `dev/turn/tests/test_lanes.py:204` `turn:up` lanes: step numbers in `hooks.json` shift once
   up.md step 5 goes; the test reads them from hooks.json, so lane:up must lay them again first.
8. `dev/turn/trials/flow/flow.py:4-6` "where a set README must pass or fail the orchestrator's own
   check of a Good"; `:12-14` `sent` "past the check of B-2's Good"; `:15-16` way `untrue` exists only
   for the check; `:17` `left` "as `untrue` in two rounds"; `:23-25` and `:68-72` `stopped` stops at
   "`turn:up will check that each Good`", a line that goes — give `stopped` another line to stop at.
9. `dev/turn/trials/flow/replies/untrue.json` (whole) goes; `replies/left.json` must reach "two rounds
   without Good" by first-user stops instead of an untrue Good the check rejects (:130-196 give B-1
   a Good at README.md:3-3, which would now be taken).
10. `dev/turn/trials/flow/results.json:142-207`, `dev/turn/trials/readme/results.json` throughout:
    records of runs with the check; stale once it goes (see C).

Decision "`x in ("a",)` becomes `==`, untellable mutants get `# pragma: no mutate`":

11. No test-side line uses the idiom. The product lines (`turn/scripts/call.py:86`
    `scope in (EACH,)`, `run.py:355` `step in ("check",)`) compare against module constants that
    are the same string objects, so the `==`→`is` mutant survives every test: those two lines are
    where the pragma goes (other auditor's slice; noted as the tests reveal it).

## B. Findings by file

### dev/turn/tests/helpers.py

12. `:1` no module docstring — noise/inconsistency, code.md F-1. Say what the tests share and why.
13. `:155` `self.repo = self.base` — two names for one folder, B-5. Keep `base`.
14. `:172` `def turn`, `:178` `def state` without docstring — F-1.
15. `:282-290` `first_read` writes `kept["sent"] = run.SENDS` into the state file — test steering
    the flow by its private state key, B-7; and `test_next.py:781` writes the same again by hand
    (B-5). Patch `run.SENDS` as `run.WAIT` is patched (`:168`), in one place.
16. `:272-280` `reading()` builds stops with `places=["README.md:1-1"], did=DID, lacking=LACKING`;
    `test_next.py:32-34` `STOPPED_F1`/`STOPPED_B1` write the same "as RepoTest.reading gives it";
    `STOPPED` (`:98-104`) is a third stop with `README.md:3-3` — B-5. One stop maker.
17. `:265-270` `made()` default claim `(GOOD, dict(GOOD, item="B-1"))` equals `test_rounds.py:24`
    `CLAIM` — B-5. Use `self.made()` there.
18. `:305` `given_record(..., folder=None)` — no caller passes `folder`, B-4. Drop it.
19. `:322` `def named` repeats `run.named` (`run.py:713`) — B-5 (prior audit 3.4, kept). Use
    `run.named`.
20. `:105` line of 101 characters — over the repository's width of 100 (ruff.toml:3).

### dev/turn/tests/test_next.py

21. `:1` no module docstring — F-1.
22. `:28-29` `ITEM_F1`, `ITEM_B1` repeat `test_forms.py:25-28` `ITEMS`, `properties.py:24`
    `ITEMS` and the dicts written out at `test_start.py:152-153`, `:189-190` — B-5. One pair in
    helpers.
23. `:486` `class TestRounds` (across rounds) while `test_rounds.py` holds the back and forth inside a
    round, and test_rounds.py also holds TestTold, TestResumed, TestFolderMoved — one name for two
    things, and files that take on several, B-5/B-3. See Structure.
24. `:709-717` and `:774-784` call `RepoTest.setUp(self)` inside a test of `TestLearner`, whose
    setUp already ran a whole run with records — the setUp's run is wasted and the test reads as one
    scenario on top of another, B-7/B-8. Give them a class of their own.
25. `:690` `self.orchestrator = ...` never read — noise, B-4.
26. `:787-884` `TestRecordsShown` tests `records.shown`/`records.orchestrator` by driving a whole
    run (start, claim, reading, check) per test — the records' behavior fails with any flow fault,
    B-7; and `:854-855` calls `run.records.wrapped` where properties.py uses `records` — B-3 idiom.
    Test `records.shown(path)` and `records.orchestrator` directly.
27. `:300-307` `test_a_reading_of_the_orchestrator_between_the_roles_stops` and
    `test_rounds.py:112-117` hold the same stop on two paths; fine, but the first's name says
    "between the roles" where its Given says "waiting on the generator's reply" — B-3, name it so.

### dev/turn/tests/test_rounds.py

28. `:1` no module docstring — F-1.
29. `:34` `self.first = ...` never read — noise, B-4.
30. `:75-84` `self.waiting.stop()` … `self.waiting.start()` around the test — roundabout; a failed
    assertion leaves the patch stopped for cleanup. Use `mock.patch.object(run, "WAIT", 100)` as
    `:107` does with 2 — B-3 (idiom unlike the code around it).
31. `:300-313` one test of two scenarios (the first user due, and another result waiting on the
    check, started twice) — B-7. Split.
32. `:328-354` `super().setUp()` mid-test for a second scenario — B-7. Split.
33. `:406-418` `test_the_start_gives_the_result_where_the_call_was_made` and
    `test_the_start_gives_what_the_orchestrator_reads_where_the_call_was_made` move no folder, and
    hold what `test_start.py:147-148` and `:157-170` already hold — B-4 noise. Drop, or move the
    folder as the class docstring says.
34. `:429` `here = os.path.join(self.repo, "{}").format` repeats `self.here` — B-5.
35. `:170-192`, `:194-220` each test holds several behaviors (line, move, description, the outcome
    line after) — B-7. One behavior each.

### dev/turn/tests/test_start.py

36. `:1` no module docstring — F-1; `:27` `call_with`, `:285` `stops` without docstring — F-1.
37. `:70-76` `test_the_script_runs_from_the_shell` runs `runpy`, not a shell, and prints the usage
    into every test run's output (the only test output); `:78-91` is the one that runs it from the
    shell and asserts the same exit — B-3 name / B-4 noise. Drop :70-76 or capture stdout.
38. `:85` `["python3", ...]` runs whatever python3 is first on PATH, not the interpreter under test,
    so the 3.9 CI job may test the newest — B-1. Use `sys.executable`.
39. `:300` `test_a_call_without_ccs_or_result_stops` loops over `"kind"` too — the name says less
    than the test, B-3.
40. `:404-408` `test_a_kind_that_is_not_a_name_stops` asserts only `'"work"'`, which other stops
    also contain — weak; assert "is not a name", B-6.
41. `:244`, `:257`, `:270` `self.started(CALL)` passes the default; `:240-247` and the folder tests
    run the check and the generator's due move where only `start` is tested (others use
    `self.turn("start", ...)`) — B-4/B-3.
42. `:361` `check: usability` in a test checklist's front matter — no reader needs it, B-4.

### dev/turn/tests/test_forms.py

43. `:1` no module docstring; `:36` `said`, `:545` `lessons` without docstring — F-1.
44. `:276-283` `test_a_check_asking_a_question_still_gives_every_item` tests `forms.CHECK` inside
    `class TestClaim` — B-3. Move to the check's class.
45. `:389-397` a test of "passes" also asserts `forms.parts(WORK) == PARTS`, a second behavior that
    `TestParts` holds — B-7; then `PARTS` (`helpers.py:128`) has no other use — B-4.
46. `:588-598` `test_a_ground_is_found_in_the_text_the_reader_gives` holds `forms.check(read=...)`,
    a parameter no caller in turn or rn passes (`forms.py:179-181`) — the test holds a seam, not a
    requirement, B-6/B-4 (prior audit 2, kept). Drop both.
47. `:673-679` "said to be for a role, as before" — a comment telling how the work went, B-3
    (prior audit, kept; now :674).
48. `:638` `FORMS = os.path.join(TURN, "forms")` between classes, a third meaning of `FORMS`
    (`properties.py:23` a tuple of Form, `run.py:58` a dict agent→Form) — B-5/B-3. Rename
    (`FORM_FILES`) and put it with the other constants.
49. `:32` `EACH_ITEM` here while `EACH`, `EACH_GOOD` are in helpers — one family in two files, B-5.

### dev/turn/tests/test_given.py

50. `:137` `"as the trial of the roles had it"` — tells where the case came from, B-3. Say what the
    run is.
51. `:148-160` and `test_start.py:157-170` both hold the start's `given` (one with `.` as what the
    receiver has, one with a page); fine as partitions, but `test_given.py:148` and
    `test_start.py:157` should sit in one file — B-5. See Structure.

### dev/turn/tests/test_lanes.py

52. `:8-9` "as the architecture gives them" — dev/turn/architecture.md names no lanes; the set is
    only in hooks.json and here — B-3 (says what the code's surroundings do not). Say "as the
    agents' steps call for them".
53. `:10` line of 101 characters — width.

### dev/turn/tests/properties.py

54. `:19` `call = run.call` reaches a module through another's attribute, while `forms` and
    `records` come from helpers — B-3. Export `call` from helpers.
55. No property test for `call.items` (any checklist text, fences included) or `records.shown` (any
    record entries), both behaviors over inputs of a kind; `forms.parts` has one for the same fence
    rule — B-6.
56. `:144-186` `test_the_paths_given_reach_all_...` rebuilds `without_run_files`' rule (`ours`,
    `on_way`) as its oracle and swallows `OSError` on layouts it cannot write — complexity; keep, but
    say in its comment why the oracle is written apart.

### dev/turn/trials/shared.py

57. `:131` `ignore_patterns(".git", ".turn", ...)` — `.turn/` is gone (turn/CHANGELOG.md:34) — dead,
    B-4 (prior audit, kept).
58. `:1-5` "the flow trial's task made a repository, with its check and a README that falls short":
    `CHECK` (:25) and `UNLICENSED` (:37) are used only by roles.py and kept.py — B-3 (prior audit
    4.9, kept).
59. `:55` `decisions: "str | None"` quoted, where every other module takes `from __future__ import
    annotations` — B-3 idiom.
60. `:91-116` `playground()` clones lovaizu/playground with `gh` and pushes nothing, while `task()`
    (:55-67) makes the same kind of repository with `git init`: two ways to one job, and a network
    and `gh` login needed for nothing the run uses — complexity, B-5. If no trial needs GitHub, use
    `task()`'s way; dev/architecture.md:337 asks the playground only of a trial that needs it.
61. `:101` skips `results.json` in a task folder: records kept inside a task folder mix the task's
    input with run records — complexity. Keep records apart (see C).

### dev/turn/trials/trial.py

62. `:31-45` `STEP` repeats turn/README.md:43-44 "Put each question it sends to the user …
    against its lines." — B-5; read it from the README, or name it as a copy.
63. `:29` `START` is the same text as `flow/flow.py:50` — B-5. Keep in shared.
64. `:54` the records' place built from `~/.claude` and a regex of Claude Code's folder naming,
    while `turn/scripts/records.py:239-243` honors `CLAUDE_CONFIG_DIR` and lane's `trying.agents`
    globs `~/.claude` — one place written three ways, B-5/B-1.
65. `:68-74` reads each agent's `.meta.json` `agentType` — as `records.kind` (records.py:265-272) and
    `flow/flow.py:108-114` do — B-5.
66. `:43` line of 170 characters, `:31`, `:37`, `:45` over 100 — line breaks from patched edits in a
    prompt, noise (prior audit, kept).
67. `:80-81` `shutil.rmtree(place)`/`(plugin)` only on success: a failed `claude` run (SystemExit in
    `trying.claude`) leaves the clone and the copy, against its docstring (:14) and
    dev/architecture.md:338-339 — defect, B-7. `try/finally`; the same in flow.py:119-120,
    roles.py:94-95, kept.py:91-93.

### dev/turn/trials/judge.py

68. `:22-25` the PROMPT hard-codes the CCS kinds (`deliverable`, `audience`, `purpose`, `checklist`,
    `source`) that `shared.call("source")` sets — B-5; build it from `shared.call`.
69. `:30-33` "run each command it tells the receiver to run … `mktemp -d`" — a fourth copy of the
    words in turn/agents/up.md, generator.md, first-user.md (prior audit 3.5 names three) — B-5.
70. `:1-9` judges each item afresh "by one bar", where KR1.1 (dev/turn/ux.md:22-27) is the calling
    AI's "own check of each Good at its lines" — judge.py measures another thing under KR1.1's name,
    inconsistency. Name what it measures, or measure KR1.1.
71. `:6-7` "one run for all the folders judged them in a few calls, and passed a link to a file that
    is not there" — how the work went, B-3 (prior audit, kept).
72. `:42` `judged()` without docstring — F-1.

### dev/turn/trials/flow/flow.py

73. `:78` `way, place = sys.argv[1], ...` — no usage stop on missing arguments (IndexError), unlike
    trial.py's `shared.arguments`; same in roles.py:28, kept.py:45 — B-2.
74. `:85-95` drops role hooks by `f" {r} " in h["command"]`, reading lane's command layout that
    `dev/lane/testing.py:136-148` `laid` reads too — B-5. Use `laid`'s reading.
75. `:1` line over 100 — width.

### dev/turn/trials/flow/stand.py

76. `:14`, `:16`, `:18` `open(...)` without `encoding="utf-8"`, as every other file gives it — B-3
    (and locale-dependent, B-1).

### dev/turn/trials/flow/roles/*.md

77. `generator.md:14-18`, `first-user.md:14-17` list prompt keys the stand-ins never use (`receiver`,
    `use`, `parts`, `checklists`, `answers`) — a third copy of `run.generator_given`/`reader_given`'s
    keys beside turn/agents — B-4/B-5. Name only `work` and `reply`.
78. `first-user.md:20`, `generator.md:20`, `learner.md:17` read files whose reading nothing checks
    (the stand-ins' lanes are removed, flow.py:85-86) — reason unsaid, B-3. Say why, or drop.
79. Each `description:` line (`:3`) runs to 118-141 characters — width.

### dev/turn/trials/flow/replies/*.json

80. The licensed README and its claim (`"## License\n\nMIT.\n"`, B-1 at README.md:11-11, three parts)
    are written out whole in plain.json, given.json, generator.json (variant), left.json, sent.json,
    untrue.json, as generator and first-user replies; the unlicensed README nine times, and again as
    `shared.UNLICENSED` — B-5, and dev/check.sh's copy check reads `.py` alone. Build the replies in
    flow.py from named pieces.

### dev/turn/trials/roles/roles.py

81. `:68-75` copies `run.replied`'s `forms.check(...)` arguments (run.py:451-458) — B-5 (prior audit
    3.7, kept).
82. `:34` "The copy of turn's scripts, on the path only once it is made": shared.py:19 has already
    put the working tree's `turn/scripts` first and imported `call`, so `run` from the copy uses the
    tree's `call` — defect against "the run uses it as it is when the run starts"; same at
    kept.py:26-36. Put the copy on the path before importing shared, or import nothing of the
    tree.
83. `:39` `def turn` without docstring; `:83-84` and kept.py:57-68 start the run and pass `CHECK`
    the same way twice — F-1, B-5.

### dev/turn/trials/roles/kept.py

84. Tries the generator and the first user together, where dev/architecture.md:319-326 asks each
    role tried on its own with the rest mocked — inconsistency. Try each kept role's message in
    roles.py, or say why the pair is tried.
85. `:3` docstring broken mid-sentence ("The\ngenerator's") — noise of a patched edit.

### dev/turn/trials/one/, readme/, flow/task/

86. `one/` is used by nothing but trial.py's usage example; dev/turn/README.md:7-8 calls it "for the
    Flow trial", which is flow/flow.py on flow/task — stale purpose, noise. Say what it is for or
    drop it.
87. `one/ccs.json`, `readme/ccs.json` name what the receiver has `source`; `flow/task/ccs.json` and
    turn/README.md:42 name it `has` — two names for one kind across the trials, B-5.

## C. Trial results files

`flow/results.json` (227 lines), `readme/results.json` (592), `roles/results.json` (357), read whole:

88. Needed: `.rn/20261013-writ-rebuild/decisions/dev/turn/architecture.decisions.md:72`, `:90` cite
    two of them as grounds. Current: no — most entries describe parts gone (evaluator, decision,
    hand-on, `.turn/out`, `turn.py given`/`record`, `forms.py:220 … "ran": []`). Explained: nowhere —
    dev/turn/README.md and no trial docstring says they exist or who writes them. Form: entries
    disagree (`commit` holding "T23 summary", "after the four prompts remade …"; `unit`/`run`/
    `stopped`/`stories` present or not; `minutes_to_return: null`). Should be: records of runs kept in
    the session folder that cites them (or left to git), out of the task folders; if kept here, one
    line in dev/turn/README.md and one entry form.

## Structure

| Part | Takes on | Split / reshape |
|---|---|---|
| `test_next.py` (884 lines) | check, made, Good check, rounds, each part, learner, records shown | `test_check.py`, `test_made.py`, `test_rounds.py` (across rounds, left), `test_parts.py`, `test_learner.py`, `test_records.py` (records.py direct, no flow) |
| `test_rounds.py` | round messages, told lines, resumed, folder moved | `test_round.py` (kept roles in a round), `test_told.py`, `test_resumed.py`; folder-moved tests into `test_given.py` |
| `test_start.py` + `test_given.py:148` | usage, start, stops, what start gives | `test_call.py` (usage, start, stops); every `given` test in `test_given.py` |
| `helpers.py` | fixtures, state shortcuts, run drivers, record writer | fixtures (one stop maker, one claim, one item pair), drivers; no state writes (patch `SENDS`) |
| `shared.py` | call, task repo, playground clone, args, keep, show, copy of turn | one `trial()` context: task repo, copy of turn, cleanup in `finally`; `START`; playground only if a trial needs GitHub |
| `flow/replies/*.json` | whole replies per way | named pieces (licensed / unlicensed README, claim, stop) composed per way in flow.py |
| `trials/*/results.json` | run records inside task folders | out of the task folders, to the session that cites them |

## Cross-slice

- `turn/scripts/forms.py:179-181` `read=` exists for one test (46).
- `turn/scripts/records.py:239-243`, `dev/lane/trying.py:55-57`: Claude Code's records folder found two
  ways (64).
- turn/agents/up.md, generator.md, first-user.md and judge.py: the same run-and-compare words (69).
- turn/README.md:43-44 copied in trial.py (62); turn/README.md:42 `has` vs task folders' `source` (87).
- dev/turn/README.md:7-11: "`one` for the Flow trial" stale, leaves out flow.py, roles.py, kept.py and
  the results files (prior audit 4.8, kept); "run each trial three times at once" against
  dev/architecture.md:337 "one at a time" for playground trials (60).
- dev/turn/cosmic-ray.toml:12 lists pyrefly's search paths by hand (`dev/turn/trials/flow`, `/readme`,
  `/roles` …) where dev/check.sh:35 finds them — two lists of one thing.
- `call.py:86`, `run.py:355`: where the `no mutate` pragma goes (11).
- dev/turn/ux.md:22-27 KR1.1 vs judge.py (70); dev/architecture.md:319-326 vs kept.py (84).

Prior audit (.rn/20261013-writ-rebuild/audits/turn.md) points in this slice: all kept (judge.py:5-6,
test_forms "as before", shared.py `.turn`, results unexplained, trial.py long lines, helpers.named,
roles.py copy of `forms.check`, shared.py:1-5, dev/turn/README stale); none dropped.

## Read

dev/turn/tests: helpers.py 324, properties.py 186, test_forms.py 679, test_given.py 191,
test_lanes.py 45, test_next.py 884, test_rounds.py 450, test_start.py 408.
dev/turn/trials: flow/flow.py 120, flow/replies/generator.json 147, given.json 175, left.json 258,
plain.json 101, sent.json 408, untrue.json 185, flow/results.json 227, flow/roles/first-user.md 23,
generator.md 27, learner.md 20, flow/stand.py 22, flow/task/ccs.json 4, checklist.md 18, demo.sh 1,
notes/decisions.md 2, judge.py 82, one/ccs.json 6, one/checklists/hello.md 12, one/hello.sh 1,
one/notes/hello.decisions.md 3, readme/ccs.json 6, readme/csvtidy.py 28,
readme/notes/readme.decisions.md 11, readme/results.json 592, roles/kept.py 93, roles/results.json
357, roles/roles.py 95, shared.py 151, trial.py 81.
To judge them: turn/scripts/run.py 751, call.py 165, forms.py 395, records.py 118, turn.py 8;
dev/lane/testing.py 149, dev/lane/trying.py 79; rn/checklists/product/code.md 202;
dev/architecture.md 411; .claude/rules/dev.md 115; .rn/20261013-writ-rebuild/audits/turn.md 127;
dev/turn/README.md 11, dev/turn/cosmic-ray.toml 15, dev/check.sh 55, dev/properties.sh 18;
parts of dev/turn/architecture.md (1-40, 100-177), dev/turn/ux.md (16-32), turn/agents/up.md (grep),
turn/README.md (36-48).

## Not read

None of the slice. Outside it, turn/agents/generator.md, first-user.md, learner.md were not read
whole (another auditor's slice); findings citing them rest on the prior audit's lines.
