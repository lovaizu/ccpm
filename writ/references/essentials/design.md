# Design doc

The readers are builders and maintainers, who may be people or AI. When they finish, they know which features give the user the README's benefits and how each is built, can check that the user gets each benefit, and can explain whether a given change fits the design and, if not, why.

- Can a builder decide which way to go when unsure, by remembering just a few policies?

    A few policies let a builder weigh one against another and decide where cases differ. A rule that concerns only one feature belongs with that feature; among the policies it is one more thing to remember everywhere.

- Does each policy trace to a benefit in the README or to a condition the design cannot change?

    Traced to a benefit, or to a condition such as the environment the product is used in or the user, a policy tells the builder what breaks if it is not kept, so they can weigh it. A policy that traces to neither is kept by habit.

- Does every benefit in the README have the features that give it?

    With a feature for each benefit, the maintainer sees how the user actually gets it. A feature is what the product provides toward a benefit, such as having the work checked by someone who did not write it. A benefit no feature serves is missing its way.

- Does every feature, role, state and handoff trace to a benefit?

    Tracing each to a benefit, the maintainer knows what each is there for. One that traces to nothing can be taken away. Parts named after mechanisms, or a benefit followed straight by the mechanism, hide which part gives which benefit.

- Can a maintainer tell, for each feature, what a change to it would cost the user?

    Finding for each feature the benefit it serves, the step of use in the README where it works, and as much of how it is built as a change touches, the maintainer weighs a change by what the user would lose.

- Can a maintainer tell which conditions must hold after every operation?

    A condition read, at the decision it concerns, as holding after every operation tells the maintainer what must still hold when they change one part. Read as one step of a procedure, it is broken when the procedure changes.

- Does each benefit have a check that measures it as the user would feel it?

    Checking the benefit itself shows whether the user would choose the product at all. If the user should be able to approve from a summary without rereading the work, the check is whether a user who reads only the summary decides as they would after reading the work. A check that an artifact has the form meant to bring a benefit, or that a feature works as designed, passes while the benefit fails.

- Does each check run on a case where, without the benefit, the user would visibly lose out?

    On such a case, a pass shows the benefit is real. On a case where the alternative does as well, the check passes without testing anything.

- Do the pass criteria say what happens to the reader or the user?

    Criteria stated as what happens to the reader or the user let every builder check the same way and say the benefit is realized. Criteria stated as what the work contains are met while the user still loses out.

- Does the design say which cases were left unchecked, and why?

    Knowing what was not checked, the maintainer knows where a pass says nothing. An unstated gap is read as covered.

- Are the benefits checked before what the user takes for granted?

    Checking the benefits first puts the checking effort where it tells whether the user would choose the product. What the user takes for granted, such as nothing being lost, is easier to check and its failures easier to see; put first, those checks multiply and all pass while no one has checked a benefit.

- Is what the user takes for granted and a script can decide left to scripts?

    A script, such as one that checks a format holds or a link resolves, is faster and gives the same answer every time, so the builder's effort goes to the benefits.

- For each option a maintainer might switch to, is it said why it was not chosen?

    Seeing what a switch would lose and why the option was not chosen, a maintainer weighs a change against the decision already made. Without it, they undo the decision unaware of its cost. An option no maintainer would reasonably reach for needs no record.

- Does every sentence say something the reader cannot read from the README or the implementation?

    Every sentence then adds intent or a decision the maintainer would otherwise lack: take it away, and they would judge some change differently. Where a decision's reason is what the user gains, the design traces to the README stage that already says why it is good for the user, so the user's why stays in one place. A restated benefit, flow of use or reason a stage is good for the user drifts from the README.

- Does every sentence stay true when the implementation is rebuilt?

    Kept to what does not change with a rebuild, the design stays true across rebuilds. Settings, procedures, how the code is split, file and function names or internal data structures go stale with each one.

- Is the form of each external agreement written here?

    What later versions or people read from the user's environment is an external agreement; it is read from outside, so its form is part of the design. Kept here, in the one home that survives rebuilding the implementation, it shows the maintainer why each item exists, the conditions that always hold and what the form looks like, so they know which items may change without breaking a reader. The implementation carries no copy, since two copies drift apart. Handoffs between roles are not external agreements.
