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
  Check: each request run on `lovaizu/playground` with both versions, the changes counted from
  every JSONL.
- AC2: On the same requests, the user spends less time from asking to their purpose achieved than
  with rn 0.8.0, with AC1 no worse.
  Check: from the same runs, the minutes the user spends answering, checking proposals, sending
  back and fixing by hand.

## Documents

- UX: `dev/rn/ux.md`
- README: `rn/README.md`
- Design: `dev/rn/design.md`

## How the work goes

- Every turn: act; gather the facts it brought, its result, the JSONL, the tests' and trials'
  output, held to the task's completion criterion and the acceptance criteria; replan from those
  facts alone, asking whether this plan still reaches G1 and whether G1 still serves the purpose,
  and bring it to what it should be, a change to G1 or the criteria confirmed with the user first;
  then replace `state.json` with the state for the next turn and push.
- Before each piece of work, look for the practice that already exists for it.
- A checklist or an environment a task lacks is a task of its own, before the task that needs it.
- Facts decided by the user: only the README and the design are agreed with the user, the rest
  built and checked by `.claude/rules/plugin.md` without asking; rn's prompts, hooks and scripts
  are made through turn; writ is folded into rn and removed.
- The documents are written in English; questions to the user are asked one at a time.
- Decisions taken by the assistant are kept in `decisions/report.decisions.md` and reported to the
  user at the end.

## Tasks

- [ ] T1: turn 0.2.0 ready to build rn on. Done when the user, shown turn's three acceptance
  trials, takes turn as the maker of rn's works. Serves AC1.
- [ ] T2: A conductor committing or pushing on the default branch, or pushing to it, by a plain
  `git commit` or `git push`, is stopped with the step and why, and nothing else it does is
  stopped. Serves AC1.
- [ ] T3: The same stop holds where git reaches the default branch through `-C`, a `cd`, `env`,
  `command`, `sh -c` or a worktree. Serves AC1.
- [ ] T4: A sign-off passes only by the user's `/rn:ty`. Serves AC1.
- [ ] T5: A plan outside the form of rn's plan checklist is stopped before it is kept. Serves AC1,
  AC2.
- [ ] T6: No work starts before the decision it follows is pushed, so wherever the user stops, the
  next conversation goes on from there. Serves AC2.
- [ ] T7: A reader of rn's design can tell how the conductor replans every turn from the facts the
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
- [ ] T14: AC1 and AC2 hold on the same real requests against rn 0.8.0. Serves AC1, AC2.
- [ ] T15: Users who update get rn 0.10.0 and turn 0.2.0, on the user's instruction. Serves AC1,
  AC2.
