# turn, rebuilt from zero

What the user and the assistant agreed on 2026-10-31 for the new turn. It is decided apart from the
turn as built today, and turn's README and architecture are rewritten from it.

## Concept: build quality up

Given the user's purpose, the work's format and intended state, and the best practice of making it,
an AI draws the concept out of the user and builds quality up to a work that meets the purpose
well.

- Quality is the degree a work meets its user's purpose (ISO 9000:2015; Juran, fitness for use).
- The AI's skill is relied on inside each step: widening, deriving, and using the work in its user's
  place. The concept is the user's to choose, and a work is never passed by the one who made it.
- The concept is the one idea of how the work meets its user's purpose; everything else derives
  from it (Brooks, conceptual integrity).

## User and purpose

turn's user is the person who wants the work. A plugin such as rn connects that person and turn.
They get a work that meets their purpose well, and spend effort only where only they can decide.

## Best practice

Agreed on 2026-11-02. **The root is a deliverable that achieves its user's purpose.** Two best
practices together produce it.

1. **The deliverable's own best practice (Standard)**: the intended state of a deliverable that
   achieves its purpose.
   - **Goal**: what the user achieves with the deliverable. Who uses it and when only make this
     concrete.
   - **Format**: the deliverable's structure that meets the goal. Every part, and its order, is
     there because the goal needs it.
   - **Checklist**: questions that check, by the essence, whether the deliverable achieves the
     goal. They ask of each part, of each dependency among parts, and of the whole, so that no
     essence is missed. **Each asks what this brings its user toward the goal.** The evaluator
     stands in the user's place and, from the goal and the question alone, looks for what in the
     deliverable serves the user. A check of form or an example would narrow this to the letter
     and give a deliverable that meets it on the surface, so a question carries neither.
   - The format and the questions are judged from the goal alone, and carry no grounds.
2. **The content's best practice (Practice)**: **for each essence a question holds, the best way of
   thinking and the steps that meet it**, with the grounds of the best practice where they have
   worked, so the generator sees why the way is the best one.

## What turn takes and gives

turn needs nothing given: planner asks the kind of work where the request does not name it, and
Pin asks this work's purpose.
turn keeps a template for each kind, and gives a work of that kind. A caller such as rn may give
what it has already settled, so the user is not asked it again.

- A template holds the kind's **Format**, the shape of the work, and its **Checklist**, the
  questions a work answers yes to when it meets the kind's purpose. Both are written in JSON, so a
  script checks one against the other.
- How turn moves a work toward its goal is the same for every kind, so a new kind needs only a
  template. That way follows the plugin architecture: each role's flow lies in `core/roles/`, and
  Lane's routes carry the work from role to role, as Flow says.

## Design tree

A design tree is the decisions to make, each joined to the goal it serves. It is made from the
goal down: at each node, ask what must hold for it, until a fact or the user settles it (KAOS goal
refinement; Brooks, The Design of Design; Matt Pocock's grilling skill, MIT).

A decision has two joins. It contributes to the questions or decisions it serves, and by these
every branch reaches the root; one that does not serves nothing and is cut. It builds on the
decisions that must be made before it, and by these the order of deciding is found: a README's
scene serves whether the reader can picture their own work, and builds on what the README
promises.

A design tree is not the questions' dependencies. A decision made early, such as what a README
promises, is checked by a question answered last, such as whether the product keeps each promise;
and one decision serves many questions, one question rests on many decisions.

## Roles

The roles and the course, as [Turn's architecture](../../dev/turn/architecture.md) settled them on
2026-11-04, which supersedes the roles agreed on 2026-10-31.

| Role | Does |
|---|---|
| up | carries each point to whoever started Turn, and each answer back, as given; starts each role Lane names |
| planner | settles the kind of work, hands Pin the design file, reads the confirmed design out, hands each shortfall back to Pin, and hands the work back |
| Pin's pinner | settles the design with the person, one point at a time, as Pin is built; Turn is Pin's maker AI |
| generator | makes the work from the design against the kind's best practice, then makes how it reads better |
| evaluator | uses the work as its user would and answers the questions, never given the design |

- The planner asks the person one point only, the kind, and only before there is a design. Pin
  alone settles the design: the planner hands it each point a calling AI settled word for word,
  each settled by `maker`, and Pin puts every other point to the person or settles it from the goal
  and the facts.
- A kind new to Turn gets its best practice first, as a work of its own made by the same course,
  with `meta` as its best practice. The person approves its purpose and its questions as they
  approve any design.
- No role starts a subagent. The pinner and the generator find facts themselves.

### Use and answer

Both generator and evaluator do this, in the same way.

1. Read the work whole, and run what runs as its user would, in a throwaway copy.
2. Using it as its user would, write for each question met, with the lines that meet it, or not
   met, with what the user still lacks, never how to make it.

## Flow

A round is one making by the generator and its check by the evaluator, which starts fresh in each.
A phase is the set of questions a round asks, and a value of the run that `rounds.py` settles from
the run's folder.

1. The content phase: what the work says and does, by the kind's own questions, until every run of
   the evaluator finds every one met. A question not met goes back through Pin to the decisions
   that serve it, and the generator makes the work again from the design. A point the design leaves
   open goes back to Pin the same way. No role puts a fix onto the work beside the design.
2. The reading phase: how the work says it, by `refactor-doc` for a document or `refactor-code` for
   code, its structure bettered while what it says stays (Fowler, Refactoring). A question of how it
   reads that only a change to what it says can meet goes back to Pin, and the content phase
   follows again.

Lane's routes, each from a role on its result to the next:

| From | On | To |
|---|---|---|
| up, the orchestrator | | planner |
| planner | `asks`, the kind for the person | none, while the point waits |
| planner | `handed`, a Request for Pin | Pin's pinner |
| planner | `ready`, the design read out | generator |
| planner | `done`, the work handed back | the end |
| pinner | `asks`, a point or the design for the person | none, while the point waits |
| pinner | `done`, the design confirmed | planner |
| generator | `made` | evaluator, a run for each group of questions |
| generator | `open`, a point the design leaves open, or a change to what the work says | planner |
| evaluator | `more`, a question of what the work says not met | planner |
| evaluator | `met`, every question of the content phase met | generator |
| evaluator | `reword`, a question of how the work reads not met | generator |
| evaluator | `good`, every question of the reading phase met | planner |

Where the evaluator's runs give different results, the first in the order `more`, `reword`, `met`,
`good` is taken. A role that needs the person's answer ends with its point, and is resumed by
SendMessage with the answer, keeping its context. Each role gives its result by its plugin's result
script.

## Files

Each is JSON. Lane holds each role to them: the work read whole before an answer is written, from
Read's file_path, offset and limit; each file in its form by `in_form`; and an answer for every
question by the result script, which the role runs before it ends. A script checks only what Lane
does not hold, as below.
Keys follow the steering's rules: a name says its intent, a one-to-many join is nested, a many-to-many join lists IDs.

- `best-practices/<kind>.json`, one for each kind, in `plugins/turn/` for those Turn ships and in
  `.turn/` for those a user's runs make, in the form Best practice says: `standard`, with `goal`;
  `format`, with `parts`, each part `id`, `what` and its `parts`; `checklist`, each question `id`,
  `about` (a part, the parts of a dependency, or the whole) and `what`; and `practice`, with
  `methods`, for each essence a question holds: `question`, the ID; `thinking`, the way of
  thinking that meets it; `steps`, in order; and `grounds`. The kind is the file's name. The evaluator is given `standard` alone, taken
  out by a script. A script verifies every part is looked at by a question, and every question has
  a method.
- `design-tree.json`, one for each work: `kind`; `goal`, this work's purpose, with its `grounds`;
  and `decisions`, each `id`, `what`, `contributes_to`, `builds_on`, `decided`, `settled_by`
  (`research`, `reasoning`, `user` or `maker`) and `grounds`, in Pin's form. Pin's check verifies
  every question is served, every decision reaches the root, and the order of deciding follows
  `builds_on`.
- The Answers of the generator and of each run of the evaluator, in `verification/`, in one form:
  `met`, each question whose aim the work meets, with the `lines` that meet it; and `not_met`, each
  question it is short of, with `lacks`, what the user still lacks, never how to make it. A script
  verifies every question stands in one of the two, and each line is there.

Questions that hold for every document, or for all code, are written once, in refactor-doc or
refactor-code; each question is named with its file, as `refactor-doc/Q3`. A refactoring best
practice has no `format`, as the deliverable keeps its kind's shape. A question copied into
each kind would be mended in one and left old in the rest.

Three best practices stand over every kind, each with one purpose:

- meta, the best practice planner builds every best practice with, refactor-doc and
  refactor-code among them: fit for its purpose. It is remade from rn's meta.md and rests on Think
  from the purpose: divide and give meaning, build in order, see across the branches.
- refactor-doc, how a document says what it says: understood as meant, on one reading.
- refactor-code, how code is written: changed with confidence.

A kind's own best practice gives what its deliverable says and does, and the refactoring one how it
says it.

## Sources

- Anthropic, "Harness design for long-running application development" (2026-03): planner,
  generator and evaluator.
- Common ground of staged making: success criteria first, a thin whole first, each step checked by
  someone other than its maker, back on a failure (Double Diamond, Wirth's stepwise refinement,
  walking skeleton, Stage-Gate, README Driven Development, Amazon Working Backwards, ISO 9241-210).
