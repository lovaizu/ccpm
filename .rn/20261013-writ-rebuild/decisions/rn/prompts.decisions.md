# What rn's prompts say

The work is rn's three skills, `rn/skills/up/SKILL.md`, `rn/skills/ty/SKILL.md` and
`rn/skills/gm/SKILL.md`, the conductor's steps for each command, from `/rn:up <what they want>` to
the pull request marked ready, as `dev/rn/architecture.md` and `dev/rn/ux.md` give them, each move
taken with `rn/scripts/rn.py` as it is after T29's script changes (`scripts.decisions.md`). Made with
`rn/checklists/product/prompt.md` open.

## Each skill

- Each runs only when the user types it (`disable-model-invocation: true`).
- Each runs `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rn.py" <subcommand>` from the top of the
  repository, uses what it prints as printed, and on a stop does what the stop says; the skill names
  each subcommand and what it prints, and does not say again what the script checks.
- Every move is kept by `rn.py state --message`, or `start`, `answer` or `proposal`, never by a
  plain `git commit` or `git push`; before each, the conductor replaces `<session>/state.json` whole
  with the state for the next move, a CCS in ACC's parts: `episodic_trace` (each checked fact the
  moves brought, the newest last), `semantic_gist` (what holds across moves, such as the user's
  way), `focal_entities` (the stage and the work in hand), `goal_orientation` (the plan),
  `constraints` (the two languages and rules met), `predictive_cue` (the next move, said so a fresh
  conversation can take it), `uncertainty_signal` (what is open) and `retrieved_artifacts` (the
  files the next move reads); each entry `{"<kind>": "<text>"}`. A fact goes in only once checked:
  the user's words, what a script printed, turn's result read at its lines.
- The message says what the move records; for a decision also the options weighed with their
  reasons, and for feedback the feedback whole with its answer, as the documents keep only what
  holds now.
- Everything said to the user is in the plan's `conversation-language`, everything written to the
  repository in its `artifact-language`; before the plan holds them, the user's language and the
  repository's, English where it has none (R17).
- Each skill begins the same way: `cd "$(git rev-parse --show-toplevel)"`, `rn.py session`, which
  prints the session, its state and the sign-off waiting for the user's answer; then read the files
  the state's `retrieved_artifacts` name, whole, and go on by its `predictive_cue`.

## `/rn:up`

`up/SKILL.md` holds the whole course; were it to pass 500 lines, each stage's steps go into a file
under `rn/skills/up/` that the step entering the stage reads whole.

- No session: with no words, say none is on this branch and that `/rn:up <what you want>` starts
  one; end. With words: start, as below.
- A sign-off waiting: give `rn.py proposal <sign-off>` again as printed, with the answer line; end.
- Otherwise go on from the state's `predictive_cue`, the user's words, if any, as what they say now.

### Start

- `rn.py start <slug> --message <m>` makes the branch from the latest default branch and keeps the
  empty state; a working tree with changes stops it, and the conductor says so and ends.
- `gh pr create --draft`, titled with the request in a line, its body linking the plan's path; the
  URL goes into `decisions/plan.decisions.md`'s front matter with `rn` (from
  `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`), `status: running` and the two languages.

### Hearing, at every stage

- The points to decide are found from the user's words, the decisions, the plan where it is there,
  the repository's README and the documentation it points to, and each file the request's words
  name or touch; each point is confirmed with the user, looked-up ones included, one per message, in
  the README's "Points to decide" form (`rn/README.md`), its fixed words in the conversation
  language. Answers to the user's own questions and slips corrected that leave nothing to decide
  come first, apart from the form.
- Each answer goes into the work's decisions, `decisions/<work>.decisions.md`, as an entry
  `## <title>` over one paragraph: what the work must be on that point, with what it is for, short
  enough for the proposal to show as one line; then the move is kept, and the next point asked.
- At the plan: the first point is what the work is for, its answer the goal; then what shows it is
  done, and the rest the plan needs.
- After the plan sign-off: which documents the purpose needs, such as a UX, a README and an
  architecture, made in the order their checklists draw them (UX, README, architecture), each with
  a name, the name its decisions and CCS take; then each document's points, into its decisions.
- During the tasks: each task's step 1, the context it needs read and what is lacking confirmed,
  into `decisions/t<n>.decisions.md`.

### Having a work made

The same move for the plan, each document, each step of a task done by turn, and the deliverable's
reading.

- Remove `<session>/ccs/<work>-result.json` where it is there and the work is to be made again from
  changed decisions; keep the move; then `rn.py ccs <work> <path>... --kind <kind> --receiver <...>
  --use <...> --has <...>`, the receiver and their use from the decisions and the plan.
- Start the `turn:up` agent in the background with the printed line as its whole prompt, hold its
  ID, and say in one line that the work is being made and used in the user's place by an AI that did
  not make it, and that the user can say stop.
- While it runs, pass each line its agents send on to the user, put into the conversation language,
  judging none; each question turn asks goes to the user as a point, its answer into the decisions,
  and back to turn by SendMessage. When the user says stop, TaskStop with the ID, and keep the
  move; the next `/rn:up` calls turn again with the same result, so it goes on from its last move.
- When turn returns, read each item's Good at its lines; a Good its lines fall short of, or an
  item without one, is a point behind it: confirm it with the user where it is theirs, put it into
  the decisions, and have the work made again. The conductor writes no line of a work turn makes
  (architecture: no work turn returns is fixed by the conductor).
- Keep the move with the work, its CCS and the result, which holds turn's lessons for the end.

### The plan, the documents and the tasks

- Plan: heard, made with work `plan`, kind `plan`, path `<session>/steering.md`, receiver the user at
  the plan sign-off and the conductor in later conversations, `--has .`; then the plan sign-off.
- Documents: the plan made again with its Documents from the plan's decisions; each document made
  in order, kind its own (`ux`, `readme`, `architecture`, or the user's); then the design sign-off.
- Tasks: the conductor divides the work into tasks by rn's plan checklist, the tasks go into the
  plan's decisions, and the plan is made again with them; this is not a point to decide, as the UX
  has rn divide the work. Each task in order, each step as the plan says it: step 1 heard; steps 2
  and 4 each a run of turn on work `t<n>`, its path and kind as the step names them, the first run's
  first user doing step 3; each step ticked in the plan once done and kept.
- Before each step of a task, one line to the user of what it will do, how far and how; after it,
  what is done and what comes next. A step the user stops goes the way they then say, as a point.
- After each task, the state replaced from what it brought, the plan's goal, criteria and next
  tasks weighed against it: a change to the goal or a criterion is a point to decide; a change to
  the tasks makes the plan again.
- Deliverable: once every task is done, work `deliverable`, kind `deliverable`, no path given (the
  script names every file the branch changed outside `.rn/`), receiver the user at the deliverable
  sign-off, use checking that the finished work does each acceptance criterion; then the
  deliverable sign-off.

### A sign-off

- Keep the state, whose `predictive_cue` says the sign-off waits and what `/rn:ty` and `/rn:gm`
  lead to; then `rn.py proposal <plan|design|deliverable>`; reply with what it printed, as printed;
  end. A stop saying the core decisions do not fit is a sign the work is not yet simple: settle its
  points again more simply with the user and have it made again.

### After feedback

- The state holds the feedback, kept by `/rn:gm`. Find the point behind it, one rn decided wrong or
  did not ask; confirm it as in Hearing, rewriting a settled entry where the answer changes it; have
  each work it touches made again; stop at the same sign-off, whose proposal shows what changed.

### The end

- After the deliverable is approved: `rn.py lessons` and the `lessons` of each `ccs/*-result.json`
  are the learnings; each is put to the user one per message in the README's "Learnings to decide"
  form, with where it is recommended to go: the user's `.rn/checklists/<kind>.md`, an issue to
  `lovaizu/ccpm`, both, or neither. An issue holds the need and its points alone, never the user's
  source, is shown to the user whole and opened with `gh issue create` only on their yes. Each
  answer is kept before the next.
- Then `status: finished` in the plan, kept, and `gh pr ready`; tell the user the pull request is
  ready to merge, and that the merge is theirs.

## `/rn:ty`

- No session, or no sign-off waiting: say what the session is doing, from its state, and that
  `/rn:up` goes on; end.
- Replace the state with the approval as a fact and the next stage as its cue, then `rn.py answer
  approved --message <m>`.
- The learner on the stretch just answered: `rn.py records`; start `rn:learner` with what it
  printed as its whole prompt and wait for it; `rn.py learnt`, sending the learner what a stop says
  by SendMessage until it passes; replace the state and keep the move.
- Then go on: read `${CLAUDE_PLUGIN_ROOT}/skills/up/SKILL.md` whole and take its steps from where
  the state now stands, as the README has the work go on after `/rn:ty` with nothing more typed.

## `/rn:gm <feedback>`

- No session, or no sign-off waiting: as `/rn:ty`. No words: ask for the change after `/rn:gm`; end.
- Replace the state with the feedback whole as a fact and the next move, finding the point behind
  it, as its cue; then `rn.py answer feedback --message <m>`, the message naming the sign-off and
  holding the feedback whole.
- The learner on the stretch, as `/rn:ty` runs it.
- Say `Your feedback is kept. Clear the conversation if you like, then type /rn:up to go on.`, in
  the conversation language; end.
