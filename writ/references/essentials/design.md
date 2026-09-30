# Design doc

The readers are builders and maintainers, who may be people or AI. When they finish, they know which features give the user the README's benefits and how each is built, and can explain whether a given change fits the design and, if not, why.

- Can a builder decide which way to go when unsure, by remembering just a few policies?

    A few policies, each with what breaks if it is not kept, traced to a benefit in the README or to a condition the design cannot change, such as the environment the product is used in or the user, let a builder weigh one against another and decide where cases differ. A rule that concerns only one feature belongs with that feature; among the policies it is one more thing to remember everywhere.

- Can a maintainer follow each benefit in the README to the features that give it and the part that builds each, and so tell what a change costs the user?

    A maintainer who can trace each benefit to its features and to the part that builds each sees what a change costs the user. A feature is what the product provides toward one of the README's benefits, such as a checker that did not make the work checking it. Every feature, role, state and handoff traces to a benefit: one that traces to nothing can be taken away, and a benefit no feature serves is missing its way. For each feature, the maintainer finds the benefit it serves, the step of use in the README where it works, and as much of how it is built as they need to tell what a change to it would cost the user. Parts named after mechanisms, or a benefit followed straight by the mechanism, hide which part gives which benefit.

- Can a maintainer tell which conditions must hold after every operation?

    A condition a maintainer reads, at the decision it concerns, as holding after every operation tells them what must still hold when they change one part. Read as one step of a procedure, it is broken when the procedure changes.

- Can a builder check that the user gets each benefit, before what the user takes for granted?

    Checking the benefits first shows whether the user would choose the product at all. The benefits are what the product gives beyond what the user would use instead, such as another tool or doing the work by hand; what that also gives, the user takes for granted, such as nothing being lost. Whether a feature works as designed is a clue to why a benefit fails, not a check of it. Checks of what the user takes for granted are easier to write and their failures easier to see; put first, they multiply and all pass while no one has checked whether the user would choose the product.

    A check of a benefit measures it as the user would feel it, not that an artifact has the form meant to bring it. If the user should be able to approve from a summary without rereading the work, the check is whether a user who reads only the summary makes the decision they would make after reading the work. It runs on a case where, without the benefit, the user would visibly lose out, and its pass criteria say what happens to the reader or the user, with what was given up in deciding how far to check; then every builder checks the same way and can say it is realized. On a case where the alternative does as well, it passes without testing anything.

    What the user takes for granted and a script can decide, such as a format holding or a link resolving, goes to scripts. They are faster and give the same answer every time, and leave the checker's attention for whether the user gets the benefit.

- When a maintainer wants to switch to another option, can they see what switching would lose and why it was not chosen?

    Seeing what a switch would lose and why the option was not chosen, a maintainer weighs a change against the decision already made. Without it, they undo the decision unaware of its cost.

- Does the reader get here the intent and decisions they cannot read from the README or from the implementation?

    Every sentence says something that reading the README or the implementation does not reveal, and that does not change when the implementation is rebuilt, so the design stays true across rebuilds. Take each part away and ask whether a maintainer would then judge some change differently, or be unable to judge it; if not, it does not belong. A restated benefit or flow of use drifts from the README, and settings, procedures, how the code is split, file and function names or internal data structures go stale with each rebuild.

    What later versions or people read from the user's environment is an external agreement. Kept in one home, the design doc, which survives rebuilding the implementation, it shows a maintainer why each item exists, the conditions that always hold and what the form looks like, so they know which items may change without breaking a reader; the implementation carries no copy, since two copies drift apart. Handoffs between roles are not external agreements.
