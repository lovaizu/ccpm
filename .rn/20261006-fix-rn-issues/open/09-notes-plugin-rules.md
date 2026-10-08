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

## Open

- What the level above (steering) is made of.
