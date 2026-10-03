# Essentials files

This file has three readers. The generator reads it as the form to aim for when it writes an essentials file. The first user tries checking a real work of the file's kind with the essentials file's questions, and reports, for each question here, what it did and what happened. How to check is for the first user to decide, and it does not judge. The conductor lays the report beside the aim and gives each question a Good or More. Once they have read it through, they can tell, from what happened when the essentials file was used, whether that essentials file can check that a real work achieved its purpose.

- For each question of the essentials file, what did you do with the real work to get an answer?

    When a question was answered by using the real work as its receiver, the answer is a fact that comes out only by using it, and can be laid beside the aim and compared. For a document, it is what was taken in and what was set out to do, reading as the reader. A question answered by only looking over the real work asks whether something is there or whether it is good, and passes with "yes" even for a real work no one can use. If you stopped without an answer, where you stopped is where the question falls short.

    Examples:
    - Document: "Does it state the reason to choose it?" is answered by looking it over. "Reading as the reader, what did you take in as the reason to choose it?" is answered only by reading it.
    - Prompt: "Does it state the purpose?" is answered by looking it over. "Given a situation no step covers, what did the AI do?" is answered only by running it.
    - Code: "Is there error handling?" is answered by looking it over. "Called with a bad value, what happened?" is answered only by calling it.
    - Tests: "Are the test names clear?" is answered by looking them over. "With the code broken on purpose and the tests run, which test failed, with what message?" is answered only by running them.

- For each question of the essentials file, what answer came out?

    When the answer is what the receiver got or what happened to the receiver, the conductor can lay it beside the aim and plainly give a Good or More, and for a More can say how far it falls short. What draws such answers is a question worked back from the purpose. The purpose also covers situations no one foresaw, so answers in those situations can be judged too. A question about a means toward the purpose gets an answer about whether the means is there; adding the means even where it does not help passes, and the real work still misses the purpose. A question with nothing to compare against, such as "How was it to read?", gets an answer that is neither good nor bad, such as "It was easy to read."

    Examples:
    - Document: the purpose is that a newcomer can decide whether to use it. "There was an example" is an answer about a means and cannot be compared with the aim. "I took in being able to leave long work to it without watching as the reason to choose it" can be compared.
    - Prompt: the purpose is that the AI acts toward the purpose even in situations no step covers. "The steps were numbered" cannot be compared. "It listed the points not decided and asked the user" is a Good when the aim is "points not decided go back to the user".
    - Code: the purpose is that the person in charge does not forget a due date. "The notification was handled in a separate function" cannot be compared. "Run again, there was still one email" is a Good when the aim is "one email per item per day".
    - Tests: the purpose is to stop what is broken before it is merged. "There were over a hundred tests" cannot be compared. "With the function's body emptied, every test passed" is a More when the aim is "breaking it makes a test fail".

- In the answer to which question did it show which parts of the real work were used toward the purpose, and which were passed by without being used?

    When the used parts and the parts passed by show in the answers, the conductor finds the parts the real work does not need. A question that only asks whether something is good gets answers only about the parts used, and the skipped parts catch no one's eye.

    Examples:
    - Document: as the reader, the sections used to decide whether to use it, and the section on history that was skipped.
    - Prompt: the instructions the AI followed when it acted, and the instructions that did not matter in any situation.
    - Code: the code paths taken when called, and the ones never taken.
    - Tests: the tests that failed when the code was broken, and the tests that never failed, whatever was broken.

- Which questions' answers did work in trying to check the real work, and which did nothing?

    Kept to the questions that did work, the file has few questions, the first user gives each its full attention, and it can choose how to check for itself. A question that did nothing either asks again what another question's answer already shows, or does not stop a real work that misses the purpose. Kept, such questions grow the essentials file into a checklist that all passes while no one has checked the purpose.

    Examples:
    - Document: the answer to "Could you follow the line from the headings alone?" did nothing. What the reader does showed in the answer to "Having read it once, what did you take it you should do?".
    - Prompt: the answer to "Was the role stated at the top?" did nothing. How the AI acted showed in the answer to "In a situation no step covers, what did the AI do?".
    - Code: the answer to "Was every function 50 lines or fewer?" did nothing. To make it a team rule, check it with a script.
    - Tests: the answer to "Were there tests for boundary values?" did nothing. Whether something broken is stopped showed in the answer to "When broken in a common way, what stopped the merge?".

- Which question answered two or more points with one answer, and what were they?

    When a question asks about one point only, the answer and the Good or More are about that point alone, and whoever fixes knows what to change. When it asks about two points at once, the answer speaks of both together, and the one that falls short hides behind the one that does not.

    Examples:
    - Document: "What did you take in as the reason to choose it, and as how to start?" splits into two.
    - Prompt: "In a situation no step covers, did the AI act toward the purpose and return to the user what the user decides?" splits into two.
    - Code: "Did the email arrive on the morning of the due date, without duplicates?" splits into two.
    - Tests: "When broken, did a test fail, and did the run finish in seconds?" splits into two.

- When a question's words alone did not settle what to check, what did you go by to decide?

    With a ground under each question saying what the receiver gains, the generator and the first user can decide, by the question's intent, what its words do not touch. Without one, a question is used to the letter, and a real work that only matches the words passes while missing what matters.
