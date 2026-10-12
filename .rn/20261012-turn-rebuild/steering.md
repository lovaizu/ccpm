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
  and the judge fill point by point; there is one learner and one judge. An item left unfilled is
  not stopped: it has no Good, so it goes to the learner or is sent back before it reaches the
  user.
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
- `design.md`: agreed with the user (2026-10-12), on Google's design docs, ADRs and arc42; it is
  set as Goals (attractive, one-dimensional and must-be quality, backward compatibility, non-goals,
  constraints), Verification of each quality, then Architecture, since what is aimed at and how it is
  checked do not depend on how the product is built.
- `prompt.md`: agreed with the user (2026-10-12), on Anthropic's prompting and skill authoring best
  practice; it holds what a prompt gives the AI that runs it, including a set and minimal form for
  what goes in and out, and leaves how a prompt is made, judged and tried to turn. Rules about
  prompts now in `.claude/rules/plugin.md` section 3 move to it in #2, which keeps only how a plugin
  is built, such as hooks.
- All five checklists are agreed, and none names a role of turn or a way of trying a deliverable.
  Whether two judges give the same answers is checked in #3, by running turn on them, since judging
  is turn's flow.
- Each file is shown to the user in Japanese, and read against `doc.md` and `essentials.md`
  before it is handed over.

### [ ] #2: Plugin rules as steps

Purpose: `.claude/rules/plugin.md` says, as steps that can be kept today, how a plugin here is
built; the builder opens the viewpoint files themselves.

Serves: A2, M1

Completion criteria:

- Attractive quality: building turn needs nothing the rules do not say.
- Must-be quality: each rule has its reason, and no step needs a tool that does not exist yet.

Progress:

- `.claude/rules/plugin.md`: agreed with the user (2026-10-12), rewritten as eight steps in the
  order a plugin is built; units are built and tried one at a time, the first carrying one
  attractive quality by the thinnest path, then the whole is checked against the design's
  Verification; registration is part of the first release. Whether building turn needs nothing more
  is seen in #3.
- Next, #3: turn's README, by step 1 of `plugin.md`, with `doc.md` and `readme.md` open.

### [ ] #3: turn from nothing

Purpose: turn's README, design, prompts, hooks, scripts and tests are made from nothing against the
new viewpoint files and rules, each document agreed with the user before the next.

Serves: A3, M1, M2, M3

Completion criteria:

- Attractive quality: a plugin hands turn one task and decides its next move from what turn returns,
  and the user can later tell which version of each viewpoint file a work was made and judged by.
- Must-be quality: tests cover every line, and the plugin and marketplace validate.

Progress:

- README and design written from nothing on the checklists and the decisions of the old design that
  still hold, then put through turn's flow by hand: a maker subagent made them meet every item, the
  assistant as conductor sent them back until it saw every item met, then readers, a learner and a
  judge ran, and the maker made them again. Last pushed in d480274; not yet agreed with the user.
- Found while running the flow, and settled: the list made from a checklist must carry its opening,
  or the maker and the reader measure under different conditions (`dev/turn/trials/make_list.py`
  makes it: `python3 dev/turn/trials/make_list.py <checklist>... > list.json`); `design.md` lacked an
  item asking that a design hold nothing of the specification, so U-2 was added; the maker read
  files beyond its inputs in every run, so a hook must stop that.
- Decided by the user (2026-10-12): the order in a round is reader, then judge, then learner on the
  items the conductor has confirmed as More only, so that no role is set to find something; Good is
  as full an answer as More, the judge gives grounds for both, and the conductor checks both.
- Run of 2026-10-12 done (README 9e479da, design 7a18991), two rounds each. README round 2 left
  five items without a Good: the figure laid over the console and prose, "question" for two things,
  rules for both routes under one route's heading, a claim on AI behaviour stated flatly. Design
  round 2 left nine: the CCS's parts named nowhere, ideas added mid-making not given in full
  (coverage's "part", the marks), items across the two documents checked in one only, decisions
  spliced in at lines and the whole not read again, assumptions marked by place not by rule, choices
  weighed only where a Weighed line already was. Seen in the run: a judge told to write Goods only
  still wrote on items without one, so the form must hold it, not words.
- Run of 2026-10-12 (second) done: README, design and a new `turn/skills/up/ccs.md` (55437af),
  two rounds. Counted Goods: README 9 then 13 of 25, design 20 then 25 of 34, ccs.md 8 of 15.
  Not converging: the same slips came back each round, all in the conductor's hand work: the
  maker's grounds were taken from its account, never counted at hand-over, so gaps visible before
  the reading reached it; send-backs asked in words for whole re-reading and got changes at lines;
  Goods naming the whole document came back though the judge was told in words not to; on unchanged
  lines two judges disagreed. What held was the form: a judge given a place for Goods only wrote
  nothing on other items.
- Seen in that run (the conductor's own account to the user): the conductor passed work it had not
  checked, looking only at the lines the maker named, not reading the whole for each item; after
  the reader found an exception, it did not look for the same kind across the work. Only the judge
  had a form; nothing held the maker or the conductor to cover everything.
- Decided by the user (2026-10-12): every role is defined in full, and a script holds each to cover
  all of it. The forms each role fills are made by script from the list: one place per item for an
  item met somewhere in the work, and one place per item and section for an item over the whole
  work (one name, said once, every part has a job, nothing to guess, as short as can be). No role
  hands on until every place is filled and its script check passes. Maker: what the work should
  be, sources, list (round 2: causes) → the lines that meet each place; the script checks every
  place is filled, the lines exist, and no line is named by no place. Conductor: the work, the
  maker's form, coverage → each place seen met in its lines, or sent back; nothing goes to the
  reader until every place is seen met and nothing is sent back. Reader: the work in a fresh copy,
  receiver, use, list → what it took and where, for each place. Judge: list, work, reading,
  records → a Good with grounds per place, and no place for anything else; the grounds exist; an
  item over the whole work is Good only with a Good in every section. Learner: each place without
  a counted Good and each line no Good names → a cause for each. Each form is filled again for
  every document on every hand-over, and the script checks it was filled for the current version.
  The work is every document made together and every document they link.
- Decided by the user (2026-10-12): a Good on lines unchanged since the round it was counted in is
  carried to the next round, so only what changed is judged again; a judge's variation on the same
  text then touches nothing that did not change.
- Decided by the user (2026-10-12): the judge gives Good only, each with its grounds, and no More;
  the conductor checks each Good against the facts, and every item without a Good it has confirmed
  is More. So the final decision is the conductor's, and an item not shown to be met never passes.
  The design takes this in once the round now running has ended.
- Decided by the user (2026-10-12): every role aims only at every item being Good, and thinks
  forward: the learner asks why no Good came out, the conductor how a Good is reached. The lists
  handed to and filled by the roles have a field for a Good and its grounds only, and none for
  More, so no role can write a shortfall; More is a word of the CCS alone, kept as the caller's
  interface.
- Decided by the user (2026-10-12): a slip the maker puts into the work is caught by coverage, as
  tests are by line coverage: a script counts the parts of the work that no item's grounds rest on,
  once when the maker hands the work over (from the words it gives for each item; the conductor
  sends it back before any reading) and once when the judge hands back its Goods (from their
  grounds; before the conductor checks them). A part no Good rests on has no job or holds a slip.
  What still slips through is of a kind no item asks about, and goes into the checklist.
- Decided by the user (2026-10-12): no role doubts, the conductor included; its aim is how more
  items reach Good, and what brings a slip to light is the coverage, a mechanism. The conductor
  counts a Good only once it has seen, in the lines the Good rests on, that the item is met.
- Found in the records of the second run (2026-10-12): it did not converge because the conductor
  took the agents' answers as they were. Grounds naming one place passed items asked of the whole
  work, so the reader found an exception elsewhere in each round; a Good naming the whole work was
  dropped by the conductor's counting rule; the judge answered differently on unchanged lines.
- Decided by the user (2026-10-12): the conductor alone decides, reading the whole work for each
  item against its purpose; the other roles support it. This replaces the forms per item and
  section and the carrying of Goods to the next round, which are dropped. Forms per item and
  coverage stay, as what shows the conductor where to look.
- Done at the user's word to make all of it as it should be (2026-10-12): the design is made on the
  conductor as the one who decides, with one name for an item without a Good; the hook on reads
  beyond an agent's inputs is dropped, since the maker needs the repository it writes about; a file
  already where the work goes is written over only when git holds it as it stands. The README tells
  how to put a checklist in the repository, and loses the coverage sentence and the plugin example,
  which ccs.md holds. ccs.md says what happens to a file already where the work goes.
- Decided by the user (2026-10-12): the role names go back to those released on main
  (orchestrator, generator, first user, evaluator, learner); they were changed in this rebuild
  without agreement. The design is written again from nothing, half its length or less: no
  specification (console details, the hooks' checks, steps the callers' page holds), no history
  beyond one ground, Weighed only for choices a builder might want to change, principles only where
  they span approaches, and a figure of who takes part, what each is for and what it depends on in
  place of the table.
- Found with the user (2026-10-12): the assistant, as orchestrator by hand, asked for agreement
  without deciding every item itself, Goods included, so the user did the orchestrator's work. The
  cause: no record shows the check was made, so a cheaper check passed for it. Decided: before asking
  for agreement, the orchestrator fills, for each document, a form made from its list with every
  item decided (met or not, the lines, what was fixed), a script sees every item filled, and the
  real thing is checked too (the figures as GitHub renders them, one reading from the top as the
  receiver). turn's orchestrator follows the same steps.
- Design written again from nothing (544 to 320 lines, 280 without the figure), with main's role
  names and a sequence figure of who takes part, each one's aim and what each depends on. The
  orchestrator's forms for the design, the README and the callers' page are in `forms/`, every item
  decided and met (`python3 dev/turn/trials/check_form.py <form> <checklist>...`); the figure was
  checked as mermaid-cli renders it.
- `turn/README.md`: agreed with the user (2026-10-12), plugin.md step 1.
- Next: ask the user to agree to the design (step 2).

### [ ] #4: The rules use turn, and turn goes through turn

Purpose: once turn works, the rules have documents and prompts made through turn, and turn's own
README, design and prompts are put through it.

Serves: A2, A3

Completion criteria:

- Attractive quality: what turn finds in its own documents is settled at its cause.
- Must-be quality: no rule still asks for a check by hand that turn now makes.

# Not yet specified

- For turn (#3), told by the user: three roles, none of which gives a way to fix. The user reads the
  checklist and the deliverable, and returns, for each item, what they could take from it, at
  possibly several places. The judge reads the checklist, the user's result, the deliverable and
  the JSONL, and gives Good only, each with its grounds; what has no Good the conductor confirmed is
  More. The learner reads the same for those Mores, and returns what was learned about the content and about the process.
  Each role fills a list made by
  script from the checklist, seen before the work begins and filled by following its steps, so that
  every item is done.
- For turn (#3), decided by the user: each role is given one aim it can work toward, on the
  premise that a work meeting every checklist item serves its purpose. The maker makes a work that
  meets every item and reports, for each, where in the work it is met. The conductor makes the
  final decision: it reads the maker's work and report and sends the work back until every item is
  met, so a shortfall is sent back where it was made (shift left), and it checks each Good and More
  against the facts before acting on it. The reader returns only what it took, for each item; the
  judge gives each Good it finds from the reading and the facts, with its grounds, without bias; the
  learner learns why each More was not taken.
- For turn (#3), decided by the user: the conductor sends the maker's work back with no limit,
  since settling it is the conductor's work. Every role takes its standpoint from the checklist
  alone: the list made from a checklist carries its opening (its purpose and who reads the work)
  with the items, so the maker, the conductor and the reader measure under the same condition.
- For turn (#3), decided by the user: the CCS is the interface between the caller and turn, and is
  kept as it was decided; inside turn, the conductor hands each role the parts it needs in forms set
  for that role.
- For turn (#3), decided by the user: the README's reader is anyone who has an AI make a
  deliverable, by asking in a conversation or from their own plugin's steps, since a person never
  writes a call to turn. Its Example shows what turn shows in the console as it works, since how the
  work is made and tried is what only turn gives, while the deliverable itself depends on the task.
- For turn (#3), agreed with the user, to be improved as it is used: the console serves a user who
  looks in now and then. It shows the whole flow first (write, have it read, check; once more if
  something is missing, two rounds at most) and each line's place in it, grouped by round; what turn
  means to make, before it writes, so the user can stop it early with Esc and say otherwise; the path
  of each round's deliverable and reading; what the reader could not take, in plain words, without
  item IDs or counts; and at the end where the deliverable is and what the user must decide. Only
  three marks are used, each with one meaning: ⚠️ what the reader could not take, ✅ nothing missing,
  ❓ what the user must decide.
- For turn (#3), decided by the user: turn runs at most two rounds. When the first gives no More, it
  ends; otherwise the More items are made again and tried in a second round, so every change is
  tried once before it is returned. What the second round leaves as More is returned as it is, with
  its reasons, and the user decides; it is not changed again, since an untried change is a patch.
  The learner and the judge judge from what the deliverable should be, by their steps and set inputs
  and outputs, so that a More is made again from its cause and not patched; the aim is that the
  first round gives no More.
- For writ's steps (next pull request): find a checklist's items by listing the parts a deliverable
  of the kind has and asking what each does for the purpose in each section's sense; try a
  checklist on one deliverable that served its user and one that did not.
- For writ's steps (next pull request), decided by the user: a checklist that holds for every
  document can be met by steps, so writ's steps for writing a document are drawn from `doc.md` and
  name the items each step makes hold by ID, without copying their words. One step, before any part
  is written, sets out what each section and paragraph is for (B-4), since that is where documents
  are most often weak. Items that only a reading shows, such as B-2, are held by a last step that
  reads the document as its reader and answers every item.
- When writ is rebuilt (next pull request): rename the folder `essentials/` and the file
  `essentials.md`, now that they hold checklists; the current writ's skills, agents and scripts
  name them, and are replaced then.
- Whether writ's steps use the usual ways a deliverable fails (wrong, too little, for someone
  else, a shape it cannot take) as a hint when finding items.

- Registration in the marketplace and the root README, and release.
