# Final check before merge (ccpm)

The user merges a change without reading it all again, sure that only what they approved reaches
`main`, and every point that is theirs to decide reaches them first.

- **Before asking the user to merge, read the whole change against its purpose for three points:
  whether its parts contradict one another, whether anything in it is not needed for its purpose,
  and whether any of its work does nothing toward that purpose.**
  - Rationale: each part was checked on its own as it was made; what lies between parts shows only
    when the whole is read at once, and the user should not have to read it all again to find it.
- **Judge each finding by the purpose, what the work should be and the approved architecture.
  Where what was approved is wrong, or does not settle the point, decide it from the purpose and
  best practice, and tell the user the change with its grounds. Bring to the user only a point
  their intent leaves open.**
  - Rationale: merging is the user standing behind what they approved, so a change to it is told,
    never slipped in; and a point that what it should be settles costs the user a decision that
    gives them nothing to weigh.
- **Before a change to a best practice, a shared rule or a name merges, find by grep every file
  that rests on it, outside `.git` and `.rn`, read each changed sentence as its reader would, and
  change every file that rests on it in the same merge.**
  - Rationale: a source merged alone leaves its dependents saying the old thing, and a reader
    meets both.
- **Run what the final check fixed, as its user would, before asking for the merge.**
  - Rationale: an unchecked fix put in last undoes the checks made before it.
- **Open the report with whether the change can be merged, give each fix one line with its ground
  in the purpose or the architecture, and set apart what the user must decide.**
  - Rationale: the user checks the judgment, not only the result, and decides the merge from the
    report alone.
