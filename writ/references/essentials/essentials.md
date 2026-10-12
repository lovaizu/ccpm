# Checklist

A checklist is written for one kind of deliverable, such as research findings, a proposal, a design
document, code or tests. It lets whoever makes a deliverable of the kind know what it needs to serve
its purpose, and lets whoever judges it, after someone has used it, decide whether it did.

## Benefit

### B-1: Cases decided by the purpose

The checklist lets the maker and the judge decide a case no item settles.

- Achieved: where no item settled a case, the maker or the judge decided it by the purpose the
  checklist opens with.
- Not achieved: where no item settled a case, they guessed, or decided against the purpose.

### B-2: What the deliverable needs

The checklist lets the maker know everything the deliverable needs to serve its user.

- Achieved: each way the deliverable fell short for its user was one an item asks about.
- Not achieved: the deliverable fell short for its user in a way no item asks about.

### B-3: Good told from bad

The checklist lets the judge tell a deliverable that served its user from one that did not.

- Achieved: a deliverable that served its user was Achieved on every item, and one that did not was
  Not achieved on at least one.
- Not achieved: a deliverable that did not serve its user passed every item, or one that did failed
  an item.

### B-4: One verdict per item

The checklist lets the judge settle every item from what happened when the deliverable was used.

- Achieved: for every item, exactly one of its two lines held.
- Not achieved: for some item, both lines held, or neither did.

## Usability

### U-1: What to change, from the item alone

The checklist lets the maker know what to change when an item is Not achieved.

- Achieved: from the item alone, the maker knew which one thing fell short.
- Not achieved: the maker had to work out which of the things the item held fell short.

### U-2: No item repeats another

The checklist lets the maker and the judge spend their attention only on items that settle
something.

- Achieved: each item's verdict told something no other item's did, in this checklist or in
  [doc.md](doc.md), the checklist for every document.
- Not achieved: two items came out the same in every use, because they ask the same thing.

## Format

### F-1: The same shape in every checklist

The checklist lets a tool read it the way it reads every other checklist.

- Achieved: a tool read the purpose, then `## Benefit`, `## Usability` and `## Format` in that
  order. Each held `None: <why>`, or items: a `### <B, U or F>-<number>: <name>` heading, a
  sentence, and the `- Achieved:` and `- Not achieved:` lines.
- Not achieved: the tool could not read one of these.

### F-2: IDs that keep their meaning

The checklist lets anything that names an item by its ID, such as a judgment kept from an earlier
use, keep pointing at that item.

- Achieved: every ID named earlier still meant the same item; a removed item left its number
  unused, and an item moved to another section took a new number there.
- Not achieved: an ID named earlier now means another item, or none.

### F-3: Sections left empty on purpose

The checklist lets the judge tell a section thought through from one forgotten.

- Achieved: every section with no item held `None:` with a reason the judge could check.
- Not achieved: a section was empty, or its `None:` gave no reason.
