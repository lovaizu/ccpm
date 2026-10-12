# Design document

A design document is read by someone who builds or maintains a product. It lets them:

- tell each quality the product must have, and within what limits;
- tell how each quality is checked;
- see how each quality is achieved, from the whole to each part;
- decide whether a change fits the design;
- tell why each choice was made over the other options.

How the product is used is the README's; code, full definitions, steps, settings and file names
are not for this reader, since they change with each rebuild. Each item of `doc.md` also applies to
a design document.

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

For each thing someone outside the product relies on, can the reader tell who relies on it, what
must keep holding, and what may change?

What others rely on: commands and settings users type, what other programs call or read, and what
the product leaves in the user's environment.

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

For each benefit, can the reader tell in what situation it is tried, and what must happen to the
user for it to pass?

Why: a check in a situation the other ways handle as well passes without showing the benefit, and a
check of whether the output has the intended shape passes while the benefit is missed.

### B-8: One-dimensional quality measured

For each one-dimensional quality, can the reader tell how it is measured and what it is compared
with?

Why: a quality not measured worsens without anyone noticing; measured against the version in use, a
change shows whether it made the product better or worse.

### B-9: Must-be quality checked

For each must-be quality, can the reader tell which test checks it?

Why: what a test can decide gives the same answer every time, and what the user takes for granted is
noticed only when it breaks.

### B-10: Backward compatibility checked

For each thing others rely on, can the reader tell which test shows it still works as earlier
versions left it?

Why: a break in backward compatibility shows first to the users who rely on it, after the release.

### B-11: Principles to judge a change

Can the reader decide whether a change fits the design from its principles, each with the quality or
the constraint it protects?

Why: a principle tied to what it protects tells what breaks when it is not kept, so principles can
be weighed against each other; one tied to nothing is kept out of habit.

### B-12: Who takes part

Can the reader see, in one place, who takes part, what each does, what passes between them, and what
each depends on?

Who takes part: the user, the product's own parts, and what is outside it, such as the host the
product runs in, other programs and the tools it needs.

Why: a maintainer changing one part needs to know what it hands to and takes from the others, and
what it cannot work without.

### B-13: An approach for each quality

For each quality the design must have, can the reader find the approach that achieves it?

Why: a quality no approach serves has no way to come about, and an approach that serves no quality
is kept for nothing.

### B-14: How each approach is built

For each approach, can the reader tell the parts it uses and how they work together?

Why: a maintainer changes an approach through its parts, and a part whose role is not known is
changed without knowing what it holds up.

### B-15: What must always hold

For each approach, can the reader tell what must hold after every operation?

Why: read as a condition, it keeps holding when one place is changed; read as one step of a
procedure, it is lost when the procedure changes.

### B-16: Why this way

For each choice a maintainer might want to change, can the reader tell which other options were
weighed, why they were not chosen, and what the choice costs?

Why: without the reasons, a decision is either kept blindly or overturned without knowing what it
cost.

## Usability

### U-1: Few principles

Is each principle needed across more than one approach?

Why: few principles can be kept in mind and weighed against each other; a rule that concerns one
approach belongs with that approach, and listed among the principles adds one more thing to keep in
mind everywhere.

## Format

### F-1: Shape

Does the design document follow this template, headings included?

```markdown
# <Product name> design

<What this document covers, with a link to the README whose benefits it serves>

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

### Principles

### Structure

### <Approach name>

<The qualities it achieves, how it is built, what must always hold, and the options weighed>
```

- A section with nothing to hold keeps its heading and says `None:` and why, so a section thought
  through is told from a section forgotten.
- Verification checks each quality by its heading in Goals, and each approach in Architecture names
  the qualities it achieves, so each quality is traced from what it is to how it is checked and how
  it is achieved.

Why: a maintainer moving between products finds the same thing under the same heading in each, and
settles what is aimed at and how it is checked, neither of which depends on how the product is
built, before reading how it is built.
