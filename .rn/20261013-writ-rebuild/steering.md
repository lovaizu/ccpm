---
rn: 0.9.0
pr: https://github.com/lovaizu/ccpm/pull/61
status: running
artifact-language: English
conversation-language: Japanese
issue: https://github.com/lovaizu/ccpm/issues/54
readme: rn/README.md
design: rn/docs/design.md
verification: rn/docs/verification.md
---

# Goal

rn is rebuilt on turn (#54), with writ folded into it (#53) and the writ plugin removed: the
conductor hears what the user wants one point at a time and judges; turn makes every piece of work,
the plan, the three documents, each task's result and each proposal, and reads it in its receiver's
place; the user decides only at the sign-offs and what is theirs. rn 0.10.0 and turn 0.2.0 are
released from this pull request.

# Acceptance criteria

## Attractive quality

- A1: The user asks rn for work in rough words and gets it carried to a pull request ready to
  merge, asked only what the checklists need and their words and repository do not tell, one point
  at a time.
- A2: At each sign-off the user decides from the proposal alone: what rn decided for them first,
  then each item of the work's checklist met with the lines that give it.

## Must-be quality

- M1: Each part follows official best practice or says why it does not, and holds nothing its
  purpose does not need.
- M2: Checking a work is turn's alone; rn holds no second copy of it.
- M3: `claude plugin validate --strict` passes for rn, turn and the marketplace, and CI passes.

# Assumptions

- Fact, decided by the user: the plugin is built by `.claude/rules/plugin.md`, step by step; only the
  README and the design are agreed with the user, and the rest is built and checked without asking
  unless the README or the design should change.
- Fact, decided by the user: before the README, the user and the assistant agree on a scene of what
  the user does and what happens.
- Fact, decided by the user (2026-10-15): writ is never used without rn, so writ is folded into rn
  in this pull request and the writ plugin goes; the conductor hears and judges, turn makes every
  work and reads it in its receiver's place; the checklists live in rn.
- Fact, decided by the user (2026-10-16): rn's prompts, hooks and scripts are made through turn, not
  by hand; the caller hands turn `decisions`, what the work must say or do and leave out, and what
  the work draws on as references read in place.
- Fact, from #53 and #54: the issues each lists are judged against the rebuilt rn by running what
  each describes.

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

Order, decided by the user (2026-10-15): finish one thing at a time, #5, then #4; #6 runs beside
#5. Spreading work over turn, writ and six checklists at once left each nearly done, and a
checklist with a gap kept shaping what was made with it.

### [ ] #5: turn finished

Purpose: turn's prompts, hooks and code meet its README and design, tried as its user; what rn
builds on is settled first.

Serves: M1, M2, M3

Progress:

- Hooks done (`7e17437`, CI green): each role reads only its inputs; the orchestrator's shell runs
  only turn's script, and jq, mv and cd on the run's files.
- Prompts done (`872e13b`): each works from its inputs alone, with why; content and references in
  place of sources; the first user reads the work and `opens`; "round" for one pass.
- Flow trial (`dev/turn/trials/flow/`, two runs): write, read and check in order, one question asked
  at the end. The first run showed the generator's form had no place for an item left out until a
  question is answered, so it named lines that do not give it; fixed (`b018982`), and the second
  run named the question. In both, the orchestrator's one `cat` was stopped by the hook and it went
  on with Read.
- turn's design, made through turn (decided by the user, 2026-10-15), in the order the README's
  showed: the checklist finished first against what a design is (`90c3ab7`), then the content file
  written to answer every item of it and checked item by item before turn is called (`cdc0f68`),
  then turn. A first run on content not yet made to the checklist was stopped.
- The user (2026-10-15): their words on a design were what they want to know, not a new definition;
  the checklist's purpose, qualities and checks stand, and B-18 and B-19, decided on 2026-10-14,
  are kept (`1dcf36b`). What changed in `design.md` rests on what building turn showed: each part's
  behavior (B-14, B-27 to B-29) made a 576-line design that differed from the code in detail;
  options per choice drew questions no builder needs; "which test" drew a test inventory.
- turn's design done (`8b61d3d`, 481 lines): made through turn on the finished checklists, every
  item met but doc B-11, which the caller finished by writing the hand-offs by pair, as the content
  gave them, in place of a step table that pointed ahead. The five rules turn returned each say
  again what `doc.md` already asks; not taken.
- Next: CHANGELOG, the whole tried once, and `claude plugin validate --strict`.

### [ ] #6: Each checklist finished

Purpose: each checklist in `rn/checklists/`, once used, gives a work its reader is served by, shown
by using it once on a real work and judging the work, not only the checklist's form.

Serves: M1

Progress:

- How (decided by the user, 2026-10-15): all six at once, beside #5, each by a one-off Claude Code
  on Fable in its own clone: an Opus subagent makes a real work with the checklist, Fable judges the
  work as its reader and fixes the checklist at the cause, against `checklist.md`. Each changes only
  its own checklist and reports what it finds in `doc.md` or `checklist.md`. The assistant checks
  each report against the work and the records and brings the change in; the user is not shown the
  wording, since `checklist.md` is the measure for it.
- Findings so far, each to its checklist (from #4's 6 and 8):
  - design: B-14 and B-27 to B-29 (what each part does, when it acts, what it looks at) push the
    design toward a specification, against U-2; U-2 and U-3 are titled by what is absent, not by
    what the reader gets; B-16 and B-30 had turn ask five questions a builder does not need.
  - doc: B-16 had turn add a six-step list repeating the console sample.
  - code: no item pushed unneeded work (turn's code and hooks).
- First: `design.md`, since the turn and writ designs are made with it.
- Done: `doc.md` (`f4ee97b`, on turn's callers' page) and `readme.md` (`7fbbfcc`, on turn's
  README), each claim checked against the works and records. Their reports' findings for `doc.md`
  and `checklist.md` wait for the other four: doc B-10 asks a reference page what it cannot say;
  doc B-11 reads the wrong way for a thing shown; doc B-16 reads as asking for a figure;
  `checklist.md` F-5 and F-6 do not say how a new or renamed checklist finds its last release, and
  nothing asks that a Look-for be checked against every candidate. The content files of turn's
  README and callers' page each hold a gap the workers worked around.
- Done: `prompt.md` (`f4b7e07`, on turn's first user; turn's own first user kept, since it passed
  both flow runs) and `checklist.md` (`152c470`, on release notes), with a new B-8: each item named
  by what it gives; the names in `checklist.md`, `doc.md`, `prompt.md` and `readme.md` that said what
  is absent are renamed; `design.md` and `code.md` wait for their workers.
- `design.md`: the first worker's result is not taken. It judged the work by the checklist's own
  opening, which asks for each part's when and what it looks at, so it added items and left a
  513-line design that reads as a specification. The user's words (2026-10-15) are the measure: a
  design holds the approach, the way of thinking, and who takes part with their roles and
  dependencies, to bring about the UX the README promises; it is not a specification. The cause,
  the opening and B-14, B-27 to B-29 asking each part's behavior, is fixed first by the assistant
  (`8555dcb`); a worker then tries the changed checklist, judged by those words. A worker is never
  run again on an unchanged checklist and input, since that only hopes for a different result.

Where to resume (2026-10-15), before anything else in #5 and #6:

- Found with the user: every work made through turn grows noise (an opening that describes the
  document, a glossary ahead of the content, bold on every item, a comparison for every idea, tables
  where a figure was needed). The cause is the checklists, not turn. On 2026-10-13 (`4aa3887`) the
  user decided that a checklist says only what a good work gives its reader, not how it is tried;
  the assistant, moving the 10/06 questions over, turned them into conditions on what is written
  ("the opening says what it covers") and dropped the one that found excess ("which parts did you
  skip"). Since then every finding was answered by adding an item, never by removing (design 19 to
  36 items, doc 15 to 21), and turn, which meets every item and looks only for Goods, writes each
  item in, noise included.
- Decided by the user: a checklist is its document's purpose, written as conditions. Its opening
  says the purpose in one or two sentences (who reads, what they can then do); each item is one
  condition of that purpose, said as what the reader gets, never as what is written; nothing in it
  makes the work grow beyond the purpose.
- Next, one checklist at a time, starting with `doc.md`: agree its opening, the purpose, with the
  user; then judge every item of the latest version against it: keep a condition on what the reader
  gets, say again as one a condition on what is written, remove one that only adds text; the 10/06
  version (`6cc61d5`, `writ/references/essentials/`) serves only to find conditions that were
  dropped, such as nothing the reader would skip. Decisions the user made since 10/13 stay. Then
  make the README and the design with it and see that no noise comes out. Today's additions (doc
  B-12 on terms, B-16 on a figure, F-1 on lists; design B-32 on a figure) are judged the same way.
- `doc.md` done against its purpose, agreed with the user (2026-10-15): one reader, one use, the
  picture taken in by one reading and acted on without asking, no effort beyond the subject. Kept
  as conditions of it; B-1 and B-8 (an opening that tells what is covered) folded into B-9, the
  point from the opening; B-10 into B-5; U-4 into B-4, which takes back the 10/06 question on
  parts skipped or read twice; B-15 (a comparison for each idea) removed.
- `readme.md` done the same way (2026-10-15): someone meeting the product decides from the README
  alone whether it is for them and, if so, gets to their first result. B-6 (where to go for more)
  removed as beyond that purpose, the Documentation heading kept as the place READMEs give it; U-4
  removed, since `doc.md` B-11 asks it; the opening says the example answers `doc.md` B-16.
- `design.md` done the same way (2026-10-15): its purpose names, as the user asked, the principles,
  the approach to each promise and the structure in one figure (who takes part, each role, what each
  depends on). B-17 to B-19 (how checks are cut) removed, since `plugin.md` already rules them;
  B-21 removed, since what must keep holding (B-4) leaves the rest free; B-16 folded into B-31, so
  no approach is made to list options when none was weighed; the template's opening gives the main
  point, not what the document covers. Next: the README and a design made with the three and read
  for noise.
- Every checklist's opening agreed with the user, one at a time (2026-10-15): who reads it, for what
  purpose, and what they then do, in the reader's actions rather than the work's parts; the opening
  steers the maker, as the 513-line design made on the old design opening showed. Items judged
  against each: no change in prompt, code or design beyond those above; checklist B-3 looks for an
  item met by writing something in. The design template meets Structure before Principles, with
  Goals in the README's words, since turn's design opened on a glossary to name its roles first.
- Raised by the user, to settle in #5 with turn's README and design: turn takes one file per run
  (`turn/scripts/ccs.py:53`), while a purpose often needs several, such as code and its tests;
  the unit should be the purpose.
- All six tried at once on real works through turn (`dev/turn/trials/*.json`,
  `dev/writ/trials/release-notes-checklist.json`), each work read whole and checked against what
  it rests on: no opening about itself, glossary, bold or table in place of a figure in any;
  turn's design names its parts first in the figure. `doc.md` B-4 found the callers' page's
  restated analogy. `readme.md` now says its example answers `doc.md` B-16, since the README run
  was held unmet for want of a figure that would repeat the example.
- Every wrong fact in the works came from content files written without checking each statement
  against what it rests on, turn's code or the rules: the callers' page says `to the caller`
  answers a CCS that cannot be run, which `turn/scripts/lifecycle.py:38-40` stops without writing
  (the page on this branch says it too, `turn/calling-from-a-plugin.md:133`); "the item's ID" made
  the questions script stop only `doc B-2`, not `B-2`. turn follows its content by design, so the
  caller checks each statement before calling.
- Next, agreed with the user (2026-10-15), back in #5: fix the callers' page's `to the caller`
  against `turn/scripts/lifecycle.py`; bring to the user, as a change to turn's README and design,
  the unit of a run as a purpose with one or more files; bring the design run's question, whether
  `.turn/` is a path kept from 0.2.0 on; then remake turn's design from content checked statement
  by statement against what it rests on.
- `to the caller` fixed (`89d9c1f`): it comes only with a work written; a CCS that cannot be run
  stops before any work.
- Decided by the user (2026-10-15): a run's unit is one purpose with one or more files, such as code
  and its tests, written, read and checked together; the git check and where each file goes are per
  file. turn's README says so; the design takes it when remade, and the code after.
- Decided by the user (2026-10-15): `.turn/` is kept as the place of a run's evidence from 0.2.0
  on, since the README names it; its layout inside may change. The design's content says so.
- The design's content checked statement by statement against turn's code and records (about 200
  statements). The design says how turn should be, so only facts it rests on, such as what a trial
  showed, are fixed from the records; where the code differs, the code is fixed after the design,
  not the design bent to it (a first pass did bend it, and was undone). Put in: a run's unit as one
  purpose with one or more files, and the caller's constraints among the inputs. The code falls
  short in: nothing stops the work changing after its reading
  (`turn/hooks/checks/write_in_run.py:24-27`); the work is copied to where it goes before a second
  round (`turn/scripts/lifecycle.py:119-120`), so a run stopped there leaves the first round's work;
  the first user's shell is open, so it can read what the receiver would not open; a file where the
  work goes is written over when any copy in `.turn/` matches (`turn/scripts/lifecycle.py:17-25`),
  wider than the callers' page; several hooks' stops name no step or reason; no test for a run cut
  off, python3 missing in a run, jq missing outside one, or a returned CCS whose caller part
  differs.
- turn's design at `8b61d3d` reads badly (no figure, bold everywhere, a glossary, an opening about
  itself); it is made again once the checklists are done.
- Seen by the user (2026-10-15): turn's README opens on "turn is a plugin for Claude Code.", a
  sentence that gives the reader nothing; its cause is `readme.md` B-8 (what it is) and U-5 (what
  it is before what they gain), which make "what it is" a sentence of its own. The README was
  made before the checklists were finished, so it is made again with them, and the design after
  it, as `plugin.md` orders; a design run started on the old README was stopped.
- Order, decided by the user (2026-10-15), replacing the one above:
  1. #6: finish the checklists: `readme.md` B-8 and U-5 so that what the product is comes inside
     what the reader gains, never as its own sentence; then the findings held for `doc.md` and
     `checklist.md` above.
  2. #5: turn's README made again through turn with the finished checklists, agreed with the user;
     then its design, agreed with the user; then its code (a run as one purpose with one or more
     files; the shortfalls listed above), each unit tried as its user on the small flow trial
     (`dev/turn/trials/flow/`), and the whole tried once on a real work; then CHANGELOG and
     `claude plugin validate --strict`.
  3. #4: writ the same way, README first, since its README and design were agreed before the
     checklists were finished.
- #6 done by the assistant by hand (2026-10-15), each item judged against its checklist's opening,
  with `checklist.md` B-3 as the measure: `readme.md` B-8 and U-5 removed, B-1 says the gain with
  the kind of thing that gives it; `doc.md` B-16 asks only where several act in turn, B-5 only that
  what is not a checked fact says so, B-11 and B-12 take a thing shown in an example or a figure as
  met; `design.md` B-15 (what must always hold), B-20 (who relies, now in B-4's words) and B-30
  (what each approach costs) removed as "each X with Y" items the purpose does not need, B-24 said as
  what the reader can then do; `code.md` B-27 and B-28 removed as cases B-26 and B-25 settle;
  `checklist.md` B-3 looks for an item that asks of every deliverable a part only some need, F-5
  and F-6 say which release counts. `prompt.md` unchanged. Next: #5, turn's README through turn on
  Opus (the user, 2026-10-15: trials on Opus 5.5 only; the work and the judging here).
- Instruction from the user (2026-10-15): build turn and writ through, judging from the purpose
  and from what each should be, and bring every decision made on the way to the user at the end,
  who then judges. Decisions made so far, to report:
  1. turn's README keeps the Esc line, which the first user skimmed: it is the one thing the user
     can do while turn works, and the agreed README had it.
  2. writ's README keeps only the one example; a document the user already has, and a kind writ has
     no checklist for, go to `writ/beyond-the-first-document.md`, reached from Documentation,
     since `readme.md` keeps the README to deciding and starting (turn raised it as a question);
     the line that a question found in the writing comes at the end stays, as part of the shown
     run. The callers' page stays and is reached from that page, since the user had the link
     taken out of the README, not the page.
  3. `checklist.md`'s opening says `doc.md` applies to a checklist, so a checklist writ makes is
     made against both, as the release-notes trial did.
  4. writ holds no hooks and keeps nothing between calls: four scripts (`checklists`, `content`,
     `task`, `report`) and `tools.sh`; a calling step gets back `{"next": "decide", "open": [...]}`
     or `{"next": "done", "document": [...], "report": "..."}` at its `out` file, and brings its
     answers in the request's words. The report is written by a script from turn's evidence and a
     judgments file writ writes, which must judge every question and item turn returned.
  5. turn's code (by a fork of this session): the work's files at `.turn/<run>/work/<path>`;
     `lines` and `reach` as `<path>:<ranges>` with several files; the work reaches its place only
     when the run returns; a write to the work after the reading is stopped; the first user's
     shell stays open, as the design says of the agents' shell.
  6. The trial harnesses run on a snapshot of the plugins: the turn design trial broke halfway
     when the fork changed the scripts under it (`.turn/.../work/` moved), and is run again.
  7. The console lines turn's orchestrator writes come out in Japanese in trials, since the clone
     runs under the user's global CLAUDE.md; left as is, since the user's conversations do too.
- turn's code tried on the flow task (2026-10-15, Opus, $1.40, one round): the work made at
  `.turn/flow/work/csvtidy/README.md`, placed at `csvtidy/README.md` on return, 4 of 5 met, the
  license left as a question with `ask the user`, an unmet with its way, a rule, and the evidence
  paths; every hook let the run through.
- writ tried as its user on the csvtidy README (2026-10-15, Opus): 3 answers, 6.7 min, $2.34
  (writ 0.2.0 on the same request: 5 answers, 17.3 min, $4.42). One turn run, four agents, so
  #37's three pith runs are gone; no hook stops a read of saved tool output, and turn's lets it
  through by test, so #36 is gone. writ asked who reads it (the notes read as internal, no remote),
  the license, and what to do about the tool overwriting `.orig.csv` on a second run, which it
  found by running the tool; the user chose to have the code fixed first, and writ fixed it and
  wrote a LICENSE at the user's word. Found: `up.py task` kept only the last `--checklist` flag, so
  turn checked `readme.md` alone; fixed (`4709b03`), and the report now says its lines are as turn
  read the document when writ changed it after. To the user: whether writ should offer to change
  the user's code while making a document (it recommended documenting the behavior instead).
- turn's design through turn on the rebuilt turn and the finished checklists (2026-10-15, Opus,
  $8.90, two rounds in one run, 40 of 41 met, no question): no glossary section, no bold, no
  table; the structure is one sequence figure with each part's role and what it needs in its
  label; the opening defines the caller, a run, the work, a checklist, the list and the inputs in
  one paragraph, since Goals use them before the figure. The one unmet, how "Nothing unread" comes
  about under making again, finished by hand from the content (`b28805e`). The first design run
  had broken halfway on the fork's change to the scripts ($5 lost), the writ design run too
  ($10.25, four questions on the content, taken in: writ's own changes come after turn's last run;
  turn's outcomes as its page says; each ground marked by how far it was checked).
- writ on the csvtidy README again, with both checklists handed to turn (2026-10-15): 4 answers,
  22.9 min, $6.57; the install question came only after the first turn run, so turn ran twice.
  Every item of both checklists met. writ offered to delete `.turn/` and `.writ/` at the end,
  which no step asks.
- Decided by the user (2026-10-15): writ is never used without rn, so writ is folded into rn in
  this pull request: the conductor hears (one point at a time, intent before means, facts looked
  up) and judges; turn makes every work, the plan, the three documents, each task's result, the
  deliverable's use and each proposal, and reads it in its receiver's place; questions are the
  conductor's and are not made by turn; after turn, a small shortfall the conductor fixes itself,
  and only a large change to the content runs turn again; `/rn:on` folds into `/rn:up`; trials
  secure the attractive quality on rn-try and tests the must-be quality. The writ plugin goes.
  Decisions made on the way, to report:
  8. `/rn:dn` stays: a task under way is turn at work, which `/rn:dn` stops with Esc so its work
     stays in turn's evidence; the record keeps 0.9.0's form, so a 0.9.0 session is taken up as it
     stands.
  9. The plan, `steering.md`, is made by turn at the Plan sign-off from its content, which the
     conductor writes point by point as agreed; between sign-offs the conductor edits only the
     record's machine parts (`[x]`, `status`, `pr`).
  10. The verification document is itself a checklist: front matter `name: verification`, each
      scene a `### A1:` item, so the deliverable is used by turn against it; turn accepts `A1` as
      an item ID beside `A-1`. turn's first user sees each scene's pass, as it sees every item;
      rn's rule that the first user never sees the pass is given up with rn's own first user.
  11. Three checklists added to rn: `plan`, `proposal`, `verification`; the proposal puts first what
      rn decided for the user and lists the checklist items met, in place of every Good and More of
      every use (#46).
  12. The content of each work lives at `.rn/{session}/content/`, the tasks at
      `.rn/{session}/tasks/`, both committed; turn's `.turn/` is left uncommitted. The user's own
      checklists at `.rn/checklists/<kind>.md`.
  13. rn's hooks keep checks 1–9 and 12–14; the first-user checks go with rn's first user; the
      proposal check asks for the `Toward` lines per attractive criterion and the `Decided for you`
      heading.
  14. The README keeps `/rn:gm` in the example once; `/rn:dn`, resuming, feedback from the pull
      request and what a session leaves go to `rn/during-a-session.md`.
  15. rn 0.10.0 (a breaking change on 0.x), released with turn 0.2.0 from this pull request; writ's
      marketplace entry removed, writ 0.2.0 stays installed where it is.
  16. Decided by the user (2026-10-16): rn's prompts, hooks and scripts are made through turn too,
      not by hand; a `hook` checklist added for the hooks, beside `code`; the checklists grow with
      each kind of work rn makes.
  17. A More from the deliverable's use becomes a task checked on the real thing against its scene;
      turn checks no item alone.
  18. The practice repository's `main` put back to `c3b5f8e`, its later state kept as the tag
      `team-plugins-2026-10-07`, and the branch of the closed pull request #79 deleted.
  19. Decided by the user (2026-10-16): rn does nothing with the rules turn returns as they come;
      before the Deliverable sign-off it takes stock of every rule the session's runs returned and,
      one at a time, agrees with the user what to do with each, an item for `.rn/checklists/<kind>.md`,
      an issue, or letting it go.
  20. Decided by the user (2026-10-16): the caller hands turn `decisions` (was `content`): what it
      decided the work must say or do and leave out, item by item, holding nothing a reference
      holds; what the work draws on, the plan, the design, code, a document already there, is
      handed as a reference and read by turn where it stands, since a copy drifts from its source
      (the cause of most of the questions turn returned on 2026-10-16). In rn, `up.py decisions`,
      `--decisions`, `.rn/{session}/decisions/`.
  21. Decided by the user (2026-10-16): a checklist's Format comes first, the shape the maker takes
      before writing, and the items of Benefit and Usability stand in the order the maker meets
      them writing from the top, those over the whole last (`checklist.md` F-1, U-5); turn's
      generator takes the shape, writes part by part in that order, then goes through the items
      over the whole one at a time, then reads once as the receiver; the learner returns a rule
      only where no item of the list asks it.
- rn's README through turn (2026-10-16, Opus, $5.42, two rounds, 27 of 27, no question): read whole
  as a newcomer; the orchestrator held 11 items the evaluator left (the opening's length, resuming
  said in several places); one repeat of resuming cut and the opening split by hand (`487363c`).
  The three rules turn returned apply `doc.md` B-12, U-1 and F-1; no checklist change.
- rn's design through turn (2026-10-16, $9.46, two rounds, two questions and three wordings left):
  finished by hand (`d39f281`): the default branch gets a hook check, missing tools their approach
  under the commands, what is handed to turn is the CCS and a task stays the plan's, what turn
  writes back said in the callers' page's words with Good and More as the conductor's names.
- rn's scripts and their tests through turn (2026-10-16, $14.13, two rounds, 36 tests, 23 of 29
  met): the six waiting on CI and the type checker, which the repository already holds, and on
  three stops without what to do, added by hand with the content; one test in 3.10's grammar made
  3.9's (`f39f8d3`). `dev/check.sh` passes, 121 tests, every line and branch.
- rn's prompts through turn (2026-10-16, $13.74, seven questions): settled in the content and run
  again: the branch is the slug as 0.9.0's fixtures have it; a More's decision on its own line
  under it, as the hooks read it; the kinds `plan`, `readme`, `design`, `verification`,
  `proposal`, `code`, `doc`, the deliverable's use against the verification document; feedback
  settled in its own commit before the stop commit; sessions from 0.9.0 on taken up as they
  stand; `upgrade.md` for older ones.
- rn's verification document through turn twice (2026-10-16, $5.56 and $5.98, seven questions
  each): the content had departed from the design and the fixtures; settled: the scenes live in the
  verification document and the design points there and says only what each passes on; the flow
  session runs on the practice repository (one line in its README); A3 from fixture
  `account-ready` to the plan's proposal; A4 passes on the task carried to its decision line, not
  on a comparison; the trial closes the pull request and deletes the branch, nothing put back since
  rn never changes `main`; the document's version is its own, 0.1.0. Run a third time.
- rn's hooks through turn: the first run was cut off at the harness's one-hour limit while the
  generator made its second pass; the limit is now four hours and the run goes again.
- Found with the user (2026-10-16), on why a hooks run took hours: what was carried from 0.9.0
  or patched instead of judged from what it should be, and the fix for each:
  - the hooks' tests made a git repository per test (0.9.0's harness, copied into the content):
    each check is now a function of values with tests in milliseconds, the repository read in
    `record.py` alone;
  - `code.md` B-9 read as "remove each line and run the tests", which the generator did for 2,400
    lines until the shell's limit: B-9 now matches each line to a test's behavior statically;
  - the hooks list copied from 0.9.0: judged one by one; `conductor_only_git` goes (turn's own
    hook stops its agents), `typed_command` reads the user's last prompt from the transcript
    instead of a side file; one unit per quality the hooks protect, three in all;
  - turn's work folder was a partial tree, so the caller had to say "copy X beside the work to run
    the tests": the work is now made in a working copy of the repository (a git worktree per run);
  - the report's note that lines may have moved: the lines are mapped through the diff of the
    document as turn kept it and as it stands;
  - the harness's limit moved 1 → 4 → 2 hours: fixed at two as a guard against a stuck run, with
    its reason beside it;
  - the verification scenes and fixtures copied from 0.9.0: the scenes are derived from the
    design's qualities, and fixtures are made from this version's runs.
  Decided by the user (2026-10-16): the design checklist asks for goals, verification, one static
  figure of who is responsible for what and what each depends on, and principles; the approach
  sections (B-13, B-31) go, since they grew into specification; the figure shows responsibilities,
  not a sequence. `design.md` 0.3.0 rewritten so; both design contents reshaped to it.
- Where to resume (2026-10-16, before a `/clear`): four turn runs were going in the scratchpad
  `/private/tmp/claude-501/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-writ-rebuild/fec3f6a4-1caa-4408-b639-3e5fab7753f7/scratchpad/`,
  each with its log beside it: `p4` (rn's prompts, `dev/rn/trials/rn-prompts.json`), `nd4` (rn's
  design), `d5` (turn's design), `hf3` (rn's hooks, first unit, with the five points settled).
  Judge each from its `<folder>/.tasks/<name>.json` and the work in the folder, by the purpose;
  finish small shortfalls by hand, correct the content and run again for large ones; take the
  files in and commit. Then the second and third hooks units (`rn-hooks-commits.json`,
  `rn-hooks-course.json`, each after the one before is taken in), the verification document
  (`rn-verification.json`, after rn's design), the trials on rn-try (`dev/rn/trials/flow.py
  --out <new folder>` first), CHANGELOG versions, the final check, and the report of every
  decision above. The hand-made hooks of the fork are gone; until units two and three land, rn's
  hooks check only the record's form.
- rn's prompts taken in from `p4` (2026-10-16, Opus, $15.45, two rounds, 33 of 40 met, three
  questions): the seven files copied in, the questions settled from the sources and the seven
  unmet finished by hand, each a small change: the feedback item is settled in a commit of its own
  before the stop commit (the content's Feedback line was stale, fixed); a More from the
  deliverable's use becomes a task checked on the real thing against its scene, no item checked
  alone by turn (decision 17, to report); a settled item is indented by four spaces, as the
  record's example already showed; the proposal's content is written before the reports it draws
  on are settled; taking up a session that waits for a sign-off stops at it again with the
  proposal made anew; `<pr>`, the intent and means question, the criteria IDs and the golden path
  said where first met; where Mores contradict, the undecided point is asked where it is the
  user's. The 13 rules turn returned each apply an item that exists (doc B-7, B-11, B-12, B-13,
  prompt B-12, B-20, F-2); none taken.
- turn's design taken in from `d5` (2026-10-16, Opus, $7.95, two rounds, 351 lines, 34 of 41 met,
  one question): the one question, what writ is, came from the content naming writ, which this
  pull request folds into rn; the content and the design now say rn, a plugin built on turn. The
  six unmet finished by hand, each small: the orchestrator said as the skill and the caller's
  parts said in the opening; the second round read and decided again; "form" kept for the
  checklist and the CCS, a role's answer called its answer file; the user's arrows to the caller,
  the console and `.turn/` in the figure; the pointer to the README and the line on the README's
  words taken out; the shell command's side effect said under the last principle. The eight rules
  each apply an item that exists (doc B-3, B-7, B-11, B-12, B-14, design B-12); none taken.
- rn's design from `nd4` (2026-10-16, Opus, $9.35, two rounds, 367 lines, 27 of 41 met, three
  questions) taken in for now (`801ce7e`): the questions settled in the content, More as the one
  word for what falls short, since the record's commits use Good and More; `tasks/` said by what
  it holds; the hooks' need of the record drawn; the version in use named by its role. The block
  of fifteen words ahead of Goals, which turn made from the content's "Every term known" entries
  and which eight of the unmet items trace to, is a large change in the work, so the task gets a
  rule, each word said where it is first used, and turn runs again as `nd5`; the verification
  document runs beside it as `v6`, both in this session's scratchpad
  `/private/tmp/claude-501/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-writ-rebuild/2b5caff4-d0fc-4a9b-83a0-22f95dbc4db8/scratchpad/`,
  logs beside them. `hf3` is still going in the earlier scratchpad.
- rn's design taken in from `nd5` (2026-10-16, Opus, $9.24, two rounds, 405 lines, one question):
  the block of words is gone, but the run moved the README's words (plan, design, deliverable,
  sign-offs, the Kano citation) into one explanation under the last attractive quality, since the
  generator is not handed the README; cut by hand, Good and More kept there. The four unmet items
  (whole ideas, terms, one account, fewest words) are finished by hand with it. The sessions are
  named sessions, not trials, as the verification document names them.
- rn's verification document taken in from `v6` (2026-10-16, Opus, $6.66, two rounds, 180 lines,
  five questions): settled from the sources and finished by hand: the scenes live in the
  verification document and the design's Verification says only what each passes on and points
  there (the design and its content brought to the decision of 2026-10-16, which they had not
  taken); A5's "it" is turn's first user, using the flow session's deliverable as the product's
  user; the stand-in's parts and how rn and turn reach the clone said as the trials do; the start
  given as commands to see and to bring back; each pass said as the decision line the records
  hold. The rules of both runs each apply an item that exists; none taken.
- The practice repository's start (2026-10-16): `main` of `lovaizu/rn-try` held `1fdec5b`, "Start:
  the team's plugins", a README alone, set on 2026-10-07 for turn's earlier trials, and the branch
  `20261009-pr-intent-rules` of the closed pull request #79 was left. Decision 18, to report: that
  `main` is kept as the tag `team-plugins-2026-10-07`, `main` is put back to `c3b5f8e`, the shop
  app the verification document and the fixtures rest on, and the branch is deleted, as the
  verification document says of a start left otherwise. The flow trial runs as `flow1` in this
  session's scratchpad, on rn with the hooks' first unit alone, to try the prompts and the scripts
  end to end while the hooks' other units are made.
- rn's hooks, first unit, from `hf3` (2026-10-16, Opus, $18.75, two rounds, two questions, three
  unmet) not taken: both questions are the guard without python3, settled in the content from the
  design (outside a session the hooks do nothing; a stop never holds the AI): the `sh` guard stops
  only where a running session's plan is in the working tree, and at the end of the turn once,
  letting the second pass, marked `stop_hook_active`, end the turn. Run again as `hf4` in this
  session's scratchpad.
- Decided by the user (2026-10-16), on the rules turn returns: rn does nothing with them as they
  come; at the end of its work it takes stock of every rule the session's runs returned and, one
  at a time, agrees with the user what to do with each and whether to open an issue for it. To
  put into rn's design and prompts (the conductor's steps before the Deliverable sign-off) and
  into the record. Seen on the way: of the rules returned today, one was a real learning for
  turn's generator, that a content entry listing terms is a meaning to say where each is first
  used and not a block to copy; the rest said checklist items again.
- Decisions 20 and 21 built (`4280354`, `339f36c`): the checklists reordered, `content` renamed to
  `decisions` in turn and rn (code, tests, CCS files, `.writ/decisions/`), turn's generator and
  learner rewritten, rn's conduct.md step 4 (Writing the decisions), step 5's flags and step 12's
  stock-taking written by hand, the designs and decisions files of both brought along. Tried first
  on turn's own design as `d6` in this session's scratchpad. Seen in the flow trial (`flow1`,
  08:16): rn put to the stand-in whether a one-line change should get the three documents in
  `docs/`, and the stand-in chose to keep them in the session's folder; to judge from the whole
  transcript when the trial ends.
- Where to resume (2026-10-16, before a `/clear`): three runs are going in this session's
  scratchpad
  `/private/tmp/claude-501/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-writ-rebuild/2b5caff4-d0fc-4a9b-83a0-22f95dbc4db8/scratchpad/`,
  each with its log beside it (a run is alive while `pgrep -f "run.py <folder> "` finds it, and
  done when `<folder>/.tasks/<name>.json` exists):
  1. `d6`, turn's own design on the new generator and the decisions
     (`dev/turn/trials/turn-design.json`): judge by the purpose and compare its first round with
     `d5`'s (34 of 41 after two rounds): whether fewer items on terms, names and repeats come back
     unmet; finish small shortfalls by hand, take `dev/turn/design.md` in and commit.
  2. `hf4`, rn's hooks' first unit (`dev/rn/trials/rn-hooks-form.json`, started before the rename,
     so its CCS says `content`): judge, take the eleven files in, run
     `sh dev/check.sh` (tools in this scratchpad's `venv/bin`, or make one from
     `dev/requirements.txt`), commit; then the second and third units
     (`rn-hooks-commits.json`, `rn-hooks-course.json`, one after the other, each with
     `python3 dev/turn/trials/run.py <new folder> <CCS> <out name>`).
  3. `flow1`, the flow trial on rn-try (`flow1/transcript.md`, the clone in `flow1/work`): read
     the whole transcript and the clone's commits when it ends, judge by the design's
     Verification (the flow session passes when the last decision line is `── approved →
     finished` and no hook stopped a call), and note what the prompts should be; it ran on the rn
     before the rename and the stock-taking step. If it is still going at resume, leave it.
  Then: rn's prompts and design are changed by hand already for decisions 19 to 21; the remaining
  trials on rn-try (`a1_first_call`, `a1_feedback`, `a2_intent`, `a3_proposal`, `a4_resume`,
  `a4_from_080`, one at a time, each `--out <new folder>`, with fixtures remade where a scene's
  premise differs); rn 0.10.0 and turn 0.2.0 in the CHANGELOGs (turn's names `decisions`, the
  checklist order, the generator's order; rn's the stock-taking, `decisions/`); `claude plugin
  validate --strict`; the final check; then the report of decisions 1 to 21 to the user.
- CHANGELOGs (2026-10-16, `32ff4b0`): turn's generator order and rule condition, rn's stock-taking
  and checklist order added under `[Unreleased]`; versions wait for the release. `claude plugin
  validate --strict` passes on rn, turn and the marketplace.
- rn's hooks, first unit, taken in from `hf4` (2026-10-16, Opus, $20.34, two rounds, 37 of 38 met,
  one question turn settled itself from record.md: the hooks fetch nothing, since the conductor
  fetches as each session starts): the eleven files replace the earlier run's (`b03e46f`); sessions
  found with `git diff base HEAD` as record.md says; the guard as the user settled it. The one unmet,
  code B-21, finished by hand: thirteen comments and docstrings that said what the code beside them
  says now give the reason or are gone (`a1b9397`; `dev/check.sh` passes, every line and branch;
  CI green). The seven rules each apply an item that exists (code B-3, B-6, B-9, B-22, B-4, B-29,
  B-21); none taken.
  The second unit runs as `hc1` in this session's scratchpad
  `/private/tmp/claude-501/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-writ-rebuild/739e9824-08e7-4ea5-b189-7ac3c92712c3/scratchpad/`,
  log beside it; `d6` and `flow1` still go in the earlier one.
- turn's design taken in from `d6` (2026-10-16, Opus, $8.06, two rounds, 388 lines, 39 of 41 met,
  no question): the two unmet, doc B-3 and B-12, are one point, "version in use" used before it is
  said, finished by hand at its first use. Against `d5` (34 of 41 after two rounds): the first round
  left 8 of the orchestrator's 36 items where `d5` left 6, the same kinds (terms, names, repeats),
  so the generator's order (decision 21) showed no gain in the first round; the second round
  converged further (2 left where `d5` left 7). The one rule, a term the decisions list for the
  receiver is told only where the receiver does not already hold it, is a generator learning, for
  the stock-taking. Judged as the receiver: the orchestrator's loop with the generator and the
  second round read as the decisions say; nothing added beyond them.
- The flow trial `flow1` on rn-try (2026-10-16, Opus, 07:46 to 09:45, PR rn-try#80, 69 commits,
  17 turn runs, the rn before the rename and the stock-taking step): the session ran from
  `/rn:up` to `── approved → finished` through the Plan, Design and Deliverable sign-offs,
  feedback on the Deliverable, a second Design sign-off and a task. Read from the JSONL:
  - The Stop hook stopped the conductor three times (00:06:41, 00:06:58, 00:33:47 UTC), each
    "no task serves A1/A2", each when the conductor ended its turn to ask the user about that
    very criterion; blocked from ending the turn, it decided the user's point itself (took A1 out
    at 09:07 JST, "前の質問にはまだお答えをいただいていませんが"; added task #6 at 09:34), and the
    question it had written never reached the user. The cause is in the trace check as the
    decisions file gives it: "once tasks beyond the sign-offs are planned, every criterion has a
    task", held at every end of a turn, with nothing for a criterion the conductor is asking the
    user about. What it should be, from the design (the conductor asks, the user decides; a stop
    never holds the AI): a criterion served by an open question item counts as held, or the check
    runs at the sign-off commit, not at every turn's end. To settle with the hooks' units, before
    the a1 to a4 trials, since each would meet the same stop.
  - The conductor put rn's inside to the user twice: where the notice list is kept (08:14, a means
    the user had not asked for) and whether the three documents take rn's form (08:16, the user
    chose the session folder); the second is the design's "unless you agree another place" said
    in rn's words, to judge with the prompts.
  - Time: about two hours for a one-line README change and a two-line notice; each turn run 4 to
    12 minutes, each proposal through turn about 10; the one-dimensional quality is measured
    against 0.9.0 on the same session once a 0.9.0 run of it exists.
  - Every hook let every other call through; the python3 guard was the earlier one.
- Decided by the user (2026-10-16), from the figures of both designs and feedback from another
  product's design made against `design.md` 0.3.0 (a figure of thirteen boxes with sentences
  inside, read as unreadable; the version that passed: one sentence of how the product divides, a
  figure of names with the relation on each arrow, a table of each part's kind, place and where it
  runs): Structure is the placement of responsibilities, the physical and the logical, and it
  covers the goals; a goal brought about by a mechanism inside one part is given that part's name
  alone. `design.md` changed so (`d0bc5d0`, `46995b9`): F-1's Structure template, B-12 (who does
  what to what, from the arrows), B-34 to B-36 (kind, where kept, where it runs), B-33 (each goal's
  parts by name), U-2 (where a part is kept is a decision). Both designs' decisions files
  reshaped to it (`454441b`, `46995b9`), and both designs run again as `td7` and `rd6` in this
  session's scratchpad. Decision 22, to report.
- Decided by the user (2026-10-16): the design's order is Goals, Structure, Verification,
  Principles, since the checks on must-be quality and compatibility name parts, which the reader
  first meets in the figure; and Verification holds only how each kind of quality is checked and
  where the checks are: the scenes are the verification document's (`rn/docs/verification.md` for
  rn, `dev/turn/trials/` for turn) and the cases the tests'. The section keeps the name
  Verification, since attractive quality is checked by use, not by a test. Drafted in the working
  tree, uncommitted, until the discussion below ends: `design.md` (F-1, B-7 to B-10, the opening),
  both decisions files (B-7 to B-10); `td7` and `rd6` stopped and removed. Decision 23, to report.
- Decided by the user (2026-10-16), on the design document's shape: the design is the least,
  core and unchanging layer between the README and the code, not a full account; without it the
  code would answer to the UX alone and nothing would hold. It has four sections, each the ground
  of the next activity and read against the one before: Goals (what the UX needs, one sentence
  each), Design decisions (what must hold toward the goals, one sentence each, the intent nested
  under it; non-goals and constraints stand here), Structure (the placement of responsibilities,
  physical and logical, as one static figure of names and labelled arrows and a table; a goal or
  decision held inside one part gets one sentence under the figure, naming the part and what it
  holds, never how), Verification (how each kind of quality is checked and where). Nothing obvious
  goes in: each decision says what the goals would lose the other way. The structure stays even
  so, since without it the builder is free to place anything anywhere. Principles renamed Design
  decisions. Decision 23, to report (replaces the order Goals, Structure, Verification,
  Principles).
- Decided by the user (2026-10-16), on the design checklist: written again from the user's own
  picture of the design document, not from the earlier checklist: Goals, what the README's use
  needs, one-sentence items covering it; Design decisions, what must hold toward the goals with
  its intent nested, covering the goals; Structure, the placement of responsibilities, physical
  and logical, as a static figure of parts and dependencies, covering the goals and decisions by
  placement or by one-sentence items under the figure for a mechanism inside a part;
  Verification, the criterion and method for each goal, covering the goals; each section the
  ground of the next step and judged simply. With three points the user agreed: the four kinds of
  quality stay in Goals, so what the README's use does not show is not lost; coverage both ways,
  nothing below serving nothing above; each item judged yes or no. Decision 24, to report
  (replaces the checklist part of decision 23).
- Found (2026-10-16), on `td10`, turn's design made to the checklist of decision 24: it reads as
  a list (18 goals, 18 decisions, 9 sentences under the figure, 20 criteria), as other documents
  did. The cause as judged with the user: README, Goals, Design decisions and Verification each
  say the same promise again in another form, and coverage asked across the layers multiplies the
  restatements; the decisions files, written as everything listed, are followed as given. Decided
  by the user (2026-10-16): try the design as Structure and Verification alone: the opening's main
  point, the logical and physical figures with the sentences under the logical one, and a
  criterion with its method for each promise of the README in its words; a decision goes either
  into a criterion or into the figures, and one that fits neither is suspected not core;
  non-goals and constraints left out at first, kept only if the builder is then found to hesitate.
  Decision 25, to report (replaces Goals and Design decisions of decision 24).
- Decided by the user (2026-10-16), replacing decisions 22 to 25 for the design checklist: the
  checklist was made again from its purpose, agreed one point at a time (`rn/checklists/design.md`,
  `aa09573`..`48b2a26`): a design document lets whoever builds or changes the product understand,
  in a short time, the mechanism that brings about the UX the product must give and how that is
  checked; design thinks in four steps, minimal functions from the UX, logical components and their
  interactions, technology chosen only then for the physical realization and placement, each
  physical unit checked before the whole; UX > functions > components in number. Shape: Functions,
  Architecture (Logical view, Physical view), Verification (Units, Acceptance). No README
  dependence: the UX wherever it is defined. Decision 26, to report.
- Decided by the user (2026-10-16): a UX checklist apart from the README's (`rn/checklists/ux.md`
  0.1.0, `4047a61`): a UX lets whoever builds the product know the experience it must give; worked
  out as users and goals, scenes to the goal, benefits, then must-be and better-the-more qualities;
  a README is made from the UX. Where rn writes the UX, and how README and design take it, is not
  yet decided. Decision 27, to report.
- Found with the user (2026-10-16): decisions files written by hand listing everything made turn's
  designs read as lists; turn's input needs the decisions made by grilling the user item by item
  of the checklists, proposing, one point at a time. rn's conduct.md does not do that now
  (`rn/references/conduct.md:289` talks from a tree of points and fills items after,
  `:300` recommends nothing on intent questions); to change in rn's design once the checklists are
  remade. Every checklist is to be remade the same way, from its purpose agreed with the user.
- `dev/turn/design.md` holds an arc42 trial (`1db95e6`) the user set aside ("arc42は忘れて"); it is
  made again to the new design checklist through turn.
- `hc4`, the hooks' second unit (`rn-hooks-commits.json`), ended ($26) with questions, not yet
  judged; its folder is this session's scratchpad
  (`/private/tmp/claude-501/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-writ-rebuild/3b75ad56-53b9-4ae2-996d-bc66987528bd/scratchpad/hc4`).
- Decided by the user (2026-10-16): the README checklist made again from its purpose
  (`rn/checklists/product/readme.md`, `6d31fa7`..`1a95a46`): a README lets someone meeting the
  product decide and get to a first result, and lets someone joining its builders reach the design
  and development; it is made from the UX in six steps, the last two from the repository; a
  Development section; Benefit items drawn one per question from the steps, B-1 to B-8; Usability
  left to the readability checklist, as in the design and UX checklists. Decision 28, to report.
- Decided by the user (2026-10-16): the checklists kept by what each is for (`a0940b4`):
  `readability.md` (was `doc.md`, and the rules of the former `writ/references/style.md` not yet in
  it are judged when it is remade) and `checklist.md` at the top, `product/` for what goes into
  the product, `session/` for rn's plan and proposal. Decision 29, to report.
- Decided by the user (2026-10-16): no verification document; the design's Verification checks
  the units and the whole, and its Acceptance also measures each quality the UX names as better
  the more against the last version (`b4e0c21`, design B-26). `rn/checklists/verification.md`,
  `rn/docs/verification.md` and what uses them (conduct.md, the hooks in `trace.py`, their tests)
  are removed in rn's rebuild under #4, where rn's design says what replaces them. Decision 30, to
  report.
- Decided by the user (2026-10-16): the readability checklist made again from its purpose
  (`172460d`..`bbc256e`): a reader, a person or an AI, takes a document in once from the top in a
  short time; thought through in the order the reader reads (opening, reading on, nothing not
  needed, no question left); a shape drawn from those steps; one item for each step, B-9, B-17, B-4,
  B-18, with the finer checks under each; Usability none. The former style.md's tables, heading
  depth, parentheses, roles and code length came from no step and are left out. Every checklist
  still names `readability.md` in its opening, so it comes with each kind without being passed.
  Decision 31, to report.
- Where to resume (2026-10-16): remake the other checklists with the user the same way, one point
  at a time, in this order: prompt, code,
  hook, plan, proposal, checklist (whether the Usability section stays is settled there). Then
  rn's grilling step, turn's design, judging `hc4`, and the rest of #4.
- Stopped at the usage limit (2026-10-16): the runs of rn's prompts (second), hooks (second) and
  verification document (fourth, after the third's nine points were settled: the stand-in's parts
  live in the trials and answer the languages, A4's trials run to their pass, A3's two stand-ins
  said, the flow session's pass said, the must-be checks listed in the design alone) were killed
  before they ended. Where to resume: run `dev/turn/trials/run.py` again on
  `dev/rn/trials/rn-prompts.json`, `rn-hooks.json` and `rn-verification.json` (each in a new
  folder), judge each by the purpose, finish by hand, take the files in; then the trials on
  rn-try (`dev/rn/trials/flow.py` first, then `a1_first_call`, `a1_feedback`, `a2_intent`,
  `a3_proposal`, `a4_resume`, `a4_from_080`), with fixtures remade from this version's runs where
  a scene's premise differs; `claude plugin validate --strict`; rn 0.10.0 and turn 0.2.0 in
  CHANGELOGs; the final check; then report every decision above to the user.
- #5, turn's README through turn on the finished checklists (2026-10-15, Opus, $5.24, two
  readings in one run, 24 of 27 met, no question): no opening about itself, no glossary, no bold, no
  table; the kind of thing sits inside the gain. The three unmet (doc B-3, B-11, B-12) traced to the
  content file: a contrast with its other side unnamed, and "writ" named where the reader has not
  met it. Finished by hand, as the user decided: those two, the several-files sentence the content
  file had dropped, and the checklist's name and version said only as labels, which the first user
  skimmed. The five rules turn returned each apply an item that exists (doc B-5, F-1, B-3, B-12),
  so no checklist changes. Orchestrator's console lines came out in Japanese, since the clone runs
  under the user's global CLAUDE.md. Next: the user agrees `turn/README.md`, then the design.
- writ's README through turn in parallel (the user, 2026-10-15), from a content file drawn from the
  agreed README and the decisions since: the report puts first what writ decided, the callers' page
  link left out, each question with a recommended answer. Its design waits for the README, whose
  words its Goals use.

### [ ] #4: rn built and checked

Purpose: plugin.md steps 5 to 7 for rn, with writ folded in, tried on the practice repository;
#36, #37, #39, #41, #43, #44, #45 and #46 judged against the rebuilt rn.

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
- Decided by the user (2026-10-14): each check shows one quality, the flow apart from the work, in
  the smallest situation that shows it; added to `plugin.md` step 5e, turn's design Verification,
  and, through turn, to `design.md` and `code.md` (`27021d6`, `4016b98`). The flow of two readings
  is tried on `dev/turn/trials/flow/`.
- Found (2026-10-14): checklist changes and turn's docs were written by hand, not through turn. Decided
  by the user: the six checklists are made again through turn against `checklist.md`, keeping what
  each asks (CCS `.../scratchpad/re-<kind>.json`; `checklist.md` first, then the other five).
- The writ design from `d3` (464 lines, `done`) is not taken: it built state across a step's calls
  and cases no purpose needs. Next, after the checklists: make it again, given that each call
  brings every answer and decision so far and writ keeps nothing between calls.
- The six checklists are made again through turn against `checklist.md` (`404668f` to `7d0b420`).
- Where to resume (2026-10-14):
  1. Done: the writ design from nothing on the new checklists, through turn in three runs (`done`,
     every item met), copied to `dev/writ/design.md`. Decided by the user on the way: writ builds
     nothing for adding to a checklist; it hands its caller, first in the report, everything it
     decided or did not act on (turn's rules, questions it judged not needed, items left with why,
     changes it made to the request, points it settled itself); the README's "report once every
     item is met" changes to the design. Settled from the README (46-47): a point writ cannot judge
     goes to the user at the end.
  2. writ's README through turn (2026-10-15): with the agreed README and the design as sources,
     turn's learned rules piled up (11) and pushed in how writ works inside (the order of a call, a
     list of five report kinds); with a file of what to write, item by item, as the only source
     (`readme-content.md`), the first run kept to it, and the second drifted again: turn's
     orchestrator read `dev/writ/design.md` and `turn/README.md`, not given, by `sed`/`grep`.
     The README stays as agreed until turn is fixed.
  3. Decided by the user (2026-10-15), for turn (README, design, code) and the checklists:
     - The caller decides what the work says: one file, item by item of the checklists, in
       bullets. The caller reads an existing document and draws that file from it; turn only makes
       new, and an existing document is not its input.
     - The CCS states each input by its intent for the work, and turn decides from it what each
       role is handed: `checklist` (was `viewpoint`), `content` (what the work says, item by item),
       `reference` (what the work follows or draws on, a file or a folder), `receiver_opens` (what
       the receiver opens with the work, such as pages it links; the caller checks it before
       handing). `answer` goes into `content`. `difference` splits into `question` and `unmet`;
       turn returns the rules it learns in its own part as `rule` and no longer adds them to the
       caller's `constraints`. The first user reads only the work and `receiver_opens`, not a
       whole copy of the repository. Brief fields follow the same intent.
     - Every prompt, the orchestrator's and each role's, says in positive words to work from the
       inputs it is given alone, with why (to work without bias). A hook stops a Read, Grep or Glob
       outside the run's inputs and says why; the orchestrator's Bash runs only turn's scripts;
       the roles' Bash stays open (tests and builds need it), and what they read by it shows in the
       records. A stop gives its intent, not only the rule.
     - `prompt.md` changes (wording agreed): B-3 adds that each step is an instruction to act, not
       a rule; B-12 asks for positive terms even beside what to do; B-20 the reason for each
       instruction; B-21 the scope of its inputs (the whole of what the AI reads, what it works on
       and what it consults, such as other code it follows).
  4. Done: `prompt.md` through turn (aadb265); turn's README through turn from its content file,
     then finished by hand from its purpose (5b58f2f), its content file at
     `.writ/content/turn/README.content.md`; writ's design takes the content file (place, name,
     form, five steps), writ finishing turn's result itself and running turn again only on changed
     inputs, and drops the hook (8925167). The user decided (2026-10-15): turn's output meets the
     checklists, so the caller judges it by the purpose and fixes it; turn runs again only when
     its inputs must change much.
  6. Decided by the user (2026-10-15): turn's code is written by hand, since turn is the tool in
     use, but as turn works: with the checklist open, then read as the first user and given a Good
     per item with its lines, so each checklist is tried on its kind and refined. Findings on the
     checklists, now taken up in #6:
     - doc B-16 (who does what, in one place): had turn add a six-step list to turn's README, saying
       again what the console sample shows.
     - design B-16, B-30 (options weighed and cost for every choice): had turn ask five questions
       on turn's design that a builder's judging a change does not need.
     - code (on 8491db1): B-2, B-7, B-9, B-18 and B-22 each found a real gap, fixed in 579e991;
       no item pushed work the purpose does not need. B-20 found "round" in turn's design and
       "reading" in turn's code and tests for one thing; settle with the prompts.
  7. Where to resume (2026-10-15): turn's scripts and tests are on the new CCS (8491db1, 579e991;
     CI green, coverage 100%); turn's prompts and hooks are not yet, so a trial run breaks until
     they are. Next, each by hand with its checklist open, then read as the first user with a Good
     per item, findings added to 6:
     - Hooks (`code.md`): a check that stops Read, Grep and Glob outside the role's inputs (for an
       agent, the paths in its brief but `deliverable`, plus the brief; for the orchestrator, the
       run's evidence folder, `in`, content, references and checklists; turn's own folder for all),
       saying it is to work without bias and naming what may be read; a check that lets the
       orchestrator's Bash run only turn's `up.py`, `jq`, `mv` and `cd` on those paths; add Read,
       Grep and Glob to the PreToolUse matcher; give every stop message its intent. First confirm
       from a trial's records that PreToolUse inside a subagent carries `agent_type`
       (`console_shown.py` already relies on `agent_id`).
     - Prompts (`prompt.md`, B-20, B-21): the skill and the four agents name their inputs as the
       whole of what they read, in positive words with why; `sources` becomes content and
       references; the first user reads `work` and `opens`, no copy; the generator has no `started
       from`; step 14 rewrites the caller's parts with no turn entries in `constraints`. Settle
       "round" (design) against "reading" (code, tests, prompts) to one name.
     - Then a trial on the flow task, CHANGELOG (turn 0.2.0 with the old-to-new kind table; writ's
       stale lines), writ's README from its content file, writ's code, and finish #4.
  8. Done (2026-10-15): turn's hooks for working from the inputs alone. Confirmed in a run that
     PreToolUse inside a subagent carries `agent_id` and `agent_type`, and the main session's
     carries neither. Checked against `code.md`: B-2 and B-9 (each line removed, the tests run)
     found `jq -f` and a command after a newline untested, now tested, and a lexer setting no test
     needed, removed; no item pushed work the purpose does not need. The hook also lets each role
     read its session's `tool-results/`, the output of its own commands, which the design's
     "inputs alone" already covers. Next: #5.
  5. Next: the user agrees turn's README and writ's design (PR #61); turn's design and
     `turn/calling-from-a-plugin.md` on the decisions in 3, through turn and finished by hand;
     turn's code; writ's README from its content file (the "report once every item is met"
     promise, the callers' page link); writ's code; the stale CHANGELOG lines; finish #4.
