# Final check before merge (ccpm)

The user merges a change without reading it all again. They trust that only what they approved
reaches `main`, and that every point theirs to decide reaches them first.

- **Before you ask the user to merge, read the whole change against its purpose for three points:
  whether its parts contradict one another, whether anything in it is not needed for its purpose,
  and whether any of its work does nothing toward that purpose.**
  - Rationale: each part was checked on its own as it was made. What lies between parts shows only
    when someone reads the whole at once. The user should not have to read it all again to find it.
- **Judge each finding by the purpose, what the work should be and the approved architecture.
  Where what the user approved is wrong, or does not settle the point, decide it from the purpose
  and best practice. Tell the user the change with its grounds. Bring to the user only a point
  their intent leaves open.**
  - Rationale: by merging, the user stands behind what they approved. So tell them each change to
    it, and never slip one in. A point that what the work should be already settles costs the user
    a decision that gives them nothing to weigh.
- **Before a change to a best practice, a shared rule or a name merges, grep for every file that
  rests on it, outside `.git` and `.rn`. Read each changed sentence as its reader would. Change
  every file that rests on it in the same merge.**
  - Rationale: a source merged alone leaves the files that rest on it saying the old thing. A
    reader then meets both.
- **Before you ask for the merge, run what the final check fixed, as its user would.**
  - Rationale: an unchecked fix put in last undoes the checks made before it.
- **Open the report with whether the change can be merged. Give each fix one line, with its ground
  in the purpose or the architecture. Set apart what the user must decide.**
  - Rationale: the user checks the judgment, not only the result. They decide the merge from the
    report alone.
