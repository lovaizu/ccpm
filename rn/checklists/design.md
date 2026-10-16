---
name: design
version: 0.3.0
---

# Design document

A design document is read by whoever builds or changes the product, to know the least that must
hold for the product to keep what its README promises: the goals, the design decisions toward
them, the structure that places them, and how each goal is verified. Each section is the ground of
the next step of the work, judged yes or no, and covers the one before it, so the builder builds
and changes the product without hesitating and decides everything else themselves.

The design stands between the README and the code: how the product is used is the README's, and
how each part works, with its steps, definitions, settings and file names, is the code's, since
these change with each rebuild while the design holds. Each item of `doc.md` applies to a design
document with what the product must achieve and which part holds it as its subject; its B-16 is
answered by the structure figure, since the order things happen in is the README's to show. The
reader comes from the README, so Goals and Verification are said in its words. Verification holds
the criterion and the method for each goal; the scenes are the verification document's and the
cases the tests'.

## Format

### F-1: Shape

Does the design document follow this template, headings included?

```markdown
# <Product name> design

<The design's main point, with a link to the README whose promises it keeps>

## Goals

### Attractive quality

- <What the README's use needs, in one sentence>

### One-dimensional quality

### Must-be quality

### Backward compatibility

## Design decisions

- <What must hold toward the goals, in one sentence>

  <Its intent: the goals it serves, by their names in Goals, and what a builder working from the
  goals alone could get wrong>

## Structure

<One static figure: a box for each part, the user and what is outside the product included,
holding its name alone; an arrow from each to what it reads, writes or calls, labelled with that
relation>

<A table of the parts inside the product: what kind of thing each is, where it is kept, where it
runs>

- <A part, and the goal or decision a mechanism inside it holds, in one sentence>

## Verification

### Attractive quality

- <The criterion that shows a goal reached, naming the goal, in one sentence>

  <How it is checked, and where the check is>

### One-dimensional quality

### Must-be quality

### Backward compatibility
```

Each list follows `doc.md`'s F-1: one sentence an item, its explanation indented under it.

Why: a builder moving between products finds the same thing under the same heading in each; each
section is read against the one before, so it comes after it; and one sentence an item keeps each
goal, decision and criterion short enough to judge at once.

### F-2: A section thought through

Does each section with nothing to hold say, after `None:`, why it holds nothing?

Why: a section thought through is told from a section forgotten.

### F-3: Each quality verified under its heading

Does Verification check each goal under the heading it has in Goals, naming it as Goals does?

Why: each goal is followed from what it is to how it is verified.

### F-5: Each decision names its goals

Does each decision's intent name the goals it serves as Goals names them?

Why: a goal is followed from Goals to the decisions that keep it.

## Benefit

### B-1: Attractive quality

Can the reader tell which benefits, of those the README promises, the product must bring the user?

Why: the benefits are why the user chooses the product, and every other part of the design serves
them or keeps them safe.

### B-2: One-dimensional quality

Can the reader tell which qualities are better the more of them there is, such as less time taken
or fewer tokens spent?

Why: such a quality is weighed against the others in every choice, and one left unnamed is given up
without anyone deciding to.

### B-3: Must-be quality

Can the reader tell what the user takes for granted, such as not losing work?

Why: the user does not ask for it and notices it only when it breaks, and the README's use does not
show it, so a design that does not name it is free to break it.

### B-4: Backward compatibility

For each thing someone outside the product relies on, can the reader tell who relies on it and what
must keep holding for them?

What others rely on: commands and settings users type, what other programs call or read, and what
the product leaves in the user's environment. What must keep holding is what each lets them do.

Why: a change to it breaks those who rely on it, who are not there to object; the design document is
the one place that outlives a rebuild of the code.

### B-17: The README's use covered

For each thing the README's use needs from the product, can the reader find the goal that holds it?

Why: a promise of the README no goal holds is not designed for, and is met by chance or not at all.

### B-18: Each goal judged

Can the reader say of the product, for each goal, whether it meets it, yes or no?

Why: the goals are the ground of every decision; one that cannot be judged met or not settles
nothing, and every decision drawn from it can be argued either way.

### B-11: Decisions to judge a change

Can the reader say of any change, for each decision, whether it keeps it or breaks it, yes or no?

Why: without decisions so said, a change can be held only against the code as it stands, where every
difference looks like a break, or against a slogan, which any change can be said to keep.

### B-19: Every goal served by a decision

For each goal, can the reader find the decisions that serve it?

Why: a goal no decision serves is left to how each builder reads it, and two builders bring it about
in two ways that do not fit together.

### B-20: Each decision needed

Can the reader tell, for each decision, what a builder working from the goals alone could get
wrong, and which goal that would lose?

A thing any builder would do anyway, such as reading the files a step needs, fails: no goal is lost
by leaving it out.

Why: a decision that serves no goal, or that no builder would break, is read and kept like the
others, and takes the attention the real ones need.

### B-5: Non-goals

Can the reader tell, among the decisions, what the design could have aimed at but leaves out on
purpose?

Why: without the non-goals, a builder takes up what was left out on purpose as a gap to fill.

### B-6: Constraints

Can the reader tell, among the decisions, which conditions the design takes as given, such as where
the product runs and who uses it?

Why: a change weighed without them turns the design into one that cannot run where it must.

### B-12: Who does what to what

Can the reader tell, for each part that takes part in the product's work, the user and what is
outside the product included, what it does and to what, from the figure's arrows alone?

Why: a builder changing one part needs to know every other its change can reach and what the part
rests on; pieced together from prose, or read out of sentences inside the boxes, it costs effort and
goes wrong, and a part left untold is reached without anyone seeing it.

### B-34: What kind of thing each part is

Can the reader tell, for each part inside the product, what kind of thing it is: a prompt an AI
follows, a script, a hook, data, or a person?

Why: a change is made differently to each kind, and the reader who cannot tell the kind cannot tell
what a change to the part costs or how it is checked.

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

### B-33: Every goal and decision placed

Can the reader tell, for each goal and each decision, which parts hold it: from the figure where
the placement itself holds it, and from an item under the figure, naming the part, where a
mechanism inside one part holds it?

What the part holds is said, not how it does it; how is the code's.

Why: a goal or decision no part holds is promised and never built, and the builder changing a part
learns from this what the change can break.

### B-21: Each part needed

Can the reader tell, for each part, which goal or decision it holds?

Why: a part that holds none is built and kept for nothing, and the builder cannot tell whether it
may go.

### B-7: Attractive quality verified

For each attractive goal, can the reader tell the criterion that shows it reached, judged by using
the product in the user's place, and where that check is?

The scenes themselves, what is put in and what must then happen to the user, are the verification
document's.

Why: a check of whether the output has the intended shape passes while the benefit is missed; and a
scene written into the design must change with the product though no decision did.

### B-8: One-dimensional quality verified

For each one-dimensional goal, can the reader tell what is measured, from what, and what it is
compared with?

Why: a quality not measured worsens without anyone noticing, and a measure compared with nothing
shows neither better nor worse.

### B-9: Must-be quality verified

For each must-be goal, can the reader tell the test that checks it, on which part, and where the
tests are?

The case each test tries, such as the one that would break the quality, is the test's.

Why: what a test can decide gives the same answer every time, and what the user takes for granted is
noticed only when it breaks.

### B-10: Backward compatibility verified

For each thing others rely on, can the reader tell the test that checks it still works as earlier
versions left it, against which versions, and where the tests are?

Why: a break in backward compatibility shows first to the users who rely on it, after the release.

### B-22: Each criterion judged

Can the reader say, for each criterion, whether the product passes it, yes or no?

Why: a criterion that cannot be judged passed or failed verifies nothing, and the goal it stands for
is taken as met because no one can show it is not.

## Usability

### U-4: What others rely on, by what it gives them

Can the reader tell a name that must be kept from one the build may change, because the design
gives a name, a path or a value of what others rely on only where they rely on that very name?

Why: a name made a promise where others rely only on what it gives ties the design to the build, and
must be kept when the build would change it.

### U-2: Decisions told from details

Can the reader tell each decision that must hold from a detail that may change, because the
document holds nothing decided anew with each build, such as steps, full definitions, values,
settings and file names?

Where a part is kept and where it runs are decisions, since who owns the part and where a change to
it shows rest on them.

Why: such details change with each rebuild, so a design that holds them must be rewritten with the
code, and the reader can no longer tell a decision that must hold from a detail that may change.

### U-3: Each case left to the decisions

Can the reader keep in mind only the decisions and the structure, because the document writes down
no case of how the product behaves that they already settle, and no way of bringing a goal about
that the builder could choose?

Why: builders work out each case and each way from the decisions and the structure; a case or a way
written down reads as one more rule to keep beside them, and must change with the code though no
decision did.

### U-1: Few decisions

Can the reader keep every decision in mind, because each is one a change anywhere must keep?

Why: few decisions can be kept in mind and weighed against each other; a rule that concerns one part
belongs with that part's code, and listed among the decisions adds one more thing to keep in mind
everywhere.
