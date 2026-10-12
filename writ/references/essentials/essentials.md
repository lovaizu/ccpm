# Checklist

A checklist says what a deliverable of one kind, such as research findings, a proposal, a design
document, code or tests, must be to serve its purpose, as questions answered yes or no. Whoever makes
a deliverable of the kind reads it before making it, and whoever judges the deliverable answers it.
This file is the checklist for checklists, and is written in the shape it asks for.

## Benefit

### B-1: User and purpose

Does the opening say who uses a deliverable of the kind, and what it lets them decide or do,
concretely enough to picture?

Why: every item is judged against the user and the purpose; without them, no item can be answered.

### B-2: Usual failures caught

For each usual way a deliverable of the kind fails its user, does some item answer no?

- What it says is wrong.
- It says too little.
- It is written for someone else.
- It comes in a shape its user or their tool cannot take.

Why: a failure no item catches lets a deliverable that misses its purpose pass.

## Usability

### U-1: One thing per item

Does each item check one thing only?

Why: when an item checks two things, the one that falls short hides behind the one that holds.

### U-2: Same answer from anyone

Can each item be answered yes or no, with the same answer whoever answers it?

Why: when the answer depends on who judges, the maker cannot tell what passes, and judgments of the
same deliverable differ.

### U-3: What the user gets, not what is there

Does each Benefit and Usability item ask whether the user gets something from the deliverable,
rather than whether something is in it?

Why: an item about what is there passes a deliverable its user cannot use, and fails a good one that
does without that part.

### U-4: Each item in its section

Does each item sit in the section these questions put it in?

Ask of each item, in this order, and stop at the first yes:

1. Does it ask for a set shape that a person or a tool relies on? Format.
2. Without it, does the user lose what they get from the deliverable? Benefit.
3. Otherwise: Usability.

Why: with every item where the questions put it, anyone finds it where they look, and each section
holds what its name says.

## Format

### F-1: Shape

Does the checklist follow this template, IDs included?

```markdown
# <Kind of deliverable>

<Who uses it, and what it lets them decide or do>

## Benefit

### B-1: <Item name>

<Question answered yes or no>

<Only what the question needs to be answered, such as a list or a template; most need nothing>

Why: <what goes wrong without it>

## Usability

None: <why the kind needs no item here>

## Format
```

- Every checklist has the three sections, in this order. A section with no item holds `None:` and
  its reason, so a section thought through is told from a section forgotten.
- An item's ID is its section's first letter and a number counted up within the section, such as
  `U-2`; across checklists it goes with the file, such as `release-notes.md U-2`.
- An ID is never used again. A removed item leaves its number unused, and an item moved to another
  section takes a new number there, so an ID named earlier always means the same item.

Why: every checklist in the same shape keeps their quality even, and lets a tool read any of them.
