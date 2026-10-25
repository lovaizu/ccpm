# rn tests and trials audit (read-only, at c537dc3)

52 findings. One defect fails a test today when it runs alone (H1). The tests and the move trials
hold three of the maintainer's decisions in their old form (T1-T3, C1). Checked by running: the
unit tests (191, 3.5 s, all pass, 100% line and branch coverage of rn/scripts/rn.py); every unit
test run on its own (one fails, see H1); the property tests on the dev profile (11, pass); ruff
check and format (pass). Mutation testing was not run. The trials were read, not run.

## dev/rn/tests/helpers.py

- H1. helpers.py:30-32 `dated.start()` / `self.addCleanup(dated.stop)`, with helpers.py:29 "Its
  commits are dated, so no test reads the clock through them". **defect**, code.md B-7.
  `testing.copied` runs `main_and_work` once a run, inside whichever test asks first, so only that
  test's commits are dated and every later test commits at the clock. Proof:
  `python -m unittest test_rn.AnswerTest.test_an_answer_the_user_did_not_type_stops_and_keeps_nothing`
  fails when run alone. Its subtest "typed before the sign-off was shown" types at
  `2000-01-01T00:00:00Z` (test_rn.py:2357), which equals DATE, and rn.py:1715 `since` takes "at or
  after". Should be: date every test's commits (patch in `RepoTest.setUp`), and give that subtest a
  time before DATE.
- H2. helpers.py:10 `sys.path.insert(... "lane")` also appears at test_rn.py:28. **duplication**,
  B-5. Keep one.
- H3. helpers.py is one class used by test_rn.py alone, and properties.py:60
  `from helpers import testing` reaches lane's module through it. **complexity**, B-3/B-5.
  properties.py should import `testing` directly. helpers.py becomes the shared base once
  test_rn.py is split (Structure).

## dev/rn/tests/test_rn.py

- T1. Decision "a work is one output": the tests hold every call of a task on `t<n>`. Places:
  :1004, :1017-1019 ("the design stage made t1 and checklist-code"), :1427 (default work `"t1"`),
  :1518-1529 ("t<n> for task T<n>"), :1531-1540, :1575, :1654-1679 (serves taken from the task),
  :1735-1743, :2132 `UX_LINK = "T1: ..."`, :2140-2149, :2167-2187, :2252-2271 (`"T1\n- Form: a page"`).
  **inconsistency** with dev/rn/architecture.md:124-126. These tests change with the work naming.
- T2. Decision "the plan's CCS holds only what replanning needs": :1694-1718 expects `{"has":
  call_at("0003")}`, `call_at("0004")` and `call_at("0004", "result.json")`, that is, every
  returned call of each done task. **inconsistency**, B-6. Should expect only what each done task
  served, decided and made.
- T3. Decision on the `x in ("a",)` idiom: :244 `work in ("learnings",)`, :627 `option in
  ("message",)`, :2277 `given in ("not returned",)`. **inconsistency**, B-3. Use `==`.
- T4. :2304 and :2397 `datetime.datetime.now(...)`. **defect**, B-7. The test reads the clock,
  against :35 "so that no test reads the clock" and helpers.py:16-18. Use a fixed time after DATE
  (after H1).
- T5. :2525-2528 `slug`: `re.sub(r"[^a-zA-Z0-9]", "-", top)` is a second rule for a project's
  records folder, different from rn.py:1647-1649, which counts UTF-16 units. properties.py:214-217
  is a third copy, the same expression as rn.py, so its expected value is taken from the code it
  checks. **duplication/defect**, B-5, B-6.
  - Should be: `RepoTest.setUp` takes the folder from `rn.project_folders` (setup, not an
    expected value), and `slug` goes.
  - The property test checks what every name must be (only `[A-Za-z0-9-]`, ASCII letters and digits
    in place, length in UTF-16 units) beside ProjectFoldersTest's fixed examples.
- T6. :1265, :1278, :1315, :1329, :1335, :1340 write `".git/rn"` and `".git/rn/record/history.txt"`
  as literals. **duplication**, B-5. `LEARNING` and `HISTORY` at :2517-2518 already hold them.
  Move those constants to the top and use them.
- T7. :2357 and :2381 `"2000-01-01T00:00:00Z"` repeat `helpers.DATE`. **duplication**, B-5. The
  subtest name "typed before the sign-off was shown" is wrong too: the time is equal, not before
  (B-3, see H1).
- T8. :2864-2889 `test_learnings_gives_the_sessions_and_turns_of_every_version_once` holds two
  behaviors: the session's learnings by ID, and turn's lessons each once with work, call and
  commit. **complexity**, B-7. Split it in two.
- T9. :1141-1148 `test_keeping_without_next_stops_with_the_usage` repeats UsageTest's `state
  --next` case (:2450). **duplication**, B-5. :607-614 (start `--title`) and :1935-1942 (ccs
  `--use`) are the same kind of one-off. Put start and ccs into UsageTest's table and drop the three.
- T10. :1266, :1295, :1316, :1768 expect the learnings part with `## Learnings`, and so does
  cases.py:363. rn/checklists/session/learnings.md F-1 has no heading. **inconsistency** (prior
  audit 4.3, kept). The tests change with the product's fix.
- T11. :1720-1733 `test_the_ccs_of_any_other_work_holds_the_goal_and_every_criterion` holds that
  `learnings` and `checklist-<kind>` serve every criterion. **inconsistency** (prior 4.4, kept). The
  tests change with the product's fix.
- T12. :1594-1600 `"work": "deliverable"` keeps the CCS key `deliverable` for every work's paths.
  **inconsistency** (prior 4.11, kept). One name stands for the finished work and for any work.
- T13. :1000-1029 test the move to build only with plan calls and document calls; no test makes a
  research or trial call in the design stage. **gap**, B-6. rn.py's `moved` counts any call other
  than the plan as a document (prior 4.9, kept).
- T14. :938 the variable `two` holds three tasks. **noise**, B-3. Name it `tasks`.
- T15. :2566 `LearningTest.start()`, the merge-base commit, shares its name with :418
  `StartTest.start()`, the arguments of `rn.py start`. **inconsistency**, B-5. Rename the first
  `left_at`.
- T16. :2543 LearningTest's docstring "A session kept." says less than the class holds (records,
  agents, learnings calls). Also :1-5 and :135 say the plugin folder holds "rn's checklists", but it
  holds stand-ins (`"# Code\n"`, `"# Plan\n"`, :146-147); rn's own plan checklist is read only
  through :56. **inconsistency**, B-3.
- T17. Constants and helpers are spread through the file. **complexity**, B-3 (layout). Should be:
  all module constants and helpers at the top. They are:
  - :119 `LEARNINGS`, apart from FOLDER and STEERING;
  - :45 `TURN`, after BRANCH but under :39's comment;
  - :1970-1979 `DONE` and `FIRST`;
  - :2132 `UX_LINK`;
  - :2516-2522 `LEARNING` to `KEPT_AT`;
  - :2525 `slug` and :2531 `said`, both defined after their first use at :161.
- T18. :2825 `ProjectFoldersTest(LearningTest)` inherits a session commit and push it never uses.
  **noise**, B-4/B-8. It needs only `CLAUDE_CONFIG_DIR`.
- T19. :1965-1967 `ShownTest.answered` is `keep(text, "feedback")` and adds nothing else.
  **noise**, B-4. Call `keep` with the message.
- T20. :1919-1933 `dict(zip(argv[2::2], argv[3::2]))` reads back options from a hand-written
  argv. **complexity**, B-3. Write each case as (work, paths, options).
- T21. :639 and :1353 leave expected texts unsplit past ruff.toml:3 `line-length = 100`, while
  every other expected text is split. **inconsistency**, B-3 (layout).
- T22. :686 `"rn: 0.10.0\n"` repeats `VERSION` (:49). **duplication**, B-5.
- T23. setUp at :869, :1425, :1573, :2548, and most PutTest and LearningsTest bodies, commit and
  push a session through git subprocesses for each test. **complexity**, B-8. A session repository
  made once with `copied("session", ...)` would do. Impact is low now (3.5 s), but mutation testing
  multiplies it.
- T24. Behaviors over a kind of input with no property test. **gap**, B-6:
  - learnings put back and renumbered after those kept (:1260-1290), over any list;
  - ticks kept across `--put` (:1179-1190), over any ticks;
  - a decision's title and wording through `decide` into the CCS (`: ` parting, :1491), over any
    text.
- T25. :2469 `test_rns_own_checklist_is_found_in_any_folder`: the checklist is in
  `checklists/product/`, so "any folder" says something else. **noise**, B-3. Say "in a folder of
  rn's checklists".

## dev/rn/tests/properties.py

- P1. :75 "as an unit test has it" should be "a unit test", and should name the test
  (test_rn.py:1116). **noise**, B-3 (prior 5, kept; line was :31).
- The expected value at :214-217 is counted in T5, and :60's import in H3.

## dev/rn/trials/moves/moves.py

- M1. :4 says "on Claude Code's default model", but dev/lane/trying.py:42 passes `--model opus`,
  and dev/architecture.md:320 asks for Opus named in each run. **inconsistency**, B-3 (prior 2.3,
  kept).
- M2. :95-102 and flow.py:311-317 each list the run's records by
  `~/.claude/projects/*/<session>.jsonl` (as trying.py:57 does). **duplication/defect**, B-5, B-1.
  They ignore `CLAUDE_CONFIG_DIR`, which rn/scripts/records.py:77 honors. Should be one function in
  trying.py, given the session IDs.
- M3. The same checks and helpers are written twice. **duplication**, B-5. Should be one each,
  beside `Seen`:
  - :44 `DEFAULT_KEPT` and cases.py:881 `KEPT` are again flow.py:117-122 `rules()`, which flow.py
    itself calls "as the move trials check";
  - :93's cost sum is again flow.py:125-128 `costed`;
  - :109's help test is again flow.py:345.

## dev/rn/trials/moves/stand.py

- S1. :168 and :219-220 write `"checked": "Read the work at each Good's lines against its item."`.
  **inconsistency**, B-3. In turn's result, `checked` is the learner's "what you checked of the
  run" (turn/scripts/run.py:686, turn/agents/learner.md:30), and this text reads as the
  orchestrator's Good check, which decision 1 removes. Give a learner's text.
- S2. :249-252 gives the line "turn: Next, turn:up will make X and give each of its N items its
  Good, round 1." **inconsistency**, B-3. turn's own form is "turn: Next, <agent> will <does>, of
  <work>, for <n> items, round <r>." (turn/scripts/run.py:285-286). Only the `turn:` prefix is
  checked (cases.py:887-890). Use turn's form, or say that only the prefix matters.

## dev/rn/trials/moves/place.py

- PL1. :63-64 `STEERING` and `CALL`, and :206 `"-ccs.json"` replaced by `"-result.json"`, restate
  rn.py's session and call names (rn.py:73). **duplication**, B-5 (prior 3.3, kept; lines were
  :69-70). Use rn's; cases.py already imports rn.
- PL2. :75 and :208 keep `Seen.calls` as positional tuples, read as `c[1]`, `c[2]`, `c[3]` at
  cases.py:839 and :846-847. **complexity**, B-3. Use a NamedTuple.
- PL3. :85-86 `Seen.steering` is a path and `Seen.text` is the steering's text. **noise**, B-3.
  Names say less: use `steering_path` and `steering_text`.
- PL4. :98, :110, :179, :183 and flow.py:151 use `self.plugins[0]` and `[1]` for turn and rn.
  **complexity**, B-3. Give each copy a name.

## dev/rn/trials/moves/cases.py

- C1. Decision "a work is one output": :64-76 `RESEARCH_CCS = ["ccs", "t1", RESEARCH, "--kind",
  "research", ...]`, :611-616, and case "task" :1080-1103 (`returned("t1", 1)`) make the research a
  call on the task's work. **inconsistency** with dev/rn/architecture.md:124-126. It follows
  rn/skills/up/SKILL.md:190 "The task's work is `t<n>`" (product, cross-slice).
- C2. Decision 1 touches rn: cases "good" (:1018-1040) and "short" (:1041-1065), `PLAN_BARE`
  (:288-290), `plan()`'s goods (:199-243), and every made's `goods` test rn's own orchestrator Good
  check (rn/skills/up/SKILL.md:174-185, "read ... each item's `good` at its `lines`"). The decision
  names turn's orchestrator only, so this is set apart for the user below.
- C3. :912 `{"plan": "plan", "design": "design"}.get(signoff, "deliverable")`. **noise**, B-4. Every
  sign-off's stage has the sign-off's name, so `front(signoff, signoff)`.
- C4. :637-656 `typed` builds Claude Code's record of a typed command again, as test_rn.py:2301-2311
  and :2531-2540 do. **duplication**, B-5. Keep one builder, which the trial imports.
- C5. :766-873 fourteen check builders (`front`, `next_has` ... `says`) have no docstring saying
  what they take and give. **noise**, code.md F-1.
- C6. :503-504 the comment "The moves before a case ..." sits above `number` and `made`, which are
  not moves. **noise**, B-3. Move it to :518.
- C7. :185 `TASKS = "## Tasks.."` is a line-range mark (stand.py's `<from>..<to>`), and its name
  says less. **noise**, B-3.
- C8. :216-224 goods keyed `B-8` between `B-4` and `B-5` mirror plan.md's numbering (prior 5).
  **inconsistency**. They follow plan.md once it is renumbered.
- C9. :43 and :417 take the date from `datetime.date.today()` when the module is imported, while
  `rn.py start` takes it at run time; a run that crosses midnight names another folder.
  **defect** (low), B-1.
- C10. The "covers" strings (:937-1309) and :131-148 `NEXT_*` write up's step numbers in about 40
  places, and a renumbered step leaves them wrong. **duplication**, B-5. All match SKILL.md:83-276
  today.

## dev/rn/trials/flow/flow.py

- F1. :13, :31 and :323 use the key `"AC2"`, but dev/rn/ux.md has KR1.1 and KR1.2 only. What it
  counts (points answered, proposals read, changes, fresh conversations) is the user's effort,
  KR1.2 (ux.md:38-45), whose minutes are reported apart under `minutes.stand-in`.
  **inconsistency**, B-3. Name it KR1.2, with the minutes in it.
- F2. :69 `SIGNOFFS` restates rn.py:174 `SIGNOFFS`. **duplication**, B-5.
- F3. :67 `LIMIT = 120` has no comment, unlike `WAIT` at :65. **noise**, B-3.
- F4. :107, :112 and :138 read `Seen` through `cases.steered`, `cases.kept_learnings` and
  `cases.REQUEST`, which are kept in the case table. **complexity**, B-5. Readers of `Seen` belong
  with it in place.py.

dev/rn/trials/flow/write.py, up.md, user.md and wants.json, and dev/rn/trials/moves/gh.py and
up.md: no finding.

## Structure

| Work | Takes on | Split / reshape |
|---|---|---|
| test_rn.py (2,948) | every subcommand's tests, fixtures, gh stand-in, record builders | split along rn.py's split (prior audit §1): test_session.py (Session, Start, State, Put), test_steering.py (FormTest), test_ccs.py (Decide, Ccs), test_proposal.py (Shown, Proposal, Design, Deliverable, Compared, Answer, Usage), test_records.py (Records, ProjectFolders, Learnings), test_command.py; fixtures (`steering`, `plan`, `task`, `said`, `typed`, constants) and RepoTest into helpers.py |
| RepoTest (:132) | repository, plugin folder, gh stand-in, Claude records folder, rn runners | keep the repository, plugin and gh stand-in; move `conversation` and the config folder to LearningTest; date commits here (H1) |
| cases.py (1,330) | works turn returns, state-making moves, checks, the case table | works.py (plans, learnings, notes, research), states.py (`started` ... `l1_answered`), checks.py (Check and builders), cases.py (CASES alone) |
| place.py | the case folder and reading what a move left | also take `steered`, `kept_learnings`, the two every-move rules, the records listing (M2-M3, F4) |

## Cross-slice

- rn/skills/up/SKILL.md:190 "The task's work is `t<n>`": the product side of decision 2, which
  T1 and C1 follow.
- rn/skills/up/SKILL.md:174-185: rn's orchestrator checks each Good (C2).
- rn/scripts/rn.py:1647-1649 `project_folders` is copied at properties.py:214-217 and differs from
  test_rn.py:2528 (T5).
- The learnings heading: rn.py `put_learnings` and the CCS cut against
  rn/checklists/session/learnings.md F-1 (T10).
- turn/scripts/run.py:285-286 (the line's form) and :686 (`checked`) against stand.py (S1, S2).
- rn/checklists/session/plan.md's B-8 placement against cases.py:216-224 (C8).
- dev/lane/trying.py:55-57 `agents` reads `~/.claude` alone (M2).
- dev/rn/cosmic-ray.toml:15 runs pyrefly before every mutant's test run, which multiplies mutation
  time (B-8). The excluded call.py and forms.py (:8-9) are prior noise 1.

## For the user to decide

- Decision 1 names turn's orchestrator. Does it also take away rn's own orchestrator Good check (rn
  up step 4, SKILL.md:174-185)? The move trial cases "good" and "short" (C2) rest on the answer.

## Prior audit points in this slice

Kept: §1 (test_rn split), 2.3 (M1), 2.7 (T3), 3.3 (PL1, now place.py:63-64), 3.4 (T5, now
properties.py:214-217), 4.1 (T1, C1), 4.3 (T10), 4.4 (T11), 4.5 (T2), 4.9 (T13), 4.11 (T12),
5 `properties.py:31` (P1, now :75). None dropped.

## Read

dev/rn/tests/test_rn.py 2948, dev/rn/tests/helpers.py 44, dev/rn/tests/properties.py 178;
dev/rn/trials/moves/moves.py 133, stand.py 142, gh.py 139, up.md 20, cases.py 1330, place.py 236;
dev/rn/trials/flow/flow.py 382, write.py 75, up.md 31, user.md 44, wants.json 6.

Also read whole: rn/checklists/product/code.md 202, rn/checklists/product/prompt.md 150,
dev/architecture.md 411, .claude/rules/dev.md 115, .rn/20261013-writ-rebuild/audits/rn.md 125,
dev/lane/testing.py 149, dev/rn/cosmic-ray.toml 18, dev/rn/README.md 13, dev/check.sh,
dev/properties.sh.

Read in part: rn/skills/up/SKILL.md (Steps 1-11 headings, step 4-5), rn/scripts/rn.py (around
:1582-1660, :1715), dev/rn/architecture.md :95-237, dev/rn/ux.md :20-45, dev/lane/trying.py :1-60,
turn/scripts/run.py :270-292, :670-690.

## Not read

dev/rn/tests/__pycache__/*.pyc and dev/rn/trials/*/__pycache__/*.pyc: bytecode, ignored by
.gitignore:3, not in the repository.
