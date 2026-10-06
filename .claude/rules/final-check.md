# Final check before merge (ccpm)

The user merges a change without reading it all again, sure that only what they approved reaches
`main`, and every point that is theirs to decide reaches them first.

- **Before asking the user to merge, read the whole change against its purpose for three points:
  whether its parts contradict one another, whether anything in it is not needed for its purpose,
  and whether any of its work does nothing toward that purpose.**
  - Rationale: each part was checked on its own as it was made; what lies between parts shows only
    when the whole is read at once, and the user should not have to read it all again to find it.
- **Judge each finding by what the user approved, the purpose and the approved design, and make no
  fix that changes what was approved. Where what was approved is wrong, or does not settle the
  point, bring it to the user.**
  - Rationale: merging is the user standing behind what they approved. Bending the design to the
    code, or correcting it on the assistant's own judgment, would have the user approve a choice they
    never saw.
- **Run what the final check fixed, as its user would, before asking for the merge.**
  - Rationale: an unchecked fix put in last undoes the checks made before it.
- **Open the report with whether the change can be merged, give each fix one line with its ground
  in the purpose or the design, and set apart what the user must decide.**
  - Rationale: the user checks the judgment, not only the result, and decides the merge from the
    report alone.
