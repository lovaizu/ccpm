# What rn's prompts say

The work is seven files that serve one purpose, the conductor's prompts: the skills
`rn/skills/up/SKILL.md`, `rn/skills/ty/SKILL.md`, `rn/skills/gm/SKILL.md` and
`rn/skills/dn/SKILL.md`, each a command the user types, and three files the skills name and the AI
reads when a step calls for them: `rn/references/conduct.md`, how the conductor carries a session,
`rn/references/record.md`, the session's record and where the session stands, and
`rn/references/upgrade.md`, how a session recorded by an rn before 0.9.0 is brought to the current
form, read only when such a session is found.

## prompt

### B-1: What is expected
- `up`: start a session from the words the user gave, or take up the session on the branch where
  it stopped, and carry the work to the next sign-off; one command serves both, since the record
  tells whether a session is there.
- `ty`: approve the sign-off the session is waiting for, record it, and stop.
- `gm`: record the user's feedback on the sign-off waited for, from the words given or from the
  user's comments on the pull request, and stop, so the session goes back to before that sign-off.
- `dn`: pause the session anywhere, leave what the next conversation needs, push everything, and
  stop.
- `conduct.md`: the AI is the conductor, the main conversation with the user, the same one
  throughout the session; it alone decides every next move and uses git; it hears what the user
  really wants one point at a time, writes for each piece of work what it must say, hands turn one
  task for it, judges what turn returns by the work's purpose, and proposes at each sign-off. turn
  makes every work, the plan, the README, the design document, the verification document, each
  task's result, the deliverable's use and each proposal, has it read or used by an AI that did not
  make it, as its receiver would, and checks each item of its checklist. The conductor makes
  nothing the user sees itself but the record and what it finishes after turn's last run.
- `record.md`: what a session's record is, so a fresh conversation and every later version of rn go
  on from it alone.

### B-2: Why it is needed
- The user should have the goal they really want achieved, spending their time only on the three
  sign-offs and on what only they can decide; the more they are asked, the less they can leave the
  work to the conductor. Every stop is a point where the user may clear the conversation, and a
  later one knows only the record, so everything decided is pushed as it is decided.
- `up`: every piece of work and every decision rests on the goal set at the start, so the goal must
  be what the user really wants, not their first words; and the user comes back without
  explaining anything again.
- `ty`: the approval becomes the ground all later work stands on, so the session goes on from it
  without asking again.
- `gm`: feedback shows the user and the session do not yet see the same thing; the words are kept
  whole, since the work is measured by them, and a summary would shift that measure.
- `dn`: the next conversation knows only the record, so everything it needs is left there.
- `record.md`: the layout, names and markers stay exactly as written, since the commands and checks
  find their way by them.

### B-3: Everything that must happen every time
- `up`: run `sh "${CLAUDE_PLUGIN_ROOT}/scripts/tools.sh"`, and when it exits with 1 show what it
  printed and end; read `record.md` whole and find the session as it says; a session there → take
  it up; none and no words → say so and end; none and words → start: when the working tree has
  uncommitted changes, say so without touching them and end; work on a new branch named `{slug}`,
  the slug naming what the words ask for in a word or words joined by hyphens, from the latest
  default branch, pushed to a branch of the same name on the remote, in `.rn/{yyyymmdd}-{slug}/`; ask the user, as one point, the two languages, proposing
  what the repository and the user's instructions already set, or else English for the repository
  and the user's own for the talk, so a single yes settles both; write `steering.md` in the form
  `${CLAUDE_PLUGIN_ROOT}/checklists/plan.md` gives, with the languages, `rn` from
  `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` and the goal as the words give it for now;
  commit and push in the artifact language with the subject and decision line record.md gives,
  `● plan ── started → working out the plan`; open a draft pull request titled with the goal in one
  line, its body linking `steering.md`, write its URL in `pr`, commit and push with `● plan ──
  pull request opened → working out the plan`; then go on as conduct.md says from Working out the
  plan. Taking up: when an older rn started it, bring it to the current form as record.md says;
  say where it resumes, `● {resuming {slug} at #{id}: {task name}, or at the next move of the last
  decision line}`; when the last decision line ends `waiting for #{id} {sign-off name}` and the
  branch is level with the latest default branch, give the proposal again as that commit's message
  body prints it, the decision line included, translated into the conversation language when the
  two differ, adding nothing and leaving nothing out, and end; otherwise go on as conduct.md says
  from Taking up the session, with any words the user gave as what they say.
- `ty`: find the session as record.md says; when the last decision line does not end `waiting for
  #{id} {sign-off name}`, say what the session is doing and end; mark that task `[x]` in
  `steering.md`; at the Deliverable sign-off set `status` to `finished` and mark the pull request
  ready with `gh pr ready`; commit and push with `● #{id} {sign-off name} ── approved → {the first
  task not [x]; planning the tasks, after the Design sign-off; finished, after the Deliverable
  sign-off}`; say the decision line and `Say "go on", or /clear and then /rn:up.`, or at the
  Deliverable sign-off that the pull request is ready with its URL and the merge is theirs; when
  the user says to go on, go on as conduct.md says from Taking up the session.
- `gm`: find the session as record.md says; when the last decision line does not end `waiting for
  ...`, say what the session is doing and end; the feedback is the words given, or without them
  every comment the `gh` user wrote on the pull request after that stop commit, on a line or on the
  whole, each with its place and URL; neither → ask the user for their feedback and end; write it
  whole, in their words, to a `feedback` item in `open/`; commit and push with `● #{id} {sign-off
  name} ── feedback in {file} → {working out the plan or the design again, or tasks for it}`; say
  the decision line and `Say "go on", or /clear and then /rn:up.`; when the user says to go on, go
  on as conduct.md says from Taking up the session.
- `dn`: find the session as record.md says; when the last decision line ends `waiting for ...`, say
  it is already stopped there, safe to clear, and that `/rn:ty` or `/rn:gm` answers it, and end;
  when turn is at work, stop it with Esc as turn's callers' page says, so its work stays in its
  evidence; write to a `notes` item in `open/` what the next conversation needs and nothing else
  records: what was under way and how far it came, the task's decisions file and the last task
  handed to turn when a task was under way, and in a talk with the user the points agreed and the
  point still open; commit and push with `● {#id task name | plan | design} ── {how far it came} →
  paused at {#id task name | plan | design}`; end, opening the message with the map as the proposal
  checklist gives it, the task under way as `👉 #{id} {task name} ── paused here`, then the decision
  line, then `Next: /clear, then /rn:up.`.
- `conduct.md`, every section as a step the conductor takes, in this order and with these
  contents:
  - The frame: `up.py` is `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/up.py"`, run from the top of
    the repository; when a command exits with 1, do what it says and run it again; read record.md
    whole once at the start of a conversation; say everything to the user in the
    `conversation-language` of `steering.md` and write everything that goes into the repository
    in its `artifact-language`, but the user's feedback, which stays in their own words; start
    every agent in the foreground and wait for it, since an agent left running in the background
    reports to a turn that has ended; the turn ends only at a stop for the user, with a question
    to them, or with an answer to what they asked.
  - Taking up the session: read `steering.md`, `open/` and the last decision line, and take up its
    next move; first merge the latest default branch in, keeping both sides' intent where they
    conflict, and when that changes what the plan or the design rests on, work it out again
    before the next sign-off; a `notes` item from `/rn:dn` says what was under way: a task goes on
    from it, a talk from the point still open, and the item is settled in the first commit after;
    a `report` left unsettled is settled first; a `feedback` item is taken up as Feedback says;
    keep going until a stop for the user.
  - Working out the plan: talk one point at a time until nothing is silently assumed; what is to
    be decided is a tree, and only a point whose prerequisites are settled is asked; an intent
    question asks why the user wants the goal and what a result should do for them or their
    users, giving what was understood so far and gains seen, but no recommended answer and no
    way, and its answer is written in the user's words as an attractive criterion, what must not
    happen being must-be quality; what the user really wants is found from the purpose behind
    their words and the ideal it calls for; a means question offers ways only where the criteria
    allow ways that give different things, names the criteria it serves, offers only ways that
    give what they say, each with what it gives and costs and the one recommended and why; facts
    the repository, the official documentation or best practice can settle are looked up, never
    asked; a fact none can show, such as what the user's records hold, is asked; each kind of input
    the goal speaks of, such as "a user with no name", has every form it takes where the product
    runs asked unless the repository shows them, and what the product does today is checked on
    each; what the user does not know but says to go on with is an `Assumption`; the languages,
    the issues the work closes or serves and the pull requests it replaces are among the points.
    Each point is written into the plan's decisions as agreed: `up.py decisions <session folder>
    <steering.md's path>` once for where the decisions file goes, then item by item of `plan.md`,
    committed and pushed; the pull request's title stays the goal; until the Design sign-off is
    approved the only tasks are the Plan and Design sign-offs, and what the deliverable needs goes
    under Not yet specified. When nothing is left to settle, turn makes the plan as Making a work
    through turn says, `steering.md` as where it goes, the user as receiver, the checklists `up.py
    checklists plan` prints, what the repository holds that the plan draws on as references; then
    the Plan sign-off, as Stopping for the user says.
  - Working out the design: one point at a time as above, the user asked only what the product
    should be and what trades effort against safety; each point agreed goes into the decisions of
    the document it belongs to, the README, the design document or the verification document, at
    the place `up.py decisions` gives, committed and pushed; the verification document holds where a
    run starts, how it goes, for each attractive criterion the fewest golden-path scenes that show
    the user getting it, each with what is put in and what must happen, and the machine checks as
    commands naming the criteria they check, each scene's input and pass fixed here since fixed
    after they could be chosen so that the work passes; turn makes each of the three documents,
    the README first, each with its reader as receiver and the checklists its kind gets, even when
    no point changes a document, since there is always a Design sign-off; then the Design sign-off.
  - Planning the tasks: once the Design sign-off is approved, the tasks that make the deliverable
    are planned, numbered on from the sign-offs, the Deliverable sign-off after them: decisions
    settled one at a time, each before the tasks that rest on it; each task with its purpose, the
    criterion IDs it serves, and Completion criteria split into Attractive quality and Must-be
    quality, each a state checked on the real thing; tasks that raise attractive quality first,
    must-be quality last; what cannot yet be stated under Not yet specified; written into
    `steering.md`, committed and pushed, and the tasks carried out without stopping; after a later
    Design sign-off, the tasks not yet done are revised by the design it approved.
  - Carrying out a task: turn makes the task's result as Making a work through turn says, its files
    as where the work goes, whoever the task's purpose serves as receiver, the design and the
    repository's rules as what it follows, and the checklists its kind gets, `code` for code and
    its tests; the conductor checks what turn returned against the task's purpose on the real
    thing and says what it decided in one line, `● #{id} {task name} ── decided: purpose fulfilled
    → {next}` or `── decided: purpose not fulfilled ({why}) → fix`, correcting the decisions and
    having turn make it again; falling short the same way again means the work cannot go on; a
    result the design does not let it fulfil is a fix to the design, so back to Working out the
    design; something only the user can decide is asked; commit and push, the task marked `[x]` in
    the commit that settles its report. When the tasks planned after the last Design sign-off are
    done, the deliverable is used once: a task for turn whose work is the files the session
    changed, whose receiver is the product's user and whose checklist is the verification
    document, so turn uses the product in each scene; the conductor runs the machine checks; the
    decision line is `● deliverable ── used → ...`; each More to fix becomes a task added before the
    Deliverable sign-off, with the scene it fell short in as its Completion criteria, and carried
    out as a task, checked on the real thing against that scene; the whole is not
    used again, since each fresh use raises points that are not essential; then the learnings
    taken stock of: every `rule` turn returned in the session, `jq -r '.semantic_gist[]? | .rule //
    empty' <session folder>/tasks/*.back.json`, each put to the user one per message as Asking the
    user says with a recommendation, an item for `.rn/checklists/<kind>.md`, an issue opened with
    `gh issue create`, or letting it go, done as the user decides and recorded in the commit that
    settles the question; then the Deliverable sign-off.
  - Making a work through turn: `up.py decisions <session folder> <the work's first file>` for where
    the decisions file goes, written as Writing the decisions says; `up.py checklists <kind>` for its
    checklists; the kinds: `plan` for the plan, `readme`, `design` and `verification` for the
    three documents, `proposal` for a proposal, `code` for code and its tests, and for any other
    document its kind or `doc`; the deliverable's use takes no kind: its checklist is the session's
    verification document itself; a kind with none is made first with the user against
    `${CLAUDE_PLUGIN_ROOT}/checklists/checklist.md`, with `up.py checklists checklist`, written to
    `.rn/checklists/<kind>.md`; `up.py task <session folder>` with `--deliverable` each file,
    `--receiver`, `--use`, `--acceptance`, `--checklist` each checklist, `--decisions`, `--reference`
    each file or folder the work follows or draws on, the plan and the design among them, `--opens` each file the receiver opens with
    the work, `--language` the artifact language, which prints `in:` and `out:`; the `turn:up`
    skill called with those two lines as its arguments, as printed, and waited for, since turn asks
    nothing while it works; what turn returned judged as Judging what turn returns says; the
    judgments file `<in path without .json>.judged.json` written with `jq`: `decided` (each point
    settled on its own, `{"point", "ground"}`), `questions` (each `question` turn returned,
    `{"question", "judged"}`), `unmet` (each `unmet` item, `{"item": "<its ID>", "judged"}`),
    `changed` (each change made after turn, `{"lines", "why"}`); `up.py report <out> <that file>`
    prints the report, written to a `report` item in `open/` and settled as record.md says.
  - Writing the decisions: for each item of the checklists, what was decided for this work that the
    item needs, what it must say or do and what it leaves out, from the plan, the design, the user's
    answers and the points agreed; each a plain statement, with the value itself where exactness
    matters, such as a command, what a screen shows or an error's text; what the work draws on as
    it stands, the plan, the design, the code it describes or a document already there, handed as a
    reference instead of copied, since turn's generator reads each reference where it stands and a
    copy drifts from its source, so the decisions hold only what no reference holds; the file's
    form, so turn reads each line as a decision for one item, its order and lists being notes to
    turn and not the work's shape: `# Decisions for <the work's path>`, `## <checklist name>`,
    `### <item ID>: <item title>`, then bullets of what the work must say or do, or leave out;
    every entry read back and each that a reference holds, or that is not what the receiver gets,
    taken out.
  - Judging what turn returns: the CCS at `out` and the work read as its receiver would, by the one
    test: a question or an item is needed when the receiver's use, or a decision of the user's,
    rests on it; `done`: nothing left; `ask the user` or `to the caller`: a question the purpose
    needs and only the user can decide, or one the conductor cannot judge either way, asked now,
    one per message; then where serving the purpose needs a large change in the decisions, a gap, a
    mistake, an answer that changes much of the work, the decisions corrected and turn run again,
    and only then, since turn on the same inputs returns the same judgments; otherwise where the
    work can be made to serve the purpose by changing it, an answer of a few lines put in or a
    part the receiver does not need taken out, changed now, after turn's last run, since turn
    writes over a file only when git holds it, each change's lines and why kept for the report; a
    question or item the purpose does not need left, with the use or decision that does not rest
    on it, in the report; `stopped`: the decisions corrected from the user's words and turn run
    again; no CCS at `out`: turn ended before any work and said why, which is put to the user. On
    each item, what the receiver gains is a Good, which a fix must not take away, and what they
    will struggle with is a More; a More that brings an attractive criterion closer, or a must-be
    gap met on the golden path, is fixed; any other must-be More is let go with its reason, since
    hunting such gaps never ends; where whether a More brings the work closer turns on what the
    user wants and the criteria do not say, the user is asked that as an intent question; the work
    cannot go on when the same More keeps coming back, each fix brings a new More, or a fix needs
    the design changed, and then the plan or the design is worked out again, that More first, and
    the session stops at that sign-off again; a fatal More, one without whose fix the goal cannot
    be achieved and whose fix only the user can decide, does the same; when Mores contradict each
    other, something is undecided in the goal or a document, and that is what is decided.
  - Feedback: a `feedback` item goes back to before the sign-off it answers, the plan or the design
    worked out again with the mismatch behind the words as the first point, since fixing only what
    the words say leaves it in place; feedback on the deliverable gets tasks for it, or goes back to
    the design when it changes what the product should be; the item is settled at the next
    sign-off in a commit of its own before the stop commit; once approved, the plan and the documents go back through their
    sign-off, added with the next unused id before the tasks not yet done, only when what they say
    changes without the user having decided it; a change the user made by answering a question is
    written without stopping.
  - Asking the user: one point per message, since with several the user answers the one they
    follow and the rest go by half-decided; the question written to a `notes` item
    `{NN}-notes-question.md`, opening with `Serves:` and the IDs of the criteria a means question
    rests on, or `goal` for an intent question, with how the conductor understands the point and,
    for a means question, each way with what it gives and costs and the one recommended and why;
    committed and pushed, and given to the user as the item holds it, translated into the
    conversation language when the two differ; the item leaves `open/` in the commit that records
    the answer; a question is not a stop.
  - Stopping for the user: only at a sign-off; when the work waits on someone outside, what to do
    meanwhile is a question; at a sign-off every report and feedback is settled, each in a commit
    of its own before the stop commit, whose body is the proposal alone, and the branch has the
    latest default branch merged in; the proposal's decisions are written, the final state only,
    item by item of `proposal.md`: what the conductor proposes next and why it serves the goal; the
    goal and every acceptance criterion as `steering.md` words them; for each attractive criterion
    how far the work now gives it and what came closer since the last proposal; what changed since
    the last approval, from the decision lines, and what the design takes away from what the
    product does today; what was decided for the user with each ground, each shortfall left with
    why, and each `Assumption` as a shortfall under the criterion it puts at risk; each item of the
    work's checklists as its report shows it; turn makes the proposal to `open/{NN}-notes-proposal.md`
    with the user as receiver and the work it proposes on as what the receiver opens; then commit
    and push with the proposal as the message body and `● #{id} {sign-off name} ── proposed: {what}
    → waiting for #{id} {sign-off name}` last, the item leaving `open/` in that commit; and the user
    is given that body as `git log -1 --format=%b` prints it, the decision line included,
    translated into the conversation language when the two differ, adding nothing and leaving
    nothing out.
- `record.md`: the session is its directory `.rn/{yyyymmdd}-{slug}/`, the README, design document
  and verification document its plan names, and git; the plan's own form is
  `${CLAUDE_PLUGIN_ROOT}/checklists/plan.md`. The directory: `steering.md`; `open/`, what is not
  yet settled, one file per item; `decisions/`, what each work was asked to say, one file per work;
  `tasks/`, each task handed to turn and the CCS turn wrote back; `decisions/` and `tasks/` are
  written by `up.py decisions` and `up.py task` and committed with the decision that made them;
  turn's evidence under `.turn/` at the top of the repository is left uncommitted. `open/` names:
  `{NN}-{kind}-{about}.md`, `{NN}` one more than the highest number there or `01`, `{kind}` one of
  `report` (the report `up.py report` printed for one work, such as `04-report-task-3.md`),
  `feedback` (the user's words from `/rn:gm`, whole, in their own language), `notes` (a question
  being put to the user, a proposal being made, or where a task stands on `/rn:dn`; a question's
  first line is `Serves:` with the criterion IDs it rests on, or `goal`); `{about}` names what it
  is about, `plan`, `design`, `task-3`, `deliverable`, a question `question`, a proposal
  `proposal`, since the checks find them by these names; an item leaves `open/` in the commit that
  settles it, copied whole into that commit's message under its file name, each line indented by
  four spaces,
  with what was decided on each shortfall as `- Good A1: <what the user gains, at path:line>`,
  `- More A1: <what the user will struggle with, at path:line>` and, on its own line indented
  under the More, `→ fixed: <how> | → let go: <why> | → to the user: <the question, or back to the
  plan or the design>`. The decision line:
  every commit the conductor makes has a subject line saying what it records, such as `rn: settle
  the report on #3 move src/cart`, and ends with `● {#id task name | plan | design | deliverable}
  ── {what was decided} → {next move}`, the first being `● plan ── started → working out the plan`;
  `●`, `──`, `→`, `waiting for`, `paused at`, `approved` and `feedback in`, and `Good` and `More`
  with their criterion ID at the start of a line, stay as written whatever the artifact language;
  the last decision line on the branch is where the session stands; the stops and what each leaves
  in `open/`: at a sign-off, with the proposal as the message body, `→ waiting for #{id} {sign-off
  name}`, nothing; after `/rn:ty`, `── approved → {the next task, or finished}`, nothing; after
  `/rn:gm`, `── feedback in {file} → {working out the plan or the design again, or the tasks for
  it}`, the `feedback` item; a pause on `/rn:dn`, `→ paused at {#id task name, plan, or design}`,
  whatever is unsettled and a `notes` item on where the task stands. Finding the session: the
  `steering.md` this conversation has been working on; otherwise the one the current branch
  changed whose `status` is not `finished`, by `git diff --name-only $(git merge-base HEAD
  origin/HEAD) HEAD -- '.rn/*/steering.md'` (`git remote set-head origin --auto` first when
  `origin/HEAD` is not set); none and `/rn:up` was given words → start a session from them; none
  and no words → say there is no session on this branch, check out the session's branch or give
  `/rn:up` what to do; only one whose `status` is `finished` → say it is finished; either way end.
  A session whose `rn` field is `0.9.0` or later is taken up as it stands; one with no `rn`
  field, or lower, was started under an earlier rn: `/rn:up` brings it to the current form as
  `upgrade.md` says, any other command asks the user to run `/rn:up` first and ends.
- `upgrade.md`: the old record is the user's request and what was done so far, and the goal is
  worked out again from it, since an older record may not hold why the user wants the goal; read
  the old `steering.md` and whatever else the old version left; work out the plan as `/rn:up`
  does on a start, with the session's branch, pull request and directory in place of new ones and
  the old record as the request, asking only what it leaves unclear; the first write of the new
  `steering.md` replaces the old one; what an old design the user approved settled goes into the
  design's decisions as agreed points, what was done becomes Facts in Assumptions each saying where,
  the other old files are removed and stay readable in git; stop at a new Plan sign-off.

### B-8: What breaks, set down exactly
- Every command, path, field name, decision line, marker and file name above is written as it
  stands, since rn's scripts and hooks read them.

### B-10: An action hard to undo, asked first
- Each skill runs only on the user typing it (`disable-model-invocation: true`), since each
  commits and pushes, and `/rn:up` opens a pull request; the conductor never commits or pushes
  on the user's default branch, and marks the pull request ready only on `/rn:ty` at the
  Deliverable sign-off.

### B-13: Details read only when needed
- `conduct.md`, `record.md` and `upgrade.md` are files of their own, named in the skills, read
  when a step calls for them, `upgrade.md` only when an older session is found; `${CLAUDE_PLUGIN_ROOT}/checklists/plan.md` and `proposal.md` likewise, for the plan's
  form and the map.

### B-17: Scripts for what must come out the same
- `tools.sh` checks the tools; `up.py checklists`, `decisions`, `task` and `report` give the
  checklists for a kind, the decisions file's place, the task as a CCS and the report; what each
  prints is used as printed.

### B-19: What the user must see, shown by a tool
- The map, the decision line and the proposal are given from the commit's message body as `git
  log -1 --format=%b` prints it; rn's hooks stop a turn that ends in the wrong language or without
  a stop or a question.

### B-21: The scope of its inputs
- The conductor works from the session's record, the repository, the official documentation of
  what it uses, the user's words, and what rn's scripts and turn return; it reads turn's evidence
  only through the report the script writes.

### F-2: Form of what goes in and out
- The skills take `$ARGUMENTS`, the user's words; `conduct.md` names the decisions file's form, the
  judgments file's fields and the task script's flags; `record.md` the record's layout, names and
  the decision line.

## doc

### B-13: One name for each thing
- "the conductor" for the AI running these prompts, "turn" for the plugin that makes each work,
  "the user" for the person, "the record" for the session's directory and git, "a work" for one
  thing turn makes, "the decisions" for what a work must say, "the report" for what `up.py report`
  prints, "a sign-off", "the plan", "the design", "the deliverable", "a Good" and "a More".
