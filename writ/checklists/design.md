---
name: design
version: 0.3.0
---

# Design document

A design document is read by whoever builds or changes the product, to know how it should be built.
Following the design, they implement it and secure its quality without hesitating.

How the product is used is the README's; how each part behaves, with its steps, definitions,
settings and file names, is the code's, since these change with each rebuild while the design
holds. Each item of `doc.md` applies to a design document with how the product brings about its
promises as its subject, and its B-16 is answered by the figure B-32 asks for. The reader comes from
the README, so Goals and Verification are said in its words, and each name of a part inside the
product is first met in that figure.

## Benefit

### B-1: Attractive quality

Can the reader tell which benefits, of those the README promises, the design must bring the user?

Why: the benefits are why the user chooses the product, and every other part of the design serves
them or keeps them safe.

### B-2: One-dimensional quality

Can the reader tell which qualities are better the more of them there is, such as less time taken
or fewer tokens spent?

Why: such a quality is weighed against the others in every choice, and one left unnamed is given up
without anyone deciding to.

### B-3: Must-be quality

Can the reader tell what the user takes for granted, such as not losing work?

Why: the user does not ask for it and notices it only when it breaks, so a design that does not name
it is free to break it.

### B-4: Backward compatibility

For each thing someone outside the product relies on, can the reader tell what must keep holding?

What others rely on: commands and settings users type, what other programs call or read, and what
the product leaves in the user's environment, each with who relies on it. What must keep holding is
what each lets them do.

Why: a change to it breaks those who rely on it, who are not there to object; the design document is
the one place that outlives a rebuild of the code.

### B-5: Non-goals

Can the reader tell what the design could have aimed at but leaves out on purpose?

Why: without the non-goals, a maintainer takes up what was left out on purpose as a gap to fill.

### B-6: Constraints

Can the reader tell which conditions the design cannot change, such as where the product runs and
who uses it?

Why: a change weighed without them turns the design into one that cannot run where it must.

### B-7: Attractive quality checked

For each benefit, can the reader tell what must happen to the user for its check to pass?

Why: a check of whether the output has the intended shape passes while the benefit is missed.

### B-8: One-dimensional quality measured

For each one-dimensional quality, can the reader tell how it is measured?

Why: a quality not measured worsens without anyone noticing.

### B-9: Must-be quality checked

For each must-be quality, can the reader tell how a test shows it holds, such as the case that
would break it?

Why: what a test can decide gives the same answer every time, and what the user takes for granted is
noticed only when it breaks.

### B-10: Backward compatibility checked

For each thing others rely on, can the reader tell how a test shows it still works as earlier
versions left it?

Why: a break in backward compatibility shows first to the users who rely on it, after the release.

### B-11: Principles to judge a change

Can the reader decide whether a change fits the design from its principles, because each principle
is said as what a change must keep, so whether a change fits is read off it?

Why: without principles, a change can be held only against the code as it stands, where every
difference looks like a break and none can be told from one that matters.

### B-12: Who takes part

Can the reader tell what each one that takes part in the product's work does?

Who takes part: the user, the product's own parts, and what is outside it, such as the host the
product runs in, other programs and the tools it needs.

Why: a maintainer changing one part needs to know every other its change can reach; one left
untold is reached without anyone seeing it.

### B-13: An approach for each quality

For each quality the design must have, can the reader find the approach that brings it about, said
as the idea of how it comes about and who takes part in it?

Why: a quality no approach serves has no way to come about.

### B-22: Where each benefit is tried

For each benefit, can the reader tell in what situation it is tried?

Why: a check in a situation the other ways handle as well passes without showing the benefit.

### B-23: What a measure is compared with

For each one-dimensional quality, can the reader tell what its measure is compared with?

Why: measured against the version in use, a change shows whether it made the product better or
worse; a measure compared with nothing shows neither.

### B-24: What each principle protects

Can the reader weigh two principles against each other where a change keeps only one, because each
names the quality or the constraint it protects?

Why: a principle tied to what it protects tells what breaks when it is not kept; one tied to nothing
is kept out of habit, and cannot be weighed.

### B-25: What passes between them

Can the reader tell what passes between each two that take part, from which to which?

Why: a maintainer changing one part needs to know what it hands to and takes from the others.

### B-26: What each one depends on

Can the reader tell what each one that takes part cannot work without?

Why: a part changed without knowing what it rests on stops working wherever that is missing.

### B-31: Why each option was turned down

For each other approach that was weighed, can the reader tell why it was not chosen?

Why: without the reasons, a decision is either kept blindly or overturned for an option already
weighed and turned down.

### B-32: The whole in one place

Can the reader see the whole of who takes part in one figure, instead of piecing it together from
the approaches or from tables?

The whole: what each one that takes part does, what passes between them and what each cannot work
without, as B-12, B-25 and B-26 ask. What the figure cannot show is said beside it, and nothing it
shows is said again.

Why: a maintainer changing one part needs all it touches at once; pieced together in the head, it
costs effort and goes wrong.

## Usability

### U-1: Few principles

Can the reader keep every principle in mind, because each is one needed across more than one
approach?

Why: few principles can be kept in mind and weighed against each other; a rule that concerns one
approach belongs with that approach, and listed among the principles adds one more thing to keep in
mind everywhere.

### U-2: Decisions told from details

Can the reader tell each decision that must hold from a detail that may change, because the
document holds nothing decided anew with each build, such as steps, full definitions, values,
settings and file names?

Why: such details change with each rebuild, so a design that holds them must be rewritten with the
code, and the reader can no longer tell a decision that must hold from a detail that may change; an
idea the design takes up is given in full as a decision and its reason, not as its specification.

### U-3: Each case left to the principles

Can the reader keep in mind only the principles and the decisions, because the document writes down
no case of how the product behaves that one of its principles already settles?

Why: maintainers work out each case from the principles and the decisions; a case written down reads
as one more rule to keep beside them, and must change with the implementation though no decision
did. A trial's finding is traced to the principle it breaks and fixed in the implementation, not
added to the design.

### U-4: What others rely on, by what it gives them

Can the reader tell a name that must be kept from one the build may change, because the design gives
a name, a path or a value of what others rely on only where they rely on that very name?

Why: a name made a promise where others rely only on what it gives ties the design to the build,
and must be kept when the build would change it.

## Format

### F-1: Shape

Does the design document follow this template, headings included?

```markdown
# <Product name> design

<The design's main point, with a link to the README whose promises it keeps>

## Goals

### Attractive quality

### One-dimensional quality

### Must-be quality

### Backward compatibility

### Non-goals

### Constraints

## Verification

### Attractive quality

### One-dimensional quality

### Must-be quality

### Backward compatibility

## Architecture

### Structure

### Principles

### <Approach name>

<The qualities it brings about, the idea of how, who takes part, and why each other approach
weighed was not chosen>
```

Why: a maintainer moving between products finds the same thing under the same heading in each, and
settles what is aimed at and how it is checked, neither of which depends on how the product is
built, before reading how it is built; and meets who takes part before the principles and approaches
that name them.

### F-2: A section thought through

Does each section with nothing to hold say, after `None:`, why it holds nothing?

Why: a section thought through is told from a section forgotten.

### F-3: Each quality checked under its heading

Does Verification check each quality under the heading it has in Goals?

Why: each quality is traced from what it is to how it is checked.

### F-4: Each approach names its qualities

Does each approach in Architecture name the qualities it achieves by the headings they have in
Goals?

Why: each quality is followed from Goals to the approach that achieves it, and an approach that
names no Goals heading, kept for nothing, shows.
