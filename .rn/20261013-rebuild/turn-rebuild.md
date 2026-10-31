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
refinement; Brooks, The Design of Design; Matt Pocock's grilling skill, MIT). A node is decided
after the node it hangs from. Every branch reaches the root; one that does not serves nothing and
is cut.

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
4. Walk the tree from the root. Ask the user the purpose. Research each fact. Decide what the
   purpose and the best practice settle. Ask the user what only they decide, one at a time, with a
   recommendation.
5. Show the user the design, the decisions in short lines, for approval; on a change, go back to
   that decision.
6. Pass the design to builder.

### builder and evaluator

Their steps are still to agree.

## Sources

- Anthropic, "Harness design for long-running application development" (2026-03): planner,
  generator and evaluator.
- Common ground of staged making: success criteria first, a thin whole first, each step checked by
  someone other than its maker, back on a failure (Double Diamond, Wirth's stepwise refinement,
  walking skeleton, Stage-Gate, README Driven Development, Amazon Working Backwards, ISO 9241-210).
