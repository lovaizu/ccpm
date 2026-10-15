---
name: verification
version: 0.1.0
---

# Verification document

A verification document is read by whoever runs the product's checks again after a change, the
conductor at the Deliverable sign-off first, to see whether the product still gives what the user
chose it for and whether something that worked broke; and by the user at the Design sign-off, to
see how they will know the product works before anything is built. Each item of `doc.md` applies
to it with the product's checks as its subject. It is also the checklist the deliverable is used
against: each scene is an item, so a reader who uses the product as the scene says can tell
whether it passed.

## Format

### F-1: Shape

Does the verification document follow this template, headings and IDs included?

```markdown
---
name: verification
version: <x.y.z>
---

# <Product name> verification

<What to run these checks for, in one or two sentences>

## Where a run starts

<the state each run starts from, fixed>

## How a run goes

<how a run is carried through>

## Scenes

### A1: <the criterion as the plan words it>

- <what is put in: what the user says, knows, and decides>

  Passes when <what must happen>.

## Machine checks

| Command | Criteria |
|---|---|
| <the command as it is run> | <the IDs it checks> |
```

- The front matter names the document as a checklist, so turn uses the deliverable against it: each
  `### A1:` heading is an item, and the deliverable gives it when, doing as the scene says, what
  must happen happens.
- Every attractive criterion of the plan has a heading under Scenes, by its ID.

Why: rn's checks find each criterion's scene and machine check by this form, and the deliverable
is used against the same document the user approved.

## Benefit

### B-1: Each run starts the same

Can the reader set up where a run starts so that each run starts from the same state, without
reaching it by running what comes before?

Why: a check whose start differs from run to run passes or fails on the start, not on the product.

### B-2: How a run goes

Can the reader carry a run through, from its start to each scene's result, as the document says?

Why: a check carried through differently each time cannot show whether a change broke something.

### B-3: Each scene shows the user getting what they chose the product for

For each attractive criterion, can the reader tell from its scenes what the user does and what
must then happen for them to get that criterion, with the fewest scenes and inputs that show it?

Look for: a scene or an input that shows nothing another does not; a scene that covers an edge
case or a way the product could fail rather than the user getting what they chose it for.

Why: a pass then shows the user getting what they chose the work for, with the fewest checks, so
the time goes to raising it rather than to checking it; checks for every way a product could fail
never end, and their passing shows nothing more of why the user chose it.

### B-4: What passes is fixed before the work is seen

Can the reader tell, for each scene, what is put in and what must happen, as fixed before anything
was built?

Why: a pass chosen after the work is seen can be chosen so that the work passes.

### B-5: Every must-be criterion is checked somewhere

Can the reader find, for each must-be criterion, the machine check that judges it, or the scene
whose pass names it where no machine can?

Why: what the user takes for granted is noticed only when it breaks, and a criterion no check
covers breaks unseen.

### B-6: The machine checks run as written

Can the reader run each machine check as the document gives it, and tell which criteria it checks?

Why: a check that must be worked out before it runs is run less often, or not at all.

## Usability

None: each thing that makes a verification document quick to run is one its reader gets from it,
so its item is in Benefit.
