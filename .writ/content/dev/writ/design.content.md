# What dev/writ/design.md says

## doc

### B-9: The point from the opening
- writ keeps what its README (`../../writ/README.md`) promises as a thin wrapper of turn: turn makes
  the document, has it read in its reader's place and checks it against the checklists; writ adds
  only what turn cannot know: which checklists measure the document, what the document must say
  for its reader, item by item, and whether what turn returns serves the document's purpose; and
  it hands its caller every decision it made or left. A change fits when it keeps writ to that.
- How to use writ is in its README; how turn makes, reads and checks a work is in turn's design
  (`../turn/design.md`); what each checklist asks, in the checklists.

### B-5: How far to rely
- A statement no trial has checked yet is marked "(assumption)".

### B-12: Every term known
- The request: what writ is asked for, a kind of document or the path of one already there, with
  whatever is said of it, such as the sources to make it from.
- A call: writ at work once, from being started until it stops, started by the user typing
  `/writ:up` or by a calling step: a step of another plugin, such as rn's, that has the skill
  `writ:up` make a document, saying as it starts writ that it is one. The caller is whoever started
  the call: the user or the calling step.
- An open point: a decision that an item of the checklists asks for and that the request does not
  state outright. writ settles one itself only from the request, the repository or the sources,
  never by a guess; one these do not settle goes to the user, and is answered by the user or by a
  calling step in the user's place.
- The content file: what the document must say for its reader, item by item of the checklists, as
  writ settles it with the request, the repository, the sources and the answers. It holds only what
  the document says or does, never how it is written, since how is turn's.
- The task: what writ hands turn: where the document goes, its reader, their use of it and what they
  must be able to do with it, the checklists, the content file, what the document follows or draws
  on, and what the reader opens with it. It is written as a CCS, the JSON file turn takes and writes
  back, in the form turn's page for plugins' steps (`../../turn/calling-from-a-plugin.md`) gives.
- A run: turn at work once, from the task it is handed to the CCS it writes back. turn asks nothing
  while it works: what only the user can decide it leaves out of the document and returns as a
  question at the end, beside each item not met; it may also return rules, each a change in how
  such work is made, for later work of the kind; and it keeps, as its evidence, the lines that meet
  each item or what the document would take to meet it, and each checklist's name and version.
- The report: what writ hands back with the document: first what the caller decides, then each item
  met with its lines, and each line writ changed after turn.
- What the purpose needs: the one test writ applies wherever it weighs whether to ask, meet or leave
  something. The purpose is the document's reader, their use of it and what they must be able to do
  with it, as the task states them. An open point, an item or a question is needed when the
  reader's use or a decision of theirs rests on it: without it, or with another answer to it, the
  reader would decide or act otherwise. Otherwise it is not needed, as the finer questions turn
  raised on a CSV tool's README, such as tabs, encodings and line endings, were not: neither the
  developer's deciding on the tool nor their starting with it changes with the answers (seen in
  three runs, 2026-10-14). When writ cannot tell whether the reader's use rests on it, the test
  leaves the case undecided, and writ puts it to the user as a question with a recommended answer,
  since a point that may change what the reader does is the user's to decide.
- What turn hands back: the document, written where the task says, and the CCS the run writes back.
  In that CCS, `next` names one of four outcomes: `done`, nothing is left for the user; `ask the
  user`, the CCS holds each question only the user can decide and each item not met with how it
  would be met; `to the caller`, an item would be met only by a change in what writ wrote in the
  task; `stopped`, the user pressed Esc during the run and said what they want instead, and the
  document is as it was before the run. When turn ends before any work, because python3 or jq is
  missing, the `out` file already exists, the CCS does not match its form, or a file where the
  document goes has changes git does not hold and is not the document a run returned unchanged,
  turn writes no CCS and says why in the conversation; writ puts that reason to its caller as it
  is.

## design

### B-1: Attractive quality
- Said in the README's words, since the reader comes from it.
- Asked what Claude alone would guess, and only that: before turn runs, writ settles every open
  point the request, the repository and the sources settle, looking facts up rather than asking,
  and asks the user, one question at a time, each with a recommended answer, those of the rest the
  purpose needs or the test leaves undecided. Once writ says it is writing, the user can leave it at
  work.
- Handed on without reading it over: the document comes back with every item the purpose needs met,
  as turn last read it in its reader's place and checked it and writ finished it for the purpose,
  whether written anew or made again from what one the user already has says; an item left not met
  is one the purpose does not need, or one the user, asked, chose to leave.
- Judged from the report: the caller reads first what is theirs to decide, each with its ground, and
  judges each item met at the lines the report gives for it, instead of reading the document over.
- A checklist for each kind: writ keeps checklists for documents, READMEs, design documents,
  prompts, code and its tests, and checklists. For a kind it has none for, the user chooses between
  the checklist for every document alone and having one made with them first, and a checklist made
  is used for that kind from then on.

### B-2: One-dimensional quality
- Each must be no worse than in the version in use.
- Questions answered: how many questions the user answers for one document. Each one beyond what
  only they could decide is time they spend on what writ could have settled.
- Time and tokens: what one document takes, from the request to the document handed back.

### B-3: Must-be quality
- The report holds: every item the report shows met is one turn showed met, at the lines turn named,
  and every item turn left not met, every question it left open and every rule it returned is in
  what the report puts first, as is every line writ changed after turn, with why; writ holds no
  check of its own.
- Nothing of the user's lost: a document already there is written over only when git holds it as it
  stands.
- Missing tools: without python3 or jq, writ stops before its first question and says what to
  install.
- Installs with turn: installing writ installs turn, and writ's manifest passes validation.

### B-4: Backward compatibility
- `/writ:up`, relied on by users, who type it. Must keep holding: a request naming a kind of
  document, or the path of one, gets the document and its report. May change: the questions'
  wording and order, and the report's layout.
- `writ:up` from a calling step, relied on by plugins whose steps make documents through writ, rn
  first. Must keep holding: a calling step that starts writ with a request and the answers it has
  settled gets back either the document with its report, or every open point writ would ask the
  user, with a recommended answer; started again with the same request and its answers to those
  points, writ goes on as if they had been settled in the first call. The form the calling step
  reads to tell which of the two it got, and what the report puts first, are kept as released. May
  change: the wording of each point and its recommendation. rn 0.9.0 started the earlier writ with
  instructions in words and read a report file; rn is rebuilt on this writ and released with it, so
  that earlier way of starting writ is replaced, not kept.
- writ's checklists, relied on by turn, which reads each by the name and version it opens with; by
  turn's README, which points users to them to copy; and by users who copied them. Must keep
  holding: each opens with its name and version in the form turn's README gives; an item's ID always
  means the same item; a checklist's version goes up once for each release that changes it, so the
  version a report names is the text the document was judged by. May change: where they sit inside
  writ, with turn's README changed in the same change, and an item's wording in a new version.
- A checklist writ made, relied on by the user and their team, who commit it and write to it, and by
  writ, which finds it again. It is at `.writ/checklists/<kind>.md` in the user's repository, as the
  README names it. Must keep holding: a checklist at that path is used for its kind. May change:
  nothing of it is writ's once written; the user may edit it.
- The content file, relied on by the user, who commits it beside turn's evidence so each item met
  traces back to what was asked of it, and by a later call, which may settle points from it. It is
  at `.writ/content/<the document's folder>/<its name without the extension>.content.md`, such as
  `.writ/content/turn/README.content.md` for `turn/README.md`, so it is found from the document's
  path and not taken for the document; it opens with `# What <the document's path> says`, holds one
  heading per checklist and, under it, one per item, with what the document says or does as
  bullets. Must keep holding: that place and form. May change: nothing else; writ writes it anew on
  each call, and git keeps the one before.

### B-5: Non-goals
- Checking the document: it is turn's alone. writ adds no AI check of its own, and its builder
  judges turn's result rather than a second checker's, since a fresh agent set to check a README
  judged beyond the README's scope and disagreed with turn (seen once, on one README, 2026-10-14).
- Keeping anything between calls: each call brings everything settled so far, and writ reads back
  nothing it wrote in an earlier call except as the repository holds it. So the conversation or the
  calling step holds every answer and brings it again, and a call cut off is started again from
  them.
- Telling turn what the document may leave out, or shaping turn's check in any other way: what turn
  returns is judged afterwards, by writ. turn may return questions and items not met that the
  purpose does not need, finer ones with each run; writ weighs each by the test of what the purpose
  needs, asks no question and runs turn no further for one the reader's use does not rest on, and
  puts each such one first in the report with the use or decision it does not touch, so the caller
  still sees it.
- Adding to a checklist: writ hands each rule, question and item left to its caller, who decides
  whether a checklist or their later work takes it in.
- Lint tools, and Claude Code choosing writ on its own: the README leaves both out.

### B-6: Constraints
- writ runs in Claude Code and holds only skills and scripts. Installing copies only its folder, so
  its checklists travel in it, and a checklist made for the user and each content file live in their
  repository.
- writ uses turn only as turn's page for plugins' steps gives it: the skill `turn:up` started with a
  CCS, and the CCS turn writes back, since turn may change everything inside.
- A subagent cannot ask the user, and a calling step may run in one (Claude Code's documentation on
  subagents, as read on 2026-10-14: a subagent has no AskUserQuestion and no way to reach the
  conversation that started it while it works).
- Users' machines run Python 3.9 or later with the standard library only, and jq; the document is in
  a git repository. turn runs on all three, and writ's own scripts require no more.
- writ is used by Claude on a person's behalf, from a conversation or from a calling step.

### B-7: Attractive quality checked
- Each attractive quality is tried on its own and judged from the records: the JSONL of every
  conversation and agent the call started, on the model the user's conversation runs and the models
  turn's agents name, never a smaller one. Each passes on what happens to the user, not on the shape
  of what writ writes.
- Asked what Claude alone would guess, and only that: tried on the README of a small tool that
  tidies CSV files, from notes that say what it does and how to run it but not its license, in a
  repository with no license file. The notes settle every other point, so any other question shows
  writ asking what it should have looked up; the license is the one point only the user can decide.
  Passes on the questions alone: writ asks that one question, with a recommended answer, before turn
  runs, and asks nothing else.
- Handed on without reading it over: tried twice: on the same README from nothing with every answer
  given, and on the same request where the tool already has a committed README, which is what makes
  turn write over a file. Passes when every item the purpose needs is met in turn's evidence, and
  each item left not met is one the purpose does not need, or one the user, asked, chose to leave.
  The builder judges need from the records by the same test writ applies: an item is needed when
  the developer's deciding on the tool or their starting with it rests on it.
- Judged from the report: tried in a call of its own on the flow trial's note and checklist, with
  the point the user decides there given in the request, so the report has two items to show and
  the answer writ took from the request to put first. Passes when the report puts first that answer,
  with its ground, and each rule, question left open and item not met that turn's evidence and
  returned CCS hold, and nothing else; when turn returned none of these, that answer alone is put
  first. And the lines it gives for each item met give that item when opened.
- A checklist for each kind: tried on "the release notes for 1.4" in a repository with no checklist
  for release notes. Passes when writ puts the choice before any other question; choosing the
  checklist for every document alone, the notes are written to it; choosing to have one made, a
  checklist is made with the user against the checklist for checklists, put at
  `.writ/checklists/release-notes.md`, and the notes are written to it; and a second request for
  release notes uses it without putting the choice again.

### B-22: Where each benefit is tried
- The flow, from the request through the open points, the task and turn's return to the handing
  back, is tried apart from what turn makes, on the smallest task that shows it: a note of a few
  lines against a checklist of two items, one of which the note's sources leave to the user. The
  flow passes when writ asks that one point, writes the content file with the answer in it, runs
  turn once, and hands back the note with its report, the answer in it. The note asks turn only for
  something to hand on, so the trial spends no real document's cost and does not fail where only
  turn's work falls short.

### B-8: One-dimensional quality measured
- Both are measured from the records of the same requests, the CSV tool's README and the release
  notes, answered the same way: the questions the user answered, the minutes, and the tokens from
  the request to the document handed back.

### B-23: What a measure is compared with
- Each is compared with the same request on the version in use, writ 0.2.0.

### B-9: Must-be quality checked
- Each is a test on the script that holds it, in the case that would break it.
- The report holds: given turn's evidence and returned CCS with items met and not met, a question
  left open and a rule, the report shows met only the items the evidence shows met, with their
  lines, and puts first every item not met, the question, the rule and each line writ changed after
  turn, with why.
- Nothing of the user's lost: turn's own test, on a file where the work goes with changes git does
  not hold; writ adds none, since turn's check stops the case.
- Missing tools: with python3 or jq missing, writ's first check says what to install.
- Installs with turn: `claude plugin validate --strict` passes for writ and for the marketplace on
  every push, and writ's manifest names turn among its dependencies.

### B-10: Backward compatibility checked
- `/writ:up`: a trial of its own on the flow trial's note, typed as users type it: once naming the
  kind, and once naming the path of the note, committed. Passes when each gets the document and its
  report.
- `writ:up` from a calling step: a trial: the CSV tool's README requested by a calling step inside
  a subagent. Passes when writ asks nothing and returns the license point with a recommended
  answer, and, started again with the same request and the answer, hands back the README naming
  it, with its report.
- writ's checklists: a test has turn's own script read every checklist writ keeps into its list,
  and finds each one's name, version and items.
- A checklist writ made: a test on the script that finds the checklists for a kind: in a repository
  holding `.writ/checklists/<kind>.md`, that checklist is found for its kind.
- The content file: a test on the script that names it: for a document's path, the content file's
  path is the one above, and the file writ writes opens and is laid out as above.

### B-12: Who takes part
- The user, who has a document to hand on; the calling step, which decides as the user's agent; the
  skill `writ:up`, which hears the caller, settles the open points, writes the content file, hands
  turn the task, and judges and finishes what turn returns; writ's scripts, which do what must come
  out the same every time, finding the checklists and writing the report; turn, which makes, reads
  and checks the document; Claude Code, which runs the skill where its caller runs; git.
- The skill runs in its caller's conversation: the user's, or the calling step's, a subagent
  included.

### B-26: What each one depends on
- The skill cannot work without turn, the checklists and Claude Code, which runs it; writ's scripts,
  without python3 and jq; turn, without the task as a CCS, git, python3 and jq, as its README says;
  the calling step, without writ's form of the open points handed back.

### B-25: What passes between them
- The user hands the skill `/writ:up` and the request; the calling step hands "a calling step", the
  request and its answers so far.
- The skill hands a script the kind, and gets its checklists back, writ's and the user's.
- The skill puts the user one open point at a time, with a recommended answer, and gets the answer;
  to a calling step it hands every open point at once, with a recommended answer, and the call
  ends.
- The skill writes the content file, hands turn the task as a CCS, and gets the CCS back: `next`,
  questions, items not met, rules and where turn's evidence is.
- The skill hands a script turn's evidence and returned CCS with its own judgments and changes, and
  gets the report; it hands the user, or the calling step, the document and its report.

### B-32: The whole in one place
- One figure, a sequence diagram, with the user, the calling step, the skill `writ:up`, writ's
  scripts and turn, each with what it is for in its label, and the passes above in order; after the
  figure, only what it cannot show: where the skill runs, and what each cannot work without.

### B-11: Principles to judge a change
- writ adds to turn only what turn cannot know: which checklists measure the document, what the
  document must say, and whether what turn returns serves the purpose. Making, reading and checking
  stay turn's; writ neither repeats a check turn makes nor shapes it. Protects: the report holds,
  time and tokens, and the constraint that writ uses turn only as turn's page for plugins' steps
  gives it.
- What to say is writ's, how to say it is turn's: the content file holds what the document says or
  does, and turn makes the form against the checklists. Protects: handed on without reading it over,
  since form written into the content is copied into the document (seen on turn's README,
  2026-10-15, where the content's wording came through as it was) or overrides turn's check
  (assumption).
- turn is given everything at once and runs once: what turn returns, met against the checklists, is
  finished by writ where the purpose needs, and turn runs again only when what it was given must
  change, and writ's own changes to the document come after turn's last run, since turn writes
  over a file only when git holds it or it is the document a run returned unchanged. Protects: time
  and tokens, since a run on the same inputs returns the same judgments (seen on turn's README,
  2026-10-15, where a second run on unchanged inputs made the same document again, a part the
  purpose did not need included), and each further run raised finer points the purpose did not
  need.
- Only what the user alone can decide reaches the user: writ settles a point from the request, the
  repository or the sources alone, puts to the user what these do not settle, and does not ask at
  all a point the purpose does not need. Protects: asked what Claude alone would guess and only
  that, questions answered.
- Each call brings everything settled so far, and writ keeps nothing between calls: what was decided
  lives in the conversation or in the calling step, as the request and its answers, and what writ
  decided or left goes back to the caller in the report. So a call from a calling step and one from
  the user go the same way, and a call that ends leaves nothing behind but the document, the content
  file and turn's evidence. Protects: `writ:up` from a calling step, judged from the report.

### B-13: An approach for each quality
- Picking the checklists. Brings about: a checklist for each kind, writ's checklists, a checklist
  writ made. Idea: every checklist found for the kind goes to turn, and for a kind with none, the
  user first chooses whether to have one made, before any other point, since every other point
  rests on the checklists. writ tells the kind from the request, from its words or from the path
  and the document there; a script finds writ's checklist for the kind and one at
  `.writ/checklists/<kind>.md`, and writ also takes each checklist that a found one's opening says
  applies with it, as the README checklist's says of the checklist for every document. To have one
  made, writ makes it first as a document of the kind "checklist", against the checklist for
  checklists, heard from the user like any other, and writes it to `.writ/checklists/<kind>.md`;
  the request then goes on with it, one after the other, never one inside the other. Who takes
  part: the skill, a script, the user. Weighed: writ's own checklists changed in a user's
  repository, as a checklist made is; not chosen, since on a user's machine they sit in writ's
  installed folder, outside git, and an update replaces them. Weighed: the checklist for every
  document alone, without asking, for a kind with none; not chosen, since a kind the user writes
  again is better served by its own checklist, and only they know whether they will. Weighed:
  making the checklist inside the document's job, as a job started inside another; not chosen,
  since the document's open points rest on the checklist, so it is made first.
- Hearing the user. Brings about: asked what Claude alone would guess and only that, questions
  answered, missing tools, `/writ:up`, `writ:up` from a calling step. Idea: writ settles every open
  point it can look up, and of the rest asks only those the purpose needs or the test leaves
  undecided, one point at a time, each with a recommended answer and its ground: the way of a
  careful interviewer working down a tree of decisions, as in mattpocock's `grilling` skill, each
  branch walked, a decision settled before those that rest on it, such as the reader before what
  the document must give them. writ goes through every item of the checklists against the request,
  the repository and the sources; what these, or the documentation of what they use, can settle,
  writ looks up instead of asking; a point the purpose does not need is not asked, and if turn
  finds it still open and returns it as a question, it is judged as in Judging what turn returns.
  Before any question, a check written for sh, since python3 itself may be missing, looks for
  python3 and jq, and writ stops saying what to install if either is missing. writ tells its caller
  from the call itself: a calling step says, as it starts writ, that it is one, and brings the
  request with every decision it has made as answers; any other call is the user's. Whether writ
  runs in a subagent is not looked at, since a calling step may run in the main conversation.
  Started by the user, writ asks one point per question, since with several the user answers the
  one they follow and the rest go half-decided (the user's own experience, 2026-10-14); started by
  a calling step, it asks nothing and
  returns at once every open point it would have asked, each with its recommended answer, and the
  call ends; the calling step decides them and starts writ again with the same request and its
  answers. Who takes part: the skill, the user or the calling step, a script for the tools. Weighed:
  depending on `grilling` instead of taking its way into writ's prompt; not chosen, since installing
  it brings 27 skills, it starts on any mention of "grill", and its tags cannot pin a version (found
  on 2026-10-14, when it was tagged `v1.3.1`). Weighed: every ready question at once, as `grilling`
  asks in its versions after 2026-07-13; not chosen, since up to that version it asked one at a
  time ("Asking multiple questions at once is bewildering"), which the user has used and found
  right. Weighed: a script that refuses to start turn until the content file has an entry for every
  item; not chosen, as more than a thin wrapper of turn calls for: an item whose form is turn's has
  no entry, and whether each item is met is turn's to decide. Weighed: a place in the repository for
  the questions being asked; not chosen, since the answers live in the conversation or the calling
  step.
- Writing the content file. Brings about: handed on without reading it over, judged from the
  report, the content file. Idea: writ writes down, item by item, what the document must say or do
  for its reader, and nothing of how it is written, so turn reads each line as content to give and
  makes the form against the checklists. For each item, what the document must say or do for this
  reader and use: for a document, its facts, decisions, examples, the meaning of its terms, and
  what it leaves out; for code, what it does, the inputs it stops and lets through, what a stop
  tells its user, what it needs to run, and the reasons for its decisions; only the caller knows
  these. Each is taken from the request, the repository, the sources, the answers, or a document or
  code already there that writ has read, so nothing in it is a guess; where exactness matters, such
  as a command, what a screen shows or an error's text, the value itself is written. A document the
  user already has is read by writ, and what it says goes into the content file the same way; turn
  makes the document anew and is not handed the old one, since what it is handed it follows,
  wording and slips included (assumption, from turn's own design, which has turn make new work
  only). Who takes part: the skill. Weighed: the content written into the task's answers; not
  chosen, decided by the user (2026-10-15) after eleven rules turn returned piled up beside the
  answers in one task's constraints and pushed into the work what the caller had not asked.
- Handing the task to turn. Brings about: handed on without reading it over, nothing of the user's
  lost. Idea: writ hands turn one task with everything turn works from, and turn works from it
  alone: where the document goes, its reader and their use, what they must be able to do, the
  checklists, the content file, each file or folder the document follows or draws on, such as code
  it describes, and what the reader opens with it; and starts `turn:up` with it. A file where the
  document goes with changes git does not hold is turn's to stop; writ adds no check of its own.
  Who takes part: the skill, turn. Weighed: checking for changes git does not hold before the first
  question, so the user is not heard and then refused; not chosen, since turn's check already stops
  the case and this repository's plugin rules add no special path for it. Weighed: a hook that
  stops any write of the document but turn's while writ is at work; not chosen, since writ finishes
  what turn returns itself.
- Judging what turn returns. Brings about: handed on without reading it over, asked what Claude
  alone would guess and only that, questions answered, time and tokens. Idea: turn returns a
  document that meets the checklists from what it was given; writ judges it by the purpose,
  finishes it itself, and runs turn again only when what turn was given must change. writ reads
  the document as its reader would, and the CCS turn returned, by the test of what the purpose
  needs. Where serving the purpose needs a large change in what turn was given, such as a gap or
  a mistake in the content file, or an answer that changes much of the document, writ corrects the
  content file or the task and runs turn again, making the document anew, and only then, since a
  run on the same inputs returns the same judgments. Where writ can make the document serve the
  purpose by changing it, such as a part the reader does not need, a slip, or an answer the user
  gave that fits in a few lines, it changes it after turn's last run and is done, each change going
  into the report with why; the order holds because turn writes over a file only when git holds it
  or it is the document a run returned unchanged, so a change of writ's own before another run
  would stop that run. writ weighs each question and item not met that `ask the user` holds as an editor
  sorts a reviewer's notes into those the author must settle and those the piece does without; the
  test, not the editor's feel, decides where the line falls, and one the purpose does not need goes
  into the report with the use or decision of the reader that does not rest on it. A question the
  purpose needs and only the user can decide, and a question or an item the test leaves undecided,
  go to the user one at a time with a recommended answer, at the end, as the README promises; and,
  on `to the caller`, the point itself, when the request, the repository and the sources do not
  settle how to correct what writ wrote; started by a calling step, writ returns these to the
  calling step instead. On `stopped`, the user's words change what turn is given, so writ corrects
  the content file or the task from them and runs turn again. A rule turn returns goes into the
  report; whether it reaches a checklist or the caller's later work is the caller's to decide. Who
  takes part: the skill, turn, the user or the calling step. Weighed: running turn until every item
  is met; not chosen, since each run raised finer questions, such as tabs, encodings and line
  endings, that the purpose does not need (seen in three runs on the CSV tool's README,
  2026-10-14), so time and tokens grew with nothing gained. Weighed: turn making every change, writ
  changing nothing itself; not chosen, since a run on unchanged inputs repeats turn's judgment and
  makes the document again from it, so a part the purpose does not need, which turn added for an
  item, comes back (seen on turn's README, 2026-10-15). Weighed: putting every question turn
  returns to the user; not chosen, since the user would answer questions the purpose does not need;
  a point writ cannot judge either way goes to the user, so the risk lies only in a point the test
  seemed to decide (assumption: a point writ judged not needed that the user would have wanted
  settled is not yet seen in a trial), which the report puts first for them to see.
- The report. Brings about: judged from the report, the report holds. Idea: the report puts first
  what the caller decides, and gives each item met only its lines, so reading it never costs what
  reading the document over would. First, each with its ground: each rule turn returned; each
  question turn left open that writ judged the purpose does not need, with the use or decision of
  the reader that does not rest on it; each item left not met, with why writ left it, by the same
  test or by the user's choice, and how it would be met; each change writ made to what the request
  asked, when turn returned `to the caller`; each point writ settled itself, with the request, the
  repository or the source it settled it from; and each change writ made to the document after
  turn, with its lines and why, since turn's reader did not read it. Then each checklist with its
  name and version, each item met with the lines turn named, as they stand in the document handed
  back, and where the content file is. A script writes the report from turn's evidence and returned
  CCS, with writ's judgments beside what they concern, so the report is the same every time and
  cannot show met an item turn did not. Who takes part: the skill, a script, the caller. Weighed:
  Claude writing the report from the evidence; not chosen, since a script gives the same report
  every time and cannot show met an item turn did not, at the cost that the script rests on the
  form of turn's evidence, which turn's design leaves free to change beyond the places a returned
  CCS points to, so writ's dependency on turn names the versions its report is tested on. Weighed:
  no report, the user opening turn's evidence; not chosen, since the evidence keeps each item in
  turn's own files, where the user would have to learn turn's forms to judge the document. Weighed:
  writ adding what turn returned to a checklist itself; not chosen, since only the caller knows
  whether a finding holds beyond this document.
- Installing with turn. Brings about: installs with turn. Idea: installing writ installs turn, since
  writ's manifest names turn among its dependencies, and the manifest passes `claude plugin
  validate --strict`, alone and in the marketplace. Who takes part: writ's manifest, Claude Code.
  Weighed: telling the user to install turn as well; not chosen, since a user who misses it gets a
  writ that cannot work.
