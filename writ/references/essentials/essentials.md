# Checklists

A checklist is written for one kind of deliverable, such as research findings, a proposal, a design
document, code or tests. It is used twice:

- While a deliverable of that kind is made: it says what the deliverable needs to serve its purpose.
- After someone has used the deliverable: it is what you judge by, item by item, whether it served
  its purpose.

This file says how to write a checklist.

## Form

```markdown
# <Kind of deliverable>

<What the deliverable lets its user decide or do>

## Benefit

### B-1: <Item name>

<What the deliverable lets its user do>

- Achieved: <what you see when the user used it and it worked>
- Not achieved: <what you see when it did not>

## Usability

## Format
```

- Start with the purpose, and nothing else. Every item comes from it, and where an item does not
  settle a case, decide by the purpose. A kind can have more than one user: code is run by people
  and changed by those who maintain it.
- Every checklist has the same three sections, so none is skipped:
  - Benefit: what the user gets, the deliverable as it should be. That it is correct, and that
    whoever maintains it can change it, belong here.
  - Usability: what makes the benefit easy to get, such as speed, ease of use and effort.
  - Format: the shape the user or a tool relies on, such as what goes in and comes out, or a style
    shared with the user's other work.
- A section with no item says `None: <why this kind needs none>`. Then a section that was thought
  through and one that was forgotten can be told apart.
- An item's sentence is what the maker aims for. Its two lines are how the judge decides; exactly
  one of them holds.

## IDs

- An item's ID is its section's letter and a number: `B-2`. Across checklists, add the file:
  `release-notes.md B-2`.
- Never reuse an ID. A removed item leaves its number unused, and an item moved to another section
  gets a new number there. Then an ID always means the same item.

## Writing the items

- For each section, ask what the user needs from the deliverable to get its purpose, and make each
  answer an item.
- One item, one thing. When an item holds two, the one that fails hides behind the one that passes.
- Keep an item only if a bad deliverable fails it. Think of how deliverables of the kind usually go
  wrong: what they say is wrong, they say too little, they are written for someone else, or they
  come in a shape the user or a tool cannot take. An item such as "has an examples section" passes
  all of these, so drop it.
- Write the two lines as what the user did or got when using the deliverable, not as what the
  deliverable contains. Then any use shows which line holds.
- Leave out what [doc.md](doc.md), the checklist for every document, already covers.

## Testing the checklist

Have a real deliverable of the kind used as its user would use it, and judge each item from what
happened. When an item cannot be judged from that, or a deliverable you know is bad passes it,
rewrite the item from the purpose, not to fit that one use.

## Example

```markdown
# Release notes

Release notes let someone who uses the product decide whether to upgrade to a version, and, once
upgraded, keep working without being caught out by what changed.

## Benefit

### B-1: What the upgrade requires

The notes let the reader know what they must do differently after upgrading.

- Achieved: after upgrading and going back to work, the reader had already done what the version
  required, or knew it required nothing.
- Not achieved: something the version required stopped the reader before they knew of it.

### B-2: What the upgrade gives

The notes let the reader weigh the upgrade against their own work.

- Achieved: the reader named what the version changes in their own work, and decided on that.
- Not achieved: the reader repeated the product's wording, or could not tell this version from any
  other.

## Usability

### U-1: What matters is found first

The notes let the reader find what affects them without reading every entry.

- Achieved: the reader found the entries that affect their work before deciding.
- Not achieved: the reader decided before finding an entry that affects their work, or had to read
  every entry.

## Format

None: people read release notes, and no tool takes them in.
```
