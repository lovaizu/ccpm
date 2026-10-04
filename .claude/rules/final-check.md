# Final check before merge (ccpm)

How a change is checked once more before the user is asked to merge it, whatever the change is.

- **Before asking the user to merge, read the whole change against three points: whether its files
  contradict one another, whether anything in it is not needed for its purpose, and whether any of
  its work does nothing toward that purpose.**
  - Rationale: each part was checked on its own as it was made, and what lies between parts shows
    only when the whole is read at once, before it reaches users.
- **Judge each finding from the purpose and the approved design, never from the implementation.
  Where the design and the code disagree, decide from the purpose which is right, and bring it to
  the user when the design does not settle it; never rewrite the design to fit the code.**
  - Rationale: the design is what the user approved and the code is derived from it; bending the
    design to the code turns a choice no one reviewed into an approved one.
