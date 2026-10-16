# What turn's design says

## design

### B-29: The user stories
- One story: as the calling AI, I want to have a work made from the decisions and checklists I hand
  over. Reading, judging and making again are how it is done, decided in the components.

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
