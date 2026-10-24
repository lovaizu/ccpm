# What rn's design says

The design is at `dev/rn/design.md`; the UX it brings about is `dev/rn/ux.md`, and turn, which rn
has make and read every work, is described in `turn/README.md` and `dev/turn/design.md`.

## User stories

- As the user, I want to ask for a piece of work in rough words with `/rn:up <what they want>`.
- As the user, I want to answer each point rn confirms with me, in one word or my own words.
- As the user, I want to approve a proposal with `/rn:ty` or ask for a change with
  `/rn:gm <feedback>`.
- As the user, I want to go on from where I stopped with `/rn:up` in a fresh conversation.
- As the user, I want to merge the pull request rn marked ready.

## Logical components and why

- The conductor: the AI the user talks with. It alone decides each next move: what to confirm with
  the user, what work to have made, whether a work returned serves the purpose, and when to stop at
  a sign-off. It alone commits and pushes.
  - Why: a decision taken without the goal and the conversation leaves a record the user cannot
    stand behind; one decider keeps the course one.
- The maker: turn. Every work the user sees or that goes into their product, the plan, each
  document, each task's result, a checklist for a kind rn has none for, is made by turn from what
  the conductor decided, and read and used by an AI that did not make it in its receiver's place.
  The conductor reads each Good at its lines, puts turn's questions to the user as points, and
  fixes by hand only what falls short of the purpose in a few lines; when the decisions must change
  much, it calls turn again.
  - Why: the work's maker finds the Good it meant, a first reader the Good the lines give (turn's
    README); turn's own design leaves the judging of its result to the caller.
- The record: the session's folder `.rn/<session>/` on the session's branch, holding the plan
  (`steering.md`, in the form of rn's plan checklist), the decisions for each work
  (`decisions/<work>.decisions.md`, what the work must say or do, written by the conductor from the
  user's answers), each call to turn (`tasks/<work>.json`, the CCS), and where the session stands.
  Every decision is committed and pushed before the work that follows it; the commit message holds
  the options weighed with their reasons, and each feedback with its answer.
  - Why: the next conversation goes on only from what was pushed; the documents keep what holds
    now, the commits how it was reached.
- The checklists: rn's own, one per kind (in the plugin, read-only), and the user's addition for a
  kind at `.rn/checklists/<kind>.md` in their repository, holding only what it adds. Both are handed
  to turn for a work of that kind. For a kind rn has none for, a checklist is made there through
  turn with rn's `checklist.md`.
- The guards: hooks that hold the conductor to what a machine can judge, at the moment it could
  break: no commit or push on the default branch; a sign-off passed only by the user's `/rn:ty`;
  the plan in its form; a decision pushed before the work that follows it. Each stop names the step
  and why.
  - Why: a rule in words is followed by chance; a stop at the moment holds every time (turn's own
    design does the same).
- The pull request: a draft pull request of the session's branch, opened with the plan, marked
  ready by the conductor after the deliverable sign-off and the lessons; the merge is the user's.

## Interactions

- Asking: the conductor finds the points to decide from the user's words, the repository and the
  documentation, and confirms each with the user, the looked-up ones included, one per message, in
  the UX's message form. Answers go into the decisions of the work they settle, committed with the
  options weighed.
- A sign-off: the conductor stops with the proposal: where the session stands (the sign-offs, done
  and ahead), what changed since the last proposal, the work's link on the pull request, and each
  item of the work's checklists with its Good and lines from turn's result. The proposal is built
  by a script from turn's result and the record, so it says nothing an AI did not have read.
- Feedback: `/rn:gm <feedback>` writes the feedback into the record, commits and pushes it, and
  stops. `/rn:up` then finds the point behind the words, rn decided wrong or did not ask, confirms
  it, writes the answer into the decisions, has the work made again, and stops at the same sign-off
  with what changed.
- Approving: `/rn:ty` records the approval, commits and pushes, and the conductor goes on to the
  next step.
- Resuming: `/rn:up` in a fresh conversation reads the session's record on the branch and goes on
  from where it stands; any stop is a place to go on from, since every decision was pushed before
  the work after it. There is no pause command: the UX's user stops wherever they stop.
- The documents: after the plan sign-off, the conductor confirms with the user which documents the
  purpose needs (such as a UX, a README, a design), and has each made in the order its checklist
  says it is drawn (UX, then README, then design), then stops at the design sign-off.
- Tasks: after the design sign-off, the conductor writes the tasks into the plan, each naming the
  acceptance criteria it serves, and has each task's work made through turn with the checklist of
  its kind and the criteria it serves as what the work is used for; a point only the user can
  decide is confirmed with them.
- The deliverable: when the tasks are done, the finished work is used through turn as the user
  would use it, with the plan's acceptance criteria as what it is used for, and the conductor stops
  at the deliverable sign-off.
- Lessons: turn returns lessons with every run; the conductor keeps them in the record. On `/rn:ty`
  at the deliverable sign-off, it confirms each with the user as a point, with what happened, the
  addition to `.rn/checklists/<kind>.md` it recommends, and whether a fault of rn's own goes to rn
  as an issue on `lovaizu/ccpm`; the additions taken are committed to the same pull request. Then
  it marks the pull request ready.

## Physical view

- rn's skills, one per command: `up`, `ty`, `gm`; each the conductor's steps for that command, run
  in the user's conversation.
- rn's scripts, Python 3.9 or later with the standard library only, and jq: find the checklists for
  a kind (rn's and the user's addition), write a work's CCS, build the proposal from turn's result
  and the record, read and write where the session stands.
- rn's hooks: one entry per hook event, each check in its own file, Python 3.
- rn's checklists: one markdown file per kind, in the plugin.
- Placed: the plugin on the user's machine, installed with turn as its dependency; the record and
  the user's checklists in the user's repository; the pull request on GitHub.
- Depends on: Claude Code; turn; git and the GitHub CLI `gh` logged in with push access;
  `python3` 3.9 or later and jq.

## Verification

- Units: rn's scripts and hooks by unittest in `dev/rn/tests/`, every line and branch run, every
  mutant caught, property tests where an input varies; each skill's flow by a trial with stand-ins
  for turn and the user on the smallest task; the content on real work in the trials of the whole.
- Acceptance, in `lovaizu/playground`, each run on a branch of its own and removed after: the flow
  from `/rn:up` to the pull request marked ready with stand-ins; each story by a stand-in user
  playing it; KR1.1, the changes a stand-in user holding the purpose sends back at the deliverable
  sign-off, and KR1.2, the user's time read from the records in its parts (answering, checking,
  sending back, by hand), each compared with the version in use, rn 0.9.0, on the same request.
- Every AI part is checked on the model it names (Opus) and judged from the JSONL of every
  conversation and agent it started.
