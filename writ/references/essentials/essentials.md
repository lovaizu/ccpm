# Viewpoint files

A viewpoint file is written for one kind of work, such as research findings, a proposal, a design
document, code or tests, and serves two people:

- To whoever makes a work of the kind, it shows what the work needs to achieve its purpose.
- To whoever judges the work from what came of using it, it is the measure of whether the work
  achieved its purpose.

This file is for writing such a viewpoint file.

## The form

```markdown
# <KIND>: <Kind>

<What a work of the kind lets its receiver decide or do, with the receiver named in general>

## PUR: The purpose itself

### <KIND>-PUR-1: <Point name>

<What the work lets its receiver do>

- Achieved: <what, in what came of using the work, shows it achieved>
- Not achieved: <what shows it not>

## COR: Correctness

## SUP: What supports it

## CHG: Those who change it later

## IO: What it takes in and hands on
```

- The opening holds the purpose and nothing else. Every point is worked back from it, and where a
  point's words do not reach, the maker and the judge decide by it. A kind can have more than one
  receiver: code is run by its users and changed by those who keep it.
- Every file has the same five sides, so the points are always looked for, talked over and judged
  from all five:
  - PUR, the purpose itself: the receiver can do what the work is for.
  - COR, correctness: what the work says or does is right, so the receiver can rely on it.
  - SUP, what supports it: speed, ease of use, the receiver's effort.
  - CHG, those who change it later: whoever keeps or takes over the work can change it.
  - IO, what it takes in and hands on: the form the next reader, person or tool, relies on.
- A side with no point holds `None: <why a work of the kind needs none here>`. Left empty, a side
  thought through and a side forgotten look the same.
- A point's sentence is what the maker aims at; its two lines are what the judge decides by, as one
  of the two.

## IDs

- The kind has a short ID of capital letters, unique among viewpoint files, such as `REL` for
  release notes. With it, a point's ID is unique wherever several files are used together.
- A point's ID is the kind's, the side's and a number counted up within the side:
  `REL-COR-2`.
- An ID is never used again. A point taken out leaves its number unused; a point moved to another
  side has changed its meaning, and takes a new number there. So a record that names an ID always
  means the same point.

## Writing the points

- Work each point back from the purpose: for each side, ask what the receiver must get from the
  work to do what it is for, and make each such thing a point.
- Give each point one thing. A point that holds two hides the one that falls short behind the one
  that holds.
- Keep a point only if a work that misses its purpose fails it. Picture the usual ways a work of the
  kind fails: what it says is wrong, it says too little, or it is written for someone else. A point
  about a part being there, or how the work looks, passes all three; style is left to a checker.
- Write the two lines in terms of what the receiver did, said or got in using the work, so that any
  use of any work of the kind shows which one holds.
- Leave out what [doc.md](doc.md) already holds for every document.

## Checking the file

Use a real work of the kind as its receiver would, and judge each point from what came of it. Where
a point cannot be judged from that, or a work known to fall short passes it, write the point again
from the purpose, not to fit that one use.

## Example

```markdown
# REL: Release notes

Release notes let someone who uses the product decide whether to upgrade to a version, and, once
upgraded, go on working without being caught out by what changed.

## PUR: The purpose itself

### REL-PUR-1: What the upgrade asks

The notes let the reader tell what they must do differently once they upgrade.

- Achieved: what the reader said they must do is what the version asked of them when they upgraded
  and went on working, "nothing" included.
- Not achieved: the reader learned what it asked of them only when something stopped them.

### REL-PUR-2: What the upgrade gives

The notes let the reader weigh the upgrade by their own work.

- Achieved: the reader named what the version changes in their own work, and decided on that.
- Not achieved: the reader repeated the product's terms, or could not tell this version from any
  other.

## COR: Correctness

### REL-COR-1: Each change as it is

The notes let the reader rely on what each change is said to be.

- Achieved: each change the reader acted on behaved as the notes said.
- Not achieved: a change behaved otherwise than the notes said, or a change the reader met was not
  in them.

## SUP: What supports it

### REL-SUP-1: What matters found first

The notes let the reader find what concerns them without reading every entry.

- Achieved: the reader reached the entries that changed their own work before deciding.
- Not achieved: the reader decided before reaching an entry that changed their work, or read every
  entry to find it.

## CHG: Those who change it later

None: release notes are written once for a version and not changed afterwards.

## IO: What it takes in and hands on

None: the reader is a person, and no tool reads the notes.
```
