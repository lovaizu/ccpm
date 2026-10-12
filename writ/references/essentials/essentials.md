# Viewpoint files

A viewpoint file is written for one kind of work, such as research findings, a proposal, a design
document, code or tests, and serves two people:

- To whoever makes a work of the kind, it shows what the work needs to achieve its purpose.
- To whoever judges the work from what came of using it, it is the measure of whether the work
  achieved its purpose.

This file is for writing such a viewpoint file.

## What a viewpoint file holds

- A heading naming the kind.
- The purpose: what a work of the kind is for, as what its receiver can decide or do once they have
  used it, with the receiver named in general. A kind can have more than one receiver: code is run
  by its users and changed by those who keep it.
- The points, each one list item. Its sentence says what the work lets its receiver do; this is
  what the maker aims at. Under it, an indented paragraph says what, in what came of using the work,
  shows the point achieved, and what shows it not; this is what the judge decides by.

## Writing the points

- Work each point back from the purpose: ask what the receiver must get from the work to do what it
  is for, and make each such thing a point.
- Give each point one thing. A point that holds two hides the one that falls short behind the one
  that holds.
- Keep a point only if a work that misses its purpose fails it. Picture the usual ways a work of the
  kind fails: what it says is wrong, it says too little, or it is written for someone else. A point
  about a part being there, or how the work looks, passes all three.
- Write each paragraph in terms of what the receiver did, said or got in using the work, so that
  any use of any work of the kind shows whether the point was achieved.
- Leave out what [doc.md](doc.md) already holds for every document.

## Checking the file

Use a real work of the kind as its receiver would, and judge each point from what came of it. Where
a point cannot be judged from that, or a work known to fall short passes it, write the point again
from the purpose, not to fit that one use.

## Example

```markdown
# Release notes

Release notes let someone who uses the product decide whether to upgrade to a version, and, once
upgraded, go on working without being caught out by what changed.

- They let the reader tell what they must do differently once they upgrade.

    Achieved when what the reader said they must do is what the version asked of them when they
    upgraded and went on working, "nothing" included. Not achieved when they learned it only when
    something stopped them.

- They let the reader weigh the upgrade by their own work.

    Achieved when the reader named what the version changes in their own work and decided on that.
    Not achieved when they repeated the product's terms, or could not tell this version from any
    other.
```
