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

- AC1: On the same real requests, the user sends back fewer changes at the deliverable sign-off
  than with rn 0.8.0.
  Check: each request run on `lovaizu/playground` with both versions, the user stood in for by an
  AI holding what the user truly wants and accepts, written beforehand and not shown to rn; the
  changes counted from every JSONL.
- AC2: On the same requests, the user spends less time from asking to their purpose achieved than
  with rn 0.8.0, with AC1 no worse.
  Check: from the same runs, what the stand-in does: the questions it answers, the proposals it
  reads, what it sends back and fixes by hand, as an AI's minutes are not a person's.

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
  built and checked by `.claude/rules/plugin.md` without asking; lane, turn and rn are built in
  that order, each work made by a subagent with the checklists open, then checked and fixed by
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
- [ ] T3: The same stop holds where git reaches the default branch through `-C`, a `cd`, `env`,
  `command`, `sh -c` or a worktree. Serves AC1.
- [ ] T4: A sign-off passes only by the user's `/rn:ty`. Serves AC1.
- [ ] T5: A plan outside the form of rn's plan checklist is stopped before it is kept. Serves AC1,
  AC2.
- [ ] T6: No work starts before the decision it follows is pushed, so wherever the user stops, the
  next conversation goes on from there. Serves AC2.
- [x] T7: A reader of rn's design can tell how the conductor replans every turn from the facts the
  turn brought and keeps one state, replaced each turn, and that a missing checklist or environment
  becomes a task; agreed with the user. Serves AC1, AC2.
- [ ] T8: The same request runs on `lovaizu/playground` with rn 0.8.0 and with this rn, and both
  runs' JSONL can be read. Serves AC1, AC2.
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
- [ ] T14: AC1 and AC2 hold on the same real requests against rn 0.8.0: a script that tidies a
  Downloads folder (truly wanted: moves only, a dry run first, a folder for each kind, macOS and
  Linux) and making issues easy to open (truly wanted: a bug and a request form, required fields,
  no blank issue), each run once on each version, more where the two do not differ plainly; then
  the user tries this rn once. Serves AC1, AC2.
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
- [ ] T22: turn's agents, scripts and hooks are made to that design, the hooks laid by `lane:up`,
  and none of turn's own checks left; check.sh 100% and mutate.sh turn 0 survivors. Serves AC1.
- [ ] T23: turn, tried as its user from start to end, achieves every story and its key results are
  counted, and passes `claude plugin validate --strict`. Serves AC1.

rn's checklists given one role each, alongside turn's trials and before rn is remade, as rn's
scripts find a kind's checklists and each lesson goes into one.

- [x] T24: Whoever makes or updates a checklist with rn, or places a lesson in one, finds from
  `rn/checklists/checklist.md` alone which checklist each item goes into, from the purpose and UX
  of whom it serves, each item in one place; then every checklist of rn read against it. Serves
  AC1.
