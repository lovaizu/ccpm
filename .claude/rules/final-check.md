# Final check before a merge in ccpm

The user merges a change without reading it all again. They trust that only what they approved
reaches `main`, and that every point theirs to decide reaches them first.

- **Before you ask the user to merge, read the whole change against its purpose for three points:
  whether its parts contradict one another, whether any part goes beyond what the purpose needs,
  and whether any of its work does nothing toward the purpose.**
  - Rationale: the maker checked each part on its own as they made it. What lies between the parts
    shows only when someone reads the whole at once. The user shouldn't have to read it all again
    to find it.
- **Judge each finding by the purpose, what the work should be, and the approved architecture.
  What the user approved may be wrong, or may leave a point open. Decide such a point by the
  purpose and the best practice. Tell the user the change and its grounds. Bring to the user only a point that
  their intent leaves open.**
  - Rationale: by merging, the user stands behind what they approved. So tell them each change to
    it, and never slip one in. When what the work should be already settles a point, asking the
    user about it spends their time on a decision with nothing for them to weigh.
- **Before a change to a best practice, a shared rule, or a name merges, grep for every file that
  rests on it, outside `.git` and `.rn`. Read each changed sentence as its reader would. Change
  every file that rests on it in the same merge.**
  - Rationale: a source merged alone leaves the files that rest on it saying the old thing. A
    reader then meets both.
- **Before you ask for the merge, run what the final check fixed, as its user would.**
  - Rationale: an unchecked fix put in last undoes the checks made before it.
- **Open the report with whether the change is ready to merge. Give each fix one line, with its
  ground in the purpose or the architecture. Set apart what the user must decide.**
  - Rationale: the user checks the judgment, not only the result. They decide the merge from the
    report alone.
