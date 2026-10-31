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

## What turn takes and gives

turn takes a template for each kind of work and gives a work of that kind.

- A template holds the kind's **Format**, the shape of the work, and its **Checklist**, the
  questions a work answers yes to when it meets the kind's purpose. Both are written in JSON, so a
  script checks one against the other.
- How turn moves a work toward its goal is the same for every kind, so a new kind needs only a
  template. That way draws on agents' best practice and on what lane and turn have done, and is
  to follow the plugin architecture where that serves; whether it does is still to judge.

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

| Role | Does |
|---|---|
| planner | designs the intended state of a kind of work from its best practice |
| designer | designs the work from the intended state |
| builder | makes the work from the design |
| evaluator | uses the work as its user would and verifies it against the Checklist |

### planner

1. Decide the kind of work from the request, and confirm it with the user.
2. Where a template for the kind exists, pass it to designer and end.
3. Research the kind's best practice.
4. Put the kind's purpose, who uses such a work and for what, at the root of a design tree, and
   split it down. Every decision comes from the best practice.
5. Write the leaf conditions as the Checklist's questions, by the meta-checklist's way of writing,
   and the shape as the Format.
6. Show the kind's purpose and the conditions to the user for approval; on a change, go back to 4.
7. Keep the Format and the Checklist as the kind's template, and pass them to designer.

The purpose of this one work is not planner's: designer asks it.

### designer

1. Take the Format and the Checklist.
2. Make a design tree: this work's purpose at the root, the Checklist's questions under it, and
   under each question the decisions that make it yes, the same decisions merged.
3. A script verifies that every question is served by a decision and every decision reaches the
   root.
4. Decide in the order the decisions build on one another, the goal first: ask the user this work's
   purpose. Research each fact. Decide what the purpose and the best practice settle. Ask the user
   what only they decide, one at a time, with a recommendation.
5. Show the user the design, the decisions in short lines, for approval; on a change, go back to
   that decision.
6. Pass the design to builder.
7. Take back what builder or evaluator returns, and trace it to the decisions that serve its
   question. Where a decision is wrong, decide it again as 4 says, with the decisions that build on
   it; where the decisions hold and the work strays from them, keep them. Either way, pass the
   design to builder again.

designer alone changes the design and alone asks the user about it, so the work is always made from
one design.

### builder

1. Take the design, the Format and the Checklist.
2. Take the decisions in the order they build on one another, one at a time: make each into the
   work along the Format, use and answer the questions it contributes to, as below, and mend each
   more before the next. Decide the small points of making, such as a phrase or a function's name,
   from the design and the best practice.
3. Where a point the design leaves open bears on the work's quality, return it to designer
   unanswered.
4. With every decision made in, use and answer every question into `self-check.json`, mending each
   more, until every question is good. No one reads it: writing an answer for each question makes
   the builder look at every one.
5. Pass the work to evaluator.

### evaluator

1. Take the work and the Checklist alone. The design is not given: the user never sees it, and an
   evaluator who has it judges whether the work follows the design, not what its user gets.
2. Use and answer, as below, into `verification.json`.
3. Where every question is good, the work goes on. Otherwise return the answers to designer.

### Use and answer

Both builder and evaluator do this, in the same way.

1. Read the work whole, and run what runs as its user would.
2. Using it as its user would, write for each question of the Checklist good, with the lines that
   meet its aim, or more, with what the user gets once it is good, never how to make it.

## Flow

designer, builder and evaluator stay started, and go always in that order: each return goes to
designer, which passes the design to builder, whose work goes to evaluator.

1. The content phase: what the work says and does. The kind's own questions alone, made up
   decision by decision from the design tree, until evaluator finds every one good. A more is
   mended at the decision that serves its question, never added onto the work, as rn's fix
   checklist asks of a change.
2. The refactoring phase: how the work says and shows it, its structure bettered while what it
   says stays (Fowler, Refactoring). The questions of the `refactor-<kind>` template the kind's
   template names in `includes`, such as `refactor-doc` for every document and `refactor-code`
   for code, which hold over the whole work. builder finishes the work by them and evaluator
   verifies it by them, with no design tree. Only how the work says a thing changes; a point that
   would change what it says goes back to the content phase.

Keeping the two phases apart keeps builder and evaluator on the content while it is made. A phase
is named so as not to meet rn's stages, inside one of which turn runs.

## Files

Each is JSON. lane's lanes hold each role to them: `read_whole` has the work read whole before an
answer is written, `every_item` an answer for every question, `in_form` each file in its form, and
`end_when` the output made before the role ends. A script checks only what no lane holds, as below.
Keys follow the steering's rules: a name says its intent, a one-to-many join is nested, a many-to-many join lists IDs.

- `<kind>.json`, the template, one for each kind: `kind`; `purpose`, who uses such a work and for
  what; `format`, with `skeleton` and `parts`, each part `id`, `what` and `why`; and `checklist`,
  each question `id`, `what`, `why`, `about` (the parts it looks at), `grounds` and `examples`
  (`fails` and `passes`). A script verifies every part is looked at by a question.
- `design-tree.json`, one for each work: `kind`; `goal`, this work's purpose, with its `grounds`;
  and `decisions`, each `id`, `what`, `contributes_to`, `builds_on`, `decided`, `settled_by`
  (`research`, `reasoning` or `user`) and `grounds`. A script verifies every question is served,
  every decision reaches the root, and the order of deciding follows `builds_on`.
- `verification.json` from evaluator, and `self-check.json` from builder, in the same form: `kind`;
  `good`, each question whose aim the work meets, with the `lines` that meet it; and `more`, each
  question it is close to, with `good_when`, what the user gets once it is good, never how to make
  it. A script verifies every question stands in one of the two, and each line is there.

Questions shared by several kinds, such as those of every document, are written once in a template
of their own, and a kind's template names it in `includes`, as `readme.json` names `refactor-doc`;
each question is named with its template, as `refactor-doc/Q3`. A
question copied into each kind would be mended in one and left old in the rest.

## Sources

- Anthropic, "Harness design for long-running application development" (2026-03): planner,
  generator and evaluator.
- Common ground of staged making: success criteria first, a thin whole first, each step checked by
  someone other than its maker, back on a failure (Double Diamond, Wirth's stepwise refinement,
  walking skeleton, Stage-Gate, README Driven Development, Amazon Working Backwards, ISO 9241-210).
