# Design document

This file has three readers. The generator reads it as the form to aim for when it writes a design document. The first user takes the design document together with its README and implementation, and reads it as someone who builds or maintains the product: it picks one likely change and tries to decide whether it fits the design, and tries to check one benefit. It then reports, for each question here, what it did and what happened. It does not judge. The conductor lays the report beside the aim and gives each question a Good or More. Once they have read it through, they can tell, from what happened when it was used by someone who builds or maintains the product, whether the design document lets its reader learn which feature brings each of the README's benefits to the user and how each is built, check that the user gets each one, and say whether a change fits the design and, if not, why.

- Having picked one likely change, how did you decide, from what the user would lose, whether it fits the design?

    When they find, for each feature, the benefit it serves, the step of the README's usage where it works, and as much of how it is built as the change touches, maintainers weigh a change by what the user loses.

- When you were unsure whether a change fits the design, which principle did you recall and use?

    With few principles, builders can weigh them against each other and decide where situations differ. A rule that concerns only one feature sits beside that feature. Listed among the principles, it adds one more thing to keep in mind everywhere.

- For each principle you used, what did you take it would break if it were not kept?

    When a principle ties to a benefit, or to a condition the design cannot change, such as the environment the product is used in or its user, builders know what breaks and can weigh principles against each other. A principle tied to neither is kept out of habit.

- For each of the README's benefits, through which feature did you take it the user gets it?

    With a feature for each benefit, maintainers see how the user actually gets it. A feature is what the product offers toward a benefit, such as having the work checked by someone who did not write it. A benefit no feature serves has no way to reach the user. A part named after its mechanism, or writing in which a mechanism follows right after a benefit, hides which part brings which benefit. For the benefits, the flow of use and why each step is good for the user, pointing to the README's steps that already say them is enough. Said again in the design document, they drift from the README.

- After the change you picked, what did you take it must always hold?

    When it reads, at the decision it concerns, as a condition that holds after every operation, maintainers know what must keep holding even when they change one place. A condition read as one step of a procedure is broken when the procedure changes.

- In trying to check one benefit, what did you take it must happen for the check to pass?

    Checking whether the user actually got the benefit shows whether the user would choose the product at all. If the aim is to approve work from a summary without reading it again, the check is whether a user who read only the summary decides the same as one who read the work. A passing bar written as what happens to the reader or the user lets every builder check the same way. A check of whether the output has the shape meant for the benefit, or whether a feature works as designed, passes even when the benefit is missed.

- In what situation did you take it that check is run?

    When the check runs in a situation where the user would plainly struggle without the benefit, a pass is real proof of the benefit. In a situation the alternatives handle just as well, it passes without checking anything.

- Where did you take it the checking effort goes?

    Checking the benefits first puts the effort where it shows whether the user would choose the product. Quality the user takes for granted, such as nothing being lost, is easy to check and easy to see when broken, so placed first, its checks multiply and all pass, while no one has checked the benefits. Leaving to a script what a script can decide, such as whether a form is kept or whether a link is broken, is fast and gives the same answer every time.

- Where you were tempted to replace the current way with another option, why did you take it the current way was chosen?

    Knowing what replacing it loses and why that option was not chosen, maintainers weigh a change against the decisions already made. Without it, they overturn a decision without knowing its cost. An option maintainers would not reach for first needs no mention.

- Supposing the change you picked were made, which sentences would have to be rewritten though the intent stays the same?

    Kept to what does not change when the product is rebuilt, the design document stays true across rebuilds. Settings, procedures, how the code is split, file and function names, and internal data structures go stale with every rebuild.

- In trying to change the form of something left in the user's environment for later versions or people to read, which fields did you take it could be changed without breaking those who read it?

    What later versions or people read from the user's environment is a contract with the outside, read from outside, so its form is part of the design. When it is in the design document, the one place that survives a rebuild of the implementation, maintainers see why each field exists, what always holds, and what the form is, and can tell which fields can change without breaking those who read it. The implementation keeps no copy; two copies drift apart. Handoffs between roles are not a contract with the outside.
