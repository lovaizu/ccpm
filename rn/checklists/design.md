---
name: design
version: 0.3.0
---

# Design document

A design document is read by whoever builds or changes the product, to know what it must achieve,
how that is checked, what every change must keep, and who is responsible for what. Holding only
these, they implement it and secure its quality without hesitating, and decide every detail
themselves.

How the product is used is the README's; how each part behaves, with its steps, definitions,
settings and file names, is the code's, since these change with each rebuild while the design
holds. Each item of `doc.md` applies to a design document with what the product must achieve and
who brings it about as its subject; its B-16 is answered by the structure figure, since the order
things happen in is the README's to show. The reader comes from the README, so Goals and
Verification are said in its words, and each name of a part inside the product is first met in
the figure.

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

## Structure

<How the product divides into its parts and what joins them, in one sentence>

<One figure: a box for each one that takes part, holding its name alone; an arrow from each to
what it reads, writes, copies or calls, labelled with that relation>

<A table of the parts inside the product: what kind of thing each is, where it is kept, where it
runs>

## Principles
```

Why: a maintainer moving between products finds the same thing under the same heading in each, and
settles what is aimed at and how it is checked, neither of which depends on how the product is
built, before reading who brings it about and what every change must keep; and meets who takes
part before the principles that name them.

### F-2: A section thought through

Does each section with nothing to hold say, after `None:`, why it holds nothing?

Why: a section thought through is told from a section forgotten.

### F-3: Each quality checked under its heading

Does Verification check each quality under the heading it has in Goals?

Why: each quality is traced from what it is to how it is checked.

### F-5: Each principle names what it protects

Does each principle name, by the headings and names Goals gives them, the qualities or constraints
it protects?

Why: a quality is followed from Goals to the principles that keep it, and a principle that names
nothing, kept for nothing, shows.

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

For each thing someone outside the product relies on, can the reader tell who relies on it and what
must keep holding for them?

What others rely on: commands and settings users type, what other programs call or read, and what
the product leaves in the user's environment. What must keep holding is what each lets them do.

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

For each benefit, can the reader tell in what situation it is tried and what must happen to the
user for its check to pass?

Why: a check of whether the output has the intended shape passes while the benefit is missed, and a
check in a situation the other ways handle as well passes without showing the benefit.

### B-8: One-dimensional quality measured

For each one-dimensional quality, can the reader tell how it is measured and what the measure is
compared with?

Why: a quality not measured worsens without anyone noticing, and a measure compared with nothing
shows neither better nor worse.

### B-9: Must-be quality checked

For each must-be quality, can the reader tell how a test shows it holds, such as the case that
would break it?

Why: what a test can decide gives the same answer every time, and what the user takes for granted is
noticed only when it breaks.

### B-10: Backward compatibility checked

For each thing others rely on, can the reader tell how a test shows it still works as earlier
versions left it?

Why: a break in backward compatibility shows first to the users who rely on it, after the release.

### B-12: Who does what to what

Can the reader tell, for each one that takes part in the product's work, the user and what is
outside the product included, what it does and to what, from the figure's arrows alone?

Why: a maintainer changing one part needs to know every other its change can reach and what the
part rests on; pieced together from prose, or read out of sentences inside the boxes, it costs
effort and goes wrong, and a part left untold is reached without anyone seeing it.

### B-34: What kind of thing each part is

Can the reader tell, for each part inside the product, what kind of thing it is: a prompt an AI
follows, a script, a hook, data, or a person?

Why: a change is made differently to each kind, and the reader who cannot tell the kind cannot
tell what a change to the part costs or how it is checked.

### B-35: Where each part is kept

Can the reader tell, for each part inside the product, where it is kept: shipped with the product,
left in the user's repository, or held by a service such as GitHub?

Why: what is shipped changes with a release, what is left with the user outlives it and is theirs,
and what a service holds is reached only through it; a change that moves a part between these
changes who owns it.

### B-36: Where each part runs

Can the reader tell, for each part inside the product that runs, where it runs: on the user's
machine, in CI, or in both?

Why: what runs in both must give the same result in both, and a part that runs only in one has no
check in the other.

### B-33: Each goal brought about by a part

Can the reader tell, for each quality in Goals, which part or parts bring it about, from the
figure and the table alone?

Why: a quality no part brings about is promised and never built; a part that brings about none is
built for nothing; and the maintainer changing a part learns from this which qualities the change
can break.

### B-11: Principles to judge a change

Can the reader decide whether a change fits the design from its principles, because each is said as
what a change must keep, with the quality or the constraint it protects?

Why: without principles, a change can be held only against the code as it stands, where every
difference looks like a break; a principle tied to what it protects tells what breaks when it is
not kept, so principles can be weighed against each other, and one tied to nothing is kept out of
habit.

## Usability

### U-4: What others rely on, by what it gives them

Can the reader tell a name that must be kept from one the build may change, because the design gives
a name, a path or a value of what others rely on only where they rely on that very name?

Why: a name made a promise where others rely only on what it gives ties the design to the build,
and must be kept when the build would change it.

### U-2: Decisions told from details

Can the reader tell each decision that must hold from a detail that may change, because the
document holds nothing decided anew with each build, such as steps, full definitions, values,
settings and file names?

Where a part is kept and where it runs are decisions, since who owns the part and where a change
to it shows rest on them.

Why: such details change with each rebuild, so a design that holds them must be rewritten with the
code, and the reader can no longer tell a decision that must hold from a detail that may change.

### U-3: Each case left to the principles

Can the reader keep in mind only the principles and the responsibilities, because the document
writes down no case of how the product behaves that they already settle, and no way of bringing a
quality about that the builder could choose?

Why: builders work out each case and each way from the principles and the responsibilities; a case
or a way written down reads as one more rule to keep beside them, and must change with the
implementation though no decision did.

### U-1: Few principles

Can the reader keep every principle in mind, because each is one a change anywhere must keep?

Why: few principles can be kept in mind and weighed against each other; a rule that concerns one
part belongs with that part's code, and listed among the principles adds one more thing to keep in
mind everywhere.
