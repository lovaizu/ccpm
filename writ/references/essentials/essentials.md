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
- An item's sentence is what the maker aims for. Its two lines are how the judge decides; in any use,
  exactly one of them holds.

## IDs

- An item's ID is its section's letter and a number: `B-2`. Across checklists, add the file:
  `release-notes.md B-2`.
- Never reuse an ID. A removed item leaves its number unused, and an item moved to another section
  gets a new number there. Then an ID always means the same item.

## Writing the items

- Find the items from the purpose, section by section. List the parts a deliverable of the kind
  usually has, and for each part ask what it does for the purpose in that section's sense: what the
  user gets from it, what makes that easy, what shape is relied on. Each answer is an item. A part
  that does nothing for the purpose gives no item.
- One item, one thing. When an item holds two, the one that fails hides behind the one that passes.
- Keep an item only if a bad deliverable fails it. Think of how deliverables of the kind usually go
  wrong: what they say is wrong, they say too little, they are written for someone else, or they
  come in a shape the user or a tool cannot take. An item such as "has an examples section" passes
  all of these, so drop it.
- Write the two lines as what the user did or got when using the deliverable, not as what the
  deliverable contains. Then any use shows which line holds.
- Leave out what [doc.md](doc.md), the checklist for every document, already covers.

## Testing the checklist

Try the checklist on two real deliverables of the kind: one that served its user and one that did
not. Have each used as its user would use it, and judge every item from what happened.

- Each item has exactly one of its two lines hold in each use.
- The deliverable that did not serve its user fails at least one item.

When an item breaks either, rewrite it from the purpose, not to fit that one use.

## Example

```markdown
# Release notes

Release notes let the product's user decide whether to upgrade to a version, and, once upgraded,
keep working without being caught out by what changed.

## Benefit

### B-1: What the upgrade requires

The notes let the user know beforehand what upgrading requires of them.

- Achieved: before upgrading, the user knew everything the version then required of them, including
  that it required nothing.
- Not achieved: before upgrading, the user did not know something the version then required of them.

### B-2: What the upgrade gives

The notes let the user weigh the upgrade against their own work.

- Achieved: the gains the user named for their own work were ones the version gave them once they
  upgraded.
- Not achieved: the user named a gain the version did not give them, or could name none.

## Usability

### U-1: What matters is found first

The notes let the user find what affects them without reading every entry.

- Achieved: the user reached the entries that affect their work without reading every entry.
- Not achieved: the user read every entry to find them, or did not find them.

## Format

### F-1: Each version in the same place

The notes let the user and their tools find a version's entries by its number.

- Achieved: the user or tool went to a version by its number and found that version's entries under
  it.
- Not achieved: the user or tool could not find a version's entries by its number, or found another
  version's.
```
