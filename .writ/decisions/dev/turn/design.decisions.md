# What turn's design says

## design

### B-29: The user stories
- One story: as the calling AI, I want to hand turn a CCS and get back the work and a new CCS, as one
  turn of ACC. Reading, judging and making again are how the work is made, decided in the
  components.

### B-18: Every logical component the stories need
- Five components: the generator, the first user, the evaluator, the learner and the orchestrator.
  The evaluator and the learner are there for the builder's reasons, so that the story is achieved
  reliably: the orchestrator alone did not settle its judgments, and the generator alone patched
  where a shortfall showed; each component's reason is written in the design.
- turn is for an AI alone: it deals only with the AI that calls it. Nothing is shown to a person
  watching, and nothing is stopped or said again by one, so the progress shown on the console, the
  stop with Esc and the start again from a person's words go.

### B-19: The stories achieved by interactions
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
  the same `session_id`. How a role's `agent_id` is tied to its orchestrator's run is tried when
  built.
- `claude -p` is not used: the docs say `--bare`, which reads no subscription login, will become
  its default, and moving its use to separate credits was announced and only paused.

### B-20: How each component is realized
- The orchestrator and the four roles are agent definitions. What must come out the same on every
  run is done by Python 3 scripts with jq, and the hooks are Python checks, one file each, with one
  entry file per hook event, as `plugin.md` sets.
- The console and the stop with Esc go, as turn deals with no person.

### B-21: Where each component is placed
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
  the generator's claim. How a hook checks that a reply answers every item is tried when built.
- A run asked to stop ends with a reply saying the items decided so far and where it stopped. A
  run cut off leaves the work as written so far; the calling AI calls turn again, the generator
  makes the work again from what is there and the readings start again. No resuming part way:
  being cut off is rare, and a reading again costs less than a resume to build and keep right.

### B-22: What each component depends on outside
- Claude Code, python3 3.9 or later, jq and git.

### B-27: The qualities that come with each benefit
- The benefit: the work read inside turn by a reader other than the one that made it, as its own
  readers would, and made again where that reading found it short. Must-be:
  - The first user is not the generator and reads only what the work's receiver opens, since the
    generator's claim or the decisions handed over would be read into the work.
  - The first user reads the whole work, for every item, since an item not read comes back as the
    generator's claim.
  - The work returned is as it was last read: what is made again is read again before it returns,
    the second reading included, since a part not read again is the generator's assumption again.
  - The orchestrator decides each item by reading the work itself, taking neither the generator's
    claim nor the evaluator's lines on trust.
  - An answer comes back for every item, and each line named is in the work and meets the item, so
    the calling AI has firm ground to check against.
  - What only the user can decide comes back as a question, not filled by a guess, since work made
    on a guess can look met and still miss what the user meant.
  - Nothing but where the work goes is changed, and nothing is committed or pushed, since the
    calling AI checks the work alone and any other change stays unchecked.
  Better the more, each measured on every trial and compared with the last version:
  - The time a run takes, since the calling AI cannot go on with its step while it waits.
  - The cost of a run, since the four roles and the orchestrator run every time, at the user's
    expense.
  - How much the calling AI fixes after the work returns, counted as the items it fixes itself,
    since the more is settled inside turn, the more the benefit gives.

- The benefit: one turn of ACC, the calling AI going on from the new CCS alone. Must-be:
  - The new CCS alone tells the calling AI what to do next, without reading what went on inside
    the run.
  - However many times turn is called, the CCS does not swell: what turn writes replaces the last
    turn's, and nothing is added on.
  - What must come back as received does not change, held by the script's check before it returns.
  Better the more, measured on every trial and compared with the last version:
  - What each call adds to the calling AI's context, the CCS and the orchestrator's last reply,
    since the less it adds, the longer the calling AI can go on.

### B-23: Checks built up unit by unit
- The scripts: unittest fed what the calling AI hands over, a case each stops and one each lets
  through, every line and branch counted in CI on every push.
- The hook checks: unittest fed what Claude Code hands each hook, a step stopped where it must be
  and let through where it must be, counted the same way.
- The orchestrator and the four roles: each run on its own on a small task, on Opus 5.5, and judged
  from the JSONL by whether it did what its steps say.

### B-24: The whole checked
- Trials in the private `lovaizu/rn-try`, one at a time: a stand-in for the calling AI is handed a
  small task's decisions and checklist and calls turn; judged from the JSONL and the work. The
  story is achieved when the work comes back where it goes with an answer and lines for every
  item, each answer checked by reading the work.

### B-28: Must-be, checked
- The first user apart and reading only what the receiver opens: a test that the hook stops any
  other read; in a trial, everything the first user opened is what the receiver opens.
- The whole work read for every item: a test that the hook stops a reply that leaves an item out;
  in a trial, the first user opened all of the work.
- The work returned as last read: in a trial, nothing is written to the work after the last reading
  begins.
- The orchestrator deciding by its own reading: in a trial, it opens the work before it decides.
- An answer for every item, with lines that are in the work: a tested script checks each line named
  is in the work; in a trial, each line is read for whether it meets its item.
- A question, not a guess: a trial on a task with one decision left out returns a question.
- Nothing changed but where the work goes, no commit or push: a test that the hooks stop them; after
  a trial, git shows changes to the work alone.

- The calling AI going on from the CCS alone: in a trial, the stand-in takes its next move from the
  new CCS, with nothing of the run's inside in its context.
- The CCS not swelling: a test that the script writes turn's parts in place of the last turn's; in
  a trial called twice, the second CCS is no larger than the first beyond what the new turn says.
- What must come back as received: a test that the script returns nothing when it has changed.

### B-26: Better the more, measured
- The time and the cost of a run from the trial's JSONL, its timestamps and usage; the items the
  calling AI fixes after the work returns, and what each call adds to its context, counted from the
  stand-in's JSONL; each compared with the last version.

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
