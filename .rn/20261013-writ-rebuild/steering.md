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

### [ ] #2: writ's README

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
- To do: turn's README is made again the same way, as the one committed was made with rules carried.
- To do in #4: `writ/.claude-plugin/plugin.json` names turn in `dependencies`, which the README's
  Installation promises; `turn/calling-from-a-plugin.md` points to turn's README for what both say
  (the checklist's front matter, writing over a file git holds, Esc).
- Next: the user agrees to the README.

### [ ] #3: writ's design

Purpose: `dev/writ/design.md` written with `doc.md` and `design.md` open, and agreed with the user
(plugin.md step 2), taking in "Essentials to add" from #53.

Serves: A1, A2, M1, M2

### [ ] #4: writ built and checked

Purpose: plugin.md steps 3 to 7; #36 and #37 judged against the rebuilt writ.

Serves: A1, A2, M1, M2, M3
