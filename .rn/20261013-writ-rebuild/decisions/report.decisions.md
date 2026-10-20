# Decided by the assistant, to report to the user

The user (2026-10-19): make rn whole through turn, and report what was decided at the end.

- R1 (rn UX run 3): "what rn fixed on its own" is slips it corrected that leave nothing to
  decide; no point is settled unasked (the run read it as matters settled without asking).
- R2 (turn's question): what the AI reading a proposal finds lacking, rn makes again before it
  stops; only a point the user alone can decide comes to them. Not chosen: show the findings with
  the proposal (the user would check the reading), bring each as a point (most are not theirs).
- R3 (turn's question): the six benefits stay with their reasons as agreed, against turn's
  recommendation to keep three, since a benefit says why the user chooses rn, which G1 and the
  scenes do not.
- R4: rn's README and design decisions rewritten from the UX, keeping only what the UX does not
  settle; the old ones described rn before the UX (asking only what cannot be looked up, feedback
  files, three fixed documents).
- R5: no pause command (`/rn:dn` goes): the UX's user stops wherever they stop, and every decision
  is pushed before the work after it, so any stop is a place to go on from.
- R6: the proposal is built by a script from turn's result and the record, so it says nothing an
  AI did not have read; no separate AI-written report.
- R7: no verification document of its own: the design's Verification holds the checks, and the
  deliverable is used with the plan's acceptance criteria as what it is used for.
- R8: the documents the purpose needs are confirmed with the user after the plan sign-off and
  made in the order their checklists draw them (UX, README, design).
- R9 (turn's question on the README): no page for fuller use; the README says the example's three
  commands are all there is to use, since the UX names no other.
- R10 (turn's question on the design): a fresh `/rn:up` goes on with the session whose folder
  `.rn/<yyyymmdd>-<slug>/` the checked-out branch changed and whose plan is not finished, as rn
  0.9.0 found it, over turn's recommendation of a folder named after the branch, so sessions 0.9.0
  left are still found.
- R11: the CCS of each work is kept at `ccs/<work>.json`, not `tasks/`, since "task" names the
  parts the work is divided into.
- turn fixed twice on the way (ac4645a, adf992b): Claude Code now ends some agents with
  SubagentHandback, where SubagentStop gives no reply and its block is ignored.
- R12: plugin.md step 3, a first reading of the README and the design by a reader who does not
  know the discussion, is taken as met by turn's first user, which read each in that place.
- R13 (turn's question on the scripts): the plan's CCS holds no language, since the plan is made
  before it can say them and the plan's own decisions carry them; every later CCS reads them
  from the plan.
- R14: the scripts' turn run was cut at Claude Code's two-hour wait for background work, in its
  first round, while the generator was checking its second remake (from the JSONL: generator
  56 min, first user's two readings, two remakes; the second fixed what the first user sent back,
  the type check of `st` and the line run only as a command, with tests, type check and coverage
  passing, and was running Cosmic Ray when cut). No reader read that remake, so its Goods were
  checked by `dev/check.sh` and `dev/mutate.sh` instead; nothing was changed by hand. Later runs
  wait without a limit.
- R15: rn's plan checklist made again to the README: the goal G1 and the criteria AC1...,
  without the split into attractive and must-be quality the README does not show; the documents
  and the tasks written after their sign-offs; no sign-off as a task, since `state.json` keeps
  where the session stands; `status: finished` once the pull request is marked ready, so the
  lessons are still in the session.
- R16: no checklist for proposals, since a script puts the proposal together (R6) and no AI makes
  it.
- R17: the two languages are not a point to decide: the conversation's is the one the user writes
  in, the artifact's the one the repository is written in, English where it has none; they show
  on the plan, where the user can send them back. The README's example asks no language.
- R18: the draft pull request opens when the session starts, not once the plan is made, so the
  plan is made with its URL in its front matter, as its checklist's form asks; the design's
  "opens with the plan" read as the pull request the plan goes on.
- R19 (turn's question on the skills): the skills' steps are held by the design's four guards
  alone, not a hook for every step prompt.md B-25 and B-26 ask, since more hooks change the
  approved design and no trial has yet shown a step the four leave out being skipped.
- R20 (turn's question on the plan checklist): a task's ID is kept like a criterion's, never given
  to another, so commit messages and earlier messages always point to one task. Also taken from
  turn's work beyond the decisions: the plan's title naming the piece of work, and B-5 asking
  that a task does something for each criterion it names, not only names it.
- R21 (turn's question on the hooks): mutation testing reaches rn's hooks as well as its scripts,
  so every mutant of the guards is caught too.
- R22 (turn's question on the hooks): the hooks are held to the items of prompt.md a hook gives;
  the items on a prompt's own text are the skills'.
- R23 (turn's question on the skills, against its recommendation): `/rn:up`'s start and feedback
  steps stay in its SKILL.md rather than files read when needed (prompt.md B-13), since the skill
  is read whole once per command at under 300 lines, and a step in a file of its own is lost when
  its read is skipped.
- R24 (turn's question on the skills): `/rn:ty` while feedback is held approves nothing and says
  that `/rn:up` brings the new proposal, since the plan may already differ from the one shown.
- R25 (turn's question on the skills): a session rn 0.9.0 left, which has no `state.json`, is
  reported and not gone on with in the first unit; how to go on with it is for the whole check.
- B-27 of the skills (a long file read whole) fixed by hand in `/rn:up`'s Role.
- turn fixed a third time (turn's question on the trial): a folder a CCS names with a trailing
  slash is kept without it, as every read inside such a folder was stopped.
- R26 (the hooks' first user found these moves let through): each guard judges git and a write
  in the folder they act on, through `-C`, `cd`, `env`, `command`, `sh -c` and a worktree, since a
  conductor stopped by a guard may try the same move another way.
- R27 (turn's question on the hooks): prompt.md's items on a prompt's own text and on what the
  user sees are judged on the skills' runs, not the hooks', as R22 set.
- R28 (turn's question on `/rn:up`'s step 4): the skill keeps saying what rn's four hooks stop,
  as the design decides them and T2 to T5 build them next.
- R29 (turn's question on `/rn:up`'s step 4, prompt.md B-19): turn's messages reach the user by
  the conductor's reply, as the prompts' decisions say, since each is put into the conversation
  language, which a script cannot do.
- B-8 of `/rn:up` (TaskStop deferred) fixed by hand: the step loads it first.
