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
- The orchestrator checks the claim against the work and sends back what it can see falls short
  before the first user reads, so the costly reading is not spent on it.
- The first user reads the work in the receiver's place; the evaluator shows from that reading the
  items met, with their lines; the orchestrator checks those lines against the work and decides
  each item; the learner finds, for each item not met, how the work would meet it, and the
  orchestrator sends that back to the generator.
