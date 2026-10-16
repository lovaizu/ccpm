---
name: design
version: 0.3.0
---

# Design document

A design document is read by whoever builds or changes the product, to know the least, core and
unchanging, that holds the product to what its README promises: where each responsibility is
placed, logically and physically, and how each promise is verified. With it, they build and change
the product without hesitating and decide everything else themselves.

The design stands between the README and the code: without it, the code would answer to the README
alone and nothing would hold it. How the product is used is the README's, and how each part works,
with its steps, definitions, settings and file names, is the code's, since these change with each
rebuild while the design holds. Each item of `doc.md` applies to a design document with what the
product must achieve and which part holds it as its subject; its B-16 is answered by the logical
figure, since the order things happen in is the README's to show. The reader comes from the README,
so the criteria name its promises in its words; the scenes of each check are the verification
document's and the cases the tests'.

## Format

### F-1: Shape

Does the design document follow this template, headings included?

```markdown
# <Product name> design

<The one idea by which the product keeps its README's promises, with a link to the README>

## Structure

### Logical structure

<One static figure: a box for each part, the user and what is outside the product included,
holding its name alone; an arrow from each to what it reads, writes or calls, labelled with that
relation>

- <A part, and the promise a mechanism inside it holds, by the promise's name, in one sentence>

### Physical structure

<One static figure: a frame for each place things are kept or run, such as what is shipped, the
user's repository, a service or the user's machine, holding the place's name alone; in each, a box
for each unit kept there, holding its kind and the logical parts it makes alone; an arrow from each
to what it depends on, labelled with that relation>

## Verification

### Attractive quality

- <The promise's name>: <the criterion that shows it kept, in one sentence>
  - <How it is checked, and where the check is, in one sentence>

### One-dimensional quality

### Must-be quality

### Backward compatibility
```

Why: a builder moving between products finds the same thing under the same heading in each; the
logical structure places each responsibility and the physical where each lives, which are not one
to one; the figures and the criteria each say what the other does not, so nothing is said twice;
and one sentence an item keeps each short enough to judge at once.

### F-2: A section thought through

Does each section with nothing to hold say, after `None:`, why it holds nothing?

Why: a section thought through is told from a section forgotten.

### F-3: Each criterion named

Does each criterion open with the name of the promise it verifies, then a colon?

Why: an item under the logical figure names the promise it places, and the builder follows it to
the criterion by that name.

## Benefit

### B-37: The idea that holds the promises

Can the reader tell from the opening the one idea by which the product keeps its README's promises?

Why: the builder meets cases the design does not name, and decides each the way the product keeps
its promises only when they hold that idea.

### B-12: Who does what to what

Can the reader tell, for each part that takes part in the product's work, the user and what is
outside the product included, what it does and to what, from the logical figure's arrows alone?

Why: a builder changing one part needs to know every other its change can reach and what the part
rests on; pieced together from prose, or read out of sentences inside the boxes, it costs effort and
goes wrong, and a part left untold is reached without anyone seeing it.

### B-38: Every promise placed

Can the reader tell, for each promise the criteria name, which parts hold it: from the figures
where the placement itself holds it, and from an item under the logical figure, naming the part,
where a mechanism inside one part holds it?

What the part holds is said, not how it does it; how is the code's.

Why: a promise no part holds is never built, and the builder changing a part learns from this what
the change can break.

### B-26: What kind of thing each unit is

Can the reader tell from the physical figure what kind of thing each unit is: a prompt an AI
follows, a script, a hook, or data?

Why: a change is made differently to each kind, and the reader who cannot tell the kind cannot tell
what a change to the unit costs or how it is checked.

### B-23: Where each part is kept

Can the reader tell from the physical figure, for each logical part, the units that make it and
where each is kept: shipped with the product, left in the user's repository, or held by a service
such as GitHub?

Why: one logical part may be made of units kept in several places; what is shipped changes with a
release, what is left with the user outlives it and is theirs, and what a service holds is reached
only through it, so a builder who moves a unit between them changes who owns it.

### B-24: Where each part runs

Can the reader tell from the physical figure, for each unit that runs, where it runs: on the user's
machine, in CI, or in both?

Why: what runs in both must give the same result in both, and a unit that runs only in one has no
check in the other.

### B-25: What the product depends on

Can the reader tell from the physical figure's arrows what each unit depends on outside the
product, such as another plugin, a tool on the user's machine or a service?

Why: what the product needs to be in place is where it breaks for the user first, and a dependency
no figure shows is added or dropped without anyone deciding to.

### B-17: Every promise of the README verified

For each benefit the README promises, can the reader find the attractive criterion that names it in
the README's words?

Why: a promise no criterion verifies is not designed for, and is met by chance or not at all.

### B-2: One-dimensional quality

Can the reader tell from the one-dimensional criteria which qualities are better the more of them
there is, such as less time taken or fewer tokens spent?

Why: such a quality is weighed against the others in every choice, and one left unnamed is given up
without anyone deciding to.

### B-3: Must-be quality

Can the reader tell from the must-be criteria what the user takes for granted, such as not losing
work?

Why: the user does not ask for it and notices it only when it breaks, and the README's use does not
show it, so a design that does not name it is free to break it.

### B-4: Backward compatibility

For each thing someone outside the product relies on, can the reader tell from the backward
compatibility criteria who relies on it and what must keep holding for them?

What others rely on: commands and settings users type, what other programs call or read, and what
the product leaves in the user's environment. What must keep holding is what each lets them do.

Why: a change to it breaks those who rely on it, who are not there to object; the design document is
the one place that outlives a rebuild of the code.

### B-7: Attractive quality verified

For each attractive criterion, can the reader tell how it is judged by using the product in the
user's place, and where that check is?

The scenes themselves, what is put in and what must then happen to the user, are the verification
document's.

Why: a check of whether the output has the intended shape passes while the benefit is missed; and a
scene written into the design must change with the product though the design did not.

### B-8: One-dimensional quality verified

For each one-dimensional criterion, can the reader tell what is measured, from what, and what it is
compared with?

Why: a quality not measured worsens without anyone noticing, and a measure compared with nothing
shows neither better nor worse.

### B-9: Must-be quality verified

For each must-be criterion, can the reader tell the test that checks it, on which part, and where
the tests are?

The case each test tries, such as the one that would break the quality, is the test's.

Why: what a test can decide gives the same answer every time, and what the user takes for granted is
noticed only when it breaks.

### B-10: Backward compatibility verified

For each backward compatibility criterion, can the reader tell the test that checks it still works
as earlier versions left it, against which versions, and where the tests are?

Why: a break in backward compatibility shows first to the users who rely on it, after the release.

### B-22: Each criterion judged

Can the reader say, for each criterion, whether the product passes it, yes or no?

Why: a criterion that cannot be judged passed or failed verifies nothing, and the promise it stands
for is taken as kept because no one can show it is not.

### B-21: Each part needed

Can the reader tell, for each part in the figures, which promise it holds?

Why: a part that holds none is built and kept for nothing, and the builder cannot tell whether it
may go.

### B-39: Each criterion needed

Can the reader tell, for each criterion, the promise of the README, the thing the user takes for
granted or the thing others rely on that it verifies?

Why: a criterion that verifies none of these holds the product to something no one asked of it, and
is kept at the cost of every change.

## Usability

### U-4: What others rely on, by what it gives them

Can the reader tell a name that must be kept from one the build may change, because the design
gives a name, a path or a value of what others rely on only where they rely on that very name?

Why: a name made a promise where others rely only on what it gives ties the design to the build, and
must be kept when the build would change it.

### U-2: The design told from details

Can the reader tell what must hold from a detail that may change, because the document holds
nothing decided anew with each build, such as steps, full definitions, values, settings and file
names?

Where a part is kept and where it runs are the design's, since who owns the part and where a change
to it shows rest on them.

Why: such details change with each rebuild, so a design that holds them must be rewritten with the
code, and the reader can no longer tell what must hold from what may change.

### U-3: Each case left to the builder

Can the reader keep in mind only the figures and the criteria, because the document writes down no
case of how the product behaves and no way of keeping a promise that the builder could choose?

Why: builders work out each case and each way from the figures and the criteria; a case or a way
written down reads as one more rule to keep beside them, and must change with the code though the
design did not.

### U-1: The whole design kept in mind

Can the reader keep the whole design in mind at once, because it holds no part, arrow, item or
criterion that a change anywhere need not keep?

Why: what can be kept in mind at once is weighed as a whole in every change; a rule that concerns
one part belongs with that part's code, and set in the design adds one more thing to keep in mind
everywhere.
