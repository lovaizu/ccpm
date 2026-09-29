# Design doc

The readers are builders and maintainers, who may be people or AI. When they finish, they know how the outcome for the user is realized, and can explain whether a given change fits the design and, if not, why.

- Can a builder decide which way to go when unsure, by remembering just a few policies?

    State each policy flatly in one sentence, and right after it write what happens if it is not kept. Trace that explanation until it reaches the outcome for the user, or a condition the design cannot change, such as the environment the product is used in or the user. Write a rule that concerns only one feature where that feature is described.

- Can a maintainer read in the order they want to know things and get a sense of where to fix?

    First, the roles and their boundaries: who does what and who decides what. Next, the states there are and how operations change them. Next, the criteria for judgment: what is looked at and which way things are sorted. Last, what remains, who writes it and who reads it. Of roles, states and handoffs alike, keep only those whose reason for being there can be traced to the outcome for the user. Leave out those that cannot; they only add rules the maintainer has no way to check.

- Can a maintainer tell which conditions must hold after every operation?

    Write each such condition at the decision it concerns, phrased so it reads as a condition that always holds, as in "after every operation, ...".

- Can a builder decide, for each quality to check from the goal, how to check it, what passes, and how far to check?

    Check only whether the outcome for the user is achieved. Draw the qualities one by one from the items the design doc says it realizes, and for each quality write which item it is for and what the user struggles with if it is missing. Write the pass criteria as what happens to the reader or the user. Whether the mechanism works as designed is a clue for finding the cause when the outcome is not achieved; it is not a quality. When qualities are listed from the mechanism, someone checks that the mechanism works, but no one checks whether the user can achieve their purpose. Also write what you gave up when deciding how far to check. Without a written way to test, the way of checking varies by builder and by change. Without written pass criteria, even after the tests run, no one can decide whether it may be called realized.

- When a maintainer wants to switch to another option, can they see what it would lose and why it was not chosen?

- Does the reader get here the intent and decisions they cannot read from the document describing the outcome for the user or from the implementation?

    Every sentence says something that reading the document describing the outcome for the user or the implementation does not reveal, and that does not change when the implementation is rebuilt. So write decisions as intent and conditions that always hold, not as the settings or steps that realize them. The same goes when there is no implementation yet: settings or steps make the design doc go stale each time the implementation is rebuilt. How the code is split, file and function names, internal data structures and processing steps do not belong in a design doc. Mention by name only what people who use it can see, and external agreements. External agreements are the formats of what remains in the user's environment and of what later versions read; handoffs between roles are not included. Later versions and people both read external agreements, so write why each item exists and show them with a real filled-in example. Show the directory layout as a full tree only for what remains in the user's environment and what later versions read, and mark where the user may and may not make changes.
