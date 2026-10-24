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
- R30 (keeping turn's trials once): what the four trials copied is kept in
  `dev/turn/trials/shared.py`; `roles.py` now prints, of each record, the messages and Stop hook
  lines `kept.py` printed as well, as one reading serves both.
- R31 (turn's question on lane's UX): without Python 3.9 or later the flow stops the run at its
  first move and asks for Python, as the hooks do, since the user chose that a check that cannot
  run stops rather than lets through (2026-10-21).
- R32 (turn's question on lane's UX): `lane:up` also writes the orchestrator's steps that tell the
  flow each move, and shows them in its proposal, as the user chose that the builder answers and
  approves and writes no flow (2026-10-21).
- lane's UX fixed by hand where turn's draft went against the decisions: a lane on a subagent's
  step alone, not a skill's; a type's steps not all subagents; the action `run`, not "a commit";
  the hooks laid where a step alone is not sure to hold; the builder's call said by what it does.
- R33 (lane's as_printed): a hand-on is an Agent call's prompt, a SendMessage's message or the
  subagent's last reply; `<input>` names the command whose output is handed on, and the hand-on
  holds its last output word for word, a heading line beside it allowed, as lane:up heads its print
  (the user agreed, 2026-10-22).
- R34 (lane's follow_next): the script prints the next move as the tool call itself, one JSON line
  `{"tool": ..., "input": {...}}`, and the subagent's next call is that tool with that input; the
  form is lane's, general to any plugin, and turn prints in it when remade on lane, since a move
  read in turn's own form would make lane turn's alone (plugin.md step 2: what is general is taken
  in).
- R35 (lane's wait_for): the lane takes the approval, such as `OK`, and the command it holds back,
  such as `lay.py write`; that command is let through only once a message holding the approval
  has reached the subagent since it last asked, read from its record, whose shape for a message
  is checked on a real run first; the sentence shows the approval alone.
- R36 (lane without Python at a subagent's end): the SubagentStop hook exits 1, the user told and
  the subagent let end, since a subagent cannot install Python and keeping it going only repeats
  the ask; the README's promise is on the tool calls the hooks watch, which still stop (R31).
- R37 (turn's design on lane, T21): the call is copied into `turn.py start` by the orchestrator and
  start_with checks only which script runs, as `turn.py start` already stops a call naming a
  missing file; a lane holding the arguments waits until a run shows the copy changed.
- R38 (turn's progress called from an agent): the lines go to `main` by SendMessage, as the agent
  that called turn cannot be messaged by a name, and the main conversation alone talks with the
  user (dev/architecture.md).
- R39 (turn's generator running its work): held by its step alone, as test_after needs a command
  the CCS's kinds do not name; a kind for it waits until a run shows the step left out.
- R40 (turn's agent IDs): the orchestrator copies each ID the Agent call returns into `turn.py
  next`; a wrong one fails the SendMessage where it shows.
- R41 (turn's requirements): jq left out of the README and the design, as no script or hook of
  turn runs it.
- R42 (turn's later questions, T22): a question the generator or the decision finds goes into the
  result for a call again to take in, and only those found at the check are sent mid-run, as one
  way back for every question is simpler and a trial has not shown the mid-run send needed.
- R43 (turn's lanes, T22): no every_item and no end_when on the result, as the flow checks every
  item answered and writes the result inside its own run, where lane does not see the write.
- R44 (the githooks): `core.hooksPath` set to `dev/githooks`, relative, as the absolute path named
  the main checkout, which has no `dev/githooks` on main yet, so no pre-push check ran.
- R45 (lane's layer and long lines): a lane's sentence stays added at the end of its step's last
  line, unwrapped, as a wrapped sentence could not be taken out again when lanes are laid anew,
  and an AI reads a long line as well as a short one.
- R46 (T29's design): `/rn:ty` goes on by reading `/rn:up`'s steps whole, so the course is in one
  place and the work goes on after an approval with nothing more typed, as the README shows.
- R47 (T29's design): the deliverable is read before its sign-off with rn's checklist
  `session/deliverable.md`, one item asking each acceptance criterion done when used, its work every
  file the branch changed outside `.rn/`; a task's two runs of turn are one work `t<n>` with one
  decisions file.
- R48 (T29's design): a proposal shows at most five decisions of a work, each at most 200
  characters, and stops otherwise, as the UX takes a core that does not fit as a sign the work is
  not yet simple.
- R49 (T29's scripts): a proposal shown again after an answer is a new commit even where nothing
  changed, showing "(… as before)", so `/rn:ty` finds a sign-off waiting; `answer` refuses a state
  as kept last; a file the branch removed is not part of the finished work.
- R50 (T29's skills): the session counts as finished by its plan as the last commit holds it, so
  the move that sets `status: finished` is kept; `rn.py lessons` also gives turn's lessons from
  every version of each result on the branch, as a remake overwrites the result; a learning taken
  into the user's checklist is made through turn as a checklist work, as every checklist made is.
- R51 (T29's skills, remade on the new record): a stop whose action is the user's, such as their
  changes not committed, is told to them and the skill ends; the slug is chosen by the orchestrator
  from the request; a move is kept before a work is made again for a Good its lines fall short of,
  as `rn.py ccs` refuses changes not kept; `--has .` where the decisions give no other; each
  learning's answer kept with `rn.py state` before the next, each checklist made once all are
  answered; the proposal shown put into the conversation language, as agreed for the languages;
  `gh pr ready` before the stage moves to finished, so a failed `gh` leaves the session to go on.
- R52 (the checks): rn's property test of Next took text that reads as a heading, which the
  steering rightly refuses; such text is left out of its inputs and `#` added to the example test;
  `rn.py proposal` sets Next to waiting at the sign-off, so the steering is never stale there.
- R53 (lane's Principle 3): lane's code read against it: turn's step words in shell.py went with
  `named()`, which nothing called since turn's own hooks were removed; `printed()` and `git()`,
  called by tests alone, removed too (code.md B-4); hands_off now reads assignments and `env`
  before a command and git's long options taking a word, so `env git commit`, `GIT_EDITOR=true git
  commit` and `git --git-dir .git commit` are stopped; a command hidden in another, as `bash -c`,
  `sudo` or `/usr/bin/git`, is left through, as lane holds the forms an AI writes
  (dev/lane/architecture.md:88-92).
- R54 (the language check): no hook checks the reply's language, as the user decided (2026-10-24):
  a reply slipping into another language costs the user little toward the purpose, while a check
  would widen lane to the main conversation and run on every reply; rn still proposes the two
  languages first and keeps them in the steering, and its skills say to talk in the conversation
  language.
