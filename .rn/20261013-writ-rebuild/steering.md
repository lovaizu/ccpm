---
rn: 0.9.0
pr: https://github.com/lovaizu/ccpm/pull/61
status: running
artifact-language: English
conversation-language: Japanese
issue: https://github.com/lovaizu/ccpm/issues/53
readme: writ/README.md
design: dev/writ/design.md
verification: dev/writ/trials
---

# Goal

writ is rebuilt on turn (#53): it hands back a document its reader understands in one reading and
acts on, which the user can pass on without reading it over, and judges from the final report alone.
writ keeps the checklists that say what a good work of each kind is, and hands each job to
`turn:up`; the pith inside writ goes.

# Acceptance criteria

## Attractive quality

- A1: The user asks for a document of a kind and gets it finished, asked only what the checklist
  needs and their request and repository do not tell.
- A2: For a kind writ has no checklist for, the user chooses between the general one and having one
  made first, and a checklist made is used from then on.

## Must-be quality

- M1: Each part follows official best practice or says why it does not, and holds nothing its
  purpose does not need.
- M2: Checking a work is turn's alone; writ holds no second copy of it.
- M3: `claude plugin validate --strict` passes for writ and for the marketplace, and CI passes.

# Assumptions

- Fact, decided by the user: the plugin is built by `.claude/rules/plugin.md`, step by step; only the
  README and the design are agreed with the user, and the rest is built and checked without asking
  unless the README or the design should change.
- Fact, decided by the user: before the README, the user and the assistant agree on a scene of what
  the user does and what happens.
- Fact, decided by the user (2026-10-13): writ reads the checklist's items and asks the user, one
  question at a time, what the items need and the request and the repository do not tell; what it
  can infer, it puts as a proposal.
- Fact, decided by the user (2026-10-13): for a kind writ has no checklist for, writ asks the user
  whether to make the document with the general `doc.md` alone or to make that kind's checklist
  first with turn, against `essentials.md`.
- Fact, from #53: #36 and #37 are judged against the rebuilt writ by running what each describes.

# Rules

- The documents are written in English from the start; the user reads them through machine
  translation, so each thing keeps one plain word.
- Questions to the user are asked one at a time.

# Tasks

### [x] #1: The scene

Purpose: the user and the assistant agree, in about five lines, on what the user does with writ and
what happens, before anything is made.

Serves: A1, A2

Progress:

- Proposed (2026-10-13), with points 2 and 5 changed at the user's word:
  1. The user asks `/writ:up` to write this tool's README.
  2. writ picks the checklists for the kind (`doc.md` and `readme.md`), reads their items, and asks,
     one question at a time, what they need and the request and repository do not tell; what it can
     infer it puts as a proposal to confirm.
  3. writ hands the job to `turn:up`: turn writes, another AI reads it as the reader, and it is
     checked against the checklists; what only the user can decide is asked while the work goes on.
  4. The user gets the finished README and, for each item of the checklists, whether it is met.
  5. For a kind writ has no checklist for (say, release notes), writ asks whether to make it with
     the general `doc.md` alone, or to make that kind's checklist first with turn against
     `essentials.md` and use it.
- Agreed by the user (2026-10-13).

### [x] #2: writ's README

Purpose: `writ/README.md` written from the agreed scene with `doc.md` and `readme.md` open, and
agreed with the user (plugin.md step 1).

Serves: A1, A2, M1

Progress:

- Written from the scene with `doc.md` and `readme.md` open. Decided in writing it, for the user to
  confirm: a checklist writ makes goes to `.writ/checklists/<kind>.md` in the user's repository; the
  old README's lint tools and Claude Code choosing writ on its own are left out, since the scene
  does not hold them.
- The assistant wrote it by hand, not through `turn:up` as #53 says, so it was made again through
  `turn:up` (two rounds, 24 of 25 items met). The installed turn was an older copy under the same
  version, so it was installed again from the marketplace.
- Decided by the user (2026-10-13): a checklist writ makes goes to `.writ/checklists/<kind>.md` in
  the user's repository.
- Settled from the sources (2026-10-13): writ also fixes a document the user already has; the
  released README promises it, #53 drops nothing of it, and turn takes a deliverable already there.
- Found in the run, for turn (decided by the user, 2026-10-13): an answer must reach the generator at
  work at once; turn's step 5 only writes it to the questions file, so it reaches the work only on
  the next generator call. Fixed in turn's steps within this rebuild.
- Found in the run: the orchestrator asked the user a question the sources answer; a question goes
  to the user only when no source settles it.
- Decided by the user (2026-10-13): when turn returns `ask the user` with a way that lies in the
  work, the caller does not put it to the user but has it fixed; the user is asked only what they
  alone can decide. The README says nothing of it: the user only answers what they alone can decide, which the
  README already says, and how writ gets the rest met is its own work. The one item left (headings for the cases) was fixed by hand.
- Seen by the user (2026-10-13): the README made through turn was too long; they stopped at the
  opening. The checklist let it pass: its opening held how writ works, and its example showed turn's
  progress with a key to read it. Decided by the user: the measure is what the opening and the
  example are for, not a length; `readme.md` 0.2.0 asks it (B-4, U-3). Also seen: the judges looked
  only for lines that meet an item, never for lines no reader needs, and a gap was met by adding an
  explanation rather than removing what needed it; this is turn's to settle.
- Made again through `turn:up` with `doc.md` and `readme.md` 0.2.0 (2026-10-13): two rounds, every
  item met. The example now shows only what the user types and what writ says back, and turn is
  named once, under Requirements.
- Found in the run, for turn: while an agent of the run works in the background, turn's Stop hook
  blocks the conversation from ending its turn to wait, saying the run is open.
- Seen by the user (2026-10-13): the opening was still far longer than READMEs commonly have.
  Compared with five common tools and five official Claude Code plugins, `readme.md` asked for two
  things they do not: three points in the opening, and a reason for every requirement. Decided by the
  user: `readme.md` asks for an opening of one or two sentences, why to choose the product in its
  own section after the example, and a reason only where the reader could not see it.
- Decided by the user (2026-10-13): what is learned in a run goes into the checklists, not on as
  rules in the next task.
- Root cause, from the runs' records (2026-10-13): each round, the first user's guesses fell under
  `doc.md` B-3 (each idea given in full), and the generator met them by adding explanation, such as
  a list of every file turn writes; B-4 and U-3 let it pass, as each addition gives the reader
  something. `readme.md` applied `doc.md` whole, with the product's whole as the subject. Decided by
  the user: `readme.md` judges the items of `doc.md` with deciding and getting to the first result
  as a README's subject, and the rest goes to pages reached from Documentation.
- Decided by the user (2026-10-13): a checklist's version goes up once for a release, not with each
  change on a branch; `readme.md` is 0.2.0 here, against 0.1.0 released.
- Made again through `turn:up` on that `readme.md`, with no rules carried (2026-10-13): 24 of 26
  items met after two rounds. The one left, that writ reports once every item is met, was written in
  by hand, as decided above; the learner's way, to show an item not met, went against that decision.
- Found in the runs, for turn: the learner makes a rule for every later task from one finding, and
  `calling-from-a-plugin.md` tells the caller to carry it on unchecked; whether turn makes such rules
  at all is turn's to settle.
- turn's README made again the same way (2026-10-14): every item met after two rounds, 129 lines.
- Found in the run, for turn: its console prints each step's file path under `.turn/`, which the
  reader of turn's README took as inner workings they need neither to decide nor to start; whether
  the console shows them is turn's to settle.
- To do in #4: `writ/.claude-plugin/plugin.json` names turn in `dependencies`, which the README's
  Installation promises; `turn/calling-from-a-plugin.md` points to turn's README for what both say
  (the checklist's front matter, writing over a file git holds, Esc).
- Agreed by the user (2026-10-14).
- Decided by the user (2026-10-14): pith is removed now, so CI tells a real failure again; `/writ:up`
  still calls it until #4 rebuilds writ.

### [x] #3: writ's design

Purpose: `dev/writ/design.md` written with `doc.md` and `design.md` open, and agreed with the user
(plugin.md step 2), taking in "Essentials to add" from #53.

Serves: A1, A2, M1, M2

Progress:

- Next (2026-10-14): turn's README is agreed by the user. Write the design through `turn:up` with
  `doc.md` and `design.md` as viewpoints, carrying no rules. turn's Stop-hook fix is in the
  repository but not in the installed turn 0.1.0, so its stop messages still show while agents work;
  it is checked for real once a turn with the fix runs.
- `design.md` 0.3.0 asks U-3 (no case a principle settles), from #53's "Essentials to add"; agreed
  by the user (2026-10-14).
- Round 1 through `turn:up` (stopped): 33 of 34 items met; the one left asked whether writ promises
  a way for another plugin's step to call it, since rn 0.9.0 calls writ from a subagent.
- Found in checking it: turn says it must be called from the main conversation because a subagent
  cannot start others (`turn/calling-from-a-plugin.md:51-52`, `dev/turn/design.md:99`); Claude
  Code's subagent documentation now lets a subagent start its own, three layers deep by default
  since 2.1.219. What does tie turn to the main conversation is its questions while it works: a
  subagent has no AskUserQuestion and no way to reach its caller mid-run.
- Decided by the user (2026-10-14): turn asks nothing while it works. The caller settles what the
  checklists need before the call; what the sources leave open turn leaves open and returns at the
  end as `ask the user` with its differences; stopping and correcting a run are the caller's, by
  stopping or messaging it. So turn runs the same wherever it is called. turn's README and design,
  and writ's README example (the license asked mid-run), change first; then the design is written
  again.
- Seen by the user (2026-10-14): turn and writ hold code (scripts, hooks) and its tests, but no
  checklist says what good code is; `plugin.md` step 5 names checklists for documents and prompts
  only. Decided by the user: writ gets a checklist for code and its tests, made through `turn:up`
  against `essentials.md`, asking at least: tests written first and held to what the code must do,
  not fitted to it (TDD); each test's intent told by Given / When / Then; every branch run by a
  test (C1 coverage at 100%), so code no test needs and a test left unwritten both show; and the
  other common best practices for code and test code, such as a linter.
- Made through `turn:up` (2026-10-14): two rounds, every item but one item per thing met; the three
  joined items (a Then checked in full and no further, a stop's what went wrong and what to do,
  slips and style by tool) were split by hand, since a third run rewrote the checklist from nothing
  and dropped half its items, the type checker the user asked for among them.
- Found in the run, for turn: called again on a work with one item left, the generator rewrote the
  work from nothing rather than from the work as it stood, and lost items it had met; turn's README
  promises the work keeps giving every item it already gave.
- Agreed by the user (2026-10-14): the code checklist (`code` 0.1.0, B-1 to B-22 and F-1).
- Where to resume (2026-10-14), one point at a time with the user:
  1. turn's README (`48f5dee`, turn asks nothing while it works): agreed by the user (2026-10-14).
  2. `writ/references/essentials/` became `writ/checklists/`, and `essentials.md` became
     `checklist.md` (agreed by the user, 2026-10-14). rn's own `rn/references/essentials/` is rn's
     (#39); the old writ files #4 replaces had only their paths changed.
  3. This repository meets the code checklist (2026-10-14): coverage counts branches, and every
     branch is taken; Ruff checks and formats every file, and Pyrefly checks types for Python 3.9
     (decided by the user: mypy 2.0 and later cannot check code for 3.9, and ty is in beta); all
     of it runs by `dev/check.sh`, on every push and for builders; `plugin.md` step 5 names
     `code.md`.
  4. turn's design and code meet the agreed README (2026-10-14, design agreed by the user): turn
     asks nothing while it works, returns every question left open with `ask the user`, and a run
     called again on the CCS it returned starts from the work it returned, written over though git
     does not hold it. Tried on the csvtidy README: run 1 asked nothing and ended with six
     questions; run 2, with the answers, had them all in the work, and raised three finer ones.
     Writ's README example asks the license at the end (`3e514b3`), waiting for the user.
     - Found in the run, for #4: each run raises finer questions (tabs, quotes, every other tool),
       since `doc.md` B-3 (each idea given in full) and `readme.md` B-3 (over another tool) set no
       bound; the checklists' root cause, not the timing of questions.
     - Left for a trial: called from a subagent (the design's assumption); until then
       `turn/calling-from-a-plugin.md` still says to call turn from the main conversation.
  5. Decided by the user (2026-10-14): turn runs one round per call (write, read, check) and
     returns; whether to run again, or what to fix (the work, the request or a checklist), is the
     caller's to decide, since the caller knows what was agreed, and the loop of answering and
     calling again already lives with the caller. So `next` says to run again when a way lies in
     the work, and the caller calls again with the CCS returned or stops by its own judgment; the
     caller writes no loop beyond that. This changes turn's README (the plan line, "two rounds at
     most"), its design (the goal that a plugin writes no loop, "`next` gains no value", the second
     round, the learner's place), the code and tests, and the callers' page; then writ's README
     example (`3e514b3`, not yet agreed by the user) as it follows. turn's README (`b09b7be`):
     agreed by the user (2026-10-14). turn's design (`631b628`, `db63479`): agreed by the user
     (2026-10-14); `next` keeps its four values, and items left More with a way in the work come
     back with `ask the user`, for the caller to decide. turn's code, tests and callers' page meet
     them (`136bf30`, CI passes); the console no longer shows turn's file paths. writ's README
     example needs no change for it: writ already runs turn again until every item is met.
  6. Decided by the user (2026-10-14): writ questions the user before calling turn as deeply as
     mattpocock's `grilling` (behind grill-me): the decisions as a tree, asked as their
     prerequisites settle, each with a recommended answer, facts looked up rather than asked, done
     when every item of the checklists is settled. Its way is taken into writ's steps, not
     depended on, since the dependency installs 27 skills, `grilling` starts on any "grill", and
     its tags (`v1.3.1`) cannot pin a version. Decided by the user (2026-10-14): one question at a
     time, as the decision of 2026-10-13 says and as `grilling` asked up to its 2026-07-13 version
     ("Asking multiple questions at once is bewildering"), which the user has used and found
     right; its later version asks every question ready at once.
  7. Tried on the csvtidy README (2026-10-14), three calls, each answering the last one's
     questions: every call read the work once, asked nothing while it worked, started from the work
     returned, and the way in the work the second call returned was taken in the third. Each call
     raised finer questions (tabs, encodings, line endings, uneven rows) that neither deciding nor
     starting needs. The trial was run wrong as a caller: the assistant made up answers and called
     again, where judging the questions by the README's purpose would have ended at the first call.
  8. Decided by the user (2026-10-14): turn keeps its questions. The caller gives, before the call,
     what the checklists need to pass; what turn still returns, questions and items without a
     Good, the caller judges each from the purpose, settles itself what it can, asks the user only
     what the user alone can decide, and calls turn again only when that is needed, never as a
     matter of course. This is writ's steps, since everything is made through writ; turn's README
     stays as agreed.
  9. Decided by the user (2026-10-14): writ is also called from other plugins' steps, since
     everything made goes through writ. In both calls writ goes through the checklists' items for
     what the request, the repository and the sources leave open, as deeply as when it questions,
     with a recommended answer where it can infer one. Called by the user with `/writ:up`, it asks
     those points one at a time; called from a plugin's step, it asks nothing and returns them
     with their recommended answers to the caller, which decides and calls writ again. From there
     on both are the same: turn makes the work, and writ judges what turn returns.
  10. Settled by the assistant for writ's design, from the sources (2026-10-14):
      - One-dimensional: the time and tokens from the request to the finished document, and how
        many questions the user answers, each compared with the version in use; #37 is one call
        weighing about three checks.
      - What others rely on: `/writ:up` as users type it; the `writ:up` skill as other plugins'
        steps call it; the checklists' place and form in writ, which turn's README points users to
        and turn reads; a checklist writ made at `.writ/checklists/<kind>.md`, which writ finds
        again. rn 0.9.0 calls `writ:up` from an agent with instructions in words and a report file;
        rn and writ are rebuilt on turn and released together (#39), so that call is replaced
        rather than kept.
      - Non-goals: checking a work, which is turn's alone (M2); lint tools, and Claude Code choosing
        writ on its own, which the README leaves out.
  11. Then writ's design again (#3). Running (2026-10-14): `dev/turn/trials/run.py` on the CCS
      `/private/tmp/claude-501/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-writ-rebuild/ebf71383-9619-40a9-8b2c-8e0716add473/scratchpad/design.json`
      (deliverable `dev/writ/design.md`; viewpoints `doc.md`, `design.md`; sources: writ's README,
      this file, turn's README, callers' page and design, `plugin.md`, rn's `conduct.md`), in the
      clone `.../scratchpad/d1`, log `.../scratchpad/d1.log`. Next: read what it returns
      (`d1/.tasks/out.json`, `d1/dev/writ/design.md`) and its records, judge each question and
      item without a Good from the purpose as step 8 says, copy the design here, and show it to
      the user for agreement.
      - Returned (2026-10-14): one question and nine items without a Good. Settled from the purpose
        by the assistant (`2926f25`, `0924e90`, `9467341`): history words out; the subagent ground
        given with its reach; what turn returns judged from the purpose, calling turn again only
        when the document must change; writ makes every kind it has a checklist for, code and its
        tests among them (the question, settled by the code checklist the user decided), and the
        README says so; a point the purpose does not need is settled by writ as a decision given
        to turn, so every item is met; an item that still does not settle goes to the user as a
        change to its checklist (leaving it More for the user to judge was tried and withdrawn:
        it hands the judging to the user). Left as not
        needed: the form and job files in full (the specification, `design.md` U-2), and
        comparisons for each idea. Trimmed what repeats a principle or is turn's own decision.
        Agreed by the user (2026-10-14), after asking how writ and turn hand work to each other
        and what setting the decisions as a tree means (`grilling`'s "walk down each branch of
        the design tree, resolving dependencies between decisions one-by-one").

### [ ] #4: writ built and checked

Purpose: plugin.md steps 3 to 7; #36 and #37 judged against the rebuilt writ.

Serves: A1, A2, M1, M2, M3

Progress:

- plugin.md step 3 (2026-10-14): a fresh reader read writ's README and the design once.
  - Decided by the user: the README's example asks the license before writing, as writ settles
    what the checklists need before turn is called; a question that shows up only in the writing
    comes at the end.
  - Decided by the user: when an item does not settle, the change is written as an addition, only
    what it adds, at `.writ/checklists/<kind>.md`, and used with writ's checklist from then on;
    writ's own checklists are not changed in place (they are outside git on a user's machine, and
    an update replaces them). Once writ's checklist takes in the same, the two only repeat it.
  - Settled by the assistant: the wording findings (`67110ea`); the rest are the code's to settle
    unit by unit.
- Units (plugin.md step 4), in order, each through the user's whole path:
  1. Asked only what the user alone can decide, by the thinnest path: `/writ:up` with a request, the
     checklists listed, the form settled one question at a time, the CCS written from it, turn
     called, and the document handed back on `done`. The old writ's code goes first.
  2. Judged from the report: the report made from turn's evidence.
  3. Judging what turn returns: every `next`, calling turn again only when the document must
     change, and an addition to a checklist.
  4. A document the user already has: a path, and its changes git does not hold found before the
     first question.
  5. A kind writ has no checklist for: the choice, and a checklist made.
  6. Called from a calling plugin: the open points handed back, and the callers' page.
  7. Keeping writ's steps: the hooks, outside a job included.
  8. Installing with turn: the manifest, and `claude plugin validate --strict`.
- Units 1 to 8 built (`9b0ede3` to `d3e4bcd`) and tried on csvtidy (`dev/writ/trials/`): a README
  from nothing, a README the user has, release notes with a checklist made first, and a call from a
  plugin's step inside a subagent, where turn's agents ran one level deeper (turn runs from a
  subagent: `dfe6409`). Against the version in use (writ 0.2.0) on the same request: 5 answers,
  11.0 min, $4.09 here; 5 answers, 17.3 min, $4.42 and 3 answers, 26.8 min, $6.25 there.
- Decided by the user (2026-10-14): the builder judges turn's result and adds no AI check of their
  own (`dev/writ/design.md` Verification changed); a fresh agent set to check a README judged beyond
  the README's scope and disagreed with turn.
- Decided by the user (2026-10-14), on reading back the whole: writ is a thin wrapper of turn. It
  keeps the checklists, hears the user grilling-style (only what the user alone can decide, one
  question at a time, with a recommended answer, facts looked up), and judges turn's result (hand
  it back, ask the user, or run turn again when the document must change). README, design and code
  all become thin. What goes, as more than the purpose needs:
  - the form with a decision for every item, and the script that refuses a CCS until each is filled;
  - writ telling turn that the document leaves a point out, which bends turn's check;
  - the `asking` place, the Stop hook, the check that the document was not written outside turn,
    the check that turn is called with the CCS as the script wrote it, and jobs nested inside jobs;
    one hook stays: during a job, the document is written by turn alone;
  - the link to a callers' page the assistant added to the agreed README without asking.
- Next (user's instruction, 2026-10-14): make the design again from nothing as that thin wrapper,
  through `turn:up` (viewpoints `doc.md`, `design.md`); the user does not need to review it. Then
  check the README against it, rebuild the code thin from the design (the current code is not
  patched; what the design does not need is deleted), try it as its user, and finish #4 (plugin.md
  steps 5 to 7, #36 and #37 judged). Never patch; judge every point from what writ should be.
- Running (2026-10-14): the design from nothing through `dev/turn/trials/run.py`, on the CCS
  `/private/tmp/claude-501/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-writ-rebuild/5b8dfbaf-6002-4c66-aec0-eba4d5bb782f/scratchpad/design.json`
  (the thin-wrapper decisions given as constraints; the current code not a source), in the clone
  `.../scratchpad/d1` with `dev/writ/design.md` removed, log `.../scratchpad/d1.log`. Next: judge
  what it returns from the purpose, copy the design here, then the README against it.
- Seen (2026-10-14): the design's first call met 25 of 35 items, its second 33 of 35, and every
  trial of this rebuild needed a second reading. Decided by the user: turn reads the work twice by
  default; the second reading runs within the call when the first leaves only ways in the work
  (turn's README, design and callers' page `d56940e`, agreed; code `3e7dec3`, CI checks pass).
- Running (2026-10-14): the same design CCS on that turn, from nothing, in `.../scratchpad/d3`, log
  `.../scratchpad/d3.log`. Next: see that one call read the work twice, judge what it returns, then
  as above.
