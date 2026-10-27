---
rn: 0.9.0
pr: https://github.com/lovaizu/ccpm/pull/61
status: running
artifact-language: English
conversation-language: Japanese
issue: https://github.com/lovaizu/ccpm/issues/54
---

# rn that achieves a purpose from a request alone

G1: Whoever wants to hand a whole piece of work to an agent asks for it without preparing anything,
only answers what they are asked, and their purpose is achieved; rn 0.10.0 brings this to them.

## Acceptance criteria

- AC1: On real requests, the user sends back few changes at the deliverable sign-off, none once G1
  is reached.
  Check: each request run on `lovaizu/playground` with this rn, the user stood in for by an AI
  holding what the user truly wants and accepts, written beforehand and not shown to rn; the
  changes counted from every JSONL and shown to the user with how close they came and what could be
  improved; the user judges.
- AC2: On the same requests, the user spends little time from asking to their purpose achieved,
  with AC1 no worse.
  Check: from the same runs, what the stand-in does: the questions it answers, the proposals it
  reads, what it sends back and fixes by hand, as an AI's minutes are not a person's; shown to the
  user as AC1's are, and the user judges.

## Documents

- UX: `dev/rn/ux.md`
- README: `rn/README.md`
- Architecture: `dev/rn/architecture.md`

## How the work goes

- Every turn: act; gather the facts it brought, its result, the JSONL, the tests' and trials'
  output, held to the task's completion criterion and the acceptance criteria; replan from those
  facts alone, asking whether this plan still reaches G1 and whether G1 still serves the purpose,
  and bring it to what it should be, a change to G1 or the criteria confirmed with the user first;
  then replace `state.json` with the state for the next turn and push.
- Before each piece of work, look for the practice that already exists for it.
- A checklist or an environment a task lacks is a task of its own, before the task that needs it.
- Facts decided by the user: only the README and the design are agreed with the user, the rest
  built and checked by `.claude/rules/dev.md` and `dev/architecture.md` without asking; lane, turn
  and rn are built in that order, each work made by a subagent with the checklists open, then checked and fixed by
  hand, with no turn run and no first-user reading; writ is folded into rn and removed.
- The documents are written in English; questions to the user are asked one at a time.
- Decisions taken by the assistant are kept in `decisions/report.decisions.md` and reported to the
  user at the end.

## Tasks

- [x] T1: turn 0.2.0 ready to build rn on. Done when the user, shown turn's three acceptance
  trials, takes turn as the maker of rn's works. Serves AC1.
- [x] T2: A conductor committing or pushing on the default branch, or pushing to it, by a plain
  `git commit` or `git push`, is stopped with the step and why, and nothing else it does is
  stopped. Serves AC1.
- [x] T4: A sign-off passes only by the user's `/rn:ty`. Serves AC1.
- [x] T5: A plan outside the form of rn's plan checklist is stopped before it is kept. Serves AC1,
  AC2.
- [x] T6: No work starts before the decision it follows is pushed, so wherever the user stops, the
  next conversation goes on from there. Serves AC2.
- [x] T7: A reader of rn's design can tell how the conductor replans every turn from the facts the
  turn brought and keeps one state, replaced each turn, and that a missing checklist or environment
  becomes a task; agreed with the user. Serves AC1, AC2.
- [ ] T9: A request in rough words reaches the plan sign-off with the user asked only the points
  that are theirs, one per message, and the user approves from the proposal alone a plan whose goal
  is what they want. Serves AC1, AC2.
- [ ] T10: The user approves at the design sign-off, from the proposal alone, the documents the
  purpose needs. Serves AC1, AC2.
- [ ] T11: Each task's result, made through turn, brings the plan's criteria closer, and the plan is
  replanned from each turn's facts. Serves AC1.
- [ ] T12: The user meets at the deliverable sign-off a finished work that does every acceptance
  criterion. Serves AC1.
- [ ] T13: Each lesson the user confirms goes where it makes later work better, and the pull request
  is ready to merge. Serves AC1, AC2.
- [ ] T34: rn's acceptance test runs rn whole as its user does, with the real turn, on
  `lovaizu/playground`, the user stood in for as AC1's Check says, and shows AC1 and AC2 from its
  records; the stand-in flow trial made into it, as dev/architecture.md's Test has the whole tried
  by acceptance tests and each move is tried alone in the move trials, as the user chose
  (2026-10-26). Serves AC1, AC2.
- [ ] T14: AC1 and AC2 shown to the user on a real request of about an hour with documents and
  code, so every stage is passed: a command-line tool that tidies a Downloads folder, with its
  README, design and tests (truly wanted: moves only, a dry run first, a folder for each kind, macOS
  and Linux), run once by T34's test; then the user tries this rn once. Serves AC1, AC2.
- [ ] T35: rn's stages are goal, ux, architecture, build, deliverable, learnings and finished, the
  ux and the architecture stage each signed off on its own and passed where it needs no document,
  and each document heard as kept, changed, kept in `.rn/` alone or not made, as issue #54's
  "Stages named by what each settles" says, the user choosing it (2026-10-27): UX and README first,
  shown to the user, then the architecture, the code and the trials. Serves AC1, AC2.
- [ ] T36: How heavily the work is checked is the architecture's decision on what a failure would
  cost, as issue #54's "Checks weighed by what a failure would cost" says, rn's code checklist
  changed so. Serves AC2.
- [x] T37: turn's roles write only what a role or the caller uses, as the user agreed (2026-10-27):
  the generator self-checks every item at the end of making and gives each by its lines alone,
  `<path>:<from>-<to>`, no words; the first user gives each item it found the Good of by its lines
  alone, and each it did not by one sentence of what the receiver would need to get for its Good,
  not how to make it; that sentence handed to the generator as the receiver's need, mended for the
  receiver, not to pass the first user (fix.md B-2); no gap, no `outside`, no argument back, as
  8d563a0 made the first user find fault where its intent is to find Good; reading.json,
  claim.json, forms.py, flow.py, the roles' prompts, turn's UX and architecture, and rn's
  orchestrator.md:200-207, which checks each `good` at its `lines`, changed together as one,
  held to fix.md whole. Serves AC2.
- [ ] T38: Every part of lane, turn and rn no purpose needs is gone, each judged by the user one
  at a time from `audit-purpose.md`, as the user asked (2026-10-27). Serves AC1, AC2.
- [ ] T39: turn is remade as `audit-purpose.md` 1 to 5 say, its README, UX, architecture,
  prompts, scripts, lanes and trials together; check.sh turn 100%, mutate.sh turn 0 survivors, its
  trials passing. Serves AC1, AC2.
- [ ] T15: Users who update get rn 0.10.0 and turn 0.2.0, on the user's instruction. Serves AC1,
  AC2.

lane's units, built before turn and rn are remade on it; the hooks of T2 to T6 come from lane.

- [x] T16: The builder asks Claude to lay lanes on a plugin outside ccpm, answers one point at a
  time and gives the OK, and its subagent, running a command its step says not to run, is stopped
  and told `<plugin>: <sentence>`, every other call let through; on a machine without Python 3.9 or
  later the hook asks for it. lane:up, the layer, the guard with hands_off alone, the copy with its
  `VERSION`, and the Python check; `common/` and `dev/common/` move into lane, rn and turn
  linking to lane's code, as a copy of them in lane would fail `dev/check.sh`. Serves AC1.
- [x] T17: Every lane on a tool call holds as the README's Lanes says, start_with, read_only,
  read_whole, write_only, in_form, test_after, as_printed, follow_next and wait_for, those on the
  order of steps from the subagent's record; lane:up is held by lanes of its own. Serves AC1.
- [x] T18: A subagent that ends before its output is made, or with an item of its input
  unanswered, is told end_when's or every_item's sentence and goes on. Serves AC1.
- [x] T19: Run where an older copy of lane's code is, lane:up brings the copy and the hooks up with
  the same lanes; a lane whose step no longer has its sentence stops the call and says to run
  lane:up again. Serves AC1.
- [x] T20: lane, tried as its user from start to end on `notes` and on turn, achieves every story
  and its KR1.1 is counted, and passes `claude plugin validate --strict`. Serves AC1.

turn remade on `dev/architecture.md` and lane, before rn is remade on it.

- [x] T21: A reader of turn's design can tell how its README and UX are kept on
  `dev/architecture.md`: an orchestrator agent holding the run by a flow script and a state file,
  roles answering it alone, questions sent to the calling AI and the run going on with the answer, a
  stopped run going on from its last step, and each role's steps held by lanes. Serves AC1.
- [x] T22: turn's agents, scripts and hooks are made to that design, the hooks laid by `lane:up`,
  and none of turn's own checks left; check.sh 100% and mutate.sh turn 0 survivors. Serves AC1.
- [x] T23: turn, tried as its user from start to end, achieves every story and its key results are
  counted, and passes `claude plugin validate --strict`. Serves AC1.

rn's checklists given one role each, alongside turn's trials and before rn is remade, as rn's
scripts find a kind's checklists and each lesson goes into one.

- [x] T24: Whoever makes or updates a checklist with rn, or places a lesson in one, finds from
  `rn/checklists/checklist.md` alone which checklist each item goes into, from the purpose and UX
  of whom it serves, each item in one place; then every checklist of rn read against it. Serves
  AC1.

The checks' tools kept as is now done in Python, after lane's code is brought to its architecture.

- [x] T25: Whoever builds ccpm sets up the checks' tools with `uv sync --locked` from the root
  `pyproject.toml`'s dependency groups and the committed `uv.lock`, CI and `dev/githooks/pre-push`
  using the same, and `dev/requirements*.in` and `.txt` gone; as the user chose (2026-10-23), since
  that is the form Python projects now take and pip-tools' home, Jazzband, is winding down. CI's
  actions on their current majors, which run on Node 24 (checkout, setup-python and setup-node v7,
  Node 20 gone from the runners on 2026-09-23), and the tools at their latest that run where they
  run now. Serves AC1.

rn remade on its architecture and lane, after turn: the conductor held by rn's scripts, `/rn:ty` and
GitHub's branch protection, each subagent by lanes; T3 dropped, as the default branch is held by
branch protection rather than a check of commands.

- [x] T26: rn has no hook of its own, the default branch held by GitHub's branch protection, which
  rn's README asks the user to turn on, and T2's check gone with it. Serves AC1.
- [x] T27: rn's scripts give what the architecture says: the state replaced whole at each move, each
  work's CCS naming its kind's one checklist, the user's addition and rn's checklist for a fix, and
  each proposal made from the record alone; check.sh 100% and mutate.sh rn 0 survivors. Serves AC1,
  AC2.
- [x] T28: rn's learner, at each sign-off the user answers, reads that stretch's record whole and
  searches the conductor's conversations of it for what only they show, turn's runs left to turn's
  learner, its lessons kept and put to the user at the end, as the user chose (2026-10-24), and gives each lesson with the words it rests on, held by lanes laid with
  `lane:up`. Serves AC1.
- [x] T29: rn's skills take each move with rn's scripts as they now are, and the proposal at each
  sign-off, the design's and the deliverable's included, shows the link to each work and its core
  decisions with their intent in a few short lines, read from where the hearing keeps them, the
  scripts and the skills designed together. Serves AC1, AC2.

turn made to make and have read alone, and rn to make what it can itself, as the user chose
(2026-10-26), before T30 and T31 are finished on them: the plan is read by the user at once, a
lesson made at each sign-off weighed down every session and named causes its records did not
show.

- [x] T32: turn has no learner: its README, UX and architecture, the learner role and the call's
  `lessons` removed, so turn makes a work and has its first user read it, and finding what fell
  short is the caller's. Serves AC2.
- [x] T33: rn's orchestrator makes the plan from the hearing with rn's plan checklist open and
  checks it against the same checklist, with no call to turn, rn's scripts holding its form; the
  documents of the design are made through turn; no learnings are made at a sign-off: once the
  user approves the finished work, the orchestrator looks once for the learnings in the branch's
  history, each send-back, remake and point asked again, and checks each it doubts in the
  conversations' JSONL before putting it to the user. Serves AC1, AC2.

rn's steering made the map kept current, and the plugins brought to what they should be, before the
acceptance, as the user chose (2026-10-25).

- [ ] T30: rn's steering holds only what is left and where it stands, its tasks laid backward from
  the criteria with one turn call per output, research and trials made as works of their own, and
  the design sign-off held only where a document is needed; the move trials passing on it. Serves
  AC1, AC2.
- [ ] T31: lane, turn and rn read whole hold their checklists: no module or prompt taking on two
  things, nothing said twice or against another part, nothing no reader needs; rn.py split by what
  each part takes on; each folder, file and name in the code saying what it is, the trials of
  lane, turn and rn named by the kind dev/architecture.md's Test gives them, unit tests of prompts
  or acceptance tests, as the user chose (2026-10-26), since turn's `trials/flow/` tries its
  orchestrator alone where rn's tried rn whole; every document and prompt rewritten in plain
  sentences, one point each, as dev/architecture.md was (2026-10-27); check.sh 100%, mutate.sh 0
  survivors, the move trials passing. Serves AC1, AC2.
