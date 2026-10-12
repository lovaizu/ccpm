---
rn: 0.9.0
pr: https://github.com/lovaizu/ccpm/pull/60
status: running
artifact-language: English
conversation-language: Japanese
readme: turn/README.md
design: dev/turn/design.md
verification: dev/turn/trials
---

# Goal

turn is rebuilt from nothing on measures that hold: writ's viewpoint files say what a good work of
each kind is, the plugin rules say how a plugin here is built in steps that can be kept today, and
turn is made against both. Each part is agreed with the user before the next is begun. writ is
rebuilt on this turn in the next pull request (#53).

# Acceptance criteria

## Attractive quality

- A1: A builder makes a document or a prompt with only the viewpoint file for its kind open, and it
  comes out as its receiver needs.
- A2: A builder builds a plugin here by following the rules' steps alone.
- A3: A plugin hands one task to turn and receives work that someone in the receiver's place has
  already used, with what only the user can decide asked of the user.

## Must-be quality

- M1: Each part follows official best practice or says why it does not, and holds nothing its
  purpose does not need.
- M2: Each part is written from nothing; nothing is carried over from the files this rebuild
  replaces.
- M3: `claude plugin validate --strict` passes for turn and for the marketplace, and CI passes.

# Assumptions

- Fact, decided by the user: PR #59 is closed and everything made on it is dropped, since it grew by
  patches and what it holds cannot be trusted.
- Fact, decided by the user: a viewpoint file says only what a good work of its kind gives its
  receiver; who reads it and how a work is tried belong to turn, not to the file.
- Fact, decided by the user: a prompt has a `## Role` that says what is expected of it and numbered
  `## Steps` written as what to do; what it receives, what it hands back and what it must do in full
  are steps, and how it thinks within a step is left to it. Hooks catch slips in the process.
- Fact, decided by the user: the rules say what can be done now; they are updated to use turn once
  turn is built, and to use writ once writ is built.
- Fact, decided by the user: each part is agreed with the user one at a time; no worker session is
  used.
- Fact, decided by the user: a viewpoint file opens with the purpose alone, then always has the
  same three sides (Benefit, Usability, Format), each with points or `None` and why; each point has
  an ID of side letter and number, never used again, a question answered yes or no, and the reason it is needed,
  and nothing else. It carries no version or frontmatter, since git keeps
  its versions.
- Fact, decided by the user: turn makes from each viewpoint file, by script, a checklist the maker
  and the judge fill point by point, and a hook stops one left unfilled; there is one learner and
  one judge, not one for each side a point is looked for from.
- Fact, seen by the user: the old README, design and viewpoint files had grown long; what was mixed
  into them could not be told.

# Rules

- The documents are written in English from the start; the user reads them through machine
  translation, so each thing keeps one plain word.
- Nothing is written before the user agrees to it; a finding goes back to the measure it comes from,
  and the part is written again from there.

# Tasks

### [ ] #1: Checklists as they should be

Purpose: writ's checklists (once called viewpoint files) say, as yes-or-no questions, what a
deliverable of each kind must be to serve its purpose, with nothing about any flow;
`essentials.md`, the checklist for checklists, comes first, then `doc.md`, `readme.md`, `design.md`
and `prompt.md`.

Serves: A1, M1, M2

Completion criteria:

- Attractive quality: a maker reads a checklist before making a deliverable and knows how it will
  be judged, and two judges give the same answers.
- Must-be quality: each checklist meets every item of `essentials.md`; no file names a reader, an
  agent or a way of trying a deliverable.

Progress:

- `essentials.md`: agreed with the user (2026-10-12).
- `doc.md`: agreed with the user (2026-10-12), built on documentation best practice (Write the
  Docs principles, Google technical writing, Diátaxis, the pyramid principle, plain language,
  cognitive load); B-7 asks for no overlap between documents only, and allows some repetition
  within one.
- `readme.md`: agreed with the user (2026-10-12), on GitHub's and makeareadme's README guidance; it
  sets the headings a reader looks for, with Requirements apart from Installation, and no support
  section, since where to ask is where the reader already looks.
- Next, `design.md`, written from nothing after researching design document best practice.
- Each file is shown to the user in Japanese, and read against `doc.md` and `essentials.md`
  before it is handed over.
- Names left to settle with the files: the folder `essentials/` and the file `essentials.md`, now
  that they hold checklists.

### [ ] #2: Plugin rules as steps

Purpose: `.claude/rules/plugin.md` says, as steps that can be kept today, how a plugin here is
built; the builder opens the viewpoint files themselves.

Serves: A2, M1

Completion criteria:

- Attractive quality: building turn needs nothing the rules do not say.
- Must-be quality: each rule has its reason, and no step needs a tool that does not exist yet.

### [ ] #3: turn from nothing

Purpose: turn's README, design, prompts, hooks, scripts and tests are made from nothing against the
new viewpoint files and rules, each document agreed with the user before the next.

Serves: A3, M1, M2, M3

Completion criteria:

- Attractive quality: a plugin hands turn one task and decides its next move from what turn returns,
  and the user can later tell which version of each viewpoint file a work was made and judged by.
- Must-be quality: tests cover every line, and the plugin and marketplace validate.

### [ ] #4: The rules use turn, and turn goes through turn

Purpose: once turn works, the rules have documents and prompts made through turn, and turn's own
README, design and prompts are put through it.

Serves: A2, A3

Completion criteria:

- Attractive quality: what turn finds in its own documents is settled at its cause.
- Must-be quality: no rule still asks for a check by hand that turn now makes.

# Not yet specified

- For writ's steps (next pull request): find a checklist's items by listing the parts a deliverable
  of the kind has and asking what each does for the purpose in each section's sense; try a
  checklist on one deliverable that served its user and one that did not.
- For writ's steps (next pull request), decided by the user: a checklist that holds for every
  document can be met by steps, so writ's steps for writing a document are drawn from `doc.md` and
  name the items each step makes hold by ID, without copying their words. One step, before any part
  is written, sets out what each section and paragraph is for (B-4), since that is where documents
  are most often weak. Items that only a reading shows, such as B-2, are held by a last step that
  reads the document as its reader and answers every item.
- Whether writ's steps use the usual ways a deliverable fails (wrong, too little, for someone
  else, a shape it cannot take) as a hint when finding items.

- Registration in the marketplace and the root README, and release.
