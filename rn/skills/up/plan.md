# The plan stage of /rn:up

Steps 7 and 8 of `/rn:up`, from the request to the plan sign-off, taken as its SKILL.md says.

7. Start the session, so every move from here has a place to be kept and shown.
   - In: the user's words; the repository's README, `cat -n README.md`, and `git log -10
     --format=%s`; the user's instructions in this conversation, such as their CLAUDE.md.
   - The first point to decide is the two languages, asked as step 2 asks a point: the conversation
     language and the artifact language each as the repository and the user's instructions set
     them, else the user's own for the conversation and English for the repository. Their answer is
     kept by `rn.py start` below, as no session holds a decision before it.
   - On the answer, choose the slug, a few lowercase words of the request joined by hyphens, such as
     `move-to-typescript`, and the title, the request in a few words, and run `rn.py start <slug>
     --title <t> --artifact-language <a> --conversation-language <c> --message <m>`, the message
     saying that the user asked for the work, in their words, and the languages they chose. It makes
     the branch and the steering, Next step 8, opens the draft pull request and prints
     `{"session": "<session>", "branch": "<branch>", "pr": "<the pull request's URL>"}`.
   - Out: the session started; go to step 8.

8. Make the plan and stop at the plan sign-off, so the user approves the goal and the criteria
   before anything is built on them.
   - In: the session started, at the plan stage.
   - Hear the purpose, with why the user wants it, and what shows it done: step 2 on work `plan`.
   - Write the plan: step 3 on work `plan`, giving nothing more, the part holding the goal, the
     criteria and only such tasks as the plan stage needs, the research or trials a gap in them
     calls for, none where none is needed.
   - Carry out each task in order, step 4; once the steering holds no task, step 5 on the plan
     sign-off.
   - Out: the plan sign-off waiting.
