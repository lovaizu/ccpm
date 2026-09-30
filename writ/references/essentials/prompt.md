# Prompt

The reader is the AI that acts by following the prompt. When it finishes, it can choose for itself a way of acting that achieves the purpose, even in situations the writer did not foresee.

- Can the AI grasp who it acts as, what it is for, and what it does?

    The purpose and the steps tell the role what to do, so the role comes first; given after them, the first orders have no one to carry them out. The role says who it reads as, what it decides itself, and what it returns to the requester instead. The purpose gives the benefit to the product's user and why it is needed, even for a role that works for another role; a purpose that ends at the handoff asks only for what the requester can check, and one that summarises the steps sends the AI back to following them where they do not reach. Knowing the benefit, the AI can choose what fits it where the steps do not cover.

- Can the AI follow each step as written without breaking what the product promises its user, and choose everything else itself from the purpose and role?

    Take a step away: if the AI, from its role and purpose, would still act rightly, it is not a step. What remains are rules that break things when they drift and cannot be derived, such as the format of a handoff. Steps are followed exactly, so a flow of work copied into numbered steps is followed even where it should not be, and a step phrased as a habit, such as "confirm with the user", overrides the purpose where the two disagree. A rule placed in another step's order, or a summary of a document the AI is told to read, is not followed where it is needed or drifts from its source.

- Can a maintainer tell, for each part of a prompt and each mechanism it relies on, which feature in the design it serves?

    A part or mechanism, such as an agent definition, a hook or a subagent launch, that traces to no feature was chosen while implementing with no ground anyone can check, and is kept by habit. Either it is left out, or the design is changed first.

- Can the checking role check as a reader, without being pulled along by the producing role's reasons?

    A checking role handed the producing role's reasons fills the work's gaps with them and misses where the reader trips. It reads the same essentials the producing role aimed for, as questions, and what it returns is what the requester fixes by: a Good says what the reader gains from it, which a fix must not take away, a More says what the reader struggles with, and both carry evidence such as path:line or a command and its output. A Good that says only "easy to understand" leaves whoever fixes it not knowing what to keep, and they break even what works.

- Is everything one role leaves for another read by a step of that other role, and everything a role reads written by someone?

    A role told that another will see its output stops dealing with it, and when no step of the other role reads that output, it falls through. Likewise, a step that reads something no one writes has nothing to work from.

- Is each role kept from what it must not see?

    The tools a role needs also reach what it must not see, such as git history, the discussion or earlier versions, so tools cannot close the boundary; only what the role is handed and what the prompt names as not to fetch can. Knowing why, the role also passes up routes to the same thing that the prompt did not name.

- Does the checking role spend its judgment where only it can judge?

    Only a role that did not produce the work can read it without knowing the discussion, so its attention goes to whether the reader gets the benefit they would choose the work for. What a script can decide, such as a format holding or a link resolving, goes to scripts, which are faster and give the same answer every time; what the reader takes for granted but no script can decide, such as whether a claim is true, stays with the checking role.

- Can the requester decide its next move itself by weighing the check's results against the purpose, and always bring the cycle of evaluating and fixing to an end?

    Acted on literally, a check's results redo even the parts that serve the purpose, and each new evaluation brings new non-essential remarks, so the cycle never settles. With judgment in one place that knows the purpose, each More is fixed, let go or handed to a person, each Good whose evidence does not hold is treated as a More, and the cycle ends as either settled or cannot proceed.

- When a person is asked something, can they answer with ease, without being asked what is already known?

    Asked several things at once, the person answers even what an earlier answer made unnecessary, and one answer cannot change the next question. Asked what the conversation, the documents handed over or the repository already tell, they answer the same thing again.

- When a person is asked for a review, can they decide whether to approve or request fixes without rereading the whole text?

    The person approves the final form, so the final Good and More for each question, each question shown as it is, with location and evidence, let them judge without rereading, and see that every question was answered. Remarks and fixes from along the way make them work out which still apply. A More that blocks the purpose with no fix the purpose decides is not a review but a question for the person.

- When the essentials are refined, can every role that uses them read the same essentials right away?

    A copy of the essentials in another document drifts each time they are refined, and the producing and checking roles then aim at and ask different things.

- Can the AI take every sentence it reads, as written, as something to do?

    Explanations of things that do not exist, how decisions came about, and rules that concern only the task at hand are not things to do.
