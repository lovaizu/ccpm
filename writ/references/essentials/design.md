# Design document

A design document is read by someone who builds or maintains a product. It lets them:

- trace each benefit the README promises to the feature that brings it, and see how that feature is
  built;
- tell what the design aims at, what it leaves out on purpose, and what it cannot change;
- decide whether a change fits the design;
- tell why each choice was made over the other options;
- keep working what others outside the product rely on;
- tell how each quality of the product is checked.

Code, full definitions, steps, settings and file names are not for this reader, since they change
with each rebuild. Each item of `doc.md` also applies to a design document.

## Benefit

### B-1: A feature for each benefit

For each benefit the README promises, can the reader find the feature that brings it to the user?

Why: a benefit no feature serves has no way to reach the user, and a feature that serves no benefit
is kept for nothing.

### B-2: How each feature is built

For each feature, can the reader tell the parts it is built from and how they work together?

Why: a maintainer changes a feature through its parts, and a part whose role is not known is changed
without knowing what it holds up.

### B-3: Goals and non-goals

Can the reader tell what the design aims at, and what it could have aimed at but leaves out on
purpose?

Why: without the non-goals, a maintainer takes up what was left out on purpose as a gap to fill.

### B-4: What cannot change

Can the reader tell which conditions the design cannot change, such as where the product runs and
who uses it?

Why: a change weighed without them turns the design into one that cannot run where it must.

### B-5: Principles to judge a change

Can the reader decide whether a change fits the design from its principles, each with the benefit or
the condition it protects?

Why: a principle tied to what it protects tells what breaks when it is not kept, so principles can
be weighed against each other; one tied to nothing is kept out of habit.

### B-6: What must always hold

For each feature, can the reader tell what must hold after every operation?

Why: read as a condition, it keeps holding when one place is changed; read as one step of a
procedure, it is lost when the procedure changes.

### B-7: Why this way

For each choice a maintainer might want to change, can the reader tell which other options were
weighed, why they were not chosen, and what the choice costs?

Why: without the reasons, a decision is either kept blindly or overturned without knowing what it
cost.

### B-8: What others rely on

For each thing someone outside the product relies on, can the reader tell who relies on it, what must
keep holding, and what may change?

What others rely on: commands and settings users type, what other programs call or read, and what
the product leaves in the user's environment.

Why: a change to it breaks those who rely on it, who are not there to object; the design document is
the one place that outlives a rebuild of the code.

### B-9: Attractive quality checked

For each benefit, can the reader tell in what situation it is tried, and what must happen to the
user for it to pass?

Why: a check in a situation the other ways handle as well passes without showing the benefit, and a
check of whether the output has the intended shape passes while the benefit is missed.

### B-10: One-dimensional quality measured

For each quality that is better the more of it there is, such as less time taken or fewer tokens
spent, can the reader tell how it is measured and what it is compared with?

Why: a quality not measured worsens without anyone noticing; measured against the version in use, a
change shows whether it made the product better or worse.

### B-11: Must-be quality checked

For each thing the user takes for granted, such as not losing work, can the reader tell which test
checks it?

Why: what a test can decide gives the same answer every time, and what the user takes for granted is
noticed only when it breaks.

### B-12: Backward compatibility checked

For each thing others rely on, can the reader tell which test shows it still works as earlier
versions left it?

Why: a break in backward compatibility shows first to the users who rely on it, after the release.

## Usability

### U-1: Few principles

Is each principle needed across more than one feature?

Why: few principles can be kept in mind and weighed against each other; a rule that concerns one
feature belongs with that feature, and listed among the principles adds one more thing to keep in
mind everywhere.

## Format

### F-1: Shape

Does the design document follow this template, headings included?

```markdown
# <Product name> design

<What this document covers, with a link to the README whose benefits it serves>

## Goals and non-goals

## Constraints

## Principles

## Features

### <Feature name>

<The README benefit it brings, how it is built, what must always hold, and the options weighed>

## Backward compatibility

## Verification

### Attractive quality

### One-dimensional quality

### Must-be quality

### Backward compatibility
```

- A section with nothing to hold keeps its heading and says `None:` and why, so a section thought
  through is told from a section forgotten.
- Verification comes last, since each check is read after what it checks; attractive quality comes
  first in it, since it shows whether the user would choose the product at all.

Why: a maintainer moving between products finds the same thing under the same heading in each, and
reads each section after what it rests on.
