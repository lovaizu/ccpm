# What turn's design says

## design

### B-1: The stories the scenes rest on
- One story: as the calling AI, I want to hand turn a CCS and get back
  the work and a new CCS, as one turn of ACC. Reading, judging and making again are how the work is made, decided in the
  components.

### B-2: Every logical component the stories need
- Five components: the generator, the first user, the evaluator, the learner and the orchestrator.
  The evaluator and the learner are there for the builder's reasons, so that the story is achieved
  reliably: the orchestrator alone did not settle its judgments, and the generator alone patched
  where a shortfall showed; each component's reason is written in the design.
- turn is for an AI alone: it deals only with the AI that calls it. Nothing is shown to a person
  watching, and nothing is stopped or said again by one, so the progress shown on the console, the
  stop with Esc and the start again from a person's words go.

### B-3: The stories achieved by interactions
- The generator makes the work and names, as its own check, the lines it meant to meet each item;
  that is its claim, not a judgment.
- The orchestrator does not take the claim on trust: it reads the work against every item of the
  checklists and sends back what it can see falls short before the first user reads, so the costly
  reading is not spent on it.
- The first user reads the work in the receiver's place; the evaluator shows from that reading the
  items met, with their lines; the orchestrator does not take those on trust either: it reads the work against
  every item of the checklists, those the evaluator shows met and those it does not, and decides
  each item; the learner finds, for each item not met, how the work would meet it, and the
  orchestrator sends that back to the generator.
- The orchestrator is an agent definition, not a skill, so it runs as its own subagent and the
  calling AI's context holds only what comes back; the calling AI starts it in the background and
  waits, so it can still take the user's pause. The four roles are the orchestrator's own
  subagents. The progress a person sees is the subagent panel's.
- The calling AI stops a run by sending the orchestrator a message; the orchestrator can message
  the calling AI before it ends. Tried (Claude Code 2.1.301, Opus): two orchestrators started at
  once each started a worker, sent `main` a message that arrived while they ran, and took a stop
  sent to their ID after their next tool call.
- Several runs go at once, as rn starts them for work that can go in parallel: each run keeps its
  own state, and the hooks tell runs apart by `agent_id`, since every agent of a conversation has
  the same `session_id`. A hook ties a role to its run by the role's
  `<transcript_path without .jsonl>/subagents/agent-<agent_id>.meta.json`, whose `parentAgentId` is
  the orchestrator's `agent_id`: tried on Claude Code 2.1.302 (2026-10-17) with two orchestrators
  at once in the background, each starting roles, every role's tool use and reply was tied to its
  own orchestrator. The file is there from a role's first tool use, not yet at `SubagentStart`, so
  what a role is started with is checked at the orchestrator's own `Agent` call, which carries the
  orchestrator's `agent_id` and the prompt. The file is Claude Code's own record, not a documented
  hook input, so the hooks' tests hold its shape and a change to it is seen there.
- `claude -p` is not used: the docs say `--bare`, which reads no subscription login, will become
  its default, and moving its use to separate credits was announced and only paused.

### B-5: How each component is realized
- The orchestrator and the four roles are agent definitions. What must come out the same on every
  run is done by Python 3 scripts with jq, and the hooks are Python checks, one file each, with one
  entry file per hook event, as `plugin.md` sets.
- The console and the stop with Esc go, as turn deals with no person.

### B-6: Where each component is placed
- The `turn:acc` skill, `turn/skills/acc/SKILL.md`, holds in its body ACC's intent and the CCS's
  specification. The intent first, drawn from the paper (linked as its source, not to be read at run
  time): an AI that replays the whole conversation through a long task holds more each turn, attends
  less to what matters, drifts from its constraints and carries forward assumptions no one checked;
  so ACC keeps one small state, the CCS, and decides from it alone. Each turn the CCS is made anew
  and replaces the last, so it does not grow; it holds only what is confirmed and what decisions
  need: the goal, the constraints, which stay as they are unless changed on purpose, what changed,
  what is not settled, said openly, and what comes next; materials stay outside it as references,
  not their contents copied in; and its fixed shape is checked without asking a model. Knowing why, the calling
  AI judges what to write into a CCS and what to leave out, and carries the new CCS, not the run;
  steps alone it would follow by rote and fill the CCS with everything. The calling AI uses the CCS
  well only knowing the ACC it serves, and the
  swelling and drift ACC prevents are the caller's to prevent. In the body, not in `references/`:
  `references/` holds what would make the body long, and this is short; a SKILL.md that only says
  to read a file adds a step and gives nothing. A skill is called by name from any installed plugin, and a plugin built on turn names it in
  `dependencies`, so the calling AI reaches the specification wherever plugins are installed.
- The work is made where it goes, in the user's repository, not in a copy. A copy was there so
  that a person's stop with Esc left where the work goes as it was; turn has no such stop now. A run
  cut off leaves its writing as changes git shows, which the calling AI undoes or finishes, and the
  calling AI checks and fixes the work in place in any case. Runs at once make different files, as
  rn starts them for work that can go in parallel. Nothing of a run is put outside the repository.
- The roles' answers to one another, the generator's claim, the first user's reading and the
  evaluator's lines, are not files: each role gives its answer as its reply to the orchestrator, so
  a run leaves nothing behind, and only the orchestrator holds them, so the first user cannot see
  the generator's claim.
- A run asked to stop ends with a reply saying the items decided so far and where it stopped. A
  run cut off leaves the work as written so far; the calling AI calls turn again, the generator
  makes the work again from what is there and the readings start again. No resuming part way:
  being cut off is rare, and a reading again costs less than a resume to build and keep right.

### B-7: What each component depends on outside
- Claude Code, python3 3.9 or later, jq and git.

### B-8: Each unit checked, and how far
- The scripts: unittest fed what the calling AI hands over, a case each stops and one each lets
  through, every line and branch counted in CI on every push.
- The hook checks: unittest fed what Claude Code hands each hook, a step stopped where it must be
  and let through where it must be, counted the same way.
- The orchestrator and the four roles: each run on its own on a small task, on Opus 5.5, and judged
  from the JSONL by whether it did what its steps say.

### B-9: The whole checked
- Trials in `lovaizu/playground`, one at a time, each on a branch of its own removed after: a stand-in for the calling AI is handed a
  small task's decisions and checklist and calls turn; judged from the JSONL and the work. The
  story is achieved when the work comes back where it goes with an answer and lines for every
  item, each answer checked by reading the work.

### B-10: Key results measured
- From every trial, measured and compared with the targets in turn's UX and the last version: the
  items the stand-in fixes in the work after it comes back, counted from its own check in its
  JSONL; the time from the call to the return, from the JSONL's timestamps.
- That the new CCS can be handed on as it is, does not swell, and keeps as received what must come
  back so are functions, either working or not: the script's tests hold them, and the stand-in in a
  trial takes its next move from the new CCS alone.

### The CCS
- turn's CCS definition, in `turn/skills/acc/SKILL.md`, takes ACC's nine parts with the
  paper's names and meanings, and defines inside them only the kinds and values turn reads and
  writes; every other kind is the caller's to define.
- The new CCS is the state after the turn: the task's parts (what is made, for whom and what for,
  the materials, the rules) and everything turn does not define come back as received; what the
  turn changes (what changed in this turn, what is not settled, what to do next) is written anew in
  place of the last turn's, so the CCS does not swell, and the CCS returned can be handed to turn
  again as it is.
- A script checks the CCS at both ends: when a run starts, that the CCS received meets turn's
  definition, stopping with what is wrong and where the definition is; before it returns, that the
  new CCS meets the definition and that what must come back as received has not changed, returning
  nothing otherwise. Each check is tested.
- Inside turn, each role is checked at both ends too, in its own forms, not the CCS: a hook lets a
  role start only with the input the orchestrator is to give it, and stops a role's reply that
  does not fill its form, every item answered and each line named in the work.
- The orchestrator settles its own judgment of every item, from its own reading of the work,
  before it sees the evaluator's: a script records it, and a hook lets the evaluator start only once
  it is recorded. The script then names the items where the two differ, and the orchestrator
  decides each of them against the first user's JSONL, what it opened and where it stopped. A
  judgment made after another's is pulled toward it, which words alone do not prevent.
- The learner looks at every item, met and not, in the work and in the JSONL of every role the run
  started: for an item not met, how the work would meet it; for an item met, what in the work meets
  it, so that making again keeps it. What fell short often lies in what a role did, which only the
  JSONL shows, and an item met is broken by a remake that does not know what holds it. What it
  learns is used within the run.
- The kinds turn defines, all else the caller's:
  - `focal_entities`: `deliverable`, where the work goes; `receiver`, who reads it. The caller's.
  - `goal_orientation`: `use`, what the receiver reads it for; `acceptance`, when it is enough. The
    caller's.
  - `retrieved_artifacts`: `checklist`, `decisions`, `reference`, `receiver_opens`. The caller's.
  - `constraints`: `language`. The caller's.
  - `episodic_trace`: `item`, for each item whether it is met and the lines that meet it. turn's.
  - `uncertainty_signal`: `question`, for the user; `unmet`, an item not met and why. turn's.
  - `predictive_cue`: `next`, one of `done`, `ask the user`, `fix`, the caller fixes. turn's.
  - `semantic_gist`, `relational_map`: none.
  That the work was written is read from `deliverable`, so no kind says it again.
