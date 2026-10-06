# Report: the question in 01-notes-question.md

## What I read and used, and what I left aside

I took up `open/01-notes-question.md` as the user would, answering it, against the "Question" section
of `references/essentials/conductor.md`. I also read:

- `steering.md`: the goal ("Address every open issue about rn. rn's quality is too low to be usable;
  make it work properly. Judge always from what rn should be; no patches."). Criteria, Assumptions and
  Tasks are empty except for #1 and #2.
- The open issues on lovaizu/ccpm (`gh issue list --repo lovaizu/ccpm --state open`), and the full
  text of #39, #41, #43, #44, #45 and #46 (`gh issue view N --repo lovaizu/ccpm`). The list also shows
  #35, #36 and #37 (writ/pith); I read only their titles.
- `rn/docs/design.md` lines 1-60 (Acceptance criteria A1-A4, M1-M7, feature table) and a grep of
  `rn/README.md` for "purpose" and "sign-off".

I did not look at the commit log, the PR conversation, earlier reports, or any other part of rn's code.

## Answering the question as the user, what did you have to look up or ask back first?

From the work I understood this. The question (`01-notes-question.md:3`) asks one open thing: what a
session should be like that it is not today. Before I could answer, I had to look up or would ask back:

- **Which issues are in.** The question names six (`01-notes-question.md:5`). The open-issue list
  also holds #37 ("writ: one /writ:up call runs pith about three times"), and #39's own text says
  "Each call runs `writ`'s own loop of checks and fixes (#37), so every extra call costs a whole round."
  So part of the design stage's hours (#39) sits in #37, which the question does not name. I would
  ask back whether #37 is in the session or left out, since it decides whether "a fraction of today's
  time" can be reached.
- **Whether #46 is rn's or all plugins'.** #46 says "This touches the rule in `.claude/rules/plugin.md`
  and every plugin that follows it (rn, writ, and pith once split out by #35), so it is settled once,
  for all of them." The question lists #46 as rn's proposal length only (`:6`). I had to read #46 to
  learn that fixing it means changing writ and the shared rule too.
- **The issue figures.** I checked the summary against the issues: #39 "2 h 43 min" matches "takes
  hours"; #46 says "72 lines", the question says "70 lines"; the others match their issue text. I did
  not need to ask back about these.

## Answering the question as the user, which separate decisions did you make?

From the work I understood this. Answering, I made three separate decisions:

1. What a session should be like (the question itself, `:3`).
2. Whether the "one thread" reading is right (`:5-10`): all six issues as "rn spends your time where
   you decide nothing". I had to decide this separately, because #43 case 2 is not about my time:
   another session "had it obeyed, ... would have gone on with split-pith's work in place of its
   conductor". That is rn acting wrongly, and the thread as written folds it into time spent.
3. Whether the three "Gains I see" (`:12-13`) are what I want, in particular "a session runs through
   in a fraction of today's time", which sets a time aim no issue states.

The message is laid out as one question, but answering it fully means deciding all three.

## Answering as the user, which ways to get the result were put before you before you had said what you want it to do for you?

From the work I understood this. No ways (approaches, designs, or options) are offered. What comes
before my answer is the conductor's reading (`:5-10`) and three outcomes it guesses I want
(`:12-13`): called only for my own decisions, each time a short yes/no message, and a fraction of
today's time. These are outcomes, not ways. Still, they are written before I have said anything.

## Choosing as the user among the ways offered, what did you want the result to do for you that no way gave?

From the work I understood this. No ways are offered, so I set what I want beside the three gains
instead. Going by the issues as filed, these are not in the gains:

- rn leaves other sessions alone: it does not stop their messages and does not send them on with
  its work (#43, "What it should be").
- rn waits for its agents the same way in every conversation (#44, "What it should be"). The question
  calls the present behaviour "improvising" (`:8`), but no gain covers this.
- rn keeps the branch of the worktree I started (#41). The gains cover being *called* only for my
  decisions, but not rn *doing* things I did not ask for without calling me.

The three gains cover #39, #45 and #46. They do not cover #41, #43 or #44, which are about rn
doing something wrong, not about my time.

## What part of the question could the goal, the conversation, the repository, the official documentation, or best practice have settled?

From the work I understood this.

- **Each issue already says what it should be.** All six have a "What it should be" section, for
  example #46: "What the user reads is bounded by what they decide, whatever the size of the work";
  #45: "A point is put to the user only when the goal, the request, and the repository leave more
  than one answer"; #39: "`writ` is called once per document, with every design point it needs
  already settled"; #41, #43 and #44 likewise. The question restates the problems (`:5-10`) but not
  these, and asks me to say again what a session should be.
- **rn's design already defines "work properly".** `rn/docs/design.md` A2 "The user is called only
  for decisions that are theirs, and does not watch over the work" and A3 "At a sign-off, the user
  decides from the proposal, without re-reading all the work" match the first two gains (`:12`).
  M1-M7 are what rn takes for granted. The goal's "Judge always from what rn should be" points there.
- **What the repository leaves open**, where more than one answer gives me something different:
  whether #37 (and #35, #36) are in the session; whether #46 is settled for all plugins or for rn
  only; and whether a time aim ("a fraction of today's time") is wanted, and how much. `design.md`
  A1-A4 have no time criterion. The question does not ask any of these directly.

## Answering the question as the user, which parts did you use to answer and which did you read past?

From the work I understood this.

- Used: the question line (`:3`); the "Gains I see" paragraph (`:12-13`), which is what I would say
  yes or no to; and in the summary (`:5-10`), the issue numbers, which I used to check scope.
- Read past: `Serves: goal` (`:1`); the per-issue paraphrases in `:5-10`, which restate issues I filed
  myself and add nothing I would answer from (only "70 lines", which I checked against #46's 72).

## Conductor

- More goal: the question asks what each issue's "What it should be" and `rn/docs/design.md` A1-A4 already settle, at 01-notes-question.md:3
- More goal: whether #46 covers writ and `.claude/rules/plugin.md` is left unsaid, though #46 settles it, at 01-notes-question.md:6
- More goal: whether #35, #36, #37 are in is left unsaid, at 01-notes-question.md:5
- More goal: the gains leave out #41, #43 and #44, at 01-notes-question.md:12-13
- More goal: a time aim is offered that no issue asks for, at 01-notes-question.md:13
- More goal: "70 lines" where #46 says 72, at 01-notes-question.md:6
