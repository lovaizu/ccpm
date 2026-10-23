# What turn's design says

## Concept, agreed with the user (2026-10-23)

- User: the AI that runs a step of a plugin and calls turn from it.
- Purpose: the work comes back meeting every item of the checklists the calling AI gave, with
  nothing left for the calling AI to fix.
- Concept: an AI that did not make the work uses it in the receiver's place and goes back and forth
  with the generator until it finds each item's Good; through that back and forth the orchestrator
  reads no work and only passes what the flow gives. Each time the first user's reading ends, the
  orchestrator checks that each Good holds, and only the items that do not hold are made again in
  the next round. The orchestrator checks every round, so a run can end in one round.
- The calling AI deals only with the orchestrator.
- turn's own principles: (1) every role that makes or reads the work looks only for each item's
  Good and works only to give it; (2) each item is judged by what the receiver gets with what they
  have, never by whether the work matches its sources.

## design

### B-1: The stories the scenes rest on
- One story: as the calling AI, I want to hand turn the path of a CCS and get the work back, with
  each item's Good and the lines that give it. Reading, judging and making again are how the work is made,
  decided in the components.
- ACC and the CCS are rn's, closed inside it. In the paper, the compressor that makes the state is a
  model apart from the agent that acts on it, and the agent's output enters memory only through the
  next compression, after it is checked; so the compressor, the CCS's definition and the store, the
  repository, are the caller's, and turn is the agent that acts: it reads the CCS it is handed,
  follows it and writes its result where the call says.
- turn defines nothing of the CCS. A CCS is JSON: parts, each a list of entries, each entry a kind
  and its value. The caller hands turn, as JSON, the CCS's path, the kinds it uses for what turn
  takes from the task's state, and where turn writes its result:
  `{"ccs": "<path>", "kind": {"work": "<kind>", "checklist": "<kind>", "receiver": "<kind>",
  "use": "<kind>", "opens": "<kind>"}, "result": "<path>"}`. The kinds are where the work goes, the
  checklists, the receiver, who reads the work, what they read it for and what they open with it;
  the first three must each be named and have an entry, and the last two may be left out; a script takes
  every entry of each from the CCS and hands it to the roles that need it, so no AI copies it, and
  the hooks bound what each role reads by them. The generator reads the CCS whole. The values stay
  in the CCS alone, so the call and the CCS cannot differ. The result is not a kind: it is where
  this call's answer goes, not the task's state, which in ACC takes in the agent's output only at
  the next compression. It is one file, as one call gives one answer for the whole work.
- turn's result is where the work was written, each item's Good with its lines, the questions only
  the user can decide, and the items without Good, each with what the receiver gets once it is Good.
  A script writes it as a file and checks its shape as it writes: a reply would be copied into a
  file by the calling AI, where a slip goes unseen.

### B-2: Every logical component the stories need
- Five components: the generator, the first user, the evaluator, the learner and the orchestrator.
  The evaluator and the learner are there for the builder's reasons, so that the story is achieved
  reliably: the orchestrator alone did not settle its judgments, and the generator alone patched
  where a shortfall showed; each component's reason is written in the design.
- turn is for an AI alone: it deals only with the AI that calls it. Nothing is shown to a person
  watching, and nothing is stopped or said again by one, so the progress shown on the console, the
  stop with Esc and the start again from a person's words go.

### B-3: The stories achieved by interactions
- Only scripts doubt. Every role that is an AI looks, against the checklists, which say what the
  work should be, only for the Good each item gives and the lines that give it; a script doubts,
  such as by naming the lines no Good rests on. An AI that looks for what more the work needs
  finds more without end, and each find is patched in, so the work drifts from what it should be.
  Every role, the flow and how each judgment is made follow from this.
- The generator hands back only once it has read the work against each item and named the lines
  that give its Good; an item it cannot give, since only the user can decide what it needs,
  becomes a question, and what the decisions do not say is not filled in from its own guess. In
  the old turn's trials it filled the form from a grep of the headings within seconds, named lines
  for items it knew it fell short of, and said its doubts only in prose.
- The orchestrator reads the work first and sends back to the generator the items whose Good it
  does not find, each said as what the receiver gets once it is Good, not as the edit to make: a
  shortfall plain to see is sent back while it costs least, and in the old turn's trials an edit
  told to the generator broke another item. An item waiting on the user's answer is not sent back.
- Each role's part is one aim, from the checklists and looking for the Good, so the AI works to
  the aim rather than to a list of steps: the orchestrator runs the turn so that the Good builds
  up; the generator passes the checklists; the first user uses the work and looks for the Good; the
  evaluator looks for the Good the first user found and for any other Good the work gives; the
  learner looks through every record of the run for what makes the Good. The first user is given
  the checklists. The evaluator is there because one reader misses Good the work gives, and an
  item judged not Good by that miss is made again for nothing.
- How the work becomes Good is the generator's to decide: the orchestrator tells what the receiver
  gets once an item is Good, and the learner tells what it learned about how to make the work,
  such as what to read and ask before writing, where no item already asks it. In the old turn's
  trials, edits told per item broke other items and added what the decisions do not hold, while
  the learnings about making were the most useful thing the learner gave.
- The generator makes the work and names, as its own check, the lines it meant to meet each item;
  that is its claim, not a judgment.
- The orchestrator does not take the claim on trust: it reads the work against every item of the
  checklists and sends back what it can see falls short before the first user reads, so the costly
  reading is not spent on it.
- The first user uses the work in the receiver's place; the evaluator shows from that reading the
  Good the work gives, with its lines; the orchestrator does not take those on trust either: it
  finds each item's Good in the work itself and decides each item; the learner finds what makes
  the Good, and the orchestrator hands that to the generator.
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
### Inside turn
- Each role is checked at both ends, in its own form: a hook lets a role start only with the input the orchestrator is to give it, and stops a role's reply that
  does not fill its form, each line named in the work.
- The orchestrator settles its own finding of every item's Good, from its own reading of the work,
  before it sees the evaluator's: a script records it, and a hook lets the evaluator start only once
  it is recorded. The script then names the items where the two differ, and the orchestrator
  decides each of them against the first user's JSONL, what it opened and where it stopped. A
  judgment made after another's is pulled toward it, which words alone do not prevent.
- The learner looks at every item, with Good and without, in the work and in the JSONL of every
  role the run started: for an item without Good, how the work would give it; for an item with
  Good, what in the work gives it, so that making again keeps it. What fell short often lies in what
  a role did, which only the JSONL shows, and a Good is lost by a remake that does not know what
  gives it. What it learns is used within the run.
- A reading is one pass of the work through the first user, the orchestrator's own finding, the
  evaluator and the orchestrator's decision. The orchestrator reads the work against every item
  once the generator hands it back, sends back what it can see has no Good, and once nothing is
  sent back, its findings are recorded and the first user reads. When the reading gives every item
  its Good or a question, the run returns; otherwise the learner looks and the generator makes the
  work again, and a second reading follows, after which the run returns with what is still without
  Good. A question waits for the calling AI: it puts it to the user, and writes the answer into the
  work itself or into the CCS and calls turn again.
- What each role is given: the generator, the CCS whole, what is sent back and what the learner
  found; the first user, the work, what the receiver opens, who the receiver is and what for, and
  the checklists; the evaluator, the same and the first user's reading; the learner, every item's
  finding and the JSONL of every role of the run, which the hooks let it read by `parentAgentId`.
  The JSON forms are the builder's to settle.
