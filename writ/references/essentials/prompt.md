# Prompt

The reader is the AI that acts by following the prompt. When it finishes, it can choose for itself a way of acting that achieves the purpose, even in situations the writer did not foresee.

- Can the AI grasp who it acts as, what it is for, and what it does?

    With the role first, the purpose and steps that follow have someone to carry them out. The role says who it reads as, what it decides itself, and what it returns to the requester instead. The purpose gives the benefit to the product's user and why it is needed, even for a role that works for another role, so the AI can choose what fits it where the steps do not reach. A purpose that ends at the handoff asks only for what the requester can check, and one that summarises the steps sends the AI back to following them.

- Can the AI follow each step as written without breaking what the product promises its user, and choose everything else itself from the purpose and role?

    Steps kept to rules that break things when they drift and cannot be derived, such as the format of a handoff, leave the AI free to choose everything else from its role and purpose. Take a step away: if the AI would still act rightly, it is not a step. Steps are followed exactly, so a flow of work copied into numbered steps is followed even where it should not be, a step phrased as a habit, such as "confirm with the user", overrides the purpose where the two disagree, and a rule placed in another step's order, or a summary of a document the AI is told to read, is missed where it is needed or drifts from its source.

- Can a maintainer tell, for each part of a prompt and each mechanism it relies on, which feature in the design it serves?

    A maintainer who can trace each part and each mechanism, such as an agent definition, a hook or a subagent launch, to a feature can tell what changing it costs. One that traces to nothing was chosen with no ground anyone can check and is kept by habit; either it is left out, or the design is changed first.

- Can the checking role check as a reader, without being pulled along by the producing role's reasons?

    Handed only the work, the reader and purpose, and the essentials, the checking role reads as the reader would and finds where they trip. It reads the same essentials the producing role aimed for, as questions, and returns what the requester fixes by: a Good says what the reader gains from it, which a fix must not take away, a More says what the reader struggles with, and both carry evidence such as path:line or a command and its output. Handed the producing role's reasons, it fills the gaps with them; a Good that says only "easy to understand" leaves whoever fixes it not knowing what to keep.

- Is everything one role leaves for another read by a step of that other role, and everything a role reads written by someone?

    When every output one role leaves is read by a step of the next, and everything a step reads is written by someone, nothing falls through between roles. A role told another will see its output stops dealing with it, and if no step reads it, it is lost; a step that reads what no one writes has nothing to work from.

- Is each role kept from what it must not see?

    Kept from what it must not see, such as git history, the discussion or earlier versions, by what it is handed and by the prompt naming them as not to fetch, with why, a role keeps the view it is there for; knowing why, it also passes up routes the prompt did not name. The tools it needs reach those too, so tools alone cannot close the boundary.

- Does the checking role spend its judgment where only it can judge?

    Only a role that did not produce the work can read it without knowing the discussion, so its attention goes to whether the reader gets the benefit they would choose the work for. What a script can decide, such as a format holding or a link resolving, goes to scripts, which are faster and give the same answer every time; what the reader takes for granted but no script can decide, such as whether a claim is true, stays with the checking role.

- Can the requester decide its next move itself by weighing the check's results against the purpose, and always bring the cycle of evaluating and fixing to an end?

    With judgment in one place that knows the purpose, each More is fixed, let go or handed to a person, each Good whose evidence does not hold is treated as a More, and the cycle ends as either settled or cannot proceed. Acted on literally, a check's results redo even the parts that serve the purpose, and each new evaluation brings new non-essential remarks.

- When a person is asked something, can they answer with ease, without being asked what is already known?

    Asked one thing at a time, and only what the conversation, the documents handed over or the repository do not already tell, the person answers with ease, and each answer can shape the next question. Asked several at once, they answer even what an earlier answer made unnecessary.

- When a person is asked for a review, can they decide whether to approve or request fixes without rereading the whole text?

    The person approves the final form, so the final Good and More for each question, each question shown as it is, with location and evidence, let them judge without rereading and see that every question was answered. A More that blocks the purpose with no fix the purpose decides is not for review but a question for the person. Remarks and fixes from along the way make them work out which still apply.

- When the essentials are refined, can every role that uses them read the same essentials right away?

    With the essentials in one place, every role reads the refined version at once, and the producing and checking roles aim at and ask the same things. A copy in another document drifts each time they are refined.

- Can the AI take every sentence it reads, as written, as something to do?

    When every sentence is something to do, the AI acts on each as written. Explanations of things that do not exist, how decisions came about, and rules that concern only the task at hand are not, and the AI acts on them anyway.
