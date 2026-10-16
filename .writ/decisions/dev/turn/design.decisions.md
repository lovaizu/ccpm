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
