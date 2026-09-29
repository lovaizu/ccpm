# Essentials

The essential viewpoints for each thing a session makes or does. Each asks not whether it was made or
done, but whether whoever receives it can do what it is for. Whoever makes a thing aims for its
section; whoever checks it asks the same questions, and answers each with Good and More.

## Goal

The Goal and Goal achieved when in `steering.md`.

- Can the user read it and say "yes, that is what I want, and why"?

    It is what the user really wants, not their first words, with the reason they want it. A plan
    built on the words achieves the wrong thing however well it is carried out, and the user finds
    out only at the end.

- Can whoever checks the deliverable tell, on the real thing, whether the goal is achieved?

    Each line of Goal achieved when is a state of the product, not an artifact or a step, so it holds
    whatever means are chosen. If every line held, the goal would be achieved.

## Plan

The rest of `steering.md`.

- Can the conductor carry the work to the goal by it, checking each task against its purpose?

    Every line of Goal achieved when is served by a task's purpose, or plainly by tasks planned once
    the design is settled. Each line of Purpose achieved when is a state checked on the real thing.
    Tasks that make the deliverable come only after the Design sign-off, since tasks planned before
    the design would mostly be rewritten once it is.

- Can a generator carry out its task without asking anyone?

    The Rules hold what the tasks must follow and cannot be told from the goal, such as the
    repository's conventions. Each Fact says how it was checked, and no Assumption hides a decision
    that is the user's.

## README

The document the `ux` field names.

- Can a newcomer tell what the product does for them, and start using it?

    It shows the product from whoever uses it: what they get, what they need, and how a use goes, in
    a scenario close to the real thing. What the product does, not how it is built.

## Design document

The document the `design` field names.

- Can whoever builds it make every decision on how to build from it?

    It holds the structure, each part's purpose, and what passes between parts, with no gap, in
    diagrams a person can follow, then what the diagrams cannot say. Each decision says what goes
    wrong without it, traced to what the product must deliver or a condition the design cannot change.

- Can whoever builds it read it and decide which qualities to check, how, and what passes?

    The qualities are drawn one by one from what the design says the product delivers, each with what
    the user struggles with if it fails; that the product achieves its goal comes before that its
    mechanisms work as designed. It says how far to check, and what that gives up.

- Can whoever changes it later tell why each decision was made, and what another way would lose?

    It holds only what cannot be read from the product itself and still holds if the code is
    rewritten. Names appear only where they are agreements with the outside, such as a file format or
    a directory layout.

## Task result

One task's changes, as they stand now.

- Does it fulfil its purpose on the real thing, within the design?

    Run where it runs, every line of Purpose achieved when holds, and the purpose holds beyond their
    letter. It follows the README, the design document, and the Rules.

- Does everything that worked still work, with nothing added that the purpose does not need?

## Deliverable

Everything the session changed apart from its directory under `.rn/`.

- Can the user approve it as achieving the goal?

    Run where it runs, every line of Goal achieved when holds, and the checks the design document
    sets pass. The goal holds beyond the letter of those lines; a gap in them the work has exposed is
    named. Besides the work, only the session's directory under `.rn/` is left behind.

## Evaluation

What an evaluator returns, and what a generator returns as its self-check.

- Can the conductor decide each More from it, without asking back?

    Each Good and More points to a place in the real thing, a `path:line` or a command and its
    output, and says why. A Good says why it must be kept when fixing; a More says what the user will
    struggle with because of it, and a fix. Both carry the same weight: a Good given in one word leaves
    whoever fixes unable to tell what to keep, and they break what works. It says whether the purpose
    is served, not whether steps were followed.

## Decision

What the conductor decides for each More, and for what comes next.

- Does it bring the work closest to the goal, and settle?

    A More is fixed when fixing brings the work closer to its purpose and keeps the Goods; otherwise
    it is let go, with the reason. Acting on the letter of an evaluation redoes work that serves the
    goal. What only the user can decide goes to the user; everything else is decided from the goal.

## Question

What the conductor asks the user.

- Can the user answer on the spot?

    It is one point, one only the user can decide: taste, scope, effort against safety, what the
    product should be, another way when fixes keep falling short. It says how the conductor
    understands it, what it decides, what each way costs and gives, and which is recommended. What
    the repository, official documentation, or best practice can answer is looked up instead.

## Review request

What the conductor gives the user at a sign-off.

- Can the user decide to approve or give feedback without reading everything again?

    It gives the final Good and More for each viewpoint of what is signed off, each with the place in
    the real thing and the grounds, not the points and fixes along the way. A More left in place says
    why it was let go. Nothing fatal is left: something that is no use until fixed is not taken to a
    sign-off.
