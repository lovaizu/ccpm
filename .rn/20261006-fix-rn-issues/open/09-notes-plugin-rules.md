# Plugin rules, rewritten from zero

Agreed with the user one point at a time; the rules are written from these points, not patched.

## Purpose of the rules

A plugin that achieves its purpose comes out simple, never heavy, and is made and checked with little
effort.

- How a plugin is made and how it is checked are decided together, since a way of making cannot be
  judged better without a check that shows it.
- The way of making is not assumed (one shared flow with domain parts is only one candidate, beside a
  short self-contained prompt per plugin and the official plugins' shape). It is chosen after the
  form of the check is decided, by comparing the candidates with that check.

## What the check shows

- What the user got: whether the user actually gets each gain the plugin's README promises.
- What the user spent for it: how long they waited, how much they read to decide, and how many times
  they were called. Every part can work while the whole keeps the user waiting for hours, as rn 0.9.0
  did; looking only at what was got misses it.

## How the check is run

- Day to day, a change is judged by scenes: each starts from the state just before the moment the user
  gets a gain and ends at the first result that shows it, so it runs in minutes.
- At each milestone, the README's whole story is run once, the only run that shows what the user
  spent; rn 0.9.0, checked by scenes alone, kept the user waiting 2 h 43 min unseen.
- The story, its starting state and the version compared against (the one in use) are fixed first
  and not changed on the way: the rebuild's comparison never finished because its subject changed
  four times.

## Who plays the user

- An AI stand-in plays the user, handed only what the README tells a user and what they want.
- Scenes run with `claude -p`; the whole story at a milestone runs in a real interactive session, since
  `-p` behaves otherwise (in an interactive session an agent started with the Agent tool runs in the
  background, #44), and what only shows there would be missed.
- Fact, tried on Claude Code 2.1.293 (worker session, script `drive.py` in its scratchpad): a Python
  stdlib pty script drives a real interactive `claude` with `--plugin-dir`. Hooks given with
  `--settings` append each event to a file; a turn has truly ended only when `Stop` comes with
  `background_tasks` empty (seen: shell and subagent running, then shell, then none). `/clear` gives a
  new session and `/rn:up` resumes; every hook input carries `transcript_path`, so the JSONL is found.
  The child must drop every `CLAUDE_CODE_*` variable, or it keeps no JSONL; the trust and
  skip-permissions dialogs must be answered; an AskUserQuestion dialog fires `Notification`
  (`permission_prompt`), not `Stop`. About 3 s overhead per turn.

## How a run turns into fixes

- The cause is found from the records, not the outcome: the JSONL of every conversation and subagent
  the run started is traced, what each role was handed, did and returned, before a fix is chosen. In
  the rebuild, 41 of 44 commits were made before any trial's JSONL was read.
- A run's findings are gathered whole and grouped by cause before anything is fixed, and only the
  cause's place is fixed; a sentence is not added per symptom. An AI's behavior varies from run to
  run, so one sighting does not show a cause (e923168 added two sentences from one stopped run).
- A fix holds when the scene where it tripped runs again without it; at a milestone, the plugin is
  compared, without saying which is which, with the version in use.

## Staying simple

- A plugin starts minimal: its purpose and its domain parts. Anthropic's own guidance is the same:
  "start by testing a minimal prompt ... then add clear instructions ... based on failure modes"
  (Effective context engineering for AI agents), and "Write minimal instructions: Create just enough
  content to address the gaps" (Skill authoring best practices).
- Something is added only for a failure reproduced in a scene.
- At each milestone report and each request to merge, each plugin's size (what a call reads, in words)
  is shown beside the version in use, and any growth comes with the failure it prevents. No CI and no
  budget file: the user, who merges, judges it there.
- Size is the measure of simple, not of good: rn 0.9.0 was smaller than 0.8.0 and did harm. Whether
  the plugin achieves its purpose is the check's to show.

## The plugin type

A plugin that has AI make something is built from one unit and two layers on it, as a web app is
handlers joined by a session, and a batch job steps joined by a record it restarts from. Whether a
layer is shared code across plugins is a separate question.

| Layer | What it does | Today |
|---|---|---|
| Return | takes what it is given and an aim, makes one thing, returns it; never talks with the user | `pith:make`, `pith:up`, `rn:make` |
| Join by talk | agrees with the user one point at a time, calls Returns, judges what comes back, decides the next move | writ's and rn's conductors |
| Resume from a record | keeps what was joined and decided, so a cleared conversation goes on | rn's `steering.md` and `/rn:up` |

pith is Return only; writ is Return and Join; rn is all three. What a plugin writes for itself is
each Return's domain part (its viewpoints and what its generator needs); Join and Resume take the same
shape in every plugin, yet today each plugin writes them again.

## The state the layers carry: CCS

The layers carry their state as a CCS (Compressed Cognitive State), not reinvented: the nine-field
YAML of Bousetouane, "AI Agents Need Memory Control Over More Context" (arXiv 2601.11653), with the
type vocabulary and operating rules aiya worked out (`worktree-aiya`, `aiya/agents/turn-brief.md`).

- Read in the paper: each turn the agent acts on the last committed CCS and the current input only,
  never the transcript; after the turn a separate compressor writes the next CCS from the finished
  turn, the previous CCS and the artifacts it let through, and it replaces the previous one; artifacts
  are referred to, never pasted. The one who acts does not write the state.
- What a receiver needs fits the existing fields as types, with no new field: the receiver in
  `focal_entities`, what they decide in `goal_orientation`, what is undecided in `uncertainty_signal`,
  sources in `retrieved_artifacts`.
- Not yet shown: the paper's results are qualitative only; aiya's try kept a CCS at 807-953 characters
  over five steps, but under a script, not under prompts alone.

## How rework is cut

The rework seen was a generator writing a whole document, then returning what was undecided, and
writing it again (8 rounds, 45 min). With a CCS:

- A Return checks before making whether it can make without guessing; what is missing goes back
  unmade, into `uncertainty_signal`, and Join resolves it (asks the user, or settles it from the
  record) before calling the Return again.
- What is decided stays in `constraints` and `goal_orientation`, so every later Return gets it and
  nothing is asked twice or contradicted between documents.
- A redo is handed only the gap found, with the attempt count, not the whole work again.
- Gaps that show only by making remain; the aim is fewer rounds, not none.

## Each Return has an IN and an OUT

| | What holds | Checked |
|---|---|---|
| IN | the latest CCS has the Return's required fields and types, and no open gap that bears on it | by a hook, just before the Return is called |
| OUT | what it made is where it was asked; its report says what it did, tried and left unsure; what it could not make is written as a gap | by a hook, just after it returns |
| Next CCS | the compressor writes it from the previous CCS and the OUT, in the CCS form | by a hook, just after it is written |

- A plugin writes, for each of its Returns, only the IN's required fields and what the OUT makes;
  the form and its checks are shared.
- A hook checks that a field is there, not that it is right; whether the work serves its purpose is
  the check by use's.
- Each hook acts only on its own plugin's CCS files and Return calls, since rn 0.9.0's hooks stopped
  other sessions and right moves (#43, #44).

## Who writes the CCS: facts by script, judgment by the one who holds it

What a role did is known only to that role once it returns, and most of it is already in the records:
written again by an LLM it would be a second copy that drifts. So:

| Part | Taken from | Written by |
|---|---|---|
| what happened (`episodic_trace`) | the role's JSONL (tool calls, results, final reply) and commits | script |
| files read and commands run | the JSONL | script |
| files changed | git (diff and commits), which also catches files written by a command | script |
| sources (`retrieved_artifacts`) | the JSONL (files read, URLs fetched) | script |
| goal and constraints | the approved documents, by path | script (reference only) |
| what was decided with the user | the user's words, kept as said | the conductor |
| what is unsure (`uncertainty_signal`) | only the role itself knows | the role that met it |
| the next move (`predictive_cue`) | judgment | the conductor |

- The two sources are cross-checked, and every mismatch is reported as a fact: a file git shows
  changed that no tool call wrote, a write the JSONL shows outside the repository, a final reply that
  claims a step whose tool result failed, a decision quoted as the user's that no user message holds.
- The JSONL stays on the machine and is not in git, so what a later conversation or another machine
  needs to resume comes from commits; the JSONL serves the checks while the work runs.
- Fact, tried on Claude Code 2.1.293 (worker session, `try2/` in its scratchpad): a SubagentStop hook
  fires for an agent started through a skill with `context: fork` and `background: false`, in both an
  interactive session and `claude -p`; its input carries `agent_type`, `agent_transcript_path` and
  `last_assistant_message`; at that moment every tool call and result is in the JSONL, the final reply
  only in the input; a stdlib script listed files read and written, commands with exit status and a
  write outside the repository, wrote them to a YAML file the next turn read, in 0.02 s. The hook also
  fires for Claude Code's prompt-suggestion helper (`agent_type` empty), so it filters by its own
  agent type.

## How the conductor judges

As a test does: the gap between what was expected and what happened, then the next move.

- Expected: what passes, written before anything is made, as what the receiver can then do; it is a
  required field of the Return's IN. Written after the work is seen, it bends to the work.
- What happened: the user-tester's report of using it as the receiver.
- Breaches: the mismatches the cross-check of the JSONL and commits reports.
- The next move is one of: accept and go on; have only the gap remade; ask the user, when what was
  expected was never decided; go back a stage, when what was expected was wrong.

## When the conductor calls the user

- Only when: an IN lacks what only the user knows (what they want, why, how much effort is worth how
  much safety); what was expected turns out undecided or wrong; a sign-off.
- One point per message, even with several waiting, so each can be talked through until both see the
  same thing; asked together, the user answers the one they follow and the rest go half-decided. The
  points still waiting stay in the CCS as `uncertainty_signal: pending`, so none is lost.
- Nothing the records can settle is asked; the facts found come with where they came from. A question
  about what the user wants carries no proposed answer; a choice among ways gives what each gives and
  costs, and the one recommended, with why.
- The user is never called to wait: a turn ends only when nothing runs in the background.

## What is agreed with the user lives above the Returns

- A Return is a leaf: its IN cannot say what the user must agree. The user agrees at the level above:
  what they want, why, what passes (the acceptance criteria) and what must hold (constraints).
- Agreement flows down and gaps flow up: a gap in a Return's IN that the agreement above settles is
  filled by the conductor, with where it came from; one that nothing above settles shows the
  agreement above was short, and is taken back up to be agreed with the user.

## Steering keeps its items; the work's state moves to the CCS

- Steering keeps rn's present items (`rn/references/steering.md`): the front matter, the goal and
  why, the acceptance criteria, facts decided by the user, facts checked with where, assumptions,
  rules, tasks with purpose and completion criteria, and what is not yet specified. Which facts the
  plan rests on is judgment, so checked facts stay, though their evidence is in the JSONL.
- What changes is where things live: steering changes only by the user's agreement, and the tasks
  made from it; the state of the work, now spread over `open/` notes and commits' decision lines,
  moves to the CCS.

## How a task joins its Returns

1. Its IN is filled from the task in steering (what it makes, what passes); a hook checks the required
   fields, and a gap nothing above settles goes back up.
2. The maker makes it, or returns the gap unmade.
3. One user-tester uses it once, as its receiver, and returns what happened.
4. The conductor judges the gap between what was expected and what happened, with the cross-checked
   facts.
5. Only the gap is remade; whether it holds is seen by doing again what the user-tester did where it
   tripped, not by a new user-tester.
6. A gap not closed after two remakes goes back up: what was expected, or the way of making, is wrong.

Weighed against the faults met, on paper only: it answers the generator writing first and returning
gaps after (8 rounds, 45 min), asking what rn could settle (#45), pith run about three times per
document (#37), rounds on the same remark, trusting the maker's account, and hooks stopping others
(#43, #44). It does not answer the three below, left open.

## One conductor per session; a plugin called by another lends its Returns and domain parts

- Only the conductor of the plugin the user started talks with the user, agrees, and judges. A plugin
  it calls lends its Returns and its domain parts (each Return's IN required fields, its viewpoints);
  the conductor fills the IN with the user from those fields and calls the Returns.
- This is the orchestrator-worker pattern: in Anthropic's multi-agent research system the user talks
  with the lead only, and subagents work in their own context and return condensed results. Claude
  Code removes `AskUserQuestion` from every subagent, and uses subagents so the main conversation is
  not flooded (official docs, sub-agents).
- Running the called plugin's conductor inside the caller's conversation floods it (rn's conductor
  reached 1.7 MB in the trial); running it apart leaves it unable to ask the user, so questions go
  back and forth through the caller.
- Cost noted by the same article: multi-agent systems use about 15 times the tokens of a chat, so
  agents are added only where needed.

## Resume

- A fresh conversation reads from the top down: steering (the goal, what was agreed, the tasks and
  which are done, so which task is current), then that task's latest CCS (how far it came, what waits),
  then only what the CCS points to (approved documents, commits). Read from the leaf up, it could go on
  in a way the agreement above no longer holds.
- A CCS is kept per task, in the repository, committed and pushed as decided, so the next day or
  another machine starts from the same place. The JSONL stays on the machine and is not used to
  resume.

## Open

- rn writes the README, design and verification documents before building, so the details of a
  product that does not exist yet are invented in prose; how rn's stages are laid out.
- Ending a turn while work runs in the background: left until it is reproduced. Seen once in the
  present rn's trial (the conductor ran the product under construction, `claude -p
  /pr-rules:learn`, longer than a foreground command can wait); Agent-tool starts, the other cause
  seen, no longer happen since Returns are skills that wait.

## Where this stands (for a summarized conversation to go on from)

- The agreed points above are written as `docs/plugin-design.md` (Japanese, for review on PR #50;
  English before merge). It was read through and fixed statically (fa0a996).
- Next agreed: rebuild pith, writ, rn from zero on it, in that order, fixing the design from what each
  rebuild shows. This conversation (fix-rn-d3) decides with the user; the worker session fix-rn-3f
  builds on instruction and reports, never deciding the design.
- pith rebuilt up to the README's first gain by the worker (b5a5bb8): Return-only, the caller's
  conversation judges, an IN hook (PreToolUse on Skill, verified to block a call with missing fields)
  and a facts hook (SubagentStop). Words read per call: conductor 2213 -> 1637, first user 1532 ->
  about 1256. Scene pr-review-hole ran in 4 min; the fixture's hole did not reproduce (caught 3/3).
- The four gaps pith's rebuild showed were settled from each role's purpose and written into the
  design: required IN fields follow each role's purpose (the pass condition goes to the maker and the
  judge, never the user-tester); a Return-only plugin keeps its CCS where the caller says, or outside
  the repository and removes it, since the CCS exists to resume; the base starts with two hooks (IN
  check, facts), others only once a failure reproduces; facts claim only what the records hold (reads
  by command and writes outside the repository by command are not seen). The judgment part of a
  Return-only plugin's CCS is written by the calling conversation, which judges.
- Next: the worker brings pith in line with these (the user-tester's IN, where its CCS goes), then
  writ.
- Where the common parts live is still open (they sit in pith for now).
- Settle what follows from the agreed purpose without asking; ask the user only about purpose or
  intent that is not yet settled.
- writ rebuilt to its first gain (up to 5aa1241). migration-plan, same fixture: in use 9.9 min / 6
  user turns; rebuilt 7.4 min / 4 turns, none of them answered by the request or the repository.
  Words per call: conductor 3,381 -> 1,841, generator 2,118 -> 1,422. Design fixes it brought: CCS and
  plan place without Resume, the conductor clears a settled gap, fix/keep, shared parts as identical
  copies tested once, fill from the request and repo before asking, how to tell a point that is not
  the user's. Two questions still went to the user against that last rule in one run; left until it
  shows again.
- Next: rn's first gain on the design. Then the remaining README gains of pith, writ and rn (writ's
  commit and lint, pith writing an essentials file), each built only as its README story needs.
- (2026-10-09) Reports had shown only cost (time, turns, words); the user pointed out the gains were
  never judged. The design's verification now says: each README promise first, judged by a blind
  stand-in receiver comparing with the version in use, then cost (470e711). The version in use is
  rn 0.8.0, writ and pith 0.1.0 (writ 0.1.0 carries its own check).
- writ blind comparison: first the rebuilt document lost to 0.1.0 (holes lost in the conductor's
  plan; fixed in 95bac41). Then writ6 won against 0.1.0 run to its end (writ010c): 6.7 vs 43.2 min,
  4 turns each. Left, seen twice: the conductor asks the user the reader's points and writes
  unsourced inferences as decided; the agreement section was rewritten around whose decision a
  point is (fe3c4cc). Next for the worker: finish the rn 0.8.0 vs rebuilt runs, then put fe3c4cc
  into writ and rn and rerun writ with a blind reader against writ6.
- CI had failed on every push from 61db0ee to 4831c6a (rn/hooks/record.py:48 unrun); green since
  afa9dbd. Check CI after each push.
- rn-try: #78 closed by the worker (its rn080 run). #74 and #75 (2026-10-07) open; no record shows who
  made them.
- (2026-10-09) writ7 (fe3c4cc) lost to writ6 blind: an inference given a source, a generator
  inference not reported, stale files never traced, a non-question. 25d9fae: the first user checks
  what the receiver relies on against the real thing; a stumble is looked up before it is written as
  undecided. writ8 and writ8s (generator Sonnet, first user Opus) both beat writ6; writ8s beat writ8,
  one run each. b0b22a4: writ's conductor never edits the work. The model split waits for the
  evaluation method.
- Evaluation method, being agreed with the user point by point (nothing written into the design
  yet; 75b44c1 was reverted in a29ec64 because it was written before agreement). Base: Anthropic's
  "Demystifying evals for AI agents": tasks with success criteria and reference solutions, from
  real failures; code graders first, LLM graders one per dimension, calibrated by the user; several
  trials; read the transcripts. Start small, one plugin first; non-functional measures to be
  discussed after the functional ones.
- Agreed with the user: the common base is four roles (conduct, make, use, learn), the CCS and
  resume; each plugin adds only its domain content. The learner runs every turn and reads all facts
  (first user's results, JSONL, commits). It only outputs learnings; the conductor decides
  everything. Content learnings are fixed at once. Process learnings go into the session's steering
  rules and apply from the next turn. At the end the conductor asks the user whether to send them as
  an issue (feedback) to the plugin's repository. Process learning is in every turn, at a cost,
  because left to the end it gets skipped.
- Survey (2026-10-09): takt, AWS AI-DLC and Archon hold the flow in a runner, not in prose. takt
  says "prompts alone do not enforce behavior". AI-DLC PR #1624: the agent reads the user's reply and
  the engine keeps their words. takt assembles each role's prompt from facets. Fix rounds are capped
  in superpowers and cc-sdd. Few have a fresh agent use the work as its receiver would. Options for
  the base in Claude Code: (A) a shared prose skill, (B) flow state and the CCS held by fw's scripts
  and hooks, with the conductor talking and judging, (C) Claude Code workflows for the stretches
  without the user. B looks likely; it will be tried small before the design is written.
- The common base goes in its own plugin, named fw (framework), that writ, pith and rn depend on.
  fw holds the make, use and learn roles, the conductor's common flow, the CCS and resume; each
  plugin keeps only its domain content. No precedent was found in Claude Code for a depended-on
  base plugin (official plugins copy), so writ is tried on fw first; the fallback is identical
  copies.
- (2026-10-09) fw's purpose, agreed with the user:
  1. The user spends time only on their own decisions and gets what they want.
  2. Work that takes days, or outlives a conversation, goes on from where it stopped.
  3. It gets better with use. Content learnings are fixed at once. Process learnings act as
     session rules, and at the end go to the plugin with the user's consent.
  4. Whether it got better is judged from facts. What the user gets and what they pay are measured
     as numbers. A drop is traced to its cause in the records (JSONL).
  5. The common flow lives in one place. It is fixed once and checked once, apart from the domain
     content, which can be swapped for mocks. A plugin maker writes only the domain content.
  6. The flow holds when tasks are added, removed or reordered during the work.
  7. It never gets stuck (no deadlock), and never touches other sessions or files outside the
     repository.
  8. fw itself stays small; it adds only what prevents a reproduced failure.
  What the flow control must ensure:
  - The work reaches the user only after a first user has used it.
  - The user is called only for their own decisions.
  - The state is in the record, and work resumes from anywhere.
  - Learnings come out every turn.
  - Tasks can be added, removed and reordered.
  - Every state can go on or go back to the user.
  - Every move can be traced from the facts afterwards.
- Still open, to be derived from that purpose: how the flow is held: prose in one place, a script
  with a state-transition table (the user asked for exhaustive transitions), or both. Proposed and
  not yet agreed: two layers. Steering is data the conductor changes (tasks change during the
  work). The cycle inside a task is a fixed state-transition table. A script is the one way to
  change the record. The user warned that scripts and hooks can deadlock. Also open: the
  evaluation method (functional first, then non-functional) and the model split.
- Order agreed: start from fw itself, with the domain parts as fixed mocks, to check the flow
  control; then put pith's real content on it.
- Agreed (2026-10-09), how fw holds the flow:
  - No script or hook just for the flow.
  - An exhaustive state-transition table is written. Each transition becomes a condition checked
    before a role is called, by the existing IN-check hook.
    - The result goes to the user only when the CCS records a first-user use.
    - The maker is called again only when the last turn's learnings are recorded.
  - State and facts are kept by the existing facts hook, the CCS and commits.
  - The conductor decides whose decision a point is, and changes steering's tasks.
  - Hooks block only role calls, never the user exchange or the end of a turn. A block always says
    what is missing.
  - Tests check that every state can go on or go back to the user.
- (2026-10-09) Decided with the user:
  - Roles are started once and held through messages that say task, role and step. The reply says
    what it answers. Numbers are not used. No role is left working at a pause or at the end.
  - The fw design is dev/fw/design.md. Each plugin has dev/<plugin>/README.md (developer guide) and
    dev/<plugin>/design.md (why). <plugin>/README.md is for users, with a link for developers.
    Developer rules move from .claude/rules/plugin.md into those files; the rules keep only
    register, release and the structure check.
  - One PR per plugin: fw first, then pith, writ and rn.
  - Unneeded things are deleted. rn-try #74 and #75 are closed, with their branches deleted. The
    stray coverage file is untracked (42d853d). The worker's old trial JSONL is deleted.
  - Next: the evaluation method. fw is being built by a one-shot agent started from this session;
    fix-rn-3f takes no more work.
