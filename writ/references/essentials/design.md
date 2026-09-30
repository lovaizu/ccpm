# Design doc

The readers are builders and maintainers, who may be people or AI. When they finish, they know which features give the user the README's benefits and how each is built, and can explain whether a given change fits the design and, if not, why.

- Can a builder decide which way to go when unsure, by remembering just a few policies?

    A policy guides a builder only where they know what breaks if it is not kept, traced until it reaches a benefit in the README or a condition the design cannot change, such as the environment the product is used in or the user. Without that, two policies cannot be weighed against each other. A rule that concerns only one feature, held among the policies, adds one more thing to remember everywhere.

- Can a maintainer follow each benefit in the README to the features that give it and the part that builds each, and so tell what a change costs the user?

    A feature is what the product provides toward one of the README's benefits, such as a checker that did not make the work checking it. Every feature, role, state and handoff traces to a benefit: one that traces to nothing can be taken away without loss, and a benefit no feature serves is missing its way. Parts named after mechanisms, or a benefit followed straight by the mechanism, leave the maintainer unable to tell which part gives which benefit. For example, the features are listed each with the benefit it serves and the step of use in the README where it works, and each then gets its own section on how it is built: who decides what, the states and how operations change them, what is looked at to judge, and what remains, who writes it and who reads it.

- Can a maintainer tell which conditions must hold after every operation?

    A maintainer changing one part needs to know what must still hold afterwards. A condition written as a step of a procedure is read as one step, and broken when the procedure changes; written at its decision as "after every operation, ...", it is kept.

- Can a builder check that the user gets each benefit, before what the user takes for granted?

    The benefits are what the product gives beyond what the user would use instead, such as another tool or doing the work by hand; what that also gives, the user takes for granted, such as nothing being lost. A product that is only correct gives the user no reason to choose it. Checks of what the user takes for granted are easier to write and their failures easier to see, so they multiply, get fixed first, and every check passes while no one has checked whether the user would choose the product. Whether a feature works as designed is a clue to why a benefit fails, not a check of it.

    A check of a benefit measures it as the user would feel it, not that an artifact has the form meant to bring it. If the user should be able to approve from a summary without rereading the work, the check is whether a user who reads only the summary makes the decision they would make after reading the work. It runs on a case where, without the benefit, the user would visibly lose out; on a case where the alternative does as well, it passes without testing anything. Its pass criteria say what happens to the reader or the user, and what was given up in deciding how far to check is written with it; without them, builders check differently and no one can say it is realized.

    What the user takes for granted and a script can decide, such as a format holding or a link resolving, goes to scripts. They are faster and give the same answer every time, and leave the checker's attention for whether the user gets the benefit.

- When a maintainer wants to switch to another option, can they see what switching would lose and why it was not chosen?

    Without it, a maintainer undoes a decision unaware of its cost, or weighs again what was already weighed.

- Does the reader get here the intent and decisions they cannot read from the README or from the implementation?

    Every sentence says something that reading the README or the implementation does not reveal, and that does not change when the implementation is rebuilt. Take each part away and ask whether a maintainer would then judge some change differently, or be unable to judge it; if not, it does not belong. A restated benefit or flow of use drifts from the README each time either changes, and settings, procedures, how the code is split, file and function names or internal data structures go stale each time the implementation is rebuilt.

    What later versions or people read from the user's environment is an external agreement, and a maintainer must know which items may change and which break a reader. The design doc is its one home, because it survives rebuilding the implementation; there it has why each item exists, the conditions that always hold, and the form shown filled in, and the implementation points there, since two copies drift apart. Handoffs between roles are not external agreements.
