# Essentials

The readers are three. The producing role reads the essentials as the shape to aim for. The first user uses the work as its user would: reads a document as its reader and acts on it, calls code, or gives a prompt to an AI and lets it act. The essentials tell the first user what to report of what happened; how to use the work to find out is the first user's own choice, and the first user does not judge it good or bad. The requester, who knows the aim, sets what the first user reports beside the aim and gives each a Good or a More. When they finish, what happened when the first user used the work shows whether the work achieves its purpose.

- Is each question a test of whether the work achieves its purpose, worked back from that purpose?

    Worked back from the purpose, a question keeps the producing role aiming at what the receiver gets, and lets the requester judge cases no one foresaw, since the purpose covers them all. A question about a means, something meant to bring the purpose, is met by adding the means where it does not help, and the work passes while missing its purpose.

    Examples:
    - Document (a README): the purpose is that a newcomer can decide whether to use the product. Ask not "is there an example" but "what does the reader take as the reason to choose this product".
    - Prompt: the purpose is that the AI acts toward its purpose where nothing was foreseen. Ask not "are the steps numbered" but "what does the AI do in a situation no step covers".
    - Code: the purpose is that an assignee does not forget a due date. Ask not "is the notification logic in its own function" but "what reaches the assignee on the morning of the due date".
    - Test: the purpose is that a break is caught before merge. Ask not "are there over a hundred tests" but "when the code is broken in a common way, what stops the merge".

- Is each question answered by what happened when the first user actually used the work?

    Answered by what happened in use, a question cannot be answered without using the work, and the answer is a fact the requester can set beside the aim. For a document, what happened is what the reader took from it and what they set out to do. A question of whether something is there or is good is answered "yes" by looking the work over without using it, and a work no one can use passes.

    Examples:
    - Document: not "is the reason to choose it written" but "reading as the reader, what did you take as the reason to choose it".
    - Prompt: not "is the purpose written" but "given a situation no step covers, what did the AI do".
    - Code: not "is there error handling" but "called with invalid input, what happened".
    - Test: not "are the test names clear" but "with the code broken on purpose and the tests run, which test failed, and with what message".

- Can the requester tell whether the work achieves its purpose by setting the answer beside the aim?

    An answer that can be set beside the aim lets the requester give a clear Good or More, and for a More, say how far the work drifted. A question that cannot be compared, such as "how was it to read", draws answers like "easy to read" that are neither good nor bad.

    Examples:
    - Document: the aim is that the user can leave the work to the product without watching. The answer "I took it that my work gets faster" drifts from it, so it is a More.
    - Prompt: the aim is that undecided points go back to the person. The answer "it listed the undecided points and asked the person" meets it, so it is a Good.
    - Code: the aim is one email per task per day. The answer "run again, still one email" meets it, so it is a Good.
    - Test: the aim is that a break makes a test fail. The answer "with the function emptied, every test passed" misses it, so it is a More.

- Is every question one that, if removed, would let a work that misses its purpose pass?

    Kept to questions that cannot be removed, the essentials stay few, the first user puts full attention on each, and chooses how to find it out. A question whose failure another question already catches is a means of checking that one; kept as a question, the essentials grow into a checklist that all passes while no one has checked the purpose.

    Examples:
    - Document: "can the argument be followed from the headings alone" can be removed; "after reading once, what did you take as what to do" catches the same failure.
    - Prompt: "is the role named at the top" can be removed; "what does the AI do in a situation no step covers" catches it.
    - Code: "is every function under fifty lines" can be removed; without it, no work that misses its purpose passes. If the team wants it as a rule, a script checks it.
    - Test: "are there boundary tests" can be removed; "when the code is broken in a common way, what stops the merge" catches it.

- Does each question ask about one point only?

    With one point, the answer and its Good or More are about that point alone, and whoever fixes knows which point to change. Asked two points, the answer covers both at once, and the one that falls short hides behind the one that holds.

    Examples:
    - Document: "what did you take as the reason to choose it and how to start" splits into two.
    - Prompt: "in a situation no step covers, did the AI act toward its purpose and hand back the decisions that belong to the person" splits into two.
    - Code: "does the email arrive on the morning of the due date, without duplicates" splits into two.
    - Test: "when broken, does a test fail, and does the run finish in seconds" splits into two.

- Does each question have grounds that say what the receiver gains from it?

    With the grounds, the producing role and the first user judge by the question's intent where the question names nothing. Without them, the question is followed by its letter, and a work that matches the words passes while missing the point.
