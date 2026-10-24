# What rn's prompts say

The work is rn's three skills, `rn/skills/up/SKILL.md`, `rn/skills/ty/SKILL.md` and
`rn/skills/gm/SKILL.md`, the orchestrator's steps for each command, from `/rn:up <what they want>`
to the pull request marked ready, as `dev/rn/architecture.md` and `dev/rn/ux.md` give them, each
move taken with `rn/scripts/rn.py` as `scripts.decisions.md` gives it. Made with
`rn/checklists/product/prompt.md` open. The words are orchestrator, not conductor, and learnings,
not lessons (agreed with the user, 2026-10-24).

## Each skill

- Each runs only when the user types it (`disable-model-invocation: true`).
- Each runs `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rn.py" <subcommand>` from the top of the
  repository, uses what it prints as printed, and on a stop does what the stop says; the skill names
  each subcommand and what it prints, and does not say again what the script checks.
- Every move is kept by one of rn.py's subcommands, never by a plain `git commit` or `git push`,
  and the orchestrator never edits the steering: it gives rn.py the next move, `--next`, as the step
  of `/rn:up` by its number and on what, so a fresh conversation can take it from the steering
  alone, and what is open, `--open`, each a fact checked: the user's words, what a script printed,
  turn's result read at its lines.
- The message says what the move records; for a decision also the options weighed with their
  reasons, and for feedback the feedback whole with its answer, as the steering and the calls keep
  only what holds now.
- Everything said to the user is in the steering's `conversation-language`, everything written to
  the repository in its `artifact-language`.
- Each skill begins the same way: `cd "$(git rev-parse --show-toplevel)"`, `rn.py session`, which
  prints the session, its stage and the sign-off waiting; then the steering read whole, and the step
  its Next names taken.

## `/rn:up`

`up/SKILL.md` holds the whole course; were it to pass 500 lines, each stage's steps go into a file
under `rn/skills/up/` that the step entering the stage reads whole.

- No session: with no words, say none is on this branch and that `/rn:up <what you want>` starts
  one; end. With words: start, as below.
- A sign-off waiting: give `rn.py proposal <sign-off>` again as printed; end.
- Otherwise go on from the steering's Next, the user's words, if any, as what they say now.

### Start

- The first point is the two languages, proposed from what the repository and the user's
  instructions set, else the user's for talk and English for the repository (the languages agreed
  for `dev/architecture.md`); on the answer, `rn.py start` with a title of the request in a few
  words, which opens the draft pull request.

### Hearing, at every stage

- The points to decide are found from the user's words, the steering, the work's decisions in its
  latest call, the repository's README and the documentation it points to, and each file the
  request's words name or touch, each read whole; what a task's first step must find out is found
  out, by reading or by trying it. Each point is confirmed with the user, looked-up ones included,
  one per message, in the README's "Points to decide" form, its fixed words in the conversation
  language; answers to the user's own questions and slips corrected that leave nothing to decide
  come first, apart from the form. A word of the user's read wider or narrower than said is a point
  of its own.
- Each answer is kept with `rn.py decide <work> --title <t> --says <s>`: what the work must be on
  that point, with what it is for, short enough for the proposal to show as one line, never how it
  was reached, which the message keeps; then the next point asked.

### Having a work made

The same move for the plan, each task's runs, each checklist, the deliverable's reading and the
learnings.

- `rn.py ccs <work> [<path>...] --kind <kind> --receiver <...> --use <...> --has <...>`, then the
  `turn:up` agent in the background with the printed line as its whole prompt, its ID held, and one
  line to the user that the work is being made and used in their place by an AI that did not make
  it, and that they can say stop.
- While it runs, each line its agents send passes to the user in the conversation language, judged
  not at all; each question turn asks goes to the user as a point, kept with `rn.py decide`, and
  back to turn by SendMessage. On stop, TaskStop with the ID, the move kept with Next saying the
  same call is made again, as turn goes on from its last move.
- When turn returns, each item's Good is read at its lines; a Good its lines fall short of, or an
  item without one, is a point behind it: confirmed with the user where it is theirs, kept as a
  decision, and the work made again. The orchestrator writes no line of a work turn makes.
- The move is kept, with `--put <nnnn>` for `plan` and `learnings`.

### The stages

- Plan: the purpose and what shows it done heard as decisions of `plan`; `plan` made, kind `plan`,
  receiver the user at the plan sign-off and the orchestrator later, `--has .`, its tasks those that
  reach the plan; each task done as below, its making a call on `plan`; then the plan sign-off.
- Design: which documents the purpose needs, such as a UX, a README and an architecture, heard as
  decisions of `plan`, in the order their checklists draw them; `plan` made again, a task for each;
  each task done; then the design sign-off.
- Build: `plan` made again with the tasks that build the finished work; each task done; after each,
  `plan` made again from what it brought, a change to the goal or a criterion first a point to
  decide; once every task is ticked, the stage moved to deliverable, `deliverable` made, kind
  `deliverable`, no path, receiver the user at the deliverable sign-off, use checking that the
  finished work does each criterion; then the deliverable sign-off.
- A task: each step as the steering says it, before it one line to the user of what it will do, how
  far and how, after it one line of what is done and what comes next; the orchestrator's step heard
  as decisions of the task's work, turn's steps each a call, the first run's first reader doing the
  trace; each step ticked with `--done` once done. A step the user stops goes the way they then say,
  as a point.
- A checklist a kind lacks, from `rn.py ccs`'s stop: `checklist-<kind>` made first, kind
  `checklist`.

### A sign-off

- `rn.py proposal <plan|design|deliverable>`; reply with what it printed, as printed; end. A stop
  saying the core decisions do not fit is a sign the work is not yet simple: its points settled
  again more simply with the user and the work made again.

### After feedback

- The steering's Open holds the feedback, kept by `/rn:gm`. The point behind it, one rn decided
  wrong or did not ask, is confirmed as in Hearing; each work it touches made again; the same
  sign-off again, whose proposal shows what changed.

### The end

- After the deliverable is approved: `rn.py learnings` gives every learning; each is put to the user
  one per message in the README's "Learnings to decide" form, with where it is recommended to go:
  the user's `.rn/checklists/<kind>.md`, an issue to `lovaizu/ccpm`, both, or neither. A learning
  taken for a checklist is a decision of `checklist-<kind>`, made through turn; an issue holds the
  need and its points alone, never the user's source, is shown to the user whole and opened with
  `gh issue create` only on their yes. Each answer is kept before the next.
- Then the stage moved to finished, and `gh pr ready`; tell the user the pull request is ready to
  merge, and that the merge is theirs.

## `/rn:ty`

- No session, or no sign-off waiting: say where the session stands, from its steering, and that
  `/rn:up` goes on; end.
- `rn.py answer approved`, Next the step the approved sign-off leads to.
- The learnings of the stretch just answered: `rn.py records`, then `learnings` made with what it
  printed as `--has`, kind `learnings`, receiver the user deciding each learning at the end; kept
  with `--put`.
- Then go on: read `${CLAUDE_PLUGIN_ROOT}/skills/up/SKILL.md` whole and take its steps from the
  steering's Next, as the README has the work go on after `/rn:ty` with nothing more typed.

## `/rn:gm <feedback>`

- No session, or no sign-off waiting: as `/rn:ty`. No words: ask for the change after `/rn:gm`; end.
- `rn.py answer feedback`, the feedback whole in the message and in `--open`, Next finding the
  point behind it.
- The learnings of the stretch, as `/rn:ty` makes them.
- Say `Your feedback is kept. Clear the conversation if you like, then type /rn:up to go on.`, in
  the conversation language; end.
